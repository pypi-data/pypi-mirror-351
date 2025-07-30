"""
EcoCycle - Weather Data Model

This module defines the WeatherData model classes, which represent weather data for cycling.
"""

from typing import Dict, List, Any, Optional, Tuple
import time
import datetime
import os
import json
import logging
import math

# Import configuration
from config.config import WEATHER_CACHE_FILE

# Configure logging
logger = logging.getLogger(__name__)

# Constants
WEATHER_CACHE_EXPIRY = 60 * 60  # 1 hour in seconds
# WEATHER_CACHE_FILE is now imported from config.config
DEFAULT_COORDINATES = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Berlin": (52.5200, 13.4050),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (-33.8688, 151.2093),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Cairo": (30.0444, 31.2357)
}


class WeatherData:
    """
    Model class representing weather data for a specific location.
    """

    def __init__(self, current: Dict[str, Any], forecast: Dict[str, Any], location: str = "Unknown"):
        """
        Initialize a WeatherData object.

        Args:
            current (Dict[str, Any]): Current weather data
            forecast (Dict[str, Any]): Forecast weather data
            location (str): Location name
        """
        self.current = current
        self.forecast = forecast
        self.location = location

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the WeatherData object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the WeatherData
        """
        return {
            "current": self.current,
            "forecast": self.forecast,
            "location": self.location
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherData':
        """
        Create a WeatherData object from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing weather data

        Returns:
            WeatherData: New WeatherData object
        """
        return cls(
            current=data.get("current", {}),
            forecast=data.get("forecast", {}),
            location=data.get("location", "Unknown")
        )

    def get_current_temperature(self) -> float:
        """
        Get the current temperature.

        Returns:
            float: Current temperature in Celsius
        """
        # Direct access to WeatherAPI.com format
        temp = self.current.get("temp_c", 0)

        # If temp_c is not available, try alternative keys that might be present
        if temp == 0 and "main" in self.current:
            # Try OpenWeatherMap format as fallback
            temp = self.current.get("main", {}).get("temp", 0)

        return temp

    def get_current_weather_condition(self) -> str:
        """
        Get the current weather condition.

        Returns:
            str: Current weather condition (e.g., "Clear", "Rain")
        """
        # Direct access to WeatherAPI.com format
        return self.current.get("condition", {}).get("text", "Unknown")

    def get_current_weather_description(self) -> str:
        """
        Get the current weather description.

        Returns:
            str: Current weather description (e.g., "Partly cloudy", "Light rain")
        """
        # Direct access to WeatherAPI.com format
        return self.current.get("condition", {}).get("text", "Unknown")

    def get_current_humidity(self) -> int:
        """
        Get the current humidity.

        Returns:
            int: Current humidity percentage
        """
        # Direct access to WeatherAPI.com format
        return self.current.get("humidity", 0)

    def get_current_visibility(self) -> float:
        """
        Get the current visibility.

        Returns:
            float: Current visibility in meters
        """
        # Direct access to WeatherAPI.com format (convert from km to meters)
        vis_km = self.current.get("vis_km", 10)  # Default to 10km if not available
        return vis_km * 1000

    def get_current_weather_icon(self) -> str:
        """
        Get the current weather icon.

        Returns:
            str: Current weather icon URL or code
        """
        # Direct access to WeatherAPI.com format
        icon = self.current.get("condition", {}).get("icon", "")
        if not icon:
            # Default icon if none found
            return "https://cdn.weatherapi.com/weather/64x64/day/113.png"

        # Make sure icon has the full URL if it doesn't already
        if not icon.startswith("http") and not icon.startswith("//"):
            icon = f"https://cdn.weatherapi.com/weather/64x64/day/{icon}"
        return icon

    def get_current_wind_speed(self) -> float:
        """
        Get the current wind speed.

        Returns:
            float: Current wind speed in m/s
        """
        # Direct access to WeatherAPI.com format (convert from kph to m/s)
        wind_kph = self.current.get("wind_kph", 0)
        return wind_kph / 3.6  # Convert kph to m/s

    def get_current_wind_direction(self) -> float:
        """
        Get the current wind direction.

        Returns:
            float: Current wind direction in degrees
        """
        # Direct access to WeatherAPI.com format
        return self.current.get("wind_degree", 0)

    def get_forecast_items(self) -> List[Dict[str, Any]]:
        """
        Get forecast items.

        Returns:
            List[Dict[str, Any]]: Forecast items
        """
        # WeatherAPI.com format handling
        # Check if we're using the proper WeatherAPI.com format or sample data
        if "forecastday" in self.forecast:
            # WeatherAPI.com format - extract daily forecasts from forecastday array
            forecastday = self.forecast.get("forecastday", [])
            forecast_items = []
            hourly_items = []

            for day in forecastday:
                # Extract all hourly forecasts for displaying next few hours
                hours = day.get("hour", [])
                if hours:
                    hourly_items.extend(hours)

                # Add the day forecast as an item (includes avgtemp_c, condition, etc.)
                day_item = {
                    "date": day.get("date"),
                    "date_epoch": day.get("date_epoch"),
                    "day": day.get("day", {}),
                    "astro": day.get("astro", {}),
                    "hour": hours  # Include all hours
                }

                forecast_items.append(day_item)

            # For hourly display, we return hourly items if that's what's being requested
            # This can be detected by the calling code by checking for the 'time' key in items
            # For example: if 'time' in items[0]
            if len(hourly_items) > 0:
                return hourly_items

            return forecast_items
        elif "list" in self.forecast:
            # This is the sample data format or older OpenWeatherMap format
            return self.forecast.get("list", [])
        else:
            # If neither recognized format is found, return an empty list
            logger.warning("Unrecognized forecast format in weather data")
            return []


class WeatherDataCollection:
    """
    Model class representing a collection of weather data with caching.
    """

    def __init__(self, cache_file: str = WEATHER_CACHE_FILE):
        """
        Initialize a WeatherDataCollection.

        Args:
            cache_file (str): Path to the cache file
        """
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        """
        Load cache from file.

        Returns:
            Dict[str, Any]: Loaded cache data
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading cache from {self.cache_file}: {e}")
        return {}

    def _save_cache(self) -> bool:
        """
        Save cache to file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.cache_file, 'w') as file:
                json.dump(self.cache, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving cache to {self.cache_file}: {e}")
            return False

    def is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid (not expired).

        Args:
            cache_key (str): Cache key to check

        Returns:
            bool: True if cache is valid, False otherwise
        """
        if cache_key not in self.cache:
            return False

        cached_time = self.cache[cache_key].get("timestamp", 0)
        current_time = time.time()

        return current_time - cached_time < WEATHER_CACHE_EXPIRY

    def get_from_cache(self, cache_key: str) -> Optional[WeatherData]:
        """
        Get weather data from cache.

        Args:
            cache_key (str): Cache key to retrieve

        Returns:
            Optional[WeatherData]: WeatherData object if found and valid, None otherwise
        """
        if not self.is_cache_valid(cache_key):
            return None

        try:
            data = self.cache[cache_key].get("data", {})
            return WeatherData.from_dict(data)
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None

    def add_to_cache(self, cache_key: str, weather_data: WeatherData) -> bool:
        """
        Add weather data to cache.

        Args:
            cache_key (str): Cache key to store under
            weather_data (WeatherData): WeatherData object to cache

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cache[cache_key] = {
                "data": weather_data.to_dict(),
                "timestamp": time.time()
            }
            return self._save_cache()
        except Exception as e:
            logger.error(f"Error adding to cache: {e}")
            return False

    def get_sample_weather_data(self, location_name: str = "Sample City") -> WeatherData:
        """
        Return sample weather data for demonstration purposes.
        Used when API key is not available.

        Args:
            location_name (str, optional): Location name to use. Defaults to "Sample City".

        Returns:
            WeatherData: Sample weather data
        """
        # Generate weather data based on the current date
        current_date = datetime.datetime.now()

        # Create sample current weather in WeatherAPI.com format
        current_weather = {
            "last_updated_epoch": int(time.time()),
            "last_updated": current_date.strftime("%Y-%m-%d %H:%M"),
            "temp_c": 22.5,
            "temp_f": 72.5,
            "is_day": 1,
            "condition": {
                "text": "Partly cloudy",
                "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png",
                "code": 1003
            },
            "wind_mph": 8.1,
            "wind_kph": 13.0,
            "wind_degree": 180,
            "wind_dir": "S",
            "pressure_mb": 1015.0,
            "pressure_in": 30.0,
            "precip_mm": 0.0,
            "precip_in": 0.0,
            "humidity": 65,
            "cloud": 25,
            "feelslike_c": 23.0,
            "feelslike_f": 73.4,
            "vis_km": 10.0,
            "vis_miles": 6.2,
            "uv": 5.0,
            "gust_mph": 10.5,
            "gust_kph": 16.9
        }

        # Create sample forecast in WeatherAPI.com format
        weather_types = ["Sunny", "Partly cloudy", "Patchy rain possible", "Sunny", "Cloudy"]
        condition_codes = [1000, 1003, 1063, 1000, 1006]
        condition_icons = ["113", "116", "176", "113", "119"]

        forecastday_list = []
        for i in range(5):
            forecast_date = current_date + datetime.timedelta(days=i)
            date_str = forecast_date.strftime("%Y-%m-%d")
            date_epoch = int(forecast_date.timestamp())

            # Create hourly forecasts for each day
            hours_list = []
            for hour in range(0, 24, 3):  # Every 3 hours
                hour_time = forecast_date.replace(hour=hour, minute=0, second=0)
                # Use simple temp variation based on time of day
                hour_f = float(hour)
                temp_variation = 5 * math.sin(hour_f / 24.0 * 2 * math.pi) if 'math' in globals() else hour_f % 12 - 6
                hour_data = {
                    "time_epoch": int(hour_time.timestamp()),
                    "time": hour_time.strftime("%Y-%m-%d %H:%M"),
                    "temp_c": 20.0 + temp_variation,
                    "temp_f": 68.0 + temp_variation * 1.8,
                    "is_day": 1 if 6 <= hour <= 18 else 0,
                    "condition": {
                        "text": weather_types[i % len(weather_types)],
                        "icon": f"//cdn.weatherapi.com/weather/64x64/{'day' if 6 <= hour <= 18 else 'night'}/{condition_icons[i % len(condition_icons)]}.png",
                        "code": condition_codes[i % len(condition_codes)]
                    },
                    "wind_mph": 8.1 + i,
                    "wind_kph": 13.0 + i * 1.6,
                    "wind_degree": 180 + i * 10,
                    "wind_dir": "S",
                    "pressure_mb": 1015.0,
                    "pressure_in": 30.0,
                    "precip_mm": 0.0 if i != 2 else 1.5,
                    "precip_in": 0.0 if i != 2 else 0.06,
                    "humidity": 65 - i * 2,
                    "cloud": 25 + i * 10,
                    "feelslike_c": 20.0 + temp_variation + 1,
                    "feelslike_f": 68.0 + (temp_variation + 1) * 1.8,
                    "windchill_c": 20.0 + temp_variation,
                    "windchill_f": 68.0 + temp_variation * 1.8,
                    "heatindex_c": 20.0 + temp_variation + 2,
                    "heatindex_f": 68.0 + (temp_variation + 2) * 1.8,
                    "dewpoint_c": 15.0,
                    "dewpoint_f": 59.0,
                    "will_it_rain": 1 if i == 2 else 0,
                    "chance_of_rain": 80 if i == 2 else 0,
                    "will_it_snow": 0,
                    "chance_of_snow": 0,
                    "vis_km": 10.0,
                    "vis_miles": 6.2,
                    "gust_mph": 10.5 + i,
                    "gust_kph": 16.9 + i * 1.6,
                    "uv": 5.0
                }
                hours_list.append(hour_data)

            # Create day summary
            day_data = {
                "date": date_str,
                "date_epoch": date_epoch,
                "day": {
                    "maxtemp_c": 25.0 + i,
                    "maxtemp_f": 77.0 + i * 1.8,
                    "mintemp_c": 15.0 + i,
                    "mintemp_f": 59.0 + i * 1.8,
                    "avgtemp_c": 20.0 + i,
                    "avgtemp_f": 68.0 + i * 1.8,
                    "maxwind_mph": 12.5 + i,
                    "maxwind_kph": 20.1 + i * 1.6,
                    "totalprecip_mm": 0.0 if i != 2 else 5.2,
                    "totalprecip_in": 0.0 if i != 2 else 0.2,
                    "totalsnow_cm": 0.0,
                    "avgvis_km": 10.0,
                    "avgvis_miles": 6.2,
                    "avghumidity": 65 - i * 2,
                    "daily_will_it_rain": 1 if i == 2 else 0,
                    "daily_chance_of_rain": 80 if i == 2 else 0,
                    "daily_will_it_snow": 0,
                    "daily_chance_of_snow": 0,
                    "condition": {
                        "text": weather_types[i % len(weather_types)],
                        "icon": f"//cdn.weatherapi.com/weather/64x64/day/{condition_icons[i % len(condition_icons)]}.png",
                        "code": condition_codes[i % len(condition_codes)]
                    },
                    "uv": 5.0
                },
                "astro": {
                    "sunrise": "06:30 AM",
                    "sunset": "07:30 PM",
                    "moonrise": "08:45 PM",
                    "moonset": "06:20 AM",
                    "moon_phase": "Full Moon",
                    "moon_illumination": "100",
                    "is_moon_up": 0,
                    "is_sun_up": 0
                },
                "hour": hours_list
            }
            forecastday_list.append(day_data)

        # Create a complete forecast object in WeatherAPI.com format
        forecast_data = {
            "forecastday": forecastday_list
        }

        return WeatherData(
            current=current_weather,
            forecast=forecast_data,
            location=location_name
        )
