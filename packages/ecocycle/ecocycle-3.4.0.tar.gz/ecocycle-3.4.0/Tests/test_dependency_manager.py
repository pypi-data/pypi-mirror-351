#!/usr/bin/env python3
"""
Test script for the dependency manager module.
This script tests the functionality of the dependency manager.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
import core.dependency.dependency_manager as dependency_manager


class TestDependencyManager(unittest.TestCase):
    """Test cases for the dependency manager module."""

    def setUp(self):
        """Set up the test environment."""
        # Reset the package cache before each test
        dependency_manager.reset_package_cache()

    def test_is_package_installed(self):
        """Test the is_package_installed function."""
        # Test with a package that should be installed (sys is part of the standard library)
        self.assertTrue(dependency_manager.is_package_installed('sys'))
        
        # Test with a package that should not be installed (a made-up package name)
        self.assertFalse(dependency_manager.is_package_installed('this_package_does_not_exist_12345'))

    @patch('core.dependency.dependency_manager.subprocess.check_call')
    @patch('core.dependency.dependency_manager.is_package_installed')
    def test_ensure_package(self, mock_is_installed, mock_check_call):
        """Test the ensure_package function."""
        # Mock is_package_installed to return False first, then True after installation
        mock_is_installed.side_effect = [False, True]
        
        # Mock subprocess.check_call to simulate successful installation
        mock_check_call.return_value = 0
        
        # Test ensuring a package
        result = dependency_manager.ensure_package('test_package', silent=True)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify that check_call was called with the correct arguments
        mock_check_call.assert_called_once()
        args = mock_check_call.call_args[0][0]
        self.assertEqual(args[-1], 'test_package')

    @patch('core.dependency.dependency_manager.ensure_package')
    def test_ensure_feature(self, mock_ensure_package):
        """Test the ensure_feature function."""
        # Mock ensure_package to return True
        mock_ensure_package.return_value = True
        
        # Add a test feature to FEATURE_DEPENDENCIES
        original_deps = dependency_manager.FEATURE_DEPENDENCIES.copy()
        dependency_manager.FEATURE_DEPENDENCIES['test_feature'] = ['package1', 'package2']
        
        try:
            # Test ensuring a feature
            success, failed = dependency_manager.ensure_feature('test_feature', silent=True)
            
            # Verify the result
            self.assertTrue(success)
            self.assertEqual(failed, [])
            
            # Verify that ensure_package was called for each package
            self.assertEqual(mock_ensure_package.call_count, 2)
        finally:
            # Restore original dependencies
            dependency_manager.FEATURE_DEPENDENCIES = original_deps

    def test_get_feature_for_package(self):
        """Test the get_feature_for_package function."""
        # Add test features to FEATURE_DEPENDENCIES
        original_deps = dependency_manager.FEATURE_DEPENDENCIES.copy()
        dependency_manager.FEATURE_DEPENDENCIES['test_feature1'] = ['package1', 'package2']
        dependency_manager.FEATURE_DEPENDENCIES['test_feature2'] = ['package2', 'package3']
        
        try:
            # Test getting features for a package
            features = dependency_manager.get_feature_for_package('package2')
            
            # Verify the result
            self.assertEqual(set(features), {'test_feature1', 'test_feature2'})
            
            # Test with a package that is not in any feature
            features = dependency_manager.get_feature_for_package('package4')
            self.assertEqual(features, [])
        finally:
            # Restore original dependencies
            dependency_manager.FEATURE_DEPENDENCIES = original_deps

    @patch('core.dependency.dependency_manager.check_system_dependencies')
    @patch('core.dependency.dependency_manager.check_all_dependencies')
    @patch('core.dependency.dependency_manager.ensure_feature')
    def test_run_diagnostics(self, mock_ensure_feature, mock_check_all, mock_check_system):
        """Test the run_diagnostics function."""
        # Mock check_system_dependencies to return some issues
        mock_check_system.return_value = {
            'pip': True,
            'python': True,
            'git': False,
            'internet_connection': True
        }
        
        # Mock check_all_dependencies to return some issues
        mock_check_all.return_value = {
            'test_feature': {
                'available': False,
                'missing': ['package1', 'package2']
            }
        }
        
        # Mock ensure_feature to return success
        mock_ensure_feature.return_value = (True, [])
        
        # Test running diagnostics with fix_issues=True
        results = dependency_manager.run_diagnostics(fix_issues=True)
        
        # Verify the results
        self.assertEqual(results['issues_found'], 3)  # 1 system + 2 packages
        self.assertEqual(results['issues_fixed'], 2)  # Only packages can be fixed
        
        # Verify that ensure_feature was called
        mock_ensure_feature.assert_called_once_with('test_feature', silent=False, max_retries=2)


if __name__ == '__main__':
    unittest.main()
