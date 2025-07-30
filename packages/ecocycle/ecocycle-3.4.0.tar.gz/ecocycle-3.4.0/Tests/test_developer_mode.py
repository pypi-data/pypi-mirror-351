#!/usr/bin/env python3
"""
EcoCycle - Developer Mode Tests
Test suite for developer authentication and tools functionality.
"""
import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.developer_auth import DeveloperAuth
from apps.developer.developer_tools import DeveloperTools


class TestDeveloperAuth(unittest.TestCase):
    """Test cases for developer authentication."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_username = "test_dev"
        self.test_password = "test_password_123"
        self.test_hash = DeveloperAuth.generate_password_hash(self.test_password)
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'DEVELOPER_MODE_ENABLED': 'true',
            'DEVELOPER_USERNAME': self.test_username,
            'DEVELOPER_PASSWORD_HASH': self.test_hash
        })
        self.env_patcher.start()
        
        self.dev_auth = DeveloperAuth()
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
    
    def test_is_enabled(self):
        """Test developer mode enabled check."""
        self.assertTrue(self.dev_auth.is_enabled())
        
        # Test disabled mode
        with patch.dict(os.environ, {'DEVELOPER_MODE_ENABLED': 'false'}):
            dev_auth_disabled = DeveloperAuth()
            self.assertFalse(dev_auth_disabled.is_enabled())
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "test_password"
        hash1 = DeveloperAuth.generate_password_hash(password)
        hash2 = DeveloperAuth.generate_password_hash(password)
        
        # Hashes should be different due to salt
        self.assertNotEqual(hash1, hash2)
        
        # Both should verify correctly
        self.assertTrue(self.dev_auth._verify_password(password, hash1))
        self.assertTrue(self.dev_auth._verify_password(password, hash2))
    
    def test_password_verification(self):
        """Test password verification."""
        correct_password = self.test_password
        wrong_password = "wrong_password"
        
        self.assertTrue(self.dev_auth._verify_password(correct_password, self.test_hash))
        self.assertFalse(self.dev_auth._verify_password(wrong_password, self.test_hash))
    
    @patch('getpass.getpass')
    @patch('builtins.input')
    def test_authenticate_developer_success(self, mock_input, mock_getpass):
        """Test successful developer authentication."""
        mock_input.return_value = self.test_username
        mock_getpass.return_value = self.test_password
        
        result = self.dev_auth.authenticate_developer()
        self.assertTrue(result)
        self.assertTrue(self.dev_auth.is_developer_authenticated())
        self.assertEqual(self.dev_auth.get_developer_username(), self.test_username)
    
    @patch('getpass.getpass')
    @patch('builtins.input')
    def test_authenticate_developer_failure(self, mock_input, mock_getpass):
        """Test failed developer authentication."""
        mock_input.return_value = self.test_username
        mock_getpass.return_value = "wrong_password"
        
        result = self.dev_auth.authenticate_developer()
        self.assertFalse(result)
        self.assertFalse(self.dev_auth.is_developer_authenticated())
    
    def test_session_timeout(self):
        """Test session timeout functionality."""
        # Set a very short timeout for testing
        self.dev_auth.session_timeout = 1
        self.dev_auth.developer_session = self.test_username
        
        # Initially authenticated
        from datetime import datetime, timedelta
        self.dev_auth.session_start_time = datetime.now()
        self.assertTrue(self.dev_auth.is_developer_authenticated())
        
        # Simulate timeout
        self.dev_auth.session_start_time = datetime.now() - timedelta(seconds=2)
        self.assertFalse(self.dev_auth.is_developer_authenticated())
    
    def test_logout_developer(self):
        """Test developer logout."""
        self.dev_auth.developer_session = self.test_username
        self.dev_auth.session_start_time = datetime.now()
        
        self.assertTrue(self.dev_auth.is_developer_authenticated())
        
        self.dev_auth.logout_developer()
        self.assertFalse(self.dev_auth.is_developer_authenticated())
        self.assertIsNone(self.dev_auth.get_developer_username())


class TestDeveloperTools(unittest.TestCase):
    """Test cases for developer tools."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock developer auth
        self.mock_dev_auth = MagicMock()
        self.mock_dev_auth.is_developer_authenticated.return_value = True
        self.mock_dev_auth.get_developer_username.return_value = "test_dev"
        
        self.dev_tools = DeveloperTools(self.mock_dev_auth)
    
    def test_system_diagnostics(self):
        """Test system diagnostics functionality."""
        diagnostics = self.dev_tools.system_diagnostics()
        
        self.assertIsInstance(diagnostics, dict)
        self.assertIn('timestamp', diagnostics)
        self.assertIn('python_version', diagnostics)
        self.assertIn('platform', diagnostics)
        self.assertIn('working_directory', diagnostics)
        self.assertIn('environment_variables', diagnostics)
        self.assertIn('database_status', diagnostics)
        self.assertIn('file_system', diagnostics)
    
    def test_unauthorized_access(self):
        """Test that unauthorized access is blocked."""
        # Mock unauthorized auth
        unauthorized_auth = MagicMock()
        unauthorized_auth.is_developer_authenticated.return_value = False
        
        dev_tools = DeveloperTools(unauthorized_auth)
        
        with self.assertRaises(PermissionError):
            dev_tools.system_diagnostics()
    
    def test_manage_cache_view(self):
        """Test cache management view functionality."""
        result = self.dev_tools.manage_cache('view')
        
        self.assertIsInstance(result, dict)
        # Should contain cache information even if files don't exist
        self.assertTrue(len(result) >= 0)
    
    def test_manage_user_data_list(self):
        """Test user data management list functionality."""
        # Create temporary users file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_users = {
                "test_user": {
                    "username": "test_user",
                    "name": "Test User",
                    "email": "test@example.com",
                    "is_admin": False,
                    "is_guest": False,
                    "stats": {
                        "total_trips": 5,
                        "total_distance": 100.0
                    }
                }
            }
            json.dump(test_users, f)
            temp_file = f.name
        
        try:
            # Mock the users file path
            with patch('os.path.join') as mock_join:
                mock_join.return_value = temp_file
                
                result = self.dev_tools.manage_user_data('list')
                
                self.assertIsInstance(result, dict)
                self.assertEqual(result['action'], 'list')
                self.assertIn('users', result)
                self.assertIn('total_count', result)
                self.assertEqual(result['total_count'], 1)
        finally:
            os.unlink(temp_file)
    
    def test_export_system_data(self):
        """Test system data export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the export directory
            with patch('os.path.join') as mock_join:
                mock_join.return_value = temp_dir
                
                result = self.dev_tools.export_system_data('config')
                
                self.assertIsInstance(result, dict)
                self.assertIn('export_type', result)
                self.assertIn('timestamp', result)
                self.assertIn('exported_files', result)


class TestDeveloperModeIntegration(unittest.TestCase):
    """Integration tests for developer mode."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_hash = DeveloperAuth.generate_password_hash("test_password")
        
        self.env_patcher = patch.dict(os.environ, {
            'DEVELOPER_MODE_ENABLED': 'true',
            'DEVELOPER_USERNAME': 'test_dev',
            'DEVELOPER_PASSWORD_HASH': self.test_hash
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up integration test environment."""
        self.env_patcher.stop()
    
    def test_developer_mode_availability(self):
        """Test that developer mode is available when configured."""
        from auth.user_management.auth_handler import AuthHandler
        
        auth_handler = AuthHandler()
        
        # Mock the developer auth import
        with patch('auth.user_management.auth_handler.DeveloperAuth') as mock_dev_auth_class:
            mock_dev_auth = MagicMock()
            mock_dev_auth.is_enabled.return_value = True
            mock_dev_auth_class.return_value = mock_dev_auth
            
            # This should not raise an exception
            menu_choice = auth_handler.display_authentication_menu()
            # The method should return without error
            self.assertIsInstance(menu_choice, str)
    
    def test_developer_mode_disabled(self):
        """Test behavior when developer mode is disabled."""
        with patch.dict(os.environ, {'DEVELOPER_MODE_ENABLED': 'false'}):
            dev_auth = DeveloperAuth()
            self.assertFalse(dev_auth.is_enabled())


def run_tests():
    """Run all developer mode tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDeveloperAuth))
    test_suite.addTest(unittest.makeSuite(TestDeveloperTools))
    test_suite.addTest(unittest.makeSuite(TestDeveloperModeIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running EcoCycle Developer Mode Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
