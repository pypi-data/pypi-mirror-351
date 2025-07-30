"""
EcoCycle - Settings View Module

This module provides the UI and functionality for the settings and preferences page,
utilizing Rich UI components for enhanced visual presentation.
"""

import os
import json
import logging
from typing import Dict, Any, List

# Setup logger
logger = logging.getLogger(__name__)

# Import notification settings constants if available
try:
    from services.notifications.config import NOTIFICATION_SETTINGS_FILE, DEFAULT_NOTIFICATION_SETTINGS
    HAS_NOTIFICATION_CONFIG = True
except ImportError:
    logger.warning("Notification config not available. Using default notification settings.")
    NOTIFICATION_SETTINGS_FILE = "config/preferences/notification_settings.json"
    DEFAULT_NOTIFICATION_SETTINGS = {
        "email_notifications": False,
        "sms_notifications": False,
        "achievement_notifications": True,
        "weekly_summary": True,
        "eco_tips": True,
        "reminder_frequency": "weekly"
    }
    HAS_NOTIFICATION_CONFIG = False

# Import utility modules
HAS_UTILS = False

# Define a dummy theme manager class
class DummyThemeManager:
    def get_theme(self, theme_id):
        # Unused parameter but needed for compatibility
        _ = theme_id
        return {"name": "Default", "description": "Default theme", "colors": {}}

    def set_current_theme(self, theme_id):
        # Unused parameter but needed for compatibility
        _ = theme_id
        return False

    def create_theme(self, theme_id, theme_data):
        # Unused parameters but needed for compatibility
        _ = theme_id
        _ = theme_data
        return False

# Create a dummy theme manager function
def get_theme_manager():
    """Dummy theme manager function."""
    return DummyThemeManager()

# Try to import the real theme manager
try:
    from utils.theme_manager import get_theme_manager
    HAS_UTILS = True
except ImportError:
    logger.warning("Theme manager not available. Theme customization will be disabled.")

# Import Rich UI components with fallback to basic UI
HAS_RICH = False

# Define dummy classes to avoid IDE warnings
class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

class DummyConsole:
    def print(self, *_, **__):
        pass

    def status(self, *_, **__):
        return DummyContext()

class DummyBox:
    pass

class DummyPanel:
    def __init__(self, *_, **__):
        pass

    def __call__(self, *_, **__):
        return None

class DummyTable:
    def __init__(self, *_, **__):
        pass

    def add_column(self, *_, **__):
        pass

    def add_row(self, *_, **__):
        pass

class DummyText:
    def __init__(self, *_, **__):
        pass

class DummyLayout:
    def __init__(self, *_, **__):
        pass

    def split(self, *_):
        pass

    def __getitem__(self, _):
        return self

    def update(self, _):
        pass

class DummyAlign:
    @staticmethod
    def center(_):
        return ""

class DummyPrompt:
    @staticmethod
    def ask(*_, **__):
        return ""

class DummyConfirm:
    @staticmethod
    def ask(*_, **__):
        return False

# Set dummy objects by default
console = DummyConsole()
Panel = DummyPanel()
Table = DummyTable
Text = DummyText
Layout = DummyLayout
Align = DummyAlign()
ROUNDED = None
DOUBLE = None
Prompt = DummyPrompt()
Confirm = DummyConfirm()
IntPrompt = DummyPrompt()

# Try to import Rich UI components
try:
    from rich.console import Console
    from rich.table import Table as RichTable
    from rich.panel import Panel as RichPanel
    from rich.text import Text as RichText
    from rich.layout import Layout as RichLayout
    from rich.align import Align as RichAlign
    from rich.box import ROUNDED as RICH_ROUNDED, DOUBLE as RICH_DOUBLE
    from rich.prompt import Prompt as RichPrompt, Confirm as RichConfirm, IntPrompt as RichIntPrompt

    # Set global variables
    HAS_RICH = True
    console = Console()
    Panel = RichPanel
    Table = RichTable
    Text = RichText
    Layout = RichLayout
    Align = RichAlign
    ROUNDED = RICH_ROUNDED
    DOUBLE = RICH_DOUBLE
    Prompt = RichPrompt
    Confirm = RichConfirm
    IntPrompt = RichIntPrompt
except ImportError:
    logger.warning("Rich UI components not available. Using basic UI.")

# Helper function to create panels with proper handling of box parameter
def create_panel(content, title=None, border_style=None, box_type=None, padding=None):
    """Create a panel with proper handling of box parameter to avoid IDE warnings."""
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if border_style is not None:
        kwargs["border_style"] = border_style
    if padding is not None:
        kwargs["padding"] = padding
    if box_type is not None and HAS_RICH:
        kwargs["box"] = box_type

    return Panel(content, **kwargs)

# Helper function to create tables with proper handling of box parameter
def create_table(title=None, border_style=None, box_type=None):
    """Create a table with proper handling of box parameter to avoid IDE warnings."""
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if border_style is not None:
        kwargs["border_style"] = border_style
    if box_type is not None and HAS_RICH:
        kwargs["box"] = box_type

    return Table(**kwargs)


class SettingsView:
    """Manages the settings and preferences view with Rich UI styling."""

    def __init__(self, user_manager):
        """Initialize the settings view with the user manager instance."""
        self.user_manager = user_manager
        self.notification_settings = self._load_notification_settings()
        self.settings_categories = [
            {
                'name': 'Personal',
                'icon': '👤',
                'settings': ['weight_kg', 'height_cm', 'age', 'gender', 'fitness_level']
            },
            {
                'name': 'Transportation',
                'icon': '🚲',
                'settings': ['default_transport_mode', 'commute_distance', 'preferred_route_type', 'auto_log_trips']
            },
            {
                'name': 'Application',
                'icon': '🖥️',
                'settings': ['theme', 'color_scheme', 'font_size', 'notifications_enabled', 'units']
            },
            {
                'name': 'Privacy',
                'icon': '🔒',
                'settings': ['share_data', 'analytics_enabled', 'data_retention_period', 'location_tracking', 'require_email_verification', 'resend_verification_email']
            },
            {
                'name': 'Notifications',
                'icon': '🔔',
                'settings': ['email_notifications', 'sms_notifications', 'achievement_notifications', 'weekly_summary', 'eco_tips_enabled', 'reminder_frequency', 'weather_alerts']
            },
            {
                'name': 'Data Management',
                'icon': '💾',
                'settings': ['auto_backup', 'export_data', 'import_data', 'reset_user_data']
            },
            {
                'name': 'Accessibility',
                'icon': '♿',
                'settings': ['high_contrast_mode', 'screen_reader_support', 'reduced_motion', 'keyboard_shortcuts']
            },
            {
                'name': 'Language',
                'icon': '🌐',
                'settings': ['language', 'date_format', 'time_format', 'distance_unit']
            },
            {
                'name': 'System Repair',
                'icon': '🔧',
                'settings': ['run_system_diagnostics', 'auto_repair_system', 'view_repair_history', 'backup_before_repair']
            }
        ]

        # Define default values for settings
        self.defaults = {
            # Personal
            'weight_kg': 70,
            'height_cm': 175,
            'age': 30,
            'gender': 'not specified',
            'fitness_level': 'intermediate',

            # Transportation
            'default_transport_mode': 'bicycle',
            'commute_distance': 5,
            'preferred_route_type': 'balanced',
            'auto_log_trips': False,

            # Application
            'theme': 'default',
            'color_scheme': 'system',
            'font_size': 'medium',
            'notifications_enabled': False,
            'units': 'metric',

            # Privacy
            'share_data': False,
            'analytics_enabled': True,
            'data_retention_period': '1 year',
            'location_tracking': 'while using',

            # Notifications
            'email_notifications': False,
            'sms_notifications': False,
            'achievement_notifications': True,
            'weekly_summary': True,
            'eco_tips_enabled': True,
            'reminder_frequency': 'weekly',
            'weather_alerts': True,

            # Data Management
            'auto_backup': False,
            'export_data': None,  # Action setting
            'import_data': None,  # Action setting
            'reset_user_data': None,  # Action setting

            # Accessibility
            'high_contrast_mode': False,
            'screen_reader_support': False,
            'reduced_motion': False,
            'keyboard_shortcuts': True,

            # Language
            'language': 'english',
            'date_format': 'MM/DD/YYYY',
            'time_format': '12-hour',
            'distance_unit': 'km',

            # System Repair
            'run_system_diagnostics': None,  # Action setting
            'auto_repair_system': None,  # Action setting
            'view_repair_history': None,  # Action setting
            'backup_before_repair': True
        }

        # Define options for settings with predefined choices
        self.options = {
            'default_transport_mode': ['bicycle', 'e-bike', 'scooter', 'skateboard', 'walking'],
            'theme': ['default', 'dark', 'eco', 'high-contrast', 'light'],
            'units': ['metric', 'imperial'],
            'gender': ['male', 'female', 'non-binary', 'not specified'],
            'fitness_level': ['beginner', 'intermediate', 'advanced', 'professional'],
            'preferred_route_type': ['fastest', 'balanced', 'scenic', 'least elevation', 'safest'],
            'color_scheme': ['system', 'blue', 'green', 'purple', 'orange', 'custom'],
            'font_size': ['small', 'medium', 'large', 'extra large'],
            'data_retention_period': ['1 month', '3 months', '6 months', '1 year', 'forever'],
            'location_tracking': ['always', 'while using', 'never'],
            'reminder_frequency': ['none', 'daily', 'weekly', 'monthly'],
            'language': ['english', 'spanish', 'french', 'german', 'chinese', 'japanese'],
            'date_format': ['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'],
            'time_format': ['12-hour', '24-hour'],
            'distance_unit': ['km', 'miles']
        }

        # Types for settings
        self.types = {
            # Personal
            'weight_kg': float,
            'height_cm': float,
            'age': int,
            'gender': str,
            'fitness_level': str,

            # Transportation
            'default_transport_mode': str,
            'commute_distance': float,
            'preferred_route_type': str,
            'auto_log_trips': bool,

            # Application
            'theme': str,
            'color_scheme': str,
            'font_size': str,
            'notifications_enabled': bool,
            'units': str,

            # Privacy
            'share_data': bool,
            'analytics_enabled': bool,
            'data_retention_period': str,
            'location_tracking': str,
            'require_email_verification': bool,
            'resend_verification_email': 'action',

            # Notifications
            'email_notifications': bool,
            'sms_notifications': bool,
            'achievement_notifications': bool,
            'weekly_summary': bool,
            'eco_tips_enabled': bool,
            'reminder_frequency': str,
            'weather_alerts': bool,

            # Data Management
            'auto_backup': bool,
            'export_data': str,  # Special handling
            'import_data': str,  # Special handling
            'reset_user_data': str,  # Special handling

            # Accessibility
            'high_contrast_mode': bool,
            'screen_reader_support': bool,
            'reduced_motion': bool,
            'keyboard_shortcuts': bool,

            # Language
            'language': str,
            'date_format': str,
            'time_format': str,
            'distance_unit': str,

            # System Repair
            'run_system_diagnostics': 'action',
            'auto_repair_system': 'action',
            'view_repair_history': 'action',
            'backup_before_repair': bool
        }

        # Descriptions for settings
        self.descriptions = {
            # Personal
            'weight_kg': 'Your weight in kilograms',
            'height_cm': 'Your height in centimeters',
            'age': 'Your age in years',
            'gender': 'Your gender for metabolic calculations',
            'fitness_level': 'Your fitness level for route recommendations',

            # Transportation
            'default_transport_mode': 'Your preferred mode of transportation',
            'commute_distance': 'Your typical commute distance in km',
            'preferred_route_type': 'Your preferred type of route for recommendations',
            'auto_log_trips': 'Automatically log trips based on detected movement',

            # Application
            'theme': 'Application theme for visual preference',
            'color_scheme': 'Color scheme for the application interface',
            'font_size': 'Text size throughout the application',
            'notifications_enabled': 'Enable or disable app notifications',
            'units': 'Measurement system (metric or imperial)',

            # Privacy
            'share_data': 'Share your activity data with the community',
            'analytics_enabled': 'Allow anonymous usage analytics',
            'data_retention_period': 'How long to keep your activity data',
            'location_tracking': 'When to track your location',
            'require_email_verification': 'Require email verification to log in',
            'resend_verification_email': 'Resend email verification link',

            # Notifications
            'email_notifications': 'Receive notifications via email',
            'sms_notifications': 'Receive notifications via SMS',
            'achievement_notifications': 'Get notified about new achievements',
            'weekly_summary': 'Receive weekly summary of your cycling activity',
            'eco_tips_enabled': 'Receive eco-friendly cycling tips',
            'reminder_frequency': 'How often to send cycling reminders',
            'weather_alerts': 'Receive alerts about optimal cycling weather',

            # Data Management
            'auto_backup': 'Automatically backup your data',
            'export_data': 'Export your data to a file',
            'import_data': 'Import data from a file',
            'reset_user_data': 'Reset or clear specific user data with verification',

            # Accessibility
            'high_contrast_mode': 'Increase contrast for better visibility',
            'screen_reader_support': 'Optimize for screen readers',
            'reduced_motion': 'Reduce animations and motion effects',
            'keyboard_shortcuts': 'Enable keyboard shortcuts',

            # Language
            'language': 'Application language',
            'date_format': 'Format for displaying dates',
            'time_format': 'Format for displaying times',
            'distance_unit': 'Unit for displaying distances',

            # System Repair
            'run_system_diagnostics': 'Run comprehensive system diagnostics to identify issues',
            'auto_repair_system': 'Automatically diagnose and repair common system problems',
            'view_repair_history': 'View history of system repairs and diagnostics',
            'backup_before_repair': 'Create backup before performing system repairs'
        }

    def show_main_menu(self) -> None:
        """Display the main settings menu with categories."""
        if not self.user_manager.is_authenticated():
            self._show_auth_required()
            return

        # Sync notification settings
        self._sync_notification_settings()

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            if HAS_RICH:
                self._show_rich_header("Settings and Preferences", "purple")
                self._show_rich_categories()

                # Show additional options
                options = [str(i) for i in range(1, len(self.settings_categories) + 3)]
                options_text = "\n[bold purple]Select a category or action[/bold purple]"
                options_text += "\n[dim]Enter 'S' to search settings[/dim]"
                options_text += "\n[dim]Enter 'T' to customize theme[/dim]"

                # Add option to return to main menu
                choice = Prompt.ask(
                    options_text,
                    choices=options + ['s', 'S', 't', 'T'],
                    default=str(len(self.settings_categories) + 1)
                )
            else:
                self._show_basic_header("Settings and Preferences")
                self._show_basic_categories()
                print("\nAdditional Options:")
                print("S. Search Settings")
                print("T. Customize Theme")

                # Get user choice
                choice = input("\nSelect a category or action (1-{}, S, or T): ".format(
                    len(self.settings_categories) + 1
                ))

            # Search settings
            if choice.lower() == 's':
                self.search_settings()
                continue

            # Customize theme
            if choice.lower() == 't':
                self.customize_theme()
                continue

            # Exit condition
            if choice == str(len(self.settings_categories) + 1):
                break

            # Process category selection
            try:
                category_index = int(choice) - 1
                if 0 <= category_index < len(self.settings_categories):
                    self.show_category_settings(self.settings_categories[category_index])
                else:
                    self._show_error("Invalid selection.")
            except ValueError:
                if choice.lower() not in ['s', 't']:
                    self._show_error("Invalid input. Please enter a number, 'S', or 'T'.")

            if not HAS_RICH:
                input("\nPress Enter to continue...")

    def show_category_settings(self, category: Dict[str, Any]) -> None:
        """Display settings for a specific category."""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            if HAS_RICH:
                self._show_rich_header(f"{category['icon']} {category['name']} Settings", "cyan")
                self._show_rich_category_settings(category)

                # Add option to return to settings menu
                options = [str(i) for i in range(1, len(category['settings']) + 2)]
                choice = Prompt.ask(
                    "\n[bold cyan]Select a setting to change[/bold cyan]",
                    choices=options,
                    default=options[-1]
                )
            else:
                self._show_basic_header(f"{category['name']} Settings")
                self._show_basic_category_settings(category)

                # Get user choice
                choice = input("\nSelect a setting to change (1-{}): ".format(
                    len(category['settings']) + 1
                ))

            # Exit condition
            if choice == str(len(category['settings']) + 1):
                break

            # Process setting selection
            try:
                setting_index = int(choice) - 1
                if 0 <= setting_index < len(category['settings']):
                    setting_key = category['settings'][setting_index]
                    self.update_setting(setting_key)
                else:
                    self._show_error("Invalid selection.")
            except ValueError:
                self._show_error("Invalid input. Please enter a number.")

            if not HAS_RICH:
                input("\nPress Enter to continue...")

    def update_setting(self, setting_key: str) -> None:
        """Update an individual setting."""
        # Get current value with fallback to default
        current_value = self.user_manager.get_user_preference(
            setting_key,
            self.defaults.get(setting_key)
        )

        # Special action settings
        if setting_key in ['export_data', 'import_data', 'reset_user_data', 'resend_verification_email',
                          'run_system_diagnostics', 'auto_repair_system', 'view_repair_history']:
            self._handle_action_setting(setting_key)
        # Settings with predefined options
        elif setting_key in self.options:
            self._update_option_setting(setting_key, current_value)
        # Boolean settings (toggle)
        elif self.types[setting_key] == bool:
            self._update_boolean_setting(setting_key, current_value)
        # Numeric or text settings
        else:
            self._update_value_setting(setting_key, current_value)

        # Sync notification settings if this is a notification setting
        if setting_key in ['email_notifications', 'sms_notifications', 'achievement_notifications',
                          'weekly_summary', 'eco_tips_enabled', 'reminder_frequency', 'weather_alerts']:
            self._update_notification_settings(setting_key)

    def _update_option_setting(self, setting_key: str, current_value: Any) -> None:
        """Update a setting with predefined options."""
        options = self.options[setting_key]
        new_value = None  # Initialize to avoid unbound variable warning

        if HAS_RICH:
            # Use helper function to create panel
            console.print(create_panel(
                self.descriptions.get(setting_key, f"Select a {setting_key.replace('_', ' ')}"),
                title=f"Update {setting_key.replace('_', ' ').title()}",
                border_style="cyan",
                box_type=ROUNDED
            ))

            # Use helper function to create table
            options_table = create_table(border_style="cyan", box_type=ROUNDED)
            options_table.add_column("Option", style="yellow")
            options_table.add_column("Value", style="green")

            for i, option in enumerate(options, 1):
                options_table.add_row(str(i), option)

            console.print(options_table)

            try:
                choice = int(Prompt.ask(
                    f"[cyan]Select a {setting_key.replace('_', ' ')}[/cyan]",
                    choices=[str(i) for i in range(1, len(options) + 1)],
                    default=str(options.index(current_value) + 1 if current_value in options else 1)
                ))

                with console.status(f"[cyan]Updating {setting_key.replace('_', ' ')}...", spinner="dots"):
                    if 1 <= choice <= len(options):
                        new_value = options[choice-1]
                        self.user_manager.update_user_preference(setting_key, new_value)

                # Use helper function to create success panel
                console.print(create_panel(
                    f"{setting_key.replace('_', ' ').title()} updated to [bold]{new_value}[/bold]",
                    title="Success",
                    border_style="green",
                    box_type=ROUNDED
                ))
            except ValueError:
                self._show_error("Invalid input. Please enter a number.")
        else:
            print(f"\nAvailable {setting_key.replace('_', ' ')}s:")
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            try:
                choice = int(input(f"\nSelect a {setting_key.replace('_', ' ')} (1-{len(options)}): "))
                if 1 <= choice <= len(options):
                    new_value = options[choice-1]
                    self.user_manager.update_user_preference(setting_key, new_value)
                    print(f"{setting_key.replace('_', ' ').title()} updated successfully!")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def _update_boolean_setting(self, setting_key: str, current_value: bool) -> None:
        """Update a boolean setting."""
        new_value = not current_value

        if HAS_RICH:
            with console.status(f"[cyan]Updating {setting_key.replace('_', ' ')}...", spinner="dots"):
                self.user_manager.update_user_preference(setting_key, new_value)

            status = "enabled" if new_value else "disabled"

            # Use helper function to create panel
            console.print(create_panel(
                f"{setting_key.replace('_', ' ').title()} is now [bold]{status}[/bold]",
                title="Success",
                border_style="green",
                box_type=ROUNDED
            ))
        else:
            self.user_manager.update_user_preference(setting_key, new_value)
            status = "enabled" if new_value else "disabled"
            print(f"{setting_key.replace('_', ' ').title()} {status} successfully!")

    def _update_value_setting(self, setting_key: str, current_value: Any) -> None:
        """Update a setting with a user-entered value."""
        setting_type = self.types.get(setting_key, str)

        if HAS_RICH:
            # Use helper function to create panel
            console.print(create_panel(
                self.descriptions.get(setting_key, f"Enter your {setting_key.replace('_', ' ')}"),
                title=f"Update {setting_key.replace('_', ' ').title()}",
                border_style="cyan",
                box_type=ROUNDED
            ))

            try:
                # Determine units or type hint
                unit = "kg" if setting_key.endswith("kg") else (
                    "cm" if setting_key.endswith("cm") else None
                )
                type_hint = f" (in {unit})" if unit else ""

                # Get input
                new_value_str = Prompt.ask(
                    f"[cyan]{setting_key.replace('_', ' ').title()}[/cyan]{type_hint}",
                    default=str(current_value)
                )

                with console.status(f"[cyan]Updating {setting_key.replace('_', ' ')}...", spinner="dots"):
                    new_value = setting_type(new_value_str)
                    self.user_manager.update_user_preference(setting_key, new_value)

                # Format display value
                display_value = f"{new_value} {unit}" if unit else str(new_value)

                # Use helper function to create success panel
                console.print(create_panel(
                    f"{setting_key.replace('_', ' ').title()} updated to [bold]{display_value}[/bold]",
                    title="Success",
                    border_style="green",
                    box_type=ROUNDED
                ))
            except ValueError:
                self._show_error(f"Invalid input. Please enter a valid {setting_type.__name__}.")
        else:
            unit = "kg" if setting_key.endswith("kg") else (
                "cm" if setting_key.endswith("cm") else None
            )
            type_hint = f" in {unit}" if unit else ""

            try:
                new_value_str = input(f"Enter your {setting_key.replace('_', ' ')}{type_hint}: ")
                new_value = setting_type(new_value_str)
                self.user_manager.update_user_preference(setting_key, new_value)
                print(f"{setting_key.replace('_', ' ').title()} updated successfully!")
            except ValueError:
                print(f"Invalid input. Please enter a valid {setting_type.__name__}.")

    def _show_rich_header(self, title: str, color: str = "green") -> None:
        """Display a styled header using Rich."""
        if not HAS_RICH:
            self._show_basic_header(title)
            return

        # Create a simple styled header without using Layout
        console.print(f"\n[bold {color}]{title}[/bold {color}]")

        # Show description
        # Only use box parameter if ROUNDED is not None (when Rich is available)
        desc_kwargs = {
            "border_style": color,
            "padding": (1, 2)
        }
        if ROUNDED is not None:
            desc_kwargs["box"] = ROUNDED

        console.print(Panel(
            "Manage your personal settings and preferences for EcoCycle",
            **desc_kwargs
        ))

    def _show_basic_header(self, title: str) -> None:
        """Display a basic header for non-Rich UI."""
        print("\n" + "=" * 50)
        print(f"{title}".center(50))
        print("=" * 50)
        print("Manage your personal settings and preferences for EcoCycle")
        print("-" * 50)

    def _show_rich_categories(self) -> None:
        """Display settings categories using Rich UI."""
        categories_table = Table(title="Settings Categories", box=ROUNDED, border_style="purple")
        categories_table.add_column("Option", style="yellow")
        categories_table.add_column("Category", style="green")
        categories_table.add_column("Icon", style="cyan")
        categories_table.add_column("Description", style="blue")

        # Category descriptions
        descriptions = {
            'Personal': 'Your personal information and statistics',
            'Transportation': 'Your preferred transport settings',
            'Application': 'EcoCycle appearance and behavior',
            'Privacy': 'Data sharing and privacy settings',
            'Notifications': 'Manage how and when you receive alerts',
            'Data Management': 'Control your data backup and history',
            'Accessibility': 'Customize app for better usability',
            'Language': 'Set your preferred language and formats',
            'System Repair': 'Diagnose and repair system issues automatically'
        }

        for i, category in enumerate(self.settings_categories, 1):
            categories_table.add_row(
                str(i),
                category['name'],
                category['icon'],
                descriptions.get(category['name'], '')
            )

        # Add back option
        categories_table.add_row(
            str(len(self.settings_categories) + 1),
            "Back to Main Menu",
            "🔙",
            "Return to the main application menu"
        )

        console.print(categories_table)

    def _show_basic_categories(self) -> None:
        """Display settings categories using basic UI."""
        print("\nSettings Categories:")
        for i, category in enumerate(self.settings_categories, 1):
            print(f"{i}. {category['icon']} {category['name']}")
        print(f"{len(self.settings_categories) + 1}. Back to Main Menu")

    def _show_rich_category_settings(self, category: Dict[str, Any]) -> None:
        """Display settings for a category using Rich UI."""
        settings_table = Table(
            title=f"{category['name']} Settings",
            box=ROUNDED,
            border_style="cyan"
        )
        settings_table.add_column("Option", style="yellow")
        settings_table.add_column("Setting", style="green")
        settings_table.add_column("Current Value", style="blue")
        settings_table.add_column("Description", style="cyan")

        for i, setting_key in enumerate(category['settings'], 1):
            # Get current value with fallback to default
            current_value = self.user_manager.get_user_preference(
                setting_key,
                self.defaults.get(setting_key)
            )

            # Format boolean values for display
            if self.types.get(setting_key) == bool:
                display_value = "Enabled" if current_value else "Disabled"
            # Add units for certain settings
            elif setting_key.endswith('_kg'):
                display_value = f"{current_value} kg"
            elif setting_key.endswith('_cm'):
                display_value = f"{current_value} cm"
            else:
                display_value = str(current_value)

            settings_table.add_row(
                str(i),
                setting_key.replace('_', ' ').title(),
                display_value,
                self.descriptions.get(setting_key, '')
            )

        # Add back option
        settings_table.add_row(
            str(len(category['settings']) + 1),
            "Back to Settings Menu",
            "",
            "Return to the main settings menu"
        )

        console.print(settings_table)

    def _show_basic_category_settings(self, category: Dict[str, Any]) -> None:
        """Display settings for a category using basic UI."""
        print(f"\n{category['name']} Settings:")
        for i, setting_key in enumerate(category['settings'], 1):
            current_value = self.user_manager.get_user_preference(
                setting_key,
                self.defaults.get(setting_key)
            )

            if self.types.get(setting_key) == bool:
                display_value = "Enabled" if current_value else "Disabled"
            elif setting_key.endswith('_kg'):
                display_value = f"{current_value} kg"
            elif setting_key.endswith('_cm'):
                display_value = f"{current_value} cm"
            else:
                display_value = str(current_value)

            print(f"{i}. {setting_key.replace('_', ' ').title()}: {display_value}")
        print(f"{len(category['settings']) + 1}. Back to Settings Menu")

    def _show_auth_required(self) -> None:
        """Display authentication required message."""
        os.system('cls' if os.name == 'nt' else 'clear')

        if HAS_RICH:
            # Use helper function to create panel
            console.print(create_panel(
                "You need to log in to manage settings and preferences.",
                title="Authentication Required",
                border_style="red",
                box_type=ROUNDED
            ))
        else:
            print("\n" + "=" * 50)
            print("Authentication Required".center(50))
            print("=" * 50)
            print("\nYou need to log in to manage settings and preferences.")

        input("\nPress Enter to continue...")

    def _handle_data_reset(self) -> None:
        """Handle comprehensive data reset with email verification and backup options."""
        # Check if user has email for verification
        user = self.user_manager.get_current_user()
        email = user.get('email')

        if not email:
            self._show_error("Email verification is required for data reset operations. Please add an email to your account first.")
            return

        # Define reset options
        reset_options = {
            '1': {
                'name': 'Reset Cycling Trips Only',
                'description': 'Clear all cycling trip logs and related statistics (distance, CO2 saved, calories)',
                'method': 'reset_cycling_trips',
                'backup_type': 'trips'
            },
            '2': {
                'name': 'Reset Statistics & Analytics',
                'description': 'Reset aggregated statistics and analytics preferences while preserving individual trip logs',
                'method': 'reset_statistics_analytics',
                'backup_type': 'stats'
            },
            '3': {
                'name': 'Reset Challenges & Achievements',
                'description': 'Clear all challenges, achievements, eco points, and gamification data',
                'method': 'reset_challenges_achievements',
                'backup_type': 'challenges'
            },
            '4': {
                'name': 'Reset Everything (Complete Wipe)',
                'description': 'Reset ALL user data while preserving account credentials and login information',
                'method': 'reset_all_user_data',
                'backup_type': 'full'
            }
        }

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            if HAS_RICH:
                # Show header
                console.print(create_panel(
                    "⚠️ DATA RESET OPERATIONS ⚠️\n\nSelect the type of data you want to reset. Email verification will be required.",
                    title="🔒 Reset User Data",
                    border_style="red",
                    box_type=ROUNDED
                ))

                # Create options table
                options_table = create_table(
                    title="Available Reset Options",
                    border_style="red",
                    box_type=ROUNDED
                )
                options_table.add_column("Option", style="yellow")
                options_table.add_column("Reset Type", style="red")
                options_table.add_column("Description", style="cyan")

                for key, option in reset_options.items():
                    options_table.add_row(key, option['name'], option['description'])

                options_table.add_row("5", "[bold green]Cancel[/bold green]", "Return to settings menu")
                console.print(options_table)

                choice = Prompt.ask(
                    "\n[bold red]Select reset option[/bold red]",
                    choices=['1', '2', '3', '4', '5'],
                    default='5'
                )
            else:
                print("\n" + "=" * 60)
                print("⚠️ DATA RESET OPERATIONS ⚠️".center(60))
                print("=" * 60)
                print("Select the type of data you want to reset.")
                print("Email verification will be required.")
                print("-" * 60)

                for key, option in reset_options.items():
                    print(f"{key}. {option['name']}")
                    print(f"   {option['description']}")
                    print()

                print("5. Cancel - Return to settings menu")

                choice = input("\nSelect reset option (1-5): ")

            if choice == '5':
                return

            if choice in reset_options:
                selected_option = reset_options[choice]
                if self._execute_data_reset(selected_option):
                    break
            else:
                self._show_error("Invalid selection. Please choose 1-5.")
                if not HAS_RICH:
                    input("Press Enter to continue...")

    def _execute_data_reset(self, reset_option: dict) -> bool:
        """Execute the selected data reset operation with verification and backup."""
        try:
            # Step 1: Offer backup creation
            if HAS_RICH:
                console.print(create_panel(
                    f"About to reset: {reset_option['name']}\n\n{reset_option['description']}\n\nWould you like to create a backup before proceeding?",
                    title="🛡️ Backup Recommendation",
                    border_style="yellow",
                    box_type=ROUNDED
                ))

                create_backup = Confirm.ask(
                    "[yellow]Create backup before reset?[/yellow]",
                    default=True
                )
            else:
                print(f"\nAbout to reset: {reset_option['name']}")
                print(f"Description: {reset_option['description']}")
                print("\nWould you like to create a backup before proceeding?")

                backup_choice = input("Create backup before reset? (y/n) [y]: ").lower()
                create_backup = backup_choice != 'n'

            backup_path = None
            if create_backup:
                if HAS_RICH:
                    with console.status("[cyan]Creating backup...", spinner="dots"):
                        backup_path = self.user_manager.create_data_backup(reset_option['backup_type'])
                else:
                    print("Creating backup...")
                    backup_path = self.user_manager.create_data_backup(reset_option['backup_type'])

                if backup_path:
                    if HAS_RICH:
                        console.print(f"[green]✓ Backup created: {backup_path}[/green]")
                    else:
                        print(f"✓ Backup created: {backup_path}")
                else:
                    self._show_error("Failed to create backup. Reset operation cancelled.")
                    return False

            # Step 2: Send verification email
            if HAS_RICH:
                console.print(create_panel(
                    "Sending verification email...\nPlease check your email for a 6-digit verification code.",
                    title="📧 Email Verification",
                    border_style="cyan",
                    box_type=ROUNDED
                ))

                with console.status("[cyan]Sending verification email...", spinner="dots"):
                    email_sent = self.user_manager.send_data_reset_verification(
                        reset_option['name'],
                        reset_option['description']
                    )
            else:
                print("\nSending verification email...")
                print("Please check your email for a 6-digit verification code.")
                email_sent = self.user_manager.send_data_reset_verification(
                    reset_option['name'],
                    reset_option['description']
                )

            if not email_sent:
                self._show_error("Failed to send verification email. Reset operation cancelled.")
                return False

            # Step 3: Get verification code
            if HAS_RICH:
                console.print("[green]✓ Verification email sent![/green]")
                verification_code = Prompt.ask(
                    "\n[cyan]Enter the 6-digit verification code from your email[/cyan]",
                    password=False
                )
            else:
                print("✓ Verification email sent!")
                verification_code = input("\nEnter the 6-digit verification code from your email: ")

            # Step 4: Verify code
            if not self.user_manager.verify_data_reset_code(verification_code):
                self._show_error("Invalid or expired verification code. Reset operation cancelled.")
                return False

            # Step 5: Final confirmation
            if HAS_RICH:
                console.print(create_panel(
                    f"⚠️ FINAL WARNING ⚠️\n\nYou are about to permanently reset:\n{reset_option['name']}\n\nThis action CANNOT be undone!",
                    title="🚨 Final Confirmation",
                    border_style="red",
                    box_type=ROUNDED
                ))

                final_confirm = Confirm.ask(
                    "[bold red]Are you absolutely sure you want to proceed?[/bold red]",
                    default=False
                )
            else:
                print("\n" + "=" * 50)
                print("⚠️ FINAL WARNING ⚠️".center(50))
                print("=" * 50)
                print(f"You are about to permanently reset:")
                print(f"{reset_option['name']}")
                print("\nThis action CANNOT be undone!")

                final_choice = input("\nAre you absolutely sure you want to proceed? (yes/no): ").lower()
                final_confirm = final_choice == 'yes'

            if not final_confirm:
                if HAS_RICH:
                    console.print("[yellow]Reset operation cancelled by user.[/yellow]")
                else:
                    print("Reset operation cancelled by user.")
                return False

            # Step 6: Execute the reset
            if HAS_RICH:
                with console.status(f"[red]Executing {reset_option['name']}...", spinner="dots"):
                    reset_method = getattr(self.user_manager, reset_option['method'])
                    success = reset_method()
            else:
                print(f"Executing {reset_option['name']}...")
                reset_method = getattr(self.user_manager, reset_option['method'])
                success = reset_method()

            # Step 7: Show results
            if success:
                if HAS_RICH:
                    success_message = f"✅ {reset_option['name']} completed successfully!"
                    if backup_path:
                        success_message += f"\n\n📁 Backup saved to: {backup_path}"

                    console.print(create_panel(
                        success_message,
                        title="🎉 Reset Complete",
                        border_style="green",
                        box_type=ROUNDED
                    ))
                else:
                    print(f"\n✅ {reset_option['name']} completed successfully!")
                    if backup_path:
                        print(f"📁 Backup saved to: {backup_path}")

                return True
            else:
                self._show_error(f"Failed to execute {reset_option['name']}. Please try again or contact support.")
                return False

        except Exception as e:
            self._show_error(f"Error during reset operation: {str(e)}")
            return False

    def _show_error(self, message: str) -> None:
        """Display an error message."""
        if HAS_RICH:
            # Use helper function to create panel
            console.print(create_panel(
                message,
                title="Error",
                border_style="red",
                box_type=ROUNDED
            ))
        else:
            print(f"\nError: {message}")

    def _handle_action_setting(self, setting_key: str) -> None:
        """Handle special action settings like export/import data and clear history."""
        import json
        import os
        import datetime
        from pathlib import Path

        if setting_key == 'export_data':
            # Export user data to a JSON file
            if HAS_RICH:
                console.print(create_panel(
                    "This will export your user data to a JSON file",
                    title="Export Data",
                    border_style="cyan",
                    box_type=ROUNDED
                ))

                # Ask for export location
                export_dir = Prompt.ask(
                    "[cyan]Export directory[/cyan]",
                    default=str(Path.home())
                )
            else:
                print("\nExport Data")
                print("This will export your user data to a JSON file")
                export_dir = input(f"Export directory [{str(Path.home())}]: ") or str(Path.home())

            try:
                # Create export directory if it doesn't exist
                os.makedirs(export_dir, exist_ok=True)

                # Get current user data
                user_data = self.user_manager.get_current_user()

                # Create filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                username = user_data.get('username', 'user')
                filename = f"ecocycle_{username}_export_{timestamp}.json"
                filepath = os.path.join(export_dir, filename)

                # Export data
                with open(filepath, 'w') as f:
                    # Remove sensitive information
                    export_data = user_data.copy()
                    if 'password_hash' in export_data:
                        del export_data['password_hash']
                    if 'salt' in export_data:
                        del export_data['salt']

                    json.dump(export_data, f, indent=2)

                # Show success message
                if HAS_RICH:
                    console.print(create_panel(
                        f"Data exported successfully to:\n[bold]{filepath}[/bold]",
                        title="Export Complete",
                        border_style="green",
                        box_type=ROUNDED
                    ))
                else:
                    print(f"\nData exported successfully to: {filepath}")

            except Exception as e:
                self._show_error(f"Error exporting data: {str(e)}")

        elif setting_key == 'import_data':
            # Import user data from a JSON file
            if HAS_RICH:
                console.print(create_panel(
                    "This will import user data from a JSON file.\nWarning: This may overwrite your current settings.",
                    title="Import Data",
                    border_style="yellow",
                    box_type=ROUNDED
                ))

                # Ask for import file
                import_file = Prompt.ask(
                    "[cyan]Import file path[/cyan]",
                    default=""
                )

                if not import_file:
                    console.print("[yellow]Import cancelled.[/yellow]")
                    return

                # Confirm import
                confirm = Confirm.ask(
                    "Are you sure you want to import this data? This may overwrite your current settings.",
                    default=False
                )

                if not confirm:
                    console.print("[yellow]Import cancelled.[/yellow]")
                    return
            else:
                print("\nImport Data")
                print("This will import user data from a JSON file.")
                print("Warning: This may overwrite your current settings.")

                import_file = input("Import file path: ")

                if not import_file:
                    print("Import cancelled.")
                    return

                confirm = input("Are you sure you want to import this data? This may overwrite your current settings. (y/n): ")
                if confirm.lower() != 'y':
                    print("Import cancelled.")
                    return

            try:
                # Import data
                with open(import_file, 'r') as f:
                    import_data = json.load(f)

                # Validate imported data
                if not isinstance(import_data, dict):
                    self._show_error("Invalid import file format. Expected a JSON object.")
                    return

                # Import preferences
                if 'preferences' in import_data and isinstance(import_data['preferences'], dict):
                    for key, value in import_data['preferences'].items():
                        self.user_manager.update_user_preference(key, value)

                # Show success message
                if HAS_RICH:
                    console.print(create_panel(
                        "Data imported successfully!",
                        title="Import Complete",
                        border_style="green",
                        box_type=ROUNDED
                    ))
                else:
                    print("\nData imported successfully!")

            except Exception as e:
                self._show_error(f"Error importing data: {str(e)}")

        elif setting_key == 'reset_user_data':
            # Comprehensive data reset with verification
            self._handle_data_reset()

        elif setting_key == 'resend_verification_email':
            # Resend verification email
            if HAS_RICH:
                console.print(create_panel(
                    "This will resend the email verification link to your registered email address.",
                    title="Resend Verification Email",
                    border_style="cyan",
                    box_type=ROUNDED
                ))

                # Get current user
                user = self.user_manager.get_current_user()
                email = user.get('email')

                if not email:
                    console.print(create_panel(
                        "You don't have an email address associated with your account. Please update your profile with an email address first.",
                        title="Email Required",
                        border_style="yellow",
                        box_type=ROUNDED
                    ))
                    return

                # Confirm resend
                confirm = Confirm.ask(
                    f"Send verification email to {email}?",
                    default=True
                )

                if not confirm:
                    console.print("[yellow]Email verification cancelled.[/yellow]")
                    return

                # Resend verification email
                with console.status("[cyan]Sending verification email...", spinner="dots"):
                    success = self.user_manager.resend_verification_email(user.get('username'))

                if success:
                    console.print(create_panel(
                        f"Verification email sent to [bold]{email}[/bold]",
                        title="Email Sent",
                        border_style="green",
                        box_type=ROUNDED
                    ))
                else:
                    console.print(create_panel(
                        "Failed to send verification email. Please check your email settings.",
                        title="Email Error",
                        border_style="red",
                        box_type=ROUNDED
                    ))
            else:
                print("\nResend Verification Email")
                print("This will resend the email verification link to your registered email address.")

                # Get current user
                user = self.user_manager.get_current_user()
                email = user.get('email')

                if not email:
                    print("\nYou don't have an email address associated with your account.")
                    print("Please update your profile with an email address first.")
                    return

                # Confirm resend
                confirm = input(f"Send verification email to {email}? (y/n): ")
                if confirm.lower() != 'y':
                    print("Email verification cancelled.")
                    return

                # Resend verification email
                print("\nSending verification email...")
                success = self.user_manager.resend_verification_email(user.get('username'))

                if success:
                    print(f"\nVerification email sent to {email}")
                else:
                    print("\nFailed to send verification email. Please check your email settings.")

        elif setting_key == 'run_system_diagnostics':
            # Run comprehensive system diagnostics
            self._handle_system_diagnostics()

        elif setting_key == 'auto_repair_system':
            # Run automated system repair
            self._handle_auto_repair_system()

        elif setting_key == 'view_repair_history':
            # View system repair history
            self._handle_view_repair_history()


    def _load_notification_settings(self) -> Dict:
        """Load notification settings from file."""
        if os.path.exists(NOTIFICATION_SETTINGS_FILE):
            try:
                with open(NOTIFICATION_SETTINGS_FILE, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading notification settings: {e}")

        # Create default settings
        default_settings = {"default": DEFAULT_NOTIFICATION_SETTINGS}

        # Save default settings
        self._save_notification_settings(default_settings)

        return default_settings

    def _save_notification_settings(self, settings: Dict) -> bool:
        """Save notification settings to file."""
        try:
            with open(NOTIFICATION_SETTINGS_FILE, 'w') as file:
                json.dump(settings, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving notification settings: {e}")
            return False

    def _sync_notification_settings(self) -> None:
        """Sync notification settings between user preferences and notification settings file."""
        if not self.user_manager.is_authenticated():
            return

        username = self.user_manager.current_user

        # Check if user has notification settings
        if username not in self.notification_settings:
            # Copy default settings for this user
            self.notification_settings[username] = self.notification_settings["default"].copy()
            self._save_notification_settings(self.notification_settings)

        # Get user settings from notification settings file
        user_settings = self.notification_settings[username]

        # Update user preferences with notification settings
        for key, value in user_settings.items():
            # Convert eco_tips to eco_tips_enabled for compatibility
            if key == 'eco_tips':
                self.user_manager.update_user_preference('eco_tips_enabled', value)
            else:
                self.user_manager.update_user_preference(key, value)

    def _update_notification_settings(self, setting_key: str) -> None:
        """Update notification settings file when a notification setting is changed."""
        if not self.user_manager.is_authenticated():
            return

        username = self.user_manager.current_user

        # Check if user has notification settings
        if username not in self.notification_settings:
            # Copy default settings for this user
            self.notification_settings[username] = self.notification_settings["default"].copy()

        # Get the current value from user preferences
        value = self.user_manager.get_user_preference(
            setting_key,
            self.defaults.get(setting_key)
        )

        # Handle special case for eco_tips_enabled
        if setting_key == 'eco_tips_enabled':
            self.notification_settings[username]['eco_tips'] = value
        else:
            self.notification_settings[username][setting_key] = value

        # Save notification settings
        self._save_notification_settings(self.notification_settings)

    def search_settings(self) -> None:
        """Search for settings by keyword."""
        os.system('cls' if os.name == 'nt' else 'clear')

        if HAS_RICH:
            self._show_rich_header("Search Settings", "cyan")

            # Get search query
            search_query = Prompt.ask(
                "\n[bold cyan]Enter search term[/bold cyan]",
                default=""
            )

            if not search_query:
                console.print("[yellow]Search cancelled.[/yellow]")
                return

            # Search in settings
            results = []

            with console.status("[cyan]Searching settings...", spinner="dots"):
                for category in self.settings_categories:
                    for setting_key in category['settings']:
                        # Search in setting key
                        if search_query.lower() in setting_key.lower():
                            results.append((category['name'], setting_key))
                            continue

                        # Search in description
                        description = self.descriptions.get(setting_key, '')
                        if search_query.lower() in description.lower():
                            results.append((category['name'], setting_key))
                            continue

                        # Search in current value
                        current_value = self.user_manager.get_user_preference(
                            setting_key,
                            self.defaults.get(setting_key)
                        )
                        if isinstance(current_value, str) and search_query.lower() in str(current_value).lower():
                            results.append((category['name'], setting_key))

            # Display results
            if results:
                results_table = Table(title=f"Search Results for '{search_query}'", box=ROUNDED, border_style="cyan")
                results_table.add_column("Option", style="yellow")
                results_table.add_column("Setting", style="green")
                results_table.add_column("Category", style="blue")
                results_table.add_column("Current Value", style="cyan")
                results_table.add_column("Description", style="white")

                for i, (category_name, setting_key) in enumerate(results, 1):
                    current_value = self.user_manager.get_user_preference(
                        setting_key,
                        self.defaults.get(setting_key)
                    )

                    # Format boolean values for display
                    if self.types.get(setting_key) == bool:
                        display_value = "Enabled" if current_value else "Disabled"
                    # Add units for certain settings
                    elif setting_key.endswith('_kg'):
                        display_value = f"{current_value} kg"
                    elif setting_key.endswith('_cm'):
                        display_value = f"{current_value} cm"
                    else:
                        display_value = str(current_value)

                    results_table.add_row(
                        str(i),
                        setting_key.replace('_', ' ').title(),
                        category_name,
                        display_value,
                        self.descriptions.get(setting_key, '')
                    )

                console.print(results_table)

                # Allow user to select a setting to change
                choice = Prompt.ask(
                    "\n[bold cyan]Select a setting to change (or Enter to cancel)[/bold cyan]",
                    choices=[str(i) for i in range(1, len(results) + 1)] + [''],
                    default=""
                )

                if choice:
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(results):
                            _, setting_key = results[index]
                            self.update_setting(setting_key)
                    except ValueError:
                        self._show_error("Invalid input. Please enter a number.")
            else:
                console.print(create_panel(
                    f"No settings found matching '{search_query}'",
                    title="Search Results",
                    border_style="yellow",
                    box_type=ROUNDED
                ))
        else:
            self._show_basic_header("Search Settings")

            # Get search query
            search_query = input("\nEnter search term: ")

            if not search_query:
                print("Search cancelled.")
                return

            # Search in settings
            results = []

            print("\nSearching settings...")
            for category in self.settings_categories:
                for setting_key in category['settings']:
                    # Search in setting key
                    if search_query.lower() in setting_key.lower():
                        results.append((category['name'], setting_key))
                        continue

                    # Search in description
                    description = self.descriptions.get(setting_key, '')
                    if search_query.lower() in description.lower():
                        results.append((category['name'], setting_key))
                        continue

                    # Search in current value
                    current_value = self.user_manager.get_user_preference(
                        setting_key,
                        self.defaults.get(setting_key)
                    )
                    if isinstance(current_value, str) and search_query.lower() in str(current_value).lower():
                        results.append((category['name'], setting_key))

            # Display results
            if results:
                print(f"\nSearch Results for '{search_query}':")
                print("-" * 50)

                for i, (category_name, setting_key) in enumerate(results, 1):
                    current_value = self.user_manager.get_user_preference(
                        setting_key,
                        self.defaults.get(setting_key)
                    )

                    # Format boolean values for display
                    if self.types.get(setting_key) == bool:
                        display_value = "Enabled" if current_value else "Disabled"
                    # Add units for certain settings
                    elif setting_key.endswith('_kg'):
                        display_value = f"{current_value} kg"
                    elif setting_key.endswith('_cm'):
                        display_value = f"{current_value} cm"
                    else:
                        display_value = str(current_value)

                    print(f"{i}. {setting_key.replace('_', ' ').title()} ({category_name}): {display_value}")
                    print(f"   {self.descriptions.get(setting_key, '')}")

                # Allow user to select a setting to change
                choice = input("\nSelect a setting to change (or Enter to cancel): ")

                if choice:
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(results):
                            _, setting_key = results[index]
                            self.update_setting(setting_key)
                    except ValueError:
                        print("Invalid input. Please enter a number.")
            else:
                print(f"\nNo settings found matching '{search_query}'")

        input("\nPress Enter to continue...")

    def customize_theme(self) -> None:
        """Customize application theme with color picker."""
        if not HAS_UTILS:
            self._show_error("Theme customization requires the theme_manager module.")
            input("\nPress Enter to continue...")
            return

        os.system('cls' if os.name == 'nt' else 'clear')

        # Get theme manager
        theme_manager = get_theme_manager()

        if HAS_RICH:
            self._show_rich_header("Theme Customization", "magenta")

            # Get current theme
            current_theme_id = self.user_manager.get_user_preference('theme', 'default')
            current_theme = theme_manager.get_theme(current_theme_id)

            # Display current theme
            theme_table = Table(title="Current Theme", box=ROUNDED, border_style="magenta")
            theme_table.add_column("Property", style="cyan")
            theme_table.add_column("Value", style="green")

            theme_table.add_row("Name", current_theme.get('name', 'Default'))
            theme_table.add_row("Description", current_theme.get('description', ''))

            console.print(theme_table)

            # Display color options
            colors_table = Table(title="Theme Colors", box=ROUNDED, border_style="magenta")
            colors_table.add_column("Option", style="yellow")
            colors_table.add_column("Color Name", style="cyan")
            colors_table.add_column("Current Value", style="green")

            colors = current_theme.get('colors', {})
            color_options = list(colors.keys())

            for i, color_name in enumerate(color_options, 1):
                color_value = colors.get(color_name, '#FFFFFF')
                colors_table.add_row(
                    str(i),
                    color_name.replace('_', ' ').title(),
                    f"{color_value}"
                )

            console.print(colors_table)

            # Allow user to select a color to change
            choice = Prompt.ask(
                "\n[bold magenta]Select a color to change (or Enter to cancel)[/bold magenta]",
                choices=[str(i) for i in range(1, len(color_options) + 1)] + [''],
                default=""
            )

            if choice:
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(color_options):
                        color_name = color_options[index]
                        current_color = colors.get(color_name, '#FFFFFF')

                        # Get new color
                        new_color = Prompt.ask(
                            f"\n[bold magenta]Enter new color for {color_name}[/bold magenta] (hex format, e.g. #FF5500)",
                            default=current_color
                        )

                        # Validate color
                        if not new_color.startswith('#') or not all(c in '0123456789ABCDEFabcdef' for c in new_color[1:]):
                            self._show_error("Invalid color format. Please use hex format (e.g. #FF5500).")
                        else:
                            # Create custom theme based on current theme
                            custom_theme = current_theme.copy()
                            custom_theme['name'] = 'Custom'
                            custom_theme['description'] = 'Your customized theme'

                            # Update color
                            custom_colors = custom_theme.get('colors', {}).copy()
                            custom_colors[color_name] = new_color
                            custom_theme['colors'] = custom_colors

                            # Save custom theme
                            theme_manager.create_theme('custom', custom_theme)

                            # Set as current theme
                            self.user_manager.update_user_preference('theme', 'custom')
                            theme_manager.set_current_theme('custom')

                            console.print(create_panel(
                                f"Theme updated with new {color_name} color: [bold]{new_color}[/bold]",
                                title="Theme Updated",
                                border_style="green",
                                box_type=ROUNDED
                            ))
                except ValueError:
                    self._show_error("Invalid input. Please enter a number.")
        else:
            self._show_basic_header("Theme Customization")

            # Get current theme
            current_theme_id = self.user_manager.get_user_preference('theme', 'default')
            current_theme = theme_manager.get_theme(current_theme_id)

            # Display current theme
            print("\nCurrent Theme:")
            print(f"Name: {current_theme.get('name', 'Default')}")
            print(f"Description: {current_theme.get('description', '')}")

            # Display color options
            print("\nTheme Colors:")
            colors = current_theme.get('colors', {})
            color_options = list(colors.keys())

            for i, color_name in enumerate(color_options, 1):
                color_value = colors.get(color_name, '#FFFFFF')
                print(f"{i}. {color_name.replace('_', ' ').title()}: {color_value}")

            # Allow user to select a color to change
            choice = input("\nSelect a color to change (or Enter to cancel): ")

            if choice:
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(color_options):
                        color_name = color_options[index]
                        current_color = colors.get(color_name, '#FFFFFF')

                        # Get new color
                        new_color = input(f"\nEnter new color for {color_name} (hex format, e.g. #FF5500) [{current_color}]: ") or current_color

                        # Validate color
                        if not new_color.startswith('#') or not all(c in '0123456789ABCDEFabcdef' for c in new_color[1:]):
                            print("Invalid color format. Please use hex format (e.g. #FF5500).")
                        else:
                            # Create custom theme based on current theme
                            custom_theme = current_theme.copy()
                            custom_theme['name'] = 'Custom'
                            custom_theme['description'] = 'Your customized theme'

                            # Update color
                            custom_colors = custom_theme.get('colors', {}).copy()
                            custom_colors[color_name] = new_color
                            custom_theme['colors'] = custom_colors

                            # Save custom theme
                            theme_manager.create_theme('custom', custom_theme)

                            # Set as current theme
                            self.user_manager.update_user_preference('theme', 'custom')
                            theme_manager.set_current_theme('custom')

                            print(f"\nTheme updated with new {color_name} color: {new_color}")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        input("\nPress Enter to continue...")

    def _handle_system_diagnostics(self) -> None:
        """Handle system diagnostics action."""
        try:
            from utils.system_repair import SystemRepair

            if HAS_RICH:
                console.print(create_panel(
                    "Running comprehensive system diagnostics...\nThis will check cache files, database integrity, configuration, and more.",
                    title="🔍 System Diagnostics",
                    border_style="cyan",
                    box_type=ROUNDED
                ))

                with console.status("[cyan]Running system diagnostics...", spinner="dots"):
                    system_repair = SystemRepair()
                    diagnostics = system_repair.run_comprehensive_diagnostics()

                self._display_diagnostics_results(diagnostics)
            else:
                print("\nSystem Diagnostics")
                print("Running comprehensive system diagnostics...")
                print("This will check cache files, database integrity, configuration, and more.")

                system_repair = SystemRepair()
                diagnostics = system_repair.run_comprehensive_diagnostics()

                self._display_diagnostics_results_basic(diagnostics)

        except ImportError:
            self._show_error("System repair module not available. Please check your installation.")
        except Exception as e:
            self._show_error(f"Error running system diagnostics: {str(e)}")

        input("\nPress Enter to continue...")

    def _handle_auto_repair_system(self) -> None:
        """Handle automated system repair action."""
        try:
            from utils.system_repair import SystemRepair

            # Get backup preference
            backup_before_repair = self.user_manager.get_user_preference('backup_before_repair', True)

            if HAS_RICH:
                console.print(create_panel(
                    "This will automatically diagnose and repair common system issues.\n\n⚠️ Warning: This may modify system files and settings.",
                    title="🔧 Automated System Repair",
                    border_style="yellow",
                    box_type=ROUNDED
                ))

                # Confirm repair
                confirm = Confirm.ask(
                    f"[yellow]Proceed with automated repair? (Backup: {'Yes' if backup_before_repair else 'No'})[/yellow]",
                    default=False
                )

                if not confirm:
                    console.print("[yellow]System repair cancelled.[/yellow]")
                    return

                with console.status("[yellow]Running automated system repair...", spinner="dots"):
                    system_repair = SystemRepair()
                    repair_result = system_repair.auto_repair_system(create_backup=backup_before_repair)

                self._display_repair_results(repair_result)
            else:
                print("\nAutomated System Repair")
                print("This will automatically diagnose and repair common system issues.")
                print("⚠️ Warning: This may modify system files and settings.")

                confirm = input(f"Proceed with automated repair? (Backup: {'Yes' if backup_before_repair else 'No'}) (y/n): ")
                if confirm.lower() != 'y':
                    print("System repair cancelled.")
                    return

                print("\nRunning automated system repair...")
                system_repair = SystemRepair()
                repair_result = system_repair.auto_repair_system(create_backup=backup_before_repair)

                self._display_repair_results_basic(repair_result)

        except ImportError:
            self._show_error("System repair module not available. Please check your installation.")
        except Exception as e:
            self._show_error(f"Error running automated repair: {str(e)}")

        input("\nPress Enter to continue...")

    def _handle_view_repair_history(self) -> None:
        """Handle view repair history action."""
        try:
            from utils.system_repair import SystemRepair

            if HAS_RICH:
                console.print(create_panel(
                    "Loading system repair history...",
                    title="📋 Repair History",
                    border_style="cyan",
                    box_type=ROUNDED
                ))

                with console.status("[cyan]Loading repair history...", spinner="dots"):
                    system_repair = SystemRepair()
                    history = system_repair.get_repair_history()

                self._display_repair_history(history)
            else:
                print("\nRepair History")
                print("Loading system repair history...")

                system_repair = SystemRepair()
                history = system_repair.get_repair_history()

                self._display_repair_history_basic(history)

        except ImportError:
            self._show_error("System repair module not available. Please check your installation.")
        except Exception as e:
            self._show_error(f"Error loading repair history: {str(e)}")

        input("\nPress Enter to continue...")

    def _display_diagnostics_results(self, diagnostics: Dict[str, Any]) -> None:
        """Display diagnostics results using Rich UI."""
        if diagnostics.get('status') == 'error':
            console.print(create_panel(
                f"Error running diagnostics: {diagnostics.get('error', 'Unknown error')}",
                title="❌ Diagnostics Error",
                border_style="red",
                box_type=ROUNDED
            ))
            return

        # System health overview
        health = diagnostics.get('system_health', 'unknown')
        health_colors = {
            'excellent': 'green',
            'good': 'green',
            'fair': 'yellow',
            'poor': 'red',
            'critical': 'red'
        }
        health_color = health_colors.get(health, 'white')

        console.print(create_panel(
            f"System Health: [{health_color}]{health.upper()}[/{health_color}]\nIssues Found: {len(diagnostics.get('issues_found', []))}",
            title="🏥 System Health Overview",
            border_style=health_color,
            box_type=ROUNDED
        ))

        # Issues summary
        issues = diagnostics.get('issues_found', [])
        if issues:
            issues_table = create_table(
                title="🚨 Issues Found",
                border_style="red",
                box_type=ROUNDED
            )
            issues_table.add_column("Issue", style="red")

            for issue in issues[:10]:  # Show first 10 issues
                issues_table.add_row(issue)

            if len(issues) > 10:
                issues_table.add_row(f"... and {len(issues) - 10} more issues")

            console.print(issues_table)
        else:
            console.print(create_panel(
                "✅ No issues found! Your system is healthy.",
                title="✅ All Clear",
                border_style="green",
                box_type=ROUNDED
            ))

        # Detailed results
        checks_table = create_table(
            title="📋 Detailed Check Results",
            border_style="cyan",
            box_type=ROUNDED
        )
        checks_table.add_column("Check", style="cyan")
        checks_table.add_column("Status", style="white")
        checks_table.add_column("Issues", style="yellow")

        for check in diagnostics.get('checks_performed', []):
            check_data = diagnostics.get(check, {})
            status = check_data.get('status', 'unknown')
            check_issues = len(check_data.get('issues', []))

            status_display = {
                'healthy': '✅ Healthy',
                'issues_found': '⚠️ Issues Found',
                'error': '❌ Error'
            }.get(status, status)

            checks_table.add_row(
                check.replace('_', ' ').title(),
                status_display,
                str(check_issues) if check_issues > 0 else "None"
            )

        console.print(checks_table)

    def _display_diagnostics_results_basic(self, diagnostics: Dict[str, Any]) -> None:
        """Display diagnostics results using basic UI."""
        if diagnostics.get('status') == 'error':
            print(f"\nError running diagnostics: {diagnostics.get('error', 'Unknown error')}")
            return

        # System health overview
        health = diagnostics.get('system_health', 'unknown')
        print(f"\nSystem Health: {health.upper()}")
        print(f"Issues Found: {len(diagnostics.get('issues_found', []))}")

        # Issues summary
        issues = diagnostics.get('issues_found', [])
        if issues:
            print("\n🚨 Issues Found:")
            print("-" * 50)
            for i, issue in enumerate(issues[:10], 1):
                print(f"{i}. {issue}")

            if len(issues) > 10:
                print(f"... and {len(issues) - 10} more issues")
        else:
            print("\n✅ No issues found! Your system is healthy.")

        # Detailed results
        print("\n📋 Detailed Check Results:")
        print("-" * 50)
        for check in diagnostics.get('checks_performed', []):
            check_data = diagnostics.get(check, {})
            status = check_data.get('status', 'unknown')
            check_issues = len(check_data.get('issues', []))

            status_display = {
                'healthy': '✅ Healthy',
                'issues_found': '⚠️ Issues Found',
                'error': '❌ Error'
            }.get(status, status)

            print(f"{check.replace('_', ' ').title()}: {status_display} ({check_issues} issues)")

    def _display_repair_results(self, repair_result: Dict[str, Any]) -> None:
        """Display repair results using Rich UI."""
        if repair_result.get('status') == 'error':
            console.print(create_panel(
                f"Error during repair: {repair_result.get('error', 'Unknown error')}",
                title="❌ Repair Error",
                border_style="red",
                box_type=ROUNDED
            ))
            return

        # Repair summary
        successful = len(repair_result.get('repairs_successful', []))
        failed = len(repair_result.get('repairs_failed', []))
        remaining = len(repair_result.get('issues_remaining', []))

        summary_color = "green" if failed == 0 else "yellow" if successful > 0 else "red"

        console.print(create_panel(
            f"Repairs Successful: {successful}\nRepairs Failed: {failed}\nIssues Remaining: {remaining}",
            title="🔧 Repair Summary",
            border_style=summary_color,
            box_type=ROUNDED
        ))

        # Backup info
        if repair_result.get('backup_created'):
            console.print(create_panel(
                f"Backup created at: {repair_result.get('backup_path', 'Unknown location')}",
                title="💾 Backup Created",
                border_style="blue",
                box_type=ROUNDED
            ))

        # Successful repairs
        if repair_result.get('repairs_successful'):
            success_table = create_table(
                title="✅ Successful Repairs",
                border_style="green",
                box_type=ROUNDED
            )
            success_table.add_column("Repair Type", style="green")

            for repair in repair_result['repairs_successful']:
                success_table.add_row(repair.replace('_', ' ').title())

            console.print(success_table)

        # Failed repairs
        if repair_result.get('repairs_failed'):
            failed_table = create_table(
                title="❌ Failed Repairs",
                border_style="red",
                box_type=ROUNDED
            )
            failed_table.add_column("Repair Type", style="red")

            for repair in repair_result['repairs_failed']:
                failed_table.add_row(repair.replace('_', ' ').title())

            console.print(failed_table)

        # Remaining issues
        if repair_result.get('issues_remaining'):
            remaining_table = create_table(
                title="⚠️ Remaining Issues",
                border_style="yellow",
                box_type=ROUNDED
            )
            remaining_table.add_column("Issue", style="yellow")

            for issue in repair_result['issues_remaining'][:5]:  # Show first 5
                remaining_table.add_row(issue)

            if len(repair_result['issues_remaining']) > 5:
                remaining_table.add_row(f"... and {len(repair_result['issues_remaining']) - 5} more")

            console.print(remaining_table)

    def _display_repair_results_basic(self, repair_result: Dict[str, Any]) -> None:
        """Display repair results using basic UI."""
        if repair_result.get('status') == 'error':
            print(f"\nError during repair: {repair_result.get('error', 'Unknown error')}")
            return

        # Repair summary
        successful = len(repair_result.get('repairs_successful', []))
        failed = len(repair_result.get('repairs_failed', []))
        remaining = len(repair_result.get('issues_remaining', []))

        print(f"\n🔧 Repair Summary:")
        print(f"Repairs Successful: {successful}")
        print(f"Repairs Failed: {failed}")
        print(f"Issues Remaining: {remaining}")

        # Backup info
        if repair_result.get('backup_created'):
            print(f"\n💾 Backup created at: {repair_result.get('backup_path', 'Unknown location')}")

        # Successful repairs
        if repair_result.get('repairs_successful'):
            print("\n✅ Successful Repairs:")
            for repair in repair_result['repairs_successful']:
                print(f"  - {repair.replace('_', ' ').title()}")

        # Failed repairs
        if repair_result.get('repairs_failed'):
            print("\n❌ Failed Repairs:")
            for repair in repair_result['repairs_failed']:
                print(f"  - {repair.replace('_', ' ').title()}")

        # Remaining issues
        if repair_result.get('issues_remaining'):
            print("\n⚠️ Remaining Issues:")
            for issue in repair_result['issues_remaining'][:5]:  # Show first 5
                print(f"  - {issue}")

            if len(repair_result['issues_remaining']) > 5:
                print(f"  ... and {len(repair_result['issues_remaining']) - 5} more")

    def _display_repair_history(self, history: List[Dict[str, Any]]) -> None:
        """Display repair history using Rich UI."""
        if not history:
            console.print(create_panel(
                "No repair history found.",
                title="📋 Repair History",
                border_style="yellow",
                box_type=ROUNDED
            ))
            return

        history_table = create_table(
            title="📋 System Repair History",
            border_style="cyan",
            box_type=ROUNDED
        )
        history_table.add_column("Date", style="cyan")
        history_table.add_column("Status", style="white")
        history_table.add_column("Successful", style="green")
        history_table.add_column("Failed", style="red")
        history_table.add_column("Remaining", style="yellow")

        for repair in history[-10:]:  # Show last 10 repairs
            timestamp = repair.get('timestamp', 'Unknown')
            if timestamp != 'Unknown':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = timestamp[:16]  # Fallback
            else:
                date_str = 'Unknown'

            status = repair.get('status', 'unknown')
            successful = len(repair.get('repairs_successful', []))
            failed = len(repair.get('repairs_failed', []))
            remaining = len(repair.get('issues_remaining', []))

            status_display = {
                'completed': '✅ Completed',
                'error': '❌ Error',
                'running': '🔄 Running'
            }.get(status, status)

            history_table.add_row(
                date_str,
                status_display,
                str(successful),
                str(failed),
                str(remaining)
            )

        console.print(history_table)

        # Show details of most recent repair
        if history:
            latest = history[-1]
            console.print(create_panel(
                f"Latest Repair Details:\nTimestamp: {latest.get('timestamp', 'Unknown')}\nBackup Created: {'Yes' if latest.get('backup_created') else 'No'}",
                title="🔍 Latest Repair",
                border_style="blue",
                box_type=ROUNDED
            ))

    def _display_repair_history_basic(self, history: List[Dict[str, Any]]) -> None:
        """Display repair history using basic UI."""
        if not history:
            print("\nNo repair history found.")
            return

        print("\n📋 System Repair History:")
        print("-" * 80)
        print(f"{'Date':<20} {'Status':<12} {'Successful':<10} {'Failed':<8} {'Remaining':<10}")
        print("-" * 80)

        for repair in history[-10:]:  # Show last 10 repairs
            timestamp = repair.get('timestamp', 'Unknown')
            if timestamp != 'Unknown':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = timestamp[:16]  # Fallback
            else:
                date_str = 'Unknown'

            status = repair.get('status', 'unknown')
            successful = len(repair.get('repairs_successful', []))
            failed = len(repair.get('repairs_failed', []))
            remaining = len(repair.get('issues_remaining', []))

            status_display = {
                'completed': '✅ Completed',
                'error': '❌ Error',
                'running': '🔄 Running'
            }.get(status, status)

            print(f"{date_str:<20} {status_display:<12} {successful:<10} {failed:<8} {remaining:<10}")

        # Show details of most recent repair
        if history:
            latest = history[-1]
            print(f"\n🔍 Latest Repair Details:")
            print(f"Timestamp: {latest.get('timestamp', 'Unknown')}")
            print(f"Backup Created: {'Yes' if latest.get('backup_created') else 'No'})")


def show_settings(user_manager_instance):
    """Main function to display the settings view."""
    settings_view = SettingsView(user_manager_instance)
    settings_view.show_main_menu()
