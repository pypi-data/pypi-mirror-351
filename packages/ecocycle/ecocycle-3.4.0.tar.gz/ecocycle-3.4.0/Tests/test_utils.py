"""
Test module for utils.py
"""
import os
import sys
import unittest
from unittest import mock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils.general_utils

class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_calculate_distance(self):
        """Test distance calculation."""
        # Test with known distances
        self.assertAlmostEqual(utils.calculate_distance(40.7128, -74.0060, 40.7128, -74.0060), 0.0, places=2)
        self.assertAlmostEqual(utils.calculate_distance(0, 0, 0, 1), 111.19, places=1)
    
    def test_calculate_co2_saved(self):
        """Test CO2 savings calculation."""
        # Test with known values
        self.assertAlmostEqual(utils.calculate_co2_saved(10), 2.3, places=1)  # 10 km should save around 2.3 kg CO2
        self.assertEqual(utils.calculate_co2_saved(0), 0)  # 0 km should save 0 kg CO2
    
    def test_calculate_calories(self):
        """Test calorie burning calculation."""
        # Test with known values
        self.assertGreater(utils.calculate_calories(10, 15, 70), 0)  # Should return positive calories
        self.assertEqual(utils.calculate_calories(0, 15, 70), 0)  # 0 distance should burn 0 calories
    
    def test_format_distance(self):
        """Test distance formatting."""
        self.assertEqual(utils.format_distance(1.0), "1.0 km")
        self.assertEqual(utils.format_distance(1), "1.0 km")
        self.assertEqual(utils.format_distance(0), "0.0 km")
    
    def test_format_co2(self):
        """Test CO2 formatting."""
        self.assertEqual(utils.format_co2(1.0), "1.0 kg")
        self.assertEqual(utils.format_co2(1), "1.0 kg")
        self.assertEqual(utils.format_co2(0), "0.0 kg")
    
    def test_format_calories(self):
        """Test calorie formatting."""
        self.assertEqual(utils.format_calories(100), "100 kcal")
        self.assertEqual(utils.format_calories(100.5), "101 kcal")  # Should round
        self.assertEqual(utils.format_calories(0), "0 kcal")
    
    @mock.patch('utils.requests')
    def test_get_current_weather(self, mock_requests):
        """Test weather retrieval with mocked API."""
        # Mock the API response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'current': {
                'temp_c': 20,
                'condition': {'text': 'Sunny'},
                'wind_kph': 10,
                'humidity': 50
            }
        }
        mock_requests.get.return_value = mock_response
        
        # Test the function
        result = utils.get_current_weather('London')
        
        # Check the result
        self.assertEqual(result['temperature'], 20)
        self.assertEqual(result['condition'], 'Sunny')
        self.assertEqual(result['wind_speed'], 10)
        self.assertEqual(result['humidity'], 50)
    
    @mock.patch('utils.requests')
    def test_get_current_weather_error(self, mock_requests):
        """Test weather retrieval with API error."""
        # Mock the API error
        mock_requests.get.side_effect = Exception("API Error")
        
        # Test the function
        result = utils.get_current_weather('London')
        
        # Check the result is None on error
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()