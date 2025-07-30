"""
EcoCycle - Theme Manager Module

This module provides theme management functionality for the EcoCycle application.
It handles loading, saving, and applying themes.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

# Setup logger
logger = logging.getLogger(__name__)

# Path to themes directory
THEMES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'themes')

# Default themes
DEFAULT_THEMES = {
    'default': {
        'name': 'Default',
        'description': 'The default EcoCycle theme',
        'colors': {
            'primary': '#4CAF50',
            'secondary': '#2196F3',
            'background': '#FFFFFF',
            'text': '#212121',
            'accent': '#FF9800',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336',
            'info': '#2196F3'
        },
        'font': 'default',
        'font_size': 'medium'
    },
    'dark': {
        'name': 'Dark',
        'description': 'A dark theme for EcoCycle',
        'colors': {
            'primary': '#4CAF50',
            'secondary': '#2196F3',
            'background': '#121212',
            'text': '#FFFFFF',
            'accent': '#FF9800',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336',
            'info': '#2196F3'
        },
        'font': 'default',
        'font_size': 'medium'
    },
    'eco': {
        'name': 'Eco',
        'description': 'A nature-inspired theme for EcoCycle',
        'colors': {
            'primary': '#4CAF50',
            'secondary': '#8BC34A',
            'background': '#F1F8E9',
            'text': '#33691E',
            'accent': '#CDDC39',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336',
            'info': '#2196F3'
        },
        'font': 'default',
        'font_size': 'medium'
    },
    'high-contrast': {
        'name': 'High Contrast',
        'description': 'A high contrast theme for better accessibility',
        'colors': {
            'primary': '#000000',
            'secondary': '#FFFFFF',
            'background': '#FFFFFF',
            'text': '#000000',
            'accent': '#FF0000',
            'success': '#008000',
            'warning': '#FF8000',
            'error': '#FF0000',
            'info': '#0000FF'
        },
        'font': 'default',
        'font_size': 'large'
    },
    'light': {
        'name': 'Light',
        'description': 'A light theme for EcoCycle',
        'colors': {
            'primary': '#4CAF50',
            'secondary': '#2196F3',
            'background': '#F5F5F5',
            'text': '#212121',
            'accent': '#FF9800',
            'success': '#4CAF50',
            'warning': '#FFC107',
            'error': '#F44336',
            'info': '#2196F3'
        },
        'font': 'default',
        'font_size': 'medium'
    }
}


class ThemeManager:
    """Manages themes for the application."""

    def __init__(self):
        """Initialize the theme manager."""
        self.themes = {}
        self.current_theme = 'default'
        self._load_themes()

    def _load_themes(self) -> None:
        """Load all available themes."""
        # Start with default themes
        self.themes = DEFAULT_THEMES.copy()

        # Create themes directory if it doesn't exist
        os.makedirs(THEMES_DIR, exist_ok=True)

        # Load custom themes
        try:
            for filename in os.listdir(THEMES_DIR):
                if filename.endswith('.json'):
                    theme_id = os.path.splitext(filename)[0]
                    theme_path = os.path.join(THEMES_DIR, filename)
                    try:
                        with open(theme_path, 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                            self.themes[theme_id] = theme_data
                    except Exception as e:
                        logger.error(f"Error loading theme '{theme_id}': {e}")
        except Exception as e:
            logger.error(f"Error loading themes: {e}")

    def get_theme(self, theme_id: str) -> Dict[str, Any]:
        """
        Get a theme by ID.

        Args:
            theme_id (str): The theme ID.

        Returns:
            Dict[str, Any]: The theme data or default theme if not found.
        """
        return self.themes.get(theme_id, self.themes['default'])

    def get_current_theme(self) -> Dict[str, Any]:
        """
        Get the current theme.

        Returns:
            Dict[str, Any]: The current theme data.
        """
        return self.get_theme(self.current_theme)

    def set_current_theme(self, theme_id: str) -> bool:
        """
        Set the current theme.

        Args:
            theme_id (str): The theme ID.

        Returns:
            bool: True if theme was set successfully, False otherwise.
        """
        if theme_id in self.themes:
            self.current_theme = theme_id
            return True
        return False

    def create_theme(self, theme_id: str, theme_data: Dict[str, Any]) -> bool:
        """
        Create a new theme.

        Args:
            theme_id (str): The theme ID.
            theme_data (Dict[str, Any]): The theme data.

        Returns:
            bool: True if theme was created successfully, False otherwise.
        """
        # Validate theme data
        if not self._validate_theme(theme_data):
            return False

        # Add theme
        self.themes[theme_id] = theme_data

        # Save theme to file
        return self._save_theme(theme_id)

    def update_theme(self, theme_id: str, theme_data: Dict[str, Any]) -> bool:
        """
        Update an existing theme.

        Args:
            theme_id (str): The theme ID.
            theme_data (Dict[str, Any]): The theme data.

        Returns:
            bool: True if theme was updated successfully, False otherwise.
        """
        # Check if theme exists
        if theme_id not in self.themes:
            return False

        # Validate theme data
        if not self._validate_theme(theme_data):
            return False

        # Update theme
        self.themes[theme_id] = theme_data

        # Save theme to file
        return self._save_theme(theme_id)

    def delete_theme(self, theme_id: str) -> bool:
        """
        Delete a theme.

        Args:
            theme_id (str): The theme ID.

        Returns:
            bool: True if theme was deleted successfully, False otherwise.
        """
        # Check if theme exists and is not a default theme
        if theme_id not in self.themes or theme_id in DEFAULT_THEMES:
            return False

        # Delete theme
        del self.themes[theme_id]

        # Delete theme file
        theme_path = os.path.join(THEMES_DIR, f"{theme_id}.json")
        try:
            if os.path.exists(theme_path):
                os.remove(theme_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting theme file '{theme_id}': {e}")
            return False

    def _save_theme(self, theme_id: str) -> bool:
        """
        Save a theme to file.

        Args:
            theme_id (str): The theme ID.

        Returns:
            bool: True if theme was saved successfully, False otherwise.
        """
        # Don't save default themes
        if theme_id in DEFAULT_THEMES and self.themes[theme_id] == DEFAULT_THEMES[theme_id]:
            return True

        # Create themes directory if it doesn't exist
        os.makedirs(THEMES_DIR, exist_ok=True)

        # Save theme to file
        theme_path = os.path.join(THEMES_DIR, f"{theme_id}.json")
        try:
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(self.themes[theme_id], f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving theme '{theme_id}': {e}")
            return False

    def _validate_theme(self, theme_data: Dict[str, Any]) -> bool:
        """
        Validate theme data.

        Args:
            theme_data (Dict[str, Any]): The theme data.

        Returns:
            bool: True if theme data is valid, False otherwise.
        """
        # Check required fields
        required_fields = ['name', 'colors']
        for field in required_fields:
            if field not in theme_data:
                logger.error(f"Theme is missing required field '{field}'")
                return False

        # Check colors
        required_colors = ['primary', 'secondary', 'background', 'text']
        if not all(color in theme_data['colors'] for color in required_colors):
            logger.error("Theme is missing required colors")
            return False

        return True

    def get_available_themes(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available themes.

        Returns:
            List[Dict[str, Any]]: List of theme data.
        """
        return [
            {'id': theme_id, **theme_data}
            for theme_id, theme_data in self.themes.items()
        ]

    def is_valid_color(self, color: str) -> bool:
        """
        Check if a color string is valid.

        Args:
            color (str): The color string to check.

        Returns:
            bool: True if color is valid, False otherwise.
        """
        # Check hex color format
        if color.startswith('#'):
            # Check if it's a valid hex color
            try:
                # Remove # and check if the rest is a valid hex number
                hex_color = color[1:]
                int(hex_color, 16)
                # Check length (3, 4, 6, or 8 characters after #)
                return len(hex_color) in [3, 4, 6, 8]
            except ValueError:
                return False
        
        # Add more color format validations if needed
        return False


# Global theme manager instance
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance.

    Returns:
        ThemeManager: The global theme manager instance.
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
