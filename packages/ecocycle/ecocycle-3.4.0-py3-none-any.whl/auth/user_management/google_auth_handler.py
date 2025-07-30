"""
EcoCycle - Google OAuth Authentication Handler
Handles Google OAuth 2.0 authentication flow.
"""
import threading
import socketserver
import http.server
import webbrowser
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config.config as config
from core import database_manager

logger = logging.getLogger(__name__)

# Constants for Google OAuth
CLIENT_SECRETS_FILE = config.GOOGLE_AUTH_FILE
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
REDIRECT_URI = 'http://localhost:8080/'  # Must match one in Google Cloud Console


class GoogleAuthHandler:
    """Handles Google OAuth 2.0 authentication."""
    
    def __init__(self):
        """Initialize the GoogleAuthHandler."""
        self.google_auth_lock = threading.Lock()
    
    def authenticate_with_google(self, users: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Handles the Google OAuth 2.0 flow.
        
        Args:
            users: Dictionary of existing users
            
        Returns:
            tuple: (success: bool, username: str or None, user_data: dict or None)
        """
        logger.info("Starting Google OAuth flow.")
        
        # Acquire lock to prevent concurrent Google auth flows
        with self.google_auth_lock:
            try:
                # Start OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                flow.redirect_uri = REDIRECT_URI
                
                # Get authorization code
                auth_code = self._get_authorization_code(flow)
                if not auth_code:
                    logger.error("Failed to retrieve authorization code.")
                    return False, None, None
                
                # Exchange code for credentials
                flow.fetch_token(code=auth_code)
                credentials = flow.credentials
                logger.info("Successfully exchanged authorization code for credentials.")
                
                # Get user info
                user_info = self._get_google_user_info(credentials)
                if not user_info or 'email' not in user_info:
                    logger.error("Failed to fetch user info or email from Google.")
                    return False, None, None
                
                # Process user
                return self._process_google_user(user_info, users)
                
            except Exception as e:
                logger.error(f"Error during Google authentication: {e}", exc_info=True)
                return False, None, None
    
    def _get_authorization_code(self, flow) -> Optional[str]:
        """
        Get authorization code from Google OAuth flow.
        
        Args:
            flow: OAuth flow object
            
        Returns:
            str: Authorization code, or None if failed
        """
        auth_code = None
        server_started = threading.Event()
        server_shutdown = threading.Event()
        
        class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                # Parse the URL and query string robustly
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                code_list = query_params.get('code')  # Returns a list or None
                
                if code_list:  # Check if 'code' parameter exists
                    auth_code = code_list[0]  # Get the first code value
                    # Send redirect response
                    self.send_response(302)
                    self.send_header('Location', 'https://ecocycle-auth-success.lovable.app/')
                    self.end_headers()
                    logger.info("Authorization code received successfully. Redirecting browser.")
                    server_shutdown.set()
                else:  # No code found in query parameters
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
                    if e.errno == 98:  # Address already in use
                        logger.warning(f"Port {port} already in use, trying next port.")
                        port += 1
                        if port > 8090:  # Limit port search range
                            logger.error("Could not find an available port between 8080 and 8090.")
                            return None
                    else:
                        logger.error(f"Error starting local server: {e}", exc_info=True)
                        return None
            
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            server_started.set()
            
            auth_url, _ = flow.authorization_url(prompt='select_account')
            print(f'\nPlease authorize EcoCycle in your browser: {auth_url}')
            webbrowser.open(auth_url)
            
            # Wait for the server thread to signal shutdown (code received or error)
            server_shutdown.wait(timeout=120)  # Wait up to 2 minutes for user action
            
        except Exception as e:
            logger.error(f"Error during OAuth setup or browser launch: {e}", exc_info=True)
            return None
        finally:
            if httpd:
                httpd.shutdown()
                httpd.server_close()
                logger.info("Local OAuth server stopped.")
            if server_thread and server_thread.is_alive():
                server_thread.join(timeout=2)
                if server_thread.is_alive():
                    logger.warning("OAuth server thread did not terminate cleanly.")
        
        return auth_code
    
    def _get_google_user_info(self, credentials) -> Optional[Dict[str, Any]]:
        """
        Fetches user info from Google People API using credentials.
        
        Args:
            credentials: Google OAuth credentials
            
        Returns:
            dict: User info from Google, or None if failed
        """
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
    
    def _process_google_user(self, user_info: Dict[str, Any], users: Dict[str, Any]) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process Google user info and create/update user account.
        
        Args:
            user_info: User info from Google
            users: Dictionary of existing users
            
        Returns:
            tuple: (success: bool, username: str, user_data: dict or None)
        """
        google_email = user_info['email']
        google_name = user_info.get('name', google_email)
        google_id = user_info.get('id')
        
        # Check if user exists, if not, register them
        if google_email not in users:
            logger.info(f"New user via Google: {google_email}. Registering...")
            
            # Create new user data
            user_data = {
                'username': google_email,
                'name': google_name,
                'email': google_email,
                'password_hash': None,  # Indicate Google login
                'salt': None,  # No salt for Google login
                'google_id': google_id,
                'is_admin': False,
                'is_guest': False,
                'email_verified': True,  # Google emails are pre-verified
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
            self._save_google_user_to_database(google_email, google_name, google_id)
            
            return True, google_email, user_data
        else:
            # Update existing user's Google ID if missing
            user_data = users[google_email]
            if 'google_id' not in user_data or not user_data['google_id']:
                user_data['google_id'] = google_id
            
            # Update database if needed
            self._update_google_user_in_database(google_email, google_name, google_id)
            
            logger.info(f"Existing user {google_email} logged in via Google.")
            return True, google_email, user_data
    
    def _save_google_user_to_database(self, email: str, name: str, google_id: str) -> None:
        """
        Save Google user to database.
        
        Args:
            email: User email
            name: User name
            google_id: Google ID
        """
        try:
            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = database_manager.create_connection()
            if conn:
                database_manager.add_user(conn, (
                    email, name, email, None, None, google_id, 0, 0, registration_date
                ))
                conn.close()
                logger.info(f"Google user {email} added to database")
            else:
                logger.error(f"Failed to create database connection for Google user {email}")
        except Exception as e:
            logger.error(f"Error saving Google user to database: {e}")
    
    def _update_google_user_in_database(self, email: str, name: str, google_id: str) -> None:
        """
        Update Google user in database.
        
        Args:
            email: User email
            name: User name
            google_id: Google ID
        """
        try:
            conn = database_manager.create_connection()
            if conn:
                # Check if user exists in database
                user_data = database_manager.get_user(conn, email)
                if user_data:
                    # User exists in database, update if needed
                    if not user_data[5]:  # Check if google_id is None or empty
                        database_manager.update_user(conn, (
                            name, email, user_data[3], user_data[4], google_id,
                            user_data[6], user_data[7], user_data[8], email
                        ))
                        logger.info(f"Updated Google ID for existing user {email} in database")
                else:
                    # User doesn't exist in database, add them
                    registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    database_manager.add_user(conn, (
                        email, name, email, None, None, google_id, 0, 0, registration_date
                    ))
                    logger.info(f"Added existing user {email} to database with Google ID")
                conn.close()
            else:
                logger.error(f"Failed to create database connection for existing Google user {email}")
        except Exception as e:
            logger.error(f"Error updating Google user in database: {e}")
