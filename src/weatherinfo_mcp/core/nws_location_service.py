import httpx
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

class Location:
    """
    Represents a specific geographic location, with latitude/longitude
    and the nearest NWS observation station resolved during initialization.

    This model is MCP-ready and suitable for repeated lookups of weather
    observations, warnings, etc., without redundant API calls.

    Attributes:
        address (str | None): Original address used for geocoding (if provided).
        latitude (float): Latitude in decimal degrees.
        longitude (float): Longitude in decimal degrees.
        station_url (str): URL of the nearest NWS observation station.
    """

    def __init__(self, *,
                 address: str = None,
                 latitude: float = None,
                 longitude: float = None,
                 station_url: str = None,
                 user_agent: str = "weatherinfo_mcp_app",
                 geocode_timeout: int = 10,
                 geocode_max_retries: int = 3,
                 http_timeout: int = 10):
        """
        Initialize a Location object. This is typically used for deserialized objects.
        For creating new locations, use Location.create() instead.
        """
        self.user_agent = user_agent
        self.geocode_timeout = geocode_timeout
        self.geocode_max_retries = geocode_max_retries
        self.http_timeout = http_timeout

        # Store the provided values
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.station_url = station_url

    @classmethod
    def from_dict(cls, data: dict):
        """
        Construct a Location directly from a serialized dict.
        """
        return cls(
            address=data.get("address"),
            latitude=data["latitude"],
            longitude=data["longitude"],
            station_url=data.get("station_url")
        )
    
    @classmethod
    async def create(cls, *, address: str = None, latitude: float = None, longitude: float = None, **kwargs):
        """
        Create a new Location with immediate station URL resolution.
        This is the recommended way to create Location objects.
        """
        # Validate inputs
        if address and (latitude is not None or longitude is not None):
            raise ValueError("Provide either address OR coordinates, not both.")
        
        if not address and (latitude is None or longitude is None):
            raise ValueError("Must provide either address or both latitude and longitude.")
        
        # Create location object
        location = cls(address=address, latitude=latitude, longitude=longitude, **kwargs)
        
        # Resolve coordinates if address provided
        if address:
            location.latitude, location.longitude = location._resolve_lat_lon(address)
        
        # Validate coordinates
        if not (-90 <= location.latitude <= 90):
            raise ValueError(f"Latitude {location.latitude} is out of range (-90 to 90).")
        if not (-180 <= location.longitude <= 180):
            raise ValueError(f"Longitude {location.longitude} is out of range (-180 to 180).")
        
        # Resolve station URL immediately (this is the key part!)
        location.station_url = await location._resolve_nearest_station(location.latitude, location.longitude)
        
        return location
    
    
    # ----------------------------------------------------------------------------
    # Helper: Geocode Address
    # ----------------------------------------------------------------------------
    def _resolve_lat_lon(self, address: str) -> tuple[float, float]:
        """Internal method to geocode the address into (lat, lon) with retry & rate limiting."""
        geolocator = Nominatim(user_agent=self.user_agent, timeout=self.geocode_timeout)
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        retries = 0
        while retries < self.geocode_max_retries:
            try:
                location = geocode(address)
                if location:
                    return location.latitude, location.longitude
                raise RuntimeError(f"Could not geocode address: '{address}'")
            except (GeocoderTimedOut, GeocoderUnavailable):
                retries += 1
                if retries >= self.geocode_max_retries:
                    raise RuntimeError(f"Geocoding service unavailable after {self.geocode_max_retries} retries.")
            except Exception as e:
                raise RuntimeError(f"Unexpected geocoding error: {e}")


    # ----------------------------------------------------------------------------
    # Helper: Resolve Nearest Station
    # ----------------------------------------------------------------------------
    async def _resolve_nearest_station(self, latitude: float, longitude: float) -> str:
        """Internal method to fetch the nearest NWS observation station URL."""
        try:
            points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(points_url, timeout=self.http_timeout)
                response.raise_for_status()
                data = response.json()

                observation_stations_url = data['properties']['observationStations']
                stations_response = await client.get(observation_stations_url, timeout=self.http_timeout)
                stations_response.raise_for_status()
                stations_data = stations_response.json()
                stations = stations_data['observationStations']

                if not stations:
                    raise RuntimeError("No observation stations found for this location.")

                return stations[0]

        except httpx.RequestError as e:
            raise httpx.RequestError(f"HTTP request error: {e}")
        except KeyError as e:
            raise KeyError(f"Missing expected data in API response: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while resolving station: {e}")


    # ----------------------------------------------------------------------------
    # Helper: Get Current Observation
    # ----------------------------------------------------------------------------
    async def get_current_observation(self) -> dict:
        """
        Get the latest weather observation data from the location's nearest station.

        Returns:
            dict: NWS 'properties' dictionary containing weather data.
        """
        if self.station_url is None:
            raise RuntimeError("Station URL not resolved. Use Location.create() to create locations with station resolution.")
            
        try:
            obs_url = f"{self.station_url}/observations/latest"
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(obs_url, timeout=self.http_timeout)
                response.raise_for_status()
                data = response.json()
                return data.get('properties', {})
        except httpx.RequestError as e:
            raise httpx.RequestError(f"Error fetching current observation: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error fetching observation: {e}")
