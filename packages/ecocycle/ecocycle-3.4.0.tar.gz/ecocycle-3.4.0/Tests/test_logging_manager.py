#!/usr/bin/env python3
"""
Test script for the logging manager module.
This script tests the functionality of the logging manager.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
import time
import logging

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
import core.logging_manager as logging_manager


class TestLoggingManager(unittest.TestCase):
    """Test cases for the logging manager module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test directory for logs
        self.test_log_dir = os.path.join(os.path.dirname(__file__), 'test_logs')
        os.makedirs(self.test_log_dir, exist_ok=True)
        
        # Set up test log files
        self.test_app_log = os.path.join(self.test_log_dir, 'test_app.log')
        self.test_debug_log = os.path.join(self.test_log_dir, 'test_debug.log')
        self.test_error_log = os.path.join(self.test_log_dir, 'test_error.log')
        self.test_performance_log = os.path.join(self.test_log_dir, 'test_performance.log')
        self.test_audit_log = os.path.join(self.test_log_dir, 'test_audit.log')
        self.test_metrics_file = os.path.join(self.test_log_dir, 'test_metrics.json')
        
        # Override log file paths
        logging_manager.APP_LOG_FILE = self.test_app_log
        logging_manager.DEBUG_LOG_FILE = self.test_debug_log
        logging_manager.ERROR_LOG_FILE = self.test_error_log
        logging_manager.PERFORMANCE_LOG_FILE = self.test_performance_log
        logging_manager.AUDIT_LOG_FILE = self.test_audit_log
        logging_manager.METRICS_FILE = self.test_metrics_file
        
        # Set up test loggers
        self.test_app_logger = logging_manager.setup_logger(
            'test_app', self.test_app_log, logging.INFO)
        self.test_debug_logger = logging_manager.setup_logger(
            'test_debug', self.test_debug_log, logging.DEBUG)
        self.test_error_logger = logging_manager.setup_logger(
            'test_error', self.test_error_log, logging.ERROR)
        self.test_performance_logger = logging_manager.setup_logger(
            'test_performance', self.test_performance_log, logging.INFO)
        self.test_audit_logger = logging_manager.setup_logger(
            'test_audit', self.test_audit_log, logging.INFO)
        
        # Override loggers
        logging_manager.app_logger = self.test_app_logger
        logging_manager.debug_logger = self.test_debug_logger
        logging_manager.error_logger = self.test_error_logger
        logging_manager.performance_logger = self.test_performance_logger
        logging_manager.audit_logger = self.test_audit_logger
        
        # Clear metrics
        logging_manager.clear_metrics()

    def tearDown(self):
        """Clean up after tests."""
        # Remove test log files
        for log_file in [self.test_app_log, self.test_debug_log, self.test_error_log,
                        self.test_performance_log, self.test_audit_log, self.test_metrics_file]:
            if os.path.exists(log_file):
                os.remove(log_file)
        
        # Remove test log directory
        if os.path.exists(self.test_log_dir):
            os.rmdir(self.test_log_dir)

    def test_log_debug(self):
        """Test the log_debug function."""
        # Log a debug message
        logging_manager.log_debug("Test debug message", "test_module")
        
        # Check that the message was logged
        self.assertTrue(os.path.exists(self.test_debug_log))
        
        # Check the log content
        with open(self.test_debug_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] Test debug message", log_content)

    def test_log_info(self):
        """Test the log_info function."""
        # Log an info message
        logging_manager.log_info("Test info message", "test_module")
        
        # Check that the message was logged
        self.assertTrue(os.path.exists(self.test_app_log))
        
        # Check the log content
        with open(self.test_app_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] Test info message", log_content)

    def test_log_warning(self):
        """Test the log_warning function."""
        # Log a warning message
        logging_manager.log_warning("Test warning message", "test_module")
        
        # Check that the message was logged
        self.assertTrue(os.path.exists(self.test_app_log))
        
        # Check the log content
        with open(self.test_app_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] Test warning message", log_content)

    def test_log_error(self):
        """Test the log_error function."""
        # Log an error message
        logging_manager.log_error("Test error message", "test_module")
        
        # Check that the message was logged to both error and app logs
        self.assertTrue(os.path.exists(self.test_error_log))
        self.assertTrue(os.path.exists(self.test_app_log))
        
        # Check the error log content
        with open(self.test_error_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] Test error message", log_content)
        
        # Check the app log content
        with open(self.test_app_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] Test error message", log_content)

    def test_log_critical(self):
        """Test the log_critical function."""
        # Log a critical message
        logging_manager.log_critical("Test critical message", "test_module")
        
        # Check that the message was logged to both error and app logs
        self.assertTrue(os.path.exists(self.test_error_log))
        self.assertTrue(os.path.exists(self.test_app_log))
        
        # Check the error log content
        with open(self.test_error_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] Test critical message", log_content)
        
        # Check the app log content
        with open(self.test_app_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] Test critical message", log_content)

    def test_log_audit(self):
        """Test the log_audit function."""
        # Log an audit event
        logging_manager.log_audit(
            action="test_action",
            user="test_user",
            resource="test_resource",
            result="success",
            details={"key": "value"}
        )
        
        # Check that the message was logged
        self.assertTrue(os.path.exists(self.test_audit_log))
        
        # Check the audit log content
        with open(self.test_audit_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("USER:test_user", log_content)
        self.assertIn("ACTION:test_action", log_content)
        self.assertIn("RESOURCE:test_resource", log_content)
        self.assertIn("RESULT:success", log_content)
        
        # Check that details were logged to debug log
        with open(self.test_debug_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("AUDIT DETAILS", log_content)
        self.assertIn("ACTION:test_action", log_content)
        self.assertIn("USER:test_user", log_content)
        self.assertIn('{"key": "value"}', log_content)

    def test_log_performance(self):
        """Test the log_performance function."""
        # Log a performance metric
        logging_manager.log_performance(
            operation="test_operation",
            duration=0.5,
            module="test_module",
            details={"key": "value"}
        )
        
        # Check that the message was logged
        self.assertTrue(os.path.exists(self.test_performance_log))
        
        # Check the performance log content
        with open(self.test_performance_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("[test_module] test_operation - 0.500000s", log_content)
        
        # Check that metrics were updated
        metrics = logging_manager.get_metrics()
        self.assertIn("test_operation", metrics)
        self.assertEqual(metrics["test_operation"]["count"], 1)
        self.assertEqual(metrics["test_operation"]["total_duration"], 0.5)
        self.assertEqual(metrics["test_operation"]["min_duration"], 0.5)
        self.assertEqual(metrics["test_operation"]["max_duration"], 0.5)
        self.assertEqual(metrics["test_operation"]["module"], "test_module")

    def test_time_function_decorator(self):
        """Test the time_function decorator."""
        # Create a test function with the decorator
        @logging_manager.time_function
        def test_function():
            time.sleep(0.1)
            return "test_result"
        
        # Call the function
        result = test_function()
        
        # Check the result
        self.assertEqual(result, "test_result")
        
        # Check that performance was logged
        self.assertTrue(os.path.exists(self.test_performance_log))
        
        # Check the performance log content
        with open(self.test_performance_log, 'r') as f:
            log_content = f.read()
        
        self.assertIn("test_function", log_content)
        
        # Check that metrics were updated
        metrics = logging_manager.get_metrics()
        self.assertIn("test_function", metrics)
        self.assertEqual(metrics["test_function"]["count"], 1)
        self.assertGreaterEqual(metrics["test_function"]["total_duration"], 0.1)

    def test_save_and_get_metrics(self):
        """Test the save_metrics and get_metrics functions."""
        # Log some performance metrics
        logging_manager.log_performance("op1", 0.1, "module1")
        logging_manager.log_performance("op1", 0.2, "module1")
        logging_manager.log_performance("op2", 0.3, "module2")
        
        # Save metrics
        logging_manager.save_metrics()
        
        # Check that metrics file was created
        self.assertTrue(os.path.exists(self.test_metrics_file))
        
        # Check the metrics file content
        with open(self.test_metrics_file, 'r') as f:
            metrics_data = json.load(f)
        
        self.assertIn("system_info", metrics_data)
        self.assertIn("metrics", metrics_data)
        self.assertIn("op1", metrics_data["metrics"])
        self.assertIn("op2", metrics_data["metrics"])
        
        # Get metrics
        metrics = logging_manager.get_metrics()
        
        # Check metrics
        self.assertIn("op1", metrics)
        self.assertEqual(metrics["op1"]["count"], 2)
        self.assertEqual(metrics["op1"]["total_duration"], 0.3)
        self.assertEqual(metrics["op1"]["min_duration"], 0.1)
        self.assertEqual(metrics["op1"]["max_duration"], 0.2)
        self.assertEqual(metrics["op1"]["module"], "module1")
        self.assertAlmostEqual(metrics["op1"]["avg_duration"], 0.15)
        
        self.assertIn("op2", metrics)
        self.assertEqual(metrics["op2"]["count"], 1)
        self.assertEqual(metrics["op2"]["total_duration"], 0.3)
        self.assertEqual(metrics["op2"]["min_duration"], 0.3)
        self.assertEqual(metrics["op2"]["max_duration"], 0.3)
        self.assertEqual(metrics["op2"]["module"], "module2")
        self.assertAlmostEqual(metrics["op2"]["avg_duration"], 0.3)

    def test_clear_metrics(self):
        """Test the clear_metrics function."""
        # Log some performance metrics
        logging_manager.log_performance("op1", 0.1, "module1")
        
        # Check that metrics were updated
        metrics = logging_manager.get_metrics()
        self.assertIn("op1", metrics)
        
        # Clear metrics
        logging_manager.clear_metrics()
        
        # Check that metrics were cleared
        metrics = logging_manager.get_metrics()
        self.assertEqual(metrics, {})
        
        # Check that metrics file was updated
        self.assertTrue(os.path.exists(self.test_metrics_file))
        
        # Check the metrics file content
        with open(self.test_metrics_file, 'r') as f:
            metrics_data = json.load(f)
        
        self.assertIn("system_info", metrics_data)
        self.assertIn("metrics", metrics_data)
        self.assertEqual(metrics_data["metrics"], {})

    def test_get_log_files(self):
        """Test the get_log_files function."""
        # Get log files
        log_files = logging_manager.get_log_files()
        
        # Check log files
        self.assertEqual(log_files["app"], self.test_app_log)
        self.assertEqual(log_files["debug"], self.test_debug_log)
        self.assertEqual(log_files["error"], self.test_error_log)
        self.assertEqual(log_files["performance"], self.test_performance_log)
        self.assertEqual(log_files["audit"], self.test_audit_log)
        self.assertEqual(log_files["metrics"], self.test_metrics_file)

    def test_get_log_contents(self):
        """Test the get_log_contents function."""
        # Log some messages
        logging_manager.log_info("Test info 1")
        logging_manager.log_info("Test info 2")
        
        # Get log contents
        log_contents = logging_manager.get_log_contents("app")
        
        # Check log contents
        self.assertEqual(len(log_contents), 2)
        self.assertIn("Test info 1", log_contents[0])
        self.assertIn("Test info 2", log_contents[1])
        
        # Test with invalid log type
        log_contents = logging_manager.get_log_contents("invalid")
        self.assertEqual(len(log_contents), 1)
        self.assertIn("Invalid log type", log_contents[0])


if __name__ == '__main__':
    unittest.main()
