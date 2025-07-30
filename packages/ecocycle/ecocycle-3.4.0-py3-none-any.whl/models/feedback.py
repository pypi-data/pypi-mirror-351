"""
EcoCycle Feedback System
========================

This module handles the collection, storage, and analysis of user feedback
throughout the application. It supports various feedback types including
ratings, comments, feature requests, and bug reports.
"""

import datetime
import json
import os
import uuid
from typing import Dict, List, Optional, Union

class FeedbackManager:
    """Manages all user feedback functionality including collection, storage, and analysis."""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the FeedbackManager.
        
        Args:
            storage_path (str, optional): Path to store feedback data. If None, uses default location.
        """
        self.storage_path = storage_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                       'db', 'feedback')
        os.makedirs(self.storage_path, exist_ok=True)
        self.feedback_file = os.path.join(self.storage_path, 'feedback.json')
        self._load_feedback()
    
    def _load_feedback(self) -> None:
        """Load existing feedback from storage."""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    self.feedback = json.load(f)
            except json.JSONDecodeError:
                self.feedback = {"items": [], "categories": {}, "stats": {}}
        else:
            self.feedback = {"items": [], "categories": {}, "stats": {}}
    
    def _save_feedback(self) -> None:
        """Save feedback to storage."""
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(self.feedback, f, indent=2)
    
    def add_feedback(self, 
                     username: str, 
                     content: str, 
                     category: str = "general", 
                     rating: Optional[int] = None,
                     context: Optional[Dict] = None,
                     feature: Optional[str] = None) -> str:
        """
        Add a new feedback item.
        
        Args:
            username (str): Username of the feedback provider
            content (str): Feedback content/message
            category (str, optional): Feedback category (bug, suggestion, general)
            rating (int, optional): Numerical rating if applicable (1-5)
            context (dict, optional): Contextual information (screen, feature, etc.)
            feature (str, optional): Specific feature the feedback relates to
            
        Returns:
            str: ID of the created feedback item
        """
        # Generate a unique ID for the feedback
        feedback_id = str(uuid.uuid4())
        
        # Create the feedback item
        feedback_item = {
            "id": feedback_id,
            "username": username,
            "timestamp": datetime.datetime.now().isoformat(),
            "content": content,
            "category": category,
            "status": "new",
            "context": context or {},
        }
        
        # Add optional fields if provided
        if rating is not None:
            feedback_item["rating"] = max(1, min(5, rating))  # Ensure rating is between 1-5
        
        if feature:
            feedback_item["feature"] = feature
        
        # Add to the feedback list
        self.feedback["items"].append(feedback_item)
        
        # Update category counters
        if category in self.feedback["categories"]:
            self.feedback["categories"][category] += 1
        else:
            self.feedback["categories"][category] = 1
        
        # Update statistics
        self._update_stats(feedback_item)
        
        # Save the updated feedback
        self._save_feedback()
        
        return feedback_id
    
    def _update_stats(self, feedback_item: Dict) -> None:
        """
        Update feedback statistics.
        
        Args:
            feedback_item (dict): The new feedback item to incorporate into stats
        """
        stats = self.feedback["stats"]
        
        # Initialize stats if needed
        if "total_count" not in stats:
            stats["total_count"] = 0
            stats["by_day"] = {}
            stats["by_feature"] = {}
            stats["average_rating"] = 0
            stats["rating_count"] = 0
        
        # Update total count
        stats["total_count"] += 1
        
        # Update daily stats
        day = feedback_item["timestamp"].split("T")[0]  # Get YYYY-MM-DD part
        stats["by_day"][day] = stats["by_day"].get(day, 0) + 1
        
        # Update feature stats if applicable
        if "feature" in feedback_item:
            feature = feedback_item["feature"]
            if feature not in stats["by_feature"]:
                stats["by_feature"][feature] = {"count": 0, "sum_rating": 0, "rating_count": 0}
            
            stats["by_feature"][feature]["count"] += 1
            
            if "rating" in feedback_item:
                stats["by_feature"][feature]["sum_rating"] += feedback_item["rating"]
                stats["by_feature"][feature]["rating_count"] += 1
                stats["by_feature"][feature]["avg_rating"] = (
                    stats["by_feature"][feature]["sum_rating"] / 
                    stats["by_feature"][feature]["rating_count"]
                )
        
        # Update overall rating stats if applicable
        if "rating" in feedback_item:
            sum_rating = stats["average_rating"] * stats["rating_count"]
            stats["rating_count"] += 1
            stats["average_rating"] = (sum_rating + feedback_item["rating"]) / stats["rating_count"]
    
    def get_feedback(self, feedback_id: str) -> Optional[Dict]:
        """
        Retrieve a specific feedback item by ID.
        
        Args:
            feedback_id (str): ID of the feedback to retrieve
            
        Returns:
            dict or None: The feedback item if found, None otherwise
        """
        for item in self.feedback["items"]:
            if item["id"] == feedback_id:
                return item
        return None
    
    def update_feedback_status(self, feedback_id: str, status: str) -> bool:
        """
        Update the status of a feedback item.
        
        Args:
            feedback_id (str): ID of the feedback to update
            status (str): New status (new, in_progress, resolved, closed)
            
        Returns:
            bool: True if successful, False otherwise
        """
        for item in self.feedback["items"]:
            if item["id"] == feedback_id:
                item["status"] = status
                item["status_updated"] = datetime.datetime.now().isoformat()
                self._save_feedback()
                return True
        return False
    
    def add_feedback_response(self, feedback_id: str, responder: str, response: str) -> bool:
        """
        Add a response to a feedback item.
        
        Args:
            feedback_id (str): ID of the feedback to respond to
            responder (str): Username of the person responding
            response (str): Response content
            
        Returns:
            bool: True if successful, False otherwise
        """
        for item in self.feedback["items"]:
            if item["id"] == feedback_id:
                if "responses" not in item:
                    item["responses"] = []
                
                item["responses"].append({
                    "responder": responder,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "content": response
                })
                
                self._save_feedback()
                return True
        return False
    
    def get_feedback_by_category(self, category: str) -> List[Dict]:
        """
        Get all feedback items for a specific category.
        
        Args:
            category (str): Category to filter by
            
        Returns:
            list: List of matching feedback items
        """
        return [item for item in self.feedback["items"] if item["category"] == category]
    
    def get_feedback_by_feature(self, feature: str) -> List[Dict]:
        """
        Get all feedback items for a specific feature.
        
        Args:
            feature (str): Feature to filter by
            
        Returns:
            list: List of matching feedback items
        """
        return [item for item in self.feedback["items"] if item.get("feature") == feature]
    
    def get_feedback_by_user(self, username: str) -> List[Dict]:
        """
        Get all feedback items from a specific user.
        
        Args:
            username (str): Username to filter by
            
        Returns:
            list: List of matching feedback items
        """
        return [item for item in self.feedback["items"] if item["username"] == username]
    
    def get_feedback_statistics(self) -> Dict:
        """
        Get comprehensive feedback statistics.
        
        Returns:
            dict: Feedback statistics
        """
        return self.feedback["stats"]
    
    def export_feedback(self, format_type: str = "json") -> Union[str, Dict]:
        """
        Export feedback data in various formats.
        
        Args:
            format_type (str): Format type ("json", "csv", "report")
            
        Returns:
            str or dict: Exported data in requested format
        """
        if format_type == "json":
            return self.feedback
        elif format_type == "csv":
            # Generate CSV formatted string
            csv_lines = ["id,username,timestamp,category,content,rating,feature,status"]
            for item in self.feedback["items"]:
                csv_lines.append(
                    f"{item['id']},{item['username']},{item['timestamp']},"
                    f"{item['category']},{item['content'].replace(',', ';')},"
                    f"{item.get('rating', '')},"
                    f"{item.get('feature', '')},"
                    f"{item['status']}"
                )
            return "\n".join(csv_lines)
        elif format_type == "report":
            # Generate a summarized report
            return {
                "total_feedback": len(self.feedback["items"]),
                "by_category": self.feedback["categories"],
                "avg_rating": self.feedback["stats"].get("average_rating", 0),
                "recent_items": sorted(
                    self.feedback["items"], 
                    key=lambda x: x["timestamp"], 
                    reverse=True
                )[:10],
                "stats": self.feedback["stats"]
            }
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
