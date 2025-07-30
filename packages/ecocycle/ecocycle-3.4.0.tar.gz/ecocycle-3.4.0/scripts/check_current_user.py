#!/usr/bin/env python3
"""
Script to check the current logged-in user and their statistics.
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.user_management.user_manager import UserManager
import config.config as config

def check_session():
    """Check the current session and user."""
    print("Checking current session...")
    
    # Check session file
    session_file = config.SESSION_FILE
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            username = session_data.get('username')
            print(f"✓ Session file found")
            print(f"  - Logged in as: {username}")
            
            return username
        except Exception as e:
            print(f"✗ Error reading session file: {e}")
            return None
    else:
        print(f"✗ No session file found at: {session_file}")
        return None

def check_user_stats(username):
    """Check user statistics."""
    print(f"\nChecking statistics for user: {username}")
    
    # Initialize user manager
    user_manager = UserManager()
    
    if username in user_manager.users:
        user_data = user_manager.users[username]
        stats = user_data.get('stats', {})
        
        print(f"User data found:")
        print(f"  - Name: {user_data.get('name', 'Unknown')}")
        print(f"  - Email: {user_data.get('email', 'None')}")
        print(f"  - Is Guest: {user_data.get('is_guest', False)}")
        print(f"  - Is Admin: {user_data.get('is_admin', False)}")
        
        print(f"\nStatistics:")
        print(f"  - Total trips: {stats.get('total_trips', 0)}")
        print(f"  - Total distance: {stats.get('total_distance', 0.0):.2f} km")
        print(f"  - Total CO2 saved: {stats.get('total_co2_saved', 0.0):.2f} kg")
        print(f"  - Total calories: {stats.get('total_calories', 0)}")
        print(f"  - Number of trip records: {len(stats.get('trips', []))}")
        
        # Show recent trips
        trips = stats.get('trips', [])
        if trips:
            print(f"\nRecent trips (last 3):")
            for i, trip in enumerate(trips[-3:], 1):
                date = trip.get('date', 'Unknown')
                distance = trip.get('distance', 0.0)
                co2 = trip.get('co2_saved', 0.0)
                calories = trip.get('calories', 0)
                print(f"  {i}. {date[:10]} - {distance:.1f}km, {co2:.2f}kg CO2, {calories} cal")
        
        return True
    else:
        print(f"✗ User '{username}' not found in user data")
        return False

def simulate_login():
    """Simulate the login process to see what happens."""
    print(f"\nSimulating login process...")
    
    # Initialize user manager
    user_manager = UserManager()
    
    # Check for existing session (like the app does)
    from main import check_existing_session
    
    logged_in_username = check_existing_session(user_manager)
    
    if logged_in_username:
        print(f"✓ Session login successful for: {logged_in_username}")
        
        # Check if this user is set as current
        if user_manager.current_user == logged_in_username:
            print(f"✓ User correctly set as current user")
            
            # Get current user data
            current_user_data = user_manager.get_current_user()
            if current_user_data:
                stats = current_user_data.get('stats', {})
                print(f"✓ Current user stats loaded:")
                print(f"  - Total trips: {stats.get('total_trips', 0)}")
                print(f"  - Total distance: {stats.get('total_distance', 0.0):.2f} km")
                print(f"  - Total CO2 saved: {stats.get('total_co2_saved', 0.0):.2f} kg")
                print(f"  - Total calories: {stats.get('total_calories', 0)}")
                
                return stats
            else:
                print(f"✗ Could not get current user data")
                return None
        else:
            print(f"✗ Current user not set correctly")
            print(f"  - Expected: {logged_in_username}")
            print(f"  - Actual: {user_manager.current_user}")
            return None
    else:
        print(f"✗ Session login failed")
        return None

def main():
    """Main function."""
    print("EcoCycle User Session Check")
    print("=" * 50)
    
    # Check session
    session_username = check_session()
    
    if session_username:
        # Check user stats
        user_found = check_user_stats(session_username)
        
        if user_found:
            # Simulate login
            login_stats = simulate_login()
            
            if login_stats:
                print(f"\n✓ Everything looks correct!")
                print(f"If you're still seeing different numbers, try:")
                print(f"1. Restart the application")
                print(f"2. Log out and log back in")
                print(f"3. Clear the session file and log in again")
            else:
                print(f"\n✗ Issue detected in login process")
        else:
            print(f"\n✗ User data issue detected")
    else:
        print(f"\n✗ No valid session found")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
