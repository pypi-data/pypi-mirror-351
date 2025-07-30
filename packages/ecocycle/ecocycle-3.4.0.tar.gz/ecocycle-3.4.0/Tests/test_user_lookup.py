import logging
import core.database_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_get_user():
    """Test the get_user function with both username and email."""
    # Initialize the database connection pool
    database_manager.initialize_connection_pool()
    
    # Test with a transaction to ensure proper cleanup
    with database_manager.transaction() as conn:
        # Test with the email that was causing issues
        email = "shirish.pothi.27@gmail.com"
        user_data = database_manager.get_user(conn, email)
        
        if user_data:
            user_id = user_data[0]  # First column is the ID
            print(f"Success! Found user with ID {user_id} for email {email}")
            
            # Test adding a trip for this user
            trip_data = (user_id, "2025-05-01", 10.5, 45.0, 2.1, 350)
            trip_id = database_manager.add_trip(conn, trip_data)
            
            if trip_id:
                print(f"Successfully added trip with ID {trip_id} for user {user_id}")
            else:
                print(f"Failed to add trip for user {user_id}")
        else:
            print(f"Could not find user for email {email}")
            print("This could be because the user doesn't exist in the database.")
            print("You may need to add the user first or check if the email is correct.")

if __name__ == "__main__":
    test_get_user()