#!/usr/bin/env python3
"""
Test script to verify that the dashboard is displaying real data instead of placeholder values.
This script tests the API endpoints that the dashboard uses to load data.
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
    print("🔐 Testing login...")
    
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

def test_stats_endpoint(session):
    """Test the stats endpoint that the dashboard uses."""
    print("\n📊 Testing /api/stats endpoint...")
    
    # Test basic stats
    response = session.get(f"{WEB_APP_URL}/api/stats/{TEST_USERNAME}")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Basic stats retrieved successfully")
        print(f"   Total trips: {stats.get('total_trips', 'N/A')}")
        print(f"   Total distance: {stats.get('total_distance', 'N/A')} km")
        print(f"   Total CO2 saved: {stats.get('total_co2_saved', 'N/A')} kg")
        print(f"   Total calories: {stats.get('total_calories', 'N/A')}")
        
        # Test detailed stats (what the dashboard actually calls)
        response = session.get(f"{WEB_APP_URL}/api/stats/{TEST_USERNAME}?detailed=1")
        
        if response.status_code == 200:
            detailed_stats = response.json()
            print("✅ Detailed stats retrieved successfully")
            
            # Check for environmental impact data
            if 'environmental_impact' in detailed_stats:
                env_impact = detailed_stats['environmental_impact']
                print(f"   Trees equivalent: {env_impact.get('trees_equivalent', 'N/A')}")
                print(f"   Car trips avoided: {env_impact.get('car_trips_avoided', 'N/A')}")
                print(f"   Gasoline saved: {env_impact.get('gasoline_saved', 'N/A')} liters")
            else:
                print("⚠️  No environmental impact data found")
            
            # Check for weekly data
            if 'weekly_distances' in detailed_stats:
                weekly = detailed_stats['weekly_distances']
                print(f"   Weekly distances: {weekly}")
            else:
                print("⚠️  No weekly distance data found")
            
            return detailed_stats
        else:
            print(f"❌ Failed to get detailed stats: {response.status_code}")
            return stats
    else:
        print(f"❌ Failed to get stats: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return None

def test_environmental_impact_endpoint(session):
    """Test the environmental impact endpoint."""
    print("\n🌱 Testing /api/environmental-impact endpoint...")
    
    response = session.get(f"{WEB_APP_URL}/api/environmental-impact/{TEST_USERNAME}")
    
    if response.status_code == 200:
        impact = response.json()
        print("✅ Environmental impact data retrieved")
        print(f"   Total CO2 saved: {impact.get('total_co2_saved', 'N/A')} kg")
        print(f"   Trees equivalent: {impact.get('trees_equivalent', 'N/A')}")
        print(f"   Car trips avoided: {impact.get('car_trips_avoided', 'N/A')}")
        print(f"   Gasoline saved: {impact.get('gasoline_saved', 'N/A')} liters")
        
        # Check for monthly breakdown
        if 'monthly_breakdown' in impact:
            monthly = impact['monthly_breakdown']
            print(f"   Monthly data points: {len(monthly)}")
            if monthly:
                latest_month = monthly[-1]
                print(f"   Latest month: {latest_month.get('month', 'N/A')} - {latest_month.get('distance', 0)} km")
        else:
            print("⚠️  No monthly breakdown data found")
        
        return impact
    else:
        print(f"❌ Failed to get environmental impact: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return None

def test_trips_endpoint(session):
    """Test the trips endpoint."""
    print("\n🚴 Testing /api/trips endpoint...")
    
    response = session.get(f"{WEB_APP_URL}/api/trips/{TEST_USERNAME}")
    
    if response.status_code == 200:
        trips = response.json()
        print(f"✅ Retrieved {len(trips)} trips")
        
        if trips:
            # Show details of the most recent trip
            latest_trip = trips[0] if trips else None
            if latest_trip:
                print(f"   Latest trip: {latest_trip.get('name', 'Unnamed')} on {latest_trip.get('date', 'Unknown date')}")
                print(f"   Distance: {latest_trip.get('distance', 'N/A')} km")
                print(f"   Duration: {latest_trip.get('duration', 'N/A')} minutes")
                print(f"   CO2 saved: {latest_trip.get('co2_saved', 'N/A')} kg")
        else:
            print("⚠️  No trips found")
        
        return trips
    else:
        print(f"❌ Failed to get trips: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return []

def analyze_data_quality(stats, impact, trips):
    """Analyze if the data looks real or like placeholder values."""
    print("\n🔍 Data Quality Analysis")
    print("=" * 50)
    
    issues = []
    
    # Check if all values are zero (typical placeholder)
    if stats:
        if (stats.get('total_trips', 0) == 0 and 
            stats.get('total_distance', 0) == 0 and 
            stats.get('total_co2_saved', 0) == 0):
            issues.append("All stats are zero - might be placeholder data")
    
    # Check for unrealistic values
    if stats:
        distance = stats.get('total_distance', 0)
        trips_count = stats.get('total_trips', 0)
        
        if trips_count > 0 and distance > 0:
            avg_distance = distance / trips_count
            if avg_distance > 1000:  # More than 1000km per trip seems unrealistic
                issues.append(f"Unrealistic average distance: {avg_distance:.1f} km per trip")
    
    # Check if environmental impact calculations make sense
    if impact and stats:
        co2_from_stats = stats.get('total_co2_saved', 0)
        co2_from_impact = impact.get('total_co2_saved', 0)
        
        if abs(co2_from_stats - co2_from_impact) > 0.1:
            issues.append("CO2 values don't match between stats and impact endpoints")
    
    # Check if trips data is consistent
    if trips and stats:
        trips_count_from_endpoint = len(trips)
        trips_count_from_stats = stats.get('total_trips', 0)
        
        if trips_count_from_endpoint != trips_count_from_stats:
            issues.append(f"Trip count mismatch: {trips_count_from_endpoint} vs {trips_count_from_stats}")
    
    # Report results
    if issues:
        print("⚠️  Potential data quality issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ Data appears to be real and consistent")
    
    # Check for positive indicators of real data
    positive_indicators = []
    
    if stats and stats.get('total_trips', 0) > 0:
        positive_indicators.append("Has recorded trips")
    
    if trips and len(trips) > 0:
        # Check if trips have realistic dates
        recent_trips = 0
        for trip in trips[:5]:  # Check last 5 trips
            try:
                trip_date = datetime.fromisoformat(trip.get('date', '').replace('Z', '+00:00'))
                days_ago = (datetime.now() - trip_date).days
                if days_ago < 30:  # Trip within last 30 days
                    recent_trips += 1
            except:
                pass
        
        if recent_trips > 0:
            positive_indicators.append(f"Has {recent_trips} recent trips")
    
    if positive_indicators:
        print("\n✅ Positive indicators of real data:")
        for indicator in positive_indicators:
            print(f"   + {indicator}")

def main():
    """Main test function."""
    print("🧪 EcoCycle Dashboard Data Quality Test")
    print("=" * 50)
    
    # Test login
    session = test_login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    # Test all endpoints
    stats = test_stats_endpoint(session)
    impact = test_environmental_impact_endpoint(session)
    trips = test_trips_endpoint(session)
    
    # Analyze data quality
    analyze_data_quality(stats, impact, trips)
    
    print("\n📋 Summary")
    print("=" * 50)
    print("The dashboard should now display real data from these endpoints.")
    print("If you see zeros or placeholder values, check:")
    print("1. User has logged trips via CLI or web interface")
    print("2. Sync service is working properly")
    print("3. Database contains trip data")
    print("4. API endpoints are returning correct data structure")

if __name__ == "__main__":
    main()
