#!/usr/bin/env python3
"""
Test script for the configuration manager module.
This script tests the functionality of the configuration manager.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
import config.config_manager as config_manager


class TestConfigManager(unittest.TestCase):
    """Test cases for the configuration manager module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test configuration files
        self.test_dir = tempfile.mkdtemp()
        self.test_config_dir = os.path.join(self.test_dir, 'config')
        self.test_profiles_dir = os.path.join(self.test_config_dir, 'profiles')
        
        # Create directories
        os.makedirs(self.test_config_dir, exist_ok=True)
        os.makedirs(self.test_profiles_dir, exist_ok=True)
        
        # Set up test configuration files
        self.test_default_config_file = os.path.join(self.test_config_dir, 'default_config.yaml')
        self.test_user_config_file = os.path.join(self.test_config_dir, 'user_config.yaml')
        
        # Save original paths
        self.original_config_dir = config_manager.CONFIG_DIR
        self.original_profiles_dir = config_manager.PROFILES_DIR
        self.original_default_config_file = config_manager.DEFAULT_CONFIG_FILE
        self.original_user_config_file = config_manager.USER_CONFIG_FILE
        
        # Override paths
        config_manager.CONFIG_DIR = self.test_config_dir
        config_manager.PROFILES_DIR = self.test_profiles_dir
        config_manager.DEFAULT_CONFIG_FILE = self.test_default_config_file
        config_manager.USER_CONFIG_FILE = self.test_user_config_file
        
        # Create a test configuration manager
        self.config_mgr = config_manager.ConfigManager()
        
        # Reset the singleton instance to force reinitialization
        config_manager.ConfigManager._instance = None
        config_manager.ConfigManager._instance = self.config_mgr
        self.config_mgr._initialized = False
        self.config_mgr.__init__()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original paths
        config_manager.CONFIG_DIR = self.original_config_dir
        config_manager.PROFILES_DIR = self.original_profiles_dir
        config_manager.DEFAULT_CONFIG_FILE = self.original_default_config_file
        config_manager.USER_CONFIG_FILE = self.original_user_config_file
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_singleton(self):
        """Test that ConfigManager is a singleton."""
        # Create two instances
        config_mgr1 = config_manager.ConfigManager()
        config_mgr2 = config_manager.ConfigManager()
        
        # Check that they are the same instance
        self.assertIs(config_mgr1, config_mgr2)

    def test_get_config(self):
        """Test the get method."""
        # Test getting a value that exists
        value = self.config_mgr.get('app.name')
        self.assertEqual(value, 'EcoCycle')
        
        # Test getting a nested value
        value = self.config_mgr.get('environmental.co2_per_km')
        self.assertEqual(value, 0.192)
        
        # Test getting a value that doesn't exist
        value = self.config_mgr.get('nonexistent.key', 'default_value')
        self.assertEqual(value, 'default_value')

    def test_set_config(self):
        """Test the set method."""
        # Set a value
        self.config_mgr.set('app.name', 'TestApp')
        
        # Check that the value was set
        value = self.config_mgr.get('app.name')
        self.assertEqual(value, 'TestApp')
        
        # Set a nested value
        self.config_mgr.set('environmental.co2_per_km', 0.2)
        
        # Check that the value was set
        value = self.config_mgr.get('environmental.co2_per_km')
        self.assertEqual(value, 0.2)
        
        # Set a value in a new section
        self.config_mgr.set('new_section.new_key', 'new_value')
        
        # Check that the value was set
        value = self.config_mgr.get('new_section.new_key')
        self.assertEqual(value, 'new_value')

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        # Set a value
        self.config_mgr.set('app.name', 'TestApp')
        
        # Save configuration
        self.config_mgr.save_config()
        
        # Check that the user configuration file was created
        self.assertTrue(os.path.exists(self.test_user_config_file))
        
        # Create a new configuration manager to load the saved configuration
        config_manager.ConfigManager._instance = None
        new_config_mgr = config_manager.ConfigManager()
        
        # Check that the value was loaded
        value = new_config_mgr.get('app.name')
        self.assertEqual(value, 'TestApp')

    def test_profiles(self):
        """Test profile management."""
        # Create a profile
        self.config_mgr.create_profile('test_profile')
        
        # Check that the profile was created
        profiles = self.config_mgr.get_profiles()
        self.assertIn('test_profile', profiles)
        
        # Check that the profile file was created
        profile_file = os.path.join(self.test_profiles_dir, 'test_profile.yaml')
        self.assertTrue(os.path.exists(profile_file))
        
        # Update the profile
        self.config_mgr.update_profile('test_profile', {'app': {'name': 'ProfileApp'}})
        
        # Activate the profile
        self.config_mgr.activate_profile('test_profile')
        
        # Check that the active profile is set
        active_profile = self.config_mgr.get_active_profile()
        self.assertEqual(active_profile, 'test_profile')
        
        # Check that the configuration was updated
        value = self.config_mgr.get('app.name')
        self.assertEqual(value, 'ProfileApp')
        
        # Delete the profile
        self.config_mgr.delete_profile('test_profile')
        
        # Check that the profile was deleted
        profiles = self.config_mgr.get_profiles()
        self.assertNotIn('test_profile', profiles)
        
        # Check that the profile file was deleted
        self.assertFalse(os.path.exists(profile_file))
        
        # Check that the active profile was reset to default
        active_profile = self.config_mgr.get_active_profile()
        self.assertEqual(active_profile, 'default')

    def test_reset_to_default(self):
        """Test resetting configuration to default values."""
        # Set a value
        self.config_mgr.set('app.name', 'TestApp')
        
        # Create a profile
        self.config_mgr.create_profile('test_profile')
        self.config_mgr.update_profile('test_profile', {'app': {'name': 'ProfileApp'}})
        self.config_mgr.activate_profile('test_profile')
        
        # Reset to default
        self.config_mgr.reset_to_default()
        
        # Check that the configuration was reset
        value = self.config_mgr.get('app.name')
        self.assertEqual(value, 'EcoCycle')
        
        # Check that the active profile is default
        active_profile = self.config_mgr.get_active_profile()
        self.assertEqual(active_profile, 'default')
        
        # Check that the profile was deleted
        profiles = self.config_mgr.get_profiles()
        self.assertEqual(profiles, ['default'])

    def test_export_and_import_config(self):
        """Test exporting and importing configuration."""
        # Set a value
        self.config_mgr.set('app.name', 'TestApp')
        
        # Export configuration
        export_file = os.path.join(self.test_dir, 'export.yaml')
        result = self.config_mgr.export_config(export_file)
        
        # Check that the export was successful
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_file))
        
        # Reset configuration
        self.config_mgr.reset_to_default()
        
        # Import configuration
        result = self.config_mgr.import_config(export_file)
        
        # Check that the import was successful
        self.assertTrue(result)
        
        # Check that the value was imported
        value = self.config_mgr.get('app.name')
        self.assertEqual(value, 'TestApp')

    def test_compatibility_functions(self):
        """Test compatibility functions for existing code."""
        # Set a value using set_config
        config_manager.set_config('app.name', 'TestApp')
        
        # Check that the value was set
        value = config_manager.get_config('app.name')
        self.assertEqual(value, 'TestApp')
        
        # Check that the value was set in the configuration manager
        value = self.config_mgr.get('app.name')
        self.assertEqual(value, 'TestApp')


if __name__ == '__main__':
    unittest.main()
