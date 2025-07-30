"""
EcoCycle Feature Suggestion System
================================

This module handles the collection, management, and processing of user
suggestions for new features and improvements to the EcoCycle application.
"""

import datetime
import json
import os
import uuid
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SuggestionController:
    """Controller responsible for managing the feature suggestion system."""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the SuggestionController.
        
        Args:
            storage_path: Path to store suggestion data. If None, uses default location.
        """
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'db', 'suggestions'
        )
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Define file paths
        self.suggestions_file = os.path.join(self.storage_path, 'suggestions.json')
        self.categories_file = os.path.join(self.storage_path, 'categories.json')
        self.votes_file = os.path.join(self.storage_path, 'votes.json')
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load existing suggestion data."""
        # Load suggestions
        if os.path.exists(self.suggestions_file):
            try:
                with open(self.suggestions_file, 'r', encoding='utf-8') as f:
                    self.suggestions = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading suggestions: {e}")
                self.suggestions = {"items": []}
        else:
            self.suggestions = {"items": []}
        
        # Load categories
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading categories: {e}")
                self.categories = self._create_default_categories()
        else:
            self.categories = self._create_default_categories()
        
        # Load votes
        if os.path.exists(self.votes_file):
            try:
                with open(self.votes_file, 'r', encoding='utf-8') as f:
                    self.votes = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading votes: {e}")
                self.votes = {"items": []}
        else:
            self.votes = {"items": []}
    
    def _create_default_categories(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Create default suggestion categories.
        
        Returns:
            Dictionary of default categories
        """
        return {
            "items": [
                {
                    "id": "ui",
                    "name": "User Interface",
                    "description": "Suggestions related to the application's user interface and experience"
                },
                {
                    "id": "routes",
                    "name": "Route Planning",
                    "description": "Suggestions for the route planning and navigation features"
                },
                {
                    "id": "tracking",
                    "name": "Activity Tracking",
                    "description": "Suggestions for activity tracking and analysis"
                },
                {
                    "id": "social",
                    "name": "Social Features",
                    "description": "Suggestions for social and community aspects"
                },
                {
                    "id": "integrations",
                    "name": "Integrations",
                    "description": "Suggestions for integrating with other services and devices"
                },
                {
                    "id": "data",
                    "name": "Data & Analytics",
                    "description": "Suggestions for data management and analytics features"
                },
                {
                    "id": "other",
                    "name": "Other",
                    "description": "Suggestions that don't fit in other categories"
                }
            ]
        }
    
    def _save_suggestions(self) -> None:
        """Save suggestions to storage."""
        with open(self.suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(self.suggestions, f, indent=2)
    
    def _save_categories(self) -> None:
        """Save categories to storage."""
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, indent=2)
    
    def _save_votes(self) -> None:
        """Save votes to storage."""
        with open(self.votes_file, 'w', encoding='utf-8') as f:
            json.dump(self.votes, f, indent=2)
    
    def add_suggestion(self, title: str, description: str, 
                      username: str, category_id: str,
                      related_features: List[str] = None,
                      priority: str = "medium") -> Dict[str, Any]:
        """
        Add a new feature suggestion.
        
        Args:
            title: Suggestion title
            description: Detailed description
            username: Username of the suggester
            category_id: Category ID for the suggestion
            related_features: Optional list of related features
            priority: Suggested priority (low, medium, high)
            
        Returns:
            Dict with status and suggestion_id if successful
        """
        try:
            # Validate inputs
            if not title or len(title.strip()) < 5:
                return {"status": "error", "message": "Title must be at least 5 characters"}
            
            if not description or len(description.strip()) < 20:
                return {"status": "error", "message": "Description must be at least 20 characters"}
            
            # Validate category
            category_exists = False
            for category in self.categories["items"]:
                if category["id"] == category_id:
                    category_exists = True
                    break
            
            if not category_exists:
                return {"status": "error", "message": "Invalid category"}
            
            # Create suggestion
            suggestion_id = str(uuid.uuid4())
            suggestion = {
                "id": suggestion_id,
                "title": title,
                "description": description,
                "username": username,
                "category_id": category_id,
                "created_at": datetime.datetime.now().isoformat(),
                "status": "new",
                "vote_count": 0,
                "priority": priority,
                "related_features": related_features or [],
                "tags": [],
                "comments": []
            }
            
            # Add to suggestions
            self.suggestions["items"].append(suggestion)
            self._save_suggestions()
            
            # Auto-vote for own suggestion
            self.add_vote(suggestion_id, username)
            
            return {"status": "success", "suggestion_id": suggestion_id}
            
        except Exception as e:
            logger.error(f"Error adding suggestion: {str(e)}")
            return {"status": "error", "message": f"Failed to add suggestion: {str(e)}"}
    
    def get_suggestions(self, category_id: Optional[str] = None, 
                       status: Optional[str] = None,
                       search_query: Optional[str] = None,
                       sort_by: str = "votes",
                       page: int = 1, 
                       limit: int = 20) -> Dict[str, Any]:
        """
        Get suggestions with optional filtering.
        
        Args:
            category_id: Optional category to filter by
            status: Optional status to filter by
            search_query: Optional search term
            sort_by: Sort field (votes, date, priority)
            page: Page number for pagination
            limit: Number of suggestions per page
            
        Returns:
            Dict with suggestions and pagination info
        """
        # Filter suggestions
        filtered_suggestions = self.suggestions["items"]
        
        if category_id:
            filtered_suggestions = [s for s in filtered_suggestions if s["category_id"] == category_id]
        
        if status:
            filtered_suggestions = [s for s in filtered_suggestions if s["status"] == status]
        
        if search_query:
            search_query = search_query.lower()
            filtered_suggestions = [
                s for s in filtered_suggestions if 
                search_query in s["title"].lower() or 
                search_query in s["description"].lower()
            ]
        
        # Sort suggestions
        if sort_by == "votes":
            filtered_suggestions = sorted(filtered_suggestions, key=lambda s: s["vote_count"], reverse=True)
        elif sort_by == "date":
            filtered_suggestions = sorted(filtered_suggestions, key=lambda s: s["created_at"], reverse=True)
        elif sort_by == "priority":
            # Custom sort by priority (high, medium, low)
            priority_order = {"high": 0, "medium": 1, "low": 2}
            filtered_suggestions = sorted(
                filtered_suggestions, 
                key=lambda s: (priority_order.get(s["priority"], 3), -s["vote_count"])
            )
        
        # Paginate
        total_suggestions = len(filtered_suggestions)
        total_pages = (total_suggestions + limit - 1) // limit
        
        start_idx = (page - 1) * limit
        end_idx = min(start_idx + limit, total_suggestions)
        
        paginated_suggestions = filtered_suggestions[start_idx:end_idx]
        
        # Prepare result
        return {
            "suggestions": paginated_suggestions,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_suggestions": total_suggestions,
                "has_previous": page > 1,
                "has_next": page < total_pages
            }
        }
    
    def get_suggestion(self, suggestion_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific suggestion by ID.
        
        Args:
            suggestion_id: ID of the suggestion to retrieve
            
        Returns:
            Suggestion dict if found, None otherwise
        """
        for suggestion in self.suggestions["items"]:
            if suggestion["id"] == suggestion_id:
                return suggestion
        return None
    
    def update_suggestion(self, suggestion_id: str, updates: Dict[str, Any], 
                         username: str) -> Dict[str, Any]:
        """
        Update a suggestion.
        
        Args:
            suggestion_id: ID of the suggestion to update
            updates: Dictionary of fields to update
            username: Username of the person making the update
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the suggestion
            suggestion = self.get_suggestion(suggestion_id)
            if not suggestion:
                return {"status": "error", "message": "Suggestion not found"}
            
            # Check permissions (only original suggester or admin can update)
            if suggestion["username"] != username:
                return {"status": "error", "message": "You don't have permission to update this suggestion"}
            
            # Update allowed fields
            allowed_fields = ["title", "description", "category_id", "related_features", "tags"]
            for field in allowed_fields:
                if field in updates:
                    suggestion[field] = updates[field]
            
            # Add edit timestamp
            suggestion["edited_at"] = datetime.datetime.now().isoformat()
            
            self._save_suggestions()
            return {"status": "success", "message": "Suggestion updated successfully"}
            
        except Exception as e:
            logger.error(f"Error updating suggestion: {str(e)}")
            return {"status": "error", "message": f"Failed to update suggestion: {str(e)}"}
    
    def update_suggestion_status(self, suggestion_id: str, new_status: str, 
                               username: str, admin_note: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a suggestion's status.
        
        Args:
            suggestion_id: ID of the suggestion to update
            new_status: New status (new, under_review, accepted, implemented, declined)
            username: Username of the person making the update
            admin_note: Optional note explaining the status change
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the suggestion
            suggestion = self.get_suggestion(suggestion_id)
            if not suggestion:
                return {"status": "error", "message": "Suggestion not found"}
            
            # Validate status
            valid_statuses = ["new", "under_review", "accepted", "implemented", "declined"]
            if new_status not in valid_statuses:
                return {"status": "error", "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
            
            # Update status
            suggestion["status"] = new_status
            suggestion["status_updated_at"] = datetime.datetime.now().isoformat()
            suggestion["status_updated_by"] = username
            
            if admin_note:
                suggestion["admin_note"] = admin_note
            
            self._save_suggestions()
            return {"status": "success", "message": f"Status updated to '{new_status}'"}
            
        except Exception as e:
            logger.error(f"Error updating suggestion status: {str(e)}")
            return {"status": "error", "message": f"Failed to update status: {str(e)}"}
    
    def add_vote(self, suggestion_id: str, username: str) -> Dict[str, Any]:
        """
        Add a vote to a suggestion.
        
        Args:
            suggestion_id: ID of the suggestion to vote for
            username: Username of the voter
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the suggestion
            suggestion = self.get_suggestion(suggestion_id)
            if not suggestion:
                return {"status": "error", "message": "Suggestion not found"}
            
            # Check if user already voted
            for vote in self.votes["items"]:
                if vote["suggestion_id"] == suggestion_id and vote["username"] == username:
                    return {"status": "error", "message": "You have already voted for this suggestion"}
            
            # Add vote
            vote = {
                "id": str(uuid.uuid4()),
                "suggestion_id": suggestion_id,
                "username": username,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            self.votes["items"].append(vote)
            
            # Update suggestion vote count
            suggestion["vote_count"] += 1
            
            self._save_votes()
            self._save_suggestions()
            
            return {"status": "success", "message": "Vote added successfully"}
            
        except Exception as e:
            logger.error(f"Error adding vote: {str(e)}")
            return {"status": "error", "message": f"Failed to add vote: {str(e)}"}
    
    def remove_vote(self, suggestion_id: str, username: str) -> Dict[str, Any]:
        """
        Remove a vote from a suggestion.
        
        Args:
            suggestion_id: ID of the suggestion to remove vote from
            username: Username of the voter
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the suggestion
            suggestion = self.get_suggestion(suggestion_id)
            if not suggestion:
                return {"status": "error", "message": "Suggestion not found"}
            
            # Find and remove vote
            vote_found = False
            new_votes = []
            
            for vote in self.votes["items"]:
                if vote["suggestion_id"] == suggestion_id and vote["username"] == username:
                    vote_found = True
                else:
                    new_votes.append(vote)
            
            if not vote_found:
                return {"status": "error", "message": "You haven't voted for this suggestion"}
            
            self.votes["items"] = new_votes
            
            # Update suggestion vote count
            suggestion["vote_count"] = max(0, suggestion["vote_count"] - 1)
            
            self._save_votes()
            self._save_suggestions()
            
            return {"status": "success", "message": "Vote removed successfully"}
            
        except Exception as e:
            logger.error(f"Error removing vote: {str(e)}")
            return {"status": "error", "message": f"Failed to remove vote: {str(e)}"}
    
    def add_comment(self, suggestion_id: str, username: str, 
                   content: str) -> Dict[str, Any]:
        """
        Add a comment to a suggestion.
        
        Args:
            suggestion_id: ID of the suggestion to comment on
            username: Username of the commenter
            content: Comment content
            
        Returns:
            Dict with status and comment_id if successful
        """
        try:
            # Find the suggestion
            suggestion = self.get_suggestion(suggestion_id)
            if not suggestion:
                return {"status": "error", "message": "Suggestion not found"}
            
            # Validate content
            if not content or len(content.strip()) < 2:
                return {"status": "error", "message": "Comment content must be at least 2 characters"}
            
            # Add comment
            comment_id = str(uuid.uuid4())
            comment = {
                "id": comment_id,
                "username": username,
                "content": content,
                "created_at": datetime.datetime.now().isoformat(),
                "edited": False
            }
            
            if "comments" not in suggestion:
                suggestion["comments"] = []
            
            suggestion["comments"].append(comment)
            self._save_suggestions()
            
            return {"status": "success", "comment_id": comment_id}
            
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            return {"status": "error", "message": f"Failed to add comment: {str(e)}"}
    
    def edit_comment(self, suggestion_id: str, comment_id: str, 
                    username: str, content: str) -> Dict[str, Any]:
        """
        Edit a comment.
        
        Args:
            suggestion_id: ID of the suggestion containing the comment
            comment_id: ID of the comment to edit
            username: Username of the person editing the comment
            content: New comment content
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the suggestion
            suggestion = self.get_suggestion(suggestion_id)
            if not suggestion:
                return {"status": "error", "message": "Suggestion not found"}
            
            # Validate content
            if not content or len(content.strip()) < 2:
                return {"status": "error", "message": "Comment content must be at least 2 characters"}
            
            # Find and update comment
            comment_found = False
            
            for comment in suggestion.get("comments", []):
                if comment["id"] == comment_id:
                    # Check permissions
                    if comment["username"] != username:
                        return {"status": "error", "message": "You don't have permission to edit this comment"}
                    
                    comment["content"] = content
                    comment["edited"] = True
                    comment["edited_at"] = datetime.datetime.now().isoformat()
                    comment_found = True
                    break
            
            if not comment_found:
                return {"status": "error", "message": "Comment not found"}
            
            self._save_suggestions()
            return {"status": "success", "message": "Comment updated successfully"}
            
        except Exception as e:
            logger.error(f"Error editing comment: {str(e)}")
            return {"status": "error", "message": f"Failed to edit comment: {str(e)}"}
    
    def delete_comment(self, suggestion_id: str, comment_id: str, 
                      username: str) -> Dict[str, Any]:
        """
        Delete a comment.
        
        Args:
            suggestion_id: ID of the suggestion containing the comment
            comment_id: ID of the comment to delete
            username: Username of the person deleting the comment
            
        Returns:
            Dict with status and message
        """
        try:
            # Find the suggestion
            suggestion = self.get_suggestion(suggestion_id)
            if not suggestion:
                return {"status": "error", "message": "Suggestion not found"}
            
            # Find and remove comment
            comment_found = False
            new_comments = []
            
            for comment in suggestion.get("comments", []):
                if comment["id"] == comment_id:
                    # Check permissions
                    if comment["username"] != username:
                        return {"status": "error", "message": "You don't have permission to delete this comment"}
                    
                    comment_found = True
                else:
                    new_comments.append(comment)
            
            if not comment_found:
                return {"status": "error", "message": "Comment not found"}
            
            suggestion["comments"] = new_comments
            self._save_suggestions()
            
            return {"status": "success", "message": "Comment deleted successfully"}
            
        except Exception as e:
            logger.error(f"Error deleting comment: {str(e)}")
            return {"status": "error", "message": f"Failed to delete comment: {str(e)}"}
    
    def get_categories(self) -> List[Dict[str, str]]:
        """
        Get all suggestion categories.
        
        Returns:
            List of category dictionaries
        """
        return self.categories["items"]
    
    def add_category(self, name: str, description: str) -> Dict[str, Any]:
        """
        Add a new suggestion category.
        
        Args:
            name: Category name
            description: Category description
            
        Returns:
            Dict with status and category_id if successful
        """
        try:
            # Validate name
            if not name or len(name.strip()) < 2:
                return {"status": "error", "message": "Category name must be at least 2 characters"}
            
            # Generate ID from name
            category_id = name.lower().replace(" ", "_")
            
            # Check if category already exists
            for category in self.categories["items"]:
                if category["id"] == category_id:
                    return {"status": "error", "message": "Category already exists"}
            
            # Add category
            category = {
                "id": category_id,
                "name": name,
                "description": description
            }
            
            self.categories["items"].append(category)
            self._save_categories()
            
            return {"status": "success", "category_id": category_id}
            
        except Exception as e:
            logger.error(f"Error adding category: {str(e)}")
            return {"status": "error", "message": f"Failed to add category: {str(e)}"}
    
    def get_user_suggestions(self, username: str) -> List[Dict[str, Any]]:
        """
        Get all suggestions made by a specific user.
        
        Args:
            username: Username to get suggestions for
            
        Returns:
            List of suggestion dictionaries
        """
        return [s for s in self.suggestions["items"] if s["username"] == username]
    
    def get_suggestion_stats(self) -> Dict[str, Any]:
        """
        Get statistics about suggestions.
        
        Returns:
            Dict with suggestion statistics
        """
        # Count suggestions by status
        status_counts = {}
        for suggestion in self.suggestions["items"]:
            status = suggestion["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count suggestions by category
        category_counts = {}
        for suggestion in self.suggestions["items"]:
            category_id = suggestion["category_id"]
            category_counts[category_id] = category_counts.get(category_id, 0) + 1
        
        # Get top voted suggestions
        top_suggestions = sorted(self.suggestions["items"], key=lambda s: s["vote_count"], reverse=True)[:5]
        
        # Get recent suggestions
        recent_suggestions = sorted(self.suggestions["items"], key=lambda s: s["created_at"], reverse=True)[:5]
        
        # Calculate implementation rate
        implemented_count = status_counts.get("implemented", 0)
        total_count = len(self.suggestions["items"])
        implementation_rate = implemented_count / total_count if total_count > 0 else 0
        
        return {
            "total_suggestions": total_count,
            "by_status": status_counts,
            "by_category": category_counts,
            "top_suggestions": top_suggestions,
            "recent_suggestions": recent_suggestions,
            "implementation_rate": implementation_rate,
            "total_votes": len(self.votes["items"])
        }
