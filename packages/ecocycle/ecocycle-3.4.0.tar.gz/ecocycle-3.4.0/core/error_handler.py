#!/usr/bin/env python3
"""
EcoCycle - Error Handling Module
Provides centralized error handling and recovery mechanisms for the application.
"""
import logging
import os
import sys
import traceback
import json
import time
from typing import Dict, Any, Optional, Callable, List, Tuple, Union
from functools import wraps

# Import config module for paths
try:
    import config.config as config
    # Use config module for log directory
    LOG_DIR = config.LOG_DIR
    DEBUG_DIR = config.DEBUG_DIR
except ImportError:
    # Fallback if config module is not available
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Logs')
    DEBUG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'debug')

# Ensure log and debug directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'error_handler.log'))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Error severity levels
SEVERITY_INFO = 'INFO'
SEVERITY_WARNING = 'WARNING'
SEVERITY_ERROR = 'ERROR'
SEVERITY_CRITICAL = 'CRITICAL'

# Error categories
CATEGORY_NETWORK = 'NETWORK'
CATEGORY_DATABASE = 'DATABASE'
CATEGORY_FILE_SYSTEM = 'FILE_SYSTEM'
CATEGORY_USER_INPUT = 'USER_INPUT'
CATEGORY_DEPENDENCY = 'DEPENDENCY'
CATEGORY_AUTHENTICATION = 'AUTHENTICATION'
CATEGORY_PERMISSION = 'PERMISSION'
CATEGORY_VALIDATION = 'VALIDATION'
CATEGORY_SYSTEM = 'SYSTEM'
CATEGORY_APPLICATION = 'APPLICATION'

# Error recovery strategies
STRATEGY_RETRY = 'RETRY'
STRATEGY_FALLBACK = 'FALLBACK'
STRATEGY_IGNORE = 'IGNORE'
STRATEGY_ABORT = 'ABORT'
STRATEGY_USER_INTERVENTION = 'USER_INTERVENTION'

# Path for error log file
ERROR_LOG_FILE = os.path.join(DEBUG_DIR, 'error_log.json')


class EcoCycleError(Exception):
    """Base exception class for EcoCycle application."""
    
    def __init__(self, 
                 message: str, 
                 severity: str = SEVERITY_ERROR,
                 category: str = CATEGORY_APPLICATION,
                 recovery_strategy: str = STRATEGY_ABORT,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            severity: Error severity level
            category: Error category
            recovery_strategy: Recovery strategy
            details: Additional error details
        """
        self.message = message
        self.severity = severity
        self.category = category
        self.recovery_strategy = recovery_strategy
        self.details = details or {}
        self.timestamp = time.time()
        self.traceback = traceback.format_exc()
        
        # Log the error
        self._log_error()
        
        super().__init__(message)
    
    def _log_error(self) -> None:
        """Log the error to the error log file."""
        try:
            # Create error log entry
            error_entry = {
                'timestamp': self.timestamp,
                'message': self.message,
                'severity': self.severity,
                'category': self.category,
                'recovery_strategy': self.recovery_strategy,
                'details': self.details,
                'traceback': self.traceback
            }
            
            # Load existing error log
            error_log = []
            if os.path.exists(ERROR_LOG_FILE):
                try:
                    with open(ERROR_LOG_FILE, 'r') as f:
                        error_log = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    error_log = []
            
            # Add new error entry
            error_log.append(error_entry)
            
            # Save error log
            with open(ERROR_LOG_FILE, 'w') as f:
                json.dump(error_log, f, indent=2)
            
            # Log to logger
            log_message = f"{self.severity} - {self.category}: {self.message}"
            if self.severity == SEVERITY_CRITICAL:
                logger.critical(log_message)
            elif self.severity == SEVERITY_ERROR:
                logger.error(log_message)
            elif self.severity == SEVERITY_WARNING:
                logger.warning(log_message)
            else:
                logger.info(log_message)
        
        except Exception as e:
            # If error logging fails, log to stderr as a last resort
            print(f"Error logging failed: {e}", file=sys.stderr)
            print(f"Original error: {self.message}", file=sys.stderr)


class NetworkError(EcoCycleError):
    """Exception raised for network-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_NETWORK)
        kwargs.setdefault('recovery_strategy', STRATEGY_RETRY)
        super().__init__(message, **kwargs)


class DatabaseError(EcoCycleError):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_DATABASE)
        kwargs.setdefault('recovery_strategy', STRATEGY_FALLBACK)
        super().__init__(message, **kwargs)


class FileSystemError(EcoCycleError):
    """Exception raised for file system-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_FILE_SYSTEM)
        kwargs.setdefault('recovery_strategy', STRATEGY_FALLBACK)
        super().__init__(message, **kwargs)


class UserInputError(EcoCycleError):
    """Exception raised for user input-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_USER_INPUT)
        kwargs.setdefault('severity', SEVERITY_WARNING)
        kwargs.setdefault('recovery_strategy', STRATEGY_USER_INTERVENTION)
        super().__init__(message, **kwargs)


class DependencyError(EcoCycleError):
    """Exception raised for dependency-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_DEPENDENCY)
        kwargs.setdefault('recovery_strategy', STRATEGY_FALLBACK)
        super().__init__(message, **kwargs)


class AuthenticationError(EcoCycleError):
    """Exception raised for authentication-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_AUTHENTICATION)
        kwargs.setdefault('recovery_strategy', STRATEGY_USER_INTERVENTION)
        super().__init__(message, **kwargs)


class PermissionError(EcoCycleError):
    """Exception raised for permission-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_PERMISSION)
        kwargs.setdefault('recovery_strategy', STRATEGY_ABORT)
        super().__init__(message, **kwargs)


class ValidationError(EcoCycleError):
    """Exception raised for validation-related errors."""
    
    def __init__(self, message: str, **kwargs):
        """Initialize the exception."""
        kwargs.setdefault('category', CATEGORY_VALIDATION)
        kwargs.setdefault('severity', SEVERITY_WARNING)
        kwargs.setdefault('recovery_strategy', STRATEGY_USER_INTERVENTION)
        super().__init__(message, **kwargs)


def handle_error(error: Exception, 
                 display_callback: Optional[Callable[[str], None]] = None) -> None:
    """
    Handle an error by logging it and displaying a message to the user.
    
    Args:
        error: The exception to handle
        display_callback: Optional callback function to display error message to user
    """
    if isinstance(error, EcoCycleError):
        # EcoCycleError already logs itself, just display to user if callback provided
        if display_callback:
            display_callback(f"{error.severity}: {error.message}")
    else:
        # Convert to EcoCycleError to log it
        eco_error = EcoCycleError(
            message=str(error),
            severity=SEVERITY_ERROR,
            category=CATEGORY_APPLICATION,
            recovery_strategy=STRATEGY_ABORT,
            details={'original_error_type': type(error).__name__}
        )
        
        # Display to user if callback provided
        if display_callback:
            display_callback(f"ERROR: {str(error)}")


def retry(max_attempts: int = 3, 
          delay: float = 1.0,
          exceptions: Tuple[Exception, ...] = (Exception,),
          on_failure: Optional[Callable[[], Any]] = None) -> Callable:
    """
    Decorator to retry a function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retry attempts in seconds
        exceptions: Tuple of exceptions to catch and retry
        on_failure: Function to call if all retry attempts fail
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} failed: {e}")
                    
                    if attempt < max_attempts:
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} retry attempts for {func.__name__} failed")
                        if on_failure:
                            return on_failure()
                        raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator


def with_fallback(fallback_function: Callable[[], Any]) -> Callable:
    """
    Decorator to provide a fallback function if the primary function fails.
    
    Args:
        fallback_function: Function to call if the primary function fails
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Function {func.__name__} failed, using fallback: {e}")
                return fallback_function()
        
        return wrapper
    
    return decorator


def get_error_log() -> List[Dict[str, Any]]:
    """
    Get the error log.
    
    Returns:
        List of error log entries
    """
    if os.path.exists(ERROR_LOG_FILE):
        try:
            with open(ERROR_LOG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []


def clear_error_log() -> None:
    """Clear the error log."""
    if os.path.exists(ERROR_LOG_FILE):
        try:
            os.remove(ERROR_LOG_FILE)
            logger.info("Error log cleared")
        except OSError as e:
            logger.error(f"Failed to clear error log: {e}")
