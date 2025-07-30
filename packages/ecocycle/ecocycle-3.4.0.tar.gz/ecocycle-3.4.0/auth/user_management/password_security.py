"""
EcoCycle - Password Security Module
Handles password hashing, verification, and security utilities.
"""
import os
import hashlib
import base64
import bcrypt
import logging

logger = logging.getLogger(__name__)

# Constants
SALT_LENGTH = 16
DEFAULT_ITERATIONS = 100000


class PasswordSecurity:
    """Handles password security operations."""
    
    @staticmethod
    def generate_salt() -> str:
        """
        Generate a cryptographically secure random salt.
        
        Returns:
            str: Base64-encoded salt
        """
        try:
            salt_bytes = os.urandom(SALT_LENGTH)
            return base64.b64encode(salt_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating salt: {e}")
            raise
    
    @staticmethod
    def hash_password(password: str, salt: str, iterations: int = DEFAULT_ITERATIONS) -> str:
        """
        Hash a password using PBKDF2 with SHA-256.
        
        Args:
            password: The password to hash
            salt: Base64-encoded salt
            iterations: Number of iterations for PBKDF2
            
        Returns:
            str: Base64-encoded password hash
        """
        try:
            # Decode the salt
            salt_bytes = base64.b64decode(salt.encode('utf-8'))
            
            # Hash the password
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt_bytes,
                iterations
            )
            
            # Return base64-encoded hash
            return base64.b64encode(password_hash).decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str, iterations: int = DEFAULT_ITERATIONS) -> bool:
        """
        Verify a password against a stored hash.
        
        Args:
            password: The password to verify
            stored_hash: The stored password hash
            salt: Base64-encoded salt
            iterations: Number of iterations used for hashing
            
        Returns:
            bool: True if password is correct, False otherwise
        """
        try:
            # Hash the provided password with the same salt
            computed_hash = PasswordSecurity.hash_password(password, salt, iterations)
            
            # Compare hashes using constant-time comparison
            return PasswordSecurity._constant_time_compare(computed_hash, stored_hash)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def _constant_time_compare(a: str, b: str) -> bool:
        """
        Perform constant-time string comparison to prevent timing attacks.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            bool: True if strings are equal, False otherwise
        """
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        
        return result == 0
    
    @staticmethod
    def check_password_strength(password: str) -> dict:
        """
        Check password strength and return detailed analysis.
        
        Args:
            password: Password to analyze
            
        Returns:
            dict: Password strength analysis
        """
        analysis = {
            'length': len(password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_number': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
            'strength_score': 0,
            'strength_text': 'Very Weak',
            'is_valid': False,
            'recommendations': []
        }
        
        # Calculate strength score
        if analysis['length'] >= 8:
            analysis['strength_score'] += 1
        if analysis['length'] >= 12:
            analysis['strength_score'] += 1
        if analysis['has_uppercase']:
            analysis['strength_score'] += 1
        if analysis['has_lowercase']:
            analysis['strength_score'] += 1
        if analysis['has_number']:
            analysis['strength_score'] += 1
        if analysis['has_special']:
            analysis['strength_score'] += 1
        
        # Determine strength text
        if analysis['strength_score'] <= 2:
            analysis['strength_text'] = 'Very Weak'
        elif analysis['strength_score'] == 3:
            analysis['strength_text'] = 'Weak'
        elif analysis['strength_score'] == 4:
            analysis['strength_text'] = 'Moderate'
        elif analysis['strength_score'] == 5:
            analysis['strength_text'] = 'Strong'
        else:
            analysis['strength_text'] = 'Very Strong'
        
        # Check if password meets minimum requirements
        analysis['is_valid'] = (
            analysis['length'] >= 8 and
            analysis['has_uppercase'] and
            analysis['has_lowercase'] and
            analysis['has_number']
        )
        
        # Generate recommendations
        if analysis['length'] < 8:
            analysis['recommendations'].append('Use at least 8 characters')
        if not analysis['has_uppercase']:
            analysis['recommendations'].append('Include at least one uppercase letter')
        if not analysis['has_lowercase']:
            analysis['recommendations'].append('Include at least one lowercase letter')
        if not analysis['has_number']:
            analysis['recommendations'].append('Include at least one number')
        if not analysis['has_special']:
            analysis['recommendations'].append('Consider adding special characters for extra security')
        if analysis['length'] < 12:
            analysis['recommendations'].append('Consider using 12+ characters for better security')
        
        return analysis
    
    @staticmethod
    def hash_password_bcrypt(password: str) -> str:
        """
        Hash a password using bcrypt (alternative method).
        
        Args:
            password: The password to hash
            
        Returns:
            str: Bcrypt hash
        """
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            return password_hash.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password with bcrypt: {e}")
            raise
    
    @staticmethod
    def verify_password_bcrypt(password: str, stored_hash: str) -> bool:
        """
        Verify a password against a bcrypt hash.
        
        Args:
            password: The password to verify
            stored_hash: The stored bcrypt hash
            
        Returns:
            bool: True if password is correct, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password with bcrypt: {e}")
            return False
