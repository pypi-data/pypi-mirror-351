#!/usr/bin/env python3
"""
EcoCycle - Enhanced UI Test Script
Test the enhanced ASCII art and animations in isolation.
"""
import os
import sys
import time
import random

try:
    import utils.ascii_art as ascii_art
    ENHANCED_UI = True
    print("Enhanced UI module loaded successfully.")
except ImportError:
    import utils.ascii_art
    ENHANCED_UI = False
    print("Enhanced UI module not available, using standard UI.")

def test_basic_features():
    """Test basic display features. """
    print("\nTesting basic display features...")
    
    # Clear screen and display header
    ascii_art.clear_screen()
    ascii_art.display_header()
    
    # Test section header
    ascii_art.display_section_header("Test Section")
    
    # Test success message
    ascii_art.display_success_message("Operation completed successfully")
    
    # Test warning message
    ascii_art.display_warning_message("This is a warning message")
    
    # Test error message
    ascii_art.display_error_message("This is an error message")
    
    # Test info message
    ascii_art.display_info_message("This is an informational message")
    
    # Test loading message
    ascii_art.display_loading_message("Loading data")
    
    # Test data table
    headers = ["Name", "Value", "Status"]
    data = [
        ["Item 1", "123", "Active"],
        ["Item 2", "456", "Inactive"],
        ["Item 3", "789", "Pending"]
    ]
    ascii_art.display_data_table(headers, data, "Sample Data")
    
    # Test progress bar
    ascii_art.display_progress_bar(75, 100, 40, "Basic Progress")
    
    print("Basic features test complete.")

def test_enhanced_features():
    """Test enhanced animation features (if available)."""
    if not ENHANCED_UI:
        print("\nSkipping enhanced features test (not available).")
        return
    
    print("\nTesting enhanced animation features...")
    
    # Test loading animation
    if hasattr(ascii_art, 'display_loading_animation'):
        print("\nTesting loading animation:")
        ascii_art.display_loading_animation("Processing data", 1.5)
    
    # Test animated menu
    if hasattr(ascii_art, 'display_animated_menu'):
        print("\nTesting animated menu:")
        options = ["Option A", "Option B", "Option C"]
        ascii_art.display_animated_menu("Test Menu", options)
        time.sleep(1)
    
    # Test animated progress bar
    if hasattr(ascii_art, 'display_animated_progress_bar'):
        print("\nTesting animated progress bar:")
        ascii_art.display_animated_progress_bar(60, 100, 40, "Loading Progress", 1.0)
    
    # Test achievement badge
    if hasattr(ascii_art, 'display_achievement_badge'):
        print("\nTesting achievement badge:")
        ascii_art.display_achievement_badge("distance", 2, "Distance Expert")
    
    # Test mascot animation
    if hasattr(ascii_art, 'display_mascot_animation'):
        print("\nTesting mascot animation:")
        ascii_art.display_mascot_animation("Eco-friendly cycling is good for the planet!")
    
    # Test social share graphic
    if hasattr(ascii_art, 'create_social_share_graphic'):
        print("\nTesting social share graphic:")
        ascii_art.create_social_share_graphic(
            "EcoCyclist", 
            "Green Commuter", 
            {
                "Trips": 12,
                "Distance": "120.5 km",
                "CO2 Saved": "30.1 kg",
                "Calories": 3500
            }
        )
    
    # Test route animation
    if hasattr(ascii_art, 'animate_route_on_map'):
        print("\nTesting route animation:")
        ascii_art.animate_route_on_map()
    
    print("Enhanced features test complete.")

def run_tests():
    """Run all UI Tests."""
    print("=== EcoCycle Enhanced UI Test ===")
    print(f"Enhanced UI available: {ENHANCED_UI}")
    
    # Run Tests
    test_basic_features()
    test_enhanced_features()
    
    print("\nAll Tests completed.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_tests()