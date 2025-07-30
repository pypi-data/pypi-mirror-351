#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EcoCycle - Configuration Module
Contains configuration constants and settings for the application.
This module provides backward compatibility with the new config_manager.
"""
import os
import logging

# Try to import the config_manager
try:
    from config.config_manager import config_manager
    # Import get_config and set_config for external use
    # These are imported for external modules to use, so we need to suppress the "unused import" warning
    from config.config_manager import get_config, set_config  # noqa
except ImportError:
    # If config_manager is not available, use the legacy configuration
    config_manager = None

# Determine the project root directory (where config.py is located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Main directories
LOG_DIR = os.path.join(PROJECT_ROOT, 'Logs')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')
USER_DATA_DIR = os.path.join(DATA_DIR, 'user')
DEBUG_DIR = os.path.join(DATA_DIR, 'debug')
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'database_backups')

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# File paths
LOG_FILENAME = os.path.join(LOG_DIR, 'ecocycle_debug.log')
CACHE_FILENAME = os.path.join(CACHE_DIR, '.ecocycle_cache')
DATABASE_FILE = os.path.join(PROJECT_ROOT, 'ecocycle.db')
USERS_FILE = os.path.join(USER_DATA_DIR, 'users.json')
SESSION_FILE = os.path.join(USER_DATA_DIR, 'session.json')
GOOGLE_AUTH_FILE = os.path.join(PROJECT_ROOT, 'client_secrets.json')

# Cache files
ROUTES_CACHE_FILE = os.path.join(CACHE_DIR, 'routes_cache.json')
WEATHER_CACHE_FILE = os.path.join(CACHE_DIR, 'weather_cache.json')
AI_ROUTES_FILE = os.path.join(USER_DATA_DIR, 'ai_routes.json')

# Preferences files
PREFERENCES_DIR = os.path.join(PROJECT_ROOT, 'config', 'preferences')
os.makedirs(PREFERENCES_DIR, exist_ok=True)
ACHIEVEMENTS_FILE = os.path.join(PREFERENCES_DIR, 'achievements.json')
CHALLENGES_FILE = os.path.join(PREFERENCES_DIR, 'challenges.json')
LEADERBOARD_FILE = os.path.join(PREFERENCES_DIR, 'leaderboard.json')
NOTIFICATION_SETTINGS_FILE = os.path.join(PREFERENCES_DIR, 'notification_settings.json')

# Application version
VERSION = "3.4.0"

# User input constants
YES_RESPONSES = ['y', 'yes', '1', 'true', 'ok', 'sure', 'yeah', 'yep', 'yup', 'yea']
NO_RESPONSES = ['n', 'no', '0', 'false', 'nah', 'nope', 'no way', 'not really']

# Debug mode settings
DEBUG_MODE = os.environ.get('DEBUG', '').lower() in YES_RESPONSES

# Configure logging based on debug mode
if DEBUG_MODE:
    logging.basicConfig(
        filename=LOG_FILENAME,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s'
    )
else:
    logging.basicConfig(
        filename=LOG_FILENAME,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s'
    )

# If config_manager is available, use it to set up configuration
if config_manager:
    # Update config_manager with legacy values for backward compatibility
    config_manager.set('paths.log_dir', LOG_DIR)
    config_manager.set('paths.data_dir', DATA_DIR)
    config_manager.set('paths.cache_dir', CACHE_DIR)
    config_manager.set('paths.user_data_dir', USER_DATA_DIR)
    config_manager.set('paths.debug_dir', DEBUG_DIR)
    config_manager.set('paths.backup_dir', BACKUP_DIR)
    config_manager.set('paths.database_file', DATABASE_FILE)
    config_manager.set('paths.users_file', USERS_FILE)
    config_manager.set('paths.session_file', SESSION_FILE)
    config_manager.set('paths.google_auth_file', GOOGLE_AUTH_FILE)
    config_manager.set('cache.routes_cache_file', ROUTES_CACHE_FILE)
    config_manager.set('cache.weather_cache_file', WEATHER_CACHE_FILE)
    config_manager.set('app.version', VERSION)
    config_manager.set('app.debug_mode', DEBUG_MODE)

    # Get values from config_manager for backward compatibility
    # Google Sheets settings
    USER_DATA_SHEET = config_manager.get('google_sheets.user_data_sheet', "UserData")
    ADMIN_ACTIONS_SHEET = config_manager.get('google_sheets.admin_actions_sheet', "AdminActions")
    EMAIL_LOG_SHEET = config_manager.get('google_sheets.email_log_sheet', "EmailLog")

    # Google Sheets column indices (zero-based)
    COL_USER_NAME = config_manager.get('google_sheets.col_user_name', 0)
    COL_LAST_DIST = config_manager.get('google_sheets.col_last_dist', 1)
    COL_LAST_PRICE = config_manager.get('google_sheets.col_last_price', 2)
    COL_CUM_POINTS = config_manager.get('google_sheets.col_cum_points', 3)
    COL_CUM_PRICE = config_manager.get('google_sheets.col_cum_price', 4)
    COL_CUM_DIST = config_manager.get('google_sheets.col_cum_dist', 5)
    COL_CUM_CO2 = config_manager.get('google_sheets.col_cum_co2', 6)
    COL_CUM_CALORIES = config_manager.get('google_sheets.col_cum_calories', 7)

    # Environmental constants
    CO2_PER_KM = config_manager.get('environmental.co2_per_km', 0.192)
    CALORIES_PER_KM = config_manager.get('environmental.calories_per_km', 50)
    POINTS_PER_KM = config_manager.get('environmental.points_per_km', 10)
    FUEL_EFFICIENCY = config_manager.get('environmental.fuel_efficiency', 0.08)
    FUEL_PRICE = config_manager.get('environmental.fuel_price', 1.50)
    TREE_CO2_PER_YEAR = config_manager.get('environmental.tree_co2_per_year', 25)

    # Admin settings
    ADMIN_PANEL_TIMEOUT = config_manager.get('admin.panel_timeout', 300)

    # Email verification settings
    BASE_URL = config_manager.get('email.base_url', os.environ.get('BASE_URL', 'http://localhost:5050'))

else:
    # Legacy configuration values
    # Google Sheets settings
    USER_DATA_SHEET = "UserData"
    ADMIN_ACTIONS_SHEET = "AdminActions"
    EMAIL_LOG_SHEET = "EmailLog"

    # Google Sheets column indices (zero-based)
    COL_USER_NAME = 0
    COL_LAST_DIST = 1
    COL_LAST_PRICE = 2
    COL_CUM_POINTS = 3
    COL_CUM_PRICE = 4
    COL_CUM_DIST = 5
    COL_CUM_CO2 = 6
    COL_CUM_CALORIES = 7

    # Environmental constants
    CO2_PER_KM = 0.192  # kg of CO2 saved per km (compared to driving)
    CALORIES_PER_KM = 50  # calories burned per km (average)
    POINTS_PER_KM = 10  # eco points earned per km
    FUEL_EFFICIENCY = 0.08  # liters per km (8L/100km)
    FUEL_PRICE = 1.50  # price per liter (default)
    TREE_CO2_PER_YEAR = 25  # kg of CO2 absorbed by a tree per year

    # Admin settings
    ADMIN_PANEL_TIMEOUT = 300  # seconds before admin session expires

    # Email verification settings
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5050')  # Base URL for email verification links

    # Legacy get_config function
    def get_config(key, default=None):
        """
        Get a configuration value from the module.

        Args:
            key (str): The configuration key to get
            default: Default value if key is not found

        Returns:
            The configuration value or default
        """
        return globals().get(key, default)

    # Legacy set_config function (does nothing in legacy mode)
    def set_config(key, value):
        """
        Set a configuration value (does nothing in legacy mode).

        Args:
            key (str): The configuration key to set
            value: The value to set
        """
        # Suppress unused parameter warnings
        _ = key
        _ = value
