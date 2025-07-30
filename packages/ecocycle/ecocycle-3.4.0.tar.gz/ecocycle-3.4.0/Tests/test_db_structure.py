import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_database_structure():
    """Check if the database has all required tables and columns."""
    try:
        # Connect to the database
        conn = sqlite3.connect("../ecocycle.db")
        cursor = conn.cursor()
        
        # Check if migrations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        if cursor.fetchone() is None:
            logging.error("Migrations table does not exist")
        else:
            logging.info("Migrations table exists")
            
            # Check migrations content
            cursor.execute("SELECT version FROM migrations ORDER BY id")
            versions = [row[0] for row in cursor.fetchall()]
            logging.info(f"Applied migrations: {versions}")
        
        # Check users table columns
        cursor.execute("PRAGMA table_info(users)")
        user_columns = {row[1] for row in cursor.fetchall()}
        required_user_columns = {'id', 'username', 'name', 'email', 'password_hash', 'salt', 
                                'google_id', 'is_admin', 'is_guest', 'registration_date', 
                                'last_login_date', 'account_status'}
        missing_user_columns = required_user_columns - user_columns
        if missing_user_columns:
            logging.error(f"Missing user columns: {missing_user_columns}")
        else:
            logging.info("All required user columns exist")
        
        # Check preferences table columns
        cursor.execute("PRAGMA table_info(preferences)")
        pref_columns = {row[1] for row in cursor.fetchall()}
        required_pref_columns = {'id', 'user_id', 'key', 'value', 'last_updated'}
        missing_pref_columns = required_pref_columns - pref_columns
        if missing_pref_columns:
            logging.error(f"Missing preference columns: {missing_pref_columns}")
        else:
            logging.info("All required preference columns exist")
        
        # Check stats table columns
        cursor.execute("PRAGMA table_info(stats)")
        stats_columns = {row[1] for row in cursor.fetchall()}
        required_stats_columns = {'id', 'user_id', 'total_trips', 'total_distance', 
                                 'total_co2_saved', 'total_calories', 'last_updated'}
        missing_stats_columns = required_stats_columns - stats_columns
        if missing_stats_columns:
            logging.error(f"Missing stats columns: {missing_stats_columns}")
        else:
            logging.info("All required stats columns exist")
        
        # Check trips table columns
        cursor.execute("PRAGMA table_info(trips)")
        trips_columns = {row[1] for row in cursor.fetchall()}
        required_trips_columns = {'id', 'user_id', 'date', 'distance', 'duration', 
                                 'co2_saved', 'calories', 'route_data', 'weather_data'}
        missing_trips_columns = required_trips_columns - trips_columns
        if missing_trips_columns:
            logging.error(f"Missing trips columns: {missing_trips_columns}")
        else:
            logging.info("All required trips columns exist")
        
        conn.close()
        
    except Exception as e:
        logging.error(f"Error checking database structure: {e}")

if __name__ == "__main__":
    check_database_structure()