"""
EcoCycle - User Manager Module (Refactored)
Main orchestrator for user authentication, registration, and profile management.
This module coordinates between specialized sub-modules for better maintainability.
"""
import os
import json
import getpass
import logging
import hashlib
import base64
import re
import hmac
import threading
import socketserver
import http.server
import webbrowser
from datetime import datetime
from typing import Dict, Optional, Any
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config.config as config
from core import database_manager
from .password_security import PasswordSecurity
from .session_manager import SessionManager
from .user_data_manager import UserDataManager
from .user_registration import UserRegistration
from .auth_handler import AuthHandler
from .google_auth_handler import GoogleAuthHandler

# Check if the rich module is available for enhanced UI
try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    HAS_RICH = True
    console = Console()
    # Initialize these variables to avoid "possibly unbound" errors
    Panel = Panel
    Prompt = Prompt
except ImportError:
    HAS_RICH = False
    # Create a dummy console class to avoid "print is not a known attribute of None" errors
    class DummyConsole:
        def print(self, *args, **kwargs):
            pass
    console = DummyConsole()

    # Create dummy classes to avoid "possibly unbound" errors
    class DummyPanel:
        @staticmethod
        def fit(*args, **kwargs):
            return None
    class DummyPrompt:
        @staticmethod
        def ask(*args, **kwargs):
            return ""
    Panel = DummyPanel
    Prompt = DummyPrompt

# Constants for Google OAuth
CLIENT_SECRETS_FILE = config.GOOGLE_AUTH_FILE
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
REDIRECT_URI = 'http://localhost:8080/' # Must match one in Google Cloud Console

logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_USERS_FILE = config.USERS_FILE
SALT_LENGTH = 16
DEFAULT_ITERATIONS = 100000
SESSION_FILE = config.SESSION_FILE
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

    def load_users(self) -> None:
        """Load users from local file or Google Sheets."""
        self.users = self.user_data_manager.load_users()

    def save_users(self) -> bool:
        """Save users to local file or Google Sheets."""
        return self.user_data_manager.save_users(self.users)

    def _get_google_user_info(self, credentials):
        """Fetches user info from Google People API using credentials."""
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            logger.info(f"Fetched Google user info for: {user_info.get('email')}")
            return user_info
        except HttpError as e:
            logger.error(f"Error fetching Google user info: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching Google user info: {e}", exc_info=True)
            return None

    def _authenticate_with_google(self) -> bool:
        """Handles the Google OAuth 2.0 flow."""
        # Placeholder for the actual OAuth flow logic
        # This will involve starting a local server, opening a browser, etc.
        logger.info("Starting Google OAuth flow.")

        # --- Start of OAuth Flow Implementation ---
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        flow.redirect_uri = REDIRECT_URI

        # Use a simple local server to handle the redirect
        auth_code = None
        server_started = threading.Event()
        server_shutdown = threading.Event()

        class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                # --- CHANGE START ---
                # Parse the URL and query string robustly
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                code_list = query_params.get('code') # Returns a list or None

                if code_list: # Check if 'code' parameter exists
                    auth_code = code_list[0] # Get the first code value
                # --- CHANGE END ---
                    # Instead of sending 200 OK with HTML, send 302 Redirect
                    self.send_response(302)
                    self.send_header('Location', 'https://ecocycle-auth-success.lovable.app/')
                    self.end_headers()
                    # No body needed for redirect
                    # --- CHANGE END ---
                    logger.info("Authorization code received successfully. Redirecting browser.")
                    # Signal that the server can shut down
                    server_shutdown.set()
                else: # No code found in query parameters
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Authentication failed or cancelled.")
                    logger.warning("OAuth callback received without authorization code.")
                    server_shutdown.set()

        httpd = None
        server_thread = None
        try:
            # Find an available port starting from 8080
            port = 8080
            while True:
                try:
                    httpd = socketserver.TCPServer(("localhost", port), OAuthCallbackHandler)
                    flow.redirect_uri = f'http://localhost:{port}/'
                    logger.info(f"Local OAuth server starting on port {port}")
                    break
                except OSError as e:
                    if e.errno == 98: # Address already in use
                        logger.warning(f"Port {port} already in use, trying next port.")
                        port += 1
                        if port > 8090: # Limit port search range
                            logger.error("Could not find an available port between 8080 and 8090.")
                            return False
                    else:
                        logger.error(f"Error starting local server: {e}", exc_info=True)
                        return False

            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            server_started.set() # Signal server is ready (though serve_forever blocks)

            auth_url, _ = flow.authorization_url(prompt='select_account')
            print(f'\nPlease authorize EcoCycle in your browser: {auth_url}')
            webbrowser.open(auth_url)

            # Wait for the server thread to signal shutdown (code received or error)
            server_shutdown.wait(timeout=120) # Wait up to 2 minutes for user action

        except Exception as e:
            logger.error(f"Error during OAuth setup or browser launch: {e}", exc_info=True)
            return False
        finally:
            if httpd:
                httpd.shutdown() # Stop the server
                httpd.server_close()
                logger.info("Local OAuth server stopped.")
            if server_thread and server_thread.is_alive():
                server_thread.join(timeout=2)
                if server_thread.is_alive():
                    logger.warning("OAuth server thread did not terminate cleanly.")

        if not auth_code:
            logger.error("Failed to retrieve authorization code.")
            return False

        try:
            # Exchange code for credentials
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            logger.info("Successfully exchanged authorization code for credentials.")

            # Fetch user info
            user_info = self._get_google_user_info(credentials)
            if not user_info or 'email' not in user_info:
                logger.error("Failed to fetch user info or email from Google.")
                return False

            google_email = user_info['email']
            google_name = user_info.get('name', google_email) # Use name if available, else email
            google_id = user_info.get('id')

            # Check if user exists, if not, register them
            if google_email not in self.users:
                logger.info(f"New user via Google: {google_email}. Registering...")
                # Store minimal info, no password hash for Google users
                self.users[google_email] = {
                    'username': google_email, # Add username field explicitly
                    'name': google_name,
                    'email': google_email, # Store email as well
                    'password_hash': None, # Indicate Google login
                    'salt': None, # No salt for Google login
                    'google_id': google_id,
                    'is_admin': False,
                    'is_guest': False,
                    'registration_date': datetime.now().isoformat(),
                    'stats': {
                        'total_trips': 0,
                        'total_distance': 0.0,
                        'total_co2_saved': 0.0,
                        'total_calories': 0,
                        'trips': []
                    },
                    'preferences': {}
                }

                # Save user to the database
                registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                conn = database_manager.create_connection()
                if conn:
                    database_manager.add_user(conn, (
                        google_email, google_name, google_email, None, None, google_id, 0, 0, registration_date
                    ))
                    conn.close()
                    logger.info(f"Google user {google_email} added to database")
                else:
                    logger.error(f"Failed to create database connection for Google user {google_email}")

                if not self.save_users():
                    logger.error(f"Failed to save new Google user {google_email} to users file.")
                    # Decide if login should proceed despite save failure (maybe)
                    # For now, let's fail the login if we can't save the user
                    return False
            else:
                # Update existing user's Google ID if missing
                if 'google_id' not in self.users[google_email] or not self.users[google_email]['google_id']:
                    self.users[google_email]['google_id'] = google_id
                    self.save_users() # Save the updated ID

                # Check if user exists in database and update if needed
                conn = database_manager.create_connection()
                if conn:
                    # Check if user exists in database
                    user_data = database_manager.get_user(conn, google_email)
                    if user_data:
                        # User exists in database, update if needed
                        if not user_data[5]:  # Check if google_id is None or empty
                            # Update user with google_id
                            name = self.users[google_email].get('name', google_email)
                            email = self.users[google_email].get('email', google_email)
                            database_manager.update_user(conn, (
                                name, email, user_data[3], user_data[4], google_id,
                                user_data[6], user_data[7], user_data[8], google_email
                            ))
                            logger.info(f"Updated Google ID for existing user {google_email} in database")
                    else:
                        # User doesn't exist in database, add them
                        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        name = self.users[google_email].get('name', google_email)
                        database_manager.add_user(conn, (
                            google_email, name, google_email, None, None, google_id, 0, 0, registration_date
                        ))
                        logger.info(f"Added existing user {google_email} to database with Google ID")
                    conn.close()
                else:
                    logger.error(f"Failed to create database connection for existing Google user {google_email}")

                logger.info(f"Existing user {google_email} logged in via Google.")

            self.current_user = google_email
            # Optionally store credentials (e.g., for refresh tokens) - BE CAREFUL WITH SECURITY
            # self._save_google_credentials(credentials)
            return True

        except Exception as e:
            logger.error(f"Error during token exchange or user processing: {e}", exc_info=True)
            return False
        # --- End of OAuth Flow Implementation ---

    # --- Session Management ---
    def _get_session_secret(self):
        """Retrieves the session secret key from environment variables."""
        secret = os.environ.get(SESSION_SECRET_ENV_VAR)
        if not secret:
            # Log critically, as session security relies on this
            logger.critical(f"{SESSION_SECRET_ENV_VAR} environment variable not set. Session persistence will be insecure or fail.")
            # Optionally, raise an exception or return a specific value if the key is absolutely mandatory
            # raise ValueError(f"{SESSION_SECRET_ENV_VAR} not set!")
            return None
        return secret.encode('utf-8') # Return as bytes for HMAC

    def _calculate_verifier(self, username):
        """Calculates the session verifier hash using HMAC-SHA256."""
        secret = self._get_session_secret()
        if not secret or not username:
            logger.error("Cannot calculate verifier: Missing secret key or username.")
            return None
        # Use a context prefix to prevent potential misuse of the hash
        message = f"session-user:{username}".encode('utf-8')
        try:
            verifier = hmac.new(secret, message, hashlib.sha256).hexdigest()
            return verifier
        except Exception as e:
            logger.error(f"Error calculating HMAC verifier: {e}")
            return None

    def _save_session(self, username):
        """Saves the current username and session verifier to the session file."""
        verifier = self._calculate_verifier(username)
        if not verifier:
            logger.error("Could not calculate session verifier. Aborting session save.")
            return False # Indicate failure

        session_data = {
            "username": username,
            "session_verifier": verifier
        }
        try:
            with open(SESSION_FILE, 'w') as f:
                json.dump(session_data, f)
            logger.info(f"Session saved for user '{username}' to {SESSION_FILE}")
            # Set permissions (optional, good practice on Linux/macOS)
            if os.name != 'nt':
                try:
                    os.chmod(SESSION_FILE, 0o600) # Read/write only for owner
                except Exception as perm_error:
                    logger.warning(f"Could not set permissions on {SESSION_FILE}: {perm_error}")
            return True # Indicate success
        except Exception as e:
            logger.error(f"Failed to write session to {SESSION_FILE}: {e}")
            return False # Indicate failure

    def _clear_session(self, expected_user=None):
        """
        Removes the session file. If expected_user is provided,
        optionally checks if the file belongs to that user before clearing.
        """
        if not os.path.exists(SESSION_FILE):
            logger.debug("No session file to clear.")
            return

        # Optional safety check: only clear if it matches the user logging out
        if expected_user:
            try:
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                # Check if username exists and matches before clearing
                if data.get("username") != expected_user:
                    logger.warning(f"Session file user '{data.get('username')}' does not match expected user '{expected_user}' during logout/clear. Not clearing.")
                    return # Don't clear if it's not the user we expected
            except FileNotFoundError:
                 logger.debug("Session file disappeared before user check during clear.")
                 return # File is gone anyway
            except (json.JSONDecodeError, KeyError, TypeError) as read_err:
                logger.warning(f"Could not read/parse session file {SESSION_FILE} for user check before clearing: {read_err}. Proceeding to clear.")
                # Proceed to clear anyway, as the file is likely corrupt

        # Clear the file
        try:
            os.remove(SESSION_FILE)
            logger.info(f"Session file {SESSION_FILE} removed.")
        except FileNotFoundError:
             logger.debug("Session file disappeared before removal attempt.")
        except Exception as e:
            logger.error(f"Failed to remove session file {SESSION_FILE}: {e}")

    # --- End Session Management ---

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
            if HAS_RICH:
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

            # First check if credentials are valid
            if username:
                # Check if email verification is required
                if self.auth_handler.check_email_verification_required(username, self.users):
                    # Handle email verification process
                    if not self._handle_email_verification(username):
                        return False

                # Check if two-factor authentication is required
                if self.auth_handler.check_two_factor_required(username, self.users):
                    # Handle two-factor authentication
                    if not self._handle_two_factor_authentication(username):
                        return False

                # Authentication successful
                self.current_user = username
                logger.info(f"User {username} authenticated successfully")

                # Load trips from database to sync with in-memory data
                self.load_user_trips_from_database(username)

                # Save session
                if not self.auth_handler.save_session(username):
                    logger.error("CRITICAL: Failed to save session state after login. User will need to log in again next time.")

                if HAS_RICH:
                    console.print(f"[bold green]Welcome back, {self.users[username].get('name', username)}![/bold green]")
                else:
                    print(f"Welcome back, {self.users[username].get('name', username)}!")
                return True
            else:
                self.current_user = None
                return False

        elif choice == '2':
            # Login as guest with unique sequential account
            guest_username = self.create_guest_account()
            self.current_user = guest_username
            logger.info(f"Guest user authenticated as {guest_username}")
            if HAS_RICH:
                console.print(f"[green]Logged in as {guest_username}.[/green]")
            else:
                print(f"Logged in as {guest_username}.")
            self._clear_session()
            return True

        elif choice == '3':
            # Register and save new user
            registration_successful = self.register_new_user()
            if registration_successful:
                # Assuming successful registration means authentication is complete
                # The actual logic might depend on whether register_new_user logs the user in
                return True
            else:
                return False

        elif choice == '4':
            # Login with Google
            if HAS_RICH:
                console.print("\n[bold blue]Attempting Google Login...[/bold blue]")
            else:
                print("\nAttempting Google Login...")

            # Acquire lock to prevent concurrent Google auth flows if somehow triggered
            with self.google_auth_lock:
                success = self._authenticate_with_google()

            if success:
                # _authenticate_with_google now handles user creation/update and sets self.current_user
                logger.info(f"User {self.current_user} authenticated via Google")
                if self.current_user and self.current_user in self.users:
                    user_name = self.users[self.current_user].get('name', self.current_user)
                    if HAS_RICH:
                        console.print(f"[bold green]Welcome, {user_name}![/bold green]")
                    else:
                        print(f"Welcome, {user_name}!")
                else:
                    if HAS_RICH:
                        console.print("[bold green]Welcome![/bold green]")
                    else:
                        print("Welcome!")

                # Save session after successful Google login
                logger.debug(f"Attempting to save session for Google user '{self.current_user}'")
                if not self._save_session(self.current_user):
                    logger.error("CRITICAL: Failed to save session state after Google login.")
                    # Decide if login should still proceed? For now, let it proceed but log error.
                return True
            else:
                logger.warning("Google authentication failed.")
                if HAS_RICH:
                    console.print("[bold red]Google authentication failed.[/bold red]")
                else:
                    print("Google authentication failed.")
                self.current_user = None # Ensure current_user is None on failure
                self._clear_session() # Clear any potentially lingering session info
                return False

        elif choice == '5':
            # Cancel
            if HAS_RICH:
                console.print("[yellow]Authentication cancelled.[/yellow]")
            else:
                print("Authentication cancelled.")
            self.current_user = None
            return False

        else:
            # Invalid choice handling (if needed, otherwise the original cancel logic fits here)
            if HAS_RICH:
                console.print("[bold red]Invalid choice.[/bold red]") # Or keep the original cancel logic if appropriate
            else:
                print("Invalid choice.") # Or keep the original cancel logic if appropriate
            self.current_user = None
            return False

    def _handle_email_verification(self, username: str) -> bool:
        """
        Handle email verification process for a user.

        Args:
            username: Username to verify email for

        Returns:
            bool: True if verification successful, False otherwise
        """
        user = self.users[username]
        email = user.get('email')

        if not email:
            logger.error(f"User {username} has no email address")
            if HAS_RICH:
                console.print("[bold red]Your account requires email verification, but no email address is associated with it.[/bold red]")
            else:
                print("Your account requires email verification, but no email address is associated with it.")
            return False

        # Get user ID from database
        conn = database_manager.create_connection()
        if not conn:
            logger.error("Failed to connect to database")
            if HAS_RICH:
                console.print("[bold red]Failed to connect to database. Please try again later.[/bold red]")
            else:
                print("Failed to connect to database. Please try again later.")
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_data = cursor.fetchone()

            if not user_data:
                logger.error(f"User {username} not found in database")
                if HAS_RICH:
                    console.print("[bold red]User not found in database. Please try again later.[/bold red]")
                else:
                    print("User not found in database. Please try again later.")
                return False

            user_id = user_data[0]

            # Send verification email
            from auth.email_verification import send_verification_email

            if send_verification_email(user_id, email, username, user.get('name', username)):
                # Check if this is initial verification or verification required by settings
                verification_message = "Your account requires email verification before you can log in."
                if user.get('email_verified', False):
                    verification_message = "Email verification is required for each login (as per your settings)."

                if HAS_RICH:
                    console.print(f"[bold yellow]{verification_message}[/bold yellow]")
                    console.print("[green]A verification email has been sent to your email address.[/green]")
                    verification_code = Prompt.ask("[bold]Enter the 6-digit verification code[/bold]")
                else:
                    print(verification_message)
                    print("A verification email has been sent to your email address.")
                    verification_code = input("Enter the 6-digit verification code: ")
            else:
                if HAS_RICH:
                    console.print("[bold red]Failed to send verification email. Please try again later.[/bold red]")
                else:
                    print("Failed to send verification email. Please try again later.")
                return False

            # Verify the code
            if verification_code and self.verify_email_code(verification_code):
                if HAS_RICH:
                    console.print("[bold green]Email verified successfully![/bold green]")
                else:
                    print("Email verified successfully!")
                return True
            else:
                if HAS_RICH:
                    console.print("[bold red]Invalid or expired verification code. Please try again later.[/bold red]")
                else:
                    print("Invalid or expired verification code. Please try again later.")
                return False
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            if HAS_RICH:
                console.print(f"[yellow]Could not send verification email: {str(e)}[/yellow]")
            else:
                print(f"Could not send verification email: {str(e)}")
            return False
        finally:
            conn.close()

    def _handle_two_factor_authentication(self, username: str) -> bool:
        """
        Handle two-factor authentication process for a user.

        Args:
            username: Username to authenticate

        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Send two-factor code
        if not self.auth_handler.send_two_factor_code(username, self.users):
            logger.error(f"Failed to send two-factor code to user {username}")
            if HAS_RICH:
                console.print("[bold red]Failed to send two-factor authentication code. Please try again later.[/bold red]")
            else:
                print("Failed to send two-factor authentication code. Please try again later.")
            return False

        # Prompt for two-factor code
        if HAS_RICH:
            console.print("[bold blue]Two-factor authentication required[/bold blue]")
            console.print("A verification code has been sent to your email address.")
            two_factor_code = Prompt.ask("Enter verification code")
        else:
            print("Two-factor authentication required")
            print("A verification code has been sent to your email address.")
            two_factor_code = input("Enter verification code: ")

        # Verify two-factor code
        if not self.auth_handler.verify_two_factor_code(username, two_factor_code):
            logger.warning(f"Invalid two-factor code for user {username}")
            if HAS_RICH:
                console.print("[bold red]Invalid verification code. Please try again.[/bold red]")
            else:
                print("Invalid verification code. Please try again.")
            return False

        return True

    def register_new_user(self) -> bool:
        """
        Register a new user with enhanced security validation.

        Returns:
            bool: True if registration successful, False otherwise
        """
        if HAS_RICH:
            console.print(Panel.fit(
                "[bold green]🌱 Create Your EcoCycle Account[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))
            console.print("[dim]Join our community of eco-conscious cyclists![/dim]")
            console.print("[dim]All fields marked with * are required[/dim]\n")
        else:
            print("\n=== Create Your EcoCycle Account ===")
            print("Join our community of eco-conscious cyclists!")
            print("All fields marked with * are required\n")

        # Get user information with enhanced validation
        while True:
            try:
                if HAS_RICH:
                    console.print("[bold]Username*[/bold] [dim](3-32 characters, letters, numbers, underscore only)[/dim]")
                    username = Prompt.ask("➤")
                else:
                    print("Username* (3-32 characters, letters, numbers, underscore only)")
                    username = input("➤ ").strip()
            except KeyboardInterrupt:
                print("\n")  # New line for better formatting
                print("Registration cancelled by user.")
                return False

            # Check if username is empty
            if not username:
                if HAS_RICH:
                    console.print("[red]⚠️ Username cannot be empty.[/red]")
                else:
                    print("⚠️ Username cannot be empty.")
                continue

            # Check length constraints (prevent too long usernames)
            if len(username) < 3:
                if HAS_RICH:
                    console.print("[red]⚠️ Username must be at least 3 characters long.[/red]")
                else:
                    print("⚠️ Username must be at least 3 characters long.")
                continue

            if len(username) > 32:
                if HAS_RICH:
                    console.print("[red]⚠️ Username cannot exceed 32 characters.[/red]")
                else:
                    print("⚠️ Username cannot exceed 32 characters.")
                continue

            # Check character constraints (prevent injection)
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                if HAS_RICH:
                    console.print("[red]⚠️ Username must contain only letters, numbers, and underscores.[/red]")
                else:
                    print("⚠️ Username must contain only letters, numbers, and underscores.")
                continue

            # Check if username exists
            if username in self.users:
                if HAS_RICH:
                    console.print("[red]⚠️ Username already exists. Please choose another.[/red]")
                else:
                    print("⚠️ Username already exists. Please choose another.")
                continue

            # Check for reserved names
            reserved_names = ['admin', 'system', 'root', 'administrator', 'guest']
            if username.lower() in reserved_names:
                if HAS_RICH:
                    console.print(f"[red]⚠️ Username '{username}' is reserved. Please choose another.[/red]")
                else:
                    print(f"⚠️ Username '{username}' is reserved. Please choose another.")
                continue

            if HAS_RICH:
                console.print(f"[green]✓ Username '{username}' is available![/green]")
            else:
                print(f"✓ Username '{username}' is available!")
            break

        # Full name validation
        if HAS_RICH:
            console.print("\n[bold]Full Name*[/bold] [dim](Your display name)[/dim]")
            name = Prompt.ask("➤")
        else:
            print("\nFull Name* (Your display name)")
            name = input("➤ ").strip()

        if not name:
            name = username  # Default to username if name is empty
            if HAS_RICH:
                console.print(f"[yellow]ℹ️ Using username as display name: {username}[/yellow]")
            else:
                print(f"ℹ️ Using username as display name: {username}")

        # Email validation
        while True:
            if HAS_RICH:
                console.print("\n[bold]Email Address[/bold] [dim](Recommended for account recovery)[/dim]")
                email = Prompt.ask("➤", default="", show_default=False)
            else:
                print("\nEmail Address (Recommended for account recovery)")
                email = input("➤ ").strip()

            if not email:
                if HAS_RICH:
                    console.print("[yellow]ℹ️ No email provided. Some features may be limited.[/yellow]")
                else:
                    print("ℹ️ No email provided. Some features may be limited.")
                email = None  # Make it explicitly None if empty
                break

            # Simple email validation regex
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                if HAS_RICH:
                    console.print("[red]⚠️ Invalid email format. Please enter a valid email or leave empty.[/red]")
                else:
                    print("⚠️ Invalid email format. Please enter a valid email or leave empty.")
                continue

            if HAS_RICH:
                console.print(f"[green]✓ Email format is valid![/green]")
            else:
                print(f"✓ Email format is valid!")
            break

        # Get and confirm password with enhanced security requirements
        if HAS_RICH:
            console.print("\n[bold]Password*[/bold] [dim](Min 8 characters, must include uppercase, lowercase, and number)[/dim]")
        else:
            print("\nPassword* (Min 8 characters, must include uppercase, lowercase, and number)")

        while True:
            try:
                password = getpass.getpass("➤ ")
            except KeyboardInterrupt:
                print("\n")  # New line for better formatting
                print("Password entry cancelled by user.")
                return False

            # Check password length
            if len(password) < 8:
                if HAS_RICH:
                    console.print("[red]⚠️ Password must be at least 8 characters long.[/red]")
                else:
                    print("⚠️ Password must be at least 8 characters long.")
                continue

            # Check password strength
            has_uppercase = any(c.isupper() for c in password)
            has_lowercase = any(c.islower() for c in password)
            has_number = any(c.isdigit() for c in password)
            has_special = any(not c.isalnum() for c in password)

            # Calculate password strength
            strength = 0
            if has_uppercase: strength += 1
            if has_lowercase: strength += 1
            if has_number: strength += 1
            if has_special: strength += 1
            if len(password) >= 12: strength += 1

            # Display password strength
            if HAS_RICH:
                if strength <= 2:
                    strength_text = "[red]Weak[/red]"
                elif strength == 3:
                    strength_text = "[yellow]Moderate[/yellow]"
                elif strength == 4:
                    strength_text = "[green]Strong[/green]"
                else:
                    strength_text = "[bold green]Very Strong[/bold green]"

                console.print(f"Password Strength: {strength_text}")
            else:
                if strength <= 2:
                    strength_text = "Weak"
                elif strength == 3:
                    strength_text = "Moderate"
                elif strength == 4:
                    strength_text = "Strong"
                else:
                    strength_text = "Very Strong"

                print(f"Password Strength: {strength_text}")

            if not (has_uppercase and has_lowercase and has_number):
                if HAS_RICH:
                    console.print("[red]⚠️ Password must contain at least one uppercase letter, one lowercase letter, and one number.[/red]")
                else:
                    print("⚠️ Password must contain at least one uppercase letter, one lowercase letter, and one number.")
                continue

            if not has_special:
                if HAS_RICH:
                    console.print("[yellow]⚠️ Warning: Adding a special character will make your password stronger.[/yellow]")
                    confirm_weak = Prompt.ask("Continue with this password anyway?", choices=["y", "n"], default="n", show_default=False)
                else:
                    print("⚠️ Warning: Adding a special character will make your password stronger.")
                    confirm_weak = input("Continue with this password anyway? [y/n]: ")

                if confirm_weak.lower() != 'y':
                    continue

            if HAS_RICH:
                console.print("\n[bold]Confirm Password*[/bold]")
            else:
                print("\nConfirm Password*")

            try:
                confirm_password = getpass.getpass("➤ ")
            except KeyboardInterrupt:
                print("\n")  # New line for better formatting
                print("Password confirmation cancelled by user.")
                return False
            if password != confirm_password:
                if HAS_RICH:
                    console.print("[red]⚠️ Passwords do not match.[/red]")
                else:
                    print("⚠️ Passwords do not match.")
                continue

            if HAS_RICH:
                console.print("[green]✓ Password confirmed![/green]")
            else:
                print("✓ Password confirmed!")
            break

        # Show registration progress
        if HAS_RICH:
            console.print("\n[bold]Creating your account...[/bold]")
        else:
            print("\nCreating your account...")

        # Generate salt and hash password
        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)

        # Create user
        self.users[username] = {
            'username': username,
            'name': name,
            'email': email if email else None,
            'password_hash': password_hash,
            'salt': salt,
            'is_admin': False,
            'is_guest': False,
            'email_verified': False,  # New field for email verification
            'stats': {
                'total_trips': 0,
                'total_distance': 0.0,
                'total_co2_saved': 0.0,
                'total_calories': 0,
                'trips': []
            },
            'preferences': {
                'require_email_verification': True  # Default to requiring email verification
            }
        }

        # Save users
        if self.save_users():
            # Set current user
            self.current_user = username

            # Save user to the database
            conn = database_manager.create_connection()
            if conn:
                # Add user to database
                user_id = database_manager.add_user(conn, (
                    username, name, email, password_hash, salt, None, 0, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))

                # Send verification email if email is provided
                verification_code = None
                if email and user_id:
                    try:
                        if HAS_RICH:
                            console.print("\n[bold]📧 Email Verification[/bold]")
                        else:
                            print("\n=== Email Verification ===")

                        from auth.email_verification import send_verification_email
                        if send_verification_email(user_id, email, username, name):
                            if HAS_RICH:
                                console.print(f"[green]✉️ Verification email sent to {email}[/green]")
                            else:
                                print(f"✉️ Verification email sent to {email}")

                            # Prompt user to enter verification code
                            if HAS_RICH:
                                console.print(Panel.fit(
                                    "[bold blue]Please check your email for a 6-digit verification code.[/bold blue]",
                                    border_style="blue",
                                    padding=(1, 2)
                                ))
                                console.print("[green]A verification email has been sent to your email address.[/green]")
                                verification_code = Prompt.ask("[bold]Enter the 6-digit verification code[/bold]")
                            else:
                                print("\n┌─────────────────────────────────────────────────┐")
                                print("│ Please check your email for a 6-digit verification code. │")
                                print("└─────────────────────────────────────────────────┘")
                                print("A verification email has been sent to your email address.")
                                verification_code = input("Enter the 6-digit verification code: ")

                            # Verify the code
                            if verification_code and self.verify_email_code(verification_code):
                                if HAS_RICH:
                                    console.print("[bold green]✅ Email verified successfully![/bold green]")
                                else:
                                    print("✅ Email verified successfully!")
                            else:
                                if HAS_RICH:
                                    console.print("[bold red]❌ Invalid or expired verification code. You can request a new code later.[/bold red]")
                                else:
                                    print("❌ Invalid or expired verification code. You can request a new code later.")
                        else:
                            if HAS_RICH:
                                console.print(f"[yellow]⚠️ Could not send verification email to {email}. Please check your email settings.[/yellow]")
                            else:
                                print(f"⚠️ Could not send verification email to {email}. Please check your email settings.")
                    except Exception as e:
                        logger.error(f"Error sending verification email: {e}")
                        if HAS_RICH:
                            console.print(f"[yellow]⚠️ Could not send verification email: {str(e)}[/yellow]")
                        else:
                            print(f"⚠️ Could not send verification email: {str(e)}")

                conn.close()

            if HAS_RICH:
                console.print(Panel.fit(
                    f"[bold green]🎉 Welcome to EcoCycle, {name}![/bold green]\n[green]Your account has been created successfully.[/green]",
                    border_style="green",
                    padding=(1, 2)
                ))

                # Remind user about verification if not completed
                if email and not self.users[username].get('email_verified', False):
                    console.print(Panel.fit(
                        "[yellow]⚠️ Remember: You need to verify your email before you can use all features.\nYou can request a new verification code from the settings menu.[/yellow]",
                        border_style="yellow",
                        padding=(1, 2)
                    ))
            else:
                print("\n┌─────────────────────────────────────────────────┐")
                print(f"│ 🎉 Welcome to EcoCycle, {name}! │")
                print("│ Your account has been created successfully. │")
                print("└─────────────────────────────────────────────────┘")

                # Remind user about verification if not completed
                if email and not self.users[username].get('email_verified', False):
                    print("\n⚠️ Remember: You need to verify your email before you can use all features.")
                    print("⚠️ You can request a new verification code from the settings menu.")

            return True
        else:
            if HAS_RICH:
                console.print("[red]❌ Error saving user information.[/red]")
            else:
                print("❌ Error saving user information.")
            return False

    def _verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify username and password.

        Args:
            username (str): Username
            password (str): Password

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if username not in self.users:
            return False

        user = self.users[username]

        # Guest user can't login with password
        if user.get('is_guest', False):
            return False

        # Get stored hash and salt
        stored_hash = user.get('password_hash')
        salt = user.get('salt')

        if not stored_hash or not salt:
            return False

        # Hash the provided password
        calculated_hash = self._hash_password(password, salt)

        # Compare hashes
        return calculated_hash == stored_hash

    def verify_email_code(self, code: str) -> bool:
        """
        Verify a user's email address using a 6-digit verification code.

        Args:
            code: The 6-digit verification code

        Returns:
            bool: True if verification was successful, False otherwise
        """
        # Import here to avoid circular imports
        from auth.email_verification import verify_code

        # Verify the code
        user_id = verify_code(code, 'email_verification')
        if not user_id:
            logger.warning(f"Invalid or expired email verification code: {code}")
            return False

        # Find the user with this ID in the database
        conn = database_manager.create_connection()
        if not conn:
            logger.error("Failed to connect to database")
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                logger.error(f"User with ID {user_id} not found in database")
                return False

            username = user_data[1]  # Index 1 is the username

            # Update user in memory
            if username in self.users:
                self.users[username]['email_verified'] = True
                self.save_users()

                # Update user in database
                cursor.execute(
                    "UPDATE users SET email_verified = 1 WHERE id = ?",
                    (user_id,)
                )
                conn.commit()

                logger.info(f"Email verified for user {username}")
                return True
            else:
                logger.error(f"User {username} found in database but not in memory")
                return False
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False
        finally:
            conn.close()

    def request_email_verification(self, username: str) -> bool:
        """
        Request a new email verification code for a user.

        Args:
            username: The username or email of the user

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Check if username is actually an email
        if '@' in username:
            # Find user by email
            user_found = False
            for user_key, user_data in self.users.items():
                if user_data.get('email') == username:
                    username = user_key
                    user_found = True
                    break

            if not user_found:
                logger.error(f"No user found with email {username}")
                return False

        if username not in self.users:
            logger.error(f"User {username} not found")
            return False

        user = self.users[username]
        email = user.get('email')
        name = user.get('name', username)

        if not email:
            logger.error(f"User {username} has no email address")
            return False

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

            user_id = user_data[0]  # Index 0 is the user ID

            # Import here to avoid circular imports
            from auth.email_verification import send_verification_email

            # Send verification email
            if send_verification_email(user_id, email, username, name):
                logger.info(f"Verification email sent to {email} for user {username}")
                return True
            else:
                logger.error(f"Failed to send verification email to {email} for user {username}")
                return False
        except Exception as e:
            logger.error(f"Error requesting email verification: {e}")
            return False
        finally:
            conn.close()

    def request_password_reset(self, username: str) -> bool:
        """
        Request a password reset code for a user.

        Args:
            username: The username or email of the user

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Check if username is actually an email
        if '@' in username:
            # Find user by email
            user_found = False
            for user_key, user_data in self.users.items():
                if user_data.get('email') == username:
                    username = user_key
                    user_found = True
                    break

            if not user_found:
                logger.error(f"No user found with email {username}")
                return False

        if username not in self.users:
            logger.error(f"User {username} not found")
            return False

        user = self.users[username]
        email = user.get('email')
        name = user.get('name', username)

        if not email:
            logger.error(f"User {username} has no email address")
            return False

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

            user_id = user_data[0]  # Index 0 is the user ID

            # Import here to avoid circular imports
            from auth.email_verification import send_password_reset_email

            # Send password reset email
            if send_password_reset_email(user_id, email, username, name):
                logger.info(f"Password reset email sent to {email} for user {username}")
                return True
            else:
                logger.error(f"Failed to send password reset email to {email} for user {username}")
                return False
        except Exception as e:
            logger.error(f"Error requesting password reset: {e}")
            return False
        finally:
            conn.close()

    def reset_password(self, username: str, code: str, new_password: str) -> bool:
        """
        Reset a user's password using a verification code.

        Args:
            username: The username or email of the user
            code: The 6-digit verification code
            new_password: The new password

        Returns:
            bool: True if password was reset successfully, False otherwise
        """
        # Check if username is actually an email
        if '@' in username:
            # Find user by email
            user_found = False
            for user_key, user_data in self.users.items():
                if user_data.get('email') == username:
                    username = user_key
                    user_found = True
                    break

            if not user_found:
                logger.error(f"No user found with email {username}")
                return False

        if username not in self.users:
            logger.error(f"User {username} not found")
            return False

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

            user_id = user_data[0]  # Index 0 is the user ID

            # Import here to avoid circular imports
            from auth.email_verification import verify_code

            # Verify the code
            verified_user_id = verify_code(code, 'password_reset')
            if not verified_user_id or verified_user_id != user_id:
                logger.warning(f"Invalid or expired password reset code for user {username}")
                return False

            # Generate new salt and hash password
            salt = self._generate_salt()
            password_hash = self._hash_password(new_password, salt)

            # Update user in memory
            self.users[username]['password_hash'] = password_hash
            self.users[username]['salt'] = salt
            self.save_users()

            # Update user in database
            cursor.execute(
                """UPDATE users
                SET password_hash = ?, salt = ?
                WHERE id = ?""",
                (password_hash, salt, user_id)
            )
            conn.commit()

            logger.info(f"Password reset for user {username}")
            return True
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return False
        finally:
            conn.close()

    def request_account_recovery(self, username: str) -> bool:
        """
        Request an account recovery code for a user.

        Args:
            username: The username or email of the user

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Check if username is actually an email
        if '@' in username:
            # Find user by email
            user_found = False
            for user_key, user_data in self.users.items():
                if user_data.get('email') == username:
                    username = user_key
                    user_found = True
                    break

            if not user_found:
                logger.error(f"No user found with email {username}")
                return False

        if username not in self.users:
            logger.error(f"User {username} not found")
            return False

        user = self.users[username]
        email = user.get('email')
        name = user.get('name', username)

        if not email:
            logger.error(f"User {username} has no email address")
            return False

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

            user_id = user_data[0]  # Index 0 is the user ID

            # Import here to avoid circular imports
            from auth.email_verification import send_account_recovery_email

            # Send account recovery email
            if send_account_recovery_email(user_id, email, username, name):
                logger.info(f"Account recovery email sent to {email} for user {username}")
                return True
            else:
                logger.error(f"Failed to send account recovery email to {email} for user {username}")
                return False
        except Exception as e:
            logger.error(f"Error requesting account recovery: {e}")
            return False
        finally:
            conn.close()

    def recover_account(self, email: str, code: str) -> bool:
        """
        Recover a user's account using a verification code.

        Args:
            email: The email address of the user
            code: The 6-digit verification code

        Returns:
            bool: True if account was recovered successfully, False otherwise
        """
        # Find user by email
        username = None
        for user_key, user_data in self.users.items():
            if user_data.get('email') == email:
                username = user_key
                break

        if not username:
            logger.error(f"No user found with email {email}")
            return False

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

            user_id = user_data[0]  # Index 0 is the user ID

            # Import here to avoid circular imports
            from auth.email_verification import verify_code

            # Verify the code
            verified_user_id = verify_code(code, 'account_recovery')
            if not verified_user_id or verified_user_id != user_id:
                logger.warning(f"Invalid or expired account recovery code for user {username}")
                return False

            # Mark email as verified
            self.users[username]['email_verified'] = True
            self.save_users()

            # Update user in database
            cursor.execute(
                "UPDATE users SET email_verified = 1 WHERE id = ?",
                (user_id,)
            )
            conn.commit()

            logger.info(f"Account recovered for user {username}")
            return True
        except Exception as e:
            logger.error(f"Error recovering account: {e}")
            return False
        finally:
            conn.close()



    def verify_email(self, token: str) -> bool:
        """
        Verify a user's email address using a verification token.

        This method is kept for backward compatibility.

        Args:
            token: The verification token

        Returns:
            bool: True if verification was successful, False otherwise
        """
        # Import here to avoid circular imports
        from auth.email_verification import verify_token

        # Verify the token
        user_id = verify_token(token, 'email_verification')
        if not user_id:
            logger.warning(f"Invalid or expired email verification token: {token[:10]}...")
            return False

        # Find the user with this ID in the database
        conn = database_manager.create_connection()
        if not conn:
            logger.error("Failed to connect to database")
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                logger.error(f"User with ID {user_id} not found in database")
                return False

            username = user_data[1]  # Index 1 is the username

            # Update user in memory
            if username in self.users:
                self.users[username]['email_verified'] = True
                self.save_users()

                # Update user in database
                cursor.execute(
                    "UPDATE users SET email_verified = 1 WHERE id = ?",
                    (user_id,)
                )
                conn.commit()

                logger.info(f"Email verified for user {username}")
                return True
            else:
                logger.error(f"User {username} found in database but not in memory")
                return False
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False
        finally:
            conn.close()

    def resend_verification_email(self, username: str) -> bool:
        """
        Resend the verification email to a user.

        Args:
            username: The username of the user

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        return self.request_email_verification(username)

    def check_two_factor_required(self, username: str) -> bool:
        """
        Check if two-factor authentication is required for a user.

        Args:
            username: The username of the user

        Returns:
            bool: True if two-factor authentication is required, False otherwise
        """
        if username not in self.users:
            return False

        # Check if user has enabled two-factor authentication
        return self.users[username].get('preferences', {}).get('enable_two_factor', False)

    def send_two_factor_code(self, username: str) -> bool:
        """
        Send a two-factor authentication code to the user's email.

        Args:
            username: The username of the user

        Returns:
            bool: True if the code was sent successfully, False otherwise
        """
        if username not in self.users:
            logger.error(f"User {username} not found")
            return False

        user = self.users[username]
        email = user.get('email')
        name = user.get('name', username)

        if not email:
            logger.error(f"User {username} has no email address")
            return False

        # Get user ID from database
        conn = database_manager.create_connection()
        if not conn:
            logger.error("Failed to connect to database")
            return False

        try:
            # Import here to avoid circular imports
            from auth.email_verification import send_two_factor_email

            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_data = cursor.fetchone()

            if not user_data:
                logger.error(f"User {username} not found in database")
                return False

            user_id = user_data[0]  # Index 0 is the user ID

            # Send two-factor email
            if send_two_factor_email(user_id, email, name):
                logger.info(f"Two-factor code sent to {email} for user {username}")
                return True
            else:
                logger.error(f"Failed to send two-factor code to {email} for user {username}")
                return False
        except Exception as e:
            logger.error(f"Error sending two-factor code: {e}")
            return False
        finally:
            conn.close()

    def verify_two_factor_code(self, username: str, code: str) -> bool:
        """
        Verify a two-factor authentication code.

        Args:
            username: The username of the user
            code: The two-factor authentication code

        Returns:
            bool: True if the code is valid, False otherwise
        """
        if username not in self.users:
            logger.error(f"User {username} not found")
            return False

        # Import here to avoid circular imports
        from auth.email_verification import verify_code

        # Verify the code
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

            user_id = user_data[0]  # Index 0 is the user ID

            # Verify the code
            verified_user_id = verify_code(code, 'two_factor', user_id)
            if verified_user_id is not None and verified_user_id == user_id:
                logger.info(f"Two-factor code verified for user {username}")
                return True
            else:
                logger.warning(f"Invalid two-factor code for user {username}")
                return False
        except Exception as e:
            logger.error(f"Error verifying two-factor code: {e}")
            return False
        finally:
            conn.close()

    def create_guest_account(self) -> str:
        """
        Create a unique guest account with sequential numbering.

        Returns:
            str: The username of the new guest account
        """
        # Find the highest guest number
        highest_guest_number = 0
        for username, user_data in self.users.items():
            if user_data.get('is_guest', False) and username.startswith('guest'):
                try:
                    # Extract the number from guestN
                    if username == 'guest':
                        guest_number = 0
                    else:
                        guest_number = int(username[5:])
                    highest_guest_number = max(highest_guest_number, guest_number)
                except ValueError:
                    # If the username doesn't follow the guestN pattern, ignore it
                    pass

        # Create new guest username
        new_guest_number = highest_guest_number + 1
        new_guest_username = f"guest{new_guest_number}" if new_guest_number > 0 else "guest"

        # Create the guest user
        self.users[new_guest_username] = {
            'username': new_guest_username,
            'name': f"Guest User {new_guest_number}" if new_guest_number > 0 else "Guest User",
            'email': None,
            'password_hash': None,
            'salt': None,
            'is_admin': False,
            'is_guest': True,
            'guest_number': new_guest_number,
            'stats': {
                'total_trips': 0,
                'total_distance': 0.0,
                'total_co2_saved': 0.0,
                'total_calories': 0,
                'trips': []
            },
            'preferences': {}
        }

        # Save the users
        if self.save_users():
            logger.info(f"Created new guest account: {new_guest_username}")

            # Save to database
            conn = database_manager.create_connection()
            if conn:
                database_manager.add_user(conn, (
                    new_guest_username,
                    f"Guest User {new_guest_number}" if new_guest_number > 0 else "Guest User",
                    None, None, None, None, 0, 1,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.close()

            return new_guest_username
        else:
            logger.error("Failed to save new guest account")
            return "guest"  # Fallback to default guest

    def _generate_salt(self) -> str:
        """
        Generate a random salt for password hashing.

        Returns:
            str: Base64-encoded salt
        """
        salt_bytes = os.urandom(SALT_LENGTH)
        return base64.b64encode(salt_bytes).decode('utf-8')

    def _hash_password(self, password: str, salt: str) -> str:
        """
        Hash a password with salt using PBKDF2.

        Args:
            password (str): Password to hash
            salt (str): Base64-encoded salt

        Returns:
            str: Base64-encoded password hash
        """
        # Decode salt from base64
        salt_bytes = base64.b64decode(salt)

        # Hash the password
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            DEFAULT_ITERATIONS
        )

        # Encode the key in base64
        return base64.b64encode(key).decode('utf-8')

    def get_current_user(self) -> Dict:
        """
        Get the currently authenticated user.

        Returns:
            dict: User data or empty dict if no user is authenticated
        """
        if self.current_user and self.current_user in self.users:
            return self.users[self.current_user]
        return {}

    def is_authenticated(self) -> bool:
        """
        Check if a user is currently authenticated.

        Returns:
            bool: True if a user is authenticated, False otherwise
        """
        return self.current_user is not None and self.current_user in self.users

    def is_guest(self) -> bool:
        """
        Check if the current user is a guest.

        Returns:
            bool: True if current user is a guest, False otherwise
        """
        if not self.is_authenticated() or self.current_user is None:
            return False

        return self.users[self.current_user].get('is_guest', False)

    def is_admin(self) -> bool:
        """
        Check if the current user is an admin.

        Returns:
            bool: True if current user is an admin, False otherwise
        """
        current_user = self.get_current_user()
        return current_user.get('is_admin', False)

    def get_current_username(self) -> str:
        """
        Get the username of the currently authenticated user.

        Returns:
            str: Username of current user or 'guest' if no user is authenticated
        """
        current_user = self.get_current_user()
        return current_user.get('username', 'guest')

    def update_user_stats(self, distance: float, co2_saved: float, calories: int, duration: float = 0.0) -> bool:
        """
        Update user statistics and add a new trip.

        Args:
            distance (float): Distance in kilometers
            co2_saved (float): CO2 saved in kilograms
            calories (int): Calories burned
            duration (float): Trip duration in minutes

        Returns:
            bool: True if stats were updated, False otherwise
        """
        if not self.is_authenticated() or self.current_user is None:
            return False

        # Get current user
        user = self.users[self.current_user]

        # Ensure stats dictionary exists
        if 'stats' not in user:
            user['stats'] = {
                'total_trips': 0,
                'total_distance': 0.0,
                'total_co2_saved': 0.0,
                'total_calories': 0,
                'trips': []
            }

        # Ensure trips list exists
        if 'trips' not in user['stats']:
            user['stats']['trips'] = []

        # Create trip data
        trip = {
            'date': datetime.now().isoformat(),
            'distance': distance,
            'duration': duration,
            'co2_saved': co2_saved,
            'calories': calories
        }

        # Add trip to trips list
        user['stats']['trips'].append(trip)

        # Update totals
        user['stats']['total_trips'] = user['stats'].get('total_trips', 0) + 1
        user['stats']['total_distance'] = user['stats'].get('total_distance', 0.0) + distance
        user['stats']['total_co2_saved'] = user['stats'].get('total_co2_saved', 0.0) + co2_saved
        user['stats']['total_calories'] = user['stats'].get('total_calories', 0) + calories

        # Save updated user data
        return self.save_users()

    def update_user_preference(self, key: str, value: Any) -> bool:
        """
        Update a user preference.

        Args:
            key (str): Preference key
            value: Preference value

        Returns:
            bool: True if preference was updated, False otherwise
        """
        if not self.is_authenticated() or self.current_user is None:
            return False

        # Get current user
        user = self.users[self.current_user]

        # Ensure preferences dictionary exists
        if 'preferences' not in user:
            user['preferences'] = {}

        # Update preference
        user['preferences'][key] = value

        # Save updated user data
        return self.save_users()

    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.

        Args:
            key (str): Preference key
            default: Default value if preference not found

        Returns:
            Preference value or default
        """
        if not self.is_authenticated() or self.current_user is None:
            return default

        # Get current user
        user = self.users[self.current_user]

        # Get preference value
        if 'preferences' in user and key in user['preferences']:
            return user['preferences'][key]

        return default

    def load_user_trips_from_database(self, username: str) -> bool:
        """
        Load trips from database and sync with in-memory user data.

        Args:
            username (str): Username to load trips for

        Returns:
            bool: True if trips were loaded successfully, False otherwise
        """
        try:
            import core.database_manager as database_manager

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
            if username in self.users:
                user = self.users[username]

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

                # Save the updated user data to ensure persistence
                self.save_users()

                logger.info(f"Loaded {len(trips_list)} trips from database for user {username}")
                logger.info(f"Updated stats: {len(trips_list)} trips, {total_distance:.2f} km, {total_co2_saved:.2f} kg CO2, {total_calories} calories")
                return True

            return False

        except Exception as e:
            logger.error(f"Error loading trips from database for user {username}: {e}")
            return False

    def get_user_trips(self, username: str) -> list:
        """
        Get all trips for a specific user from database and in-memory data.

        Args:
            username (str): Username to get trips for

        Returns:
            list: List of trip dictionaries
        """
        trips = []

        try:
            # First, get trips from in-memory user data
            if username in self.users:
                user_stats = self.users[username].get('stats', {})
                memory_trips = user_stats.get('trips', [])
                trips.extend(memory_trips)

            # Then, get trips from database to ensure we have the latest data
            try:
                import core.database_manager as database_manager

                # Get user ID from username
                conn = database_manager.create_connection()
                if conn:
                    # Get user ID
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    user_row = cursor.fetchone()

                    if user_row:
                        user_id = user_row[0]

                        # Get trips from database
                        db_trips = database_manager.get_user_trips(conn, user_id)

                        # Convert database trips to dictionary format
                        for trip_row in db_trips:
                            # trip_row format: (id, user_id, date, distance, duration, co2_saved, calories, route_data, weather_data, created_at)
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

                            # Check if this trip is already in memory trips (avoid duplicates)
                            trip_exists = False
                            for memory_trip in trips:
                                if (memory_trip.get('date') == trip_dict['date'] and
                                    memory_trip.get('distance') == trip_dict['distance'] and
                                    memory_trip.get('duration') == trip_dict['duration']):
                                    trip_exists = True
                                    break

                            if not trip_exists:
                                trips.append(trip_dict)

                    conn.close()

            except Exception as db_error:
                logger.warning(f"Could not fetch trips from database for user {username}: {db_error}")

            # Sort trips by date (newest first)
            trips.sort(key=lambda x: x.get('date', ''), reverse=True)

            logger.info(f"Retrieved {len(trips)} trips for user {username}")
            return trips

        except Exception as e:
            logger.error(f"Error getting trips for user {username}: {e}")
            return []

    def logout(self) -> None:
        """Log out the current user and clear the session."""
        logged_out_user = self.current_user  # Store username before clearing
        if logged_out_user:
            logger.info(f"User '{logged_out_user}' logged out")
            self._clear_session(expected_user=logged_out_user)  # Clear the session file
            self.current_user = None
            logger.info("Logout complete.")
        else:
            logger.debug("Logout called but no user was logged in.")
            # Ensure session file is cleared even if current_user was somehow None
            self._clear_session()

    def create_data_backup(self, backup_type: str = "full") -> Optional[str]:
        """
        Create a backup of user data before reset operations.

        Args:
            backup_type: Type of backup to create ("full", "trips", "stats", "challenges", "achievements")

        Returns:
            Path to the backup file if successful, None otherwise
        """
        if not self.is_authenticated():
            logger.error("User not authenticated for backup creation")
            return None

        try:
            import json
            import datetime
            from pathlib import Path

            # Get current user data
            user = self.get_current_user()
            username = user.get('username', 'unknown')

            # Create backup directory
            backup_dir = Path("data/backups")
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Determine what to backup based on type
            backup_data = {}
            if backup_type == "full":
                backup_data = user.copy()
                # Remove sensitive information
                if 'password_hash' in backup_data:
                    del backup_data['password_hash']
                if 'salt' in backup_data:
                    del backup_data['salt']
            elif backup_type == "trips":
                backup_data = {
                    'username': username,
                    'stats': user.get('stats', {}),
                    'backup_type': 'trips'
                }
            elif backup_type == "stats":
                backup_data = {
                    'username': username,
                    'stats': user.get('stats', {}),
                    'backup_type': 'stats'
                }
            elif backup_type == "challenges":
                backup_data = {
                    'username': username,
                    'active_challenges': user.get('active_challenges', []),
                    'completed_challenges': user.get('completed_challenges', []),
                    'backup_type': 'challenges'
                }
            elif backup_type == "achievements":
                backup_data = {
                    'username': username,
                    'completed_achievements': user.get('completed_achievements', []),
                    'eco_points': user.get('eco_points', 0),
                    'backup_type': 'achievements'
                }

            # Create backup filename
            backup_filename = f"ecocycle_{username}_{backup_type}_backup_{timestamp}.json"
            backup_path = backup_dir / backup_filename

            # Save backup
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def reset_cycling_trips(self) -> bool:
        """
        Reset only cycling trips and related statistics.

        Returns:
            True if reset was successful, False otherwise
        """
        if not self.is_authenticated() or self.current_user is None:
            logger.error("User not authenticated for trips reset")
            return False

        try:
            user = self.users[self.current_user]

            # Reset only trip-related data
            if 'stats' in user:
                user['stats']['total_trips'] = 0
                user['stats']['total_distance'] = 0.0
                user['stats']['total_co2_saved'] = 0.0
                user['stats']['total_calories'] = 0
                user['stats']['trips'] = []

            # Save changes
            success = self.save_users()
            if success:
                logger.info(f"Cycling trips reset for user: {self.current_user}")
            return success

        except Exception as e:
            logger.error(f"Error resetting cycling trips: {e}")
            return False

    def reset_statistics_analytics(self) -> bool:
        """
        Reset statistics and analytics data while preserving trip logs.

        Returns:
            True if reset was successful, False otherwise
        """
        if not self.is_authenticated() or self.current_user is None:
            logger.error("User not authenticated for statistics reset")
            return False

        try:
            user = self.users[self.current_user]

            # Reset aggregated statistics but keep individual trips
            if 'stats' in user:
                trips = user['stats'].get('trips', [])  # Preserve trips
                user['stats'] = {
                    'total_trips': len(trips),
                    'total_distance': sum(trip.get('distance', 0) for trip in trips),
                    'total_co2_saved': sum(trip.get('co2_saved', 0) for trip in trips),
                    'total_calories': sum(trip.get('calories', 0) for trip in trips),
                    'trips': trips
                }

            # Reset any analytics preferences
            if 'preferences' in user:
                analytics_keys = ['analytics_enabled', 'share_data']
                for key in analytics_keys:
                    if key in user['preferences']:
                        del user['preferences'][key]

            # Save changes
            success = self.save_users()
            if success:
                logger.info(f"Statistics and analytics reset for user: {self.current_user}")
            return success

        except Exception as e:
            logger.error(f"Error resetting statistics and analytics: {e}")
            return False

    def reset_challenges_achievements(self) -> bool:
        """
        Reset challenges and achievements data.

        Returns:
            True if reset was successful, False otherwise
        """
        if not self.is_authenticated() or self.current_user is None:
            logger.error("User not authenticated for challenges/achievements reset")
            return False

        try:
            user = self.users[self.current_user]

            # Reset challenge and achievement data
            challenge_achievement_keys = [
                'active_challenges', 'completed_challenges', 'challenge_history',
                'completed_achievements', 'achievement_progress', 'eco_points',
                'level', 'badges', 'rewards'
            ]

            for key in challenge_achievement_keys:
                if key in user:
                    if key == 'eco_points':
                        user[key] = 0
                    else:
                        user[key] = []

            # Save changes
            success = self.save_users()
            if success:
                logger.info(f"Challenges and achievements reset for user: {self.current_user}")
            return success

        except Exception as e:
            logger.error(f"Error resetting challenges and achievements: {e}")
            return False

    def reset_all_user_data(self) -> bool:
        """
        Reset all user data (complete account data wipe) while preserving account credentials.

        Returns:
            True if reset was successful, False otherwise
        """
        if not self.is_authenticated() or self.current_user is None:
            logger.error("User not authenticated for complete data reset")
            return False

        try:
            # At this point we know current_user is not None due to the check above
            current_username = self.current_user
            assert current_username is not None  # Type checker hint

            user = self.users[current_username]

            # Preserve essential account information
            preserved_data = {
                'username': user.get('username'),
                'name': user.get('name'),
                'email': user.get('email'),
                'password_hash': user.get('password_hash'),
                'salt': user.get('salt'),
                'is_admin': user.get('is_admin', False),
                'is_guest': user.get('is_guest', False),
                'email_verified': user.get('email_verified', False),
                'google_id': user.get('google_id'),  # For Google users
                'guest_number': user.get('guest_number'),  # For guest users
                'registration_date': user.get('registration_date')
            }

            # Reset to clean state with preserved credentials
            self.users[current_username] = {
                **{k: v for k, v in preserved_data.items() if v is not None},
                'stats': {
                    'total_trips': 0,
                    'total_distance': 0.0,
                    'total_co2_saved': 0.0,
                    'total_calories': 0,
                    'trips': []
                },
                'preferences': {
                    'require_email_verification': True  # Default security setting
                }
            }

            # Save changes
            success = self.save_users()
            if success:
                logger.info(f"Complete data reset for user: {self.current_user}")
            return success

        except Exception as e:
            logger.error(f"Error resetting all user data: {e}")
            return False

    def send_data_reset_verification(self, reset_type: str, reset_description: str) -> bool:
        """
        Send email verification for data reset operation.

        Args:
            reset_type: Type of reset being performed
            reset_description: Description of what will be reset

        Returns:
            True if verification email was sent successfully, False otherwise
        """
        if not self.is_authenticated():
            logger.error("User not authenticated for data reset verification")
            return False

        user = self.get_current_user()
        email = user.get('email')

        if not email:
            logger.error("User has no email address for verification")
            return False

        # Get user ID from database using connection pool
        try:
            with database_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (user.get('username'),))
                user_data = cursor.fetchone()

                if not user_data:
                    logger.error(f"User {user.get('username')} not found in database")
                    return False

                user_id = user_data[0]

                # Import here to avoid circular imports
                from auth.email_verification import send_data_reset_verification_email

                # Send verification email
                if send_data_reset_verification_email(
                    user_id, email, user.get('username', ''), user.get('name', ''),
                    reset_type, reset_description
                ):
                    logger.info(f"Data reset verification email sent to {email}")
                    return True
                else:
                    logger.error(f"Failed to send data reset verification email to {email}")
                    return False

        except Exception as e:
            logger.error(f"Error sending data reset verification: {e}")
            return False

    def verify_data_reset_code(self, code: str) -> bool:
        """
        Verify a data reset verification code.

        Args:
            code: The 6-digit verification code

        Returns:
            True if verification was successful, False otherwise
        """
        # Import here to avoid circular imports
        from auth.email_verification import verify_code, DATA_RESET_TYPE

        # Verify the code
        user_id = verify_code(code, DATA_RESET_TYPE)
        if not user_id:
            logger.warning(f"Invalid or expired data reset verification code: {code}")
            return False

        logger.info(f"Data reset verification successful for user ID: {user_id}")
        return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test UserManager
    manager = UserManager()

    # Create a new admin user (for testing purposes)
    if 'admin' not in manager.users:
        print("Creating admin user...")

        # Generate admin credentials
        manager.users['admin'] = {
            'username': 'admin',
            'name': 'Administrator',
            'email': 'admin@example.com',
            'is_admin': True,
            'is_guest': False,
            'salt': manager._generate_salt(),
            'stats': {
                'total_trips': 0,
                'total_distance': 0.0,
                'total_co2_saved': 0.0,
                'total_calories': 0,
                'trips': []
            },
            'preferences': {}
        }

        # Set admin password (hard-coded for this test only)
        manager.users['admin']['password_hash'] = manager._hash_password('adminpass', manager.users['admin']['salt'])

        # Save users
        manager.save_users()
        print("Admin user created with username 'admin' and password 'adminpass'")

    # Test authentication
    success = manager.authenticate()
    print(f"Authentication {'successful' if success else 'failed'}")

    if success:
        print(f"Current user: {manager.get_current_user().get('name')}")
        print(f"Is admin: {manager.is_admin()}")
        print(f"Is guest: {manager.is_guest()}")

        # Test updating user preferences
        manager.update_user_preference('theme', 'dark')
        print(f"Theme preference: {manager.get_user_preference('theme')}")

        # Test updating user stats
        manager.update_user_stats(10.5, 2.42, 300)
        user = manager.get_current_user()
        print(f"User stats: {user['stats']}")

        # Test logout
        manager.logout()
        print(f"After logout - Is authenticated: {manager.is_authenticated()}")
