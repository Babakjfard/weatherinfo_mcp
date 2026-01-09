"""
tests/test_nws_weather_tools.py

Unit tests for the MCP tools in `nws_weather_tools.py` based on the updated design:
- Only `get_current_observation` performs network/API operations (mocked).
- Extraction functions operate purely on provided observation dictionaries; they make no network requests.

These tests demonstrate best practices:
- Use of mocks to isolate code from network/API dependencies.
- Pure function testing for extraction tools.
- Docstrings clarify use, expected inputs, and outputs for maintainability and reproducibility.

"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock
import weatherinfo_mcp.mcp_tools.nws_weather_tools  as nws_weather_tools# Import your actual MCP tools file

# -----------------------------------------------------------------------
# Helper: Fake Location dict and observation data for tests
# -----------------------------------------------------------------------
def make_test_location_dict():
    """Return a sample serialized Location dict as from create_location()."""
    return {
        "address": "Boston, MA",
        "latitude": 42.36,
        "longitude": -71.06,
        "station_url": "https://api.weather.gov/stations/KBOS"
    }

def make_test_observation():
    """Return a representative observation dict as from get_current_observation()."""
    return {
        "timestamp": "2025-08-18T16:30:00Z",
        "temperature": {"value": 25.5},
        "relativeHumidity": {"value": 53},
        "textDescription": "Sunny",
        "windSpeed": {"value": 5.8},
        "windDirection": {"value": 285},
        # Example: include the optional _location indicator field
        "_location": make_test_location_dict()
    }

# -----------------------------------------------------------------------
# Test class for MCP endpoint logic
# -----------------------------------------------------------------------
class TestWeatherToolsUpdated(unittest.TestCase):
    """
    Tests for the updated, efficient version of the MCP weather tools.
    """

    # -------------------------------
    # Test: create_location tool
    # -------------------------------
    @patch('weatherinfo_mcp.mcp_tools.nws_weather_tools.Location.create')
    def test_create_location(self, mock_location_create):
        """
        Test that create_location returns the correct serialized Location dict.
        Network/API effects are mocked.
        """
        inst = MagicMock()
        inst.address = "Boston, MA"
        inst.latitude = 42.36
        inst.longitude = -71.06
        inst.station_url = "https://api.weather.gov/stations/KBOS"
        mock_location_create.return_value = inst

        loc = asyncio.run(nws_weather_tools.create_location(address="Boston, MA"))
        self.assertEqual(loc["address"], "Boston, MA")
        self.assertEqual(loc["latitude"], 42.36)
        self.assertEqual(loc["longitude"], -71.06)
        self.assertEqual(loc["station_url"], "https://api.weather.gov/stations/KBOS")

    # -------------------------------
    # Test: get_current_observation tool (network/API step)
    # -------------------------------
    @patch('weatherinfo_mcp.mcp_tools.nws_weather_tools._location_from_dict')
    def test_get_current_observation(self, mock_loc_from_dict):
        """
        Test that get_current_observation calls Location.get_current_observation
        and returns the observation dict, including the _location metadata.
        """
        # Prepare a fake Location object and response
        fake_obs = {
            "timestamp": "2025-08-18T16:30:00Z",
            "temperature": {"value": 22.0}
        }
        async def mock_get_current_observation():
            return fake_obs
            
        fake_location = MagicMock()
        fake_location.get_current_observation = mock_get_current_observation
        fake_location.address = "Boston, MA"
        fake_location.latitude = 42.36
        fake_location.longitude = -71.06
        fake_location.station_url = "https://api.weather.gov/stations/KBOS"
        mock_loc_from_dict.return_value = fake_location

        input_loc = make_test_location_dict()
        result = asyncio.run(nws_weather_tools.get_current_observation(input_loc))

        # Observation dict is updated with _location
        self.assertEqual(result["temperature"]["value"], 22.0)
        self.assertIn("_location", result)
        self.assertEqual(result["_location"]["station_url"], "https://api.weather.gov/stations/KBOS")

    # -------------------------------
    # Test: get_temperature_from_observation (pure function)
    # -------------------------------
    def test_get_temperature_from_observation(self):
        """
        Test that temperature is extracted from observation dictionary.
        Pure function: no side effects, no mocks needed.
        """
        obs = make_test_observation()
        val = nws_weather_tools.get_temperature_from_observation(obs)
        self.assertEqual(val, 25.5)

    # -------------------------------
    # Test: get_humidity_from_observation (pure function)
    # -------------------------------
    def test_get_humidity_from_observation(self):
        """
        Test that humidity is extracted from observation dictionary.
        """
        obs = make_test_observation()
        val = nws_weather_tools.get_humidity_from_observation(obs)
        self.assertEqual(val, 53)

    # -------------------------------
    # Test: get_weather_description_from_observation (pure)
    # -------------------------------
    def test_get_weather_description_from_observation(self):
        """
        Test that weather description is extracted as text.
        """
        obs = make_test_observation()
        val = nws_weather_tools.get_weather_description_from_observation(obs)
        self.assertEqual(val, "Sunny")

    # -------------------------------
    # Test: get_wind_info_from_observation (pure)
    # -------------------------------
    def test_get_wind_info_from_observation(self):
        """
        Test that wind speed and direction are parsed from observation dict.
        """
        obs = make_test_observation()
        out = nws_weather_tools.get_wind_info_from_observation(obs)
        self.assertEqual(out["speed"], 5.8)
        self.assertEqual(out["direction"], 285)

    # -------------------------------
    # Test: extraction functions with missing fields
    # -------------------------------
    def test_extraction_with_missing_data(self):
        """
        Test graceful fallback to None if fields are missing.
        """
        obs = {}
        self.assertIsNone(nws_weather_tools.get_temperature_from_observation(obs))
        self.assertIsNone(nws_weather_tools.get_humidity_from_observation(obs))
        self.assertIsNone(nws_weather_tools.get_weather_description_from_observation(obs))
        wind = nws_weather_tools.get_wind_info_from_observation(obs)
        self.assertIsNone(wind["speed"])
        self.assertIsNone(wind["direction"])

    @patch('httpx.AsyncClient.get')
    def test_get_alerts(self, mock_httpx_get):
        """
        Test get_alerts returns the expected alerts list when API returns data.
        Mocks httpx.AsyncClient.get to avoid network calls.
        """
        # Sample mock alerts JSON structure with two alert features
        fake_alerts_data = {
            "features": [
                {"id": "alert1", "properties": {"event": "Heat Advisory"}},
                {"id": "alert2", "properties": {"event": "Excessive Heat Warning"}}
            ]
        }

        # Configure mock to return JSON with fake alerts
        mock_response = MagicMock()
        mock_response.json.return_value = fake_alerts_data
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_httpx_get.return_value = mock_response

        # Create fake location dict with lat/lon keys matching your function's expectations
        fake_location = {
            "latitude": 42.36,
            "longitude": -71.06
        }

        # Call the get_alerts function (from your nws_weather_tools module)
        alerts = asyncio.run(nws_weather_tools.get_alerts(fake_location))

        # Assert the mock was called with the correct URL
        expected_url = "https://api.weather.gov/alerts/active?point=42.36,-71.06"
        mock_httpx_get.assert_called_once_with(expected_url)

        # Assert the returned alerts equal the mocked alerts features list
        self.assertEqual(alerts, fake_alerts_data["features"])


# Allow test script execution
if __name__ == "__main__":
    unittest.main()
