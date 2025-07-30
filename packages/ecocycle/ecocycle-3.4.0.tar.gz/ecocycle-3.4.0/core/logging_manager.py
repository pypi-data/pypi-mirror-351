#!/usr/bin/env python3
"""
EcoCycle - Logging Manager Module
Provides centralized logging and monitoring capabilities for the application.
"""
import logging
import os
import sys
import time
import json
import socket
import platform
import threading
import traceback
from typing import Dict, Any, Optional, List, Union, Callable
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
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

# Log file paths
APP_LOG_FILE = os.path.join(LOG_DIR, 'ecocycle.log')
DEBUG_LOG_FILE = os.path.join(LOG_DIR, 'debug.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'error.log')
PERFORMANCE_LOG_FILE = os.path.join(LOG_DIR, 'performance.log')
AUDIT_LOG_FILE = os.path.join(LOG_DIR, 'audit.log')
METRICS_FILE = os.path.join(DEBUG_DIR, 'metrics.json')

# Log levels
LOG_LEVEL_DEBUG = logging.DEBUG
LOG_LEVEL_INFO = logging.INFO
LOG_LEVEL_WARNING = logging.WARNING
LOG_LEVEL_ERROR = logging.ERROR
LOG_LEVEL_CRITICAL = logging.CRITICAL

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Performance metrics
_performance_metrics = {}
_metrics_lock = threading.Lock()


def setup_logger(name: str, 
                log_file: str, 
                level: int = logging.INFO, 
                log_format: str = DEFAULT_LOG_FORMAT,
                max_bytes: int = 10485760,  # 10MB
                backup_count: int = 5) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Log file path
        level: Logging level
        log_format: Log format string
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)  # Only show errors and above in console
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Set up loggers
app_logger = setup_logger('app', APP_LOG_FILE, LOG_LEVEL_INFO)
debug_logger = setup_logger('debug', DEBUG_LOG_FILE, LOG_LEVEL_DEBUG)
error_logger = setup_logger('error', ERROR_LOG_FILE, LOG_LEVEL_ERROR)
performance_logger = setup_logger('performance', PERFORMANCE_LOG_FILE, LOG_LEVEL_INFO)
audit_logger = setup_logger(
    'audit', 
    AUDIT_LOG_FILE, 
    LOG_LEVEL_INFO,
    '%(asctime)s - %(levelname)s - USER:%(user)s - ACTION:%(action)s - RESOURCE:%(resource)s - RESULT:%(result)s'
)


def log_debug(message: str, module: str = 'app') -> None:
    """
    Log a debug message.
    
    Args:
        message: Debug message
        module: Module name
    """
    debug_logger.debug(f"[{module}] {message}")


def log_info(message: str, module: str = 'app') -> None:
    """
    Log an info message.
    
    Args:
        message: Info message
        module: Module name
    """
    app_logger.info(f"[{module}] {message}")


def log_warning(message: str, module: str = 'app') -> None:
    """
    Log a warning message.
    
    Args:
        message: Warning message
        module: Module name
    """
    app_logger.warning(f"[{module}] {message}")


def log_error(message: str, module: str = 'app', exc_info: bool = False) -> None:
    """
    Log an error message.
    
    Args:
        message: Error message
        module: Module name
        exc_info: Whether to include exception info
    """
    error_logger.error(f"[{module}] {message}", exc_info=exc_info)
    app_logger.error(f"[{module}] {message}", exc_info=exc_info)


def log_critical(message: str, module: str = 'app', exc_info: bool = True) -> None:
    """
    Log a critical message.
    
    Args:
        message: Critical message
        module: Module name
        exc_info: Whether to include exception info
    """
    error_logger.critical(f"[{module}] {message}", exc_info=exc_info)
    app_logger.critical(f"[{module}] {message}", exc_info=exc_info)


def log_audit(action: str, 
             user: str = 'system', 
             resource: str = '', 
             result: str = 'success',
             details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an audit event.
    
    Args:
        action: Action performed
        user: User who performed the action
        resource: Resource affected by the action
        result: Result of the action
        details: Additional details
    """
    extra = {
        'user': user,
        'action': action,
        'resource': resource,
        'result': result
    }
    
    # Log the audit event
    audit_logger.info('', extra=extra)
    
    # Log details if provided
    if details:
        debug_logger.debug(f"AUDIT DETAILS - ACTION:{action} - USER:{user} - {json.dumps(details)}")


def log_performance(operation: str, 
                   duration: float, 
                   module: str = 'app',
                   details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a performance metric.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        module: Module name
        details: Additional details
    """
    # Log to performance logger
    performance_logger.info(f"[{module}] {operation} - {duration:.6f}s")
    
    # Update performance metrics
    with _metrics_lock:
        if operation not in _performance_metrics:
            _performance_metrics[operation] = {
                'count': 0,
                'total_duration': 0,
                'min_duration': float('inf'),
                'max_duration': 0,
                'module': module
            }
        
        metrics = _performance_metrics[operation]
        metrics['count'] += 1
        metrics['total_duration'] += duration
        metrics['min_duration'] = min(metrics['min_duration'], duration)
        metrics['max_duration'] = max(metrics['max_duration'], duration)
        
        # Save metrics periodically (every 10 operations)
        if metrics['count'] % 10 == 0:
            save_metrics()


def time_function(func: Callable) -> Callable:
    """
    Decorator to time a function and log its performance.
    
    Args:
        func: Function to time
        
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        
        # Log performance
        module = func.__module__ if hasattr(func, '__module__') else 'unknown'
        log_performance(func.__name__, duration, module)
        
        return result
    
    return wrapper


def save_metrics() -> None:
    """Save performance metrics to file."""
    try:
        with _metrics_lock:
            # Calculate averages
            metrics_with_avg = {}
            for op, metrics in _performance_metrics.items():
                metrics_copy = metrics.copy()
                if metrics_copy['count'] > 0:
                    metrics_copy['avg_duration'] = metrics_copy['total_duration'] / metrics_copy['count']
                metrics_with_avg[op] = metrics_copy
            
            # Add system info
            system_info = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'timestamp': time.time()
            }
            
            data = {
                'system_info': system_info,
                'metrics': metrics_with_avg
            }
            
            # Save to file
            with open(METRICS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
    
    except Exception as e:
        error_logger.error(f"Failed to save metrics: {e}", exc_info=True)


def get_metrics() -> Dict[str, Any]:
    """
    Get performance metrics.
    
    Returns:
        Dictionary of performance metrics
    """
    with _metrics_lock:
        # Calculate averages
        metrics_with_avg = {}
        for op, metrics in _performance_metrics.items():
            metrics_copy = metrics.copy()
            if metrics_copy['count'] > 0:
                metrics_copy['avg_duration'] = metrics_copy['total_duration'] / metrics_copy['count']
            metrics_with_avg[op] = metrics_copy
        
        return metrics_with_avg


def clear_metrics() -> None:
    """Clear performance metrics."""
    with _metrics_lock:
        _performance_metrics.clear()
        
        # Save empty metrics
        save_metrics()


def get_log_files() -> Dict[str, str]:
    """
    Get log file paths.
    
    Returns:
        Dictionary of log file paths
    """
    return {
        'app': APP_LOG_FILE,
        'debug': DEBUG_LOG_FILE,
        'error': ERROR_LOG_FILE,
        'performance': PERFORMANCE_LOG_FILE,
        'audit': AUDIT_LOG_FILE,
        'metrics': METRICS_FILE
    }


def get_log_contents(log_type: str, max_lines: int = 100) -> List[str]:
    """
    Get the contents of a log file.
    
    Args:
        log_type: Type of log file ('app', 'debug', 'error', 'performance', 'audit')
        max_lines: Maximum number of lines to return
        
    Returns:
        List of log lines
    """
    log_files = get_log_files()
    
    if log_type not in log_files:
        return [f"Invalid log type: {log_type}"]
    
    log_file = log_files[log_type]
    
    if not os.path.exists(log_file):
        return [f"Log file does not exist: {log_file}"]
    
    try:
        with open(log_file, 'r') as f:
            # Read the last max_lines lines
            lines = f.readlines()
            return lines[-max_lines:] if len(lines) > max_lines else lines
    
    except Exception as e:
        return [f"Error reading log file: {e}"]
