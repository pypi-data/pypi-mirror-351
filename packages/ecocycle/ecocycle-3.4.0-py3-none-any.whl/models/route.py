"""
EcoCycle - Route Model

This module defines the Route model classes, which represent cycling routes.
"""

from typing import Dict, List, Any, Optional, Tuple
import time
import datetime
import os
import json
import logging

# Import configuration
from config.config import ROUTES_CACHE_FILE

# Configure logging
logger = logging.getLogger(__name__)

# Constants are now imported from config.config


class Route:
    """
    Model class representing a cycling route.
    """

    def __init__(self, name: str, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                 distance: float, duration: float, date_saved: Optional[str] = None):
        """
        Initialize a Route object.

        Args:
            name (str): Name of the route
            start_coords (Tuple[float, float]): Starting coordinates (latitude, longitude)
            end_coords (Tuple[float, float]): Ending coordinates (latitude, longitude)
            distance (float): Distance of the route in kilometers
            duration (float): Estimated duration in minutes
            date_saved (Optional[str]): ISO format date when the route was saved
        """
        self.name = name
        self.start_coords = start_coords
        self.end_coords = end_coords
        self.distance = distance
        self.duration = duration
        self.date_saved = date_saved or datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Route object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the Route
        """
        return {
            "name": self.name,
            "start_coords": self.start_coords,
            "end_coords": self.end_coords,
            "distance": self.distance,
            "duration": self.duration,
            "date_saved": self.date_saved
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Route':
        """
        Create a Route object from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing route data

        Returns:
            Route: New Route object
        """
        return cls(
            name=data.get("name", "Unnamed Route"),
            start_coords=tuple(data.get("start_coords", (0, 0))),
            end_coords=tuple(data.get("end_coords", (0, 0))),
            distance=data.get("distance", 0),
            duration=data.get("duration", 0),
            date_saved=data.get("date_saved")
        )

    def get_average_speed(self) -> float:
        """
        Calculate the average speed for this route.

        Returns:
            float: Average speed in km/h
        """
        if self.duration <= 0:
            return 0
        return self.distance / (self.duration / 60)

    def get_formatted_date(self, format_str: str = "%Y-%m-%d") -> str:
        """
        Get the formatted date when the route was saved.

        Args:
            format_str (str): Format string for the date

        Returns:
            str: Formatted date string
        """
        try:
            date_obj = datetime.datetime.fromisoformat(self.date_saved)
            return date_obj.strftime(format_str)
        except (ValueError, TypeError):
            return "Unknown date"


class RouteCollection:
    """
    Model class representing a collection of cycling routes with caching.
    """

    def __init__(self, cache_file: str = ROUTES_CACHE_FILE):
        """
        Initialize a RouteCollection.

        Args:
            cache_file (str): Path to the cache file
        """
        self.cache_file = cache_file
        self.routes_cache = self._load_cache()
        self.user_routes: List[Route] = []

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
                json.dump(self.routes_cache, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving cache to {self.cache_file}: {e}")
            return False

    def get_route_from_cache(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Optional[Dict[str, Any]]:
        """
        Get route information from cache.

        Args:
            start_coords (Tuple[float, float]): Starting coordinates
            end_coords (Tuple[float, float]): Ending coordinates

        Returns:
            Optional[Dict[str, Any]]: Route information if found, None otherwise
        """
        cache_key = f"{start_coords[0]},{start_coords[1]}-{end_coords[0]},{end_coords[1]}"
        return self.routes_cache.get(cache_key)

    def add_route_to_cache(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                          route_info: Dict[str, Any]) -> bool:
        """
        Add route information to cache.

        Args:
            start_coords (Tuple[float, float]): Starting coordinates
            end_coords (Tuple[float, float]): Ending coordinates
            route_info (Dict[str, Any]): Route information to cache

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = f"{start_coords[0]},{start_coords[1]}-{end_coords[0]},{end_coords[1]}"
            self.routes_cache[cache_key] = route_info
            return self._save_cache()
        except Exception as e:
            logger.error(f"Error adding route to cache: {e}")
            return False

    def get_route_from_cache_with_key(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get route information from cache using a custom cache key.

        Args:
            cache_key (str): Custom cache key

        Returns:
            Optional[Dict[str, Any]]: Route information if found, None otherwise
        """
        return self.routes_cache.get(cache_key)

    def add_route_to_cache_with_key(self, cache_key: str, route_info: Dict[str, Any]) -> bool:
        """
        Add route information to cache using a custom cache key.

        Args:
            cache_key (str): Custom cache key
            route_info (Dict[str, Any]): Route information to cache

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add timestamp to route info for cache expiry
            route_info_with_timestamp = route_info.copy()
            route_info_with_timestamp['cached_at'] = time.time()

            self.routes_cache[cache_key] = route_info_with_timestamp
            return self._save_cache()
        except Exception as e:
            logger.error(f"Error adding route to cache with key {cache_key}: {e}")
            return False

    def clear_expired_cache(self, max_age_hours: int = 24) -> int:
        """
        Clear expired cache entries.

        Args:
            max_age_hours (int): Maximum age of cache entries in hours

        Returns:
            int: Number of entries removed
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        expired_keys = []

        for key, route_info in self.routes_cache.items():
            if isinstance(route_info, dict) and 'cached_at' in route_info:
                age = current_time - route_info['cached_at']
                if age > max_age_seconds:
                    expired_keys.append(key)

        for key in expired_keys:
            del self.routes_cache[key]

        if expired_keys:
            self._save_cache()
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def load_user_routes(self, user_routes_data: List[Dict[str, Any]]) -> None:
        """
        Load routes from user data.

        Args:
            user_routes_data (List[Dict[str, Any]]): List of route dictionaries from user data
        """
        self.user_routes = [Route.from_dict(route_data) for route_data in user_routes_data]

    def get_all_user_routes(self) -> List[Route]:
        """
        Get all user routes.

        Returns:
            List[Route]: List of all user routes
        """
        return self.user_routes

    def add_user_route(self, route: Route) -> None:
        """
        Add a route to the user's routes.

        Args:
            route (Route): Route to add
        """
        self.user_routes.append(route)

    def remove_user_route(self, index: int) -> Optional[Route]:
        """
        Remove a route from the user's routes.

        Args:
            index (int): Index of the route to remove

        Returns:
            Optional[Route]: Removed route if successful, None otherwise
        """
        if 0 <= index < len(self.user_routes):
            return self.user_routes.pop(index)
        return None

    def get_user_routes_as_dicts(self) -> List[Dict[str, Any]]:
        """
        Get all user routes as dictionaries.

        Returns:
            List[Dict[str, Any]]: List of route dictionaries
        """
        return [route.to_dict() for route in self.user_routes]