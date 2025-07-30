#!/usr/bin/env python3
"""
Weather API Debug Script - To test direct WeatherAPI.com integration
"""

import os
import sys
import json
import logging
import re
from typing import Dict, Any, Optional

# Helper function to load variables from .env file
def load_env_file(env_path=".env"):
    """Load environment variables from .env file"""
    if not os.path.exists(env_path):
        return False
        
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Simple parsing to handle basic KEY=VALUE format
            # Ignores comments at the end of lines
            match = re.match(r'^([^=]+)=([^#]+)', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip().strip('"').strip("'")
                os.environ[key] = value
                
    return True

# Configure logging to show detailed output
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("weather_debug")

try:
    import requests
except ImportError:
    logger.error("Requests package not available. Install with: pip install requests")
    sys.exit(1)

# Load environment variables from .env file
env_loaded = load_env_file()
if env_loaded:
    logger.info("Loaded environment variables from .env file")
else:
    logger.warning(".env file not found, using existing environment variables")

# Read API key from environment
api_key = os.environ.get("WEATHER_API_KEY", "")
if not api_key:
    logger.error("No WeatherAPI.com API key found in environment variables")
    logger.info("Please set WEATHER_API_KEY in your environment or .env file")
    sys.exit(1)
else:
    # Mask key for security while still showing some characters to verify
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
    logger.info(f"Using WeatherAPI.com API key: {masked_key}")

def test_direct_api_request(city: str = "Singapore"):
    """Test direct API request to WeatherAPI.com"""
    logger.info(f"Testing direct API request for: {city}")
    
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3&aqi=yes&alerts=yes"
        logger.info(f"Making request to WeatherAPI.com for {city}")
        
        response = requests.get(url)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"API Error: {response.text}")
            return None
            
        data = response.json()
        
        # Check if we have the expected data
        if 'current' not in data:
            logger.error("Response missing 'current' data")
            logger.info(f"Response keys: {list(data.keys())}")
            return None
            
        # Extract and display key weather information
        current = data.get('current', {})
        location = data.get('location', {})
        
        logger.info(f"Weather for {location.get('name', 'Unknown')}, {location.get('country', '')}")
        logger.info(f"Temperature: {current.get('temp_c')}°C")
        logger.info(f"Condition: {current.get('condition', {}).get('text', 'Unknown')}")
        logger.info(f"Wind: {current.get('wind_kph')} kph, {current.get('wind_dir', '?')}")
        logger.info(f"Humidity: {current.get('humidity')}%")
        
        # Save raw response for inspection
        with open(f"weather_debug_{city.lower()}.json", 'w') as f:
            json.dump(data, f, indent=2)
            logger.info(f"Saved raw response to weather_debug_{city.lower()}.json")
            
        return data
    except Exception as e:
        logger.error(f"Error making API request: {e}")
        return None

def test_multiple_cities():
    """Test API with multiple cities"""
    cities = ["Singapore", "New York", "London", "Tokyo"]
    results = {}
    
    for city in cities:
        logger.info(f"{'='*20} Testing {city} {'='*20}")
        result = test_direct_api_request(city)
        results[city] = result is not None
        
    # Print summary
    logger.info("\nTest results summary:")
    for city, success in results.items():
        logger.info(f"{city}: {'SUCCESS' if success else 'FAILED'}")
    
    return results

if __name__ == "__main__":
    logger.info("Starting WeatherAPI.com debug script")
    
    # If city provided as command line arg, use it
    if len(sys.argv) > 1:
        city = sys.argv[1]
        test_direct_api_request(city)
    else:
        # Otherwise test multiple cities
        test_multiple_cities()
