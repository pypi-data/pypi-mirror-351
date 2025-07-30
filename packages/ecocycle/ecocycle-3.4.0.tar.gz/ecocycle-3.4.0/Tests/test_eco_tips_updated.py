"""
Test module for eco_tips.py (updated version)
"""
import os
import sys
import unittest
import datetime
from unittest import mock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import apps.eco_tips

class TestEcoTips(unittest.TestCase):
    """Test cases for eco_tips module."""
    
    def test_get_random_tip(self):
        """Test getting a random eco tip."""
        # Get a random tip
        tip = eco_tips.get_random_tip()
        
        # Verify the tip is a dictionary
        self.assertIsInstance(tip, dict)
        
        # Verify the tip has the expected keys
        self.assertIn('tip', tip)
        self.assertIn('category', tip)
        self.assertIn('impact', tip)
        
        # Verify the tip content is not empty
        self.assertTrue(tip['tip'])
        self.assertTrue(tip['category'])
        self.assertTrue(tip['impact'])
    
    def test_get_all_tips(self):
        """Test getting all eco tips."""
        # Get all tips
        tips = eco_tips.get_all_tips()
        
        # Verify the tips is a list
        self.assertIsInstance(tips, list)
        
        # Verify the list is not empty
        self.assertTrue(tips)
        
        # Verify each tip has the expected structure
        for tip in tips:
            self.assertIsInstance(tip, dict)
            self.assertIn('tip', tip)
            self.assertIn('category', tip)
            self.assertIn('impact', tip)
    
    def test_get_tips_by_category(self):
        """Test getting tips by category."""
        # Get tips for a specific category
        health_tips = eco_tips.get_tips_by_category('health')
        
        # Verify the result is a list
        self.assertIsInstance(health_tips, list)
        
        # Verify each tip in the result has the 'health' category
        for tip in health_tips:
            categories = [cat.lower() for cat in tip['category']]
            self.assertIn('health', categories)
    
    def test_get_high_impact_tips(self):
        """Test getting high impact tips."""
        # Get high impact tips
        high_impact_tips = eco_tips.get_high_impact_tips()
        
        # Verify the result is a list
        self.assertIsInstance(high_impact_tips, list)
        
        # Verify each tip in the result has 'high' impact
        for tip in high_impact_tips:
            self.assertEqual(tip['impact'], 'high')
    
    def test_get_daily_tip(self):
        """Test getting the daily tip."""
        # Get the daily tip
        daily_tip = eco_tips.get_daily_tip()
        
        # Verify the result is a string
        self.assertIsInstance(daily_tip, str)
        
        # Verify the result is not empty
        self.assertTrue(daily_tip)
        
        # Verify the result contains the day of the week
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_of_week = datetime.datetime.now().weekday()
        self.assertIn(day_names[day_of_week], daily_tip)
    
    def test_get_tip_of_the_day(self):
        """Test getting the tip of the day."""
        # Get the tip of the day
        tip_of_the_day = eco_tips.get_tip_of_the_day()
        
        # Verify the result is a dictionary
        self.assertIsInstance(tip_of_the_day, dict)
        
        # Verify the tip has the expected keys
        self.assertIn('tip', tip_of_the_day)
        self.assertIn('category', tip_of_the_day)
        self.assertIn('impact', tip_of_the_day)
        
        # Get the tip again and verify it's the same (consistent for the day)
        second_tip = eco_tips.get_tip_of_the_day()
        self.assertEqual(tip_of_the_day, second_tip)

if __name__ == '__main__':
    unittest.main()