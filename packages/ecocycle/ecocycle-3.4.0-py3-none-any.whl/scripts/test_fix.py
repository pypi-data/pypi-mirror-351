#!/usr/bin/env python3
"""
Test script to verify the fix for the 'bool' object has no attribute 'substitute' error
in the GeminiAPI.generate_alternative_routes method.
"""
import logging
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Make sure the module path is available
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the fixed modules
    from apps.route_planner.ai_planner.api.gemini_api import GeminiAPI
    from apps.route_planner.ai_planner.ui.cli import RoutePlannerCLI

    def test_alternative_routes():
        """Test the generate_alternative_routes method with API unavailable scenario."""
        api = GeminiAPI()

        # Force the API to be unavailable for testing error handling
        api.gemini_available = False
        api.gemini_error = "Test error - API unavailable"

        # Test parameters
        location = "Test Location"
        preferences = {"preferred_distance": 10, "preferred_difficulty": "intermediate"}
        priority_types = ["scenic", "quick", "safe"]

        # Call the method that previously had the error
        logger.info("Testing generate_alternative_routes with API unavailable...")
        success, result = api.generate_alternative_routes(location, preferences, priority_types)

        # Verify the result
        if not success:
            if isinstance(result, dict) and "error" in result:
                logger.info("Test passed: Error handled correctly with a proper error dictionary")
                logger.info(f"Error message: {result['error']}")
                return True
            else:
                logger.error(f"Test failed: Error not handled correctly. Result: {result}")
                return False
        else:
            logger.error("Test failed: Expected error but got success")
            return False

    def test_cli_display_message():
        """Test the CLI display_message method with boolean values."""
        cli = RoutePlannerCLI()

        # Test with boolean value
        logger.info("Testing CLI display_message with boolean value...")
        try:
            # This would previously cause the error: 'bool' object has no attribute 'substitute'
            cli.display_message(False, "Boolean Test", "info")
            logger.info("Test passed: CLI display_message handled boolean value correctly")
            return True
        except Exception as e:
            logger.error(f"Test failed: CLI display_message error: {e}")
            return False

    if __name__ == "__main__":
        print("\n=== Testing API Error Handling ===")
        api_result = test_alternative_routes()

        print("\n=== Testing CLI Boolean Handling ===")
        cli_result = test_cli_display_message()

        overall_result = api_result and cli_result
        print("\nOverall test result:", "PASSED" if overall_result else "FAILED")
        sys.exit(0 if overall_result else 1)

except ImportError as e:
    logger.error(f"Import error: {e}")
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)
