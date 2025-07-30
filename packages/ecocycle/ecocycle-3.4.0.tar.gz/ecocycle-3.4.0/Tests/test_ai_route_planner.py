"""
Test script for the modularized AI Route Planner.
"""
import sys
import os
from unittest.mock import Mock, patch
import pytest

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.route_planner.ai_route_planner_new import AIRoutePlanner
from apps.route_planner.modules.constants import ROUTE_TYPES, DIFFICULTY_LEVELS


def test_airouteplanner_initialization():
    """Test AIRoutePlanner initialization."""
    # Create mock user manager and sheets manager
    user_manager = Mock()
    sheets_manager = Mock()
    
    # Initialize the planner
    planner = AIRoutePlanner(user_manager, sheets_manager)
    
    # Verify initialization
    assert planner.user_manager == user_manager
    assert planner.sheets_manager == sheets_manager
    assert hasattr(planner, 'api_service')
    assert hasattr(planner, 'cache_manager')
    assert hasattr(planner, 'route_manager')
    assert hasattr(planner, 'route_generator')
    assert hasattr(planner, 'route_analyzer')
    assert hasattr(planner, 'ui')
    
    # Verify backward compatibility properties
    assert planner.routes_file == os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'routes.json')
    assert hasattr(planner, 'saved_routes')
    assert hasattr(planner, 'route_cache')


def test_generate_route_recommendation():
    """Test generating a route recommendation."""
    # Create mock objects
    user_manager = Mock()
    sheets_manager = Mock()
    
    # Initialize the planner
    planner = AIRoutePlanner(user_manager, sheets_manager)
    
    # Mock user input
    with patch('builtins.input', side_effect=['London', '2', '2', '15', '2', '1,2']):
        # Generate route
        result = planner.generate_route_recommendation('test_user')
        
        # Verify result
        assert isinstance(result, dict)
        assert 'name' in result
        assert 'location' in result
        assert 'distance' in result
        assert 'difficulty' in result
        assert 'terrain' in result
        
        # Verify preferences were saved
        user_manager.update_user_preferences.assert_called()


def test_view_saved_routes():
    """Test viewing saved routes."""
    # Create mock objects
    user_manager = Mock()
    sheets_manager = Mock()
    
    # Initialize the planner
    planner = AIRoutePlanner(user_manager, sheets_manager)
    
    # Add test routes
    test_routes = [
        {
            'name': 'Test Route 1',
            'location': 'Test Location',
            'distance': 10.0,
            'difficulty': 'intermediate',
            'terrain': 'mixed'
        },
        {
            'name': 'Test Route 2',
            'location': 'Test Location',
            'distance': 15.0,
            'difficulty': 'advanced',
            'terrain': 'hilly'
        }
    ]
    
    # Mock route manager
    planner.route_manager.get_user_routes = Mock(return_value=test_routes)
    
    # Test viewing routes
    with patch('builtins.input', side_effect=['q']):
        planner.view_saved_routes('test_user')
        
    # Verify route manager was called
    planner.route_manager.get_user_routes.assert_called_with('test_user')


def test_update_preferences():
    """Test updating cycling preferences."""
    # Create mock objects
    user_manager = Mock()
    sheets_manager = Mock()
    
    # Initialize the planner
    planner = AIRoutePlanner(user_manager, sheets_manager)
    
    # Mock user input
    with patch('builtins.input', side_effect=['2', '2', '15', '2', '1,2']):
        planner.update_cycling_preferences('test_user')
        
    # Verify user manager was called
    user_manager.update_user_preferences.assert_called()

if __name__ == '__main__':
    pytest.main([__file__])
