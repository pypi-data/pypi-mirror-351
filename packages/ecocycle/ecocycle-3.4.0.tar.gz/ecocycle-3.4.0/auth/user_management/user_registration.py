"""
EcoCycle - User Registration Module
Handles new user registration with validation and security checks.
"""
import re
import getpass
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from .password_security import PasswordSecurity

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


class UserRegistration:
    """Handles user registration process."""
    
    def __init__(self):
        """Initialize the UserRegistration."""
        self.password_security = PasswordSecurity()
    
    def register_new_user(self, existing_users: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Register a new user with enhanced security validation.
        
        Args:
            existing_users: Dictionary of existing users to check against
            
        Returns:
            tuple: (success: bool, user_data: dict or None)
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
        
        # Get and validate username
        username = self._get_valid_username(existing_users)
        if not username:
            return False, None
        
        # Get full name
        name = self._get_full_name(username)
        
        # Get and validate email
        email = self._get_valid_email()
        
        # Get and validate password
        password = self._get_valid_password()
        if not password:
            return False, None
        
        # Create user data
        user_data = self._create_user_data(username, name, email, password)
        
        if HAS_RICH:
            console.print(f"\n[bold green]✅ Account created successfully![/bold green]")
            console.print(f"[green]Welcome to EcoCycle, {name}![/green]")
        else:
            print(f"\n✅ Account created successfully!")
            print(f"Welcome to EcoCycle, {name}!")
        
        return True, user_data
    
    def _get_valid_username(self, existing_users: Dict[str, Any]) -> Optional[str]:
        """
        Get and validate username input.
        
        Args:
            existing_users: Dictionary of existing users
            
        Returns:
            str: Valid username, or None if cancelled
        """
        while True:
            try:
                if HAS_RICH:
                    console.print("[bold]Username*[/bold] [dim](3-32 characters, letters, numbers, underscore only)[/dim]")
                    username = Prompt.ask("➤")
                else:
                    print("Username* (3-32 characters, letters, numbers, underscore only)")
                    username = input("➤ ").strip()
            except KeyboardInterrupt:
                print("\n")
                print("Registration cancelled by user.")
                return None
            
            # Validate username
            validation_result = self._validate_username(username, existing_users)
            if validation_result['valid']:
                if HAS_RICH:
                    console.print(f"[green]✓ Username '{username}' is available![/green]")
                else:
                    print(f"✓ Username '{username}' is available!")
                return username
            else:
                if HAS_RICH:
                    console.print(f"[red]⚠️ {validation_result['message']}[/red]")
                else:
                    print(f"⚠️ {validation_result['message']}")
    
    def _validate_username(self, username: str, existing_users: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate username according to rules.
        
        Args:
            username: Username to validate
            existing_users: Dictionary of existing users
            
        Returns:
            dict: Validation result with 'valid' and 'message' keys
        """
        # Check if username is empty
        if not username:
            return {'valid': False, 'message': 'Username cannot be empty.'}
        
        # Check length constraints
        if len(username) < 3:
            return {'valid': False, 'message': 'Username must be at least 3 characters long.'}
        
        if len(username) > 32:
            return {'valid': False, 'message': 'Username cannot exceed 32 characters.'}
        
        # Check character constraints
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return {'valid': False, 'message': 'Username must contain only letters, numbers, and underscores.'}
        
        # Check if username exists
        if username in existing_users:
            return {'valid': False, 'message': 'Username already exists. Please choose another.'}
        
        # Check for reserved names
        reserved_names = ['admin', 'system', 'root', 'administrator', 'guest']
        if username.lower() in reserved_names:
            return {'valid': False, 'message': f"Username '{username}' is reserved. Please choose another."}
        
        return {'valid': True, 'message': 'Username is valid'}
    
    def _get_full_name(self, username: str) -> str:
        """
        Get and validate full name input.
        
        Args:
            username: Username to use as fallback
            
        Returns:
            str: Full name or username as fallback
        """
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
        
        return name
    
    def _get_valid_email(self) -> Optional[str]:
        """
        Get and validate email input.
        
        Returns:
            str: Valid email or None if not provided
        """
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
                return None
            
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
            return email
    
    def _get_valid_password(self) -> Optional[str]:
        """
        Get and validate password input.
        
        Returns:
            str: Valid password, or None if cancelled
        """
        if HAS_RICH:
            console.print("\n[bold]Password*[/bold] [dim](Min 8 characters, must include uppercase, lowercase, and number)[/dim]")
        else:
            print("\nPassword* (Min 8 characters, must include uppercase, lowercase, and number)")
        
        while True:
            try:
                password = getpass.getpass("➤ ")
            except KeyboardInterrupt:
                print("\n")
                print("Password entry cancelled by user.")
                return None
            
            # Check password strength
            strength_analysis = self.password_security.check_password_strength(password)
            
            # Display password strength
            self._display_password_strength(strength_analysis)
            
            if not strength_analysis['is_valid']:
                if HAS_RICH:
                    console.print("[red]⚠️ Password must contain at least one uppercase letter, one lowercase letter, and one number.[/red]")
                else:
                    print("⚠️ Password must contain at least one uppercase letter, one lowercase letter, and one number.")
                continue
            
            # Confirm password
            try:
                confirm_password = getpass.getpass("Confirm password: ")
            except KeyboardInterrupt:
                print("\n")
                print("Password confirmation cancelled by user.")
                return None
            
            if password != confirm_password:
                if HAS_RICH:
                    console.print("[red]⚠️ Passwords do not match. Please try again.[/red]")
                else:
                    print("⚠️ Passwords do not match. Please try again.")
                continue
            
            return password
    
    def _display_password_strength(self, analysis: Dict[str, Any]) -> None:
        """
        Display password strength analysis.
        
        Args:
            analysis: Password strength analysis from PasswordSecurity
        """
        if HAS_RICH:
            if analysis['strength_score'] <= 2:
                strength_text = "[red]Weak[/red]"
            elif analysis['strength_score'] == 3:
                strength_text = "[yellow]Moderate[/yellow]"
            elif analysis['strength_score'] == 4:
                strength_text = "[green]Strong[/green]"
            else:
                strength_text = "[bold green]Very Strong[/bold green]"
            
            console.print(f"Password Strength: {strength_text}")
        else:
            print(f"Password Strength: {analysis['strength_text']}")
    
    def _create_user_data(self, username: str, name: str, email: Optional[str], password: str) -> Dict[str, Any]:
        """
        Create user data structure with hashed password.
        
        Args:
            username: Username
            name: Full name
            email: Email address (optional)
            password: Plain text password
            
        Returns:
            dict: User data structure
        """
        # Generate salt and hash password
        salt = self.password_security.generate_salt()
        password_hash = self.password_security.hash_password(password, salt)
        
        return {
            'username': username,
            'name': name,
            'email': email if email else None,
            'password_hash': password_hash,
            'salt': salt,
            'is_admin': False,
            'is_guest': False,
            'email_verified': False,
            'registration_date': datetime.now().isoformat(),
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
