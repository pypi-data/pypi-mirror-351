"""
Test module for weather_route_planner.py
"""
import os
import sys
import unittest
from unittest import mock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import apps.route_planner.weather_route_planner

class TestWeatherRoutePlanner(unittest.TestCase):
    """Test cases for WeatherRoutePlanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test weather route planner
        self.planner = weather_route_planner.WeatherRoutePlanner()
    
    @mock.patch('weather_route_planner.requests.get')
    def test_check_weather(self, mock_get):
        """Test checking weather with mocked API."""
        # Mock the API response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'location': {
                'name': 'London',
                'region': 'City of London',
                'country': 'UK'
            },
            'current': {
                'last_updated': '2025-04-15 12:00',
                'temp_c': 20,
                'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/weather/64x64/day/113.png'},
                'wind_kph': 10,
                'humidity': 50,
                'feelslike_c': 21
            },
            'forecast': {
                'forecastday': [
                    {
                        'date': '2025-04-15',
                        'day': {
                            'maxtemp_c': 22,
                            'mintemp_c': 15,
                            'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/weather/64x64/day/113.png'},
                            'uv': 5.0
                        },
                        'hour': [
                            {
                                'time': '2025-04-15 00:00',
                                'temp_c': 16,
                                'condition': {'text': 'Clear', 'icon': '//cdn.weatherapi.com/weather/64x64/night/113.png'},
                                'chance_of_rain': 0
                            }
                            # More hours would be here in a real response
                        ]
                    }
                    # More days would be here in a real response
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Test checking weather with mocked response
        with mock.patch('builtins.print') as mock_print:
            result = self.planner.check_weather('London')
        
        # Verify the API was called
        mock_get.assert_called_once()
        
        # Verify print was called
        mock_print.assert_called()
        
        # Check the result
        self.assertIsInstance(result, dict)
        self.assertEqual(result['location']['name'], 'London')
    
    @mock.patch('weather_route_planner.requests.get')
    def test_check_weather_api_error(self, mock_get):
        """Test checking weather with API error."""
        # Mock the API error
        mock_get.side_effect = Exception("API Error")
        
        # Test checking weather with mocked error
        with mock.patch('builtins.print') as mock_print:
            result = self.planner.check_weather('London')
        
        # Verify print was called with error message
        mock_print.assert_called()
        
        # Check the result is None on error
        self.assertIsNone(result)
    
    @mock.patch('weather_route_planner.requests.get')
    def test_get_route(self, mock_get):
        """Test getting a route with mocked API."""
        # Mock the API response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'routes': [
                {
                    'legs': [
                        {
                            'distance': {'text': '10 km', 'value': 10000},
                            'duration': {'text': '30 mins', 'value': 1800},
                            'steps': [
                                {
                                    'html_instructions': 'Start cycling',
                                    'distance': {'text': '5 km', 'value': 5000},
                                    'duration': {'text': '15 mins', 'value': 900}
                                },
                                {
                                    'html_instructions': 'Turn right',
                                    'distance': {'text': '5 km', 'value': 5000},
                                    'duration': {'text': '15 mins', 'value': 900}
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Test getting a route with mocked response
        with mock.patch('builtins.print') as mock_print:
            result = self.planner.get_route('London', 'Cambridge')
        
        # Verify the API was called
        mock_get.assert_called_once()
        
        # Verify print was called
        mock_print.assert_called()
        
        # Check the result
        self.assertIsInstance(result, dict)
        self.assertEqual(result['routes'][0]['legs'][0]['distance']['text'], '10 km')
    
    @mock.patch('weather_route_planner.requests.get')
    def test_get_route_api_error(self, mock_get):
        """Test getting a route with API error."""
        # Mock the API error
        mock_get.side_effect = Exception("API Error")
        
        # Test getting a route with mocked error
        with mock.patch('builtins.print') as mock_print:
            result = self.planner.get_route('London', 'Cambridge')
        
        # Verify print was called with error message
        mock_print.assert_called()
        
        # Check the result is None on error
        self.assertIsNone(result)
    
    def test_calculate_cycling_eco_impact(self):
        """Test calculating cycling eco impact."""
        # Calculate impact for a known distance
        co2_saved, calories_burned = self.planner.calculate_cycling_eco_impact(10)
        
        # Verify the results
        self.assertGreater(co2_saved, 0)
        self.assertGreater(calories_burned, 0)
    
    def test_display_cycling_eco_impact(self):
        """Test displaying cycling eco impact."""
        # Test display function
        with mock.patch('builtins.print') as mock_print:
            self.planner.display_cycling_eco_impact(10)
        
        # Verify print was called
        mock_print.assert_called()

if __name__ == '__main__':
    unittest.main()