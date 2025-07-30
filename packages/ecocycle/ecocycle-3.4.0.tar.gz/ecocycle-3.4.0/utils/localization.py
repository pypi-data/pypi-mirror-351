"""
EcoCycle - Localization Module

This module provides localization support for the EcoCycle application.
It handles loading and managing translations for different languages.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Setup logger
logger = logging.getLogger(__name__)

# Default language
DEFAULT_LANGUAGE = 'english'

# Available languages
AVAILABLE_LANGUAGES = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese']

# Path to language files
LANGUAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'languages')


class LocalizationManager:
    """Manages localization and translations for the application."""

    def __init__(self, language: str = DEFAULT_LANGUAGE):
        """
        Initialize the localization manager.

        Args:
            language (str): The language to use. Defaults to DEFAULT_LANGUAGE.
        """
        self.language = language
        self.translations = {}
        self._load_language(language)

    def _load_language(self, language: str) -> bool:
        """
        Load translations for the specified language.

        Args:
            language (str): The language to load.

        Returns:
            bool: True if language was loaded successfully, False otherwise.
        """
        # Ensure language is valid
        if language not in AVAILABLE_LANGUAGES:
            logger.warning(f"Language '{language}' not available. Using default language.")
            language = DEFAULT_LANGUAGE

        # Create language directory if it doesn't exist
        os.makedirs(LANGUAGE_DIR, exist_ok=True)

        # Path to language file
        language_file = os.path.join(LANGUAGE_DIR, f"{language}.json")

        # Check if language file exists
        if not os.path.exists(language_file):
            # Create default language file if it doesn't exist
            if language == DEFAULT_LANGUAGE:
                self._create_default_language_file(language_file)
            else:
                logger.warning(f"Language file for '{language}' not found. Using default language.")
                return self._load_language(DEFAULT_LANGUAGE)

        # Load language file
        try:
            with open(language_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            logger.info(f"Loaded language file for '{language}'")
            self.language = language
            return True
        except Exception as e:
            logger.error(f"Error loading language file for '{language}': {e}")
            if language != DEFAULT_LANGUAGE:
                return self._load_language(DEFAULT_LANGUAGE)
            return False

    def _create_default_language_file(self, language_file: str) -> None:
        """
        Create the default language file.

        Args:
            language_file (str): Path to the language file.
        """
        # Default translations
        default_translations = {
            "app_name": "EcoCycle",
            "app_description": "Cycle into a greener tomorrow",
            "settings": {
                "title": "Settings and Preferences",
                "description": "Manage your personal settings and preferences for EcoCycle",
                "categories": {
                    "personal": {
                        "name": "Personal",
                        "description": "Your personal information and statistics"
                    },
                    "transportation": {
                        "name": "Transportation",
                        "description": "Your preferred transport settings"
                    },
                    "application": {
                        "name": "Application",
                        "description": "EcoCycle appearance and behavior"
                    },
                    "privacy": {
                        "name": "Privacy",
                        "description": "Data sharing and privacy settings"
                    },
                    "notifications": {
                        "name": "Notifications",
                        "description": "Notification preferences and alerts"
                    },
                    "data_management": {
                        "name": "Data Management",
                        "description": "Manage your data and backups"
                    },
                    "accessibility": {
                        "name": "Accessibility",
                        "description": "Accessibility options for better usability"
                    },
                    "language": {
                        "name": "Language",
                        "description": "Language and localization settings"
                    }
                }
            }
        }

        # Create language file
        try:
            os.makedirs(os.path.dirname(language_file), exist_ok=True)
            with open(language_file, 'w', encoding='utf-8') as f:
                json.dump(default_translations, f, indent=2, ensure_ascii=False)
            logger.info(f"Created default language file at '{language_file}'")
        except Exception as e:
            logger.error(f"Error creating default language file: {e}")

    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """
        Get translated text for a key.

        Args:
            key (str): The translation key (dot notation for nested keys).
            default (Optional[str]): Default text if key not found.

        Returns:
            str: Translated text or default if not found.
        """
        # Split key by dots to access nested dictionaries
        keys = key.split('.')
        value = self.translations

        # Navigate through nested dictionaries
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default or key

        # Return value if it's a string, otherwise return default
        return value if isinstance(value, str) else default or key

    def change_language(self, language: str) -> bool:
        """
        Change the current language.

        Args:
            language (str): The language to change to.

        Returns:
            bool: True if language was changed successfully, False otherwise.
        """
        return self._load_language(language)


# Global localization manager instance
_localization_manager = None


def get_localization_manager(language: str = None) -> LocalizationManager:
    """
    Get the global localization manager instance.

    Args:
        language (str, optional): Language to initialize with. Defaults to None.

    Returns:
        LocalizationManager: The global localization manager instance.
    """
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager(language or DEFAULT_LANGUAGE)
    elif language is not None:
        _localization_manager.change_language(language)
    return _localization_manager


def get_text(key: str, default: Optional[str] = None) -> str:
    """
    Get translated text for a key using the global localization manager.

    Args:
        key (str): The translation key.
        default (Optional[str]): Default text if key not found.

    Returns:
        str: Translated text or default if not found.
    """
    return get_localization_manager().get_text(key, default)
