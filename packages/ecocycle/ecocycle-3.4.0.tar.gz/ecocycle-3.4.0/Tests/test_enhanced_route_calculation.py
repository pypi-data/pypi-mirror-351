#!/usr/bin/env python3
"""
Test script for enhanced route calculation in the log cycling trip feature.
This script tests the accuracy and functionality of the improved bicycle routing system.
"""

import os
import sys
import logging
from typing import Dict, Any, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_coordinate_validation():
    """Test coordinate validation functionality."""
    print("\n=== Testing Coordinate Validation ===")
    
    try:
        from controllers.route_controller import RouteController
        controller = RouteController()
        
        # Test valid coordinates
        valid_coords = [(40.7128, -74.0060), (34.0522, -118.2437)]  # NYC to LA
        assert controller._validate_coordinate_ranges(*valid_coords), "Valid coordinates should pass validation"
        print("✓ Valid coordinates passed validation")
        
        # Test invalid latitude
        invalid_lat = [(91.0, -74.0060), (34.0522, -118.2437)]
        assert not controller._validate_coordinate_ranges(*invalid_lat), "Invalid latitude should fail validation"
        print("✓ Invalid latitude correctly rejected")
        
        # Test invalid longitude
        invalid_lon = [(40.7128, -181.0), (34.0522, -118.2437)]
        assert not controller._validate_coordinate_ranges(*invalid_lon), "Invalid longitude should fail validation"
        print("✓ Invalid longitude correctly rejected")
        
        print("✅ Coordinate validation tests passed!")
        
    except Exception as e:
        print(f"❌ Coordinate validation test failed: {e}")
        return False
    
    return True

def test_enhanced_route_calculation():
    """Test enhanced route calculation with cycling preferences."""
    print("\n=== Testing Enhanced Route Calculation ===")
    
    try:
        from controllers.route_controller import RouteController
        controller = RouteController()
        
        # Test coordinates (New York to Brooklyn)
        start_coords = (40.7128, -74.0060)  # Manhattan
        end_coords = (40.6782, -73.9442)    # Brooklyn
        
        # Test with cycling preferences
        cycling_preferences = {
            "avoid_highways": True,
            "prefer_bike_lanes": True,
            "avoid_steep_hills": False,
            "surface_preference": "paved"
        }
        
        print(f"Calculating route from {start_coords} to {end_coords}")
        route_info = controller.get_route_info(start_coords, end_coords, cycling_preferences)
        
        # Validate route info structure
        required_fields = ['distance', 'duration', 'elevation', 'route_quality', 'source']
        for field in required_fields:
            assert field in route_info, f"Route info missing required field: {field}"
        
        print(f"✓ Route calculated successfully:")
        print(f"  - Distance: {route_info['distance']:.2f} km")
        print(f"  - Duration: {route_info['duration']:.1f} minutes")
        print(f"  - Quality: {route_info['route_quality']}")
        print(f"  - Source: {route_info['source']}")
        
        # Test that distance is reasonable (should be > 0 and < 1000 km for local routes)
        assert 0 < route_info['distance'] < 1000, f"Distance seems unreasonable: {route_info['distance']} km"
        print("✓ Distance is within reasonable range")
        
        # Test that duration is reasonable (should be > 0)
        assert route_info['duration'] > 0, f"Duration should be positive: {route_info['duration']}"
        print("✓ Duration is positive")
        
        # Test route quality assessment
        valid_qualities = ['excellent', 'good', 'fair', 'poor', 'error']
        assert route_info['route_quality'] in valid_qualities, f"Invalid route quality: {route_info['route_quality']}"
        print("✓ Route quality assessment is valid")
        
        print("✅ Enhanced route calculation tests passed!")
        
    except Exception as e:
        print(f"❌ Enhanced route calculation test failed: {e}")
        logger.error(f"Route calculation test error: {e}", exc_info=True)
        return False
    
    return True

def test_fallback_calculation():
    """Test fallback route calculation when APIs are not available."""
    print("\n=== Testing Fallback Route Calculation ===")
    
    try:
        from controllers.route_controller import RouteController
        controller = RouteController()
        
        # Test coordinates
        start_coords = (40.7128, -74.0060)  # Manhattan
        end_coords = (40.6782, -73.9442)    # Brooklyn
        
        # Test enhanced fallback calculation directly
        preferences = {
            "avoid_highways": True,
            "prefer_bike_lanes": True,
            "avoid_steep_hills": False,
            "surface_preference": "paved"
        }
        
        # Calculate direct distance for comparison
        import utils.general_utils as utils
        direct_distance = utils.calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
        
        fallback_route = controller._get_enhanced_fallback_route(start_coords, end_coords, direct_distance, preferences)
        
        print(f"✓ Fallback route calculated:")
        print(f"  - Direct distance: {direct_distance:.2f} km")
        print(f"  - Estimated route distance: {fallback_route['distance']:.2f} km")
        print(f"  - Estimated duration: {fallback_route['duration']:.1f} minutes")
        print(f"  - Bike friendly: {fallback_route['bike_friendly']}")
        
        # Validate fallback calculation
        assert fallback_route['distance'] > direct_distance, "Route distance should be greater than direct distance"
        assert fallback_route['estimated'] == True, "Fallback route should be marked as estimated"
        assert fallback_route['bike_friendly'] == True, "Fallback route should be bike-friendly"
        
        print("✅ Fallback route calculation tests passed!")
        
    except Exception as e:
        print(f"❌ Fallback route calculation test failed: {e}")
        logger.error(f"Fallback calculation test error: {e}", exc_info=True)
        return False
    
    return True

def test_caching_functionality():
    """Test route caching functionality."""
    print("\n=== Testing Route Caching ===")
    
    try:
        from models.route import RouteCollection
        collection = RouteCollection()
        
        # Test custom cache key functionality
        cache_key = "test_route_key"
        test_route_info = {
            "distance": 10.5,
            "duration": 45.0,
            "elevation": 100,
            "bike_friendly": True,
            "source": "test"
        }
        
        # Add to cache
        success = collection.add_route_to_cache_with_key(cache_key, test_route_info)
        assert success, "Failed to add route to cache"
        print("✓ Route added to cache successfully")
        
        # Retrieve from cache
        cached_route = collection.get_route_from_cache_with_key(cache_key)
        assert cached_route is not None, "Failed to retrieve route from cache"
        assert cached_route['distance'] == test_route_info['distance'], "Cached route data mismatch"
        assert 'cached_at' in cached_route, "Cache timestamp not added"
        print("✓ Route retrieved from cache successfully")
        
        print("✅ Route caching tests passed!")
        
    except Exception as e:
        print(f"❌ Route caching test failed: {e}")
        logger.error(f"Caching test error: {e}", exc_info=True)
        return False
    
    return True

def main():
    """Run all tests for enhanced route calculation."""
    print("🚴 Testing Enhanced Route Calculation for Bicycling Trips")
    print("=" * 60)
    
    tests = [
        test_coordinate_validation,
        test_enhanced_route_calculation,
        test_fallback_calculation,
        test_caching_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            logger.error(f"Test {test.__name__} failed: {e}", exc_info=True)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced route calculation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
