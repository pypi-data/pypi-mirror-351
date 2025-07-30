"""
EcoCycle - Notification Storage Module
Handles loading and saving notification settings and logs.
"""
import os
import json
import logging
from typing import Dict, Any

from services.notifications.config import (
    NOTIFICATION_SETTINGS_FILE, NOTIFICATION_LOGS_FILE,
    DEFAULT_NOTIFICATION_SETTINGS, DEFAULT_NOTIFICATION_LOGS
)

logger = logging.getLogger(__name__)


class NotificationStorage:
    """Storage manager for notification settings and logs."""
    
    @staticmethod
    def load_notification_settings() -> Dict:
        """
        Load notification settings from file.
        
        Returns:
            Dict: Notification settings
        """
        if os.path.exists(NOTIFICATION_SETTINGS_FILE):
            try:
                with open(NOTIFICATION_SETTINGS_FILE, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading notification settings: {e}")
        
        # Create default settings
        default_settings = {"default": DEFAULT_NOTIFICATION_SETTINGS}
        
        # Save default settings
        NotificationStorage.save_notification_settings(default_settings)
        
        return default_settings
    
    @staticmethod
    def save_notification_settings(settings: Dict) -> bool:
        """
        Save notification settings to file.
        
        Args:
            settings (Dict): Notification settings to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(NOTIFICATION_SETTINGS_FILE, 'w') as file:
                json.dump(settings, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving notification settings: {e}")
            return False
    
    @staticmethod
    def load_notification_logs() -> Dict:
        """
        Load notification logs from file.
        
        Returns:
            Dict: Notification logs
        """
        if os.path.exists(NOTIFICATION_LOGS_FILE):
            try:
                with open(NOTIFICATION_LOGS_FILE, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading notification logs: {e}")
        
        # Create default logs structure
        default_logs = DEFAULT_NOTIFICATION_LOGS
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(NOTIFICATION_LOGS_FILE), exist_ok=True)
        
        # Save default logs
        NotificationStorage.save_notification_logs(default_logs)
        
        return default_logs
    
    @staticmethod
    def save_notification_logs(logs: Dict) -> bool:
        """
        Save notification logs to file.
        
        Args:
            logs (Dict): Notification logs to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(NOTIFICATION_LOGS_FILE), exist_ok=True)
            
            with open(NOTIFICATION_LOGS_FILE, 'w') as file:
                json.dump(logs, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving notification logs: {e}")
            return False
