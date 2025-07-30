"""
EcoCycle - Session Management Module
Handles user session persistence, verification, and cleanup.
"""
import os
import json
import hmac
import hashlib
import logging
import time
from typing import Optional
import config.config as config

logger = logging.getLogger(__name__)

# Constants
SESSION_FILE = config.SESSION_FILE
SESSION_SECRET_ENV_VAR = "SESSION_SECRET_KEY"


class SessionManager:
    """Handles user session management."""

    def __init__(self):
        """Initialize the SessionManager."""
        pass

    def get_session_secret(self) -> Optional[bytes]:
        """
        Retrieves the session secret key from environment variables.

        Returns:
            bytes: Session secret key as bytes, or None if not set
        """
        secret = os.environ.get(SESSION_SECRET_ENV_VAR)
        if not secret:
            logger.critical(f"{SESSION_SECRET_ENV_VAR} environment variable not set. Session persistence will be insecure or fail.")
            return None
        return secret.encode('utf-8')

    def calculate_verifier(self, username: str) -> Optional[str]:
        """
        Calculates the session verifier hash using HMAC-SHA256.

        Args:
            username: Username to calculate verifier for

        Returns:
            str: HMAC verifier hash, or None if calculation fails
        """
        secret = self.get_session_secret()
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

    def save_session(self, username: str) -> bool:
        """
        Saves the current username and session verifier to the session file.

        Args:
            username: Username to save session for

        Returns:
            bool: True if session was saved successfully, False otherwise
        """
        if not username or not username.strip():
            logger.error("Cannot save session: username is empty or None")
            return False

        verifier = self.calculate_verifier(username)
        if not verifier:
            logger.error("Could not calculate session verifier. Aborting session save.")
            return False

        session_data = {
            "username": username,
            "session_verifier": verifier,
            "created_at": time.time(),
            "last_accessed": time.time()
        }

        try:
            # Ensure session directory exists with proper error handling
            session_dir = os.path.dirname(SESSION_FILE)
            if session_dir and not os.path.exists(session_dir):
                try:
                    os.makedirs(session_dir, exist_ok=True)
                    logger.debug(f"Created session directory: {session_dir}")
                except OSError as dir_error:
                    logger.error(f"Failed to create session directory {session_dir}: {dir_error}")
                    return False

            # Write session data with atomic operation
            temp_file = SESSION_FILE + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            # Atomic move to prevent corruption
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            os.rename(temp_file, SESSION_FILE)

            logger.info(f"Session saved for user '{username}' to {SESSION_FILE}")

            # Set permissions (optional, good practice on Linux/macOS)
            if os.name != 'nt':
                try:
                    os.chmod(SESSION_FILE, 0o600)  # Read/write only for owner
                except Exception as perm_error:
                    logger.warning(f"Could not set permissions on {SESSION_FILE}: {perm_error}")

            return True
        except Exception as e:
            logger.error(f"Failed to write session to {SESSION_FILE}: {e}")
            # Clean up temp file if it exists
            temp_file = SESSION_FILE + '.tmp'
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False

    def load_session(self) -> Optional[str]:
        """
        Loads and verifies a session from the session file.

        Returns:
            str: Username if session is valid, None otherwise
        """
        if not os.path.exists(SESSION_FILE):
            logger.debug("No session file found.")
            return None

        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)

            username = session_data.get("username")
            stored_verifier = session_data.get("session_verifier")
            created_at = session_data.get("created_at", 0)
            last_accessed = session_data.get("last_accessed", 0)

            if not username or not stored_verifier:
                logger.warning("Invalid session data: missing username or verifier.")
                self.clear_session()
                return None

            # Check session age (expire after 30 days)
            current_time = time.time()
            session_age = current_time - created_at
            max_session_age = 30 * 24 * 60 * 60  # 30 days in seconds

            if session_age > max_session_age:
                logger.info(f"Session for user '{username}' has expired (age: {session_age/86400:.1f} days)")
                self.clear_session()
                return None

            # Verify the session
            calculated_verifier = self.calculate_verifier(username)
            if not calculated_verifier:
                logger.error("Could not calculate verifier for session verification.")
                self.clear_session()
                return None

            if calculated_verifier != stored_verifier:
                logger.warning(f"Session verifier mismatch for user '{username}'. Session may be compromised.")
                self.clear_session()
                return None

            # Update last accessed time
            session_data["last_accessed"] = current_time
            try:
                with open(SESSION_FILE, 'w') as f:
                    json.dump(session_data, f, indent=2)
            except Exception as update_error:
                logger.warning(f"Could not update session last accessed time: {update_error}")

            logger.info(f"Valid session found for user '{username}'")
            return username

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Could not read/parse session file {SESSION_FILE}: {e}. Clearing session.")
            self.clear_session()
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading session: {e}")
            self.clear_session()
            return None

    def clear_session(self, expected_user: Optional[str] = None) -> None:
        """
        Removes the session file. If expected_user is provided,
        optionally checks if the file belongs to that user before clearing.

        Args:
            expected_user: Expected username for safety check
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
                    return  # Don't clear if it's not the user we expected
            except FileNotFoundError:
                logger.debug("Session file disappeared before user check during clear.")
                return  # File is gone anyway
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

    def is_session_valid(self, username: str) -> bool:
        """
        Check if there's a valid session for the given username.

        Args:
            username: Username to check session for

        Returns:
            bool: True if session is valid, False otherwise
        """
        session_user = self.load_session()
        return session_user == username

    def refresh_session(self, username: str) -> bool:
        """
        Refresh an existing session by updating the verifier.

        Args:
            username: Username to refresh session for

        Returns:
            bool: True if session was refreshed successfully, False otherwise
        """
        if not self.is_session_valid(username):
            logger.warning(f"Cannot refresh session: no valid session found for user '{username}'")
            return False

        return self.save_session(username)
