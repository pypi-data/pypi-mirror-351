#!/usr/bin/env python3
"""
EcoCycle - Configuration Manager Module
Provides a flexible configuration system with profiles.
"""
import os
import json
import logging
import yaml
import copy
from typing import Dict, Any, Optional, List, Union, Set

# Determine the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration directories
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
PROFILES_DIR = os.path.join(CONFIG_DIR, 'profiles')
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, 'default_config.yaml')
USER_CONFIG_FILE = os.path.join(CONFIG_DIR, 'user_config.yaml')

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(PROFILES_DIR, exist_ok=True)

# Default configuration values
DEFAULT_CONFIG = {
    'app': {
        'name': 'EcoCycle',
        'version': '3.0.0',
        'debug_mode': False,
        'theme': 'light',
        'language': 'en',
        'auto_update': True,
        'check_dependencies': True,
        'max_log_size': 10485760,  # 10MB
        'log_backup_count': 5,
        'session_timeout': 3600,  # 1 hour
    },
    'paths': {
        'project_root': PROJECT_ROOT,
        'log_dir': os.path.join(PROJECT_ROOT, 'Logs'),
        'data_dir': os.path.join(PROJECT_ROOT, 'data'),
        'cache_dir': os.path.join(PROJECT_ROOT, 'data', 'cache'),
        'user_data_dir': os.path.join(PROJECT_ROOT, 'data', 'user'),
        'debug_dir': os.path.join(PROJECT_ROOT, 'data', 'debug'),
        'backup_dir': os.path.join(PROJECT_ROOT, 'database_backups'),
        'database_file': os.path.join(PROJECT_ROOT, 'ecocycle.db'),
        'users_file': os.path.join(PROJECT_ROOT, 'data', 'user', 'users.json'),
        'session_file': os.path.join(PROJECT_ROOT, 'data', 'user', 'session.json'),
        'google_auth_file': os.path.join(PROJECT_ROOT, 'client_secrets.json'),
    },
    'cache': {
        'enabled': True,
        'ttl': 3600,  # 1 hour
        'max_size': 104857600,  # 100MB
        'routes_cache_file': os.path.join(PROJECT_ROOT, 'data', 'cache', 'routes_cache.json'),
        'weather_cache_file': os.path.join(PROJECT_ROOT, 'data', 'cache', 'weather_cache.json'),
    },
    'email': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': os.environ.get('EMAIL_USERNAME', ''),
        'smtp_password': os.environ.get('EMAIL_PASSWORD', ''),
        'from_email': os.environ.get('FROM_EMAIL', 'nexus.ecocycle@gmail.com'),
        'verification_required': True,
        'verification_code_length': 6,
        'verification_code_ttl': 3600,  # 1 hour
    },
    'security': {
        'password_min_length': 8,
        'password_require_uppercase': True,
        'password_require_lowercase': True,
        'password_require_number': True,
        'password_require_special': True,
        'session_secret_key': os.environ.get('SESSION_SECRET_KEY', 'default-secret-key'),
        'jwt_secret_key': os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret'),
        'jwt_expiration': 86400,  # 24 hours
    },
    'developer': {
        'enabled': os.environ.get('DEVELOPER_MODE_ENABLED', 'false').lower() == 'true',
        'username': os.environ.get('DEVELOPER_USERNAME', 'dev_admin'),
        'password_hash': os.environ.get('DEVELOPER_PASSWORD_HASH', ''),
        'session_timeout': 1800,  # 30 minutes
        'audit_logging': True,
        'bypass_restrictions': True,
        'debug_level': 'DEBUG',
    },
    'features': {
        'route_planning': True,
        'weather_integration': True,
        'achievements': True,
        'challenges': True,
        'leaderboard': True,
        'notifications': True,
        'social_sharing': True,
        'analytics': True,
    },
    'environmental': {
        'co2_per_km': 0.192,  # kg of CO2 saved per km (compared to driving)
        'calories_per_km': 50,  # calories burned per km (average)
        'points_per_km': 10,  # eco points earned per km
        'fuel_efficiency': 0.08,  # liters per km (8L/100km)
        'fuel_price': 1.50,  # price per liter (default)
        'tree_co2_per_year': 25,  # kg of CO2 absorbed by a tree per year
    },
    'ui': {
        'theme': 'light',
        'accent_color': '#4CAF50',
        'font_size': 'medium',
        'animations_enabled': True,
        'compact_mode': False,
        'sidebar_visible': True,
        'show_welcome_screen': True,
    },
    'notifications': {
        'enabled': True,
        'email_notifications': True,
        'push_notifications': False,
        'achievement_notifications': True,
        'challenge_notifications': True,
        'leaderboard_notifications': True,
        'weather_alerts': True,
    },
    'api': {
        'google_maps_key': os.environ.get('GOOGLE_MAPS_API_KEY', ''),
        'openweathermap_key': os.environ.get('OPENWEATHERMAP_API_KEY', ''),
        'strava_client_id': os.environ.get('STRAVA_CLIENT_ID', ''),
        'strava_client_secret': os.environ.get('STRAVA_CLIENT_SECRET', ''),
    },
    'logging': {
        'level': 'INFO',
        'file_logging': True,
        'console_logging': True,
        'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'log_file': os.path.join(PROJECT_ROOT, 'Logs', 'ecocycle.log'),
        'error_log_file': os.path.join(PROJECT_ROOT, 'Logs', 'error.log'),
        'debug_log_file': os.path.join(PROJECT_ROOT, 'Logs', 'debug.log'),
    },
}


class ConfigManager:
    """Configuration manager class for handling application configuration."""

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of ConfigManager exists."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the configuration manager."""
        if self._initialized:
            return

        self._config = copy.deepcopy(DEFAULT_CONFIG)
        self._active_profile = 'default'
        self._profiles = {}
        self._initialized = True

        # Create default configuration file if it doesn't exist
        if not os.path.exists(DEFAULT_CONFIG_FILE):
            self._save_yaml(DEFAULT_CONFIG_FILE, DEFAULT_CONFIG)

        # Load default configuration
        self.load_config()

        # Load profiles
        self._load_profiles()

    def _save_yaml(self, file_path: str, data: Dict[str, Any]) -> None:
        """
        Save data to a YAML file.

        Args:
            file_path: Path to the YAML file
            data: Data to save
        """
        try:
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            logging.error(f"Error saving YAML file {file_path}: {e}")

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Load data from a YAML file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Dictionary of loaded data
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            return {}
        except Exception as e:
            logging.error(f"Error loading YAML file {file_path}: {e}")
            return {}

    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep update a nested dictionary.

        Args:
            target: Target dictionary to update
            source: Source dictionary with updates

        Returns:
            Updated dictionary
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                target[key] = self._deep_update(target[key], value)
            else:
                target[key] = value
        return target

    def load_config(self) -> None:
        """Load configuration from files."""
        # Start with default configuration
        self._config = copy.deepcopy(DEFAULT_CONFIG)

        # Load from default configuration file
        default_config = self._load_yaml(DEFAULT_CONFIG_FILE)
        if default_config:
            self._config = self._deep_update(self._config, default_config)

        # Load from user configuration file
        user_config = self._load_yaml(USER_CONFIG_FILE)
        if user_config:
            self._config = self._deep_update(self._config, user_config)

        # Ensure directories exist
        for path_key, path_value in self._config['paths'].items():
            if path_key.endswith('_dir'):
                os.makedirs(path_value, exist_ok=True)

    def save_config(self) -> None:
        """Save configuration to user configuration file."""
        self._save_yaml(USER_CONFIG_FILE, self._config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (dot notation for nested keys)
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def _load_profiles(self) -> None:
        """Load configuration profiles."""
        self._profiles = {'default': copy.deepcopy(self._config)}

        # Load profiles from profiles directory
        if os.path.exists(PROFILES_DIR):
            for filename in os.listdir(PROFILES_DIR):
                if filename.endswith('.yaml'):
                    profile_name = os.path.splitext(filename)[0]
                    profile_path = os.path.join(PROFILES_DIR, filename)
                    profile_config = self._load_yaml(profile_path)

                    if profile_config:
                        # Create profile by starting with default config and applying profile-specific changes
                        self._profiles[profile_name] = copy.deepcopy(self._config)
                        self._profiles[profile_name] = self._deep_update(self._profiles[profile_name], profile_config)

    def get_profiles(self) -> List[str]:
        """
        Get list of available profiles.

        Returns:
            List of profile names
        """
        return list(self._profiles.keys())

    def create_profile(self, profile_name: str, base_profile: str = 'default') -> bool:
        """
        Create a new profile.

        Args:
            profile_name: Name of the new profile
            base_profile: Name of the profile to base the new profile on

        Returns:
            True if profile was created, False otherwise
        """
        if profile_name in self._profiles:
            return False

        if base_profile not in self._profiles:
            base_profile = 'default'

        # Create new profile based on base profile
        self._profiles[profile_name] = copy.deepcopy(self._profiles[base_profile])

        # Save profile to file
        profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.yaml")
        self._save_yaml(profile_path, self._profiles[profile_name])

        return True

    def delete_profile(self, profile_name: str) -> bool:
        """
        Delete a profile.

        Args:
            profile_name: Name of the profile to delete

        Returns:
            True if profile was deleted, False otherwise
        """
        if profile_name == 'default':
            return False

        if profile_name not in self._profiles:
            return False

        # Delete profile from memory
        del self._profiles[profile_name]

        # Delete profile file
        profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.yaml")
        if os.path.exists(profile_path):
            try:
                os.remove(profile_path)
            except Exception as e:
                logging.error(f"Error deleting profile file {profile_path}: {e}")
                return False

        # If active profile was deleted, switch to default
        if self._active_profile == profile_name:
            self.activate_profile('default')

        return True

    def activate_profile(self, profile_name: str) -> bool:
        """
        Activate a profile.

        Args:
            profile_name: Name of the profile to activate

        Returns:
            True if profile was activated, False otherwise
        """
        if profile_name not in self._profiles:
            return False

        # Set active profile
        self._active_profile = profile_name

        # Update current configuration with profile configuration
        self._config = copy.deepcopy(self._profiles[profile_name])

        return True

    def get_active_profile(self) -> str:
        """
        Get the name of the active profile.

        Returns:
            Name of the active profile
        """
        return self._active_profile

    def update_profile(self, profile_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update a profile with new values.

        Args:
            profile_name: Name of the profile to update
            updates: Dictionary of updates to apply

        Returns:
            True if profile was updated, False otherwise
        """
        if profile_name not in self._profiles:
            return False

        # Update profile
        self._profiles[profile_name] = self._deep_update(self._profiles[profile_name], updates)

        # Save profile to file
        profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.yaml")
        self._save_yaml(profile_path, self._profiles[profile_name])

        # If active profile was updated, update current configuration
        if self._active_profile == profile_name:
            self._config = copy.deepcopy(self._profiles[profile_name])

        return True

    def reset_to_default(self) -> None:
        """Reset configuration to default values."""
        self._config = copy.deepcopy(DEFAULT_CONFIG)
        self.save_config()

        # Reset profiles
        self._profiles = {'default': copy.deepcopy(DEFAULT_CONFIG)}
        self._active_profile = 'default'

        # Delete all profile files
        if os.path.exists(PROFILES_DIR):
            for filename in os.listdir(PROFILES_DIR):
                if filename.endswith('.yaml'):
                    try:
                        os.remove(os.path.join(PROFILES_DIR, filename))
                    except Exception as e:
                        logging.error(f"Error deleting profile file {filename}: {e}")

    def export_config(self, file_path: str) -> bool:
        """
        Export current configuration to a file.

        Args:
            file_path: Path to export configuration to

        Returns:
            True if configuration was exported, False otherwise
        """
        try:
            self._save_yaml(file_path, self._config)
            return True
        except Exception as e:
            logging.error(f"Error exporting configuration to {file_path}: {e}")
            return False

    def import_config(self, file_path: str) -> bool:
        """
        Import configuration from a file.

        Args:
            file_path: Path to import configuration from

        Returns:
            True if configuration was imported, False otherwise
        """
        try:
            imported_config = self._load_yaml(file_path)
            if imported_config:
                self._config = self._deep_update(copy.deepcopy(DEFAULT_CONFIG), imported_config)
                self.save_config()
                return True
            return False
        except Exception as e:
            logging.error(f"Error importing configuration from {file_path}: {e}")
            return False


# Create a singleton instance
config_manager = ConfigManager()


# Compatibility functions for existing code
def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value.

    Args:
        key: Configuration key
        default: Default value if key is not found

    Returns:
        Configuration value or default
    """
    return config_manager.get(key, default)


def set_config(key: str, value: Any) -> None:
    """
    Set a configuration value.

    Args:
        key: Configuration key
        value: Value to set
    """
    config_manager.set(key, value)
    config_manager.save_config()
