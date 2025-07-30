"""
EcoCycle - AI Route Planner Route Model
Provides data models and operations for route management
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
import datetime

# Configure logging
logger = logging.getLogger(__name__)


class RouteManager:
    """Manages route data storage and retrieval"""
    
    def __init__(self, routes_file_path: str):
        """Initialize the route manager
        
        Args:
            routes_file_path: Path to the JSON file storing routes
        """
        self.routes_file = routes_file_path
        self.saved_routes = self._load_routes()
    
    def _load_routes(self) -> Dict:
        """Load saved routes from file"""
        if os.path.exists(self.routes_file):
            try:
                with open(self.routes_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing routes file: {self.routes_file}")
                return {}
        return {}
    
    def _save_routes(self) -> bool:
        """Save routes to file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.routes_file), exist_ok=True)
        
        try:
            with open(self.routes_file, 'w') as f:
                json.dump(self.saved_routes, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving routes: {e}")
            return False
    
    def get_user_routes(self, username: str) -> List[Dict[str, Any]]:
        """Get all routes for a specific user
        
        Args:
            username: The username to get routes for
            
        Returns:
            List of route dictionaries
        """
        if username not in self.saved_routes:
            return []
        
        return self.saved_routes[username].get("saved_routes", [])
    
    def get_user_preferences(self, username: str) -> Dict[str, Any]:
        """Get cycling preferences for a specific user
        
        Args:
            username: The username to get preferences for
            
        Returns:
            Dictionary of user preferences
        """
        if username not in self.saved_routes:
            # Return default preferences
            return {
                "preferred_distance": 10,
                "preferred_difficulty": "intermediate",
                "preferred_terrain": "mixed",
                "preferred_route_types": ["leisure", "nature"],
                "points_of_interest": ["viewpoints", "cafes", "parks"]
            }
        
        return self.saved_routes[username].get("preferences", {})
    
    def initialize_user(self, username: str) -> None:
        """Initialize user data if not present
        
        Args:
            username: The username to initialize
        """
        if username not in self.saved_routes:
            self.saved_routes[username] = {
                "preferences": {
                    "preferred_distance": 10,
                    "preferred_difficulty": "intermediate",
                    "preferred_terrain": "mixed",
                    "preferred_route_types": ["leisure", "nature"],
                    "points_of_interest": ["viewpoints", "cafes", "parks"]
                },
                "saved_routes": []
            }
            self._save_routes()
    
    def save_route(self, username: str, route: Dict[str, Any]) -> bool:
        """Save a new route for a user
        
        Args:
            username: The username to save the route for
            route: The route dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        # Initialize user if not present
        self.initialize_user(username)
        
        # Add timestamp if not present
        if "created_at" not in route:
            route["created_at"] = datetime.datetime.now().isoformat()
        
        # Add the route
        self.saved_routes[username]["saved_routes"].append(route)
        
        # Save to file
        return self._save_routes()
    
    def update_preferences(self, username: str, preferences: Dict[str, Any]) -> bool:
        """Update preferences for a user
        
        Args:
            username: The username to update preferences for
            preferences: The new preferences dictionary
            
        Returns:
            True if successful, False otherwise
        """
        # Initialize user if not present
        self.initialize_user(username)
        
        # Update preferences
        self.saved_routes[username]["preferences"] = preferences
        
        # Save to file
        return self._save_routes()
    
    def delete_route(self, username: str, route_index: int) -> bool:
        """Delete a route by index
        
        Args:
            username: The username to delete the route for
            route_index: The index of the route to delete
            
        Returns:
            True if successful, False otherwise
        """
        if username not in self.saved_routes:
            return False
        
        routes = self.saved_routes[username].get("saved_routes", [])
        
        if route_index < 0 or route_index >= len(routes):
            return False
        
        # Remove the route
        del self.saved_routes[username]["saved_routes"][route_index]
        
        # Save to file
        return self._save_routes()