"""
EcoCycle - AI Route Planner Cache Module
Provides caching functionality for route recommendations to improve performance
and reduce API calls
"""
import os
import json
import time
import logging
from typing import Dict, Any

from ..utils.constants import ROUTE_CACHE_EXPIRY, CACHE_FILE_PATH

# Configure logging
logger = logging.getLogger(__name__)


class RouteCache:
    """Handles caching of route recommendations to reduce API calls"""
    
    def __init__(self):
        """Initialize the route cache"""
        self.cache = {}
        self.load_cache()
    
    def load_cache(self) -> Dict:
        """Load the route cache from file"""
        if os.path.exists(CACHE_FILE_PATH):
            try:
                with open(CACHE_FILE_PATH, "r") as cache_file:
                    self.cache = json.load(cache_file)
                # Clean expired cache entries
                self.clean_cache()
                logger.info(f"Loaded {len(self.cache)} cached routes")
            except Exception as e:
                logger.warning(f"Failed to load route cache: {e}")
                self.cache = {}
        return self.cache
    
    def save_cache(self) -> bool:
        """Save the route cache to file"""
        try:
            with open(CACHE_FILE_PATH, 'w') as f:
                json.dump(self.cache, f, indent=4)
            logger.debug(f"Route cache saved with {len(self.cache)} entries")
            return True
        except Exception as e:
            logger.error(f"Error saving route cache: {e}")
            return False
    
    def clean_cache(self) -> None:
        """Remove expired entries from route cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry.get("timestamp", 0) > ROUTE_CACHE_EXPIRY:
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.cache[key]
            
        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired route cache entries")
    
    def get_cache_key(self, location: str, preferences: Dict[str, Any]) -> str:
        """Generate a cache key based on route parameters"""
        # Create a normalized representation of the request for cache keying
        # Ensure all values are properly converted to strings before any string operations
        try:
            # Handle preferred_difficulty - ensure it's a string
            preferred_difficulty = preferences.get('preferred_difficulty', '')
            if not isinstance(preferred_difficulty, str):
                preferred_difficulty = str(preferred_difficulty)
            
            # Handle preferred_terrain - ensure it's a string
            preferred_terrain = preferences.get('preferred_terrain', '')
            if not isinstance(preferred_terrain, str):
                preferred_terrain = str(preferred_terrain)
            
            # Handle route types - ensure it's a list and all items are strings
            route_types = preferences.get('preferred_route_types', [])
            if route_types is None:
                route_types = []
            elif not isinstance(route_types, list):
                route_types = [str(route_types)]
            
            # Handle points of interest - ensure it's a list and all items are strings
            poi = preferences.get('points_of_interest', [])
            if poi is None:
                poi = []
            elif not isinstance(poi, list):
                poi = [str(poi)]
            
            key_parts = [
                location.lower() if isinstance(location, str) else str(location).lower(),
                str(preferences.get('preferred_distance', 0)),
                preferred_difficulty.lower(),
                preferred_terrain.lower(),
                ",".join(sorted([str(r).lower() for r in route_types])),
                ",".join(sorted([str(p).lower() for p in poi]))
            ]
            return "|".join(key_parts)
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            # Return a fallback cache key if there's an error
            return f"{location.lower() if isinstance(location, str) else str(location)}|error"
    
    def get(self, key: str) -> Dict[str, Any]:
        """Get a cached route by key"""
        return self.cache.get(key, {})
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set a cached route by key"""
        # Add timestamp to the entry
        value["timestamp"] = time.time()
        self.cache[key] = value
        self.save_cache()