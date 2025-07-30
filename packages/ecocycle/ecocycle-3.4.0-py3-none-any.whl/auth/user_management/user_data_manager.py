"""
EcoCycle - User Data Management Module
Handles user data loading, saving, statistics, and preferences management.
"""
import os
import json
import time
import shutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import config.config as config
from core import database_manager

logger = logging.getLogger(__name__)

# Constants
DEFAULT_USERS_FILE = config.USERS_FILE


class UserDataManager:
    """Handles user data persistence and management."""

    def __init__(self, sheets_manager=None):
        """
        Initialize the UserDataManager.

        Args:
            sheets_manager: Optional sheets manager for Google Sheets integration
        """
        self.sheets_manager = sheets_manager

        # Ensure users file directory exists
        os.makedirs(os.path.dirname(DEFAULT_USERS_FILE) if os.path.dirname(DEFAULT_USERS_FILE) else '.', exist_ok=True)

    def load_users(self) -> Dict[str, Any]:
        """
        Load users from local file or Google Sheets.

        Returns:
            dict: Dictionary of user data
        """
        # Try to load from Google Sheets first if available
        if self.sheets_manager and self.sheets_manager.is_available():
            users = self.sheets_manager.get_users()
            if users:
                logger.info("Users loaded from Google Sheets")
                return users

        # Fall back to local file
        return self._load_local_users()

    def _load_local_users(self) -> Dict[str, Any]:
        """
        Load users from local JSON file with enhanced security practices.

        Returns:
            dict: Dictionary of user data
        """
        if not os.path.exists(DEFAULT_USERS_FILE):
            logger.info(f"Users file {DEFAULT_USERS_FILE} not found, starting with empty users")
            return {}

        try:
            # Check file size before loading to prevent memory issues
            file_size = os.path.getsize(DEFAULT_USERS_FILE)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                logger.error(f"Users file {DEFAULT_USERS_FILE} is too large ({file_size} bytes). Possible corruption or attack.")
                return {}

            # Load and parse the file
            with open(DEFAULT_USERS_FILE, 'r') as file:
                data = json.load(file)

            # Validate the structure of the loaded data
            if not isinstance(data, dict):
                logger.error(f"Invalid users file format. Expected dictionary, got {type(data).__name__}")
                return {}

            # Basic validation of user entries
            for username, user_data in list(data.items()):
                if not isinstance(user_data, dict):
                    logger.warning(f"Removing invalid user entry for '{username}': not a dictionary")
                    del data[username]
                    continue

                # Ensure required fields exist with proper types
                if 'username' not in user_data or user_data['username'] != username:
                    logger.warning(f"Fixing inconsistent username for '{username}'")
                    user_data['username'] = username

                # Ensure stats and preferences dictionaries exist
                if 'stats' not in user_data or not isinstance(user_data['stats'], dict):
                    logger.warning(f"Initializing missing stats for user '{username}'")
                    user_data['stats'] = {
                        'total_trips': 0,
                        'total_distance': 0.0,
                        'total_co2_saved': 0.0,
                        'total_calories': 0,
                        'trips': []
                    }

                if 'preferences' not in user_data or not isinstance(user_data['preferences'], dict):
                    logger.warning(f"Initializing missing preferences for user '{username}'")
                    user_data['preferences'] = {}

            logger.info(f"Users loaded from {DEFAULT_USERS_FILE} ({len(data)} users)")

            # Try to fix file permissions if needed
            try:
                if os.name != 'nt':  # Skip on Windows
                    current_mode = os.stat(DEFAULT_USERS_FILE).st_mode
                    secure_mode = 0o600  # Only owner can read/write
                    if (current_mode & 0o777) != secure_mode:
                        os.chmod(DEFAULT_USERS_FILE, secure_mode)
                        logger.info(f"Fixed file permissions for {DEFAULT_USERS_FILE}")
            except Exception as perm_error:
                logger.warning(f"Unable to set secure file permissions: {perm_error}")

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in users file: {e}")

            # Backup the corrupted file
            backup_file = f"{DEFAULT_USERS_FILE}.corrupted.{int(time.time())}"
            try:
                shutil.copy2(DEFAULT_USERS_FILE, backup_file)
                logger.info(f"Backed up corrupted users file to {backup_file}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted users file: {backup_error}")

            return {}

        except Exception as e:
            logger.error(f"Error loading users from file: {e}")
            return {}

    def save_users(self, users: Dict[str, Any]) -> bool:
        """
        Save users to local file or Google Sheets.

        Args:
            users: Dictionary of user data to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        # Try to save to Google Sheets if available
        if self.sheets_manager and self.sheets_manager.is_available():
            if self.sheets_manager.save_users(users):
                logger.info("Users saved to Google Sheets")
                # Also save to local file as backup
                self._save_local_users(users)
                return True

        # Fall back to local file
        return self._save_local_users(users)

    def _save_local_users(self, users: Dict[str, Any]) -> bool:
        """
        Save users to local JSON file with enhanced security practices.

        Args:
            users: Dictionary of user data to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        # First backup the existing file if it exists
        try:
            if os.path.exists(DEFAULT_USERS_FILE):
                backup_file = f"{DEFAULT_USERS_FILE}.bak"
                shutil.copy2(DEFAULT_USERS_FILE, backup_file)
                logger.debug(f"Backed up users file to {backup_file}")
        except Exception as e:
            logger.warning(f"Failed to create backup of users file: {e}")

        # Use a temporary file to write the data, then rename it
        temp_file = f"{DEFAULT_USERS_FILE}.tmp"
        try:
            # Write to temporary file first
            with open(temp_file, 'w') as file:
                json.dump(users, file, indent=2)
                # Ensure Python's buffers are written to the OS buffer
                file.flush()
                # Ensure the OS buffer is written to disk
                os.fsync(file.fileno())

            # Atomic rename
            if os.name == 'nt':  # Windows
                if os.path.exists(DEFAULT_USERS_FILE):
                    os.replace(temp_file, DEFAULT_USERS_FILE)
                else:
                    os.rename(temp_file, DEFAULT_USERS_FILE)
            else:  # Unix-like
                os.rename(temp_file, DEFAULT_USERS_FILE)

            # Set secure file permissions on Unix-like systems
            if os.name != 'nt':
                try:
                    os.chmod(DEFAULT_USERS_FILE, 0o600)  # Owner read/write only
                except Exception as perm_error:
                    logger.warning(f"Could not set permissions on {DEFAULT_USERS_FILE}: {perm_error}")

            logger.info(f"Users saved to {DEFAULT_USERS_FILE}")
            return True

        except Exception as e:
            logger.error(f"Error saving users to file: {e}")
            # Clean up temporary file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as cleanup_error:
                    logger.error(f"Error removing temporary file {temp_file}: {cleanup_error}")
            return False

    def create_guest_user(self, guest_number: int = 0) -> Dict[str, Any]:
        """
        Create a guest user data structure.

        Args:
            guest_number: Guest number for unique identification

        Returns:
            dict: Guest user data
        """
        username = f"guest{guest_number}" if guest_number > 0 else "guest"
        name = f"Guest User {guest_number}" if guest_number > 0 else "Guest User"

        return {
            'username': username,
            'name': name,
            'email': None,
            'password_hash': None,
            'salt': None,
            'is_admin': False,
            'is_guest': True,
            'guest_number': guest_number,
            'stats': {
                'total_trips': 0,
                'total_distance': 0.0,
                'total_co2_saved': 0.0,
                'total_calories': 0,
                'trips': []
            },
            'preferences': {}
        }

    def update_user_stats(self, user_data: Dict[str, Any], distance: float, co2_saved: float, calories: int, duration: float = 0.0) -> bool:
        """
        Update user statistics and add a new trip.

        Args:
            user_data: User data dictionary to update
            distance: Distance in kilometers
            co2_saved: CO2 saved in kilograms
            calories: Calories burned
            duration: Trip duration in minutes

        Returns:
            bool: True if stats were updated successfully
        """
        try:
            # Ensure stats dictionary exists
            if 'stats' not in user_data:
                user_data['stats'] = {
                    'total_trips': 0,
                    'total_distance': 0.0,
                    'total_co2_saved': 0.0,
                    'total_calories': 0,
                    'trips': []
                }

            # Ensure trips list exists
            if 'trips' not in user_data['stats']:
                user_data['stats']['trips'] = []

            # Update totals
            user_data['stats']['total_trips'] += 1
            user_data['stats']['total_distance'] += distance
            user_data['stats']['total_co2_saved'] += co2_saved
            user_data['stats']['total_calories'] += calories

            # Add new trip
            trip = {
                'date': datetime.now().isoformat(),
                'distance': distance,
                'co2_saved': co2_saved,
                'calories': calories,
                'duration': duration
            }
            user_data['stats']['trips'].append(trip)

            return True

        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
            return False

    def update_user_preference(self, user_data: Dict[str, Any], key: str, value: Any) -> bool:
        """
        Update a user preference.

        Args:
            user_data: User data dictionary to update
            key: Preference key
            value: Preference value

        Returns:
            bool: True if preference was updated successfully
        """
        try:
            # Ensure preferences dictionary exists
            if 'preferences' not in user_data:
                user_data['preferences'] = {}

            # Update preference
            user_data['preferences'][key] = value
            return True

        except Exception as e:
            logger.error(f"Error updating user preference: {e}")
            return False

    def get_user_preference(self, user_data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Get a user preference.

        Args:
            user_data: User data dictionary
            key: Preference key
            default: Default value if preference not found

        Returns:
            Preference value or default
        """
        if 'preferences' in user_data and key in user_data['preferences']:
            return user_data['preferences'][key]
        return default

    def load_user_trips_from_database(self, username: str, users: Dict[str, Any]) -> bool:
        """
        Load trips from database and sync with in-memory user data.

        Args:
            username: Username to load trips for
            users: Users dictionary to update

        Returns:
            bool: True if trips were loaded successfully, False otherwise
        """
        try:
            # Get user ID from username
            conn = database_manager.create_connection()
            if not conn:
                logger.warning(f"Could not connect to database to load trips for user {username}")
                return False

            # Get user ID
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()

            if not user_row:
                logger.warning(f"User {username} not found in database")
                conn.close()
                return False

            user_id = user_row[0]

            # Get trips from database
            db_trips = database_manager.get_user_trips(conn, user_id)
            conn.close()

            # Update in-memory user data with database trips
            if username in users:
                user = users[username]

                # Ensure stats dictionary exists
                if 'stats' not in user:
                    user['stats'] = {
                        'total_trips': 0,
                        'total_distance': 0.0,
                        'total_co2_saved': 0.0,
                        'total_calories': 0,
                        'trips': []
                    }

                # Convert database trips to dictionary format and replace in-memory trips
                trips_list = []
                total_distance = 0.0
                total_co2_saved = 0.0
                total_calories = 0

                for trip_row in db_trips:
                    trip_dict = {
                        'id': trip_row[0],
                        'date': trip_row[2],
                        'distance': float(trip_row[3]) if trip_row[3] else 0.0,
                        'duration': float(trip_row[4]) if trip_row[4] else 0.0,
                        'co2_saved': float(trip_row[5]) if trip_row[5] else 0.0,
                        'calories': int(trip_row[6]) if trip_row[6] else 0,
                        'route_data': trip_row[7] if len(trip_row) > 7 else None,
                        'weather_data': trip_row[8] if len(trip_row) > 8 else None
                    }
                    trips_list.append(trip_dict)

                    # Calculate totals
                    total_distance += trip_dict['distance']
                    total_co2_saved += trip_dict['co2_saved']
                    total_calories += trip_dict['calories']

                # Update user stats with database data
                user['stats']['trips'] = trips_list
                user['stats']['total_trips'] = len(trips_list)
                user['stats']['total_distance'] = total_distance
                user['stats']['total_co2_saved'] = total_co2_saved
                user['stats']['total_calories'] = total_calories

                logger.info(f"Loaded {len(trips_list)} trips from database for user {username}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error loading trips from database for user {username}: {e}")
            return False
