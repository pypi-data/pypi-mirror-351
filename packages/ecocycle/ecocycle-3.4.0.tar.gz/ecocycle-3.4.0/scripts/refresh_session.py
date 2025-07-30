#!/usr/bin/env python3
"""
Script to refresh the user session and force reload statistics.
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.user_management.user_manager import UserManager
import config.config as config

def clear_session():
    """Clear the current session."""
    session_file = config.SESSION_FILE
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
            print(f"✓ Session file cleared: {session_file}")
            return True
        except Exception as e:
            print(f"✗ Error clearing session file: {e}")
            return False
    else:
        print(f"✓ No session file to clear")
        return True

def force_reload_user_data():
    """Force reload user data from database."""
    print("Force reloading user data...")
    
    # Initialize user manager
    user_manager = UserManager()
    
    # Target user
    username = "nexus.ecocycle@gmail.com"
    
    if username in user_manager.users:
        print(f"✓ User found: {username}")
        
        # Force reload trips from database
        print("Reloading trips from database...")
        success = user_manager.load_user_trips_from_database(username)
        
        if success:
            print("✓ Successfully reloaded trips from database")
            
            # Get updated stats
            user_data = user_manager.users[username]
            stats = user_data.get('stats', {})
            
            print(f"Updated statistics:")
            print(f"  - Total trips: {stats.get('total_trips', 0)}")
            print(f"  - Total distance: {stats.get('total_distance', 0.0):.2f} km")
            print(f"  - Total CO2 saved: {stats.get('total_co2_saved', 0.0):.2f} kg")
            print(f"  - Total calories: {stats.get('total_calories', 0)}")
            
            return True
        else:
            print("✗ Failed to reload trips from database")
            return False
    else:
        print(f"✗ User not found: {username}")
        return False

def create_fresh_session():
    """Create a fresh session for the user."""
    print("Creating fresh session...")
    
    # Initialize user manager
    user_manager = UserManager()
    
    # Target user
    username = "nexus.ecocycle@gmail.com"
    
    if username in user_manager.users:
        # Set as current user
        user_manager.current_user = username
        
        # Force reload trips
        user_manager.load_user_trips_from_database(username)
        
        # Create session manually
        session_data = {
            "username": username,
            "session_verifier": user_manager._calculate_verifier(username)
        }
        
        session_file = config.SESSION_FILE
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            
            print(f"✓ Fresh session created: {session_file}")
            return True
        except Exception as e:
            print(f"✗ Error creating session: {e}")
            return False
    else:
        print(f"✗ User not found: {username}")
        return False

def verify_session():
    """Verify the session works correctly."""
    print("Verifying session...")
    
    # Initialize user manager
    user_manager = UserManager()
    
    # Check session like the app does
    from main import check_existing_session
    
    logged_in_username = check_existing_session(user_manager)
    
    if logged_in_username:
        print(f"✓ Session verification successful")
        print(f"  - Logged in as: {logged_in_username}")
        
        # Get current user stats
        current_user_data = user_manager.get_current_user()
        if current_user_data:
            stats = current_user_data.get('stats', {})
            print(f"  - Current stats: {stats.get('total_trips', 0)} trips, {stats.get('total_distance', 0.0):.1f} km")
            return True
        else:
            print(f"✗ Could not get current user data")
            return False
    else:
        print(f"✗ Session verification failed")
        return False

def main():
    """Main function."""
    print("EcoCycle Session Refresh")
    print("=" * 50)
    
    # Step 1: Clear existing session
    print("Step 1: Clearing existing session...")
    clear_success = clear_session()
    
    if clear_success:
        # Step 2: Force reload user data
        print("\nStep 2: Force reloading user data...")
        reload_success = force_reload_user_data()
        
        if reload_success:
            # Step 3: Create fresh session
            print("\nStep 3: Creating fresh session...")
            session_success = create_fresh_session()
            
            if session_success:
                # Step 4: Verify session
                print("\nStep 4: Verifying session...")
                verify_success = verify_session()
                
                if verify_success:
                    print("\n" + "=" * 50)
                    print("✓ Session refresh completed successfully!")
                    print("Your statistics should now display correctly when you log in.")
                    print("Please restart the EcoCycle application.")
                else:
                    print("\n✗ Session verification failed")
            else:
                print("\n✗ Failed to create fresh session")
        else:
            print("\n✗ Failed to reload user data")
    else:
        print("\n✗ Failed to clear session")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
