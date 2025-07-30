"""
Test suite for the Forum API functionality
"""
import os
import sys
import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, ANY

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from web.forum_api import forum_api, get_db
from flask import Flask, g

class MockResponse:
    """Mock class for Supabase responses"""
    def __init__(self, data=None, error=None, count=None):
        self.data = data or []
        self.error = error
        self.count = count
    
    def get(self, key, default=None):
        if key == 'data':
            return self.data
        elif key == 'error':
            return self.error
        elif key == 'count':
            return self.count
        return default

class ForumAPITest(unittest.TestCase):
    """Test cases for Forum API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.register_blueprint(forum_api)
        self.client = self.app.test_client()
        
        # Configure app context
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Mock database connection
        self.db_mock = MagicMock()
        
        # Mock g.user for authenticated endpoints
        g.user = "test_user_id"
        
        # Set up patchers
        self.get_db_patcher = patch('web.forum_api.get_db', return_value=self.db_mock)
        self.get_db_mock = self.get_db_patcher.start()
        
        self.user_manager_patcher = patch('web.forum_api.user_manager')
        self.user_manager_mock = self.user_manager_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.get_db_patcher.stop()
        self.user_manager_patcher.stop()
        self.app_context.pop()
    
    def test_get_categories(self):
        """Test getting all forum categories"""
        # Mock DB response
        mock_categories = [
            {"id": 1, "name": "Cycling Tips", "description": "Tips for efficient cycling", "icon": "bicycle"},
            {"id": 2, "name": "Route Sharing", "description": "Share your favorite routes", "icon": "map"}
        ]
        
        # Configure mock
        select_mock = MagicMock()
        execute_mock = MagicMock(return_value={"data": mock_categories})
        
        self.db_mock.table.return_value.select.return_value = select_mock
        select_mock.execute.return_value = execute_mock
        
        # Make request
        with self.app.test_request_context('/api/forum/categories'):
            response = forum_api.get_categories()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 200)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertEqual(response_data, mock_categories)
        
        # Verify DB calls
        self.db_mock.table.assert_called_once_with('forum_categories')
        self.db_mock.table().select.assert_called_once_with('*')
    
    def test_get_categories_error(self):
        """Test error handling when getting categories fails"""
        # Configure mock to return error
        select_mock = MagicMock()
        execute_mock = MagicMock(return_value={"error": "Database error"})
        
        self.db_mock.table.return_value.select.return_value = select_mock
        select_mock.execute.return_value = execute_mock
        
        # Make request
        with self.app.test_request_context('/api/forum/categories'):
            response = forum_api.get_categories()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 500)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertEqual(response_data, {"error": "Failed to fetch categories"})
    
    def test_get_topics(self):
        """Test getting topics for a category"""
        category_id = "1"
        mock_topics = [
            {"id": 1, "title": "First topic", "author_id": "user1", "username": "User One", 
             "profile_image": "avatar1.jpg", "reply_count": 5, "last_activity": "2025-05-01T12:00:00Z"},
            {"id": 2, "title": "Second topic", "author_id": "user2", "username": "User Two", 
             "profile_image": "avatar2.jpg", "reply_count": 2, "last_activity": "2025-05-02T14:30:00Z"}
        ]
        
        # Configure mocks
        raw_mock = MagicMock()
        raw_execute_mock = MagicMock(return_value={"data": mock_topics})
        
        count_mock = MagicMock()
        count_execute_mock = MagicMock(return_value={"count": 10})
        
        self.db_mock.raw.return_value = raw_mock
        raw_mock.execute.return_value = raw_execute_mock
        
        self.db_mock.table.return_value.select.return_value.eq.return_value = count_mock
        count_mock.execute.return_value = count_execute_mock
        
        # Make request
        with self.app.test_request_context(f'/api/forum/topics/{category_id}?page=1&page_size=10'):
            response = forum_api.get_topics(category_id)
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 200)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertEqual(response_data["topics"], mock_topics)
        self.assertEqual(response_data["pagination"]["total_count"], 10)
        self.assertEqual(response_data["pagination"]["page"], 1)
    
    def test_create_topic(self):
        """Test creating a new topic"""
        mock_topic_data = {
            "title": "Test Topic",
            "content": "<p>This is a test topic</p>",
            "category_id": "1"
        }
        
        # Configure mock
        insert_mock = MagicMock()
        execute_mock = MagicMock(return_value={"data": [{"id": "new_topic_id"}]})
        
        self.db_mock.table.return_value.insert.return_value = insert_mock
        insert_mock.execute.return_value = execute_mock
        
        # Make request
        with self.app.test_request_context(
            '/api/forum/topic',
            method='POST',
            json=mock_topic_data
        ):
            response = forum_api.create_topic()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 201)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["topic_id"], "new_topic_id")
        
        # Verify DB calls
        self.db_mock.table.assert_called_with('forum_topics')
        self.db_mock.table().insert.assert_called_once()
    
    def test_create_topic_missing_fields(self):
        """Test error handling when creating topic with missing fields"""
        # Missing content field
        mock_incomplete_data = {
            "title": "Test Topic",
            "category_id": "1"
        }
        
        # Make request
        with self.app.test_request_context(
            '/api/forum/topic',
            method='POST',
            json=mock_incomplete_data
        ):
            response = forum_api.create_topic()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 400)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertEqual(response_data["error"], "Missing required field: content")
    
    def test_create_post(self):
        """Test creating a new post (reply)"""
        mock_post_data = {
            "topic_id": "test_topic_id",
            "content": "<p>This is a test reply</p>"
        }
        
        # Configure mock
        insert_mock = MagicMock()
        execute_mock = MagicMock(return_value={"data": [{"id": "new_post_id"}]})
        
        update_mock = MagicMock()
        update_execute_mock = MagicMock(return_value={"data": [{"id": "test_topic_id"}]})
        
        self.db_mock.table.return_value.insert.return_value = insert_mock
        insert_mock.execute.return_value = execute_mock
        
        self.db_mock.table.return_value.update.return_value.eq.return_value = update_mock
        update_mock.execute.return_value = update_execute_mock
        
        # Make request
        with self.app.test_request_context(
            '/api/forum/post',
            method='POST',
            json=mock_post_data
        ):
            response = forum_api.create_post()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 201)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["post_id"], "new_post_id")
    
    def test_edit_post(self):
        """Test editing a post"""
        post_id = "test_post_id"
        mock_edit_data = {
            "content": "<p>Updated content</p>"
        }
        
        # Configure mocks
        # 1. First, mock getting the post to check ownership
        post_mock = MagicMock()
        post_execute_mock = MagicMock(return_value={"data": {"author_id": "test_user_id"}})
        
        self.db_mock.table.return_value.select.return_value.eq.return_value.single.return_value = post_mock
        post_mock.execute.return_value = post_execute_mock
        
        # 2. Then, mock updating the post
        update_mock = MagicMock()
        update_execute_mock = MagicMock(return_value={"data": [{"id": post_id}]})
        
        self.db_mock.table.return_value.update.return_value.eq.return_value = update_mock
        update_mock.execute.return_value = update_execute_mock
        
        # Make request
        with self.app.test_request_context(
            f'/api/forum/post/{post_id}',
            method='PUT',
            json=mock_edit_data
        ):
            response = forum_api.edit_post(post_id)
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 200)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertTrue(response_data["success"])
        
        # Verify the update data includes edited flag and timestamp
        update_call_args = self.db_mock.table().update.call_args[0][0]
        self.assertEqual(update_call_args["content"], "<p>Updated content</p>")
        self.assertTrue(update_call_args["edited"])
        self.assertIn("updated_at", update_call_args)
    
    def test_add_reaction(self):
        """Test adding a reaction to a post"""
        mock_reaction_data = {
            "post_id": "test_post_id",
            "reaction_type": "like"
        }
        
        # Configure mocks for checking existing reaction (not found)
        existing_mock = MagicMock()
        existing_execute_mock = MagicMock(return_value={"data": []})
        
        self.db_mock.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value = existing_mock
        existing_mock.execute.return_value = existing_execute_mock
        
        # Configure mock for inserting reaction
        insert_mock = MagicMock()
        insert_execute_mock = MagicMock(return_value={"data": [{"id": "new_reaction_id"}]})
        
        self.db_mock.table.return_value.insert.return_value = insert_mock
        insert_mock.execute.return_value = insert_execute_mock
        
        # Make request
        with self.app.test_request_context(
            '/api/forum/reaction',
            method='POST',
            json=mock_reaction_data
        ):
            response = forum_api.add_reaction()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 200)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["action"], "added")
    
    def test_add_reaction_toggle(self):
        """Test toggling a reaction (removing existing)"""
        mock_reaction_data = {
            "post_id": "test_post_id",
            "reaction_type": "like"
        }
        
        # Configure mocks for checking existing reaction (found)
        existing_mock = MagicMock()
        existing_execute_mock = MagicMock(return_value={"data": [{"id": "existing_reaction_id"}]})
        
        self.db_mock.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value = existing_mock
        existing_mock.execute.return_value = existing_execute_mock
        
        # Configure mock for deleting reaction
        delete_mock = MagicMock()
        delete_execute_mock = MagicMock(return_value={"data": [{"id": "existing_reaction_id"}]})
        
        self.db_mock.table.return_value.delete.return_value.eq.return_value = delete_mock
        delete_mock.execute.return_value = delete_execute_mock
        
        # Make request
        with self.app.test_request_context(
            '/api/forum/reaction',
            method='POST',
            json=mock_reaction_data
        ):
            response = forum_api.add_reaction()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 200)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["action"], "removed")
    
    def test_search_forum(self):
        """Test searching forum content"""
        # Mock search results
        mock_topics = [
            {"id": 1, "title": "Cycling Safety", "content": "Tips for safe cycling"},
            {"id": 2, "title": "Mountain Routes", "content": "Best mountain cycling routes"}
        ]
        
        mock_posts = [
            {"id": 1, "topic_id": 1, "content": "I agree with these safety tips"},
            {"id": 2, "topic_id": 2, "content": "I tried the mountain route yesterday"}
        ]
        
        # Configure mocks
        topics_raw_mock = MagicMock()
        topics_execute_mock = MagicMock(return_value={"data": mock_topics})
        
        posts_raw_mock = MagicMock()
        posts_execute_mock = MagicMock(return_value={"data": mock_posts})
        
        # Need to handle two different raw() calls
        def side_effect_raw(*args, **kwargs):
            query = args[0]
            if "forum_topics t" in query:
                return topics_raw_mock
            elif "forum_posts p" in query:
                return posts_raw_mock
            return MagicMock()
            
        self.db_mock.raw.side_effect = side_effect_raw
        topics_raw_mock.execute.return_value = topics_execute_mock
        posts_raw_mock.execute.return_value = posts_execute_mock
        
        # Make request
        with self.app.test_request_context('/api/forum/search?q=cycling'):
            response = forum_api.search_forum()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 200)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertEqual(response_data["topics"], mock_topics)
        self.assertEqual(response_data["posts"], mock_posts)
    
    def test_search_forum_short_query(self):
        """Test search validation with short query"""
        # Make request with a short query
        with self.app.test_request_context('/api/forum/search?q=ab'):
            response = forum_api.search_forum()
            
        # Verify response
        self.assertIsInstance(response, tuple)
        self.assertEqual(response[1], 400)  # Status code
        
        response_data = json.loads(response[0].get_data(as_text=True))
        self.assertEqual(response_data["error"], "Search query too short")


if __name__ == '__main__':
    unittest.main()
