"""
Test module for eco_tips.py
"""
import os
import sys
import unittest

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import apps.eco_tips

class TestEcoTips(unittest.TestCase):
    """Test cases for eco_tips module."""
    
    def test_get_random_tip(self):
        """Test getting a random eco tip."""
        # Get a random tip
        tip = eco_tips.get_random_tip()
        
        # Verify the tip is a string
        self.assertIsInstance(tip, str)
        
        # Verify the tip is not empty
        self.assertTrue(tip)
    
    def test_get_all_tips(self):
        """Test getting all eco tips."""
        # Get all tips
        tips = eco_tips.get_all_tips()
        
        # Verify the tips is a list
        self.assertIsInstance(tips, list)
        
        # Verify the list is not empty
        self.assertTrue(tips)
        
        # Verify each tip is a string
        for tip in tips:
            self.assertIsInstance(tip, str)
            self.assertTrue(tip)

if __name__ == '__main__':
    unittest.main()