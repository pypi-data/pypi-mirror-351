#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration in EcoCycle application.
"""

import requests
import json
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_endpoints():
    """Test the main API endpoints that the frontend uses."""
    
    base_url = "http://localhost:5050"
    
    # Test endpoints that don't require authentication
    print("Testing public endpoints...")
    
    # Test login page
    try:
        response = requests.get(f"{base_url}/login")
        print(f"✓ Login page: {response.status_code}")
    except Exception as e:
        print(f"✗ Login page failed: {e}")
    
    # Test signup page
    try:
        response = requests.get(f"{base_url}/signup")
        print(f"✓ Signup page: {response.status_code}")
    except Exception as e:
        print(f"✗ Signup page failed: {e}")
    
    # Create a session for authenticated requests
    session = requests.Session()
    
    # Test guest login
    print("\nTesting guest authentication...")
    try:
        response = session.get(f"{base_url}/auth/guest")
        if response.status_code == 200 or response.status_code == 302:
            print("✓ Guest login successful")
            
            # Test dashboard access
            response = session.get(f"{base_url}/")
            if response.status_code == 200:
                print("✓ Dashboard accessible after guest login")
            else:
                print(f"✗ Dashboard not accessible: {response.status_code}")
                
            # Test API endpoints that require authentication
            print("\nTesting authenticated API endpoints...")
            
            # Test user stats API
            try:
                response = session.get(f"{base_url}/api/stats/guest")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ User stats API: {response.status_code}")
                    print(f"  - Total trips: {data.get('total_trips', 'N/A')}")
                    print(f"  - Total distance: {data.get('total_distance', 'N/A')}")
                else:
                    print(f"✗ User stats API failed: {response.status_code}")
            except Exception as e:
                print(f"✗ User stats API error: {e}")
            
            # Test user trips API
            try:
                response = session.get(f"{base_url}/api/trips/guest")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ User trips API: {response.status_code}")
                    print(f"  - Number of trips: {len(data) if isinstance(data, list) else 'N/A'}")
                else:
                    print(f"✗ User trips API failed: {response.status_code}")
            except Exception as e:
                print(f"✗ User trips API error: {e}")
            
            # Test sync status API
            try:
                response = session.get(f"{base_url}/api/sync/status")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Sync status API: {response.status_code}")
                    print(f"  - Sync enabled: {data.get('sync_enabled', 'N/A')}")
                    print(f"  - Database available: {data.get('database_available', 'N/A')}")
                else:
                    print(f"✗ Sync status API failed: {response.status_code}")
            except Exception as e:
                print(f"✗ Sync status API error: {e}")
            
            # Test sync refresh API
            try:
                response = session.post(f"{base_url}/api/sync/refresh")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Sync refresh API: {response.status_code}")
                    print(f"  - Success: {data.get('success', 'N/A')}")
                else:
                    print(f"✗ Sync refresh API failed: {response.status_code}")
            except Exception as e:
                print(f"✗ Sync refresh API error: {e}")
            
            # Test weather API
            try:
                response = session.get(f"{base_url}/api/weather/London")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Weather API: {response.status_code}")
                    print(f"  - Location: {data.get('location', 'N/A')}")
                    print(f"  - Temperature: {data.get('temperature', 'N/A')}°C")
                else:
                    print(f"✗ Weather API failed: {response.status_code}")
            except Exception as e:
                print(f"✗ Weather API error: {e}")
            
            # Test routes API
            try:
                response = session.get(f"{base_url}/api/routes/guest")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Routes API: {response.status_code}")
                    print(f"  - Number of routes: {len(data) if isinstance(data, list) else 'N/A'}")
                else:
                    print(f"✗ Routes API failed: {response.status_code}")
            except Exception as e:
                print(f"✗ Routes API error: {e}")
                
        else:
            print(f"✗ Guest login failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Guest authentication error: {e}")

def test_data_flow():
    """Test data flow between frontend and backend."""
    print("\n" + "="*50)
    print("TESTING DATA FLOW")
    print("="*50)
    
    # This would test actual data submission and retrieval
    # For now, we'll just verify the endpoints are responding
    
    session = requests.Session()
    base_url = "http://localhost:5050"
    
    # Login as guest
    session.get(f"{base_url}/auth/guest")
    
    # Test trip logging (would normally submit real data)
    print("Testing trip logging data flow...")
    try:
        # This is a mock trip data submission
        trip_data = {
            "distance": 5.2,
            "duration": 25,
            "start_location": "Home",
            "end_location": "Work",
            "date": "2024-01-15"
        }
        
        # Note: This endpoint might not exist yet, but we're testing the concept
        response = session.post(f"{base_url}/api/trips/guest", json=trip_data)
        print(f"Trip submission response: {response.status_code}")
        
    except Exception as e:
        print(f"Trip logging test error: {e}")

if __name__ == "__main__":
    print("EcoCycle Frontend-Backend Integration Test")
    print("="*50)
    
    print("Make sure the web application is running on http://localhost:5050")
    print("You can start it with: python web/web_app.py")
    print()
    
    # Wait a moment for user to start the server if needed
    input("Press Enter when the server is running...")
    
    try:
        test_api_endpoints()
        test_data_flow()
        
        print("\n" + "="*50)
        print("INTEGRATION TEST COMPLETE")
        print("="*50)
        print("Check the results above to see which endpoints are working correctly.")
        print("Any ✗ marks indicate issues that need to be fixed.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
