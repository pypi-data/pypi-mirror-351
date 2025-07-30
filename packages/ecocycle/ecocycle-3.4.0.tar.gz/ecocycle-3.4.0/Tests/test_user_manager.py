"""
Test module for user_manager.py
"""
import os
import sys
import json
import unittest
from unittest import mock
from datetime import datetime
import tempfile

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import auth.user_management.user_manager

class TestUserManager(unittest.TestCase):
    """Test cases for UserManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for cache
        self.temp_cache = tempfile.NamedTemporaryFile(delete=False)
        self.temp_cache.close()
        
        # Create a test user manager
        self.mock_sheets_manager = mock.MagicMock()
        self.user_manager = user_manager.UserManager(self.mock_sheets_manager)
        self.user_manager.cache_filename = self.temp_cache.name
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary file
        if os.path.exists(self.temp_cache.name):
            os.unlink(self.temp_cache.name)
    
    def test_load_cache_no_file(self):
        """Test loading cache when file doesn't exist."""
        # Remove the cache file
        if os.path.exists(self.user_manager.cache_filename):
            os.unlink(self.user_manager.cache_filename)
        
        # Load the cache
        self.user_manager.load_cache()
        
        # Verify no user is loaded
        self.assertIsNone(self.user_manager.current_user)
    
    def test_load_cache_with_file(self):
        """Test loading cache with existing file."""
        # Create a cache file with test data
        test_data = {
            'current_user': 'test_user',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.user_manager.cache_filename, 'w') as f:
            json.dump(test_data, f)
        
        # Load the cache
        self.user_manager.load_cache()
        
        # Verify the user is loaded
        self.assertEqual(self.user_manager.current_user, 'test_user')
    
    def test_save_cache(self):
        """Test saving cache."""
        # Set the current user
        self.user_manager.current_user = 'test_user'
        
        # Save the cache
        self.user_manager.save_cache()
        
        # Verify the cache file exists
        self.assertTrue(os.path.exists(self.user_manager.cache_filename))
        
        # Verify the cache file contains the user
        with open(self.user_manager.cache_filename, 'r') as f:
            cache_data = json.load(f)
            self.assertEqual(cache_data['current_user'], 'test_user')
    
    def test_get_user_data_no_sheets_manager(self):
        """Test getting user data without sheets manager."""
        # Create a user manager without sheets manager
        user_mgr = user_manager.UserManager(None)
        
        # Try to get user data
        user_data, row_num = user_mgr.get_user_data('test_user')
        
        # Verify the result
        self.assertIsNone(user_data)
        self.assertEqual(row_num, -1)
    
    def test_get_user_data_with_sheets_manager(self):
        """Test getting user data with sheets manager."""
        # Mock the sheets manager to return data
        test_data = ['test_user', '10', '20', '30', '40', '50', '60', '70']
        self.mock_sheets_manager.get_user_data.return_value = (test_data, 1)
        
        # Get user data
        user_data, row_num = self.user_manager.get_user_data('test_user')
        
        # Verify the result
        self.assertEqual(user_data, test_data)
        self.assertEqual(row_num, 1)
        
        # Verify the current user is set
        self.assertEqual(self.user_manager.current_user, 'test_user')
    
    def test_create_user_no_sheets_manager(self):
        """Test creating user without sheets manager."""
        # Create a user manager without sheets manager
        user_mgr = user_manager.UserManager(None)
        
        # Try to create a user
        result = user_mgr.create_user('test_user')
        
        # Verify the result
        self.assertFalse(result)
    
    def test_create_user_already_exists(self):
        """Test creating user that already exists."""
        # Mock the sheets manager to return existing user
        self.mock_sheets_manager.get_user_data.return_value = (['test_user', '0', '0', '0', '0', '0', '0', '0'], 1)
        
        # Try to create a user
        result = self.user_manager.create_user('test_user')
        
        # Verify the result
        self.assertFalse(result)
    
    def test_create_user_success(self):
        """Test creating user successfully."""
        # Mock the sheets manager to return no existing user, then success on update
        self.mock_sheets_manager.get_user_data.return_value = (None, -1)
        self.mock_sheets_manager.update_user_data.return_value = True
        
        # Create a user
        result = self.user_manager.create_user('test_user')
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the current user is set
        self.assertEqual(self.user_manager.current_user, 'test_user')
    
    def test_update_user_data_no_sheets_manager(self):
        """Test updating user data without sheets manager."""
        # Create a user manager without sheets manager
        user_mgr = user_manager.UserManager(None)
        
        # Try to update user data
        result = user_mgr.update_user_data('test_user', ['test_user', '10', '20', '30', '40', '50', '60', '70'])
        
        # Verify the result
        self.assertFalse(result)
    
    def test_update_user_data_success(self):
        """Test updating user data successfully."""
        # Mock the sheets manager to return success on update
        self.mock_sheets_manager.update_user_data.return_value = True
        
        # Update user data
        result = self.user_manager.update_user_data('test_user', ['test_user', '10', '20', '30', '40', '50', '60', '70'])
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the current user is set
        self.assertEqual(self.user_manager.current_user, 'test_user')
    
    def test_get_current_user(self):
        """Test getting current user."""
        # Set the current user
        self.user_manager.current_user = 'test_user'
        
        # Get the current user
        result = self.user_manager.get_current_user()
        
        # Verify the result
        self.assertEqual(result, 'test_user')
    
    def test_set_current_user(self):
        """Test setting current user."""
        # Set the current user
        self.user_manager.set_current_user('test_user')
        
        # Verify the current user is set
        self.assertEqual(self.user_manager.current_user, 'test_user')
        
        # Verify the cache is saved
        with open(self.user_manager.cache_filename, 'r') as f:
            cache_data = json.load(f)
            self.assertEqual(cache_data['current_user'], 'test_user')

if __name__ == '__main__':
    unittest.main()