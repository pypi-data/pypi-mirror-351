#!/usr/bin/env python3
"""
Test script to verify synchronization between backend and frontend.
This script tests the data flow from CLI logging to web display.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
WEB_APP_URL = "http://localhost:5050"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass123"

def test_login():
    """Test login to the web application."""
    print("Testing login...")
    
    session = requests.Session()
    
    # First get the login page to establish session
    response = session.get(f"{WEB_APP_URL}/login")
    if response.status_code != 200:
        print(f"❌ Failed to access login page: {response.status_code}")
        return None
    
    # Attempt login
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }
    
    response = session.post(f"{WEB_APP_URL}/login", data=login_data, allow_redirects=False)
    
    if response.status_code == 302:  # Redirect indicates successful login
        print("✅ Login successful")
        return session
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return None

def test_get_trips(session):
    """Test getting trips from the API."""
    print("Testing trip retrieval...")
    
    response = session.get(f"{WEB_APP_URL}/api/trips/{TEST_USERNAME}")
    
    if response.status_code == 200:
        trips = response.json()
        print(f"✅ Retrieved {len(trips)} trips")
        return trips
    else:
        print(f"❌ Failed to get trips: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return []

def test_sync_refresh(session):
    """Test the sync refresh endpoint."""
    print("Testing sync refresh...")
    
    response = session.post(f"{WEB_APP_URL}/api/sync/refresh/{TEST_USERNAME}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Sync refresh successful")
            return True
        else:
            print(f"❌ Sync refresh failed: {result.get('message', 'Unknown error')}")
            return False
    else:
        print(f"❌ Sync refresh request failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return False

def test_environmental_impact(session):
    """Test the environmental impact endpoint."""
    print("Testing environmental impact...")
    
    response = session.get(f"{WEB_APP_URL}/api/environmental-impact/{TEST_USERNAME}")
    
    if response.status_code == 200:
        impact = response.json()
        print("✅ Environmental impact data retrieved")
        print(f"   Total CO2 saved: {impact.get('total_co2_saved', 0)} kg")
        print(f"   Trees equivalent: {impact.get('trees_equivalent', 0)}")
        print(f"   Car trips avoided: {impact.get('car_trips_avoided', 0)}")
        return True
    else:
        print(f"❌ Failed to get environmental impact: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return False

def test_log_trip(session):
    """Test logging a trip via the web API."""
    print("Testing trip logging...")
    
    trip_data = {
        'name': 'Test Trip',
        'date': datetime.now().isoformat(),
        'distance': 5.0,
        'duration': 20.0,
        'start_location': 'Test Start',
        'end_location': 'Test End'
    }
    
    response = session.post(f"{WEB_APP_URL}/api/trips/log", 
                           json=trip_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Trip logged successfully")
            print(f"   Trip ID: {result.get('trip_id')}")
            return True
        else:
            print(f"❌ Trip logging failed: {result}")
            return False
    else:
        print(f"❌ Trip logging request failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return False

def main():
    """Main test function."""
    print("🧪 Starting EcoCycle Synchronization Tests")
    print("=" * 50)
    
    # Test login
    session = test_login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    print()
    
    # Test initial trip retrieval
    initial_trips = test_get_trips(session)
    print(f"Initial trip count: {len(initial_trips)}")
    
    print()
    
    # Test environmental impact
    test_environmental_impact(session)
    
    print()
    
    # Test logging a new trip
    test_log_trip(session)
    
    print()
    
    # Test sync refresh
    test_sync_refresh(session)
    
    print()
    
    # Test trip retrieval after sync
    final_trips = test_get_trips(session)
    print(f"Final trip count: {len(final_trips)}")
    
    print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    if len(final_trips) > len(initial_trips):
        print("✅ Synchronization working: New trip appears in frontend")
    else:
        print("⚠️  Synchronization may have issues: Trip count unchanged")
    
    print(f"Initial trips: {len(initial_trips)}")
    print(f"Final trips: {len(final_trips)}")
    
    if final_trips:
        latest_trip = max(final_trips, key=lambda x: x.get('date', ''))
        print(f"Latest trip: {latest_trip.get('name', 'Unknown')} on {latest_trip.get('date', 'Unknown')}")

if __name__ == "__main__":
    main()
