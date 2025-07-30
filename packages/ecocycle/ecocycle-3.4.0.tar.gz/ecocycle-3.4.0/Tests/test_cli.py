"""
Test module for cli.py
"""
import os
import sys
import unittest
from unittest import mock
import argparse

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cli

class TestCLI(unittest.TestCase):
    """Test cases for CLI module."""
    
    def test_check_python_version(self):
        """Test Python version checking."""
        is_compatible, current_version, required_version = cli.check_python_version()
        self.assertIsInstance(is_compatible, bool)
        self.assertIsInstance(current_version, tuple)
        self.assertIsInstance(required_version, tuple)
    
    @mock.patch('cli.pkg_resources')
    def test_check_dependencies(self, mock_pkg_resources):
        """Test dependency checker with mocked pkg_resources."""
        # Mock the get_distribution function
        mock_dist = mock.MagicMock()
        mock_dist.version = "1.0.0"
        mock_pkg_resources.get_distribution.return_value = mock_dist
        
        # Test function with all packages available
        result, missing, outdated, installed = cli.check_dependencies()
        
        # Verify result
        self.assertIsInstance(result, bool)
        self.assertIsInstance(missing, list)
        self.assertIsInstance(outdated, list)
        self.assertIsInstance(installed, dict)
    
    def test_check_env_configuration(self):
        """Test environment configuration checker."""
        # Mock environment variables
        with mock.patch.dict(os.environ, {
            'GOOGLE_SHEET_ID': 'test_sheet_id',
            'SERVICE_ACCOUNT_INFO': '{}',
            'API_WEATHER_KEY': 'test_weather_key',
            'API_DISTANCE_KEY': 'test_distance_key'
        }):
            result, missing_required, missing_optional = cli.check_env_configuration()
            self.assertTrue(result)
            self.assertEqual(missing_required, [])
    
    @mock.patch('os.path.isfile')
    def test_check_file_integrity(self, mock_isfile):
        """Test file integrity checker with mocked file system."""
        # Mock os.path.isfile to return True for all files
        mock_isfile.return_value = True
        
        # Test function
        result, missing_files = cli.check_file_integrity()
        
        # Verify result
        self.assertTrue(result)
        self.assertEqual(missing_files, [])
    
    @mock.patch('cli.subprocess.run')
    def test_doctor_command(self, mock_run):
        """Test doctor command with mocked subprocess."""
        # Create mock args
        args = mock.MagicMock()
        
        # Test function
        with mock.patch('builtins.print') as mock_print:
            result = cli.doctor_command(args)
        
        # Verify function called print
        mock_print.assert_called()
        
        # Check return value
        self.assertEqual(result, 0)
    
    @mock.patch('cli.main')
    def test_run_command(self, mock_main):
        """Test run command with mocked main module."""
        # Create mock args
        args = mock.MagicMock()
        args.profile = 'test_user'
        
        # Mock main.main to return 0
        mock_main.main.return_value = 0
        
        # Test function
        result = cli.run_command(args)
        
        # Verify main function was called
        mock_main.main.assert_called_once()
        
        # Check return value
        self.assertEqual(result, 0)
    
    @mock.patch('cli.requests')
    @mock.patch('cli.packaging.version')
    def test_update_command(self, mock_version, mock_requests):
        """Test update command with mocked version and requests."""
        # Create mock args
        args = mock.MagicMock()
        args.install = False
        
        # Mock version.parse to return comparable objects
        class MockVersion:
            def __init__(self, ver):
                self.ver = ver
            def __gt__(self, other):
                return self.ver > other.ver
        
        mock_version.parse.side_effect = lambda v: MockVersion(v)
        
        # Test function
        with mock.patch('builtins.print') as mock_print:
            result = cli.update_command(args)
        
        # Verify function called print
        mock_print.assert_called()
        
        # Check return value
        self.assertEqual(result, 0)
    
    def test_help_command(self):
        """Test help command."""
        # Create mock args
        args = mock.MagicMock()
        
        # Test function
        with mock.patch('builtins.print') as mock_print:
            result = cli.help_command(args)
        
        # Verify function called print
        mock_print.assert_called()
        
        # Check return value
        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()