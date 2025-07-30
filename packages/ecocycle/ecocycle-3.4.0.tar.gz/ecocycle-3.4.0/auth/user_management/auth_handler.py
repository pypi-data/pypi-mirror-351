"""
EcoCycle - Authentication Handler Module
Handles user authentication, login/logout, and credential verification.
"""
import getpass
import logging
from typing import Dict, Any, Optional, Tuple
from .password_security import PasswordSecurity
from .session_manager import SessionManager

# Check if the rich module is available for enhanced UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handles user authentication operations."""

    def __init__(self):
        """Initialize the AuthHandler."""
        self.password_security = PasswordSecurity()
        self.session_manager = SessionManager()

    def verify_credentials(self, username: str, password: str, users: Dict[str, Any]) -> bool:
        """
        Verify user credentials.

        Args:
            username: Username to verify
            password: Password to verify
            users: Dictionary of user data

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if username not in users:
            logger.warning(f"Authentication attempt for non-existent user: {username}")
            return False

        user = users[username]

        # Check if user has a password (Google users might not)
        if not user.get('password_hash') or not user.get('salt'):
            logger.warning(f"User {username} has no password set (possibly Google user)")
            return False

        # Verify password
        return self.password_security.verify_password(
            password,
            user['password_hash'],
            user['salt']
        )

    def authenticate_user(self, users: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Authenticate a user through username/password.

        Args:
            users: Dictionary of user data

        Returns:
            tuple: (success: bool, username: str or None)
        """
        try:
            if HAS_RICH:
                console.print(Panel.fit("[bold blue]Login[/bold blue]", border_style="blue"))
                username = Prompt.ask("Username")
                password = getpass.getpass("Password: ")
            else:
                username = input("Username: ")
                password = getpass.getpass("Password: ")
        except KeyboardInterrupt:
            print("\n")
            print("Login cancelled by user.")
            return False, None

        # Verify credentials
        if self.verify_credentials(username, password, users):
            logger.info(f"User {username} authenticated successfully")
            return True, username
        else:
            logger.warning(f"Failed authentication attempt for username: {username}")
            if HAS_RICH:
                console.print("[bold red]Invalid username or password.[/bold red]")
            else:
                print("Invalid username or password.")
            return False, None

    def check_email_verification_required(self, username: str, users: Dict[str, Any]) -> bool:
        """
        Check if email verification is required for the user.

        Args:
            username: Username to check
            users: Dictionary of user data

        Returns:
            bool: True if email verification is required, False otherwise
        """
        if username not in users:
            return False

        user = users[username]

        # Check if email verification is required
        # Either the user is not verified yet OR the user has enabled the "require verification every time" setting
        return (not user.get('email_verified', False) or
                user.get('preferences', {}).get('require_email_verification', True))

    def check_two_factor_required(self, username: str, users: Dict[str, Any]) -> bool:
        """
        Check if two-factor authentication is required for the user.

        Args:
            username: Username to check
            users: Dictionary of user data

        Returns:
            bool: True if two-factor authentication is required, False otherwise
        """
        if username not in users:
            return False

        user = users[username]
        return user.get('preferences', {}).get('two_factor_enabled', False)

    def send_two_factor_code(self, username: str, users: Dict[str, Any]) -> bool:
        """
        Send two-factor authentication code to user.

        Args:
            username: Username to send code to
            users: Dictionary of user data

        Returns:
            bool: True if code was sent successfully, False otherwise
        """
        if username not in users:
            logger.error(f"User {username} not found for two-factor code")
            return False

        user = users[username]
        email = user.get('email')

        if not email:
            logger.error(f"User {username} has no email address for two-factor code")
            return False

        try:
            # Import here to avoid circular imports
            from auth.email_verification import send_verification_email
            from core import database_manager

            # Get user ID from database
            conn = database_manager.create_connection()
            if not conn:
                logger.error("Failed to connect to database")
                return False

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                user_data = cursor.fetchone()

                if not user_data:
                    logger.error(f"User {username} not found in database")
                    return False

                user_id = user_data[0]

                # Send two-factor code
                return send_verification_email(user_id, email, username, user.get('name', username), 'two_factor')

            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Error sending two-factor code: {e}")
            return False

    def verify_two_factor_code(self, username: str, code: str) -> bool:
        """
        Verify two-factor authentication code.

        Args:
            username: Username to verify code for
            code: Verification code

        Returns:
            bool: True if code is valid, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from auth.email_verification import verify_code

            # Verify the code
            user_id = verify_code(code, 'two_factor')
            if not user_id:
                logger.warning(f"Invalid or expired two-factor code for user {username}")
                return False

            # Verify that the code belongs to the correct user
            from core import database_manager
            conn = database_manager.create_connection()
            if not conn:
                logger.error("Failed to connect to database")
                return False

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
                user_data = cursor.fetchone()

                if not user_data or user_data[0] != username:
                    logger.warning(f"Two-factor code user mismatch: expected {username}, got {user_data[0] if user_data else 'None'}")
                    return False

                return True

            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Error verifying two-factor code: {e}")
            return False

    def save_session(self, username: str) -> bool:
        """
        Save user session.

        Args:
            username: Username to save session for

        Returns:
            bool: True if session was saved successfully, False otherwise
        """
        return self.session_manager.save_session(username)

    def load_session(self) -> Optional[str]:
        """
        Load user session.

        Returns:
            str: Username if session is valid, None otherwise
        """
        return self.session_manager.load_session()

    def clear_session(self, username: str = None) -> None:
        """
        Clear user session.

        Args:
            username: Expected username for safety check
        """
        self.session_manager.clear_session(username)

    def logout_user(self, username: str) -> None:
        """
        Log out a user and clear their session.

        Args:
            username: Username to log out
        """
        logger.info(f"User {username} logged out")
        self.clear_session(username)

        if HAS_RICH:
            console.print(f"[green]Goodbye, {username}![/green]")
        else:
            print(f"Goodbye, {username}!")

    def display_authentication_menu(self) -> str:
        """
        Display authentication menu and get user choice.

        Returns:
            str: User's menu choice
        """
        # Check if developer mode is available
        try:
            from auth.developer_auth import DeveloperAuth
            dev_auth = DeveloperAuth()
            developer_mode_available = dev_auth.is_enabled()
        except ImportError:
            developer_mode_available = False

        if HAS_RICH:
            console.print(Panel.fit(
                "[bold green]Authentication[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))

            options = [
                "[cyan]1.[/cyan] Login with username and password",
                "[cyan]2.[/cyan] Continue as guest",
                "[cyan]3.[/cyan] Register new user",
                "[cyan]4.[/cyan] Login with Google"
            ]

            if developer_mode_available:
                options.append("[yellow]5.[/yellow] [bold]Developer Mode[/bold]")
                options.append("[cyan]6.[/cyan] Cancel")
                choices = ["1", "2", "3", "4", "5", "6"]
            else:
                options.append("[cyan]5.[/cyan] Cancel")
                choices = ["1", "2", "3", "4", "5"]

            for option in options:
                console.print(option)

            choice = Prompt.ask("\nSelect an option", choices=choices, default="1", show_default=False)
        else:
            print("\nAuthentication")
            print("1. Login with username and password")
            print("2. Continue as guest")
            print("3. Register new user")
            print("4. Login with Google")

            if developer_mode_available:
                print("5. Developer Mode")
                print("6. Cancel")
                max_choice = 6
            else:
                print("5. Cancel")
                max_choice = 5

            try:
                choice = input(f"\nSelect an option (1-{max_choice}): ")
            except KeyboardInterrupt:
                print("\n")
                print("Authentication cancelled by user.")
                return str(max_choice)  # Return cancel option

        return choice
