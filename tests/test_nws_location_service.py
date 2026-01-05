# test_nws_location_service.py

import unittest
import asyncio
from unittest.mock import patch, MagicMock
from weatherinfo_mcp.core.nws_location_service import Location

class TestLocationCore(unittest.TestCase):

    def test_init_with_address(self):
        # Test that __init__ just stores the address without processing
        obj = Location(address="Dallas, TX")
        self.assertEqual(obj.address, "Dallas, TX")
        self.assertIsNone(obj.latitude)
        self.assertIsNone(obj.longitude)
        self.assertIsNone(obj.station_url)

    def test_init_with_latlon(self):
        # Test that __init__ just stores lat/lon without processing
        obj = Location(latitude=32.8, longitude=-98.5)
        self.assertIsNone(obj.address)
        self.assertEqual(obj.latitude, 32.8)
        self.assertEqual(obj.longitude, -98.5)
        self.assertIsNone(obj.station_url)

    def test_init_with_latlon_stores_values(self):
        # Test that __init__ stores even invalid coordinates (validation happens elsewhere)
        obj1 = Location(latitude=100, longitude=90)
        self.assertEqual(obj1.latitude, 100)
        self.assertEqual(obj1.longitude, 90)
        
        obj2 = Location(latitude=42, longitude=200)
        self.assertEqual(obj2.latitude, 42)
        self.assertEqual(obj2.longitude, 200)

    def test_init_missing_params_works(self):
        # Test that __init__ works with no parameters (validation happens elsewhere)
        obj = Location()
        self.assertIsNone(obj.address)
        self.assertIsNone(obj.latitude)
        self.assertIsNone(obj.longitude)
        self.assertIsNone(obj.station_url)

    @patch('httpx.AsyncClient.get')
    def test_get_current_observation_success(self, mock_get):
        # Arrange
        test_station_url = "https://api.weather.gov/stations/TEST"
        obj = Location.__new__(Location)  # don't call __init__
        obj.station_url = test_station_url
        obj.http_timeout = 10

        # Set up fake response
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {'properties': {'temperature': {'value': 30}}}
        mock_get.return_value = mock_resp

        # Act
        props = asyncio.run(obj.get_current_observation())

        # Assert
        mock_get.assert_called_once_with(f"{test_station_url}/observations/latest", timeout=10)
        self.assertEqual(props['temperature']['value'], 30)

    @patch('httpx.AsyncClient.get', side_effect=Exception("HTTP error"))
    def test_get_current_observation_error(self, mock_get):
        obj = Location.__new__(Location)
        obj.station_url = "https://api.weather.gov/stations/TEST"
        obj.http_timeout = 10

        with self.assertRaises(Exception):
            asyncio.run(obj.get_current_observation())

if __name__ == "__main__":
    unittest.main()
