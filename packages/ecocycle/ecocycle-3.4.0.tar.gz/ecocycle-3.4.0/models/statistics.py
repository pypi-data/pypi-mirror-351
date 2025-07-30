#!/usr/bin/env python3
"""
EcoCycle - Statistics Module
Handles user statistics and analytics.
"""
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Statistics:
    """Statistics class for tracking and reporting user activities and metrics."""
    
    def __init__(self, stats_file="db/statistics.json"):
        """
        Initialize the Statistics instance.
        
        Args:
            stats_file: Path to the statistics database file
        """
        self.stats_file = stats_file
        self.stats = self._load_stats()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(stats_file), exist_ok=True)
    
    def _load_stats(self):
        """Load statistics from file."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            else:
                return {"users": {}, "global": {"last_updated": datetime.now().isoformat()}}
        except Exception as e:
            logger.error(f"Error loading statistics file: {e}")
            return {"users": {}, "global": {"last_updated": datetime.now().isoformat()}}
    
    def _save_stats(self):
        """Save statistics to file."""
        try:
            self.stats["global"]["last_updated"] = datetime.now().isoformat()
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving statistics file: {e}")
            return False
    
    def get_user_stats(self, username):
        """
        Get statistics for a specific user.
        
        Args:
            username: Username to get statistics for
            
        Returns:
            Dictionary of user statistics or empty dict if user not found
        """
        return self.stats.get("users", {}).get(username, {
            "routes_created": 0,
            "total_distance": 0,
            "carbon_saved": 0,
            "challenges_completed": 0,
            "eco_points": 0,
            "joined_date": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        })
    
    def update_user_stat(self, username, stat_name, value, increment=False):
        """
        Update a specific statistic for a user.
        
        Args:
            username: Username to update
            stat_name: Name of the statistic to update
            value: New value or increment amount
            increment: If True, add value to existing stat, otherwise replace
            
        Returns:
            Boolean indicating success
        """
        if "users" not in self.stats:
            self.stats["users"] = {}
            
        if username not in self.stats["users"]:
            self.stats["users"][username] = {
                "routes_created": 0,
                "total_distance": 0,
                "carbon_saved": 0,
                "challenges_completed": 0,
                "eco_points": 0,
                "joined_date": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
            
        if increment and stat_name in self.stats["users"][username]:
            self.stats["users"][username][stat_name] += value
        else:
            self.stats["users"][username][stat_name] = value
            
        self.stats["users"][username]["last_active"] = datetime.now().isoformat()
        return self._save_stats()
    
    def update_user_stats(self, username, stats_dict):
        """
        Update multiple statistics for a user at once.
        
        Args:
            username: Username to update
            stats_dict: Dictionary of stat_name: value pairs to update
            
        Returns:
            Boolean indicating success
        """
        for stat_name, value in stats_dict.items():
            self.update_user_stat(username, stat_name, value, increment=False)
        return True
    
    def get_global_stats(self):
        """
        Get global statistics across all users.
        
        Returns:
            Dictionary of global statistics
        """
        if "global" not in self.stats:
            self.stats["global"] = {"last_updated": datetime.now().isoformat()}
            
        # Calculate global stats from user data
        users = self.stats.get("users", {})
        total_users = len(users)
        total_routes = sum(user.get("routes_created", 0) for user in users.values())
        total_distance = sum(user.get("total_distance", 0) for user in users.values())
        total_carbon = sum(user.get("carbon_saved", 0) for user in users.values())
        
        global_stats = {
            "total_users": total_users,
            "total_routes": total_routes,
            "total_distance": total_distance,
            "total_carbon_saved": total_carbon,
            "last_updated": self.stats["global"]["last_updated"]
        }
        
        return global_stats
