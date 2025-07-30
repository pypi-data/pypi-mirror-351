"""
EcoCycle Forum Controller
=======================

This controller handles all forum-related operations including categories,
topics, posts, and user interactions for the community support forum.
"""

import datetime
import logging
from typing import Dict, List, Optional, Any
import uuid

from models.user_manager import UserManager

logger = logging.getLogger(__name__)

class ForumController:
    """Controller responsible for handling forum-related operations."""
    
    def __init__(self, user_manager: UserManager, db_path: str = None):
        """
        Initialize the ForumController.
        
        Args:
            user_manager: The user manager instance for authentication
            db_path: Optional path to the forum database
        """
        self.user_manager = user_manager
        
        # In a real implementation, this would use proper database models
        # For now, we'll use in-memory data for demonstration
        self.categories = [
            {
                "id": "general",
                "name": "General Discussion",
                "description": "General discussion about EcoCycle and sustainable transportation",
                "icon": "comments",
                "topic_count": 15,
                "post_count": 87
            },
            {
                "id": "help",
                "name": "Help & Support",
                "description": "Get help with using EcoCycle features and troubleshooting issues",
                "icon": "life-ring",
                "topic_count": 32,
                "post_count": 213
            },
            {
                "id": "feature-requests",
                "name": "Feature Requests",
                "description": "Suggest and discuss new features for EcoCycle",
                "icon": "lightbulb",
                "topic_count": 24,
                "post_count": 156
            },
            {
                "id": "routes",
                "name": "Route Sharing",
                "description": "Share and discover cycling routes created by the community",
                "icon": "map-marked-alt",
                "topic_count": 45,
                "post_count": 189
            },
            {
                "id": "challenges",
                "name": "Challenges & Events",
                "description": "Discuss ongoing challenges and coordinate community events",
                "icon": "trophy",
                "topic_count": 18,
                "post_count": 124
            },
            {
                "id": "technical",
                "name": "Technical Discussion",
                "description": "Technical discussions about EcoCycle development and APIs",
                "icon": "code",
                "topic_count": 12,
                "post_count": 67
            }
        ]
        
        # Sample topics and posts would be stored here
        self.topics = []
        self.posts = []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all forum categories.
        
        Returns:
            List of category dictionaries
        """
        return self.categories
    
    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific category by ID.
        
        Args:
            category_id: ID of the category to retrieve
            
        Returns:
            Category dictionary if found, None otherwise
        """
        for category in self.categories:
            if category["id"] == category_id:
                return category
        return None
    
    def get_topics(self, category_id: Optional[str] = None, 
                  page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Get topics, optionally filtered by category.
        
        Args:
            category_id: Optional category ID to filter by
            page: Page number for pagination
            limit: Number of topics per page
            
        Returns:
            Dict containing topics and pagination info
        """
        # This would normally query the database
        # For demonstration, we'll return sample data
        filtered_topics = [
            {
                "id": "topic1",
                "category_id": "help",
                "title": "How do I sync my mobile app with desktop?",
                "creator": "cycling_enthusiast",
                "created_at": "2025-04-28T14:32:11",
                "last_post_at": "2025-05-04T09:16:45",
                "view_count": 128,
                "post_count": 7,
                "is_pinned": False,
                "is_solved": True
            },
            {
                "id": "topic2",
                "category_id": "feature-requests",
                "title": "Add integration with Strava API",
                "creator": "mountain_biker",
                "created_at": "2025-04-30T10:15:22",
                "last_post_at": "2025-05-05T08:22:33",
                "view_count": 85,
                "post_count": 12,
                "is_pinned": False,
                "is_solved": False
            },
            {
                "id": "topic3",
                "category_id": "help",
                "title": "Can't update profile picture - getting error",
                "creator": "city_commuter",
                "created_at": "2025-05-01T16:42:18",
                "last_post_at": "2025-05-02T11:55:21",
                "view_count": 42,
                "post_count": 5,
                "is_pinned": False,
                "is_solved": True
            }
        ]
        
        if category_id:
            filtered_topics = [t for t in filtered_topics if t["category_id"] == category_id]
        
        # Calculate pagination
        total_topics = len(filtered_topics)
        total_pages = (total_topics + limit - 1) // limit
        
        start_idx = (page - 1) * limit
        end_idx = min(start_idx + limit, total_topics)
        
        return {
            "topics": filtered_topics[start_idx:end_idx],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_topics": total_topics,
                "has_previous": page > 1,
                "has_next": page < total_pages
            }
        }
    
    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific topic by ID.
        
        Args:
            topic_id: ID of the topic to retrieve
            
        Returns:
            Topic dictionary if found, None otherwise
        """
        # This would normally query the database
        if topic_id == "topic1":
            return {
                "id": "topic1",
                "category_id": "help",
                "title": "How do I sync my mobile app with desktop?",
                "creator": "cycling_enthusiast",
                "created_at": "2025-04-28T14:32:11",
                "last_post_at": "2025-05-04T09:16:45",
                "view_count": 128,
                "post_count": 7,
                "is_pinned": False,
                "is_solved": True,
                "posts": [
                    {
                        "id": "post1",
                        "topic_id": "topic1",
                        "author": "cycling_enthusiast",
                        "content": "I just installed EcoCycle on both my desktop and mobile, but I can't figure out how to sync my data between them. Can someone help?",
                        "created_at": "2025-04-28T14:32:11",
                        "edited_at": None,
                        "likes": 0
                    },
                    {
                        "id": "post2",
                        "topic_id": "topic1",
                        "author": "eco_helper",
                        "content": "Hi! To sync your devices, you need to:\n\n1. Make sure you're logged into the same account on both devices\n2. Go to Settings > Synchronization on the desktop app\n3. Enable 'Cloud Sync'\n4. On your mobile app, go to Settings > Account and tap 'Sync Now'\n\nLet me know if that works!",
                        "created_at": "2025-04-28T15:03:45",
                        "edited_at": None,
                        "likes": 3,
                        "is_solution": True
                    }
                ]
            }
        return None
    
    def create_topic(self, category_id: str, title: str, content: str, 
                    username: str) -> Dict[str, Any]:
        """
        Create a new forum topic.
        
        Args:
            category_id: Category ID for the new topic
            title: Topic title
            content: Initial post content
            username: Username of the topic creator
            
        Returns:
            Dict containing status and topic_id if successful
        """
        try:
            # Verify user exists
            if not self.user_manager.user_exists(username):
                return {"status": "error", "message": "User not found"}
            
            # Verify category exists
            category = self.get_category(category_id)
            if not category:
                return {"status": "error", "message": "Category not found"}
            
            # Validate title and content
            if not title or len(title.strip()) < 5:
                return {"status": "error", "message": "Title must be at least 5 characters"}
            
            if not content or len(content.strip()) < 10:
                return {"status": "error", "message": "Content must be at least 10 characters"}
            
            # In a real implementation, this would create records in the database
            topic_id = str(uuid.uuid4())
            
            logger.info(f"Topic created successfully: {topic_id}")
            return {"status": "success", "topic_id": topic_id}
            
        except Exception as e:
            logger.error(f"Error creating topic: {str(e)}")
            return {"status": "error", "message": f"Failed to create topic: {str(e)}"}
    
    def create_post(self, topic_id: str, content: str, username: str) -> Dict[str, Any]:
        """
        Create a new post in a topic.
        
        Args:
            topic_id: Topic ID to post in
            content: Post content
            username: Username of the post author
            
        Returns:
            Dict containing status and post_id if successful
        """
        try:
            # Verify user exists
            if not self.user_manager.user_exists(username):
                return {"status": "error", "message": "User not found"}
            
            # Verify topic exists
            topic = self.get_topic(topic_id)
            if not topic:
                return {"status": "error", "message": "Topic not found"}
            
            # Validate content
            if not content or len(content.strip()) < 10:
                return {"status": "error", "message": "Content must be at least 10 characters"}
            
            # In a real implementation, this would create a record in the database
            post_id = str(uuid.uuid4())
            
            logger.info(f"Post created successfully: {post_id}")
            return {"status": "success", "post_id": post_id}
            
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return {"status": "error", "message": f"Failed to create post: {str(e)}"}
    
    def mark_solution(self, post_id: str, topic_id: str, username: str) -> Dict[str, Any]:
        """
        Mark a post as the solution to a topic.
        
        Args:
            post_id: Post ID to mark as solution
            topic_id: Topic ID containing the post
            username: Username of the user marking the solution
            
        Returns:
            Dict containing status and success message if successful
        """
        try:
            # Verify user exists and has permission
            if not self.user_manager.user_exists(username):
                return {"status": "error", "message": "User not found"}
            
            # Verify topic exists and user is either the creator or a moderator
            topic = self.get_topic(topic_id)
            if not topic:
                return {"status": "error", "message": "Topic not found"}
            
            user_role = self.user_manager.get_user_role(username)
            if username != topic["creator"] and user_role not in ["admin", "moderator"]:
                return {"status": "error", "message": "You don't have permission to mark solutions in this topic"}
            
            # In a real implementation, this would update the database
            
            logger.info(f"Post {post_id} marked as solution for topic {topic_id}")
            return {"status": "success", "message": "Post marked as solution"}
            
        except Exception as e:
            logger.error(f"Error marking solution: {str(e)}")
            return {"status": "error", "message": f"Failed to mark solution: {str(e)}"}
    
    def search_forum(self, query: str, category_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for topics and posts in the forum.
        
        Args:
            query: Search query
            category_id: Optional category ID to limit search to
            
        Returns:
            Dict containing search results
        """
        try:
            # In a real implementation, this would query the database with full-text search
            
            # For demonstration, we'll return sample results
            results = {
                "topics": [
                    {
                        "id": "topic_result1",
                        "title": f"Sample topic matching '{query}'",
                        "category_id": "help",
                        "category_name": "Help & Support",
                        "created_at": "2025-04-20T10:15:22",
                        "post_count": 7,
                        "is_solved": True
                    }
                ],
                "posts": [
                    {
                        "id": "post_result1",
                        "topic_id": "topic_related1",
                        "topic_title": f"Topic containing post with '{query}'",
                        "content_excerpt": f"...matching text with <strong>{query}</strong> highlighted...",
                        "author": "eco_expert",
                        "created_at": "2025-04-22T14:37:18"
                    }
                ],
                "total_results": 2
            }
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"Error searching forum: {str(e)}")
            return {"status": "error", "message": f"Failed to search forum: {str(e)}"}
