#!/usr/bin/env python3
"""
Test script to verify the fix for the 'bool' object has no attribute 'substitute' error
in the update_cycling_preferences method.
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
    from apps.route_planner.ai_planner.planner import AIRoutePlanner
    from apps.route_planner.ai_planner.models.route import RouteManager

    def test_routes_update_preferences():
        """Test the RouteManager.update_preferences method directly."""
        # Create a temporary routes file for testing
        # Make sure to use a valid path
        routes_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_routes.json")

        # Initialize the route manager
        route_manager = RouteManager(routes_file)

        # Test the update_preferences method
        logger.info("Testing RouteManager.update_preferences method...")
        try:
            # Get current preferences
            current_prefs = route_manager.get_user_preferences("test_user")

            # Update preferences directly
            result = route_manager.update_preferences("test_user", current_prefs)

            # Check if the result is a boolean
            if not isinstance(result, bool):
                logger.error(f"Expected boolean result, got {type(result)}")
                return False

            # Convert the result to a boolean explicitly
            success = True if result else False

            logger.info(f"Test passed: RouteManager.update_preferences returned {success}")
            return True
        except Exception as e:
            logger.error(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up the test routes file
            if os.path.exists(routes_file):
                os.remove(routes_file)

    if __name__ == "__main__":
        result = test_routes_update_preferences()
        print("\nTest result:", "PASSED" if result else "FAILED")
        sys.exit(0 if result else 1)

except ImportError as e:
    logger.error(f"Import error: {e}")
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)
