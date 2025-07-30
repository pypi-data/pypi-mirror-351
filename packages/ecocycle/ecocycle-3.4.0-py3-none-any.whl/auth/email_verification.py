"""
Email Verification Module for EcoCycle

This module handles email verification functionality including:
- Verification code generation and validation
- Sending verification emails with 6-digit codes
- Verifying email addresses
- Resending verification emails
- Password reset functionality
- Account recovery
- Two-factor authentication
"""

import os
import logging
import secrets
import string
import datetime
import re
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import core.database_manager as database_manager

# Configure logging
logger = logging.getLogger(__name__)

# Constants
EMAIL_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'email_templates')
TOKEN_LENGTH = 64
VERIFICATION_CODE_LENGTH = 6
TOKEN_EXPIRY_HOURS = 24
PASSWORD_RESET_EXPIRY_MINUTES = 10
TWO_FACTOR_EXPIRY_MINUTES = 5
EMAIL_VERIFICATION_TYPE = 'email_verification'
PASSWORD_RESET_TYPE = 'password_reset'
ACCOUNT_RECOVERY_TYPE = 'account_recovery'
TWO_FACTOR_TYPE = 'two_factor'
DATA_RESET_TYPE = 'data_reset'

def generate_token(length: int = TOKEN_LENGTH) -> str:
    """
    Generate a secure random token for verification purposes.

    Args:
        length: Length of the token to generate

    Returns:
        A secure random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_verification_code(length: int = VERIFICATION_CODE_LENGTH) -> str:
    """
    Generate a secure random numeric verification code.

    Args:
        length: Length of the verification code to generate

    Returns:
        A secure random numeric code as string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def create_verification_token(user_id: int, token_type: str = EMAIL_VERIFICATION_TYPE) -> str:
    """
    Create a verification token and store it in the database.

    Args:
        user_id: User ID to associate with the token
        token_type: Type of token (email_verification, password_reset, account_recovery)

    Returns:
        The generated token string
    """
    # Generate a secure token
    token = generate_token()

    # Calculate expiration time (24 hours from now)
    created_at = datetime.datetime.now().isoformat()
    expires_at = (datetime.datetime.now() + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat()

    # Store token in database using connection pool
    try:
        with database_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO verification_tokens
                (user_id, token, token_type, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, token, token_type, created_at, expires_at)
            )
            conn.commit()
            logger.info(f"Created verification token for user {user_id}")
    except Exception as e:
        logger.error(f"Error creating verification token: {e}")
        return ""

    return token

def create_verification_code(user_id: int, token_type: str = EMAIL_VERIFICATION_TYPE,
                            expiry_minutes: int = TOKEN_EXPIRY_HOURS * 60) -> str:
    """
    Create a 6-digit verification code and store it in the database.

    Args:
        user_id: User ID to associate with the code
        token_type: Type of code (email_verification, password_reset, two_factor, account_recovery)
        expiry_minutes: Minutes until the code expires

    Returns:
        The generated verification code
    """
    # Generate a secure 6-digit code
    code = generate_verification_code()

    # Calculate expiration time
    created_at = datetime.datetime.now().isoformat()
    expires_at = (datetime.datetime.now() + datetime.timedelta(minutes=expiry_minutes)).isoformat()

    # Store code in database using connection pool
    try:
        with database_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO verification_tokens
                (user_id, token, token_type, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, code, token_type, created_at, expires_at)
            )
            conn.commit()
            logger.info(f"Created verification code for user {user_id}")
    except Exception as e:
        logger.error(f"Error creating verification code: {e}")
        return ""

    return code

def verify_token(token: str, token_type: str = EMAIL_VERIFICATION_TYPE) -> Optional[int]:
    """
    Verify a token and return the associated user ID if valid.

    Args:
        token: The token to verify
        token_type: Type of token to verify

    Returns:
        User ID if token is valid, None otherwise
    """
    # Clean up expired tokens and verify token using connection pool
    try:
        with database_manager.get_connection() as conn:
            # Delete expired tokens
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM verification_tokens WHERE expires_at < datetime('now')"
            )
            conn.commit()

            # Get token from database
            cursor.execute(
                """SELECT id, user_id, token, token_type, created_at, expires_at, used
                FROM verification_tokens
                WHERE token = ? AND token_type = ?""",
                (token, token_type)
            )
            token_data = cursor.fetchone()

            if not token_data:
                logger.warning(f"Token not found: {token[:10]}...")
                return None

            # Check if token is already used
            if token_data[6]:  # Index 6 is the 'used' column
                logger.warning(f"Token already used: {token[:10]}...")
                return None

            # Check if token is expired
            expires_at = datetime.datetime.fromisoformat(token_data[5])
            if expires_at < datetime.datetime.now():
                logger.warning(f"Token expired: {token[:10]}...")
                return None

            # Token is valid, mark as used
            cursor.execute(
                "UPDATE verification_tokens SET used = 1 WHERE id = ?",
                (token_data[0],)
            )
            conn.commit()

            # Return the user ID
            return token_data[1]  # Index 1 is the user_id
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None

def verify_code(code: str, token_type: str, user_id: Optional[int] = None) -> Optional[int]:
    """
    Verify a 6-digit code and return the associated user ID if valid.

    Args:
        code: The verification code to verify
        token_type: Type of code to verify
        user_id: Optional user ID to check against (for two-factor authentication)

    Returns:
        User ID if code is valid, None otherwise
    """
    # Clean up expired tokens and verify code using connection pool
    try:
        with database_manager.get_connection() as conn:
            # Delete expired tokens
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM verification_tokens WHERE expires_at < datetime('now')"
            )
            conn.commit()

            # Get token from database with optional user_id filter
            if user_id is not None:
                # For two-factor authentication, we need to check the user_id as well
                cursor.execute(
                    """SELECT id, user_id, token, token_type, created_at, expires_at, used
                    FROM verification_tokens
                    WHERE token = ? AND token_type = ? AND user_id = ?""",
                    (code, token_type, user_id)
                )
            else:
                cursor.execute(
                    """SELECT id, user_id, token, token_type, created_at, expires_at, used
                    FROM verification_tokens
                    WHERE token = ? AND token_type = ?""",
                    (code, token_type)
                )

            token_data = cursor.fetchone()

            if not token_data:
                logger.warning(f"Code not found: {code}")
                return None

            # Check if token is already used
            if token_data[6]:  # Index 6 is the 'used' column
                logger.warning(f"Code already used: {code}")
                return None

            # Check if token is expired
            expires_at = datetime.datetime.fromisoformat(token_data[5])
            if expires_at < datetime.datetime.now():
                logger.warning(f"Code expired: {code}")
                return None

            # Token is valid, mark as used
            cursor.execute(
                "UPDATE verification_tokens SET used = 1 WHERE id = ?",
                (token_data[0],)
            )
            conn.commit()

            # Return the user ID
            return token_data[1]  # Index 1 is the user_id
    except Exception as e:
        logger.error(f"Error verifying code: {e}")
        return None

def send_verification_email(user_id: int, email: str, username: str, name: str) -> bool:
    """
    Send a verification email to the user with a 6-digit code.

    Args:
        user_id: User ID
        email: Email address to send to
        username: Username for the email (not used in the template)
        name: User's name for personalization

    Returns:
        True if email was sent successfully, False otherwise
    """
    # Create a verification code
    verification_code = create_verification_code(user_id, EMAIL_VERIFICATION_TYPE)

    # Try to load HTML template first
    html_template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'email_verification.html')
    if os.path.exists(html_template_path):
        # Read HTML template
        with open(html_template_path, 'r') as f:
            template = f.read()

        # Replace placeholders
        email_body = template.replace('{name}', name)
        email_body = email_body.replace('{verification_code}', verification_code)

        # Send HTML email
        return send_email(
            to_email=email,
            subject="Verify Your EcoCycle Email Address",
            message_body=email_body,
            is_html=True
        )
    else:
        # Fallback to text template
        template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'email_verification.txt')
        if not os.path.exists(template_path):
            # Create template directory if it doesn't exist
            os.makedirs(EMAIL_TEMPLATES_DIR, exist_ok=True)

            # Create a default template if it doesn't exist
            default_template = """Hello {name},

Thank you for registering with EcoCycle! Please verify your email address by entering the 6-digit code below:

Your verification code: {verification_code}

This code will expire in 24 hours.

If you did not register for an EcoCycle account, please ignore this email.

The EcoCycle Team
"""
            with open(template_path, 'w') as f:
                f.write(default_template)

        # Read template
        with open(template_path, 'r') as f:
            template = f.read()

        # Replace placeholders
        email_body = template.replace('{name}', name)
        email_body = email_body.replace('{verification_code}', verification_code)

        # Send plain text email
        return send_email(
            to_email=email,
            subject="Verify Your EcoCycle Email Address",
            message_body=email_body
        )

def send_password_reset_email(user_id: int, email: str, username: str, name: str) -> bool:
    """
    Send a password reset email to the user with a 6-digit code.

    Args:
        user_id: User ID
        email: Email address to send to
        username: Username for the email
        name: User's name for personalization

    Returns:
        True if email was sent successfully, False otherwise
    """
    # Create a password reset code with 10-minute expiration
    reset_code = create_verification_code(user_id, PASSWORD_RESET_TYPE, PASSWORD_RESET_EXPIRY_MINUTES)

    # Load email template
    template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'password_reset.txt')
    if not os.path.exists(template_path):
        # Create template directory if it doesn't exist
        os.makedirs(EMAIL_TEMPLATES_DIR, exist_ok=True)

        # Create a default template if it doesn't exist
        default_template = """Hello {name},

We received a request to reset your EcoCycle password. Please use the 6-digit code below to reset your password:

Your reset code: {reset_code}

This code will expire in 10 minutes.

If you did not request a password reset, please ignore this email.

The EcoCycle Team
"""
        with open(template_path, 'w') as f:
            f.write(default_template)

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    email_body = template.replace('{name}', name)
    email_body = email_body.replace('{reset_code}', reset_code)

    # Send email
    return send_email(
        to_email=email,
        subject="Reset Your EcoCycle Password",
        message_body=email_body
    )

def send_account_recovery_email(user_id: int, email: str, username: str, name: str) -> bool:
    """
    Send an account recovery email to the user with a 6-digit code.

    Args:
        user_id: User ID
        email: Email address to send to
        username: Username for the email
        name: User's name for personalization

    Returns:
        True if email was sent successfully, False otherwise
    """
    # Create an account recovery code
    recovery_code = create_verification_code(user_id, ACCOUNT_RECOVERY_TYPE)

    # Load email template
    template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'account_recovery.txt')
    if not os.path.exists(template_path):
        # Create template directory if it doesn't exist
        os.makedirs(EMAIL_TEMPLATES_DIR, exist_ok=True)

        # Create a default template if it doesn't exist
        default_template = """Hello {name},

We received a request to recover your EcoCycle account. Please use the 6-digit code below to verify your identity:

Your recovery code: {recovery_code}

This code will expire in 24 hours.

If you did not request account recovery, please ignore this email.

The EcoCycle Team
"""
        with open(template_path, 'w') as f:
            f.write(default_template)

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    email_body = template.replace('{name}', name)
    email_body = email_body.replace('{recovery_code}', recovery_code)

    # Send email
    return send_email(
        to_email=email,
        subject="Recover Your EcoCycle Account",
        message_body=email_body
    )

def send_two_factor_email(user_id: int, email: str, name: str) -> str:
    """
    Send a two-factor authentication email with a 6-digit code.

    Args:
        user_id: User ID
        email: Email address to send to
        name: User's name for personalization

    Returns:
        The generated two-factor code if email was sent successfully, empty string otherwise
    """
    # Create a two-factor code with 5-minute expiration
    two_factor_code = create_verification_code(user_id, TWO_FACTOR_TYPE, TWO_FACTOR_EXPIRY_MINUTES)

    # Load email template
    template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'two_factor.txt')
    if not os.path.exists(template_path):
        # Create template directory if it doesn't exist
        os.makedirs(EMAIL_TEMPLATES_DIR, exist_ok=True)

        # Create a default template if it doesn't exist
        default_template = """Hello {name},

Here is your two-factor authentication code for EcoCycle:

Your code: {two_factor_code}

This code will expire in 5 minutes.

If you did not attempt to log in to your EcoCycle account, please change your password immediately.

The EcoCycle Team
"""
        with open(template_path, 'w') as f:
            f.write(default_template)

    # Read template
    with open(template_path, 'r') as f:
        template = f.read()

    # Replace placeholders
    email_body = template.replace('{name}', name)
    email_body = email_body.replace('{two_factor_code}', two_factor_code)

    # Send email
    success = send_email(
        to_email=email,
        subject="EcoCycle Two-Factor Authentication Code",
        message_body=email_body
    )

    return two_factor_code if success else ""

def send_data_reset_verification_email(user_id: int, email: str, username: str, name: str, reset_type: str, reset_description: str) -> bool:
    """
    Send a data reset verification email to the user with a 6-digit code.

    Args:
        user_id: User ID
        email: Email address to send to
        username: Username for the email (not used in the template)
        name: User's name for personalization
        reset_type: Type of reset being performed
        reset_description: Description of what will be reset

    Returns:
        True if email was sent successfully, False otherwise
    """
    # Create a verification code with 10-minute expiration for security
    verification_code = create_verification_code(user_id, DATA_RESET_TYPE, 10)

    # Try to load HTML template first
    html_template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'data_reset_verification.html')
    if os.path.exists(html_template_path):
        # Read HTML template
        with open(html_template_path, 'r') as f:
            template = f.read()

        # Replace placeholders
        email_body = template.replace('{name}', name)
        email_body = email_body.replace('{verification_code}', verification_code)
        email_body = email_body.replace('{reset_type}', reset_type)
        email_body = email_body.replace('{reset_description}', reset_description)

        # Send HTML email
        return send_email(
            to_email=email,
            subject="🔒 EcoCycle Data Reset Verification Required",
            message_body=email_body,
            is_html=True
        )
    else:
        # Fallback to text template
        template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'data_reset_verification.txt')
        if not os.path.exists(template_path):
            # Create template directory if it doesn't exist
            os.makedirs(EMAIL_TEMPLATES_DIR, exist_ok=True)

            # Create a default template if it doesn't exist
            default_template = """Hello {name},

🔒 DATA RESET VERIFICATION REQUIRED

⚠️ SECURITY ALERT: A data reset operation has been requested for your account.

Reset Type Requested: {reset_type}
What will be reset: {reset_description}

You have requested to reset specific data in your EcoCycle account. To proceed with this operation, please use the following verification code:

Your verification code: {verification_code}

This code is valid for 10 minutes. Please enter it in the program promptly to confirm this data reset operation.

SECURITY NOTICE: This action cannot be undone. If you did not request this data reset, please ignore this email and consider changing your password.

If you have any questions about this data reset operation, please contact our support team.

The EcoCycle Team

---
This is an automated security email. Please do not reply.
"""
            with open(template_path, 'w') as f:
                f.write(default_template)

        # Read template
        with open(template_path, 'r') as f:
            template = f.read()

        # Replace placeholders
        email_body = template.replace('{name}', name)
        email_body = email_body.replace('{verification_code}', verification_code)
        email_body = email_body.replace('{reset_type}', reset_type)
        email_body = email_body.replace('{reset_description}', reset_description)

        # Send plain text email
        return send_email(
            to_email=email,
            subject="🔒 EcoCycle Data Reset Verification Required",
            message_body=email_body
        )

def create_test_verification_code(user_id: int, token_type: str = EMAIL_VERIFICATION_TYPE) -> str:
    """
    Create a verification code for a user (for testing purposes only).
    This function is used when email sending is disabled or fails.

    Args:
        user_id: User ID to create code for
        token_type: Type of code to create

    Returns:
        The created verification code
    """
    # Generate a 6-digit code
    code = ''.join(secrets.choice(string.digits) for _ in range(6))

    # Store the code in the database using connection pool
    try:
        with database_manager.get_connection() as conn:
            cursor = conn.cursor()
            # Delete any existing unused tokens for this user and type
            cursor.execute(
                "DELETE FROM verification_tokens WHERE user_id = ? AND token_type = ? AND used = 0",
                (user_id, token_type)
            )

            # Insert the new token
            expiry = datetime.datetime.now() + datetime.timedelta(hours=24)
            cursor.execute(
                """INSERT INTO verification_tokens
                (user_id, token, token_type, created_at, expires_at, used)
                VALUES (?, ?, ?, datetime('now'), ?, 0)""",
                (user_id, code, token_type, expiry.strftime('%Y-%m-%d %H:%M:%S'))
            )
            conn.commit()
            return code
    except Exception as e:
        logger.error(f"Error creating verification code: {e}")
        return code


class EmailVerification:
    """
    EmailVerification class that provides a convenient interface for email verification functionality.
    This class wraps the module-level functions for easier use in other parts of the application.
    """

    def __init__(self):
        """Initialize the EmailVerification instance."""
        self.logger = logger

    def generate_verification_code(self, length: int = VERIFICATION_CODE_LENGTH) -> str:
        """Generate a secure random numeric verification code."""
        return generate_verification_code(length)

    def create_verification_code(self, user_id: int, token_type: str = EMAIL_VERIFICATION_TYPE,
                                expiry_minutes: int = TOKEN_EXPIRY_HOURS * 60) -> str:
        """Create a 6-digit verification code and store it in the database."""
        return create_verification_code(user_id, token_type, expiry_minutes)

    def verify_code(self, code: str, token_type: str, user_id: Optional[int] = None) -> Optional[int]:
        """Verify a 6-digit code and return the associated user ID if valid."""
        return verify_code(code, token_type, user_id)

    def send_verification_email(self, email: str, verification_code: str, name: str = "User") -> bool:
        """
        Send a verification email with the provided code.

        Args:
            email: Email address to send to
            verification_code: The verification code to include
            name: User's name for personalization

        Returns:
            True if email was sent successfully, False otherwise
        """
        # For testing purposes, we'll use the send_email function directly
        # In a real implementation, you might want to create a user_id for this
        try:
            # Try to load HTML template first
            html_template_path = os.path.join(EMAIL_TEMPLATES_DIR, 'email_verification.html')
            if os.path.exists(html_template_path):
                # Read HTML template
                with open(html_template_path, 'r') as f:
                    template = f.read()

                # Replace placeholders
                email_body = template.replace('{name}', name)
                email_body = email_body.replace('{verification_code}', verification_code)

                # Send HTML email
                return send_email(
                    to_email=email,
                    subject="Verify Your EcoCycle Email Address",
                    message_body=email_body,
                    is_html=True
                )
            else:
                # Fallback to plain text
                email_body = f"""Hello {name},

Thank you for using EcoCycle! Please verify your email address by entering the 6-digit code below:

Your verification code: {verification_code}

This code will expire in 24 hours.

If you did not request this verification, please ignore this email.

The EcoCycle Team"""

                return send_email(
                    to_email=email,
                    subject="Verify Your EcoCycle Email Address",
                    message_body=email_body
                )
        except Exception as e:
            self.logger.error(f"Error sending verification email: {e}")
            return False

    def send_password_reset_email(self, user_id: int, email: str, username: str, name: str) -> bool:
        """Send a password reset email to the user with a 6-digit code."""
        return send_password_reset_email(user_id, email, username, name)

    def send_account_recovery_email(self, user_id: int, email: str, username: str, name: str) -> bool:
        """Send an account recovery email to the user with a 6-digit code."""
        return send_account_recovery_email(user_id, email, username, name)

    def send_two_factor_email(self, user_id: int, email: str, username: str, name: str) -> str:
        """Send a two-factor authentication email and return the code."""
        return send_two_factor_email(user_id, email, username, name)

    def send_data_reset_verification_email(self, user_id: int, email: str, username: str,
                                         name: str, reset_type: str, reset_description: str) -> bool:
        """Send a data reset verification email to the user with a 6-digit code."""
        return send_data_reset_verification_email(user_id, email, username, name, reset_type, reset_description)

def get_latest_verification_code(user_id: int, token_type: str = EMAIL_VERIFICATION_TYPE) -> Optional[str]:
    """
    Get the latest verification code for a user (for testing purposes).

    Args:
        user_id: User ID to get code for
        token_type: Type of code to get

    Returns:
        The latest verification code or None if not found
    """
    try:
        with database_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT token FROM verification_tokens
                WHERE user_id = ? AND token_type = ? AND used = 0
                ORDER BY created_at DESC LIMIT 1""",
                (user_id, token_type)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting verification code: {e}")
        return None

def send_email(to_email: str, subject: str, message_body: str, is_html: bool = False) -> bool:
    """
    Send an email using the configured SMTP server.

    Args:
        to_email: Recipient email address
        subject: Email subject
        message_body: Email body
        is_html: Whether the message body is HTML

    Returns:
        True if email was sent successfully, False otherwise
    """
    # Get email configuration from environment variables
    smtp_server = os.environ.get('EMAIL_SMTP_SERVER', os.environ.get('SMTP_SERVER'))
    smtp_port = os.environ.get('EMAIL_SMTP_PORT', os.environ.get('SMTP_PORT'))
    email_username = os.environ.get('EMAIL_USERNAME')
    email_password = os.environ.get('EMAIL_PASSWORD')
    email_from = os.environ.get('EMAIL_FROM', os.environ.get('EMAIL_SENDER'))
    use_tls = os.environ.get('EMAIL_USE_TLS', 'true').lower() in ('true', 'yes', '1', 'y')
    use_ssl = os.environ.get('EMAIL_USE_SSL', 'false').lower() in ('true', 'yes', '1', 'y')

    # Log email configuration (without password)
    logger.debug(f"Email config: server={smtp_server}, port={smtp_port}, username={email_username}, from={email_from}, TLS={use_tls}, SSL={use_ssl}")

    # Check if email configuration is available
    if not all([smtp_server, smtp_port, email_username, email_password, email_from]):
        logger.error("Email configuration is incomplete. Check environment variables.")
        return False

    try:
        # Create email message
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # Create a multipart message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = email_from if email_from else "noreply@ecocycle.app"
        message['To'] = to_email

        # Add plain text and HTML parts
        if is_html:
            # Create a plain text version as fallback
            plain_text = message_body.replace('<div class="code">', 'Code: ').replace('</div>', '\n')
            plain_text = re.sub(r'<.*?>', '', plain_text)
            message.attach(MIMEText(plain_text, 'plain'))

            # Add the HTML version
            message.attach(MIMEText(message_body, 'html'))
        else:
            # Just plain text
            message.attach(MIMEText(message_body, 'plain'))

        # Type checking to ensure we have valid values
        if not isinstance(smtp_server, str) or not isinstance(smtp_port, str):
            logger.error("SMTP server or port is not properly configured")
            return False

        if not isinstance(email_username, str) or not isinstance(email_password, str):
            logger.error("Email username or password is not properly configured")
            return False

        # Create SSL context
        context = ssl.create_default_context()

        # For development only: disable certificate verification
        # This is not secure for production, but helps with testing
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Connect to server based on SSL/TLS settings
        if use_ssl:
            # Use SMTP_SSL for direct SSL connection
            logger.debug("Using SMTP_SSL connection")
            with smtplib.SMTP_SSL(smtp_server, int(smtp_port), context=context) as server:
                server.login(email_username, email_password)
                server.send_message(message)
        else:
            # Use SMTP with STARTTLS
            logger.debug("Using SMTP with STARTTLS")
            with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
                server.ehlo()
                if use_tls:
                    server.starttls(context=context)
                    server.ehlo()
                server.login(email_username, email_password)
                server.send_message(message)

        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
