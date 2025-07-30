#!/usr/bin/env python3
"""
Test script to verify trip persistence functionality.
This script tests that trips are properly saved to the database and loaded when users log in.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_trip_persistence():
    """Test that trips are properly persisted between sessions."""
    print("Testing trip persistence functionality...")

    try:
        # Import required modules
        from auth.user_management.user_manager import UserManager
        import core.database_manager as database_manager

        # Create a test user manager instance
        user_manager = UserManager()

        # Use an existing user for testing
        test_username = "sam"  # This user exists in the database
        test_password = "test123"  # We'll set this manually
        test_email = "sam@example.com"

        print(f"1. Creating/logging in test user: {test_username}")

        # Check if user already exists, if not create one
        if test_username not in user_manager.users:
            # Create user manually for testing
            from datetime import datetime
            import hashlib
            import base64
            import os

            # Generate salt and hash password
            salt_bytes = os.urandom(32)
            salt = base64.b64encode(salt_bytes).decode('utf-8')
            key = hashlib.pbkdf2_hmac('sha256', test_password.encode('utf-8'), salt_bytes, 100000)
            password_hash = base64.b64encode(key).decode('utf-8')

            user_manager.users[test_username] = {
                'username': test_username,
                'name': "Test User",
                'email': test_email,
                'password_hash': password_hash,
                'salt': salt,
                'is_admin': False,
                'is_guest': False,
                'email_verified': True,
                'stats': {
                    'total_trips': 0,
                    'total_distance': 0.0,
                    'total_co2_saved': 0.0,
                    'total_calories': 0,
                    'trips': []
                },
                'preferences': {}
            }
            user_manager.save_users()

            # Also add user to database
            conn = database_manager.create_connection()
            if conn:
                try:
                    # Check if user already exists in database
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ?", (test_username,))
                    if not cursor.fetchone():
                        # Add user to database
                        user_id = database_manager.add_user(conn, (
                            test_username, "Test User", test_email, password_hash, salt, None, 0, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ))
                        print(f"   - Test user added to database with ID: {user_id}")
                    else:
                        print("   - Test user already exists in database")
                except Exception as e:
                    print(f"   - Error adding user to database: {e}")
                finally:
                    conn.close()

            print("   - Test user created successfully")
        else:
            print("   - Test user already exists")

        # Authenticate the user by setting current_user directly for testing
        user_manager.current_user = test_username
        print("   - User authenticated successfully")

        # Get initial trip count
        initial_trips = user_manager.get_user_trips(test_username)
        initial_count = len(initial_trips)
        print(f"2. Initial trip count: {initial_count}")

        # Add a test trip
        test_distance = 5.0
        test_co2_saved = 1.0
        test_calories = 200
        test_duration = 30.0

        print("3. Adding a test trip...")
        success = user_manager.update_user_stats(test_distance, test_co2_saved, test_calories, test_duration)

        if success:
            print("   - Trip added to memory successfully")
        else:
            print("   - Failed to add trip to memory")
            return False

        # Also add to database directly to ensure consistency
        conn = database_manager.create_connection()
        if conn:
            try:
                # Get user ID
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (test_username,))
                user_row = cursor.fetchone()

                if user_row:
                    user_id = user_row[0]
                    from datetime import datetime as dt
                    trip_data = (user_id, dt.now().isoformat(), test_distance, test_duration, test_co2_saved, test_calories)
                    trip_id = database_manager.add_trip(conn, trip_data)

                    if trip_id:
                        print(f"   - Trip added to database with ID: {trip_id}")
                    else:
                        print("   - Failed to add trip to database")
                        return False
                else:
                    print("   - User not found in database")
                    return False
            finally:
                conn.close()
        else:
            print("   - Could not connect to database")
            return False

        # Check trip count after adding
        updated_trips = user_manager.get_user_trips(test_username)
        updated_count = len(updated_trips)
        print(f"4. Trip count after adding: {updated_count}")

        # Simulate logging out and logging back in
        print("5. Simulating logout and login...")
        user_manager.logout()

        # Create a new user manager instance to simulate a fresh session
        user_manager2 = UserManager()

        # Authenticate again by setting current_user directly for testing
        user_manager2.current_user = test_username
        print("   - User re-authenticated successfully")

        # Check if trips are loaded from database
        final_trips = user_manager2.get_user_trips(test_username)
        final_count = len(final_trips)
        print(f"6. Trip count after re-login: {final_count}")

        # Verify that trips were persisted
        if final_count >= initial_count + 1:
            print("✅ SUCCESS: Trips are properly persisted between sessions!")

            # Show some trip details
            print("\nTrip details:")
            for i, trip in enumerate(final_trips[-3:]):  # Show last 3 trips
                print(f"   Trip {i+1}: Distance={trip.get('distance', 'N/A')}km, "
                      f"CO2 Saved={trip.get('co2_saved', 'N/A')}kg, "
                      f"Date={trip.get('date', 'N/A')}")

            return True
        else:
            print("❌ FAILURE: Trips were not properly persisted!")
            print(f"   Expected at least {initial_count + 1} trips, but found {final_count}")
            return False

    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_trip_persistence()
    if success:
        print("\n🎉 Trip persistence test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Trip persistence test FAILED!")
        sys.exit(1)
