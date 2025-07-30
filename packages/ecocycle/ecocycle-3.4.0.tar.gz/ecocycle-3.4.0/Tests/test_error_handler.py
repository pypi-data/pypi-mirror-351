#!/usr/bin/env python3
"""
Test script for the error handler module.
This script tests the functionality of the error handler.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
import json
import time

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
import core.error_handler as error_handler


class TestErrorHandler(unittest.TestCase):
    """Test cases for the error handler module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary error log file for testing
        self.test_error_log_file = os.path.join(os.path.dirname(__file__), 'test_error_log.json')
        error_handler.ERROR_LOG_FILE = self.test_error_log_file
        
        # Clear the error log
        if os.path.exists(self.test_error_log_file):
            os.remove(self.test_error_log_file)

    def tearDown(self):
        """Clean up after tests."""
        # Remove the test error log file
        if os.path.exists(self.test_error_log_file):
            os.remove(self.test_error_log_file)

    def test_ecocycle_error(self):
        """Test the EcoCycleError class."""
        # Create an error
        error = error_handler.EcoCycleError(
            message="Test error",
            severity=error_handler.SEVERITY_ERROR,
            category=error_handler.CATEGORY_APPLICATION,
            recovery_strategy=error_handler.STRATEGY_ABORT,
            details={"test_key": "test_value"}
        )
        
        # Check error attributes
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.severity, error_handler.SEVERITY_ERROR)
        self.assertEqual(error.category, error_handler.CATEGORY_APPLICATION)
        self.assertEqual(error.recovery_strategy, error_handler.STRATEGY_ABORT)
        self.assertEqual(error.details, {"test_key": "test_value"})
        
        # Check that the error was logged
        self.assertTrue(os.path.exists(self.test_error_log_file))
        
        # Check the error log content
        with open(self.test_error_log_file, 'r') as f:
            error_log = json.load(f)
        
        self.assertEqual(len(error_log), 1)
        self.assertEqual(error_log[0]['message'], "Test error")
        self.assertEqual(error_log[0]['severity'], error_handler.SEVERITY_ERROR)
        self.assertEqual(error_log[0]['category'], error_handler.CATEGORY_APPLICATION)
        self.assertEqual(error_log[0]['recovery_strategy'], error_handler.STRATEGY_ABORT)
        self.assertEqual(error_log[0]['details'], {"test_key": "test_value"})

    def test_specialized_errors(self):
        """Test the specialized error classes."""
        # Test NetworkError
        network_error = error_handler.NetworkError("Network error")
        self.assertEqual(network_error.category, error_handler.CATEGORY_NETWORK)
        self.assertEqual(network_error.recovery_strategy, error_handler.STRATEGY_RETRY)
        
        # Test DatabaseError
        db_error = error_handler.DatabaseError("Database error")
        self.assertEqual(db_error.category, error_handler.CATEGORY_DATABASE)
        self.assertEqual(db_error.recovery_strategy, error_handler.STRATEGY_FALLBACK)
        
        # Test FileSystemError
        fs_error = error_handler.FileSystemError("File system error")
        self.assertEqual(fs_error.category, error_handler.CATEGORY_FILE_SYSTEM)
        self.assertEqual(fs_error.recovery_strategy, error_handler.STRATEGY_FALLBACK)
        
        # Test UserInputError
        ui_error = error_handler.UserInputError("User input error")
        self.assertEqual(ui_error.category, error_handler.CATEGORY_USER_INPUT)
        self.assertEqual(ui_error.severity, error_handler.SEVERITY_WARNING)
        self.assertEqual(ui_error.recovery_strategy, error_handler.STRATEGY_USER_INTERVENTION)

    def test_handle_error(self):
        """Test the handle_error function."""
        # Create a mock display callback
        mock_display = MagicMock()
        
        # Test with EcoCycleError
        error = error_handler.EcoCycleError("Test error")
        error_handler.handle_error(error, mock_display)
        
        # Check that the display callback was called
        mock_display.assert_called_once_with(f"{error_handler.SEVERITY_ERROR}: Test error")
        
        # Reset the mock
        mock_display.reset_mock()
        
        # Test with standard Exception
        std_error = ValueError("Standard error")
        error_handler.handle_error(std_error, mock_display)
        
        # Check that the display callback was called
        mock_display.assert_called_once_with("ERROR: Standard error")

    def test_retry_decorator(self):
        """Test the retry decorator."""
        # Create a mock function that fails twice then succeeds
        mock_func = MagicMock(side_effect=[ValueError("First failure"), 
                                          ValueError("Second failure"), 
                                          "Success"])
        
        # Create a decorated function
        @error_handler.retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def test_func():
            return mock_func()
        
        # Call the function
        result = test_func()
        
        # Check that the function was called three times
        self.assertEqual(mock_func.call_count, 3)
        
        # Check the result
        self.assertEqual(result, "Success")
        
        # Reset the mock
        mock_func.reset_mock()
        
        # Create a mock function that always fails
        mock_func.side_effect = ValueError("Always fails")
        
        # Create a decorated function with on_failure callback
        on_failure_mock = MagicMock(return_value="Fallback")
        
        @error_handler.retry(max_attempts=2, delay=0.01, exceptions=(ValueError,), 
                           on_failure=on_failure_mock)
        def test_func_fails():
            return mock_func()
        
        # Call the function
        result = test_func_fails()
        
        # Check that the function was called twice
        self.assertEqual(mock_func.call_count, 2)
        
        # Check that on_failure was called
        on_failure_mock.assert_called_once()
        
        # Check the result
        self.assertEqual(result, "Fallback")

    def test_with_fallback_decorator(self):
        """Test the with_fallback decorator."""
        # Create a mock function that fails
        mock_func = MagicMock(side_effect=ValueError("Failure"))
        
        # Create a fallback function
        fallback_mock = MagicMock(return_value="Fallback")
        
        # Create a decorated function
        @error_handler.with_fallback(fallback_mock)
        def test_func():
            return mock_func()
        
        # Call the function
        result = test_func()
        
        # Check that the function was called
        mock_func.assert_called_once()
        
        # Check that fallback was called
        fallback_mock.assert_called_once()
        
        # Check the result
        self.assertEqual(result, "Fallback")

    def test_error_log_functions(self):
        """Test the error log functions."""
        # Create some errors to populate the log
        error_handler.EcoCycleError("Error 1")
        error_handler.EcoCycleError("Error 2")
        
        # Get the error log
        error_log = error_handler.get_error_log()
        
        # Check the error log
        self.assertEqual(len(error_log), 2)
        self.assertEqual(error_log[0]['message'], "Error 1")
        self.assertEqual(error_log[1]['message'], "Error 2")
        
        # Clear the error log
        error_handler.clear_error_log()
        
        # Check that the error log is empty
        self.assertFalse(os.path.exists(self.test_error_log_file))
        
        # Get the error log again
        error_log = error_handler.get_error_log()
        
        # Check that the error log is empty
        self.assertEqual(error_log, [])


if __name__ == '__main__':
    unittest.main()
