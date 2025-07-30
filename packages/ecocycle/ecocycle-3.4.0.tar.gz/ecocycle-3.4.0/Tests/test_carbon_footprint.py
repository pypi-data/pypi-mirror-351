"""
Test module for carbon_footprint.py
"""
import os
import sys
import unittest
from unittest import mock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import apps.carbon_footprint

class TestCarbonFootprint(unittest.TestCase):
    """Test cases for carbon_footprint module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a CarbonFootprint instance for testing
        self.carbon_footprint = carbon_footprint.CarbonFootprint()
        
        # Sample user footprint data for testing
        self.sample_footprint = {
            'commute_mode': '1',  # Car
            'commute_distance': 15.0,
            'flights_per_year': 4,
            'avg_flight_distance': 2500.0,
            'car_km_per_week': 100.0,
            'beef_meals': 3,
            'chicken_meals': 5,
            'vegetarian_meals': 7,
            'vegan_meals': 6,
            'food_waste_percent': 15,
            'heating_months': 5,
            'ac_months': 3,
            'shower_minutes': 10.0,
            'showers_per_week': 7,
            'laundry_loads': 3,
            'dishwasher_cycles': 4,
            'computer_hours': 8.0,
            'tv_hours': 2.0
        }
        
        # Set the sample footprint data
        self.carbon_footprint.user_footprint = self.sample_footprint
    
    def test_initialization(self):
        """Test initialization of CarbonFootprint class."""
        # Verify the instance is created correctly
        self.assertIsInstance(self.carbon_footprint, carbon_footprint.CarbonFootprint)
        
        # Verify the emissions constants are set
        self.assertEqual(self.carbon_footprint.car_emissions_per_km, 0.192)
        self.assertEqual(self.carbon_footprint.bus_emissions_per_km, 0.105)
        self.assertEqual(self.carbon_footprint.train_emissions_per_km, 0.041)
        self.assertEqual(self.carbon_footprint.plane_emissions_per_km, 0.255)
        
        # Verify the emissions data dictionary is populated
        self.assertIn('beef_meal', self.carbon_footprint.emissions_data)
        self.assertIn('vegetarian_meal', self.carbon_footprint.emissions_data)
        self.assertIn('hot_shower', self.carbon_footprint.emissions_data)
    
    def test_calculate_transportation_emissions(self):
        """Test calculation of transportation emissions."""
        # Calculate transportation emissions
        transport_emissions = self.carbon_footprint._calculate_transportation_emissions()
        
        # Expected calculations:
        # Commute: 15 km * 0.192 kg/km * 250 days = 720 kg
        # Flights: 4 flights * 2500 km * 0.255 kg/km = 2550 kg
        # Other car: 100 km/week * 0.192 kg/km * 52 weeks = 998.4 kg
        # Total: 720 + 2550 + 998.4 = 4268.4 kg
        expected_emissions = 720 + 2550 + 998.4
        
        # Verify the result is close to the expected value (allowing for floating point precision)
        self.assertAlmostEqual(transport_emissions, expected_emissions, places=1)
    
    def test_calculate_food_emissions(self):
        """Test calculation of food emissions."""
        # Calculate food emissions
        food_emissions = self.carbon_footprint._calculate_food_emissions()
        
        # Expected calculations:
        # Weekly emissions: 
        # (3 * 6.6) + (5 * 1.8) + (7 * 0.5) + (6 * 0.3) = 19.8 + 9 + 3.5 + 1.8 = 34.1 kg
        # Annual: 34.1 * 52 = 1773.2 kg
        # With food waste (15%): 1773.2 * 1.15 = 2039.18 kg
        expected_emissions = ((3 * 6.6) + (5 * 1.8) + (7 * 0.5) + (6 * 0.3)) * 52 * 1.15
        
        # Verify the result is close to the expected value
        self.assertAlmostEqual(food_emissions, expected_emissions, places=1)
    
    def test_calculate_home_emissions(self):
        """Test calculation of home emissions."""
        # Calculate home emissions
        home_emissions = self.carbon_footprint._calculate_home_emissions()
        
        # Expected calculations (simplified for testing):
        # Heating: 5 months * 30 days * 7.5 kg = 1125 kg
        # AC: 3 months * 30 days * 10.5 kg = 945 kg
        # Shower: (10/10) * 2.5 kg * 7 showers/week * 52 weeks = 910 kg
        # Laundry: 3 loads/week * 0.6 kg * 52 weeks = 93.6 kg
        # Dishwasher: 4 cycles/week * 0.4 kg * 52 weeks = 83.2 kg
        # Computer: 8 hours/day * 0.1 kg * 365 days = 292 kg
        # TV: 2 hours/day * 0.08 kg * 365 days = 58.4 kg
        # Total: 1125 + 945 + 910 + 93.6 + 83.2 + 292 + 58.4 = 3507.2 kg
        expected_emissions = 1125 + 945 + 910 + 93.6 + 83.2 + 292 + 58.4
        
        # Verify the result is close to the expected value
        self.assertAlmostEqual(home_emissions, expected_emissions, places=1)
    
    def test_calculate_total_footprint(self):
        """Test calculation of total carbon footprint."""
        # Calculate total footprint
        total_footprint = self.carbon_footprint._calculate_total_footprint()
        
        # Verify the result is a dictionary with the expected keys
        self.assertIsInstance(total_footprint, dict)
        self.assertIn('transportation', total_footprint)
        self.assertIn('food', total_footprint)
        self.assertIn('home', total_footprint)
        self.assertIn('total', total_footprint)
        
        # Verify the total is the sum of the individual categories
        self.assertEqual(
            total_footprint['total'],
            total_footprint['transportation'] + total_footprint['food'] + total_footprint['home']
        )
    
    @mock.patch('carbon_footprint.input', return_value='')
    def test_collect_transportation_data_with_defaults(self, mock_input):
        """Test collecting transportation data with default values."""
        # Reset user_footprint
        self.carbon_footprint.user_footprint = {}
        
        # Call the method
        self.carbon_footprint._collect_transportation_data()
        
        # Verify default values are set
        self.assertEqual(self.carbon_footprint.user_footprint['commute_mode'], '1')
        self.assertEqual(self.carbon_footprint.user_footprint['commute_distance'], 10)
        self.assertEqual(self.carbon_footprint.user_footprint['flights_per_year'], 2)
        self.assertEqual(self.carbon_footprint.user_footprint['avg_flight_distance'], 2000)
        self.assertEqual(self.carbon_footprint.user_footprint['car_km_per_week'], 50)
    
    @mock.patch('carbon_footprint.input', side_effect=['2', '20', '5', '3000', '75'])
    def test_collect_transportation_data_with_input(self, mock_input):
        """Test collecting transportation data with user input."""
        # Reset user_footprint
        self.carbon_footprint.user_footprint = {}
        
        # Call the method
        self.carbon_footprint._collect_transportation_data()
        
        # Verify input values are set
        self.assertEqual(self.carbon_footprint.user_footprint['commute_mode'], '2')
        self.assertEqual(self.carbon_footprint.user_footprint['commute_distance'], 20)
        self.assertEqual(self.carbon_footprint.user_footprint['flights_per_year'], 5)
        self.assertEqual(self.carbon_footprint.user_footprint['avg_flight_distance'], 3000)
        self.assertEqual(self.carbon_footprint.user_footprint['car_km_per_week'], 75)
    
    @mock.patch('carbon_footprint.input', return_value='invalid')
    def test_collect_transportation_data_with_invalid_input(self, mock_input):
        """Test collecting transportation data with invalid input."""
        # Reset user_footprint
        self.carbon_footprint.user_footprint = {}
        
        # Call the method
        self.carbon_footprint._collect_transportation_data()
        
        # Verify default values are set when input is invalid
        self.assertEqual(self.carbon_footprint.user_footprint['commute_mode'], '1')
        self.assertEqual(self.carbon_footprint.user_footprint['commute_distance'], 10)
        self.assertEqual(self.carbon_footprint.user_footprint['flights_per_year'], 2)
        self.assertEqual(self.carbon_footprint.user_footprint['avg_flight_distance'], 2000)
        self.assertEqual(self.carbon_footprint.user_footprint['car_km_per_week'], 50)
    
    def test_different_commute_modes(self):
        """Test calculation with different commute modes."""
        # Test car mode (mode 1)
        self.carbon_footprint.user_footprint['commute_mode'] = '1'
        car_emissions = self.carbon_footprint._calculate_transportation_emissions()
        
        # Test bus mode (mode 2)
        self.carbon_footprint.user_footprint['commute_mode'] = '2'
        bus_emissions = self.carbon_footprint._calculate_transportation_emissions()
        
        # Test train mode (mode 3)
        self.carbon_footprint.user_footprint['commute_mode'] = '3'
        train_emissions = self.carbon_footprint._calculate_transportation_emissions()
        
        # Test bicycle/walking mode (mode 4)
        self.carbon_footprint.user_footprint['commute_mode'] = '4'
        bike_emissions = self.carbon_footprint._calculate_transportation_emissions()
        
        # Verify car emissions are highest, followed by bus, train, and bicycle/walking
        self.assertGreater(car_emissions, bus_emissions)
        self.assertGreater(bus_emissions, train_emissions)
        self.assertGreater(train_emissions, bike_emissions)
        
        # Bicycle/walking should have zero commute emissions
        # Calculate expected non-commute emissions
        flights_emissions = 4 * 2500 * 0.255
        other_car_emissions = 100 * 0.192 * 52
        expected_bike_emissions = flights_emissions + other_car_emissions
        
        # Verify bicycle/walking emissions match expected non-commute emissions
        self.assertAlmostEqual(bike_emissions, expected_bike_emissions, places=1)

if __name__ == '__main__':
    unittest.main()