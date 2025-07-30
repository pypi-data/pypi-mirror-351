"""
EcoCycle - Weather Controller

This module defines the WeatherController class, which handles the business logic for weather data.
"""

import os
import logging
from typing import Dict, Optional, Tuple

# Import dependency_manager for ensuring packages
from core.dependency import dependency_manager

# Use dependency manager to check for requests availability
REQUESTS_AVAILABLE = dependency_manager.is_package_installed('requests', force_check=True)

# Try to import requests if available
try:
    import requests
except ImportError:
    requests = None

from models.weather_data import WeatherData, WeatherDataCollection, DEFAULT_COORDINATES

# Add Singapore to DEFAULT_COORDINATES if not already included
DEFAULT_COORDINATES.update({
    "Singapore": (1.3521, 103.8198),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (-33.8688, 151.2093),
    "Berlin": (52.5200, 13.4050),
    "Paris": (48.8566, 2.3522),
    "Rome": (41.9028, 12.4964)
})

# Configure logging
logger = logging.getLogger(__name__)

# Note: API keys are now loaded dynamically to ensure they pick up environment changes
# This fixes the issue where module-level constants cache old environment variable values


class WeatherController:
    """
    Controller class for handling weather data business logic.
    """

    def __init__(self, weather_collection: Optional[WeatherDataCollection] = None):
        """
        Initialize a WeatherController.

        Args:
            weather_collection (Optional[WeatherDataCollection]): Collection of weather data to use
        """
        global REQUESTS_AVAILABLE
        self.weather_collection = weather_collection or WeatherDataCollection()

        # Check again if requests is available, with a fresh check
        # We reset the cache for this package to ensure we get the current state
        dependency_manager.reset_package_cache('requests')
        self.requests_available = dependency_manager.is_package_installed('requests', force_check=True)
        REQUESTS_AVAILABLE = self.requests_available

        # Try to ensure the requests package is installed if not available
        if not self.requests_available:
            logger.info("Requests package not available, attempting to install")

            # Use dependency_manager to install requests via the route_planning feature
            success, failed = dependency_manager.ensure_feature('route_planning', silent=False)

            if success and 'requests' not in failed:
                # If installation was successful, update the availability flag
                logger.info("Successfully installed requests package")

                # Force a refresh of the package cache for 'requests'
                dependency_manager.reset_package_cache('requests')
                self.requests_available = dependency_manager.is_package_installed('requests', force_check=True)
                REQUESTS_AVAILABLE = self.requests_available

                if self.requests_available:
                    # Import requests now that it's available
                    global requests
                    import requests
                    logger.info("Successfully imported requests package")
            else:
                logger.warning(f"Failed to install requests package: {failed}")

    def _get_weather_api_key(self) -> str:
        """Get WeatherAPI key dynamically from environment."""
        return os.environ.get("WEATHER_API_KEY", "")

    def _get_openweathermap_api_key(self) -> str:
        """Get OpenWeatherMap API key dynamically from environment."""
        return os.environ.get("OPENWEATHERMAP_API_KEY", "")

    def _get_google_maps_api_key(self) -> str:
        """Get Google Maps API key dynamically from environment."""
        return os.environ.get("GOOGLE_MAPS_API_KEY", "")

    def _parse_current_location_format(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Parse coordinates from "Current Location (lat, lon)" format.

        Args:
            location (str): Location string to parse

        Returns:
            Optional[Tuple[float, float]]: Coordinates if successfully parsed, None otherwise
        """
        import re

        # Pattern to match "Current Location (lat, lon)" format
        pattern = r"Current Location \((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)"
        match = re.match(pattern, location)

        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                logger.debug(f"Parsed coordinates from '{location}': {lat}, {lon}")
                return (lat, lon)
            except ValueError as e:
                logger.error(f"Error parsing coordinates from '{location}': {e}")
                return None

        return None

    def get_coordinates_for_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a location name using multiple services for redundancy.

        Args:
            location (str): Location name

        Returns:
            Optional[Tuple[float, float]]: Coordinates (latitude, longitude) if found, None otherwise
        """
        # Log the location being searched
        logger.info(f"Searching for coordinates for location: '{location}'")

        # Validate input
        if not location or not isinstance(location, str):
            logger.error(f"Invalid location input: {location}")
            return None

        # Clean the location string (remove extra spaces, etc.)
        location = location.strip()
        if not location:
            logger.error("Empty location after cleaning")
            return None

        # Check if this is a "Current Location" format with coordinates
        coords = self._parse_current_location_format(location)
        if coords:
            logger.info(f"Parsed coordinates from current location format: {coords}")
            return coords

        # Check if it's a default location (case-insensitive)
        for default_location, coords in DEFAULT_COORDINATES.items():
            if location.lower() == default_location.lower():
                logger.info(f"Found coordinates for '{location}' in defaults: {coords}")
                return coords

        if not self.requests_available:
            logger.warning("Requests package not available, cannot look up coordinates")
            return None

        # Method 1: Try using OpenWeatherMap Geocoding API
        openweathermap_key = self._get_openweathermap_api_key()
        if openweathermap_key and requests is not None:
            try:
                logger.info(f"Trying OpenWeatherMap Geocoding API for '{location}'")
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={openweathermap_key}"
                geo_response = requests.get(geo_url)
                geo_data = geo_response.json()

                if geo_data and len(geo_data) > 0:
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]
                    logger.info(f"Found coordinates for '{location}' via OpenWeatherMap: {lat}, {lon}")
                    return (lat, lon)
                else:
                    logger.warning(f"OpenWeatherMap returned no results for '{location}'")
            except Exception as e:
                logger.error(f"Error getting coordinates from OpenWeatherMap: {e}")

        # Method 2: Try using Google Geocoding API as fallback
        google_maps_key = self._get_google_maps_api_key()
        if google_maps_key and requests is not None:
            try:
                logger.info(f"Trying Google Geocoding API for '{location}'")
                # Check if API key is properly formatted
                if len(google_maps_key) < 10:  # Simple check for key validity
                    logger.error(f"Google Maps API key appears to be invalid: {google_maps_key[:4]}...")

                geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={google_maps_key}"
                response = requests.get(geo_url)
                data = response.json()

                if data['status'] == 'OK':
                    latlng = data['results'][0]['geometry']['location']
                    lat, lon = latlng['lat'], latlng['lng']
                    logger.info(f"Found coordinates for '{location}' via Google Maps: {lat}, {lon}")
                    return (lat, lon)
                else:
                    # Log more details about the error
                    error_message = data.get('error_message', 'No error message provided')
                    logger.error(f"Google Geocoding API error: {data['status']} - {error_message}")

                    # Provide more specific guidance based on the error
                    if data['status'] == 'ZERO_RESULTS':
                        logger.warning(f"Google couldn't find any location matching '{location}'. Try a more specific or well-known location name.")
                    elif data['status'] == 'INVALID_REQUEST':
                        logger.error("Invalid request to Google Geocoding API. Check the location format.")
                    elif data['status'] == 'REQUEST_DENIED':
                        logger.error("Google Geocoding API request denied. Check if your API key is valid and has the Geocoding API enabled.")
                    elif data['status'] == 'OVER_QUERY_LIMIT':
                        logger.error("Google Geocoding API query limit exceeded. Try again later or check your API usage limits.")
            except Exception as e:
                logger.error(f"Error getting coordinates from Google Maps: {e}")

        # Method 3: Try using WeatherAPI.com Geocoding (if available)
        weather_api_key = self._get_weather_api_key()
        if weather_api_key and requests is not None:
            try:
                logger.info(f"Trying WeatherAPI.com Geocoding for '{location}'")
                geo_url = f"http://api.weatherapi.com/v1/search.json?key={weather_api_key}&q={location}"
                response = requests.get(geo_url)
                data = response.json()

                if data and len(data) > 0:
                    lat = data[0]['lat']
                    lon = data[0]['lon']
                    logger.info(f"Found coordinates for '{location}' via WeatherAPI: {lat}, {lon}")
                    return (float(lat), float(lon))
                else:
                    logger.warning(f"WeatherAPI.com returned no results for '{location}'")
            except Exception as e:
                logger.error(f"Error getting coordinates from WeatherAPI: {e}")

        # Method 4: Try free Nominatim service (OpenStreetMap) as last resort
        if requests is not None:
            try:
                logger.info(f"Trying Nominatim (OpenStreetMap) for '{location}'")
                geo_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
                headers = {"User-Agent": "EcoCycle/1.0"}
                response = requests.get(geo_url, headers=headers)
                data = response.json()

                if data and len(data) > 0:
                    lat = data[0]['lat']
                    lon = data[0]['lon']
                    logger.info(f"Found coordinates for '{location}' via Nominatim: {lat}, {lon}")
                    return (float(lat), float(lon))
                else:
                    logger.warning(f"Nominatim returned no results for '{location}'")
            except Exception as e:
                logger.error(f"Error getting coordinates from Nominatim: {e}")

        # If we get here, we couldn't get coordinates from any source
        logger.error(f"Could not find coordinates for '{location}' using any available service")
        logger.info("Suggestions: 1) Check spelling 2) Use a more specific location 3) Try a nearby major city")
        return None

    def get_location_name_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """
        Get a readable location name from coordinates using reverse geocoding.

        Args:
            lat (float): Latitude
            lon (float): Longitude

        Returns:
            Optional[str]: Location name if found, None otherwise
        """
        if not self.requests_available:
            logger.warning("Requests library not available, cannot perform reverse geocoding")
            return None

        # Method 1: Try Google Reverse Geocoding API
        google_maps_key = self._get_google_maps_api_key()
        if google_maps_key and requests is not None:
            try:
                logger.info(f"Trying Google Reverse Geocoding for coordinates: {lat}, {lon}")
                geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={google_maps_key}"
                response = requests.get(geo_url)
                data = response.json()

                if data['status'] == 'OK' and data['results']:
                    # Get the most appropriate result (usually the first one)
                    result = data['results'][0]
                    formatted_address = result.get('formatted_address', '')

                    # Try to get a more specific location name from address components
                    components = result.get('address_components', [])
                    neighborhood = None
                    sublocality = None
                    locality = None
                    administrative_area = None
                    country = None

                    for component in components:
                        types = component.get('types', [])
                        name = component.get('long_name')

                        # Get neighborhood/area information (most specific)
                        if 'neighborhood' in types:
                            neighborhood = name
                        elif 'sublocality' in types or 'sublocality_level_1' in types:
                            sublocality = name
                        # Get city/locality information
                        elif 'locality' in types:
                            locality = name
                        elif 'administrative_area_level_1' in types:
                            administrative_area = name
                        # Get country
                        elif 'country' in types:
                            country = name

                    # Build location name with increasing specificity
                    location_parts = []

                    # Add the most specific area first
                    if neighborhood:
                        location_parts.append(neighborhood)
                    elif sublocality:
                        location_parts.append(sublocality)

                    # Add city/locality
                    if locality:
                        location_parts.append(locality)
                    elif administrative_area:
                        location_parts.append(administrative_area)

                    # Add country
                    if country:
                        location_parts.append(country)

                    # Format the location name
                    if location_parts:
                        location_name = ", ".join(location_parts)
                    elif formatted_address:
                        # Fallback: use first two parts of formatted address for more detail
                        address_parts = [part.strip() for part in formatted_address.split(',')]
                        if len(address_parts) >= 2:
                            location_name = f"{address_parts[0]}, {address_parts[1]}"
                        else:
                            location_name = address_parts[0] if address_parts else formatted_address
                    else:
                        location_name = formatted_address

                    logger.info(f"Found location name via Google: {location_name}")
                    return location_name
                else:
                    logger.warning(f"Google Reverse Geocoding returned status: {data.get('status', 'Unknown')}")
            except Exception as e:
                logger.error(f"Error with Google Reverse Geocoding: {e}")

        # Method 2: Try Nominatim (OpenStreetMap) reverse geocoding as fallback
        if requests is not None:
            try:
                logger.info(f"Trying Nominatim reverse geocoding for coordinates: {lat}, {lon}")
                geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
                headers = {"User-Agent": "EcoCycle/1.0"}
                response = requests.get(geo_url, headers=headers)
                data = response.json()

                if 'display_name' in data:
                    display_name = data['display_name']

                    # Try to extract a more readable name from the display_name
                    address = data.get('address', {})

                    # Get various levels of location detail
                    neighborhood = address.get('neighbourhood') or address.get('suburb')
                    road = address.get('road')
                    city = address.get('city') or address.get('town') or address.get('village')
                    state = address.get('state')
                    country = address.get('country')

                    # Build location name with specificity
                    location_parts = []

                    # Add the most specific area first
                    if neighborhood:
                        location_parts.append(neighborhood)
                    elif road:
                        # Use road name if no neighborhood but be selective
                        if not any(word in road.lower() for word in ['unnamed', 'service', 'access']):
                            location_parts.append(road)

                    # Add city
                    if city:
                        location_parts.append(city)
                    elif state:
                        location_parts.append(state)

                    # Add country
                    if country:
                        location_parts.append(country)

                    # Format the location name
                    if location_parts:
                        location_name = ", ".join(location_parts)
                    else:
                        # Fallback: use first two parts of display name
                        display_parts = [part.strip() for part in display_name.split(',')]
                        if len(display_parts) >= 2:
                            location_name = f"{display_parts[0]}, {display_parts[1]}"
                        else:
                            location_name = display_parts[0] if display_parts else display_name

                    logger.info(f"Found location name via Nominatim: {location_name}")
                    return location_name
                else:
                    logger.warning("Nominatim reverse geocoding returned no display_name")
            except Exception as e:
                logger.error(f"Error with Nominatim reverse geocoding: {e}")

        # If all methods fail, return None
        logger.warning(f"Could not find location name for coordinates: {lat}, {lon}")
        return None

    def get_current_location_coordinates(self) -> Optional[Tuple[float, float]]:
        """
        Try to get current location coordinates via IP using multiple services for reliability.

        Returns:
            Optional[Tuple[float, float]]: Coordinates (latitude, longitude) if found, None otherwise
        """
        if not self.requests_available:
            logger.warning("Requests library not available, cannot get current location")
            return None

        # List of IP geolocation services to try (in order of preference)
        services = [
            {
                'name': 'ipinfo.io',
                'url': 'https://ipinfo.io/json',
                'timeout': 5,
                'parse_func': self._parse_ipinfo_response
            },
            {
                'name': 'ip-api.com',
                'url': 'http://ip-api.com/json',
                'timeout': 5,
                'parse_func': self._parse_ipapi_response
            },
            {
                'name': 'ipapi.co',
                'url': 'https://ipapi.co/json',
                'timeout': 5,
                'parse_func': self._parse_ipapico_response
            }
        ]

        for service in services:
            if requests is not None:
                try:
                    logger.info(f"Trying {service['name']} for current location...")
                    response = requests.get(
                        service['url'],
                        timeout=service['timeout'],
                        headers={'User-Agent': 'EcoCycle/1.0'}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        coords = service['parse_func'](data)
                        if coords:
                            lat, lon = coords
                            logger.info(f"Current location detected via {service['name']}: {lat:.4f}, {lon:.4f}")
                            return coords
                    else:
                        logger.warning(f"{service['name']} returned status code: {response.status_code}")

                except Exception as e:
                    # Handle all exceptions including requests-specific ones
                    if requests is not None and hasattr(requests, 'exceptions'):
                        if isinstance(e, requests.exceptions.Timeout):
                            logger.warning(f"{service['name']} request timed out")
                        elif isinstance(e, requests.exceptions.ConnectionError):
                            logger.warning(f"Connection error with {service['name']}")
                        else:
                            logger.warning(f"Error with {service['name']}: {e}")
                    else:
                        logger.warning(f"Error with {service['name']}: {e}")
            else:
                logger.warning(f"Requests not available, skipping {service['name']}")

        logger.warning("Could not determine current location from any IP geolocation service")
        return None

    def get_current_location_with_name(self) -> Optional[Tuple[Tuple[float, float], str]]:
        """
        Get current location coordinates and a readable location name.

        Returns:
            Optional[Tuple[Tuple[float, float], str]]: ((lat, lon), location_name) if found, None otherwise
        """
        # Get current coordinates
        coords = self.get_current_location_coordinates()
        if not coords:
            return None

        lat, lon = coords

        # Try to get a readable location name
        location_name = self.get_location_name_from_coordinates(lat, lon)

        if location_name:
            logger.info(f"Current location: {location_name} ({lat:.4f}, {lon:.4f})")
            return (coords, location_name)
        else:
            # Fallback to coordinates format if reverse geocoding fails
            fallback_name = f"Current Location ({lat:.4f}, {lon:.4f})"
            logger.info(f"Using fallback location name: {fallback_name}")
            return (coords, fallback_name)

    def _parse_ipinfo_response(self, data: dict) -> Optional[Tuple[float, float]]:
        """Parse response from ipinfo.io"""
        try:
            coordinates = data.get("loc", "").split(",")
            if len(coordinates) == 2:
                lat, lon = float(coordinates[0]), float(coordinates[1])
                city = data.get('city', 'Unknown')
                region = data.get('region', 'Unknown')
                logger.debug(f"Location from ipinfo.io: {city}, {region}")
                return (lat, lon)
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing ipinfo.io response: {e}")
        return None

    def _parse_ipapi_response(self, data: dict) -> Optional[Tuple[float, float]]:
        """Parse response from ip-api.com"""
        try:
            if data.get('status') == 'success':
                lat = float(data.get('lat', 0))
                lon = float(data.get('lon', 0))
                city = data.get('city', 'Unknown')
                region = data.get('regionName', 'Unknown')
                logger.debug(f"Location from ip-api.com: {city}, {region}")
                return (lat, lon)
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing ip-api.com response: {e}")
        return None

    def _parse_ipapico_response(self, data: dict) -> Optional[Tuple[float, float]]:
        """Parse response from ipapi.co"""
        try:
            lat = float(data.get('latitude', 0))
            lon = float(data.get('longitude', 0))
            city = data.get('city', 'Unknown')
            region = data.get('region', 'Unknown')
            logger.debug(f"Location from ipapi.co: {city}, {region}")
            return (lat, lon)
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing ipapi.co response: {e}")
        return None

    def get_weather_data(self, lat: Optional[float] = None, lon: Optional[float] = None, location_name: Optional[str] = None) -> WeatherData:
        """
        Get weather data for coordinates or location name using WeatherAPI.com.

        Args:
            lat (Optional[float]): Latitude, can be None if location_name is provided
            lon (Optional[float]): Longitude, can be None if location_name is provided
            location_name (Optional[str]): Location name. If not provided, it will be extracted from the API response.

        Returns:
            WeatherData: Weather data for the location
        """
        # Validate input - we need either coordinates or a location name
        if (lat is None or lon is None) and not location_name:
            logger.error("Neither coordinates nor location name provided")
            return self.weather_collection.get_sample_weather_data("Unknown Location")

        # Create cache key based on available parameters
        if lat is not None and lon is not None:
            cache_key = f"{lat},{lon}"
        elif location_name:
            cache_key = location_name
        else:
            cache_key = "unknown"

        # Check cache for weather data
        cached_data = self.weather_collection.get_from_cache(cache_key)
        if cached_data:
            logger.debug(f"Retrieved weather from cache for {cache_key}")
            return cached_data

        # Check if we have the WeatherAPI key
        weather_api_key = self._get_weather_api_key()
        # Print the API key value to help with debugging (but hide most of it for security)
        key_start = weather_api_key[:4] if weather_api_key and len(weather_api_key) > 4 else ""
        key_end = weather_api_key[-4:] if weather_api_key and len(weather_api_key) > 4 else ""
        logger.info(f"Using WeatherAPI key: {key_start}...{key_end}")

        if not weather_api_key:
            logger.warning("WeatherAPI key not set")
            logger.info("To use actual weather data, set the WEATHER_API_KEY environment variable")
            logger.info("You can get a free API key from https://www.weatherapi.com/")
            return self.weather_collection.get_sample_weather_data(location_name or "Unknown Location")

        if not self.requests_available:
            logger.warning("Requests library not available")
            logger.info("To use actual weather data, install the requests library: pip install requests")
            return self.weather_collection.get_sample_weather_data(location_name or "Unknown Location")

        try:
            # Get current weather and forecast in one call using WeatherAPI.com
            # Format: q=lat,lon for coordinates, but can also accept city names directly
            if lat is not None and lon is not None:
                q_param = f"{lat},{lon}"
                logger.info(f"Using coordinates for weather lookup: {lat}, {lon}")
            elif location_name:
                q_param = location_name
                logger.info(f"Using location name for weather lookup: {location_name}")
            else:
                logger.error("No valid location information provided")
                return self.weather_collection.get_sample_weather_data("Unknown Location")

            # Build the API URL without showing the API key in logs
            weather_url = f"http://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={q_param}&days=7&aqi=yes&alerts=yes"
            logger.info(f"Making WeatherAPI request for location: {q_param}")

            # Make the API request
            if requests is not None:
                response = requests.get(weather_url)
                logger.info(f"WeatherAPI response status: {response.status_code}")
            else:
                logger.error("Requests library not available for API call")
                return self.weather_collection.get_sample_weather_data(location_name or "Unknown Location")

            if response.status_code != 200:
                error_message = "Unknown error"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_message = error_data['error'].get('message', 'Unknown error')
                except:
                    error_message = response.text

                logger.error(f"WeatherAPI error: {response.status_code} - {error_message}")

                # Provide more helpful error messages based on status code
                if response.status_code == 401:
                    logger.error("Authentication failed. Please check your API key.")
                elif response.status_code == 403:
                    logger.error("Access forbidden. Your API key may have exceeded its quota or been disabled.")
                elif response.status_code == 429:
                    logger.error("Too many requests. You've exceeded the rate limit for your API key.")

                return self.weather_collection.get_sample_weather_data(location_name or "Unknown Location")

            # Get the raw API response data
            weather_data_json = response.json()

            # Log detailed weather information for debugging
            current = weather_data_json.get('current', {})
            location_data = weather_data_json.get('location', {})

            logger.info(f"Weather received for {location_data.get('name', 'Unknown')}, {location_data.get('country', '')}")
            logger.info(f"Temperature: {current.get('temp_c')}°C")
            logger.info(f"Condition: {current.get('condition', {}).get('text', 'Unknown')}")
            logger.info(f"Wind: {current.get('wind_kph')} kph, {current.get('wind_dir', '?')}")
            logger.info(f"Humidity: {current.get('humidity')}%")

            # Extract location name if not provided
            if not location_name:
                location_name = f"{location_data.get('name', 'Unknown')}, {location_data.get('country', '')}"

            # Create a WeatherData object with the raw current and forecast data
            weather_data = WeatherData(current, weather_data_json.get('forecast', {}), location_name)

            # Cache the data
            self.weather_collection.add_to_cache(cache_key, weather_data)

            logger.debug(f"Retrieved weather data from WeatherAPI.com for {q_param}")
            return weather_data

        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            logger.debug("Using sample weather data due to error")
            return self.weather_collection.get_sample_weather_data(location_name or "Unknown Location")

    def _transform_weatherapi_current(self, current: Dict, location: Dict) -> Dict:
        """
        Transform WeatherAPI.com current weather format to OpenWeatherMap format for compatibility.

        Args:
            current: The 'current' section from WeatherAPI.com response
            location: The 'location' section from WeatherAPI.com response

        Returns:
            Dict: Weather data in OpenWeatherMap format for compatibility
        """
        # Get temperature with fallback to default value
        temp_c = current.get("temp_c", 20.0)  # Default to 20°C if not available

        # Create a structure compatible with our existing WeatherData class
        transformed = {
            "coord": {"lat": location.get("lat"), "lon": location.get("lon")},
            "weather": [{
                "id": 800,  # Default clear sky
                "main": current.get("condition", {}).get("text", "Clear"),
                "description": current.get("condition", {}).get("text", "Clear sky"),
                "icon": current.get("condition", {}).get("icon", "01d").split("/")[-1]
            }],
            "main": {
                "temp": temp_c,
                "feels_like": current.get("feelslike_c", temp_c),
                "temp_min": temp_c - 1.0,  # Estimate
                "temp_max": temp_c + 1.0,  # Estimate
                "pressure": current.get("pressure_mb", 1013),
                "humidity": current.get("humidity", 50)
            },
            "wind": {
                "speed": current.get("wind_kph", 0) / 3.6,  # Convert to m/s
                "deg": current.get("wind_degree", 0),
                "gust": current.get("gust_kph", 0) / 3.6  # Convert to m/s
            },
            "clouds": {"all": current.get("cloud", 0)},
            "visibility": current.get("vis_km", 10) * 1000,  # Convert to meters
            "dt": current.get("last_updated_epoch", 0),
            "sys": {
                "country": location.get("country", "Unknown"),
                "sunrise": 0,  # Not provided directly
                "sunset": 0  # Not provided directly
            },
            "name": location.get("name", "Unknown"),
            "timezone": location.get("localtime_epoch", 0) - location.get("last_updated_epoch", 0)
        }

        return transformed

    def _transform_weatherapi_forecast(self, forecast: Dict) -> Dict:
        """
        Transform WeatherAPI.com forecast format to OpenWeatherMap format for compatibility.

        Args:
            forecast: The 'forecast' section from WeatherAPI.com response

        Returns:
            Dict: Forecast data in OpenWeatherMap format for compatibility
        """
        # Create a structure compatible with our existing WeatherData class expectations
        transformed = {
            "list": []
        }

        # Process each day in the forecast
        if "forecastday" in forecast:
            for day in forecast["forecastday"]:
                # Get day data with fallbacks
                day_data = day.get("day", {})
                hour_data = day.get("hour", [])

                # Get min/max temps with fallbacks
                min_temp = day_data.get("mintemp_c", 15.0)  # Default to 15°C if not available
                max_temp = day_data.get("maxtemp_c", 25.0)  # Default to 25°C if not available

                # Use hourly data if available
                for hour in hour_data:
                    hour_timestamp = hour.get("time_epoch", 0)
                    # Get hourly temp with fallback
                    hour_temp = hour.get("temp_c", 20.0)  # Default to 20°C if not available

                    entry = {
                        "dt": hour_timestamp,
                        "main": {
                            "temp": hour_temp,
                            "feels_like": hour.get("feelslike_c", hour_temp),
                            "temp_min": min_temp,
                            "temp_max": max_temp,
                            "pressure": hour.get("pressure_mb", 1013),
                            "humidity": hour.get("humidity", 50)
                        },
                        "weather": [{
                            "id": 800,  # Default
                            "main": hour.get("condition", {}).get("text", "Clear"),
                            "description": hour.get("condition", {}).get("text", "Clear sky"),
                            "icon": hour.get("condition", {}).get("icon", "01d").split("/")[-1]
                        }],
                        "clouds": {"all": hour.get("cloud", 0)},
                        "wind": {
                            "speed": hour.get("wind_kph", 0) / 3.6,  # Convert to m/s
                            "deg": hour.get("wind_degree", 0)
                        },
                        "visibility": hour.get("vis_km", 10) * 1000,  # Convert to meters
                        "pop": hour.get("chance_of_rain", 0) / 100,  # Convert percentage to decimal
                        "sys": {"pod": "d" if hour.get("is_day", 0) == 1 else "n"},
                        "dt_txt": hour.get("time", "")
                    }
                    transformed["list"].append(entry)

        return transformed

    def get_cycling_recommendation(self, weather_data: WeatherData) -> str:
        """
        Get cycling recommendation based on weather conditions.

        Args:
            weather_data (WeatherData): Weather data to analyze

        Returns:
            str: Cycling recommendation
        """
        temp = weather_data.get_current_temperature()
        weather = weather_data.get_current_weather_condition()
        wind_speed = weather_data.get_current_wind_speed()

        # Bad weather conditions
        if weather in ["Thunderstorm", "Tornado", "Hurricane", "Snow", "Sleet", "Hail"]:
            return "Not recommended - Dangerous weather conditions"

        if weather in ["Heavy Rain", "Freezing Rain"]:
            return "Not recommended - Heavy rain conditions"

        # Temperature considerations
        if temp < 0:
            return "Challenging - Very cold, dress in layers and protect extremities"

        if temp < 5:
            return "Challenging - Cold conditions, dress warmly"

        if temp > 35:
            return "Challenging - Very hot, stay hydrated and avoid midday rides"

        # Wind considerations
        if wind_speed > 40:
            return "Not recommended - Dangerously high winds"

        if wind_speed > 25:
            return "Challenging - Strong winds, be cautious"

        # Light rain
        if weather in ["Rain", "Drizzle"]:
            return "Fair - Light rain, use fenders and water-resistant gear"

        # Ideal conditions
        if 10 <= temp <= 25 and weather in ["Clear", "Clouds", "Mist"] and wind_speed < 15:
            return "Excellent - Ideal conditions for cycling"

        # Good conditions
        if 5 <= temp <= 30 and weather not in ["Rain", "Drizzle"] and wind_speed < 20:
            return "Good - Favorable conditions for cycling"

        # Default
        return "Fair - Acceptable conditions but be prepared"

    def get_wind_direction_text(self, degrees: float) -> str:
        """
        Convert wind direction in degrees to cardinal direction.

        Args:
            degrees (float): Wind direction in degrees

        Returns:
            str: Cardinal direction (e.g., "N", "NE")
        """
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

        index = round(degrees / 22.5) % 16
        return directions[index]

    def get_current_weather(self) -> Optional[WeatherData]:
        """
        Get current weather using the user's selected or current location.

        Returns:
            Optional[WeatherData]: Weather data for current location or None if not available
        """
        # Try to get current location via IP
        coords = self.get_current_location_coordinates()
        if coords:
            lat, lon = coords
            logger.info(f"Using current location coordinates: {lat}, {lon}")
            return self.get_weather_data(lat=lat, lon=lon, location_name="Current Location")
        else:
            logger.warning("Could not get current location, falling back to default")
            # Fall back to a default (New York City)
            logger.info("Using default location (New York City)")
            return self.get_weather_data(lat=40.7128, lon=-74.0060, location_name="New York (Default)")

    def get_weather_for_city(self, city: str) -> Optional[WeatherData]:
        """
        Get weather data for a specific city.

        Args:
            city (str): Name of the city

        Returns:
            Optional[WeatherData]: Weather data for the city, or None if not found
        """
        if not city or city == "0":
            logger.info("User skipped weather checking")
            return None

        # Clean the input
        city = city.strip()
        if not city:
            logger.warning("Empty city name after cleaning")
            return None

        if city.lower() == "current":
            return self.get_current_weather()

        logger.info(f"Getting weather for city: '{city}'")

        # With WeatherAPI.com, we can pass the city name directly to the API
        # without getting coordinates first in many cases, which improves reliability
        weather_api_key = self._get_weather_api_key()
        if self.requests_available and weather_api_key:
            try:
                # Try direct city query first - this is more reliable with WeatherAPI.com
                logger.info(f"Trying direct city query for '{city}'")
                return self.get_weather_data(location_name=city)
            except Exception as e:
                logger.error(f"Direct city query failed: {e}, trying coordinates method")

        # Fallback to coordinates method
        logger.info(f"Trying coordinates method for '{city}'")
        coords = self.get_coordinates_for_location(city)
        if coords:
            lat, lon = coords
            logger.info(f"Found coordinates for '{city}': {lat}, {lon}")
            return self.get_weather_data(lat=lat, lon=lon, location_name=city)
        else:
            logger.warning(f"Could not find coordinates for '{city}'")
            # Return sample data instead of None to avoid crashes
            logger.info(f"Using sample weather data for '{city}'")
            return self.weather_collection.get_sample_weather_data(city)
