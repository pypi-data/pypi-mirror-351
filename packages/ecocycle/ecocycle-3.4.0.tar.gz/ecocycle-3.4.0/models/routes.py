#!/usr/bin/env python3
"""
EcoCycle - Routes Module
Manages route creation, storage, and retrieval.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class RouteManager:
    """RouteManager class for managing user routes and navigation data."""
    
    def __init__(self, routes_file="db/routes.json"):
        """
        Initialize the RouteManager instance.
        
        Args:
            routes_file: Path to the routes database file
        """
        self.routes_file = routes_file
        self.routes = self._load_routes()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(routes_file), exist_ok=True)
    
    def _load_routes(self) -> Dict[str, Any]:
        """Load routes from file."""
        try:
            if os.path.exists(self.routes_file):
                with open(self.routes_file, 'r') as f:
                    return json.load(f)
            else:
                return {"users": {}, "meta": {"last_updated": datetime.now().isoformat()}}
        except Exception as e:
            logger.error(f"Error loading routes file: {e}")
            return {"users": {}, "meta": {"last_updated": datetime.now().isoformat()}}
    
    def _save_routes(self) -> bool:
        """Save routes to file."""
        try:
            self.routes["meta"]["last_updated"] = datetime.now().isoformat()
            with open(self.routes_file, 'w') as f:
                json.dump(self.routes, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving routes file: {e}")
            return False
    
    def get_user_routes(self, username: str) -> List[Dict[str, Any]]:
        """
        Get all routes for a specific user.
        
        Args:
            username: Username to get routes for
            
        Returns:
            List of route dictionaries or empty list if user not found
        """
        return self.routes.get("users", {}).get(username, [])
    
    def add_route(self, username: str, route_data: Dict[str, Any]) -> bool:
        """
        Add a new route for a user.
        
        Args:
            username: Username to add route for
            route_data: Dictionary containing route information
            
        Returns:
            Boolean indicating success
        """
        if "users" not in self.routes:
            self.routes["users"] = {}
            
        if username not in self.routes["users"]:
            self.routes["users"][username] = []
        
        # Add timestamp if not provided
        if "created_at" not in route_data:
            route_data["created_at"] = datetime.now().isoformat()
            
        # Add route ID if not provided
        if "id" not in route_data:
            route_data["id"] = f"route_{len(self.routes['users'][username]) + 1}"
        
        self.routes["users"][username].append(route_data)
        return self._save_routes()
    
    def update_route(self, username: str, route_id: str, route_data: Dict[str, Any]) -> bool:
        """
        Update an existing route.
        
        Args:
            username: Username of route owner
            route_id: ID of the route to update
            route_data: New route data
            
        Returns:
            Boolean indicating success
        """
        user_routes = self.get_user_routes(username)
        
        for i, route in enumerate(user_routes):
            if route.get("id") == route_id:
                # Preserve creation timestamp and ID
                route_data["created_at"] = route.get("created_at", datetime.now().isoformat())
                route_data["id"] = route_id
                route_data["updated_at"] = datetime.now().isoformat()
                
                self.routes["users"][username][i] = route_data
                return self._save_routes()
        
        # Route not found
        return False
    
    def delete_route(self, username: str, route_id: str) -> bool:
        """
        Delete a user route.
        
        Args:
            username: Username of route owner
            route_id: ID of the route to delete
            
        Returns:
            Boolean indicating success
        """
        user_routes = self.get_user_routes(username)
        
        for i, route in enumerate(user_routes):
            if route.get("id") == route_id:
                self.routes["users"][username].pop(i)
                return self._save_routes()
        
        # Route not found
        return False
    
    def get_route(self, username: str, route_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific route by ID.
        
        Args:
            username: Username of route owner
            route_id: ID of the route to retrieve
            
        Returns:
            Route dictionary or None if not found
        """
        user_routes = self.get_user_routes(username)
        
        for route in user_routes:
            if route.get("id") == route_id:
                return route
        
        # Route not found
        return None
