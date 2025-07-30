#!/usr/bin/env python3
"""
Test script to verify the goodbye message format
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_goodbye_message():
    """Test the goodbye message format"""
    print("Testing goodbye message format...")
    
    # Simulate the goodbye message
    print("\nThank you for using EcoCycle! Goodbye.")
    print("With ♡ - the EcoCycle team.")
    
    print("\nThis is how the goodbye message will appear when users press Ctrl+C")

if __name__ == "__main__":
    test_goodbye_message()
