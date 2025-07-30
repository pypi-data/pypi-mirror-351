#!/usr/bin/env python3
"""
Test script for geocoding functionality in the weather controller.
This script tests the geocoding functionality with various inputs.
"""

import os
import sys
import logging
from typing import Optional, Tuple

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("geocoding_test")

# Try to import the WeatherController class
try:
    from controllers.weather_controller import WeatherController
    logger.info("Successfully imported WeatherController")
except ImportError as e:
    logger.error(f"Error importing WeatherController: {e}")
    sys.exit(1)

def test_geocoding(location: str) -> Optional[Tuple[float, float]]:
    """Test geocoding for a specific location."""
    logger.info(f"Testing geocoding for location: '{location}'")

    # Create an instance of WeatherController
    controller = WeatherController()

    # Get coordinates for the location
    coords = controller.get_coordinates_for_location(location)

    if coords:
        lat, lon = coords
        logger.info(f"✅ Found coordinates for '{location}': {lat}, {lon}")
        return coords
    else:
        logger.error(f"❌ Could not find coordinates for '{location}'")
        return None

def test_weather_for_city(city: str) -> bool:
    """Test getting weather data for a specific city."""
    logger.info(f"Testing weather data for city: '{city}'")

    # Create an instance of WeatherController
    controller = WeatherController()

    # Get weather data for the city
    weather_data = controller.get_weather_for_city(city)

    if weather_data:
        logger.info(f"✅ Got weather data for '{city}'")
        logger.info(f"Temperature: {weather_data.get_current_temperature()}°C")
        logger.info(f"Condition: {weather_data.get_current_weather_condition()}")
        return True
    else:
        logger.error(f"❌ Could not get weather data for '{city}'")
        return False

def run_tests():
    """Run a series of tests for geocoding and weather data."""
    logger.info("Starting geocoding and weather data tests")

    # Test valid locations
    valid_locations = [
        "New York",
        "London",
        "Tokyo",
        "Paris",
        "Sydney"
    ]

    # Test problematic locations
    problematic_locations = [
        "",  # Empty string
        "XYZ123",  # Non-existent location
        "Small Village, Middle of Nowhere",  # Very specific location
        "123 Main St"  # Street address without city
    ]

    # Test valid locations
    logger.info("\n=== Testing Valid Locations ===")
    valid_results = {}
    for location in valid_locations:
        valid_results[location] = test_geocoding(location) is not None

    # Test problematic locations
    logger.info("\n=== Testing Problematic Locations ===")
    problem_results = {}
    for location in problematic_locations:
        problem_results[location] = test_geocoding(location) is not None

    # Test weather data for valid locations
    logger.info("\n=== Testing Weather Data for Valid Locations ===")
    weather_results = {}
    for location in valid_locations:
        weather_results[location] = test_weather_for_city(location)

    # Print summary
    logger.info("\n=== Test Results Summary ===")
    logger.info("Valid Locations Geocoding:")
    for location, success in valid_results.items():
        logger.info(f"  {location}: {'✅ PASS' if success else '❌ FAIL'}")

    logger.info("\nProblematic Locations Geocoding:")
    for location, success in problem_results.items():
        location_display = location if location else "'empty string'"
        logger.info(f"  {location_display}: {'✅ PASS' if success else '❌ FAIL'}")

    logger.info("\nWeather Data:")
    for location, success in weather_results.items():
        logger.info(f"  {location}: {'✅ PASS' if success else '❌ FAIL'}")

if __name__ == "__main__":
    run_tests()
