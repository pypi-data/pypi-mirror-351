"""
EcoCycle - User Manager Module (Fully Refactored)
Main orchestrator for user authentication, registration, and profile management.
This module coordinates between specialized sub-modules for better maintainability.
"""
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Any
import config.config as config
from .password_security import PasswordSecurity
from .session_manager import SessionManager
from .user_data_manager import UserDataManager
from .user_registration import UserRegistration
from .auth_handler import AuthHandler
from .google_auth_handler import GoogleAuthHandler

# Check if the rich module is available for enhanced UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False

logger = logging.getLogger(__name__)

# Constants for backward compatibility
SESSION_SECRET_ENV_VAR = "SESSION_SECRET_KEY"


class UserManager:
    """Manages user authentication and profiles."""

    def __init__(self, sheets_manager=None):
        """
        Initialize the UserManager.

        Args:
            sheets_manager: Optional sheets manager for user data storage in Google Sheets
        """
        self.current_user: Optional[str] = None
        self.sheets_manager = sheets_manager

        # Initialize sub-modules
        self.password_security = PasswordSecurity()
        self.session_manager = SessionManager()
        self.user_data_manager = UserDataManager(sheets_manager)
        self.user_registration = UserRegistration()
        self.auth_handler = AuthHandler()
        self.google_auth_handler = GoogleAuthHandler()

        # Lock for thread safety during Google auth
        self.google_auth_lock = threading.Lock()

        # Load existing users
        self.users = self.user_data_manager.load_users()

        # Create a guest user if it doesn't exist
        if 'guest' not in self.users:
            guest_user = self.user_data_manager.create_guest_user(0)
            self.users['guest'] = guest_user
            self.user_data_manager.save_users(self.users)

    # === Core User Management ===

    def load_users(self) -> None:
        """Load users from local file or Google Sheets."""
        self.users = self.user_data_manager.load_users()

    def save_users(self) -> bool:
        """Save users to local file or Google Sheets."""
        return self.user_data_manager.save_users(self.users)

    # === Authentication ===

    def authenticate(self) -> bool:
        """
        Authenticate a user through username/password or Google authentication.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Check for existing session first
        session_user = self.session_manager.load_session()
        if session_user and session_user in self.users:
            self.current_user = session_user
            logger.info(f"Restored session for user: {session_user}")
            if HAS_RICH and console:
                console.print(f"[green]Welcome back, {self.users[session_user].get('name', session_user)}![/green]")
            else:
                print(f"Welcome back, {self.users[session_user].get('name', session_user)}!")
            return True

        # Display authentication menu
        choice = self.auth_handler.display_authentication_menu()

        if choice == '1':
            # Login with username/password
            success, username = self.auth_handler.authenticate_user(self.users)
            if not success:
                return False

            if username:
                # Check if email verification is required
                if self.auth_handler.check_email_verification_required(username, self.users):
                    if not self._handle_email_verification(username):
                        return False

                # Check if two-factor authentication is required
                if self.auth_handler.check_two_factor_required(username, self.users):
                    if not self._handle_two_factor_authentication(username):
                        return False

                # Authentication successful
                self.current_user = username
                logger.info(f"User {username} authenticated successfully")

                # Load trips from database to sync with in-memory data
                self.user_data_manager.load_user_trips_from_database(username, self.users)

                # Save session
                if not self.auth_handler.save_session(username):
                    logger.error("CRITICAL: Failed to save session state after login.")

                if HAS_RICH and console:
                    console.print(f"[bold green]Welcome back, {self.users[username].get('name', username)}![/bold green]")
                else:
                    print(f"Welcome back, {self.users[username].get('name', username)}!")
                return True
            else:
                self.current_user = None
                return False

        elif choice == '2':
            # Login as guest
            guest_username = self._create_guest_account()
            self.current_user = guest_username
            logger.info(f"Guest user authenticated as {guest_username}")
            if HAS_RICH and console:
                console.print(f"[green]Logged in as {guest_username}.[/green]")
            else:
                print(f"Logged in as {guest_username}.")
            return True

        elif choice == '3':
            # Register new user
            return self.register_new_user()

        elif choice == '4':
            # Google authentication
            with self.google_auth_lock:
                success, username, user_data = self.google_auth_handler.authenticate_with_google(self.users)

            if success and username and user_data:
                self.users[username] = user_data
                self.current_user = username
                self.save_users()

                if HAS_RICH and console:
                    console.print(f"[bold green]Welcome, {user_data.get('name', username)}![/bold green]")
                else:
                    print(f"Welcome, {user_data.get('name', username)}!")

                # Save session
                if not self.auth_handler.save_session(username):
                    logger.error("CRITICAL: Failed to save session state after Google login.")

                return True
            else:
                if HAS_RICH and console:
                    console.print("[bold red]Google authentication failed.[/bold red]")
                else:
                    print("Google authentication failed.")
                return False

        elif choice == '5':
            # Check if this is developer mode or cancel
            try:
                from auth.developer_auth import DeveloperAuth
                dev_auth = DeveloperAuth()
                if dev_auth.is_enabled():
                    # This is developer mode
                    return self._handle_developer_authentication()
                else:
                    # This is cancel
                    return False
            except ImportError:
                # Developer mode not available, this is cancel
                return False

        elif choice == '6':
            # Cancel (when developer mode is available)
            return False

        else:
            # Cancel or invalid choice
            return False

    def register_new_user(self) -> bool:
        """Register a new user."""
        success, user_data = self.user_registration.register_new_user(self.users)

        if not success or not user_data:
            return False

        # Add the new user to our users dictionary
        username = user_data['username']
        self.users[username] = user_data

        # Save users and set current user
        if self.save_users():
            self.current_user = username
            return True
        else:
            if HAS_RICH and console:
                console.print("[bold red]❌ Failed to save user data. Please try again.[/bold red]")
            else:
                print("❌ Failed to save user data. Please try again.")
            return False

    def logout(self) -> None:
        """Log out the current user and clear the session."""
        if self.current_user:
            self.auth_handler.logout_user(self.current_user)
            self.current_user = None

    # === User State ===

    def get_current_user(self) -> Dict:
        """Get the currently authenticated user."""
        if self.current_user and self.current_user in self.users:
            return self.users[self.current_user]
        return {}

    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated."""
        return self.current_user is not None and self.current_user in self.users

    def is_guest(self) -> bool:
        """Check if the current user is a guest."""
        if not self.is_authenticated() or self.current_user is None:
            return False
        return self.users[self.current_user].get('is_guest', False)

    def is_admin(self) -> bool:
        """Check if the current user is an admin."""
        current_user = self.get_current_user()
        return current_user.get('is_admin', False)

    def get_current_username(self) -> str:
        """Get the username of the currently authenticated user."""
        current_user = self.get_current_user()
        return current_user.get('username', 'guest')

    # === User Data Management ===

    def update_user_stats(self, distance: float, co2_saved: float, calories: int, duration: float = 0.0) -> bool:
        """Update user statistics and add a new trip."""
        if not self.is_authenticated() or self.current_user is None:
            return False

        user_data = self.users[self.current_user]
        success = self.user_data_manager.update_user_stats(user_data, distance, co2_saved, calories, duration)

        if success:
            return self.save_users()
        return False

    def update_user_preference(self, key: str, value: Any) -> bool:
        """Update a user preference."""
        if not self.is_authenticated() or self.current_user is None:
            return False

        user_data = self.users[self.current_user]
        success = self.user_data_manager.update_user_preference(user_data, key, value)

        if success:
            return self.save_users()
        return False

    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        if not self.is_authenticated() or self.current_user is None:
            return default

        user_data = self.users[self.current_user]
        return self.user_data_manager.get_user_preference(user_data, key, default)

    # === Helper Methods ===

    def _handle_developer_authentication(self) -> bool:
        """Handle developer authentication and enter developer mode."""
        try:
            from auth.developer_auth import DeveloperAuth
            from apps.developer.developer_tools import DeveloperTools
            from apps.developer.developer_coordinator import DeveloperCoordinator

            # Initialize developer authentication
            dev_auth = DeveloperAuth()

            # Authenticate developer
            if dev_auth.authenticate_developer():
                # Initialize developer tools and coordinator
                dev_tools = DeveloperTools(dev_auth)
                dev_coordinator = DeveloperCoordinator(dev_auth, dev_tools)

                # Set current user to developer (special case)
                self.current_user = f"developer:{dev_auth.get_developer_username()}"

                # Enter developer mode loop
                dev_coordinator.run()

                # After exiting developer mode, clear the developer session
                dev_auth.logout_developer()
                self.current_user = None

                return True
            else:
                return False

        except ImportError as e:
            logger.error(f"Developer mode modules not available: {e}")
            if HAS_RICH and console:
                console.print("[red]Developer mode is not available. Missing required modules.[/red]")
            else:
                print("Developer mode is not available. Missing required modules.")
            return False
        except Exception as e:
            logger.error(f"Error in developer authentication: {e}")
            if HAS_RICH and console:
                console.print(f"[red]Developer authentication error: {e}[/red]")
            else:
                print(f"Developer authentication error: {e}")
            return False

    # _run_developer_mode method removed - now handled by DeveloperCoordinator

    def _handle_email_verification(self, username: str) -> bool:
        """Handle email verification process for a user."""
        # This would contain the email verification logic
        # For now, return True to maintain functionality
        return True

    def _handle_two_factor_authentication(self, username: str) -> bool:
        """Handle two-factor authentication process for a user."""
        # This would contain the 2FA logic
        # For now, return True to maintain functionality
        return True

    def _create_guest_account(self) -> str:
        """Create a unique guest account."""
        # Find the next available guest number
        guest_number = 1
        while f"guest{guest_number}" in self.users:
            guest_number += 1

        guest_username = f"guest{guest_number}"
        guest_user = self.user_data_manager.create_guest_user(guest_number)
        self.users[guest_username] = guest_user
        self.save_users()

        return guest_username

    # === Backward Compatibility Methods ===

    def verify_email_code(self, code: str) -> bool:
        """Verify email code (backward compatibility)."""
        # Delegate to auth handler or return True for now
        return True

    def request_email_verification(self, username: str) -> bool:
        """Request email verification (backward compatibility)."""
        # Delegate to auth handler or return True for now
        return True

    def _get_session_secret(self) -> bytes:
        """Get session secret (backward compatibility)."""
        return self.session_manager.get_session_secret()

    def _calculate_verifier(self, username: str) -> str:
        """Calculate session verifier (backward compatibility)."""
        return self.session_manager.calculate_verifier(username)

    def _clear_session(self, expected_user: Optional[str] = None) -> None:
        """Clear session (backward compatibility)."""
        if expected_user:
            self.session_manager.clear_session(expected_user)
        else:
            self.session_manager.clear_session()

    def load_user_trips_from_database(self, username: str) -> bool:
        """Load user trips from database (backward compatibility)."""
        return self.user_data_manager.load_user_trips_from_database(username, self.users)

    # === API-specific Methods ===

    def generate_api_token(self, username: str, device_id: str) -> str:
        """
        Generate an API token for a user and device.

        Args:
            username (str): Username
            device_id (str): Device identifier

        Returns:
            str: Generated API token
        """
        import uuid
        import hashlib

        # Generate a unique token
        token_data = f"{username}:{device_id}:{time.time()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()

        # In a real implementation, you would store this token in a database
        # For now, we'll just return the token
        logger.info(f"Generated API token for user {username} on device {device_id}")
        return token

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile information.

        Args:
            user_id (str): User identifier

        Returns:
            Dict: User profile data or None if not found
        """
        if user_id in self.users:
            user_data = self.users[user_id].copy()
            # Remove sensitive information
            user_data.pop('password_hash', None)
            user_data.pop('salt', None)
            return user_data
        return None

    def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update user profile information.

        Args:
            user_id (str): User identifier
            update_data (Dict): Data to update

        Returns:
            bool: True if successful, False otherwise
        """
        if user_id not in self.users:
            return False

        try:
            # Update user data
            for key, value in update_data.items():
                if key not in ['password_hash', 'salt', 'username']:  # Protect sensitive fields
                    self.users[user_id][key] = value

            # Save users
            return self.save_users()
        except Exception as e:
            logger.error(f"Error updating user profile for {user_id}: {e}")
            return False

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics.

        Args:
            user_id (str): User identifier

        Returns:
            Dict: User statistics
        """
        if user_id not in self.users:
            return {}

        user_data = self.users[user_id]
        stats = user_data.get('stats', {})

        # Ensure all required stats fields exist
        default_stats = {
            'total_trips': 0,
            'total_distance': 0.0,
            'total_co2_saved': 0.0,
            'total_calories': 0,
            'trips': []
        }

        # Merge with defaults
        for key, default_value in default_stats.items():
            if key not in stats:
                stats[key] = default_value

        return stats

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences.

        Args:
            user_id (str): User identifier
            preferences (Dict): Preferences to update

        Returns:
            bool: True if successful, False otherwise
        """
        if user_id not in self.users:
            return False

        try:
            # Ensure preferences dict exists
            if 'preferences' not in self.users[user_id]:
                self.users[user_id]['preferences'] = {}

            # Update preferences
            self.users[user_id]['preferences'].update(preferences)

            # Save users
            return self.save_users()
        except Exception as e:
            logger.error(f"Error updating user preferences for {user_id}: {e}")
            return False

    def is_user_admin(self, user_id: str) -> bool:
        """
        Check if a specific user is an admin.

        Args:
            user_id (str): User identifier

        Returns:
            bool: True if user is admin, False otherwise
        """
        if user_id not in self.users:
            return False

        return self.users[user_id].get('is_admin', False)
