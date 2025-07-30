"""
EcoCycle - Synchronization Service Module
Handles bidirectional data synchronization between web dashboard and Python core modules.
"""
import os
import json
import logging
import time
import queue
import threading
import sqlite3
import traceback
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Import EcoCycle modules
import config.config
from core.dependency.dependency_manager import ensure_packages
import core.database_manager

logger = logging.getLogger(__name__)

class SyncService:
    """
    Manages bidirectional data synchronization between web dashboard and core Python modules.

    Features:
    - Real-time synchronization of user data between web and Python modules
    - Automatic conflict resolution
    - Timestamp tracking for data consistency
    - Support for all authentication methods
    """

    def __init__(self, user_manager=None, sheets_manager=None, db_manager=None):
        """
        Initialize the SyncService.

        Args:
            user_manager: UserManager instance
            sheets_manager: SheetsManager instance for Google Sheets integration
            db_manager: DatabaseManager instance for SQLite storage
        """
        # Store references to the managers
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager

        # Setup database connection
        self.db_manager = db_manager

        # Ensure database is initialized
        if self.db_manager:
            self.db_manager.initialize_database()

        # Create synchronization queue
        self.sync_queue = queue.Queue()

        # Synchronization thread control
        self.sync_thread_running = False
        self.sync_thread = None

        # Cache for optimizing sync operations
        self.last_sync_timestamps = {}

        # Create sync tables if they don't exist
        self._init_sync_tables()

        # Start synchronization thread
        self.start_sync_thread()

    def _init_sync_tables(self):
        """Initialize database tables needed for synchronization."""
        try:
            # Create sync_timestamps table
            create_sync_timestamps_sql = '''
            CREATE TABLE IF NOT EXISTS sync_timestamps (
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                last_sync TIMESTAMP NOT NULL,
                last_modified TIMESTAMP NOT NULL,
                source TEXT NOT NULL,
                PRIMARY KEY (entity_type, entity_id)
            );
            '''

            # Create sync_queue table
            create_sync_queue_sql = '''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                operation TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0
            );
            '''

            # Create sync_conflicts table
            create_sync_conflicts_sql = '''
            CREATE TABLE IF NOT EXISTS sync_conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                web_data TEXT NOT NULL,
                core_data TEXT NOT NULL,
                resolution TEXT DEFAULT 'pending',
                resolved_data TEXT
            );
            '''

            # Create user_data table for fallback storage
            create_user_data_sql = '''
            CREATE TABLE IF NOT EXISTS user_data (
                username TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                last_updated TIMESTAMP NOT NULL
            );
            '''

            # Use database_manager to create the tables
            import core.database_manager as database_manager
            with database_manager.get_connection() as conn:
                database_manager.create_table(conn, create_sync_timestamps_sql)
                database_manager.create_table(conn, create_sync_queue_sql)
                database_manager.create_table(conn, create_sync_conflicts_sql)
                database_manager.create_table(conn, create_user_data_sql)

            logger.info("Sync tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing sync tables: {e}")

    def start_sync_thread(self):
        """Start the background synchronization thread."""
        if not self.sync_thread_running:
            self.sync_thread_running = True
            self.sync_thread = threading.Thread(target=self._background_sync, daemon=True)
            self.sync_thread.start()
            logger.info("Synchronization thread started")

    def stop_sync_thread(self):
        """Stop the background synchronization thread."""
        if self.sync_thread_running:
            self.sync_thread_running = False
            if self.sync_thread:
                self.sync_thread.join(timeout=5)
            logger.info("Synchronization thread stopped")

    def _background_sync(self):
        """Background thread for periodic synchronization."""
        while self.sync_thread_running:
            try:
                # Process any queued sync requests
                while not self.sync_queue.empty():
                    sync_task = self.sync_queue.get()
                    try:
                        username = sync_task.get('username')
                        operation = sync_task.get('operation')
                        data = sync_task.get('data')

                        if operation == 'sync_user_stats':
                            self._sync_user_stats(username, data)
                        elif operation == 'sync_user_preferences':
                            self._sync_user_preferences(username, data)
                        elif operation == 'sync_new_user':
                            self._sync_new_user(data)
                        elif operation == 'sync_user_trips':
                            self._sync_user_trips(username, data)
                    except Exception as e:
                        logger.error(f"Error processing sync task: {e}")
                    finally:
                        self.sync_queue.task_done()

                # Perform periodic full synchronization
                self._perform_full_sync()

                # Sleep before next check
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in synchronization thread: {e}")
                time.sleep(5)  # Longer sleep on error

    def _perform_full_sync(self):
        """Perform a full synchronization between all data sources."""
        # Only perform full sync periodically (every 5 minutes)
        current_time = time.time()
        last_full_sync = self.last_sync_timestamps.get('full_sync', 0)

        if current_time - last_full_sync < 300:  # 5 minutes
            return

        try:
            logger.info("Starting full synchronization")

            # Sync users
            if self.user_manager and self.sheets_manager and self.sheets_manager.is_available():
                # Get users from both sources
                local_users = self.user_manager.users
                sheet_users = self.sheets_manager.get_users()

                if sheet_users:
                    # Check for new or updated users in sheets
                    for username, sheet_user in sheet_users.items():
                        if username not in local_users:
                            # New user in sheets, add to local
                            local_users[username] = sheet_user
                            logger.info(f"Added new user '{username}' from Google Sheets")
                        else:
                            # User exists in both, merge data
                            self._merge_user_data(username, local_users[username], sheet_user)

                    # Check for users in local but not in sheets
                    for username, local_user in local_users.items():
                        if username not in sheet_users:
                            # User exists locally but not in sheets, add to sheets
                            self.sheets_manager.add_user(username, local_user)
                            logger.info(f"Added user '{username}' to Google Sheets")

                # Save updated users
                self.user_manager.save_users()

            self.last_sync_timestamps['full_sync'] = current_time
            logger.info(f"Full synchronization completed successfully at {datetime.fromtimestamp(current_time).isoformat()}")
        except Exception as e:
            logger.error(f"Error during full synchronization: {e}")

    def _merge_user_data(self, username, local_user, remote_user):
        """
        Merge user data from local and remote sources, resolving conflicts.

        Args:
            username (str): Username of the user
            local_user (dict): User data from local source
            remote_user (dict): User data from remote source
        """
        # Strategy: Use most recent data for each field based on timestamps
        # For complex data like stats, sum values if possible

        try:
            # Merge stats (sum numeric values, use max for dates)
            if 'stats' in local_user and 'stats' in remote_user:
                local_stats = local_user.get('stats', {})
                remote_stats = remote_user.get('stats', {})

                # Use the higher value for cumulative stats
                for stat_key in ['total_trips', 'total_distance', 'total_co2_saved', 'total_calories']:
                    local_val = local_stats.get(stat_key, 0)
                    remote_val = remote_stats.get(stat_key, 0)

                    # Convert to appropriate type
                    if isinstance(local_val, (int, float)) and isinstance(remote_val, (int, float)):
                        local_stats[stat_key] = max(local_val, remote_val)

                # Merge trip lists
                local_trips = local_stats.get('trips', [])
                remote_trips = remote_stats.get('trips', [])

                if local_trips or remote_trips:
                    # Use trip ID or timestamp as unique identifier
                    all_trips = {trip.get('id', trip.get('timestamp', f"trip_{i}")): trip
                                for i, trip in enumerate(local_trips)}

                    # Add/update with remote trips
                    for trip in remote_trips:
                        trip_id = trip.get('id', trip.get('timestamp'))
                        if trip_id and trip_id not in all_trips:
                            all_trips[trip_id] = trip

                    # Convert back to list
                    local_stats['trips'] = list(all_trips.values())

            # Merge preferences (use most recent if timestamp available, otherwise keep both)
            local_prefs = local_user.get('preferences', {})
            remote_prefs = remote_user.get('preferences', {})

            for key, remote_value in remote_prefs.items():
                if key not in local_prefs:
                    local_prefs[key] = remote_value

            logger.info(f"Successfully merged user data for '{username}'")
        except Exception as e:
            logger.error(f"Error merging user data for '{username}': {e}")

    def queue_sync_task(self, operation, username=None, data=None):
        """
        Queue a synchronization task to be processed by the sync thread.

        Args:
            operation (str): Sync operation type ('sync_user_stats', 'sync_user_preferences', etc.)
            username (str, optional): Username associated with the sync task
            data (dict, optional): Data to be synchronized
        """
        task = {
            'operation': operation,
            'username': username,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }

        self.sync_queue.put(task)
        logger.debug(f"Queued sync task: {operation} for user: {username}")

    def _sync_user_stats(self, username, stats):
        """
        Synchronize user statistics.

        Args:
            username (str): Username of the user
            stats (dict): User statistics to sync
        """
        try:
            if not self.user_manager:
                logger.error("UserManager not available for synchronization")
                return

            # Update local user stats
            if username in self.user_manager.users:
                user = self.user_manager.users[username]
                user_stats = user.get('stats', {})

                # Update stats values
                for key, value in stats.items():
                    user_stats[key] = value

                user['stats'] = user_stats
                user['last_sync'] = datetime.now().isoformat()
                self.user_manager.users[username] = user
                self.user_manager.save_users()

                # Sync to Google Sheets if available
                if self.sheets_manager and self.sheets_manager.is_available():
                    self.sheets_manager.update_user_stats(username, stats)

                logger.info(f"Synchronized stats for user '{username}'")
            else:
                logger.warning(f"Cannot sync stats: User '{username}' not found")
        except Exception as e:
            logger.error(f"Error synchronizing stats for user '{username}': {e}")

    def _sync_user_preferences(self, username, preferences):
        """
        Synchronize user preferences.

        Args:
            username (str): Username of the user
            preferences (dict): User preferences to sync
        """
        try:
            if not self.user_manager:
                logger.error("UserManager not available for synchronization")
                return

            # Update local user preferences
            if username in self.user_manager.users:
                user = self.user_manager.users[username]
                user_prefs = user.get('preferences', {})

                # Update preferences values
                for key, value in preferences.items():
                    user_prefs[key] = value

                user['preferences'] = user_prefs
                user['last_sync'] = datetime.now().isoformat()
                self.user_manager.users[username] = user
                self.user_manager.save_users()

                # Sync to Google Sheets if available
                if self.sheets_manager and self.sheets_manager.is_available():
                    self.sheets_manager.update_user_preferences(username, preferences)

                logger.info(f"Synchronized preferences for user '{username}'")
            else:
                logger.warning(f"Cannot sync preferences: User '{username}' not found")
        except Exception as e:
            logger.error(f"Error synchronizing preferences for user '{username}': {e}")

    def _sync_new_user(self, user_data):
        """
        Synchronize a new user across platforms.

        Args:
            user_data (dict): User data to sync
        """
        try:
            if not self.user_manager:
                logger.error("UserManager not available for synchronization")
                return

            username = user_data.get('username')
            if not username:
                logger.error("Cannot sync new user: Missing username")
                return

            # Add user to local storage
            if username not in self.user_manager.users:
                self.user_manager.users[username] = user_data
                self.user_manager.save_users()
                logger.info(f"Added new user '{username}' to local storage")

            # Sync to Google Sheets if available
            if self.sheets_manager and self.sheets_manager.is_available():
                self.sheets_manager.add_user(username, user_data)
                logger.info(f"Added new user '{username}' to Google Sheets")
        except Exception as e:
            logger.error(f"Error synchronizing new user: {e}")

    def _sync_user_trips(self, username, trips_data):
        """
        Synchronize user trips.

        Args:
            username (str): Username of the user
            trips_data (dict): User trips to sync
        """
        try:
            if not self.user_manager:
                logger.error("UserManager not available for synchronization")
                return

            # Update local user trips
            if username in self.user_manager.users:
                user = self.user_manager.users[username]
                user_stats = user.get('stats', {})

                # Get existing trips
                existing_trips = user_stats.get('trips', [])
                existing_trip_ids = {trip.get('id', trip.get('timestamp')): i
                                    for i, trip in enumerate(existing_trips)}

                # Process new trips
                new_trips = trips_data.get('trips', [])
                for trip in new_trips:
                    trip_id = trip.get('id', trip.get('timestamp'))
                    if trip_id in existing_trip_ids:
                        # Update existing trip
                        existing_trips[existing_trip_ids[trip_id]] = trip
                    else:
                        # Add new trip
                        existing_trips.append(trip)

                # Update stats based on trips
                user_stats['trips'] = existing_trips
                user_stats['total_trips'] = len(existing_trips)

                # Recalculate totals
                total_distance = sum(trip.get('distance', 0) for trip in existing_trips)
                total_co2_saved = sum(trip.get('co2_saved', 0) for trip in existing_trips)
                total_calories = sum(trip.get('calories', 0) for trip in existing_trips)

                user_stats['total_distance'] = total_distance
                user_stats['total_co2_saved'] = total_co2_saved
                user_stats['total_calories'] = total_calories

                user['stats'] = user_stats
                user['last_sync'] = datetime.now().isoformat()
                self.user_manager.users[username] = user
                self.user_manager.save_users()

                # Sync to Google Sheets if available
                if self.sheets_manager and self.sheets_manager.is_available():
                    self.sheets_manager.update_user_stats(username, user_stats)

                logger.info(f"Synchronized trips for user '{username}'")
            else:
                logger.warning(f"Cannot sync trips: User '{username}' not found")
        except Exception as e:
            logger.error(f"Error synchronizing trips for user '{username}': {e}")

    # API methods for web app to use
    def get_user_data(self, username):
        """
        Get synchronized user data including stats and preferences.

        Args:
            username (str): Username of the user

        Returns:
            dict: User data including stats and preferences, or None if not found
        """
        if not username:
            logger.warning("No username provided to get_user_data")
            return None

        try:
            user_data = None

            # 1. Try to get from UserManager first
            if self.user_manager:
                try:
                    # Use get_user method if available, otherwise access users dict directly
                    if hasattr(self.user_manager, 'get_user') and callable(self.user_manager.get_user):
                        user_data = self.user_manager.get_user(username)
                    elif hasattr(self.user_manager, 'users') and username in self.user_manager.users:
                        user_data = self.user_manager.users.get(username)
                except Exception as e:
                    logger.error(f"Error getting user data from UserManager: {e}")

            # 2. If not found, try to sync from Google Sheets if available
            if not user_data and self.sheets_manager and self.sheets_manager.is_available():
                try:
                    sheet_users = self.sheets_manager.get_users()
                    if sheet_users and username in sheet_users:
                        user_data = sheet_users[username]
                        # Update local user manager if possible
                        if self.user_manager:
                            if not hasattr(self.user_manager, 'users'):
                                self.user_manager.users = {}
                            self.user_manager.users[username] = user_data
                            # Try to save if the method exists
                            if hasattr(self.user_manager, 'save_users') and callable(self.user_manager.save_users):
                                try:
                                    self.user_manager.save_users()
                                except Exception as save_error:
                                    logger.error(f"Error saving user data: {save_error}")
                except Exception as e:
                    logger.error(f"Error syncing user data from sheets: {e}")

            # 3. If still not found, try database fallback
            if not user_data:
                logger.info(f"Falling back to database for user data: '{username}'")
                user_data = self._get_user_data_from_database(username)

            # 4. Ensure basic structure exists
            if user_data and isinstance(user_data, dict):
                # Ensure stats exists
                if 'stats' not in user_data or not isinstance(user_data['stats'], dict):
                    user_data['stats'] = {
                        'total_trips': 0,
                        'total_distance': 0.0,
                        'total_co2_saved': 0.0,
                        'total_calories': 0,
                        'trips': []
                    }

                # Ensure preferences exists
                if 'preferences' not in user_data or not isinstance(user_data['preferences'], dict):
                    user_data['preferences'] = {}

                # Ensure username is set
                if 'username' not in user_data:
                    user_data['username'] = username

                # Update last sync timestamp
                user_data['_last_sync'] = datetime.now().isoformat()

                # Queue a sync to ensure data is persisted
                self.queue_sync_task('sync_user_data', username=username, data=user_data)

            return user_data

        except Exception as e:
            logger.error(f"Error in get_user_data for '{username}': {e}")
            logger.debug(f"Error details: {traceback.format_exc()}")

            # Return minimal user data structure on error
            return {
                'username': username,
                'stats': {
                    'total_trips': 0,
                    'total_distance': 0.0,
                    'total_co2_saved': 0.0,
                    'total_calories': 0,
                    'trips': []
                },
                'preferences': {},
                '_error': str(e)
            }

    def update_user_data(self, username, data, source='web'):
        """
        Update user data and sync across platforms.

        Args:
            username (str): Username of the user
            data (dict): User data to update
            source (str): Source of the update ('web' or 'core')

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_exists = False

            # Check if user exists in UserManager
            if self.user_manager and username in self.user_manager.users:
                user_exists = True
                user = self.user_manager.users[username]
            else:
                # Check if user exists in database
                user = self._get_user_data_from_database(username)
                if user:
                    user_exists = True
                    # Add to UserManager if it exists
                    if self.user_manager:
                        self.user_manager.users[username] = user

            if not user_exists:
                logger.error(f"Cannot update user data: User '{username}' not found in any source")
                return False

            # Queue sync tasks for different data types
            success = True

            # Update stats if provided
            if 'stats' in data:
                try:
                    self.queue_sync_task('sync_user_stats', username, data['stats'])
                    # Also store in database for fallback
                    self._update_user_data_in_database(username, {'stats': data['stats']})
                except Exception as e:
                    logger.error(f"Error updating stats for '{username}': {e}")
                    success = False

            # Update preferences if provided
            if 'preferences' in data:
                try:
                    self.queue_sync_task('sync_user_preferences', username, data['preferences'])
                    # Also store in database for fallback
                    self._update_user_data_in_database(username, {'preferences': data['preferences']})
                except Exception as e:
                    logger.error(f"Error updating preferences for '{username}': {e}")
                    success = False

            # Update trips if provided
            if 'trips' in data:
                try:
                    trips_data = {'trips': data['trips']}
                    self.queue_sync_task('sync_user_trips', username, trips_data)
                    # Also store in database for fallback
                    self._update_user_data_in_database(username, {'trips': data['trips']})
                except Exception as e:
                    logger.error(f"Error updating trips for '{username}': {e}")
                    success = False

            return success
        except Exception as e:
            logger.error(f"Error updating user data for '{username}': {e}")
            # Attempt to update database as fallback
            try:
                self._update_user_data_in_database(username, data)
                logger.info(f"Fallback: Updated user data in database for '{username}'")
                return True
            except Exception as db_e:
                logger.error(f"Failed to update user data in database for '{username}': {db_e}")
                return False

    def refresh_user_data(self, username):
        """
        Force a refresh of user data from all sources.

        Args:
            username (str): Username of the user

        Returns:
            dict: Updated user data
        """
        try:
            # Update sync timestamp to indicate a manual refresh occurred
            current_time = time.time()
            self.last_sync_timestamps['full_sync'] = current_time
            logger.info(f"Manual sync triggered for user '{username}' at {datetime.fromtimestamp(current_time).isoformat()}")

            # Check for user existence
            user_exists = False

            if self.user_manager:
                user_exists = username in self.user_manager.users

            if not user_exists:
                # Check if user exists in database
                db_user = self._get_user_data_from_database(username)
                if db_user:
                    # If found in database but not in memory, add to memory
                    if self.user_manager:
                        self.user_manager.users[username] = db_user
                        user_exists = True
                        logger.info(f"Loaded user '{username}' from database to memory")

                if not user_exists:
                    return None

            # Try to get user data from Google Sheets
            sheets_sync_success = False
            if self.sheets_manager and self.sheets_manager.is_available():
                try:
                    # Get all users from sheets and extract the specific user we want
                    all_sheet_users = self.sheets_manager.get_users()
                    if all_sheet_users and username in all_sheet_users:
                        sheet_user = all_sheet_users[username]
                        if self.user_manager and username in self.user_manager.users:
                            self._merge_user_data(username, self.user_manager.users[username], sheet_user)
                            self.user_manager.save_users()
                            sheets_sync_success = True
                except Exception as e:
                    logger.warning(f"Error syncing with Google Sheets for '{username}': {e}")

            # Ensure database has latest data
            if self.user_manager and username in self.user_manager.users:
                user_data = self.user_manager.users.get(username)
                self._store_user_data_in_database(username, user_data)
                return user_data
            else:
                # Final fallback to database
                return self._get_user_data_from_database(username)

        except Exception as e:
            logger.error(f"Error refreshing user data for '{username}': {e}")
            # Final fallback to database
            return self._get_user_data_from_database(username)


    def _get_user_data_from_database(self, username):
        """
        Get user data from the local database with enhanced error handling and logging.

        Args:
            username (str): Username to look up

        Returns:
            dict: User data with basic structure if not found, or None on critical error
        """
        if not username:
            logger.warning("No username provided to _get_user_data_from_database")
            return None

        # Default user data structure to return if no data found
        default_data = {
            'username': username,
            'stats': {
                'total_trips': 0,
                'total_distance': 0.0,
                'total_co2_saved': 0.0,
                'total_calories': 0,
                'trips': []
            },
            'preferences': {}
        }

        if not self.db_manager:
            logger.warning("No database manager available for user data lookup")
            return default_data

        try:
            # Ensure we have a connection
            conn = None
            try:
                conn = self.db_manager.get_connection()
                if not conn:
                    logger.error("Failed to get database connection")
                    return default_data

                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data, last_updated FROM user_data
                    WHERE username = ?
                """, (username,))

                result = cursor.fetchone()
                if result and result[0]:
                    try:
                        user_data = json.loads(result[0])
                        logger.debug(f"Retrieved user data from database for {username} (updated: {result[1]})")

                        # Ensure basic structure exists in the retrieved data
                        if not isinstance(user_data, dict):
                            logger.warning(f"Invalid user data format for {username}, using defaults")
                            return default_data

                        # Ensure required fields exist
                        if 'username' not in user_data:
                            user_data['username'] = username
                        if 'stats' not in user_data or not isinstance(user_data['stats'], dict):
                            user_data['stats'] = default_data['stats']
                        if 'preferences' not in user_data or not isinstance(user_data['preferences'], dict):
                            user_data['preferences'] = {}

                        # Now fetch trips from the trips table to ensure we have the latest data
                        try:
                            # Get user ID from users table
                            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                            user_id_row = cursor.fetchone()

                            if user_id_row:
                                user_id = user_id_row[0]

                                # Get trips from trips table
                                cursor.execute("""
                                    SELECT id, date, distance, duration, co2_saved, calories, route_data, weather_data
                                    FROM trips WHERE user_id = ? ORDER BY date DESC
                                """, (user_id,))

                                trip_rows = cursor.fetchall()

                                # Convert database trips to dictionary format
                                trips_list = []
                                for trip_row in trip_rows:
                                    trip_dict = {
                                        'id': trip_row[0],
                                        'date': trip_row[1],
                                        'distance': float(trip_row[2]) if trip_row[2] else 0.0,
                                        'duration': float(trip_row[3]) if trip_row[3] else 0.0,
                                        'co2_saved': float(trip_row[4]) if trip_row[4] else 0.0,
                                        'calories': int(trip_row[5]) if trip_row[5] else 0,
                                        'route_data': trip_row[6] if len(trip_row) > 6 else None,
                                        'weather_data': trip_row[7] if len(trip_row) > 7 else None
                                    }
                                    trips_list.append(trip_dict)

                                # Update user data with fresh trips from database
                                user_data['stats']['trips'] = trips_list

                                # Recalculate totals from actual trip data
                                total_trips = len(trips_list)
                                total_distance = sum(trip.get('distance', 0) for trip in trips_list)
                                total_co2_saved = sum(trip.get('co2_saved', 0) for trip in trips_list)
                                total_calories = sum(trip.get('calories', 0) for trip in trips_list)

                                user_data['stats'].update({
                                    'total_trips': total_trips,
                                    'total_distance': total_distance,
                                    'total_co2_saved': total_co2_saved,
                                    'total_calories': total_calories
                                })

                                logger.info(f"Retrieved {total_trips} trips from database for user {username}")

                        except Exception as trips_error:
                            logger.warning(f"Could not fetch trips from database for user {username}: {trips_error}")
                            # Continue with existing user data even if trips fetch fails

                        return user_data

                    except json.JSONDecodeError as je:
                        logger.error(f"Failed to decode JSON data for user {username}: {je}")
                        return default_data
                    except Exception as e:
                        logger.error(f"Error processing user data for {username}: {e}")
                        return default_data

                logger.info(f"No user data found in database for {username}")
                return default_data

            except Exception as e:
                logger.error(f"Database error while fetching user data for {username}: {e}")
                return default_data

                # Ensure connection is properly closed
                try:
                    if conn:
                        conn.close()
                except Exception as e:
                    logger.error(f"Error closing database connection: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in _get_user_data_from_database for {username}: {e}")
            logger.debug(f"Error details: {traceback.format_exc()}")

        return default_data

    def _store_user_data_in_database(self, username, user_data):
        """
        Store user data in the database with enhanced error handling and validation.

        Args:
            username (str): Username of the user
            user_data (dict): User data to store

        Returns:
            bool: True if successful, False otherwise
        """
        if not username or not user_data:
            logger.warning(f"Invalid parameters for _store_user_data_in_database: username={username}")
            return False

        conn = None
        try:
            # Ensure user_data is a dict
            if not isinstance(user_data, dict):
                logger.warning(f"user_data for '{username}' is not a dict, converting: {type(user_data)}")
                try:
                    # Try to convert to dict if it's a JSON string
                    if isinstance(user_data, str):
                        user_data = json.loads(user_data)
                    else:
                        # If conversion isn't possible, wrap it
                        user_data = {"data": str(user_data)}
                except Exception as e:
                    logger.error(f"Failed to convert user_data to dict: {e}")
                    user_data = {"data": str(user_data)}

            # Ensure username is set in the data
            if 'username' not in user_data:
                user_data['username'] = username

            # Ensure basic structure exists
            if 'stats' not in user_data or not isinstance(user_data['stats'], dict):
                user_data['stats'] = {
                    'total_trips': 0,
                    'total_distance': 0.0,
                    'total_co2_saved': 0.0,
                    'total_calories': 0,
                    'trips': []
                }

            if 'preferences' not in user_data or not isinstance(user_data['preferences'], dict):
                user_data['preferences'] = {}

            # Add/update timestamps
            timestamp = datetime.now().isoformat()
            user_data['_last_updated'] = timestamp

            # Convert to JSON string
            try:
                data_json = json.dumps(user_data)
            except Exception as e:
                logger.error(f"Failed to serialize user data to JSON: {e}")
                return False

            if not self.db_manager:
                logger.error("No database manager available for storing user data")
                return False

            # Get database connection
            conn = self.db_manager.get_connection()
            if not conn:
                logger.error("Failed to get database connection")
                return False

            cursor = conn.cursor()

            # Check if user exists
            cursor.execute("SELECT 1 FROM user_data WHERE username = ?", (username,))
            user_exists = cursor.fetchone() is not None

            if user_exists:
                # Update existing user
                cursor.execute(
                    "UPDATE user_data SET data = ?, last_updated = ? WHERE username = ?",
                    (data_json, timestamp, username)
                )
                logger.debug(f"Updated user data in database for '{username}'")
            else:
                # Insert new user
                cursor.execute(
                    "INSERT INTO user_data (username, data, last_updated) VALUES (?, ?, ?)",
                    (username, data_json, timestamp)
                )
                logger.debug(f"Inserted new user data in database for '{username}'")

            conn.commit()
            logger.info(f"Successfully stored user data in database for '{username}'")
            return True

        except Exception as e:
            logger.error(f"Error storing user data in database for '{username}': {e}")
            logger.debug(f"Error details: {traceback.format_exc()}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return False

        finally:
            # Ensure connection is properly closed
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing database connection: {e}")

    def _update_user_data_in_database(self, username, partial_data):
        """
        Update specific fields of user data in the database.

        Args:
            username (str): Username of the user
            partial_data (dict): Partial user data to update

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get existing data first
            existing_data = self._get_user_data_from_database(username)

            if not existing_data:
                # If no existing data, store the partial data directly
                return self._store_user_data_in_database(username, partial_data)

            # Update existing data with new partial data
            for key, value in partial_data.items():
                # Special handling for nested structures
                if key in existing_data and isinstance(existing_data[key], dict) and isinstance(value, dict):
                    # Deep update for nested dictionaries
                    existing_data[key].update(value)
                else:
                    # Direct replacement for non-dict values or new keys
                    existing_data[key] = value

            # Store the updated data
            return self._store_user_data_in_database(username, existing_data)
        except Exception as e:
            logger.error(f"Error updating user data in database for '{username}': {e}")
            return False

# Singleton instance
_sync_service_instance = None

def get_sync_service(user_manager=None, sheets_manager=None, db_manager=None):
    """
    Get the singleton instance of SyncService.

    Args:
        user_manager: UserManager instance
        sheets_manager: SheetsManager instance
        db_manager: DatabaseManager instance

    Returns:
        SyncService: Singleton instance
    """
    global _sync_service_instance

    if _sync_service_instance is None:
        _sync_service_instance = SyncService(user_manager, sheets_manager, db_manager)

    return _sync_service_instance
