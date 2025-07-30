"""
EcoCycle - Notification Manager Module
Main notification system controller that orchestrates all notification components.
"""
import os
import logging
import datetime
from typing import Dict, List, Optional, Any, Tuple, Union

from services.notifications.config import DEFAULT_NOTIFICATION_SETTINGS
from services.notifications.storage import NotificationStorage
from services.notifications.templates import TemplateManager
from services.notifications.senders import EmailSender, SmsSender, AppNotifier
from services.notifications.ui import NotificationUI
from services.notifications.generators import ContentGenerator

logger = logging.getLogger(__name__)


class NotificationManager:
    """Notification manager for EcoCycle application."""

    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the notification system.

        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager

        # Create directories for templates
        from services.notifications.config import EMAIL_TEMPLATES_DIR
        os.makedirs(EMAIL_TEMPLATES_DIR, exist_ok=True)

        # Load notification settings and logs
        self.notification_settings = NotificationStorage.load_notification_settings()
        self.notification_logs = NotificationStorage.load_notification_logs()

        # Create default templates
        TemplateManager.create_default_templates()

    def run_notification_manager(self) -> None:
        """Run the notification system interactive interface with Rich UI styling."""
        NotificationUI.print_header("EcoCycle Notification Center")

        # Get username if not in test mode
        if self.user_manager is None:
            username = NotificationUI.get_string_input("Enter username")
        else:
            # List users
            usernames = list(self.user_manager.users.keys())
            for i, name in enumerate(usernames):
                NotificationUI.print_message(f"{i+1}. {name}")

            selection = NotificationUI.get_string_input("Select user (number or username)")

            try:
                # Try to interpret as index
                idx = int(selection) - 1
                if 0 <= idx < len(usernames):
                    username = usernames[idx]
                else:
                    username = selection
            except ValueError:
                username = selection

        # Main menu loop
        while True:
            NotificationUI.print_header(f"Notification Center - {username}")

            options = [
                "Update notification settings",
                "Update contact information",
                "View notification history",
                "Test notifications",
                "Process scheduled notifications",
                "Return to main menu"
            ]

            for i, option in enumerate(options):
                NotificationUI.print_message(f"{i+1}. {option}")

            choice = NotificationUI.get_string_input("\nSelect option")

            if choice == "1":
                self.update_notification_settings(username)
            elif choice == "2":
                self.update_contact_information(username)
            elif choice == "3":
                self.view_notification_history(username)
            elif choice == "4":
                self.test_notifications(username)
            elif choice == "5":
                sent_count = self.process_scheduled_notifications()
                NotificationUI.print_message(f"Processed {sent_count} notifications.")
            elif choice == "6" or choice.lower() in ("q", "quit", "exit"):
                break
            else:
                NotificationUI.print_message("Invalid option. Please try again.", "yellow")

    def update_notification_settings(self, username: str) -> None:
        """
        Update notification settings for a user with Rich UI styling.

        Args:
            username (str): Username to update settings for
        """
        NotificationUI.print_header(f"Update Notification Settings - {username}")

        # Check if user has notification settings
        if username not in self.notification_settings:
            # Copy default settings for this user
            self.notification_settings[username] = self.notification_settings["default"].copy()
            NotificationStorage.save_notification_settings(self.notification_settings)

        user_settings = self.notification_settings[username]

        # Display current settings
        NotificationUI.print_message("Current notification settings:", "blue")
        for setting, value in user_settings.items():
            NotificationUI.print_message(f"{setting}: {value}")

        # Update settings
        email_notifications = NotificationUI.get_boolean_input(
            "Enable email notifications?",
            default=user_settings.get("email_notifications", False)
        )

        sms_notifications = NotificationUI.get_boolean_input(
            "Enable SMS notifications?",
            default=user_settings.get("sms_notifications", False)
        )

        achievement_notifications = NotificationUI.get_boolean_input(
            "Enable achievement notifications?",
            default=user_settings.get("achievement_notifications", True)
        )

        weekly_summary = NotificationUI.get_boolean_input(
            "Enable weekly summary emails?",
            default=user_settings.get("weekly_summary", True)
        )

        eco_tips = NotificationUI.get_boolean_input(
            "Enable daily eco tips?",
            default=user_settings.get("eco_tips", True)
        )

        # Reminder frequency options
        NotificationUI.print_message("\nReminder frequency options:", "blue")
        reminder_options = ["none", "daily", "weekly", "monthly"]
        for i, option in enumerate(reminder_options):
            NotificationUI.print_message(f"{i+1}. {option}")

        reminder_choice = NotificationUI.get_string_input(
            "Select reminder frequency (number or name)",
            default=user_settings.get("reminder_frequency", "weekly")
        )

        try:
            # Try to interpret as index
            idx = int(reminder_choice) - 1
            if 0 <= idx < len(reminder_options):
                reminder_frequency = reminder_options[idx]
            else:
                reminder_frequency = reminder_choice
        except ValueError:
            reminder_frequency = reminder_choice

        # Validate reminder frequency
        if reminder_frequency not in reminder_options:
            NotificationUI.print_message(f"Invalid reminder frequency: {reminder_frequency}. Using 'weekly'.", "yellow")
            reminder_frequency = "weekly"

        # Update settings
        user_settings.update({
            "email_notifications": email_notifications,
            "sms_notifications": sms_notifications,
            "achievement_notifications": achievement_notifications,
            "weekly_summary": weekly_summary,
            "eco_tips": eco_tips,
            "reminder_frequency": reminder_frequency
        })

        # Save settings
        if NotificationStorage.save_notification_settings(self.notification_settings):
            NotificationUI.print_message("Notification settings updated successfully.", "green")
        else:
            NotificationUI.print_message("Failed to save notification settings.", "red")

    def update_contact_information(self, username: str) -> None:
        """
        Update contact information for a user with Rich UI styling.

        Args:
            username (str): Username to update contact info for
        """
        if not self.user_manager:
            NotificationUI.print_message(
                "User manager not available. Cannot update contact information.",
                "red"
            )
            return

        NotificationUI.print_header(f"Update Contact Information - {username}")

        # Check if user exists
        user = self.user_manager.get_user(username)
        if not user:
            NotificationUI.print_message(f"User '{username}' not found.", "red")
            return

        # Display current contact information
        NotificationUI.print_message("Current contact information:", "blue")
        NotificationUI.print_message(f"Email: {user.get('email', 'Not set')}")
        NotificationUI.print_message(f"Phone: {user.get('phone', 'Not set')}")

        # Update email
        email = NotificationUI.get_string_input(
            "Email address",
            default=user.get('email', '')
        )

        # Update phone
        phone = NotificationUI.get_string_input(
            "Phone number",
            default=user.get('phone', '')
        )

        # Update carrier if phone is provided
        carrier = None
        if phone:
            carrier_options = list(SmsSender.CARRIER_GATEWAYS.keys())
            NotificationUI.print_message("\nMobile carrier options:", "blue")
            for i, option in enumerate(carrier_options):
                NotificationUI.print_message(f"{i+1}. {option}")

            carrier_choice = NotificationUI.get_string_input(
                "Select mobile carrier (number or name)",
                default=user.get('carrier', carrier_options[0] if carrier_options else '')
            )

            try:
                # Try to interpret as index
                idx = int(carrier_choice) - 1
                if 0 <= idx < len(carrier_options):
                    carrier = carrier_options[idx]
                else:
                    carrier = carrier_choice
            except ValueError:
                carrier = carrier_choice

        # Update user information
        user_updated = self.user_manager.update_user(username, {
            'email': email,
            'phone': phone,
            'carrier': carrier
        })

        if user_updated:
            NotificationUI.print_message("Contact information updated successfully.", "green")
        else:
            NotificationUI.print_message("Failed to update contact information.", "red")

    def view_notification_history(self, username: str) -> None:
        """
        View notification history for a user with Rich UI styling.

        Args:
            username (str): Username to view history for
        """
        NotificationUI.print_header(f"Notification History - {username}")

        # Filter logs for user
        email_logs = [log for log in self.notification_logs["email_logs"]
                      if log.get("username") == username]
        sms_logs = [log for log in self.notification_logs["sms_logs"]
                    if log.get("username") == username]
        app_logs = [log for log in self.notification_logs["app_logs"]
                    if log.get("username") == username]

        # Display logs
        NotificationUI.display_email_logs(email_logs)
        NotificationUI.display_sms_logs(sms_logs)
        NotificationUI.display_app_logs(app_logs)

    def test_notifications(self, username: str) -> None:
        """
        Test sending notifications to a user with Rich UI styling.

        Args:
            username (str): Username to test notifications with
        """
        if not self.user_manager:
            NotificationUI.print_message(
                "User manager not available. Cannot test notifications.",
                "red"
            )
            return

        NotificationUI.print_header(f"Test Notifications - {username}")

        # Check if user exists
        if username in self.user_manager.users:
            user = self.user_manager.users[username]
        else:
            NotificationUI.print_message(f"User '{username}' not found.", "red")
            return

        # Check if user has notification settings
        if username not in self.notification_settings:
            # Copy default settings for this user
            self.notification_settings[username] = self.notification_settings["default"].copy()
            NotificationStorage.save_notification_settings(self.notification_settings)

        # Get user name
        name = user.get('name', username)

        # Test options
        NotificationUI.print_message("Select notification type to test:", "blue")
        options = [
            "Email notification",
            "SMS notification",
            "Achievement notification",
            "Weekly summary",
            "Eco tip",
            "Reminder",
            "Return to menu"
        ]

        for i, option in enumerate(options):
            NotificationUI.print_message(f"{i+1}. {option}")

        choice = NotificationUI.get_string_input("\nSelect option")

        if choice == "1":
            # Test email
            if not user.get('email'):
                NotificationUI.print_message("No email address set for this user.", "yellow")
                return

            subject = NotificationUI.get_string_input("Email subject", "EcoCycle Test Email")
            message = NotificationUI.get_string_input("Email message", f"Hello {name}, this is a test email from EcoCycle.")

            status, error = EmailSender.send_email(
                to_email=user.get('email'),
                subject=subject,
                message_body=message
            )

            # Log attempt
            self._log_email_attempt(
                username=username,
                to_email=user.get('email'),
                subject=subject,
                message=message,
                status="success" if status else "failed",
                error=error
            )

            if status:
                NotificationUI.print_message("Test email sent successfully.", "green")
            else:
                NotificationUI.print_message(f"Failed to send test email: {error}", "red")

        elif choice == "2":
            # Test SMS
            if not user.get('phone'):
                NotificationUI.print_message("No phone number set for this user.", "yellow")
                return

            if not user.get('carrier'):
                NotificationUI.print_message("No carrier set for this user.", "yellow")
                return

            message = NotificationUI.get_string_input("SMS message", f"EcoCycle Test SMS")

            status, error = SmsSender.send_sms_via_email(
                to_phone=user.get('phone'),
                carrier=user.get('carrier'),
                message_body=message
            )

            # Log attempt
            self._log_sms_attempt(
                username=username,
                to_phone=user.get('phone'),
                message=message,
                status="success" if status else "failed",
                error=error
            )

            if status:
                NotificationUI.print_message("Test SMS sent successfully.", "green")
            else:
                NotificationUI.print_message(f"Failed to send test SMS: {error}", "red")

        elif choice == "3":
            # Test achievement notification
            test_achievement = {
                "name": "Test Achievement",
                "description": "This is a test achievement for notification testing.",
                "points": 50
            }

            success = self.send_achievement_notification(username, test_achievement)

            if success:
                NotificationUI.print_message("Test achievement notification sent successfully.", "green")
            else:
                NotificationUI.print_message("Failed to send test achievement notification.", "red")

        elif choice == "4":
            # Test weekly summary
            success = self.generate_weekly_summary(username)

            if success:
                NotificationUI.print_message("Test weekly summary sent successfully.", "green")
            else:
                NotificationUI.print_message("Failed to send test weekly summary.", "red")

        elif choice == "5":
            # Test eco tip
            success = self.send_daily_eco_tip(username)

            if success:
                NotificationUI.print_message("Test eco tip sent successfully.", "green")
            else:
                NotificationUI.print_message("Failed to send test eco tip.", "red")

        elif choice == "6":
            # Test reminder
            success = self.send_reminder(username)

            if success:
                NotificationUI.print_message("Test reminder sent successfully.", "green")
            else:
                NotificationUI.print_message("Failed to send test reminder.", "red")

        elif choice == "7" or choice.lower() in ("q", "quit", "exit"):
            return
        else:
            NotificationUI.print_message("Invalid option. Please try again.", "yellow")

    def _log_email_attempt(self, username, to_email, subject, message, status, error="") -> None:
        """
        Helper function to log email attempts consistently.

        Args:
            username (str): Username
            to_email (str): Recipient email
            subject (str): Email subject
            message (str): Email message
            status (str): Status of the attempt (success/failed)
            error (str): Error message if any
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "username": username,
            "to_email": to_email,
            "subject": subject,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "status": status,
            "error": error
        }

        self.notification_logs["email_logs"].append(log_entry)
        NotificationStorage.save_notification_logs(self.notification_logs)

    def _log_sms_attempt(self, username, to_phone, message, status, error="") -> None:
        """
        Helper function to log SMS attempts consistently.

        Args:
            username (str): Username
            to_phone (str): Recipient phone
            message (str): SMS message
            status (str): Status of the attempt (success/failed)
            error (str): Error message if any
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "username": username,
            "to_phone": to_phone,
            "message": message,
            "status": status,
            "error": error
        }

        self.notification_logs["sms_logs"].append(log_entry)
        NotificationStorage.save_notification_logs(self.notification_logs)

    def _log_app_notification(self, username, notification_type, message) -> None:
        """
        Log an in-app notification.

        Args:
            username (str): Recipient username
            notification_type (str): Type of notification (achievement, reminder, etc.)
            message (str): Notification message
        """
        log_entry = AppNotifier.create_notification(
            username=username,
            notification_type=notification_type,
            message=message
        )

        self.notification_logs["app_logs"].append(log_entry)
        NotificationStorage.save_notification_logs(self.notification_logs)

    def generate_weekly_summary(self, username: str) -> bool:
        """
        Generate and send a weekly cycling summary for a user.

        Args:
            username (str): Username to generate summary for

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.user_manager:
            logger.error("User manager not available. Cannot generate weekly summary.")
            return False

        # Check if user exists
        if username in self.user_manager.users:
            user = self.user_manager.users[username]
        else:
            logger.error(f"User '{username}' not found.")
            return False

        # Get user settings
        user_settings = self.notification_settings.get(
            username,
            self.notification_settings.get("default", DEFAULT_NOTIFICATION_SETTINGS)
        )

        # Skip if weekly summary is disabled
        if not user_settings.get("weekly_summary", True):
            return False

        # Get user name
        name = user.get('name', username)

        # Get user data for summary generation
        user_data = user

        # Generate content
        content = ContentGenerator.generate_weekly_summary_content(
            username=username,
            name=name,
            user_data=user_data
        )

        if not content["subject"] or not content["body"]:
            logger.error(f"Failed to generate weekly summary content for user {username}")
            return False

        # Log in-app notification
        self._log_app_notification(
            username=username,
            notification_type="weekly_summary",
            message=f"Your weekly cycling summary is ready."
        )

        # Send email if enabled and email is set
        if user_settings.get("email_notifications", False) and user.get('email'):
            status, error = EmailSender.send_email(
                to_email=user.get('email'),
                subject=content["subject"],
                message_body=content["body"]
            )

            # Log attempt
            self._log_email_attempt(
                username=username,
                to_email=user.get('email'),
                subject=content["subject"],
                message=content["body"],
                status="success" if status else "failed",
                error=error
            )

            return status

        return True

    def send_achievement_notification(self, username: str, achievement: Dict) -> bool:
        """
        Send a notification for a new achievement.

        Args:
            username (str): Username to notify
            achievement (dict): Achievement details

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.user_manager:
            logger.error("User manager not available. Cannot send achievement notification.")
            return False

        # Check if user exists
        if username in self.user_manager.users:
            user = self.user_manager.users[username]
        else:
            logger.error(f"User '{username}' not found.")
            return False

        # Get user settings
        user_settings = self.notification_settings.get(
            username,
            self.notification_settings.get("default", DEFAULT_NOTIFICATION_SETTINGS)
        )

        # Skip if achievement notifications are disabled
        if not user_settings.get("achievement_notifications", True):
            return False

        # Get user name
        name = user.get('name', username)

        # Generate content
        content = ContentGenerator.generate_achievement_content(
            username=username,
            name=name,
            achievement=achievement
        )

        if not content["subject"] or not content["body"]:
            logger.error(f"Failed to generate achievement notification content for user {username}")
            return False

        # Log in-app notification
        achievement_name = achievement.get("name", "New Achievement")
        self._log_app_notification(
            username=username,
            notification_type="achievement",
            message=f"Achievement unlocked: {achievement_name}"
        )

        # Send email if enabled and email is set
        if user_settings.get("email_notifications", False) and user.get('email'):
            status, error = EmailSender.send_email(
                to_email=user.get('email'),
                subject=content["subject"],
                message_body=content["body"]
            )

            # Log attempt
            self._log_email_attempt(
                username=username,
                to_email=user.get('email'),
                subject=content["subject"],
                message=content["body"],
                status="success" if status else "failed",
                error=error
            )

        return True

    def send_reminder(self, username: str) -> bool:
        """
        Send a reminder to users who haven't logged a trip recently.

        Args:
            username (str): Username to remind

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.user_manager:
            logger.error("User manager not available. Cannot send reminder.")
            return False

        # Check if user exists
        if username in self.user_manager.users:
            user = self.user_manager.users[username]
        else:
            logger.error(f"User '{username}' not found.")
            return False

        # Get user settings
        user_settings = self.notification_settings.get(
            username,
            self.notification_settings.get("default", DEFAULT_NOTIFICATION_SETTINGS)
        )

        # Skip if reminders are disabled
        if user_settings.get("reminder_frequency", "none") == "none":
            return False

        # Get user name
        name = user.get('name', username)

        # Find last trip date
        trips = user.get("trips", [])
        last_trip_date = None

        if trips:
            try:
                sorted_trips = sorted(
                    [trip for trip in trips if "date" in trip],
                    key=lambda x: x["date"],
                    reverse=True
                )

                if sorted_trips:
                    last_trip_date = sorted_trips[0]["date"]
            except (KeyError, TypeError) as e:
                logger.error(f"Error finding last trip date: {e}")

        # Generate content
        content = ContentGenerator.generate_reminder_content(
            username=username,
            name=name,
            last_trip_date=last_trip_date
        )

        if not content["subject"] or not content["body"]:
            logger.error(f"Failed to generate reminder content for user {username}")
            return False

        # Log in-app notification
        self._log_app_notification(
            username=username,
            notification_type="reminder",
            message="Don't forget to log your cycling trips!"
        )

        # Send email if enabled and email is set
        if user_settings.get("email_notifications", False) and user.get('email'):
            status, error = EmailSender.send_email(
                to_email=user.get('email'),
                subject=content["subject"],
                message_body=content["body"]
            )

            # Log attempt
            self._log_email_attempt(
                username=username,
                to_email=user.get('email'),
                subject=content["subject"],
                message=content["body"],
                status="success" if status else "failed",
                error=error
            )

        # Send SMS if enabled and phone is set
        if user_settings.get("sms_notifications", False) and user.get('phone') and user.get('carrier'):
            sms_message = f"EcoCycle Reminder: Don't forget to log your cycling trips!"

            status, error = SmsSender.send_sms_via_email(
                to_phone=user.get('phone'),
                carrier=user.get('carrier'),
                message_body=sms_message
            )

            # Log attempt
            self._log_sms_attempt(
                username=username,
                to_phone=user.get('phone'),
                message=sms_message,
                status="success" if status else "failed",
                error=error
            )

        return True

    def send_daily_eco_tip(self, username: str) -> bool:
        """
        Send a daily eco tip to a user.

        Args:
            username (str): Username to send tip to

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.user_manager:
            logger.error("User manager not available. Cannot send eco tip.")
            return False

        # Check if user exists
        if username in self.user_manager.users:
            user = self.user_manager.users[username]
        else:
            logger.error(f"User '{username}' not found.")
            return False

        # Get user settings
        user_settings = self.notification_settings.get(
            username,
            self.notification_settings.get("default", DEFAULT_NOTIFICATION_SETTINGS)
        )

        # Skip if eco tips are disabled
        if not user_settings.get("eco_tips", True):
            return False

        # Get user name
        name = user.get('name', username)

        # Generate content
        content = ContentGenerator.generate_eco_tip_content(
            username=username,
            name=name
        )

        if not content["subject"] or not content["body"]:
            logger.error(f"Failed to generate eco tip content for user {username}")
            return False

        # Log in-app notification
        self._log_app_notification(
            username=username,
            notification_type="eco_tip",
            message=f"New eco tip available!"
        )

        # Send email if enabled and email is set
        if user_settings.get("email_notifications", False) and user.get('email'):
            status, error = EmailSender.send_email(
                to_email=user.get('email'),
                subject=content["subject"],
                message_body=content["body"]
            )

            # Log attempt
            self._log_email_attempt(
                username=username,
                to_email=user.get('email'),
                subject=content["subject"],
                message=content["body"],
                status="success" if status else "failed",
                error=error
            )

        return True

    def process_scheduled_notifications(self) -> int:
        """
        Process all scheduled notifications for all users.

        Returns:
            int: Number of notifications sent
        """
        if not self.user_manager:
            return 0

        sent_count = 0
        today = datetime.date.today()

        # Process for each user
        for username, user in self.user_manager.users.items():
            # Skip guest user
            if user.get('is_guest', False):
                continue

            # Check if user has notification settings
            if username not in self.notification_settings:
                # Copy default settings for this user
                self.notification_settings[username] = self.notification_settings["default"].copy()
                NotificationStorage.save_notification_settings(self.notification_settings)

            # Daily eco tip (if enabled)
            if self.notification_settings[username]['eco_tips']:
                if self.send_daily_eco_tip(username):
                    sent_count += 1

            # Weekly summary (if it's Sunday and enabled)
            if today.weekday() == 6 and self.notification_settings[username]['weekly_summary']:
                if self.generate_weekly_summary(username):
                    sent_count += 1

            # Reminders based on frequency
            if self.notification_settings[username]['reminder_frequency'] != 'none':
                reminder_frequency = self.notification_settings[username]['reminder_frequency']

                # Daily reminders
                if reminder_frequency == 'daily':
                    if self.send_reminder(username):
                        sent_count += 1

                # Weekly reminders (on Mondays)
                elif reminder_frequency == 'weekly' and today.weekday() == 0:
                    if self.send_reminder(username):
                        sent_count += 1

                # Monthly reminders (on 1st of the month)
                elif reminder_frequency == 'monthly' and today.day == 1:
                    if self.send_reminder(username):
                        sent_count += 1

        return sent_count


def run_notification_manager(user_manager=None, sheets_manager=None):
    """
    Run the notification manager as a standalone module.

    Args:
        user_manager: User manager instance
        sheets_manager: Sheets manager instance
    """
    notification_manager = NotificationManager(user_manager, sheets_manager)
    notification_manager.run_notification_manager()
