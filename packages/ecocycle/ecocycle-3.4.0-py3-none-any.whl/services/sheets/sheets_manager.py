"""
EcoCycle - Google Sheets Manager Module
Handles data storage and retrieval using Google Sheets.
"""
import os
import json
import logging
import sys
import re
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from datetime import datetime, timedelta
import time
from functools import wraps
from tqdm import tqdm

# Import dependency_manager for ensuring packages
import core.dependency.dependency_manager

logger = logging.getLogger(__name__)

# Check if Google API clients are available
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    logger.warning("Google Sheets API not available. Will attempt to install required packages.")

# Import validation function to check if all required packages are installed
def check_required_packages(auto_install=False):
    """
    Check if all required packages for Google Sheets integration are installed.

    Args:
        auto_install (bool): If True, attempt to install missing packages

    Returns:
        bool: True if all packages are available or successfully installed, False otherwise
    """
    missing_packages = []

    try:
        import google.oauth2.service_account
    except ImportError:
        missing_packages.append("google-auth")

    try:
        import googleapiclient.discovery
    except ImportError:
        missing_packages.append("google-api-python-client")

    if missing_packages:
        if auto_install:
            logger.info(f"Attempting to install missing packages: {', '.join(missing_packages)}")
            success, failed = dependency_manager.ensure_packages(missing_packages, silent=False)
            if success:
                logger.info("Successfully installed all required packages")
                return True
            else:
                logger.error(f"Failed to install some packages: {', '.join(failed)}")
                return False
        else:
            install_command = f"pip install {' '.join(missing_packages)}"
            logger.error(f"Missing required packages: {', '.join(missing_packages)}")
            logger.error(f"Please install them using: {install_command}")
            return False

    return True


def retry_on_error(max_retries=3, delay=1.0):
    """
    Decorator to retry a function on exception with exponential backoff.

    Args:
        max_retries (int): Maximum number of retries
        delay (float): Initial delay in seconds, doubled after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise

                    logger.warning(f"Attempt {retries} failed, retrying in {current_delay}s: {e}")
                    time.sleep(current_delay)
                    current_delay *= 2

            return None  # Should never reach here, but added as a safeguard
        return wrapper
    return decorator


class SheetsManager:
    """Manages data storage and retrieval using Google Sheets."""

    # Sheet name constants for better consistency and easier management
    SHEET_USERS = "Registered Users"            # User data
    SHEET_TRIPS = "Trips Logged"            # Trip logs
    SHEET_TEAMS = "Team Stats"             # Team data
    SHEET_CHALLENGES = "Challenges"       # Eco challenges
    SHEET_LEADERBOARD = "Leaderboard"      # Leaderboard stats
    SHEET_REPORTS = "Reports"          # Monthly reports
    SHEET_CONFIG = "Config"           # System configuration

    def __init__(self):
        """Initialize the SheetsManager."""
        self.credentials = None
        self.service = None
        self.drive_service = None
        self.spreadsheet_id = os.environ.get('ECOCYCLE_SPREADSHEET_ID')

        # Try to ensure the required packages are installed if not available
        global GOOGLE_SHEETS_AVAILABLE
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.info("Google Sheets API not available, attempting to install required packages")
            # Try to install the sheets_integration feature
            success, _ = dependency_manager.ensure_feature('sheets_integration', silent=False)
            if success:
                try:
                    # Try to import again after installation
                    global service_account, build, HttpError
                    from google.oauth2 import service_account
                    from googleapiclient.discovery import build
                    from googleapiclient.errors import HttpError
                    GOOGLE_SHEETS_AVAILABLE = True
                    logger.info("Successfully installed Google Sheets API packages")
                except ImportError:
                    logger.warning("Failed to import Google Sheets API packages even after installation attempt")
                    return
            else:
                logger.warning("SheetsManager initialized, but Google Sheets API is not available")
                logger.warning("Install required packages with: pip install google-api-python-client google-auth")
                return

        # Initialize Google Sheets API if credentials are available
        creds_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_file:
            # Try a few common locations for credentials
            common_locations = [
                'google-credentials.json',
                'Google Auth Client Secret.json',
                os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
            ]

            for loc in common_locations:
                if os.path.exists(loc):
                    creds_file = loc
                    logger.info(f"Found credentials at {creds_file}")
                    break

        if creds_file and os.path.exists(creds_file):
            try:
                self.credentials = service_account.Credentials.from_service_account_file(
                    creds_file,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
                self.service = build('sheets', 'v4', credentials=self.credentials)
                self.drive_service = build('drive', 'v3', credentials=self.credentials)

                if not self.spreadsheet_id:
                    logger.warning("No spreadsheet ID found in environment variable ECOCYCLE_SPREADSHEET_ID")
                    logger.info("You can set it manually with sheets_manager.spreadsheet_id = 'your_id'")

                logger.info("Google Sheets API initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Google Sheets API: {e}")
                self.credentials = None
                self.service = None

                # More detailed error explanation
                if "invalid_grant" in str(e).lower():
                    logger.error("Authentication failed - credentials may be expired or invalid")
                elif "not found" in str(e).lower():
                    logger.error("The specified credentials file was found but could not be read properly")
                elif "permission" in str(e).lower():
                    logger.error("Permission denied when reading credentials file")
        else:
            if creds_file:
                logger.error(f"Credentials file specified but not found at: {creds_file}")
            else:
                logger.warning("No credentials file specified. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")

            logger.warning("Google Sheets integration will be unavailable")

        if not self.is_available():
            logger.warning("Google Sheets integration is not fully configured and will not be available")
            logger.warning("Make sure both credentials and spreadsheet ID are properly set")

    def is_available(self) -> bool:
        """
        Check if Google Sheets integration is available.

        Returns:
            bool: True if Google Sheets integration is available, False otherwise
        """
        return self.service is not None and self.spreadsheet_id is not None

    def validate_sheet_name(self, sheet_name: str) -> bool:
        """
        Validate a sheet name according to Google Sheets rules.

        Args:
            sheet_name (str): Name of the sheet to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not sheet_name:
            logger.error("Sheet name cannot be empty")
            return False

        # Google Sheets has a 100 character limit for sheet names
        if len(sheet_name) > 100:
            logger.error(f"Sheet name '{sheet_name}' is too long (max 100 characters)")
            return False

        # Check for invalid characters
        invalid_chars = ":/\\?*[]"
        for char in invalid_chars:
            if char in sheet_name:
                logger.error(f"Sheet name '{sheet_name}' contains invalid character: '{char}'")
                return False

        return True

    def validate_cell_range(self, range_name: str) -> bool:
        """
        Validate a cell range in A1 notation.

        Args:
            range_name (str): Range to validate (e.g., "A1:C10")

        Returns:
            bool: True if valid, False otherwise
        """
        if not range_name:
            logger.error("Range cannot be empty")
            return False

        # Check if it's a valid A1 notation
        import re

        # Pattern for single cell (e.g., "A1")
        cell_pattern = r"^[A-Z]{1,3}[1-9][0-9]*$"

        # Pattern for range (e.g., "A1:C10")
        range_pattern = r"^[A-Z]{1,3}[1-9][0-9]*:[A-Z]{1,3}[1-9][0-9]*$"

        if ":" in range_name:
            # It's a range
            if not re.match(range_pattern, range_name):
                logger.error(f"Invalid range format: '{range_name}'. Expected format like 'A1:C10'")
                return False

            # Check if start cell comes before end cell
            start_cell, end_cell = range_name.split(":")

            # Extract column letters and row numbers
            start_col = ''.join(filter(str.isalpha, start_cell)).upper()
            start_row = int(''.join(filter(str.isdigit, start_cell)))

            end_col = ''.join(filter(str.isalpha, end_cell)).upper()
            end_row = int(''.join(filter(str.isdigit, end_cell)))

            # Convert column letters to numbers
            start_col_num = 0
            for i, char in enumerate(reversed(start_col)):
                start_col_num += (ord(char) - ord('A') + 1) * (26 ** i)

            end_col_num = 0
            for i, char in enumerate(reversed(end_col)):
                end_col_num += (ord(char) - ord('A') + 1) * (26 ** i)

            # Check if range is valid (end comes after start)
            if end_row < start_row or end_col_num < start_col_num:
                logger.error(f"Invalid range: '{range_name}'. End cell must come after start cell")
                return False
        else:
            # It's a single cell
            if not re.match(cell_pattern, range_name):
                logger.error(f"Invalid cell format: '{range_name}'. Expected format like 'A1'")
                return False

        return True

    def _column_letter_to_index(self, column_letter: str) -> int:
        """
        Convert column letter to column index (0-based).
        Handles multi-letter columns (e.g., 'AA', 'ZZ') correctly.

        Args:
            column_letter (str): Column letter (A, B, ..., Z, AA, AB, etc.)

        Returns:
            int: 0-based column index
        """
        column_letter = column_letter.upper()
        column_index = 0

        for i, char in enumerate(reversed(column_letter)):
            # For each position, multiply by 26^position and add letter value
            # A=0, B=1, ..., Z=25
            column_index += (ord(char) - ord('A') + (0 if i > 0 else 0)) * (26 ** i)

        return column_index

    def _parse_a1_notation(self, a1_range: str) -> Tuple[int, int, int, int]:
        """
        Parse A1 notation range into row/column indices.

        Args:
            a1_range (str): Range in A1 notation (e.g., "A1:C10")

        Returns:
            tuple: (start_row, start_col, end_row, end_col) as 0-based indices
        """
        if not a1_range or ':' not in a1_range:
            # Handle single cell
            if a1_range:
                # Extract column letters and row number
                column_letters = ''.join(filter(str.isalpha, a1_range))
                row_number = int(''.join(filter(str.isdigit, a1_range)))

                # Convert to 0-based indices
                column_index = self._column_letter_to_index(column_letters)
                row_index = row_number - 1

                return row_index, column_index, row_index + 1, column_index + 1

            logger.error(f"Invalid A1 notation: {a1_range}")
            return 0, 0, 1, 1

        # Handle range (e.g., "A1:C10")
        start_cell, end_cell = a1_range.split(':')

        # Extract column letters and row numbers
        start_column_letters = ''.join(filter(str.isalpha, start_cell))
        start_row_number = int(''.join(filter(str.isdigit, start_cell)))

        end_column_letters = ''.join(filter(str.isalpha, end_cell))
        end_row_number = int(''.join(filter(str.isdigit, end_cell)))

        # Convert to 0-based indices
        start_column_index = self._column_letter_to_index(start_column_letters)
        start_row_index = start_row_number - 1

        end_column_index = self._column_letter_to_index(end_column_letters) + 1  # Add 1 for exclusive end
        end_row_index = end_row_number  # Already exclusive

        return start_row_index, start_column_index, end_row_index, end_column_index

    @retry_on_error()
    def get_or_create_sheet(self, sheet_name: str) -> bool:
        """
        Get or create a sheet with the given name.

        Args:
            sheet_name (str): Name of the sheet

        Returns:
            bool: True if the sheet exists or was created, False otherwise
        """
        if not self.is_available():
            return False

        # Validate sheet name
        if not self.validate_sheet_name(sheet_name):
            return False

        try:
            # Get spreadsheet info
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

            # Check if sheet exists
            sheet_exists = False
            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_exists = True
                    break

            # Create sheet if it doesn't exist
            if not sheet_exists:
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
                logger.info(f"Created new sheet: {sheet_name}")

            return True

        except Exception as e:
            logger.error(f"Error getting or creating sheet {sheet_name}: {e}")
            return False

    @retry_on_error()
    def read_sheet(self, sheet_name: str) -> List[List[str]]:
        """
        Read all data from a sheet.

        Args:
            sheet_name (str): Name of the sheet

        Returns:
            list: List of rows, where each row is a list of values
        """
        if not self.is_available():
            return []

        try:
            # Ensure sheet exists
            if not self.get_or_create_sheet(sheet_name):
                return []

            # Read sheet data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name
            ).execute()

            return result.get('values', [])

        except Exception as e:
            logger.error(f"Error reading sheet {sheet_name}: {e}")
            return []

    @retry_on_error()
    def write_sheet(self, sheet_name: str, data: List[List[str]]) -> bool:
        """
        Write data to a sheet, replacing all existing data.

        Args:
            sheet_name (str): Name of the sheet
            data (list): List of rows, where each row is a list of values

        Returns:
            bool: True if the data was written successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Ensure sheet exists
            if not self.get_or_create_sheet(sheet_name):
                return False

            # Clear existing data
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name
            ).execute()

            # Write new data
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name,
                valueInputOption='RAW',
                body={'values': data}
            ).execute()

            logger.info(f"Wrote {len(data)} rows to sheet {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error writing to sheet {sheet_name}: {e}")
            return False

    @retry_on_error()
    def append_to_sheet(self, sheet_name: str, data: List[List[str]]) -> bool:
        """
        Append data to a sheet.

        Args:
            sheet_name (str): Name of the sheet
            data (list): List of rows, where each row is a list of values

        Returns:
            bool: True if the data was appended successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Ensure sheet exists
            if not self.get_or_create_sheet(sheet_name):
                return False

            # Append data
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': data}
            ).execute()

            logger.info(f"Appended {len(data)} rows to sheet {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error appending to sheet {sheet_name}: {e}")
            return False

    def get_users(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all users from Google Sheets with enhanced format support.

        Returns:
            dict: Dictionary of users, where each key is a username and each value is user data
        """
        if not self.is_available():
            return {}

        try:
            # Read users sheet
            rows = self.read_sheet(self.SHEET_USERS)

            if not rows:
                logger.info("No users found in Google Sheets")
                return {}

            # Convert rows to users dict
            users = {}

            # Check if we're using the new expanded format or old format
            if len(rows) > 0 and len(rows[0]) > 2 and rows[0][0] == 'username' and rows[0][-1] == 'full_user_data':
                # New expanded format - use the full_user_data column
                for row in rows[1:]:  # Skip header row
                    if len(row) >= 12:  # Make sure we have the full_user_data column
                        username = row[0]
                        try:
                            # Use the full user data JSON from the last column
                            user_data = json.loads(row[11])  # full_user_data is the 12th column (index 11)
                            users[username] = user_data
                        except json.JSONDecodeError:
                            logger.error(f"Error decoding user data for {username}")
                            # Try to reconstruct basic user data from individual fields
                            try:
                                users[username] = {
                                    'username': username,
                                    'name': row[1],
                                    'email': row[2],
                                    'registration_date': row[3],
                                    'is_admin': row[4] == 'Yes',
                                    'is_guest': row[5] == 'Yes',
                                    'stats': {
                                        'total_trips': float(row[6]) if row[6] else 0,
                                        'total_distance': float(row[7]) if row[7] else 0.0,
                                        'total_co2_saved': float(row[8]) if row[8] else 0.0,
                                        'total_calories': float(row[9]) if row[9] else 0,
                                        'trips': []
                                    },
                                    'preferences': json.loads(row[10]) if row[10] else {}
                                }
                                logger.info(f"Reconstructed user data for {username} from individual fields")
                            except (ValueError, json.JSONDecodeError, IndexError) as e:
                                logger.error(f"Failed to reconstruct user data for {username}: {e}")
            else:
                # Old format with just username and JSON data
                for row in rows[1:]:  # Skip header row
                    if len(row) >= 2:
                        username = row[0]
                        user_json = row[1]
                        try:
                            user_data = json.loads(user_json)
                            users[username] = user_data
                        except json.JSONDecodeError:
                            logger.error(f"Error decoding user data for {username}")

            logger.info(f"Loaded {len(users)} users from Google Sheets")
            return users

        except Exception as e:
            logger.error(f"Error getting users from Google Sheets: {e}")
            return {}

    def save_users(self, users: Dict[str, Dict[str, Any]]) -> bool:
        """
        Save all users to Google Sheets with improved formatting and organization.

        Args:
            users (dict): Dictionary of users, where each key is a username and each value is user data

        Returns:
            bool: True if the users were saved successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Create header row with expanded columns for better readability in sheets
            rows = [
                ['Username', 'Name', 'Email', 'Registration Date', 'Admin', 'Guest',
                 'Trips Count', 'Total Distance', 'Total CO2 Saved', 'Total Calories Burned',
                 'Preferences', 'Full User Data - JSON String']
            ]

            # Add user rows with expanded data
            for username, user_data in users.items():
                # Extract stats with defaults for missing values
                stats = user_data.get('stats', {})
                preferences = user_data.get('preferences', {})

                row = [
                    username,
                    user_data.get('name', ''),
                    user_data.get('email', ''),
                    user_data.get('registration_date', ''),
                    'Yes' if user_data.get('is_admin', False) else 'No',
                    'Yes' if user_data.get('is_guest', False) else 'No',
                    stats.get('total_trips', 0),
                    stats.get('total_distance', 0.0),
                    stats.get('total_co2_saved', 0.0),
                    stats.get('total_calories', 0),
                    json.dumps(preferences),
                    json.dumps(user_data)  # Full JSON as the last column for backwards compatibility
                ]
                rows.append(row)

            # Write to sheet
            success = self.write_sheet(self.SHEET_USERS, rows)

            if success:
                logger.info(f"Saved {len(users)} users to Google Sheets with enhanced formatting")

                # Apply formatting to improve readability
                try:
                    # Format header row in bold
                    self.set_cell_formatting(self.SHEET_USERS, "A1:L1", {
                        "textFormat": {"bold": True},
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
                    })

                    # Set column width and formatting for better display
                    if len(rows) > 1:
                        # Format numeric columns
                        num_rows = len(rows)
                        self.set_cell_formatting(self.SHEET_USERS, f"G2:J{num_rows}", {
                            "horizontalAlignment": "RIGHT",
                            "numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}
                        })
                except Exception as format_error:
                    logger.warning(f"User data saved but formatting failed: {format_error}")

            return success

        except Exception as e:
            logger.error(f"Error saving users to Google Sheets: {e}")
            return False

    def log_trip(self, username: str, trip_data: Dict[str, Any]) -> bool:
        """
        Log a trip to Google Sheets.

        Args:
            username (str): Username of the user who took the trip
            trip_data (dict): Trip data (date, distance, duration, calories, co2_saved)

        Returns:
            bool: True if the trip was logged successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Format trip data row
            date = trip_data.get('date', '')
            distance = str(trip_data.get('distance', 0))
            duration = str(trip_data.get('duration', 0))
            calories = str(trip_data.get('calories', 0))
            co2_saved = str(trip_data.get('co2_saved', 0))
            route = trip_data.get('route', '')

            row = [username, date, distance, duration, calories, co2_saved, route]

            # Step 1: Ensure sheet exists
            if not self.get_or_create_sheet(self.SHEET_TRIPS):
                return False

            # Step 2: Check if trips sheet has header
            trips = self.read_sheet(self.SHEET_TRIPS)
            if not trips:
                # Add header row
                header = ['username', 'date', 'distance_km', 'duration_minutes', 'calories', 'co2_saved_kg', 'route']
                self.append_to_sheet(self.SHEET_TRIPS, [header])

            # Step 3: Append trip data
            result = self.append_to_sheet(self.SHEET_TRIPS, [row])
            return result

        except Exception as e:
            logger.error(f"Error logging trip for {username}: {e}")
            return False

    @retry_on_error()
    def filter_sheet_data(self, sheet_name: str, filter_conditions: Dict[int, Any]) -> List[List[str]]:
        """
        Filter data from a sheet based on specified conditions.

        Args:
            sheet_name (str): Name of the sheet
            filter_conditions (dict): Dictionary mapping column indices to filter values
                Example: {0: 'username1', 2: lambda x: float(x) > 10.0}

        Returns:
            list: Filtered list of rows
        """
        if not self.is_available():
            return []

        try:
            # Read sheet data
            rows = self.read_sheet(sheet_name)

            if not rows:
                return []

            # Filter rows based on conditions
            filtered_rows = []
            for row in rows:
                include_row = True

                for col_idx, condition in filter_conditions.items():
                    if col_idx >= len(row):
                        continue

                    cell_value = row[col_idx]

                    if callable(condition):
                        # If condition is a function, call it with the cell value
                        if not condition(cell_value):
                            include_row = False
                            break
                    else:
                        # Otherwise, compare directly
                        if cell_value != str(condition):
                            include_row = False
                            break

                if include_row:
                    filtered_rows.append(row)

            return filtered_rows

        except Exception as e:
            logger.error(f"Error filtering data from sheet {sheet_name}: {e}")
            return []

    def sort_sheet_data(self, data: List[List[str]], sort_by: int, reverse: bool = False) -> List[List[str]]:
        """
        Sort sheet data by a specific column.

        Args:
            data (list): List of rows to sort
            sort_by (int): Column index to sort by
            reverse (bool): Whether to sort in reverse order

        Returns:
            list: Sorted list of rows
        """
        if not data or len(data) <= 1:
            return data

        # Separate header if present
        header = data[0] if data else []
        rows = data[1:] if data else []

        try:
            # Try to sort numerically
            sorted_rows = sorted(
                rows,
                key=lambda row: float(row[sort_by]) if sort_by < len(row) else 0,
                reverse=reverse
            )
        except (ValueError, TypeError):
            # Fall back to string sorting
            sorted_rows = sorted(
                rows,
                key=lambda row: row[sort_by] if sort_by < len(row) else "",
                reverse=reverse
            )

        # Reattach header if present
        return [header] + sorted_rows if header else sorted_rows

    def aggregate_data(self, sheet_name: str, group_by: int, agg_columns: Dict[int, str]) -> Dict[str, Dict[str, float]]:
        """
        Aggregate data from a sheet by grouping and applying aggregation functions.

        Args:
            sheet_name (str): Name of the sheet
            group_by (int): Column index to group by
            agg_columns (dict): Dictionary mapping column indices to aggregation function names
                Supported functions: 'sum', 'avg', 'min', 'max', 'count'
                Example: {2: 'sum', 3: 'avg', 4: 'max'}

        Returns:
            dict: Dictionary with group values as keys and aggregated values as nested dicts
        """
        if not self.is_available():
            return {}

        try:
            # Read sheet data
            rows = self.read_sheet(sheet_name)

            if len(rows) <= 1:  # No data or just header
                return {}

            header = rows[0]
            data_rows = rows[1:]

            # Initialize result dictionary
            result = {}

            # Group data
            for row in data_rows:
                if group_by >= len(row):
                    continue

                group_value = row[group_by]

                if group_value not in result:
                    result[group_value] = {
                        'count': 0,
                        'sums': {},
                        'mins': {},
                        'maxs': {},
                        'sum_for_avg': {}
                    }

                result[group_value]['count'] += 1

                # Process each aggregation column
                for col_idx, agg_func in agg_columns.items():
                    if col_idx >= len(row):
                        continue

                    try:
                        value = float(row[col_idx])

                        # Update aggregation values
                        if agg_func in ('sum', 'avg'):
                            if col_idx not in result[group_value]['sums']:
                                result[group_value]['sums'][col_idx] = 0
                                result[group_value]['sum_for_avg'][col_idx] = 0
                            result[group_value]['sums'][col_idx] += value
                            result[group_value]['sum_for_avg'][col_idx] += value

                        if agg_func in ('min', 'max'):
                            if agg_func == 'min':
                                if col_idx not in result[group_value]['mins'] or value < result[group_value]['mins'][col_idx]:
                                    result[group_value]['mins'][col_idx] = value
                            else:  # max
                                if col_idx not in result[group_value]['maxs'] or value > result[group_value]['maxs'][col_idx]:
                                    result[group_value]['maxs'][col_idx] = value
                    except ValueError:
                        continue

            # Prepare final result with named columns
            final_result = {}
            for group_value, data in result.items():
                final_result[group_value] = {}

                for col_idx, agg_func in agg_columns.items():
                    col_name = header[col_idx] if col_idx < len(header) else f"column_{col_idx}"

                    if agg_func == 'sum':
                        final_result[group_value][f"sum_{col_name}"] = data['sums'].get(col_idx, 0)
                    elif agg_func == 'avg':
                        count = data['count'] or 1  # Avoid division by zero
                        final_result[group_value][f"avg_{col_name}"] = data['sum_for_avg'].get(col_idx, 0) / count
                    elif agg_func == 'min':
                        if col_idx in data['mins']:
                            final_result[group_value][f"min_{col_name}"] = data['mins'][col_idx]
                    elif agg_func == 'max':
                        if col_idx in data['maxs']:
                            final_result[group_value][f"max_{col_name}"] = data['maxs'][col_idx]
                    elif agg_func == 'count':
                        final_result[group_value][f"count"] = data['count']

            return final_result

        except Exception as e:
            logger.error(f"Error aggregating data from sheet {sheet_name}: {e}")
            return {}

    def get_trips_for_user(self, username: str) -> List[Dict[str, Any]]:
        """
        Get all trips for a specific user.

        Args:
            username (str): Username to filter trips by

        Returns:
            list: List of trip dictionaries
        """
        if not self.is_available():
            return []

        try:
            # Filter trips by username
            trips_data = self.filter_sheet_data(self.SHEET_TRIPS, {0: username})

            if not trips_data:
                return []

            # Skip header if present
            if trips_data[0][0] == 'username':
                trips_data = trips_data[1:]

            # Convert to list of dictionaries
            trips = []
            for row in trips_data:
                if len(row) >= 6:
                    trip = {
                        'username': row[0],
                        'date': row[1],
                        'distance': float(row[2]) if row[2] else 0,
                        'duration': float(row[3]) if row[3] else 0,
                        'calories': float(row[4]) if row[4] else 0,
                        'co2_saved': float(row[5]) if row[5] else 0,
                        'route': row[6] if len(row) > 6 else ''
                    }
                    trips.append(trip)

            return trips

        except Exception as e:
            logger.error(f"Error getting trips for user {username}: {e}")
            return []

    def get_trips_in_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get all trips within a date range.

        Args:
            start_date (str): Start date (ISO format: YYYY-MM-DD)
            end_date (str): End date (ISO format: YYYY-MM-DD)

        Returns:
            list: List of trip dictionaries
        """
        if not self.is_available():
            return []

        try:
            # Read all trips
            trips_data = self.read_sheet(self.SHEET_TRIPS)

            if not trips_data:
                return []

            # Parse header if present
            header = trips_data[0] if trips_data[0][0] == 'username' else None
            data_rows = trips_data[1:] if header else trips_data

            # Filter trips by date
            filtered_trips = []
            for row in data_rows:
                if len(row) >= 2:
                    try:
                        # Extract date from timestamp
                        date_str = row[1].split('T')[0] if 'T' in row[1] else row[1]

                        # Check if within range
                        if start_date <= date_str <= end_date:
                            if len(row) >= 6:
                                trip = {
                                    'username': row[0],
                                    'date': row[1],
                                    'distance': float(row[2]) if row[2] else 0,
                                    'duration': float(row[3]) if row[3] else 0,
                                    'calories': float(row[4]) if row[4] else 0,
                                    'co2_saved': float(row[5]) if row[5] else 0,
                                    'route': row[6] if len(row) > 6 else ''
                                }
                                filtered_trips.append(trip)
                    except (ValueError, IndexError):
                        continue

            return filtered_trips

        except Exception as e:
            logger.error(f"Error getting trips in date range {start_date} to {end_date}: {e}")
            return []

    def get_user_stats(self, username: str) -> Dict[str, float]:
        """
        Calculate statistics for a specific user.

        Args:
            username (str): Username to calculate stats for

        Returns:
            dict: Dictionary of user statistics
        """
        if not self.is_available():
            return {}

        try:
            # Get user trips
            trips = self.get_trips_for_user(username)

            if not trips:
                return {
                    'total_trips': 0,
                    'total_distance': 0,
                    'total_duration': 0,
                    'total_calories': 0,
                    'total_co2_saved': 0,
                    'avg_distance': 0,
                    'avg_duration': 0
                }

            # Calculate stats
            total_trips = len(trips)
            total_distance = sum(trip['distance'] for trip in trips)
            total_duration = sum(trip['duration'] for trip in trips)
            total_calories = sum(trip['calories'] for trip in trips)
            total_co2_saved = sum(trip['co2_saved'] for trip in trips)

            # Calculate averages
            avg_distance = total_distance / total_trips if total_trips > 0 else 0
            avg_duration = total_duration / total_trips if total_trips > 0 else 0

            return {
                'total_trips': total_trips,
                'total_distance': total_distance,
                'total_duration': total_duration,
                'total_calories': total_calories,
                'total_co2_saved': total_co2_saved,
                'avg_distance': avg_distance,
                'avg_duration': avg_duration
            }

        except Exception as e:
            logger.error(f"Error calculating stats for user {username}: {e}")
            return {}

    def get_leaderboard(self, metric: str = 'distance', limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get a leaderboard of users ranked by a specific metric.

        Args:
            metric (str): Metric to rank by ('distance', 'duration', 'calories', 'co2_saved', 'trips')
            limit (int): Maximum number of users to include

        Returns:
            list: List of (username, value) tuples
        """
        if not self.is_available():
            return []

        valid_metrics = {
            'distance': 2,
            'duration': 3,
            'calories': 4,
            'co2_saved': 5,
            'trips': 0  # Special case, count trips per user
        }

        if metric not in valid_metrics:
            logger.error(f"Invalid metric: {metric}")
            return []

        try:
            # Read trips data
            trips_data = self.read_sheet(self.SHEET_TRIPS)

            if len(trips_data) <= 1:  # No data or just header
                return []

            # Skip header if present
            if trips_data[0][0] == 'username':
                trips_data = trips_data[1:]

            # Handle 'trips' metric separately (count trips per user)
            if (metric == 'trips'):
                user_counts = {}
                for row in trips_data:
                    username = row[0]
                    if username in user_counts:
                        user_counts[username] += 1
                    else:
                        user_counts[username] = 1

                # Sort users by trip count
                sorted_users = sorted(
                    user_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )

                return sorted_users[:limit]

            # For other metrics, aggregate values per user
            col_idx = valid_metrics[metric]
            user_totals = {}

            for row in trips_data:
                if len(row) <= col_idx:
                    continue

                username = row[0]
                try:
                    value = float(row[col_idx]) if row[col_idx] else 0
                    if username in user_totals:
                        user_totals[username] += value
                    else:
                        user_totals[username] = value
                except ValueError:
                    continue

            # Sort users by total value
            sorted_users = sorted(
                user_totals.items(),
                key=lambda x: x[1],
                reverse=True
            )

            return sorted_users[:limit]

        except Exception as e:
            logger.error(f"Error generating leaderboard for {metric}: {e}")
            return []

    @retry_on_error()
    def apply_conditional_formatting(self, sheet_name: str, range_name: str, formatting_rule: Dict[str, Any]) -> bool:
        """
        Apply conditional formatting to a range in a sheet.

        Args:
            sheet_name (str): Name of the sheet
            range_name (str): Range to apply formatting to (e.g., "A1:C10")
            formatting_rule (dict): Conditional formatting rule.
                Example for gradient: {
                    'type': 'gradient',
                    'minpoint': {'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
                    'midpoint': {'color': {'red': 0.5, 'green': 0.8, 'blue': 0.5}},
                    'maxpoint': {'color': {'red': 0.2, 'green': 0.9, 'blue': 0.2}}
                }
                Example for boolean: {
                    'type': 'boolean',
                    'condition': {'type': 'NUMBER_GREATER', 'values': [{'userEnteredValue': '50'}]},
                    'format': {'backgroundColor': {'red': 0, 'green': 0.7, 'blue': 0}},
                }

        Returns:
            bool: True if formatting was applied successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Get sheet ID
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = None

            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_id = sheet.get('properties', {}).get('sheetId')
                    break

            if sheet_id is None:
                logger.error(f"Sheet {sheet_name} not found")
                return False

            # Build request based on formatting type
            request = {
                'addConditionalFormatRule': {
                    'rule': {
                        'ranges': [
                            {
                                'sheetId': sheet_id,
                                'startRowIndex': 0,
                                'startColumnIndex': 0
                            }
                        ]
                    }
                }
            }

            # Parse range (e.g., "A1:C10")
            if range_name and ':' in range_name:
                start_cell, end_cell = range_name.split(':')
                # Convert A1 notation to row/column indices
                start_col = ord(start_cell[0]) - ord('A')
                start_row = int(start_cell[1:]) - 1
                end_col = ord(end_cell[0]) - ord('A') + 1
                end_row = int(end_cell[1:])

                request['addConditionalFormatRule']['rule']['ranges'][0].update({
                    'startRowIndex': start_row,
                    'endRowIndex': end_row,
                    'startColumnIndex': start_col,
                    'endColumnIndex': end_col
                })

            # Set up formatting rule
            rule_type = formatting_rule.get('type', '')

            if rule_type == 'gradient':
                request['addConditionalFormatRule']['rule']['gradientRule'] = {
                    'minpoint': formatting_rule.get('minpoint', {}),
                    'midpoint': formatting_rule.get('midpoint', {}),
                    'maxpoint': formatting_rule.get('maxpoint', {})
                }
            elif rule_type == 'boolean':
                request['addConditionalFormatRule']['rule']['booleanRule'] = {
                    'condition': formatting_rule.get('condition', {}),
                    'format': formatting_rule.get('format', {})
                }
            else:
                logger.error(f"Unsupported conditional formatting type: {rule_type}")
                return False

            # Apply formatting
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [request]}
            ).execute()

            logger.info(f"Applied {rule_type} conditional formatting to {range_name} in sheet {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error applying conditional formatting to {sheet_name}: {e}")
            return False

    @retry_on_error()
    def set_cell_formatting(self, sheet_name: str, range_name: str, format_properties: Dict[str, Any]) -> bool:
        """
        Set cell formatting for a range in a sheet.

        Args:
            sheet_name (str): Name of the sheet
            range_name (str): Range to format (e.g., "A1:B5")
            format_properties (dict): Formatting properties
                Example: {
                    'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                    'textFormat': {'bold': True, 'fontSize': 12},
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                }

        Returns:
            bool: True if formatting was applied successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Get sheet ID
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = None

            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_id = sheet.get('properties', {}).get('sheetId')
                    break

            if sheet_id is None:
                logger.error(f"Sheet {sheet_name} not found")
                return False

            # Parse range (e.g., "A1:C10")
            if range_name and ':' in range_name:
                start_cell, end_cell = range_name.split(':')
                # Convert A1 notation to row/column indices
                start_col = ord(start_cell[0]) - ord('A')
                start_row = int(start_cell[1:]) - 1
                end_col = ord(end_cell[0]) - ord('A') + 1
                end_row = int(end_cell[1:])

                # Build request
                request = {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': start_row,
                            'endRowIndex': end_row,
                            'startColumnIndex': start_col,
                            'endColumnIndex': end_col
                        },
                        'cell': {
                            'userEnteredFormat': format_properties
                        },
                        'fields': 'userEnteredFormat'
                    }
                }

                # Apply formatting
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': [request]}
                ).execute()

                logger.info(f"Applied formatting to {range_name} in sheet {sheet_name}")
                return True
            else:
                logger.error(f"Invalid range format: {range_name}")
                return False

        except Exception as e:
            logger.error(f"Error setting cell formatting in {sheet_name}: {e}")
            return False

    @retry_on_error()
    def create_chart(self, sheet_name: str, chart_type: str, data_range: str,
                     title: str = "", options: Dict[str, Any] = None) -> bool:
        """
        Create a chart in a sheet.

        Args:
            sheet_name (str): Name of the sheet
            chart_type (str): Type of chart ('BAR', 'LINE', 'PIE', 'COLUMN', 'SCATTER', 'AREA')
            data_range (str): Range containing the data (e.g., "A1:B10")
            title (str): Chart title
            options (dict): Additional chart options

        Returns:
            bool: True if chart was created successfully, False otherwise
        """
        if not self.is_available():
            return False

        # Map chart types to Google Sheets chart specs
        chart_type_map = {
            'BAR': 'BAR',
            'LINE': 'LINE',
            'PIE': 'PIE',
            'COLUMN': 'COLUMN',
            'SCATTER': 'SCATTER',
            'AREA': 'AREA'
        }

        if chart_type not in chart_type_map:
            logger.error(f"Unsupported chart type: {chart_type}")
            return False

        try:
            # Get sheet ID
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = None

            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_id = sheet.get('properties', {}).get('sheetId')
                    break

            if sheet_id is None:
                logger.error(f"Sheet {sheet_name} not found")
                return False

            # Parse data range (e.g., "A1:C10") to get row/column indices
            if ':' in data_range:
                start_cell, end_cell = data_range.split(':')

                # Convert A1 notation to row/column indices
                start_col = ord(start_cell[0]) - ord('A')
                start_row = int(''.join(filter(str.isdigit, start_cell))) - 1

                # Handle multi-letter column references like AA, AB, etc.
                end_col_letters = ''.join(filter(str.isalpha, end_cell)).upper()
                end_col = 0
                for i, char in enumerate(reversed(end_col_letters)):
                    end_col += (ord(char) - ord('A') + 1) * (26 ** i)

                end_row = int(''.join(filter(str.isdigit, end_cell)))

                # Default to using the first column as domain and second column as series
                domain_col_start = start_col
                domain_col_end = domain_col_start + 1
                series_col_start = start_col + 1
                series_col_end = series_col_start + 1

                # If we have multiple columns, use them for multiple series
                if end_col - start_col > 1:
                    series_col_end = end_col
            else:
                logger.error(f"Invalid data range format: {data_range}")
                return False

            # Check if options contains chart positioning
            chart_position = options.get('position', {}) if options else {}
            anchor_cell = chart_position.get('anchor_cell', {'row': 0, 'column': end_col + 1})
            width_pixels = chart_position.get('width', 600)
            height_pixels = chart_position.get('height', 371)

            # Build chart spec based on the chart type
            chart_spec = {
                'title': title
            }

            if chart_type == 'PIE':
                chart_spec['pieChart'] = {
                    'legendPosition': 'BOTTOM_LEGEND',
                    'domain': {
                        'sourceRange': {
                            'sources': [
                                {
                                    'sheetId': sheet_id,
                                    'startRowIndex': start_row,
                                    'endRowIndex': end_row,
                                    'startColumnIndex': domain_col_start,
                                    'endColumnIndex': domain_col_end
                                }
                            ]
                        }
                    },
                    'series': {
                        'sourceRange': {
                            'sources': [
                                {
                                    'sheetId': sheet_id,
                                    'startRowIndex': start_row,
                                    'endRowIndex': end_row,
                                    'startColumnIndex': series_col_start,
                                    'endColumnIndex': series_col_end
                                }
                            ]
                        }
                    }
                }
            else:
                # For all other chart types
                chart_spec['basicChart'] = {
                    'chartType': chart_type_map[chart_type],
                    'legendPosition': 'BOTTOM_LEGEND',
                    'axis': [
                        {
                            'position': 'BOTTOM_AXIS',
                            'title': options.get('x_axis_title', '') if options else ''
                        },
                        {
                            'position': 'LEFT_AXIS',
                            'title': options.get('y_axis_title', '') if options else ''
                        }
                    ],
                    'domains': [
                        {
                            'domain': {
                                'sourceRange': {
                                    'sources': [
                                        {
                                            'sheetId': sheet_id,
                                            'startRowIndex': start_row,
                                            'endRowIndex': end_row,
                                            'startColumnIndex': domain_col_start,
                                            'endColumnIndex': domain_col_end
                                        }
                                    ]
                                }
                            }
                        }
                    ],
                    'series': []
                }

                # Add series for each data column (excluding the domain column)
                for col_idx in range(series_col_start, series_col_end):
                    chart_spec['basicChart']['series'].append({
                        'series': {
                            'sourceRange': {
                                'sources': [
                                    {
                                        'sheetId': sheet_id,
                                        'startRowIndex': start_row,
                                        'endRowIndex': end_row,
                                        'startColumnIndex': col_idx,
                                        'endColumnIndex': col_idx + 1
                                    }
                                ]
                            }
                        },
                        'targetAxis': 'LEFT_AXIS'
                    })

            # Build request
            request = {
                'addChart': {
                    'chart': {
                        'spec': chart_spec,
                        'position': {
                            'overlayPosition': {
                                'anchorCell': {
                                    'sheetId': sheet_id,
                                    'rowIndex': anchor_cell.get('row', 0),
                                    'columnIndex': anchor_cell.get('column', end_col + 1)
                                },
                                'offsetXPixels': 0,
                                'offsetYPixels': 0,
                                'widthPixels': width_pixels,
                                'heightPixels': height_pixels
                            }
                        }
                    }
                }
            }

            # Apply chart
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [request]}
            ).execute()

            logger.info(f"Created {chart_type} chart in sheet {sheet_name} using data range {data_range}")
            return True

        except Exception as e:
            logger.error(f"Error creating chart in {sheet_name}: {e}")
            return False

    @retry_on_error()
    def insert_formulas(self, sheet_name: str, formulas: Dict[str, str]) -> bool:
        """
        Insert formulas into cells in a sheet.

        Args:
            sheet_name (str): Name of the sheet
            formulas (dict): Dictionary mapping cell references to formulas
                Example: {'D2': '=SUM(A2:C2)', 'D3': '=AVERAGE(A3:C3)'}

        Returns:
            bool: True if formulas were inserted successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Get all cells with formulas
            data = []
            for cell_ref, formula in formulas.items():
                # Convert cell reference to row/column
                col_name = ''.join(filter(str.isalpha, cell_ref))
                row_num = int(''.join(filter(str.isdigit, cell_ref)))

                # Calculate range in A1 notation
                cell_range = f"{sheet_name}!{cell_ref}"

                # Add to data
                data.append({
                    'range': cell_range,
                    'values': [[formula]]
                })

            # Update cells with formulas
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    'valueInputOption': 'USER_ENTERED',  # Important: this makes Google Sheets interpret formulas
                    'data': data
                }
            ).execute()

            logger.info(f"Inserted {len(formulas)} formulas into sheet {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error inserting formulas into {sheet_name}: {e}")
            return False

    @retry_on_error()
    def apply_data_validation(self, sheet_name: str, range_name: str, validation_rule: Dict[str, Any]) -> bool:
        """
        Apply data validation to a range in a sheet.

        Args:
            sheet_name (str): Name of the sheet
            range_name (str): Range to apply validation to (e.g., "A1:A10")
            validation_rule (dict): Data validation rule.
                Examples:
                - List validation: {'type': 'list', 'values': ['Bike', 'Walk', 'Public Transit']}
                - Number validation: {'type': 'number', 'condition': 'BETWEEN', 'min': 0, 'max': 100}
                - Custom formula: {'type': 'custom', 'formula': '=LEN(A1)>5'}

        Returns:
            bool: True if validation was applied successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Get sheet ID
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = None

            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_id = sheet.get('properties', {}).get('sheetId')
                    break

            if sheet_id is None:
                logger.error(f"Sheet {sheet_name} not found")
                return False

            # Parse range (e.g., "A1:A10")
            if range_name and ':' in range_name:
                start_cell, end_cell = range_name.split(':')
                # Convert A1 notation to row/column indices
                start_col = ord(start_cell[0]) - ord('A')
                start_row = int(start_cell[1:]) - 1
                end_col = ord(end_cell[0]) - ord('A') + 1
                end_row = int(end_cell[1:])
            else:
                # Single cell
                start_col = ord(range_name[0]) - ord('A')
                start_row = int(range_name[1:]) - 1
                end_col = start_col + 1
                end_row = start_row + 1

            # Build validation rule
            validation_type = validation_rule.get('type', '')
            validation = {}

            if validation_type == 'list':
                values = validation_rule.get('values', [])
                validation = {
                    'condition': {
                        'type': 'ONE_OF_LIST',
                        'values': [{'userEnteredValue': value} for value in values]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            elif validation_type == 'number':
                condition = validation_rule.get('condition', '')
                if condition == 'BETWEEN':
                    min_val = validation_rule.get('min', 0)
                    max_val = validation_rule.get('max', 100)
                    validation = {
                        'condition': {
                            'type': 'NUMBER_BETWEEN',
                            'values': [
                                {'userEnteredValue': str(min_val)},
                                {'userEnteredValue': str(max_val)}
                            ]
                        },
                        'showCustomUi': True,
                        'strict': True
                    }
                elif condition in ('GREATER', 'LESS'):
                    value = validation_rule.get('value', 0)
                    validation = {
                        'condition': {
                            'type': f'NUMBER_{condition}',
                            'values': [
                                {'userEnteredValue': str(value)}
                            ]
                        },
                        'showCustomUi': True,
                        'strict': True
                    }
            elif validation_type == 'custom':
                formula = validation_rule.get('formula', '')
                validation = {
                    'condition': {
                        'type': 'CUSTOM_FORMULA',
                        'values': [{'userEnteredValue': formula}]
                    },
                    'showCustomUi': True,
                    'strict': True
                }
            else:
                logger.error(f"Unsupported validation type: {validation_type}")
                return False

            # Apply validation
            request = {
                'setDataValidation': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': start_row,
                        'endRowIndex': end_row,
                        'startColumnIndex': start_col,
                        'endColumnIndex': end_col
                    },
                    'rule': validation
                }
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [request]}
            ).execute()

            logger.info(f"Applied {validation_type} validation to {range_name} in sheet {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error applying data validation to {sheet_name}: {e}")
            return False

    def create_team(self, team_name: str, members: List[str], team_data: Dict[str, Any] = None) -> bool:
        """
        Create or update a team.

        Args:
            team_name (str): Name of the team
            members (list): List of usernames in the team
            team_data (dict): Additional team data

        Returns:
            bool: True if the team was created successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Read existing teams
            teams_data = self.read_sheet(self.SHEET_TEAMS)

            # Check if teams sheet has header
            if not teams_data:
                # Create header row
                header = ['team_name', 'members', 'team_data']
                teams_data = [header]

            # Check if team exists
            team_exists = False
            team_index = -1

            for i, row in enumerate(teams_data):
                if i == 0:  # Skip header
                    continue

                if len(row) >= 1 and row[0] == team_name:
                    team_exists = True
                    team_index = i
                    break

            # Format team data
            team_row = [
                team_name,
                json.dumps(members),
                json.dumps(team_data or {})
            ]

            # Update or append team
            if team_exists:
                teams_data[team_index] = team_row
                success = self.write_sheet(self.SHEET_TEAMS, teams_data)
            else:
                success = self.append_to_sheet(self.SHEET_TEAMS, [team_row])

            if success:
                logger.info(f"Team '{team_name}' with {len(members)} members saved successfully")

            return success

        except Exception as e:
            logger.error(f"Error creating team {team_name}: {e}")
            return False

    def get_teams(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all teams.

        Returns:
            dict: Dictionary of teams, where each key is a team name and each value is a team dict
        """
        if not self.is_available():
            return {}

        try:
            # Read teams sheet
            rows = self.read_sheet(self.SHEET_TEAMS)

            if not rows:
                logger.info("No teams found")
                return {}

            # Convert rows to teams dict
            teams = {}
            for row in rows[1:]:  # Skip header row
                if len(row) >= 3:
                    team_name = row[0]

                    try:
                        members = json.loads(row[1])
                        team_data = json.loads(row[2]) if len(row) > 2 else {}

                        teams[team_name] = {
                            'name': team_name,
                            'members': members,
                            **team_data
                        }
                    except json.JSONDecodeError:
                        logger.error(f"Error decoding team data for {team_name}")

            logger.info(f"Loaded {len(teams)} teams")
            return teams

        except Exception as e:
            logger.error(f"Error getting teams: {e}")
            return {}

    def get_team_stats(self, team_name: str) -> Dict[str, float]:
        """
        Calculate statistics for a team.

        Args:
            team_name (str): Team name

        Returns:
            dict: Dictionary of team statistics
        """
        if not self.is_available():
            return {}

        try:
            # Get team members
            teams = self.get_teams()
            if (team_name) not in teams:
                logger.error(f"Team {team_name} not found")
                return {}

            members = teams[team_name].get('members', [])

            if not members:
                logger.warning(f"No members in team {team_name}")
                return {
                    'total_users': 0,
                    'total_trips': 0,
                    'total_distance': 0,
                    'total_duration': 0,
                    'total_calories': 0,
                    'total_co2_saved': 0,
                    'avg_distance_per_user': 0,
                    'avg_trips_per_user': 0
                }

            # Get stats for each member
            member_stats = {member: self.get_user_stats(member) for member in members}

            # Calculate team totals
            total_users = len([user for user, stats in member_stats.items() if stats])
            total_trips = sum(stats.get('total_trips', 0) for stats in member_stats.values() if stats)
            total_distance = sum(stats.get('total_distance', 0) for stats in member_stats.values() if stats)
            total_duration = sum(stats.get('total_duration', 0) for stats in member_stats.values() if stats)
            total_calories = sum(stats.get('total_calories', 0) for stats in member_stats.values() if stats)
            total_co2_saved = sum(stats.get('total_co2_saved', 0) for stats in member_stats.values() if stats)

            # Calculate averages
            avg_distance_per_user = total_distance / total_users if total_users > 0 else 0
            avg_trips_per_user = total_trips / total_users if total_users > 0 else 0

            return {
                'total_users': total_users,
                'total_trips': total_trips,
                'total_distance': total_distance,
                'total_duration': total_duration,
                'total_calories': total_calories,
                'total_co2_saved': total_co2_saved,
                'avg_distance_per_user': avg_distance_per_user,
                'avg_trips_per_user': avg_trips_per_user
            }

        except Exception as e:
            logger.error(f"Error calculating stats for team {team_name}: {e}")
            return {}

    def get_team_leaderboard(self, metric: str = 'distance', limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get a leaderboard of teams ranked by a specific metric.

        Args:
            metric (str): Metric to rank by ('distance', 'duration', 'calories', 'co2_saved', 'trips')
            limit (int): Maximum number of teams to include

        Returns:
            list: List of (team_name, value) tuples
        """
        if not self.is_available():
            return []

        try:
            # Get all teams
            teams = self.get_teams()

            if not teams:
                return []

            # Get stats for each team
            team_stats = {name: self.get_team_stats(name) for name in teams.keys()}

            # Map metrics to stat keys
            metric_map = {
                'distance': 'total_distance',
                'duration': 'total_duration',
                'calories': 'total_calories',
                'co2_saved': 'total_co2_saved',
                'trips': 'total_trips',
                'users': 'total_users'
            }

            if metric not in metric_map:
                logger.error(f"Invalid metric: {metric}")
                return []

            # Get values for each team
            stat_key = metric_map[metric]
            team_values = [(name, stats.get(stat_key, 0)) for name, stats in team_stats.items()]

            # Sort teams by value
            sorted_teams = sorted(team_values, key=lambda x: x[1], reverse=True)

            return sorted_teams[:limit]

        except Exception as e:
            logger.error(f"Error generating team leaderboard for {metric}: {e}")
            return []

    @retry_on_error()
    def batch_update_cells(self, updates: List[Tuple[str, str, Any]]) -> bool:
        """
        Update multiple cells across sheets in a single batch operation.

        Args:
            updates (list): List of (sheet_name, cell_ref, value) tuples

        Returns:
            bool: True if all cells were updated successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Group updates by sheet
            sheet_updates = {}
            for sheet_name, cell_ref, value in updates:
                if sheet_name not in sheet_updates:
                    sheet_updates[sheet_name] = {}

                sheet_updates[sheet_name][cell_ref] = value

            # Prepare data for batch update
            data = []
            for sheet_name, cell_updates in sheet_updates.items():
                # Ensure sheet exists
                if not self.get_or_create_sheet(sheet_name):
                    logger.error(f"Failed to get or create sheet {sheet_name}")
                    return False

                # Group updates by range where possible
                # For simplicity, we'll treat each cell update separately for now
                for cell_ref, value in cell_updates.items():
                    cell_range = f"{sheet_name}!{cell_ref}"

                    # Convert value to list of lists for API
                    cell_value = [[value]]

                    data.append({
                        'range': cell_range,
                        'values': cell_value
                    })

            # Execute batch update
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    'valueInputOption': 'USER_ENTERED',
                    'data': data
                }
            ).execute()

            logger.info(f"Updated {len(updates)} cells in batch operation")
            return True

        except Exception as e:
            logger.error(f"Error in batch update: {e}")
            return False

    @retry_on_error()
    def batch_append_rows(self, append_data: Dict[str, List[List[Any]]]) -> bool:
        """
        Append rows to multiple sheets in a single batch operation.

        Args:
            append_data (dict): Dictionary mapping sheet names to lists of rows

        Returns:
            bool: True if all rows were appended successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Prepare batch requests
            batch_requests = []

            for sheet_name, rows in append_data.items():
                # Ensure sheet exists
                if not self.get_or_create_sheet(sheet_name):
                    logger.error(f"Failed to get or create sheet {sheet_name}")
                    return False

                # Create append request
                batch_requests.append({
                    'spreadsheetId': self.spreadsheet_id,
                    'range': sheet_name,
                    'valueInputOption': 'USER_ENTERED',
                    'insertDataOption': 'INSERT_ROWS',
                    'body': {'values': rows}
                })

            # Execute batch requests
            for request in batch_requests:
                self.service.spreadsheets().values().append(**request).execute()

            total_rows = sum(len(rows) for rows in append_data.values())
            logger.info(f"Appended {total_rows} rows across {len(append_data)} sheets in batch operation")
            return True

        except Exception as e:
            logger.error(f"Error in batch append: {e}")
            return False

    @retry_on_error()
    def create_spreadsheet(self, title: str, sheets: List[str] = None) -> Optional[str]:
        """
        Create a new spreadsheet.

        Args:
            title (str): Title of the spreadsheet
            sheets (list): List of sheet names to create

        Returns:
            str: ID of the created spreadsheet, or None if creation failed
        """
        if not self.is_available():
            return None

        if not self.drive_service:
            logger.error("Google Drive API is not initialized")
            return None

        try:
            # Prepare sheet data
            sheet_properties = []

            if sheets:
                for sheet_name in sheets:
                    sheet_properties.append({
                        'properties': {
                            'title': sheet_name
                        }
                    })

            # Create spreadsheet
            spreadsheet_body = {
                'properties': {
                    'title': title
                }
            }

            if sheet_properties:
                spreadsheet_body['sheets'] = sheet_properties

            response = self.service.spreadsheets().create(body=spreadsheet_body).execute()
            spreadsheet_id = response.get('spreadsheetId')

            logger.info(f"Created spreadsheet '{title}' with ID: {spreadsheet_id}")
            return spreadsheet_id

        except Exception as e:
            logger.error(f"Error creating spreadsheet '{title}': {e}")
            return None

    @retry_on_error()
    def delete_sheet(self, sheet_name: str) -> bool:
        """
        Delete a sheet from the current spreadsheet.

        Args:
            sheet_name (str): Name of the sheet to delete

        Returns:
            bool: True if the sheet was deleted successfully, False otherwise
        """
        if not self.is_available():
            return False

        try:
            # Get sheet ID
            spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = None

            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_id = sheet.get('properties', {}).get('sheetId')
                    break

            if sheet_id is None:
                logger.error(f"Sheet {sheet_name} not found")
                return False

            # Delete sheet
            request = {
                'deleteSheet': {
                    'sheetId': sheet_id
                }
            }

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [request]}
            ).execute()

            logger.info(f"Deleted sheet {sheet_name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting sheet {sheet_name}: {e}")
            return False

    @retry_on_error()
    def share_spreadsheet(self, email: str, role: str = 'reader', notify: bool = False, message: str = '') -> bool:
        """
        Share the current spreadsheet with a user.

        Args:
            email (str): Email address of the user to share with
            role (str): Access role ('reader', 'writer', 'commenter', 'owner')
            notify (bool): Whether to send notification email
            message (str): Message to include in notification email

        Returns:
            bool: True if the spreadsheet was shared successfully, False otherwise
        """
        if not self.is_available() or not self.drive_service:
            return False

        # Map roles to Google Drive API roles
        role_map = {
            'reader': 'reader',
            'writer': 'writer',
            'commenter': 'commenter',
            'owner': 'owner'
        }

        if role not in role_map:
            logger.error(f"Invalid role: {role}")
            return False

        try:
            # Create permission
            user_permission = {
                'type': 'user',
                'role': role_map[role],
                'emailAddress': email
            }

            self.drive_service.permissions().create(
                fileId=self.spreadsheet_id,
                body=user_permission,
                sendNotificationEmail=notify,
                emailMessage=message if notify else None
            ).execute()

            logger.info(f"Shared spreadsheet with {email} as {role}")
            return True

        except Exception as e:
            logger.error(f"Error sharing spreadsheet with {email}: {e}")
            return False

    def export_sheet_to_csv(self, sheet_name: str) -> Optional[str]:
        """
        Export a sheet to CSV format.

        Args:
            sheet_name (str): Name of the sheet to export

        Returns:
            str: CSV content, or None if export failed
        """
        if not self.is_available():
            return None

        try:
            # Read sheet data
            rows = self.read_sheet(sheet_name)

            if not rows:
                logger.warning(f"No data in sheet {sheet_name}")
                return ""

            # Convert to CSV
            csv_lines = []
            for row in rows:
                # Escape commas and quotes in values
                escaped_values = []
                for value in row:
                    value_str = str(value)
                    if '"' in value_str or ',' in value_str or '\n' in value_str:
                        # Double the quotes for proper CSV escaping
                        escaped_value = value_str.replace('"', '""')
                        escaped_values.append(f'"{escaped_value}"')
                    else:
                        escaped_values.append(value_str)

                csv_lines.append(','.join(escaped_values))

            csv_content = '\n'.join(csv_lines)

            logger.info(f"Exported {len(rows)} rows from sheet {sheet_name} to CSV")
            return csv_content

        except Exception as e:
            logger.error(f"Error exporting sheet {sheet_name} to CSV: {e}")
            return None

    def generate_monthly_report(self, month: int, year: int) -> Dict[str, Any]:
        """
        Generate a monthly report with trip statistics.

        Args:
            month (int): Month number (1-12)
            year (int): Year (e.g., 2023)

        Returns:
            dict: Report data
        """
        if not self.is_available():
            return {}

        try:
            # Input validation
            if not isinstance(month, int) or not isinstance(year, int):
                logger.error(f"Invalid month or year: month={month}, year={year}")
                return {}

            if month < 1 or month > 12:
                logger.error(f"Invalid month: {month}. Month must be between 1 and 12.")
                return {}

            # Define date range for the month
            start_date = f"{year}-{month:02d}-01"

            # Get the last day of the month
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year

            end_date = f"{next_year}-{next_month:02d}-01"

            # Get trips in date range
            trips = self.get_trips_in_date_range(start_date, end_date)

            if not trips:
                logger.warning(f"No trips found for {year}-{month:02d}")
                return {
                    'month': month,
                    'year': year,
                    'total_trips': 0,
                    'total_users': 0,
                    'total_distance': 0,
                    'total_duration': 0,
                    'total_calories': 0,
                    'total_co2_saved': 0,
                    'user_stats': {},
                    'day_stats': {},
                    'average_trip_distance': 0,
                    'average_trip_duration': 0
                }

            # Calculate overall stats
            total_trips = len(trips)
            unique_users = len(set(trip['username'] for trip in trips))
            total_distance = sum(trip['distance'] for trip in trips)
            total_duration = sum(trip['duration'] for trip in trips)
            total_calories = sum(trip['calories'] for trip in trips)
            total_co2_saved = sum(trip['co2_saved'] for trip in trips)

            # Calculate averages
            average_trip_distance = total_distance / total_trips if total_trips > 0 else 0
            average_trip_duration = total_duration / total_trips if total_trips > 0 else 0
            average_trip_co2_saved = total_co2_saved / total_trips if total_trips > 0 else 0

            # Calculate user stats
            user_stats = {}
            for trip in trips:
                username = trip['username']

                if username not in user_stats:
                    user_stats[username] = {
                        'trips': 0,
                        'distance': 0,
                        'duration': 0,
                        'calories': 0,
                        'co2_saved': 0
                    }

                user_stats[username]['trips'] += 1
                user_stats[username]['distance'] += trip['distance']
                user_stats[username]['duration'] += trip['duration']
                user_stats[username]['calories'] += trip['calories']
                user_stats[username]['co2_saved'] += trip['co2_saved']

            # Calculate day stats
            day_stats = {}
            for trip in trips:
                # Extract day from date
                day = trip['date'].split('T')[0] if 'T' in trip['date'] else trip['date']

                if day not in day_stats:
                    day_stats[day] = {
                        'trips': 0,
                        'distance': 0,
                        'duration': 0,
                        'calories': 0,
                        'co2_saved': 0
                    }

                day_stats[day]['trips'] += 1
                day_stats[day]['distance'] += trip['distance']
                day_stats[day]['duration'] += trip['duration']
                day_stats[day]['calories'] += trip['calories']
                day_stats[day]['co2_saved'] += trip['co2_saved']

            # Create report
            report = {
                'month': month,
                'year': year,
                'total_trips': total_trips,
                'total_users': unique_users,
                'total_distance': total_distance,
                'total_duration': total_duration,
                'total_calories': total_calories,
                'total_co2_saved': total_co2_saved,
                'average_trip_distance': average_trip_distance,
                'average_trip_duration': average_trip_duration,
                'average_trip_co2_saved': average_trip_co2_saved,
                'user_stats': user_stats,
                'day_stats': day_stats,
                'report_generated_at': datetime.now().isoformat(),
                'report_id': f"{year}-{month:02d}-{hash(str(datetime.now()))}",
            }

            logger.info(f"Generated report for {year}-{month:02d} with {total_trips} trips")
            return report

        except Exception as e:
            logger.error(f"Error generating report for {year}-{month:02d}: {e}")
            return {}

    def batch_get_values(self, ranges: List[str]) -> Dict[str, List[List[str]]]:
        """
        Get values from multiple ranges in a single batch operation.

        Args:
            ranges (list): List of range strings in A1 notation (e.g., "Sheet1!A1:B10")

        Returns:
            dict: Dictionary mapping range strings to lists of rows
        """
        if not self.is_available():
            return {}

        try:
            # Execute batch get
            result = self.service.spreadsheets().values().batchGet(
                spreadsheetId=self.spreadsheet_id,
                ranges=ranges
            ).execute()

            # Process results
            value_ranges = result.get('valueRanges', [])
            results = {}

            for i, value_range in enumerate(value_ranges):
                range_str = value_range.get('range')
                values = value_range.get('values', [])
                results[ranges[i]] = values

            logger.info(f"Retrieved data from {len(ranges)} ranges in batch operation")
            return results

        except Exception as e:
            logger.error(f"Error in batch get: {e}")
            return {}

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test SheetsManager
    sheets_manager = SheetsManager()

    if sheets_manager.is_available():
        print("Google Sheets integration is available!")

        # Test reading and writing
        test_data = [
            ['Name', 'Age', 'City'],
            ['Alice', '28', 'New York'],
            ['Bob', '35', 'Los Angeles'],
            ['Charlie', '42', 'Chicago']
        ]

        if sheets_manager.write_sheet('test', test_data):
            print("Test data written successfully")

            read_data = sheets_manager.read_sheet('test')
            print("Read data:", read_data)

        # Test user operations
        test_users = {
            'user1': {
                'username': 'user1',
                'name': 'Test User 1',
                'email': 'user1@example.com',
                'stats': {
                    'total_trips': 5,
                    'total_distance': 25.5,
                    'total_co2_saved': 5.87,
                    'total_calories': 750
                }
            },
            'user2': {
                'username': 'user2',
                'name': 'Test User 2',
                'email': 'user2@example.com',
                'stats': {
                    'total_trips': 3,
                    'total_distance': 15.2,
                    'total_co2_saved': 3.5,
                    'total_calories': 450
                }
            }
        }

        if sheets_manager.save_users(test_users):
            print("Test users saved successfully")

            users = sheets_manager.get_users()
            print(f"Read {len(users)} users")

        # Test trip logging
        trip = {
            'date': '2023-04-01T12:34:56',
            'distance': 10.5,
            'duration': 45,
            'calories': 300,
            'co2_saved': 2.42
        }

        if sheets_manager.log_trip('user1', trip):
            print("Trip logged successfully")
    else:
        print("Google Sheets integration is not available")
        print("Make sure you have set the GOOGLE_APPLICATION_CREDENTIALS and ECOCYCLE_SPREADSHEET_ID environment variables")
