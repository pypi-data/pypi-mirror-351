#!/usr/bin/env python3
"""
Test script to verify KeyboardInterrupt handling in EcoCycle
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_safe_input():
    """Test the safe input functions"""
    print("Testing KeyboardInterrupt handling...")
    print("Press Ctrl+C to test the interrupt handling")
    
    try:
        from utils.safe_input import safe_input, safe_menu_choice, safe_confirmation
        
        print("\n1. Testing safe_input:")
        result = safe_input("Enter some text (or press Ctrl+C): ")
        print(f"Result: {result}")
        
        print("\n2. Testing safe_menu_choice:")
        result = safe_menu_choice("Choose an option", ["1", "2", "3"], "1")
        print(f"Result: {result}")
        
        print("\n3. Testing safe_confirmation:")
        result = safe_confirmation("Do you want to continue?", True)
        print(f"Result: {result}")
        
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught at top level - this should not happen with safe functions")
    except Exception as e:
        print(f"Error: {e}")


def test_main_app_interrupt():
    """Test KeyboardInterrupt handling in main app"""
    print("\n" + "="*50)
    print("Testing main application KeyboardInterrupt handling")
    print("This will start the main app - press Ctrl+C to test")
    print("="*50)
    
    try:
        import main
        main.main()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught at test level - main app should handle this")
    except Exception as e:
        print(f"Error in main app: {e}")


if __name__ == "__main__":
    print("EcoCycle KeyboardInterrupt Handling Test")
    print("="*50)
    
    choice = input("Test (1) Safe input functions or (2) Main app? [1/2]: ").strip()
    
    if choice == "1":
        test_safe_input()
    elif choice == "2":
        test_main_app_interrupt()
    else:
        print("Invalid choice")
        
    print("\nTest completed.")
