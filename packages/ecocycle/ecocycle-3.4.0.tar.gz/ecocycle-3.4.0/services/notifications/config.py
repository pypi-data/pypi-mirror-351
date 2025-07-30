"""
EcoCycle - Notification System Configuration
Contains constants and configuration for the notification system.
"""
import os
import logging

# Import from main config
from config.config import NOTIFICATION_SETTINGS_FILE

logger = logging.getLogger(__name__)

# Constants
# NOTIFICATION_SETTINGS_FILE is now imported from config.config
NOTIFICATION_LOGS_FILE = "Logs/notification_logs.json"
EMAIL_TEMPLATES_DIR = "email_templates"

# Email configuration
EMAIL_SENDER = os.environ.get("GMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# Default settings
DEFAULT_NOTIFICATION_SETTINGS = {
    "email_notifications": False,
    "sms_notifications": False,
    "achievement_notifications": True,
    "weekly_summary": True,
    "eco_tips": True,
    "reminder_frequency": "weekly"  # none, daily, weekly, monthly
}

# Default logs structure
DEFAULT_NOTIFICATION_LOGS = {
    "email_logs": [],
    "sms_logs": [],
    "app_logs": []
}
