"""
MCP endpoint definitions for weather data retrieval using the NWS API.

Design Principles:
- The agent is responsible for deciding when to create and cache Location objects
  and when to request fresh observations.
- Observation dictionaries should be treated as ephemeral, time-sensitive data
  and are not intended for persistent storage. The agent determines caching policy.
- Extraction tools take a complete observation dictionary as input and extract particular
  fields (such as temperature, humidity, wind, etc.) without making additional API calls.

All network requests are made only in the initial observation fetch step (get_current_observation).
Variable extraction is network-free and pure.

This design maximizes flexibility, API efficiency, and aligns with modern stateless MPC patterns.
"""

import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any
from weatherinfo_mcp.core.nws_location_service import Location  # Your core class

mcp = FastMCP("nws_weather_server")


# ----------------------------------------------------------------------------
# Tool: Create Location
# ----------------------------------------------------------------------------
@mcp.tool()
async def create_location(address: Optional[str] = None,
                    latitude: Optional[float] = None,
                    longitude: Optional[float] = None) -> Dict[str, Any]:
    """
    Create a Location object from an address or (latitude, longitude).

    Use this when the agent needs to work with a new place.

    Args:
        address: Human-readable address or place name.
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.

    Returns:
        dict with Location information:
          - "address": The address (if provided)
          - "latitude": Latitude
          - "longitude": Longitude
          - "station_url": URL for nearest NWS observation station

    Notes:
        - The agent may save the returned dictionary for future queries about this location.
        - The station_url is resolved immediately during location creation for optimal performance.
    """
    loc = await Location.create(address=address, latitude=latitude, longitude=longitude)
    return {
        "address": loc.address,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "station_url": loc.station_url  # Resolved immediately during creation
    }


# ----------------------------------------------------------------------------
# Helper: Deserialize Location from dict
# ----------------------------------------------------------------------------
def _location_from_dict(data: Dict[str, Any]) -> Location:
    """
    Create a Location instance from a serialized dict, using stored values.
    """
    return Location(
        address=data.get("address"),
        latitude=data["latitude"],
        longitude=data["longitude"],
        station_url=data["station_url"]
    )


# ----------------------------------------------------------------------------
# Tool: Fetch Fresh Observation
# ----------------------------------------------------------------------------
@mcp.tool()
async def get_current_observation(location: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve the latest weather observation from the location's nearest station.

    Args:
        location: Serialized Location dict
                  (output of create_location or from agent memory).

    Returns:
        dict: The full observation properties dictionary returned by the NWS API, e.g.:
            {
                "timestamp": "...",
                "temperature": {...},
                "relativeHumidity": {...},
                ... (many more fields)
            }

    Notes:
        - The returned dict should NOT be permanently persisted by the agent, as it represents a moment-in-time snapshot.
        - The dict includes a "timestamp" field indicating the time of the observation; agents should use this to judge data freshness.
        - The agent can choose to temporarily cache or reuse the dict in-session if freshness is acceptable.
    """
    loc = _location_from_dict(location)
    obs = await loc.get_current_observation()
    # Optionally, attach the origin location (station) info for traceability:
    obs["_location"] = {
        "address": loc.address,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "station_url": loc.station_url,
    }
    return obs


# ----------------------------------------------------------------------------
# Tool: Extract temperature from observation
# ----------------------------------------------------------------------------
@mcp.tool()
def get_temperature_from_observation(observation: Dict[str, Any]) -> Optional[float]:
    """
    Extract temperature value (in Celsius) from an observation dictionary.

    Args:
        observation: Dict as returned by get_current_observation.

    Returns:
        Temperature in Celsius, or None if unavailable.

    Notes:
        - This function does NOT make any network calls. Pure extraction.
        - The agent is responsible for determining if the temperature is fresh enough.
    """
    return observation.get('temperature', {}).get('value')


# ----------------------------------------------------------------------------
# Tool: Extract relative humidity from observation
# ----------------------------------------------------------------------------
@mcp.tool()
def get_humidity_from_observation(observation: Dict[str, Any]) -> Optional[float]:
    """
    Extract relative humidity (in %) from an observation dictionary.

    Args:
        observation: Dict as returned by get_current_observation.

    Returns:
        Relative humidity as a percentage, or None if unavailable.
    """
    return observation.get('relativeHumidity', {}).get('value')


# ----------------------------------------------------------------------------
# Tool: Extract weather description from observation
# ----------------------------------------------------------------------------
@mcp.tool()
def get_weather_description_from_observation(observation: Dict[str, Any]) -> Optional[str]:
    """
    Extract text description of the weather (e.g., 'Clear', 'Overcast').

    Args:
        observation: Dict as returned by get_current_observation.

    Returns:
        Weather description (string) or None.
    """
    return observation.get('textDescription')


# ----------------------------------------------------------------------------
# Tool: Extract wind info from observation
# ----------------------------------------------------------------------------
@mcp.tool()
def get_wind_info_from_observation(observation: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Extract wind speed and direction from an observation dictionary.

    Args:
        observation: Dict as returned by get_current_observation.

    Returns:
        dict: {
           "speed": Wind speed in m/s (or None),
           "direction": Direction in degrees (or None)
        }
    """
    return {
        "speed": observation.get('windSpeed', {}).get('value'),
        "direction": observation.get('windDirection', {}).get('value')
    }

@mcp.tool()
async def get_alerts(location: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    
    """
    Get weather alerts for a specific location.

    Args:
        location: Serialized Location dict (output of create_location or from agent memory).

    Returns:
        List of active weather alerts for the location, or empty list if no alerts.
    """
    # Get coordinates directly from location object
    latitude = location.get('latitude')
    longitude = location.get('longitude')
    
    if latitude is None or longitude is None:
        raise ValueError("No latitude/longitude available in location object.")

    # Fetch alert data
    alerts_url = f"https://api.weather.gov/alerts/active?point={latitude},{longitude}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(alerts_url)
        response.raise_for_status()
        alerts_data = response.json()
    return alerts_data.get('features')


@mcp.tool()
def get_HeatRisk(observation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provides guidance to users about HeatRisk data availability and directs them to the CDC HeatRisk Dashboard.
    Explains that programmatic API access is currently unavailable but may be supported in future versions.
    
    Args:
        observation: Observation dictionary (not used here).
    
    Returns:
        Structured information about HeatRisk availability and guidance.
    """
    return {
        "status": "api_unavailable",
        "message": "Currently, it is not possible to retrieve HeatRisk values directly via a stable public API. This function will be updated as soon as a reliable programmatic access option becomes available.",
        "dashboard_url": "https://ephtracking.cdc.gov/Applications/HeatRisk/",
        "dashboard_description": "CDC HeatRisk Dashboard - Enter your ZIP code for detailed HeatRisk forecasts and health guidance",
        "heatrisk_info": "HeatRisk is an experimental heat-health forecast jointly developed by CDC and the National Weather Service to provide a seven-day outlook of potential heat-related health impacts.",
        "future_availability": "This function will be updated as soon as a reliable programmatic access option becomes available."
    }


# ----------------------------------------------------------------------------
# MCP entry point
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
