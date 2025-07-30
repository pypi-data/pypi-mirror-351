"""
EcoCycle - Notifications Package
Provides a modular notification system for the EcoCycle application.
"""

# Re-export the main components for cleaner imports
from services.notifications.notification_system import NotificationSystem, run_notification_manager
from services.notifications.manager import NotificationManager
from services.notifications.ui import NotificationUI
from services.notifications.senders import EmailSender, SmsSender, AppNotifier
from services.notifications.storage import NotificationStorage
from services.notifications.templates import TemplateManager
from services.notifications.generators import ContentGenerator

# Provide backwards compatibility
__all__ = [
    'NotificationSystem',
    'run_notification_manager',
    'NotificationManager',
    'NotificationUI',
    'EmailSender',
    'SmsSender',
    'AppNotifier',
    'NotificationStorage',
    'TemplateManager',
    'ContentGenerator',
]