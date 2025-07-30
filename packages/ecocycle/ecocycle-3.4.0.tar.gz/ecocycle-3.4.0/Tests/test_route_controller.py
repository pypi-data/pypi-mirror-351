import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('..'))

# Try to import the RouteController class
try:
    from controllers.route_controller import RouteController
    print("Successfully imported RouteController")
    
    # Create an instance of RouteController
    controller = RouteController()
    print("Successfully created RouteController instance")
    
    print("Test passed: The syntax error has been fixed")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
    print("Test failed: The syntax error still exists")
except Exception as e:
    print(f"Other error: {e}")
    print("Test failed due to an unexpected error")