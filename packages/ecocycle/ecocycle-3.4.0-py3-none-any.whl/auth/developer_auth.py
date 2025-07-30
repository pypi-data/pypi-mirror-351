"""
EcoCycle - Developer Authentication Module
Handles secure authentication for developer/debug mode access.
"""
import os
import hashlib
import hmac
import logging
import getpass
from typing import Optional, Tuple
from datetime import datetime, timedelta

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


class DeveloperAuth:
    """Handles developer authentication and session management."""
    
    def __init__(self, config_manager=None):
        """Initialize the DeveloperAuth with configuration."""
        self.config_manager = config_manager
        self.developer_session = None
        self.session_start_time = None
        
        # Load developer configuration
        self._load_developer_config()
    
    def _load_developer_config(self):
        """Load developer configuration from config manager or environment."""
        if self.config_manager:
            self.enabled = self.config_manager.get('developer.enabled', False)
            self.dev_username = self.config_manager.get('developer.username', 'dev_admin')
            self.dev_password_hash = self.config_manager.get('developer.password_hash', '')
            self.session_timeout = self.config_manager.get('developer.session_timeout', 1800)
            self.audit_logging = self.config_manager.get('developer.audit_logging', True)
        else:
            # Fallback to environment variables
            self.enabled = os.environ.get('DEVELOPER_MODE_ENABLED', 'false').lower() == 'true'
            self.dev_username = os.environ.get('DEVELOPER_USERNAME', 'dev_admin')
            self.dev_password_hash = os.environ.get('DEVELOPER_PASSWORD_HASH', '')
            self.session_timeout = int(os.environ.get('DEVELOPER_SESSION_TIMEOUT', '1800'))
            self.audit_logging = os.environ.get('DEVELOPER_AUDIT_LOGGING', 'true').lower() == 'true'
    
    def is_enabled(self) -> bool:
        """Check if developer mode is enabled."""
        return self.enabled and bool(self.dev_password_hash)
    
    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash a password with salt."""
        if salt is None:
            salt = os.urandom(32).hex()
        
        # Use PBKDF2 for secure password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()
        
        return password_hash, salt
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against stored hash."""
        try:
            # Extract salt from stored hash (format: salt:hash)
            if ':' in stored_hash:
                salt, hash_part = stored_hash.split(':', 1)
                computed_hash, _ = self._hash_password(password, salt)
                return hmac.compare_digest(computed_hash, hash_part)
            else:
                # Legacy format - direct hash comparison (less secure)
                computed_hash = hashlib.sha256(password.encode()).hexdigest()
                return hmac.compare_digest(computed_hash, stored_hash)
        except Exception as e:
            logger.error(f"Error verifying developer password: {e}")
            return False
    
    def authenticate_developer(self) -> bool:
        """Authenticate developer credentials."""
        if not self.is_enabled():
            if HAS_RICH and console:
                console.print("[red]Developer mode is not enabled or configured.[/red]")
            else:
                print("Developer mode is not enabled or configured.")
            return False
        
        try:
            if HAS_RICH and console:
                console.print(Panel.fit(
                    "[bold yellow]🔧 Developer Authentication[/bold yellow]\n"
                    "[dim]Enter developer credentials to access debug mode[/dim]",
                    border_style="yellow"
                ))
                username = Prompt.ask("Developer Username", default=self.dev_username)
                password = getpass.getpass("Developer Password: ")
            else:
                print("\n🔧 Developer Authentication")
                print("Enter developer credentials to access debug mode")
                username = input(f"Developer Username [{self.dev_username}]: ").strip() or self.dev_username
                password = getpass.getpass("Developer Password: ")
        
        except KeyboardInterrupt:
            print("\nDeveloper authentication cancelled.")
            return False
        
        # Verify credentials
        if username == self.dev_username and self._verify_password(password, self.dev_password_hash):
            self.developer_session = username
            self.session_start_time = datetime.now()
            
            if self.audit_logging:
                self._log_developer_action("LOGIN", "Developer authenticated successfully")
            
            if HAS_RICH and console:
                console.print("[bold green]✅ Developer authentication successful![/bold green]")
                console.print("[yellow]⚠️  You are now in DEVELOPER MODE[/yellow]")
            else:
                print("✅ Developer authentication successful!")
                print("⚠️  You are now in DEVELOPER MODE")
            
            logger.info(f"Developer '{username}' authenticated successfully")
            return True
        else:
            if self.audit_logging:
                self._log_developer_action("LOGIN_FAILED", f"Failed authentication attempt for username: {username}")
            
            if HAS_RICH and console:
                console.print("[bold red]❌ Invalid developer credentials.[/bold red]")
            else:
                print("❌ Invalid developer credentials.")
            
            logger.warning(f"Failed developer authentication attempt for username: {username}")
            return False
    
    def is_developer_authenticated(self) -> bool:
        """Check if developer is currently authenticated."""
        if not self.developer_session:
            return False
        
        # Check session timeout
        if self.session_start_time:
            elapsed = datetime.now() - self.session_start_time
            if elapsed.total_seconds() > self.session_timeout:
                self.logout_developer()
                return False
        
        return True
    
    def logout_developer(self):
        """Logout developer and clear session."""
        if self.developer_session and self.audit_logging:
            self._log_developer_action("LOGOUT", "Developer logged out")
        
        self.developer_session = None
        self.session_start_time = None
        
        if HAS_RICH and console:
            console.print("[yellow]Developer session ended.[/yellow]")
        else:
            print("Developer session ended.")
    
    def get_developer_username(self) -> Optional[str]:
        """Get the current developer username."""
        return self.developer_session if self.is_developer_authenticated() else None
    
    def _log_developer_action(self, action: str, details: str):
        """Log developer actions for audit purposes."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[DEVELOPER] {timestamp} - {action}: {details}"
        
        # Log to main logger
        logger.info(log_entry)
        
        # Also log to a separate developer audit file
        try:
            audit_log_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'Logs', 'developer_audit.log'
            )
            
            # Ensure log directory exists
            os.makedirs(os.path.dirname(audit_log_path), exist_ok=True)
            
            with open(audit_log_path, 'a', encoding='utf-8') as f:
                f.write(f"{log_entry}\n")
        except Exception as e:
            logger.error(f"Failed to write to developer audit log: {e}")
    
    def log_action(self, action: str, details: str):
        """Public method to log developer actions."""
        if self.is_developer_authenticated() and self.audit_logging:
            self._log_developer_action(action, details)
    
    def extend_session(self):
        """Extend the developer session timeout."""
        if self.is_developer_authenticated():
            self.session_start_time = datetime.now()
            if self.audit_logging:
                self._log_developer_action("SESSION_EXTENDED", "Developer session timeout extended")
    
    @staticmethod
    def generate_password_hash(password: str) -> str:
        """Generate a password hash for configuration (utility method)."""
        salt = os.urandom(32).hex()
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return f"{salt}:{password_hash}"


def setup_developer_credentials():
    """Utility function to help set up developer credentials."""
    print("🔧 Developer Mode Setup")
    print("This will help you generate secure developer credentials.")
    print()
    
    username = input("Enter developer username [dev_admin]: ").strip() or "dev_admin"
    password = getpass.getpass("Enter developer password: ")
    
    if len(password) < 12:
        print("⚠️  Warning: Password should be at least 12 characters for security.")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Setup cancelled.")
            return
    
    password_hash = DeveloperAuth.generate_password_hash(password)
    
    print("\n✅ Developer credentials generated!")
    print("Add these environment variables to your .env file:")
    print(f"DEVELOPER_MODE_ENABLED=true")
    print(f"DEVELOPER_USERNAME={username}")
    print(f"DEVELOPER_PASSWORD_HASH={password_hash}")
    print()
    print("⚠️  Keep these credentials secure and do not commit them to version control!")


if __name__ == "__main__":
    # Allow running this module directly to set up credentials
    setup_developer_credentials()
