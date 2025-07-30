"""
EcoCycle - Route Controller

This module defines the RouteController class, which handles the business logic for cycling routes.
"""

import os
import logging
import time
import webbrowser
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta

# Import dependency_manager for ensuring packages
from core.dependency import dependency_manager

from models.route import Route, RouteCollection
import utils.general_utils as utils  # Import with alias for clarity

# Use dependency manager to check for folium availability
FOLIUM_AVAILABLE = dependency_manager.is_package_installed('folium', force_check=True)

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_ACCESS_TOKEN", "")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
OPENROUTESERVICE_API_KEY = os.environ.get("OPENROUTESERVICE_API_KEY", "")


class RouteController:
    """
    Controller class for handling cycling route business logic.
    """

    # Default bicycle speed in km/h (used for time estimation when API doesn't provide duration)
    DEFAULT_CYCLING_SPEED = 15.0

    def __init__(self, route_collection: Optional[RouteCollection] = None, user_manager=None):
        """
        Initialize a RouteController.

        Args:
            route_collection (Optional[RouteCollection]): Collection of routes to use
            user_manager: User manager for accessing user data
        """
        self.route_collection = route_collection or RouteCollection()
        self.user_manager = user_manager

        # Check for required package availability
        self.requests_available = self._check_requests_available()

        # Try to ensure folium is installed if not available
        global FOLIUM_AVAILABLE
        # Set folium availability as instance attribute
        self.FOLIUM_AVAILABLE = FOLIUM_AVAILABLE

        if not FOLIUM_AVAILABLE:
            logger.info("Folium package not available, attempting to install")
            success, failed = dependency_manager.ensure_feature('route_planning', silent=False)

            if success and 'folium' not in failed:
                # Force a refresh of the package cache for 'folium'
                dependency_manager.reset_package_cache('folium')
                FOLIUM_AVAILABLE = dependency_manager.is_package_installed('folium', force_check=True)

                if FOLIUM_AVAILABLE:
                    # Import folium now that it's available
                    import folium
                    logger.info("Successfully imported folium package")
                else:
                    logger.warning("Failed to use folium package despite successful installation")
            else:
                logger.warning(f"Failed to install route planning packages: {failed}")

    def _check_requests_available(self) -> bool:
        """
        Check if the requests library is available.
        Attempts to install it if not available.

        Returns:
            bool: True if available, False otherwise
        """
        # Force a fresh check by resetting the cache for 'requests'
        dependency_manager.reset_package_cache('requests')
        requests_available = dependency_manager.is_package_installed('requests', force_check=True)

        if requests_available:
            # Import the module to ensure it works
            try:
                import requests
                logger.debug("Requests package is already installed and working")
                return True
            except ImportError as e:
                logger.warning(f"Requests package shows as installed but fails to import: {e}")
                requests_available = False

        if not requests_available:
            # Try to install requests using dependency_manager
            logger.info("Requests package not available, attempting to install")
            success, failed = dependency_manager.ensure_feature('route_planning', silent=False)

            if success and 'requests' not in failed:
                # Force a refresh of the package cache
                dependency_manager.reset_package_cache('requests')
                requests_available = dependency_manager.is_package_installed('requests', force_check=True)

                if requests_available:
                    try:
                        import requests
                        logger.debug("Requests package successfully installed and imported")
                        return True
                    except ImportError as e:
                        logger.error(f"Failed to import requests after installation: {e}")
                else:
                    logger.warning("Requests package shows as not available after installation attempt")
            else:
                logger.warning(f"Failed to install route planning packages: {failed}")

        return requests_available  # Return the actual status instead of always False

    def get_route_info(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                      preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get route information between two coordinates with bicycle-specific routing.

        Args:
            start_coords (Tuple[float, float]): Starting coordinates (latitude, longitude)
            end_coords (Tuple[float, float]): Ending coordinates (latitude, longitude)
            preferences (Optional[Dict[str, Any]]): Routing preferences for cycling

        Returns:
            Dict[str, Any]: Route information including distance, duration, elevation, and route quality
        """
        # Validate coordinates first
        if not all(isinstance(coord, (int, float)) for coord in start_coords + end_coords):
            logger.error(f"Invalid coordinates provided: {start_coords} to {end_coords}")
            return {
                "distance": 0,
                "duration": 0,
                "elevation": 0,
                "error": "Invalid coordinates",
                "route_quality": "error"
            }

        # Validate coordinate ranges
        if not self._validate_coordinate_ranges(start_coords, end_coords):
            logger.error(f"Coordinates out of valid range: {start_coords} to {end_coords}")
            return {
                "distance": 0,
                "duration": 0,
                "elevation": 0,
                "error": "Coordinates out of valid range",
                "route_quality": "error"
            }

        # Set default preferences for cycling
        if preferences is None:
            preferences = {
                "avoid_highways": True,
                "prefer_bike_lanes": True,
                "avoid_steep_hills": False,
                "surface_preference": "paved"
            }

        # Check cache first (include preferences in cache key)
        cache_key = f"{start_coords}_{end_coords}_{hash(str(sorted(preferences.items())))}"
        cached_route = self.route_collection.get_route_from_cache_with_key(cache_key)
        if cached_route:
            logger.debug(f"Retrieved route from cache for {start_coords} to {end_coords}")
            return cached_route

        # Calculate direct distance for fallback
        try:
            direct_distance = utils.calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            direct_distance = 0

        # Try multiple routing services in order of preference
        route_info = None

        # 1. Try Google Maps Directions API (best for cycling)
        if GOOGLE_MAPS_API_KEY and self.requests_available:
            route_info = self._get_google_maps_route(start_coords, end_coords, preferences)
            if route_info:
                route_info["source"] = "google_maps"
                logger.debug(f"Retrieved route from Google Maps API for {start_coords} to {end_coords}")

        # 2. Try MapBox Directions API (good cycling support)
        if not route_info and MAPBOX_ACCESS_TOKEN and self.requests_available:
            route_info = self._get_mapbox_route(start_coords, end_coords, preferences)
            if route_info:
                route_info["source"] = "mapbox"
                logger.debug(f"Retrieved route from MapBox API for {start_coords} to {end_coords}")

        # 3. Try OpenRouteService (open source alternative)
        if not route_info and OPENROUTESERVICE_API_KEY and self.requests_available:
            route_info = self._get_openrouteservice_route(start_coords, end_coords, preferences)
            if route_info:
                route_info["source"] = "openrouteservice"
                logger.debug(f"Retrieved route from OpenRouteService API for {start_coords} to {end_coords}")

        # 4. Fallback to enhanced estimation
        if not route_info:
            route_info = self._get_enhanced_fallback_route(start_coords, end_coords, direct_distance, preferences)
            route_info["source"] = "estimation"
            logger.debug(f"Created enhanced estimated route for {start_coords} to {end_coords}")

        # Add route quality assessment
        route_info["route_quality"] = self._assess_route_quality(route_info, preferences)

        # Cache the route with preferences
        self.route_collection.add_route_to_cache_with_key(cache_key, route_info)

        return route_info

    def _validate_coordinate_ranges(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> bool:
        """
        Validate that coordinates are within valid latitude/longitude ranges.

        Args:
            start_coords: Starting coordinates (latitude, longitude)
            end_coords: Ending coordinates (latitude, longitude)

        Returns:
            bool: True if coordinates are valid, False otherwise
        """
        for coords in [start_coords, end_coords]:
            lat, lon = coords
            # Latitude must be between -90 and 90
            if not (-90 <= lat <= 90):
                return False
            # Longitude must be between -180 and 180
            if not (-180 <= lon <= 180):
                return False
        return True

    def _get_google_maps_route(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                              preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get route information from Google Maps Directions API with cycling preferences.

        Args:
            start_coords: Starting coordinates (latitude, longitude)
            end_coords: Ending coordinates (latitude, longitude)
            preferences: Cycling preferences

        Returns:
            Optional[Dict[str, Any]]: Route information or None if failed
        """
        try:
            import requests

            # Build URL with cycling mode and preferences
            origin = f"{start_coords[0]},{start_coords[1]}"
            destination = f"{end_coords[0]},{end_coords[1]}"

            params = {
                'origin': origin,
                'destination': destination,
                'mode': 'bicycling',
                'key': GOOGLE_MAPS_API_KEY,
                'units': 'metric'
            }

            # Add cycling preferences
            avoid_params = []
            if preferences.get('avoid_highways', True):
                avoid_params.append('highways')
            if avoid_params:
                params['avoid'] = '|'.join(avoid_params)

            url = "https://maps.googleapis.com/maps/api/directions/json"
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get('status') == 'OK' and data.get('routes'):
                route = data['routes'][0]
                leg = route['legs'][0]

                distance = leg['distance']['value'] / 1000  # Convert to kilometers
                duration = leg['duration']['value'] / 60    # Convert to minutes

                # Extract elevation data if available
                elevation = 0
                if 'elevation_gain' in leg:
                    elevation = leg['elevation_gain']

                return {
                    "distance": distance,
                    "duration": duration,
                    "elevation": elevation,
                    "bike_friendly": True,  # Google Maps cycling mode is bike-friendly
                    "has_bike_lanes": preferences.get('prefer_bike_lanes', False)
                }

        except Exception as e:
            logger.error(f"Error getting route from Google Maps API: {e}")

        return None

    def _get_mapbox_route(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                         preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get route information from MapBox Directions API with enhanced cycling parameters.

        Args:
            start_coords: Starting coordinates (latitude, longitude)
            end_coords: Ending coordinates (latitude, longitude)
            preferences: Cycling preferences

        Returns:
            Optional[Dict[str, Any]]: Route information or None if failed
        """
        try:
            import requests

            # Build URL with enhanced cycling parameters
            coords = f"{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"

            params = {
                'geometries': 'geojson',
                'access_token': MAPBOX_ACCESS_TOKEN,
                'overview': 'full',
                'steps': 'true'
            }

            # Add cycling-specific parameters
            if preferences.get('avoid_highways', True):
                params['exclude'] = 'motorway'

            url = f"https://api.mapbox.com/directions/v5/mapbox/cycling/{coords}"
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                distance = route["distance"] / 1000  # Convert to kilometers
                duration = route["duration"] / 60    # Convert to minutes

                # Extract additional route information
                elevation = 0
                bike_friendly = True

                return {
                    "distance": distance,
                    "duration": duration,
                    "elevation": elevation,
                    "bike_friendly": bike_friendly,
                    "has_bike_lanes": False  # MapBox doesn't provide this info directly
                }

        except Exception as e:
            logger.error(f"Error getting route from MapBox API: {e}")

        return None

    def _get_openrouteservice_route(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                                   preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get route information from OpenRouteService API.

        Args:
            start_coords: Starting coordinates (latitude, longitude)
            end_coords: Ending coordinates (latitude, longitude)
            preferences: Cycling preferences

        Returns:
            Optional[Dict[str, Any]]: Route information or None if failed
        """
        try:
            import requests

            # Build request for OpenRouteService
            headers = {
                'Authorization': OPENROUTESERVICE_API_KEY,
                'Content-Type': 'application/json'
            }

            body = {
                "coordinates": [[start_coords[1], start_coords[0]], [end_coords[1], end_coords[0]]],
                "profile": "cycling-regular",
                "format": "json",
                "units": "m"
            }

            # Add cycling preferences
            if preferences.get('avoid_highways', True):
                body["options"] = {"avoid_features": ["highways"]}

            url = "https://api.openrouteservice.org/v2/directions/cycling-regular"
            response = requests.post(url, json=body, headers=headers, timeout=10)
            data = response.json()

            if "routes" in data and len(data["routes"]) > 0:
                route = data["routes"][0]
                summary = route["summary"]

                distance = summary["distance"] / 1000  # Convert to kilometers
                duration = summary["duration"] / 60    # Convert to minutes

                return {
                    "distance": distance,
                    "duration": duration,
                    "elevation": 0,  # Would need additional API call for elevation
                    "bike_friendly": True,
                    "has_bike_lanes": False
                }

        except Exception as e:
            logger.error(f"Error getting route from OpenRouteService API: {e}")

        return None

    def _get_enhanced_fallback_route(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                                    direct_distance: float, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate enhanced fallback route estimation with cycling-specific calculations.

        Args:
            start_coords: Starting coordinates (latitude, longitude)
            end_coords: Ending coordinates (latitude, longitude)
            direct_distance: Direct distance between points in kilometers
            preferences: Cycling preferences

        Returns:
            Dict[str, Any]: Enhanced route estimation
        """
        # Enhanced distance calculation based on terrain and preferences
        distance_multiplier = 1.2  # Base multiplier for non-direct routes

        # Adjust multiplier based on preferences
        if preferences.get('avoid_highways', True):
            distance_multiplier += 0.1  # Avoiding highways adds distance
        if preferences.get('prefer_bike_lanes', True):
            distance_multiplier += 0.05  # Bike lanes might add slight detour

        # Calculate estimated distance
        estimated_distance = direct_distance * distance_multiplier

        # Enhanced speed calculation
        base_speed = self.DEFAULT_CYCLING_SPEED  # 15 km/h

        # Adjust speed based on preferences and terrain
        if preferences.get('avoid_steep_hills', False):
            base_speed *= 0.9  # Slower when avoiding hills (more detours)
        if preferences.get('surface_preference') == 'unpaved':
            base_speed *= 0.8  # Slower on unpaved surfaces

        # Calculate duration
        estimated_duration = (estimated_distance / base_speed) * 60  # Convert to minutes

        return {
            "distance": estimated_distance,
            "duration": estimated_duration,
            "elevation": 0,
            "bike_friendly": True,  # Assume fallback routes are bike-friendly
            "has_bike_lanes": False,
            "estimated": True
        }

    def _assess_route_quality(self, route_info: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """
        Assess the quality of a route for cycling based on various factors.

        Args:
            route_info: Route information dictionary
            preferences: User cycling preferences

        Returns:
            str: Route quality assessment ('excellent', 'good', 'fair', 'poor')
        """
        quality_score = 0
        max_score = 10

        # Check if route is bike-friendly
        if route_info.get('bike_friendly', False):
            quality_score += 3

        # Check for bike lanes
        if route_info.get('has_bike_lanes', False):
            quality_score += 2

        # Check if route source is reliable
        source = route_info.get('source', 'unknown')
        if source == 'google_maps':
            quality_score += 3  # Google Maps has excellent cycling data
        elif source == 'mapbox':
            quality_score += 2  # MapBox has good cycling data
        elif source == 'openrouteservice':
            quality_score += 2  # OpenRouteService has good cycling data
        else:
            quality_score += 1  # Estimation is less reliable

        # Check distance reasonableness (not too long detour)
        if not route_info.get('estimated', False):
            quality_score += 1  # Real API data is better than estimation

        # Convert score to quality rating
        quality_percentage = (quality_score / max_score) * 100

        if quality_percentage >= 80:
            return 'excellent'
        elif quality_percentage >= 60:
            return 'good'
        elif quality_percentage >= 40:
            return 'fair'
        else:
            return 'poor'

    def save_user_route(self, name: str, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                       distance: float, duration: float) -> bool:
        """
        Save a route to the user's saved routes.

        Args:
            name (str): Name of the route
            start_coords (Tuple[float, float]): Starting coordinates
            end_coords (Tuple[float, float]): Ending coordinates
            distance (float): Distance in kilometers
            duration (float): Duration in minutes

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.user_manager or not self.user_manager.is_authenticated():
            logger.warning("Cannot save route: User not authenticated")
            return False

        # Create route object
        route = Route(name, start_coords, end_coords, distance, duration)

        # Get user's saved routes
        user = self.user_manager.get_current_user()
        if "saved_routes" not in user:
            user["saved_routes"] = []

        # Add to saved routes
        user["saved_routes"].append(route.to_dict())

        # Save user data
        if self.user_manager.save_users():
            logger.info(f"Route '{name}' saved successfully")
            return True
        else:
            logger.error(f"Error saving route '{name}'")
            return False

    def get_user_routes(self) -> List[Route]:
        """
        Get all routes saved by the current user.

        Returns:
            List[Route]: List of user's saved routes
        """
        if not self.user_manager or not self.user_manager.is_authenticated():
            logger.warning("Cannot get routes: User not authenticated")
            return []

        # Get user's saved routes
        user = self.user_manager.get_current_user()
        routes_data = user.get("saved_routes", [])

        # Load routes into collection
        self.route_collection.load_user_routes(routes_data)

        return self.route_collection.get_all_user_routes()

    def delete_user_route(self, index: int) -> bool:
        """
        Delete a route from the user's saved routes.

        Args:
            index (int): Index of the route to delete

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.user_manager or not self.user_manager.is_authenticated():
            logger.warning("Cannot delete route: User not authenticated")
            return False

        # Get user's saved routes
        user = self.user_manager.get_current_user()
        routes = user.get("saved_routes", [])

        if not isinstance(index, int):
            try:
                index = int(index)
            except (ValueError, TypeError):
                logger.error(f"Invalid index type: {type(index)}")
                return False

        if 0 <= index < len(routes):
            # Remove the route
            routes.pop(index)

            # Save user data
            if self.user_manager.save_users():
                logger.info(f"Route at index {index} deleted successfully")
                return True
            else:
                logger.error(f"Error saving user data after deleting route at index {index}")
                return False
        else:
            logger.error(f"Index {index} out of bounds for user routes (length: {len(routes)})")
            return False

    def generate_route_map(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                           title: str = "Cycling Route") -> Optional[str]:
        """
        Generate a route map between two points and save it as HTML.

        Args:
            start_coords (Tuple[float, float]): Starting coordinates
            end_coords (Tuple[float, float]): Ending coordinates
            title (str): Title for the map

        Returns:
            Optional[str]: Path to the generated map file, or None if generation failed
        """
        # Validate coordinates first
        if not all(isinstance(coord, (int, float)) for coord in start_coords + end_coords):
            logger.error(f"Invalid coordinates provided: {start_coords} to {end_coords}")
            return None

        global FOLIUM_AVAILABLE
        # Use the instance attribute if available
        folium_check = getattr(self, 'FOLIUM_AVAILABLE', FOLIUM_AVAILABLE)

        if not folium_check:
            logger.warning("Folium library not available, attempting to install it")
            success, failed = dependency_manager.ensure_feature('route_planning', silent=False)
            if success and 'folium' not in failed:
                try:
                    import folium
                    FOLIUM_AVAILABLE = True
                    self.FOLIUM_AVAILABLE = True
                    logger.info("Successfully installed folium")
                except ImportError:
                    logger.warning("Failed to import folium even after installation attempt")
                    return None
            else:
                logger.warning(f"Failed to install folium: {failed}")
                return None

        try:
            # Ensure folium is imported
            import folium

            # Calculate center point
            center_lat = (start_coords[0] + end_coords[0]) / 2
            center_lon = (start_coords[1] + end_coords[1]) / 2

            # Create map
            cycling_map = folium.Map(location=[center_lat, center_lon], zoom_start=10)

            # Add markers
            folium.Marker(
                location=[start_coords[0], start_coords[1]],
                popup="Start",
                icon=folium.Icon(icon="play", color="green")
            ).add_to(cycling_map)

            folium.Marker(
                location=[end_coords[0], end_coords[1]],
                popup="End",
                icon=folium.Icon(icon="stop", color="red")
            ).add_to(cycling_map)

            # Add a simple line for the route
            folium.PolyLine(
                locations=[[start_coords[0], start_coords[1]], [end_coords[0], end_coords[1]]],
                color="blue",
                weight=5,
                opacity=0.8
            ).add_to(cycling_map)

            # Add title
            folium.Marker(
                [start_coords[0], start_coords[1]],
                icon=folium.DivIcon(
                    icon_size=(150, 36),
                    icon_anchor=(75, 60),
                    html=f'<div style="font-size: 14pt; font-weight: bold; color: blue">{title}</div>'
                )
            ).add_to(cycling_map)

            # Create maps directory if it doesn't exist
            maps_dir = os.path.join(os.getcwd(), "maps")
            os.makedirs(maps_dir, exist_ok=True)

            # Save map
            timestamp = int(time.time())
            filename = f"route_map_{timestamp}.html"
            file_path = os.path.join(maps_dir, filename)

            logger.info(f"Route map generated: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error generating map: {e}")
            return None

    def open_map_in_browser(self, map_path: str) -> bool:
        """
        Open a map file in the default web browser.

        Args:
            map_path (str): Path to the map file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            webbrowser.open(f"file://{os.path.abspath(map_path)}")
            logger.debug(f"Opened map in browser: {map_path}")
            return True
        except Exception as e:
            logger.error(f"Error opening map in browser: {e}")
            return False

    def calculate_cycling_eco_impact(self, distance: float) -> Dict[str, float]:
        """
        Calculate environmental impact of a cycling trip.

        Args:
            distance (float): Distance in kilometers

        Returns:
            Dict[str, float]: Dictionary with impact metrics
        """
        # Calculate CO2 savings
        try:
            co2_saved = utils.calculate_co2_saved(distance)
        except AttributeError:
            # Fallback if function doesn't exist in the module
            co2_saved = distance * 0.2  # Approximate CO2 savings (kg) per km

        # Calculate fuel savings (rough estimate - 7 liters per 100 km for average car)
        fuel_saved = distance * 0.07  # liters

        # Calculate money saved (rough estimate - average fuel price $1.5 per liter)
        money_saved = fuel_saved * 1.5  # dollars

        # Calculate equivalents
        trees_day = co2_saved / 0.055  # One tree absorbs about 20kg CO2 per year = 0.055kg per day
        light_bulbs = co2_saved / 0.1  # 100W light bulb for 24 hours ~ 0.1kg CO2

        return {
            "co2_saved": co2_saved,
            "fuel_saved": fuel_saved,
            "money_saved": money_saved,
            "trees_equivalent": trees_day,
            "light_bulbs_equivalent": light_bulbs
        }

    def estimate_travel_time(self, origin: str, destination: str) -> Optional[Tuple[int, int]]:
        """
        Estimate travel time between two locations by bicycle.

        Args:
            origin (str): Starting location (address or place name)
            destination (str): Ending location (address or place name)

        Returns:
            Optional[Tuple[int, int]]: A tuple of (hours, minutes) if successful, None otherwise
        """
        # Skip if either input is "0" (user requested to skip)
        if origin == "0" or destination == "0":
            logger.info("User skipped travel time estimation")
            return None

        try:
            # Get coordinates for origin and destination
            origin_coords = self._get_coordinates_for_location(origin)
            if not origin_coords:
                logger.warning(f"Could not find coordinates for origin: {origin}")
                return None

            destination_coords = self._get_coordinates_for_location(destination)
            if not destination_coords:
                logger.warning(f"Could not find coordinates for destination: {destination}")
                return None

            # Get route information
            route_info = self.get_route_info(origin_coords, destination_coords)

            if route_info and "duration" in route_info:
                # Duration is in minutes from the API
                total_minutes = route_info["duration"]
                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)

                logger.info(f"Estimated travel time from {origin} to {destination}: {hours}h {minutes}m")
                return (hours, minutes)
            else:
                logger.warning("Could not get duration from route info")
                return None

        except Exception as e:
            logger.error(f"Error estimating travel time: {e}")
            return None

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

    def _get_coordinates_for_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a location name using geocoding services.

        Args:
            location (str): Location name or address

        Returns:
            Optional[Tuple[float, float]]: Coordinates (latitude, longitude) if found, None otherwise
        """
        # Check if this is a "Current Location" format with coordinates
        coords = self._parse_current_location_format(location)
        if coords:
            logger.info(f"Parsed coordinates from current location format: {coords}")
            return coords

        # First, check for requests availability
        if not self.requests_available:
            logger.warning("Requests library not available for geocoding")
            return None

        try:
            import requests

            # Try different geocoding services in order of preference

            # 1. Try MapBox Geocoding API if available
            if MAPBOX_ACCESS_TOKEN:
                url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token={MAPBOX_ACCESS_TOKEN}"
                response = requests.get(url)
                data = response.json()

                if "features" in data and len(data["features"]) > 0:
                    # MapBox returns [longitude, latitude] format
                    coordinates = data["features"][0]["center"]
                    # Convert to [latitude, longitude] format for consistency
                    return (coordinates[1], coordinates[0])

            # 2. Use a simple estimation based on direct distance and average cycling speed
            # (This is a fallback when API services are not available)
            logger.warning("Could not geocode location, using fallback method")
            return None

        except Exception as e:
            logger.error(f"Error geocoding location {location}: {e}")
            return None

    def calculate_cycling_impact(self, distance: float, trips_per_week: float,
                               weight: float = 70.0, speed: float = 15.0) -> Dict[str, Any]:
        """
        Calculate comprehensive environmental and health impact of cycling.

        Args:
            distance (float): Average cycling distance per trip in kilometers
            trips_per_week (float): Number of trips per week
            weight (float): Rider's weight in kg
            speed (float): Average cycling speed in km/h

        Returns:
            Dict[str, Any]: Dictionary with impact metrics
        """
        # Calculate weekly, monthly, yearly distances
        weekly_distance = distance * trips_per_week
        monthly_distance = weekly_distance * 4.33  # Average weeks per month
        yearly_distance = weekly_distance * 52

        # Calculate CO2 savings
        try:
            weekly_co2 = utils.calculate_co2_saved(weekly_distance)
            monthly_co2 = utils.calculate_co2_saved(monthly_distance)
            yearly_co2 = utils.calculate_co2_saved(yearly_distance)
        except AttributeError:
            # Fallback if function doesn't exist in the module
            weekly_co2 = weekly_distance * 0.2  # Approximate CO2 savings (kg) per km
            monthly_co2 = monthly_distance * 0.2
            yearly_co2 = yearly_distance * 0.2

        # Calculate calories burned
        try:
            calories_per_trip = utils.calculate_calories(distance, speed, int(weight))
        except AttributeError:
            # Fallback if function doesn't exist in the module - formula: cal = weight(kg) * distance(km) * speed_factor
            speed_factor = 0.08 if speed <= 15 else 0.1  # Estimate based on speed
            calories_per_trip = weight * distance * speed_factor
        weekly_calories = calories_per_trip * trips_per_week
        monthly_calories = weekly_calories * 4.33
        yearly_calories = weekly_calories * 52

        # Calculate equivalents
        trees_yearly = yearly_co2 / 20  # One tree absorbs about 20kg CO2 per year
        car_km = yearly_co2 / 0.13  # Average car emits about 130g CO2 per km

        # Weight loss estimation (very rough - 7700 kcal = 1kg fat)
        weight_loss = yearly_calories / 7700 if yearly_calories > 0 else 0

        return {
            "distances": {
                "weekly": weekly_distance,
                "monthly": monthly_distance,
                "yearly": yearly_distance
            },
            "calories": {
                "per_trip": calories_per_trip,
                "weekly": weekly_calories,
                "monthly": monthly_calories,
                "yearly": yearly_calories
            },
            "co2_saved": {
                "weekly": weekly_co2,
                "monthly": monthly_co2,
                "yearly": yearly_co2
            },
            "equivalents": {
                "trees_yearly": trees_yearly,
                "car_km": car_km
            },
            "health": {
                "potential_weight_loss": weight_loss
            }
        }
