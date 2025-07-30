"""
EcoCycle - Keyboard Shortcuts Module

This module provides keyboard shortcut management for the EcoCycle application.
It handles loading, saving, and applying keyboard shortcuts.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Tuple

# Setup logger
logger = logging.getLogger(__name__)

# Path to shortcuts file
SHORTCUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shortcuts')
SHORTCUTS_FILE = os.path.join(SHORTCUTS_DIR, 'shortcuts.json')

# Default shortcuts
DEFAULT_SHORTCUTS = {
    'global': {
        'help': {
            'key': 'h',
            'description': 'Show help',
            'enabled': True
        },
        'quit': {
            'key': 'q',
            'description': 'Quit application',
            'enabled': True
        },
        'back': {
            'key': 'escape',
            'description': 'Go back',
            'enabled': True
        },
        'settings': {
            'key': 's',
            'description': 'Open settings',
            'enabled': True
        }
    },
    'main_menu': {
        'route_planner': {
            'key': '1',
            'description': 'Open route planner',
            'enabled': True
        },
        'trip_logger': {
            'key': '2',
            'description': 'Open trip logger',
            'enabled': True
        },
        'stats_analytics': {
            'key': '3',
            'description': 'Open stats and analytics',
            'enabled': True
        },
        'challenges': {
            'key': '4',
            'description': 'Open challenges',
            'enabled': True
        },
        'settings_preferences': {
            'key': '5',
            'description': 'Open settings and preferences',
            'enabled': True
        },
        'social_sharing': {
            'key': '6',
            'description': 'Open social sharing',
            'enabled': True
        },
        'notifications': {
            'key': '7',
            'description': 'Open notifications',
            'enabled': True
        },
        'help_support': {
            'key': '8',
            'description': 'Open help and support',
            'enabled': True
        },
        'admin_panel': {
            'key': '9',
            'description': 'Open admin panel',
            'enabled': True
        },
        'logout': {
            'key': '0',
            'description': 'Logout',
            'enabled': True
        }
    },
    'settings': {
        'search': {
            'key': 'ctrl+f',
            'description': 'Search settings',
            'enabled': True
        },
        'save': {
            'key': 'ctrl+s',
            'description': 'Save settings',
            'enabled': True
        },
        'reset': {
            'key': 'ctrl+r',
            'description': 'Reset settings',
            'enabled': True
        }
    },
    'route_planner': {
        'new_route': {
            'key': 'n',
            'description': 'Create new route',
            'enabled': True
        },
        'save_route': {
            'key': 's',
            'description': 'Save route',
            'enabled': True
        },
        'load_route': {
            'key': 'l',
            'description': 'Load route',
            'enabled': True
        },
        'calculate': {
            'key': 'c',
            'description': 'Calculate route',
            'enabled': True
        }
    }
}


class KeyboardShortcutsManager:
    """Manages keyboard shortcuts for the application."""

    def __init__(self):
        """Initialize the keyboard shortcuts manager."""
        self.shortcuts = {}
        self.handlers = {}
        self._load_shortcuts()

    def _load_shortcuts(self) -> None:
        """Load keyboard shortcuts from file."""
        # Start with default shortcuts
        self.shortcuts = DEFAULT_SHORTCUTS.copy()

        # Create shortcuts directory if it doesn't exist
        os.makedirs(SHORTCUTS_DIR, exist_ok=True)

        # Load custom shortcuts if file exists
        if os.path.exists(SHORTCUTS_FILE):
            try:
                with open(SHORTCUTS_FILE, 'r', encoding='utf-8') as f:
                    custom_shortcuts = json.load(f)
                    # Merge custom shortcuts with defaults
                    for section, shortcuts in custom_shortcuts.items():
                        if section not in self.shortcuts:
                            self.shortcuts[section] = {}
                        for shortcut_id, shortcut in shortcuts.items():
                            self.shortcuts[section][shortcut_id] = shortcut
            except Exception as e:
                logger.error(f"Error loading shortcuts: {e}")

    def save_shortcuts(self) -> bool:
        """
        Save keyboard shortcuts to file.

        Returns:
            bool: True if shortcuts were saved successfully, False otherwise.
        """
        # Create shortcuts directory if it doesn't exist
        os.makedirs(SHORTCUTS_DIR, exist_ok=True)

        # Save shortcuts to file
        try:
            with open(SHORTCUTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving shortcuts: {e}")
            return False

    def get_shortcut(self, section: str, shortcut_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a shortcut by section and ID.

        Args:
            section (str): The shortcut section.
            shortcut_id (str): The shortcut ID.

        Returns:
            Optional[Dict[str, Any]]: The shortcut data or None if not found.
        """
        if section in self.shortcuts and shortcut_id in self.shortcuts[section]:
            return self.shortcuts[section][shortcut_id]
        return None

    def update_shortcut(self, section: str, shortcut_id: str, key: str) -> bool:
        """
        Update a shortcut key.

        Args:
            section (str): The shortcut section.
            shortcut_id (str): The shortcut ID.
            key (str): The new shortcut key.

        Returns:
            bool: True if shortcut was updated successfully, False otherwise.
        """
        # Check if shortcut exists
        shortcut = self.get_shortcut(section, shortcut_id)
        if not shortcut:
            return False

        # Check for conflicts
        if self._check_conflict(section, key):
            return False

        # Update shortcut
        shortcut['key'] = key
        return self.save_shortcuts()

    def toggle_shortcut(self, section: str, shortcut_id: str) -> bool:
        """
        Toggle a shortcut's enabled state.

        Args:
            section (str): The shortcut section.
            shortcut_id (str): The shortcut ID.

        Returns:
            bool: True if shortcut was toggled successfully, False otherwise.
        """
        # Check if shortcut exists
        shortcut = self.get_shortcut(section, shortcut_id)
        if not shortcut:
            return False

        # Toggle enabled state
        shortcut['enabled'] = not shortcut.get('enabled', True)
        return self.save_shortcuts()

    def _check_conflict(self, section: str, key: str) -> bool:
        """
        Check if a key conflicts with existing shortcuts in the same section.

        Args:
            section (str): The shortcut section.
            key (str): The shortcut key to check.

        Returns:
            bool: True if there is a conflict, False otherwise.
        """
        if section in self.shortcuts:
            for shortcut_id, shortcut in self.shortcuts[section].items():
                if shortcut.get('key') == key and shortcut.get('enabled', True):
                    return True
        return False

    def register_handler(self, section: str, shortcut_id: str, handler: Callable) -> bool:
        """
        Register a handler for a shortcut.

        Args:
            section (str): The shortcut section.
            shortcut_id (str): The shortcut ID.
            handler (Callable): The handler function.

        Returns:
            bool: True if handler was registered successfully, False otherwise.
        """
        # Check if shortcut exists
        if not self.get_shortcut(section, shortcut_id):
            return False

        # Register handler
        if section not in self.handlers:
            self.handlers[section] = {}
        self.handlers[section][shortcut_id] = handler
        return True

    def handle_key(self, section: str, key: str) -> bool:
        """
        Handle a key press.

        Args:
            section (str): The current section.
            key (str): The pressed key.

        Returns:
            bool: True if key was handled, False otherwise.
        """
        # Check global shortcuts first
        if self._handle_section_key('global', key):
            return True

        # Check section-specific shortcuts
        return self._handle_section_key(section, key)

    def _handle_section_key(self, section: str, key: str) -> bool:
        """
        Handle a key press for a specific section.

        Args:
            section (str): The section.
            key (str): The pressed key.

        Returns:
            bool: True if key was handled, False otherwise.
        """
        if section in self.shortcuts:
            for shortcut_id, shortcut in self.shortcuts[section].items():
                if shortcut.get('key') == key and shortcut.get('enabled', True):
                    # Call handler if registered
                    if (section in self.handlers and 
                        shortcut_id in self.handlers[section]):
                        self.handlers[section][shortcut_id]()
                        return True
        return False

    def get_shortcuts_by_section(self, section: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all shortcuts for a section.

        Args:
            section (str): The section.

        Returns:
            Dict[str, Dict[str, Any]]: The shortcuts for the section.
        """
        return self.shortcuts.get(section, {})

    def get_all_shortcuts(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Get all shortcuts.

        Returns:
            Dict[str, Dict[str, Dict[str, Any]]]: All shortcuts.
        """
        return self.shortcuts

    def reset_shortcuts(self, section: Optional[str] = None) -> bool:
        """
        Reset shortcuts to defaults.

        Args:
            section (Optional[str]): The section to reset, or None to reset all.

        Returns:
            bool: True if shortcuts were reset successfully, False otherwise.
        """
        if section:
            # Reset specific section
            if section in DEFAULT_SHORTCUTS:
                self.shortcuts[section] = DEFAULT_SHORTCUTS[section].copy()
        else:
            # Reset all shortcuts
            self.shortcuts = DEFAULT_SHORTCUTS.copy()
        return self.save_shortcuts()


# Global keyboard shortcuts manager instance
_shortcuts_manager = None


def get_shortcuts_manager() -> KeyboardShortcutsManager:
    """
    Get the global keyboard shortcuts manager instance.

    Returns:
        KeyboardShortcutsManager: The global keyboard shortcuts manager instance.
    """
    global _shortcuts_manager
    if _shortcuts_manager is None:
        _shortcuts_manager = KeyboardShortcutsManager()
    return _shortcuts_manager
