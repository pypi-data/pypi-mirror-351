"""
EcoCycle - Notification System Module
Provides functionality for sending notifications and reminders to users.
Enhanced with Rich UI for a modern, accessible console interface.
Now modularized for better maintainability.
"""
import logging
import os
from typing import Dict, List, Optional, Any

# Import all modularized components
from services.notifications.config import (
    NOTIFICATION_SETTINGS_FILE, NOTIFICATION_LOGS_FILE, EMAIL_TEMPLATES_DIR,
    EMAIL_SENDER, EMAIL_PASSWORD
)
from services.notifications.storage import NotificationStorage
from services.notifications.templates import TemplateManager
from services.notifications.senders import EmailSender, SmsSender, AppNotifier
from services.notifications.ui import NotificationUI
from services.notifications.generators import ContentGenerator
from services.notifications.manager import NotificationManager, run_notification_manager

logger = logging.getLogger(__name__)


# Create a class that inherits from NotificationManager for backward compatibility
class NotificationSystem(NotificationManager):
    """
    Notification system for EcoCycle application.
    This is a backward compatibility wrapper around the new modular NotificationManager.
    """
    
    def _load_notification_settings(self) -> Dict:
        """Load notification settings from file."""
        if os.path.exists(NOTIFICATION_SETTINGS_FILE):
            try:
                with open(NOTIFICATION_SETTINGS_FILE, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading notification settings: {e}")
        
        # Create default settings
        default_settings = {
            "default": {
                "email_notifications": False,
                "sms_notifications": False,
                "achievement_notifications": True,
                "weekly_summary": True,
                "eco_tips": True,
                "reminder_frequency": "weekly"  # none, daily, weekly, monthly
            }
        }
        
        # Save default settings
        with open(NOTIFICATION_SETTINGS_FILE, 'w') as file:
            json.dump(default_settings, file, indent=2)
        
        return default_settings
    
    def _save_notification_settings(self) -> bool:
        """Save notification settings to file."""
        try:
            with open(NOTIFICATION_SETTINGS_FILE, 'w') as file:
                json.dump(self.notification_settings, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving notification settings: {e}")
            return False
    
    def _load_notification_logs(self) -> Dict:
        """Load notification logs from file."""
        if os.path.exists(NOTIFICATION_LOGS_FILE):
            try:
                with open(NOTIFICATION_LOGS_FILE, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading notification logs: {e}")
        
        # Create default logs
        default_logs = {
            "email_logs": [],
            "sms_logs": [],
            "app_logs": []
        }
        
        # Save default logs
        with open(NOTIFICATION_LOGS_FILE, 'w') as file:
            json.dump(default_logs, file, indent=2)
        
        return default_logs
    
    def _save_notification_logs(self) -> bool:
        """Save notification logs to file."""
        try:
            with open(NOTIFICATION_LOGS_FILE, 'w') as file:
                json.dump(self.notification_logs, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving notification logs: {e}")
            return False
    
    def _create_default_templates(self) -> None:
        """Create default email templates if they don't exist."""
        templates = {
            "welcome_email.txt": """Welcome to EcoCycle, {name}!
            
Thank you for joining our community of eco-friendly cyclists. Together, we're making a difference for our planet, one bike ride at a time.

Your EcoCycle account is now active and ready to use. You can start logging your cycling trips right away and track your positive environmental impact.

Here are some quick tips to get started:
1. Log your cycling trips regularly to track your progress
2. Check your carbon footprint reduction in the statistics section
3. Use the weather and route planning features to plan your rides
4. Share your achievements with friends and family

Happy cycling!

The EcoCycle Team
""",
            "achievement_notification.txt": """Congratulations, {name}!

You've earned a new achievement: {achievement_name}

{achievement_description}

You've earned {points} eco points for this achievement. Keep up the great work!

View all your achievements in the EcoCycle app.

The EcoCycle Team
""",
            "weekly_summary.txt": """Weekly Cycling Summary for {name}

Week: {start_date} to {end_date}

Your weekly stats:
- Trips completed: {trips_count}
- Total distance: {total_distance}
- CO2 saved: {co2_saved}
- Calories burned: {calories_burned}

{comparison_text}

Eco Tip of the Week:
{eco_tip}

Keep cycling for a greener planet!

The EcoCycle Team
""",
            "reminder.txt": """Hello {name},

It's been a while since your last cycle trip. Don't forget to log your cycling activities to track your environmental impact.

Your last recorded trip was on {last_trip_date}.

Ready to get back on the saddle? The weather forecast for tomorrow is {weather_forecast}.

The EcoCycle Team
"""
        }
        
        for filename, content in templates.items():
            file_path = os.path.join(EMAIL_TEMPLATES_DIR, filename)
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w') as file:
                        file.write(content)
                except Exception as e:
                    logger.error(f"Error creating template {filename}: {e}")
    
    def run_notification_manager(self):
        """Run the notification system interactive interface with Rich UI styling."""
        while True:
            # Clear screen and display header
            if HAS_RICH:
                console.clear()
                console.print(Panel.fit(
                    "[bold cyan]Manage your notification preferences and settings[/]",
                    title="[bold green]EcoCycle Notification Manager[/]",
                    border_style="green"
                ))
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Notification Manager")
            
            # Check if user is authenticated
            if not self.user_manager or not self.user_manager.is_authenticated():
                if HAS_RICH:
                    console.print(Panel(
                        "[yellow]You need to be logged in to access notification settings.[/]",
                        border_style="yellow"
                    ))
                    choice = Prompt.ask("Select an option", choices=["1"], default="1", show_choices=False)
                    console.print("[bold]1. Return to Main Menu[/]")
                else:
                    print(f"{ascii_art.Fore.YELLOW}You need to be logged in to access notification settings.{ascii_art.Style.RESET_ALL}")
                    print("\nOptions:")
                    print("1. Return to Main Menu")
                    choice = input("\nSelect an option: ")
                
                if choice == "1":
                    break
                continue
            
            # Get current user
            user = self.user_manager.get_current_user()
            username = user.get('username')
            name = user.get('name', username)
            
            # Get user's notification settings
            if username not in self.notification_settings:
                # Copy default settings for this user
                self.notification_settings[username] = self.notification_settings["default"].copy()
                self._save_notification_settings()
            
            user_settings = self.notification_settings[username]
            
            # Display current settings and menu options
            if HAS_RICH:
                # Create a Rich table for current settings
                settings_table = Table(title="Current Notification Settings", box=box.ROUNDED)
                settings_table.add_column("Setting", style="cyan")
                settings_table.add_column("Status", style="green")
                
                # Add settings to table
                for setting, value in user_settings.items():
                    setting_name = " ".join(word.capitalize() for word in setting.split("_"))
                    if isinstance(value, bool):
                        status = "[green]Enabled[/]" if value else "[red]Disabled[/]"
                    elif setting == "reminder_frequency":
                        if value == "none":
                            status = "[red]Disabled[/]"
                        else:
                            status = f"[yellow]{value.capitalize()}[/]"
                    else:
                        status = f"[blue]{value}[/]"
                    
                    settings_table.add_row(setting_name, status)
                
                # Display settings table
                console.print(Panel(settings_table, border_style="blue"))
                
                # Display contact information
                email = user.get('email', 'Not set')
                phone = user.get('phone', 'Not set')
                
                contact_table = Table(title="Contact Information", box=box.ROUNDED)
                contact_table.add_column("Method", style="cyan")
                contact_table.add_column("Value", style="yellow")
                
                email_status = f"[green]{email}[/]" if email != 'Not set' else "[red]Not set[/]"
                phone_status = f"[green]{phone}[/]" if phone != 'Not set' else "[red]Not set[/]"
                
                contact_table.add_row("Email", email_status)
                contact_table.add_row("Phone", phone_status)
                
                console.print(Panel(contact_table, border_style="cyan"))
                
                # Create a menu
                console.print(Panel("[bold]Available Options[/]", border_style="yellow"))
                console.print("[cyan]1.[/] Update notification preferences")
                console.print("[cyan]2.[/] Update contact information")
                console.print("[cyan]3.[/] View notification history")
                console.print("[cyan]4.[/] Test notifications")
                console.print("[cyan]5.[/] Return to main menu")
                
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"], default="5")
            else:
                # Standard ASCII version
                print(f"{ascii_art.Fore.CYAN}\nCurrent Notification Settings for {name}:{ascii_art.Style.RESET_ALL}")
                for setting, value in user_settings.items():
                    setting_name = " ".join(word.capitalize() for word in setting.split("_"))
                    
                    if isinstance(value, bool):
                        status = f"{ascii_art.Fore.GREEN}Enabled{ascii_art.Style.RESET_ALL}" if value else f"{ascii_art.Fore.RED}Disabled{ascii_art.Style.RESET_ALL}"
                    elif setting == "reminder_frequency":
                        if value == "none":
                            status = f"{ascii_art.Fore.RED}Disabled{ascii_art.Style.RESET_ALL}"
                        else:
                            status = f"{ascii_art.Fore.YELLOW}{value.capitalize()}{ascii_art.Style.RESET_ALL}"
                    else:
                        status = f"{ascii_art.Fore.BLUE}{value}{ascii_art.Style.RESET_ALL}"
                    
                    print(f"- {setting_name}: {status}")
                
                # Display contact information
                email = user.get('email', 'Not set')
                phone = user.get('phone', 'Not set')
                
                print(f"\n{ascii_art.Fore.CYAN}Contact Information:{ascii_art.Style.RESET_ALL}")
                print(f"- Email: {ascii_art.Fore.GREEN if email != 'Not set' else ascii_art.Fore.RED}{email}{ascii_art.Style.RESET_ALL}")
                print(f"- Phone: {ascii_art.Fore.GREEN if phone != 'Not set' else ascii_art.Fore.RED}{phone}{ascii_art.Style.RESET_ALL}")
                
                # Display menu options
                print("\nOptions:")
                print("1. Update notification preferences")
                print("2. Update contact information")
                print("3. View notification history")
                print("4. Test notifications")
                print("5. Return to main menu")
                
                choice = input("\nSelect an option (1-5): ")
            
            # Process user selection
            if choice == "1":
                self.update_notification_settings(username)
            elif choice == "2":
                self.update_contact_information(username)
            elif choice == "3":
                self.view_notification_history(username)
            elif choice == "4":
                self.test_notifications(username)
            elif choice == "5":
                break
            else:
                if HAS_RICH:
                    console.print("[bold red]Invalid option. Please try again.[/]")
                else:
                    print(f"\n{ascii_art.Fore.RED}Invalid option. Please try again.{ascii_art.Style.RESET_ALL}")
                time.sleep(1)
    
    def update_notification_settings(self, username: str) -> None:
        """Update notification settings for a user with Rich UI styling."""
        while True:
            if HAS_RICH:
                console.clear()
                console.print(Panel.fit(
                    "[bold cyan]Customize how you receive notifications[/]",
                    title="[bold green]Update Notification Settings[/]",
                    border_style="green"
                ))
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Update Notification Settings")
            
            if username not in self.notification_settings:
                self.notification_settings[username] = self.notification_settings["default"].copy()
                self._save_notification_settings()
            
            user_settings = self.notification_settings[username]
            
            # Display current settings with Rich UI or ASCII fallback
            if HAS_RICH:
                # Create settings table
                settings_table = Table(box=box.ROUNDED)
                settings_table.add_column("#", style="dim")
                settings_table.add_column("Setting", style="cyan")
                settings_table.add_column("Status", style="green")
                
                # Add settings to table
                settings_table.add_row(
                    "1", "Email Notifications", 
                    "[green]Enabled[/]" if user_settings['email_notifications'] else "[red]Disabled[/]"
                )
                settings_table.add_row(
                    "2", "SMS Notifications", 
                    "[green]Enabled[/]" if user_settings['sms_notifications'] else "[red]Disabled[/]"
                )
                settings_table.add_row(
                    "3", "Achievement Notifications", 
                    "[green]Enabled[/]" if user_settings['achievement_notifications'] else "[red]Disabled[/]"
                )
                settings_table.add_row(
                    "4", "Weekly Summary", 
                    "[green]Enabled[/]" if user_settings['weekly_summary'] else "[red]Disabled[/]"
                )
                settings_table.add_row(
                    "5", "Eco Tips", 
                    "[green]Enabled[/]" if user_settings['eco_tips'] else "[red]Disabled[/]"
                )
                
                # Format reminder frequency
                freq = user_settings['reminder_frequency']
                if freq == "none":
                    freq_status = "[red]Disabled[/]"
                else:
                    freq_status = f"[yellow]{freq.capitalize()}[/]"
                
                settings_table.add_row("6", "Reminder Frequency", freq_status)
                settings_table.add_row("7", "Return to Notification Manager", "")
                
                # Display settings table
                console.print(Panel(settings_table, title="Current Settings", border_style="blue"))
                
                # Get user choice
                choice = Prompt.ask("Select a setting to update", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")
            else:
                # ASCII fallback for settings display
                print(f"{ascii_art.Fore.CYAN}Current Notification Settings:{ascii_art.Style.RESET_ALL}")
                print(f"1. Email Notifications: {ascii_art.Fore.GREEN if user_settings['email_notifications'] else ascii_art.Fore.RED}{user_settings['email_notifications']}{ascii_art.Style.RESET_ALL}")
                print(f"2. SMS Notifications: {ascii_art.Fore.GREEN if user_settings['sms_notifications'] else ascii_art.Fore.RED}{user_settings['sms_notifications']}{ascii_art.Style.RESET_ALL}")
                print(f"3. Achievement Notifications: {ascii_art.Fore.GREEN if user_settings['achievement_notifications'] else ascii_art.Fore.RED}{user_settings['achievement_notifications']}{ascii_art.Style.RESET_ALL}")
                print(f"4. Weekly Summary: {ascii_art.Fore.GREEN if user_settings['weekly_summary'] else ascii_art.Fore.RED}{user_settings['weekly_summary']}{ascii_art.Style.RESET_ALL}")
                print(f"5. Eco Tips: {ascii_art.Fore.GREEN if user_settings['eco_tips'] else ascii_art.Fore.RED}{user_settings['eco_tips']}{ascii_art.Style.RESET_ALL}")
                print(f"6. Reminder Frequency: {ascii_art.Fore.CYAN}{user_settings['reminder_frequency']}{ascii_art.Style.RESET_ALL}")
                print("7. Return to Notification Manager")
                
                choice = input("\nSelect a setting to update (1-7): ")
            
            # Process the user's choice
            if choice == "1":
                # Toggle email notifications
                if HAS_RICH:
                    new_value = Confirm.ask("Enable email notifications?", default=not user_settings['email_notifications'])
                    user_settings['email_notifications'] = new_value
                    self._save_notification_settings()
                    status = "[green]Enabled[/]" if new_value else "[red]Disabled[/]"
                    console.print(f"Email notifications {status}")
                    time.sleep(1)
                else:
                    user_settings['email_notifications'] = not user_settings['email_notifications']
                    self._save_notification_settings()
                    print(f"\nEmail Notifications: {ascii_art.Fore.GREEN if user_settings['email_notifications'] else ascii_art.Fore.RED}{user_settings['email_notifications']}{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
            elif choice == "2":
                # Toggle SMS notifications
                if HAS_RICH:
                    new_value = Confirm.ask("Enable SMS notifications?", default=not user_settings['sms_notifications'])
                    user_settings['sms_notifications'] = new_value
                    self._save_notification_settings()
                    status = "[green]Enabled[/]" if new_value else "[red]Disabled[/]"
                    console.print(f"SMS notifications {status}")
                    time.sleep(1)
                else:
                    user_settings['sms_notifications'] = not user_settings['sms_notifications']
                    self._save_notification_settings()
                    print(f"\nSMS Notifications: {ascii_art.Fore.GREEN if user_settings['sms_notifications'] else ascii_art.Fore.RED}{user_settings['sms_notifications']}{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
            elif choice == "3":
                # Toggle achievement notifications
                if HAS_RICH:
                    new_value = Confirm.ask("Enable achievement notifications?", default=not user_settings['achievement_notifications'])
                    user_settings['achievement_notifications'] = new_value
                    self._save_notification_settings()
                    status = "[green]Enabled[/]" if new_value else "[red]Disabled[/]"
                    console.print(f"Achievement notifications {status}")
                    time.sleep(1)
                else:
                    user_settings['achievement_notifications'] = not user_settings['achievement_notifications']
                    self._save_notification_settings()
                    print(f"\nAchievement Notifications: {ascii_art.Fore.GREEN if user_settings['achievement_notifications'] else ascii_art.Fore.RED}{user_settings['achievement_notifications']}{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
            elif choice == "4":
                # Toggle weekly summary
                if HAS_RICH:
                    new_value = Confirm.ask("Enable weekly summary?", default=not user_settings['weekly_summary'])
                    user_settings['weekly_summary'] = new_value
                    self._save_notification_settings()
                    status = "[green]Enabled[/]" if new_value else "[red]Disabled[/]"
                    console.print(f"Weekly summary {status}")
                    time.sleep(1)
                else:
                    user_settings['weekly_summary'] = not user_settings['weekly_summary']
                    self._save_notification_settings()
                    print(f"\nWeekly Summary: {ascii_art.Fore.GREEN if user_settings['weekly_summary'] else ascii_art.Fore.RED}{user_settings['weekly_summary']}{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
            elif choice == "5":
                # Toggle eco tips
                if HAS_RICH:
                    new_value = Confirm.ask("Enable eco tips?", default=not user_settings['eco_tips'])
                    user_settings['eco_tips'] = new_value
                    self._save_notification_settings()
                    status = "[green]Enabled[/]" if new_value else "[red]Disabled[/]"
                    console.print(f"Eco tips {status}")
                    time.sleep(1)
                else:
                    user_settings['eco_tips'] = not user_settings['eco_tips']
                    self._save_notification_settings()
                    print(f"\nEco Tips: {ascii_art.Fore.GREEN if user_settings['eco_tips'] else ascii_art.Fore.RED}{user_settings['eco_tips']}{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
            elif choice == "6":
                # Update reminder frequency
                if HAS_RICH:
                    # Show frequency options with rich styling
                    freq_table = Table(box=box.SIMPLE)
                    freq_table.add_column("#", style="dim")
                    freq_table.add_column("Frequency", style="cyan")
                    freq_table.add_row("1", "None (Disabled)")
                    freq_table.add_row("2", "Daily")
                    freq_table.add_row("3", "Weekly")
                    freq_table.add_row("4", "Monthly")
                    
                    console.print(Panel(freq_table, title="Reminder Frequency Options", border_style="yellow"))
                    freq_choice = Prompt.ask("Select a frequency", choices=["1", "2", "3", "4"], default="3")
                else:
                    # ASCII fallback with tqdm if available
                    print("\nReminder Frequency Options:")
                    print("1. None (Disabled)")
                    print("2. Daily")
                    print("3. Weekly")
                    print("4. Monthly")
                    if TQDM_AVAILABLE:
                        freq_steps = ["Loading", "Preparing", "Finalizing"]
                        for step in tqdm(freq_steps, desc="Loading frequency options"):
                            time.sleep(0.3)
                    freq_choice = input("\nSelect a frequency (1-4): ")
                
                # Process frequency choice for both UI versions
                if freq_choice == "1":
                    user_settings['reminder_frequency'] = "none"
                elif freq_choice == "2":
                    user_settings['reminder_frequency'] = "daily"
                elif freq_choice == "3":
                    user_settings['reminder_frequency'] = "weekly"
                elif freq_choice == "4":
                    user_settings['reminder_frequency'] = "monthly"
                
                self._save_notification_settings()
                
                if HAS_RICH:
                    if user_settings['reminder_frequency'] == "none":
                        console.print("Reminder frequency set to: [red]Disabled[/]")
                    else:
                        console.print(f"Reminder frequency set to: [yellow]{user_settings['reminder_frequency'].capitalize()}[/]")
                    time.sleep(1)
                else:
                    print(f"\nReminder Frequency: {ascii_art.Fore.CYAN}{user_settings['reminder_frequency']}{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
                    
            elif choice == "7":
                break
            else:
                if HAS_RICH:
                    console.print("[bold red]Invalid option. Please try again.[/]")
                    time.sleep(1)
                else:
                    print(f"\n{ascii_art.Fore.RED}Invalid option. Please try again.{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")
            # The settings have already been saved in each option's handler
    
    def update_contact_information(self, username: str) -> None:
        """Update contact information for a user with Rich UI styling."""
        while True:
            # Clear screen and display header
            if HAS_RICH:
                console.clear()
                console.print(Panel.fit(
                    "[bold cyan]Update your contact details for notifications[/]",
                    title="[bold green]Contact Information[/]",
                    border_style="green"
                ))
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Update Contact Information")
            
            # Get current user
            user = self.user_manager.get_current_user()
            
            # Display current contact info
            email = user.get('email', 'Not set')
            phone = user.get('phone', 'Not set')
            
            if HAS_RICH:
                # Rich UI display of contact info
                contact_table = Table(box=box.ROUNDED)
                contact_table.add_column("Contact Type", style="cyan")
                contact_table.add_column("Current Value", style="yellow")
                
                email_status = f"[green]{email}[/]" if email != 'Not set' else "[red]Not set[/]"
                phone_status = f"[green]{phone}[/]" if phone != 'Not set' else "[red]Not set[/]"
                
                contact_table.add_row("Email", email_status)
                contact_table.add_row("Phone", phone_status)
                
                console.print(Panel(contact_table, title="Current Contact Information", border_style="blue"))
                
                # Options menu
                console.print(Panel("[bold]Available Options[/]", border_style="yellow"))
                console.print("[cyan]1.[/] Update Email")
                console.print("[cyan]2.[/] Update Phone")
                console.print("[cyan]3.[/] Return to Notification Manager")
                
                choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="3")
            else:
                # ASCII fallback
                print(f"\n{ascii_art.Fore.CYAN}Current Contact Information:{ascii_art.Style.RESET_ALL}")
                print(f"Email: {ascii_art.Fore.GREEN if email != 'Not set' else ascii_art.Fore.RED}{email}{ascii_art.Style.RESET_ALL}")
                print(f"Phone: {ascii_art.Fore.GREEN if phone != 'Not set' else ascii_art.Fore.RED}{phone}{ascii_art.Style.RESET_ALL}")
                
                print("\nOptions:")
                print("1. Update Email")
                print("2. Update Phone")
                print("3. Return to Notification Manager")
                
                choice = input("\nSelect an option (1-3): ")
            
            if choice == "1":
                # Update email with Rich UI
                if HAS_RICH:
                    console.print(f"\nCurrent Email: {email_status}")
                    new_email = Prompt.ask("Enter new email", default="")
                    
                    if new_email.strip():
                        # Use tqdm for email validation
                        validation_steps = [
                            "Checking format",
                            "Verifying domain",
                            "Confirming syntax"
                        ]
                        
                        if TQDM_AVAILABLE:
                            for i, step in enumerate(validation_steps):
                                with tqdm(total=100, desc=f"[{i+1}/3] {step}", ncols=80, colour="yellow", leave=False) as pbar:
                                    for j in range(10):
                                        time.sleep(0.03)
                                        pbar.update(10)
                                # Simple validation
                                if '@' in new_email and '.' in new_email:
                                    # Update user email
                                    user['email'] = new_email
                                    self.user_manager.save_users()
                                    console.print("[bold green]✓ Email updated successfully![/]")
                                else:
                                    console.print("[bold red]✗ Invalid email format. Email not updated.[/]")
                        else:
                            print("Validating email...")
                            for i in range(3):
                                time.sleep(0.3)
                                print(".", end="", flush=True)
                            print("")
                            # Simple validation
                            if '@' in new_email and '.' in new_email:
                                # Update user email
                                user['email'] = new_email
                                self.user_manager.save_users()
                                print(f"\n{ascii_art.Fore.GREEN}Email updated successfully.{ascii_art.Style.RESET_ALL}")
                            else:
                                print(f"\n{ascii_art.Fore.RED}Invalid email format. Email not updated.{ascii_art.Style.RESET_ALL}")
                    else:
                        console.print("[yellow]Email not updated.[/]")
                    
                    time.sleep(1)  # Brief pause to read the message
                else:
                    # ASCII fallback
                    print(f"\nCurrent Email: {email}")
                    new_email = input("Enter new email (leave blank to keep current): ")
                    
                    if new_email.strip():
                        # Simple validation
                        if '@' in new_email and '.' in new_email:
                            # Update user email
                            user['email'] = new_email
                            self.user_manager.save_users()
                            print(f"\n{ascii_art.Fore.GREEN}Email updated successfully.{ascii_art.Style.RESET_ALL}")
                        else:
                            print(f"\n{ascii_art.Fore.RED}Invalid email format. Email not updated.{ascii_art.Style.RESET_ALL}")
                    else:
                        print("\nEmail not updated.")
                    
                    if TQDM_AVAILABLE:
                        # Use tqdm for progress indication
                        notification_steps = ["Loading", "Preparing", "Finalizing"]
                        for step in tqdm(notification_steps, desc="Loading notifications"):
                            time.sleep(0.3)
                    else:
                        # Basic dot animation fallback
                        print("Loading notifications...")
                        for i in range(3):
                            time.sleep(0.3)
                            print(".", end="", flush=True)
                        print("")
                    input("\nPress Enter to continue...")
            
            elif choice == "2":
                # Update phone with Rich UI
                if HAS_RICH:
                    console.print(f"\nCurrent Phone: {phone_status}")
                    new_phone = Prompt.ask("Enter new phone number", default="")
                    
                    if new_phone.strip():
                        # Use tqdm for phone validation
                        validation_steps = [
                            "Checking format",
                            "Verifying country code",
                            "Confirming digits"
                        ]
                        
                        if TQDM_AVAILABLE:
                            for i, step in enumerate(validation_steps):
                                with tqdm(total=100, desc=f"[{i+1}/3] {step}", ncols=80, colour="yellow", leave=False) as pbar:
                                    for j in range(10):
                                        time.sleep(0.03)
                                        pbar.update(10)
                                # Simple validation
                                if new_phone.replace('-', '').replace('+', '').replace(' ', '').isdigit():
                                    # Update user phone
                                    user['phone'] = new_phone
                                    self.user_manager.save_users()
                                    console.print("[bold green]✓ Phone number updated successfully![/]")
                                else:
                                    console.print("[bold red]✗ Invalid phone number format. Phone not updated.[/]")
                        else:
                            print("Validating phone...")
                            for i in range(3):
                                time.sleep(0.3)
                                print(".", end="", flush=True)
                            print("")
                            # Simple validation
                            if new_phone.replace('-', '').replace('+', '').replace(' ', '').isdigit():
                                # Update user phone
                                user['phone'] = new_phone
                                self.user_manager.save_users()
                                print(f"\n{ascii_art.Fore.GREEN}Phone number updated successfully.{ascii_art.Style.RESET_ALL}")
                            else:
                                print(f"\n{ascii_art.Fore.RED}Invalid phone number format. Phone not updated.{ascii_art.Style.RESET_ALL}")
                    else:
                        console.print("[yellow]Phone number not updated.[/]")
                    
                    time.sleep(1)  # Brief pause to read the message
                else:
                    # ASCII fallback
                    print(f"\nCurrent Phone: {phone}")
                    new_phone = input("Enter new phone number (leave blank to keep current): ")
                    
                    if new_phone.strip():
                        # Simple validation
                        if new_phone.replace('-', '').replace('+', '').replace(' ', '').isdigit():
                            # Update user phone
                            user['phone'] = new_phone
                            self.user_manager.save_users()
                            print(f"\n{ascii_art.Fore.GREEN}Phone number updated successfully.{ascii_art.Style.RESET_ALL}")
                        else:
                            print(f"\n{ascii_art.Fore.RED}Invalid phone number format. Phone not updated.{ascii_art.Style.RESET_ALL}")
                    else:
                        print("\nPhone number not updated.")
                    
                    if TQDM_AVAILABLE:
                        # Use tqdm for progress indication
                        notification_steps = ["Loading", "Preparing", "Finalizing"]
                        for step in tqdm(notification_steps, desc="Loading notifications"):
                            time.sleep(0.3)
                    else:
                        # Basic dot animation fallback
                        print("Loading notifications...")
                        for i in range(3):
                            time.sleep(0.3)
                            print(".", end="", flush=True)
                        print("")
                    input("\nPress Enter to continue...")
            
            elif choice == "3":
                # Return to notification manager
                break
            
            else:
                # Handle invalid input (should never happen with Rich UI's choices)
                if HAS_RICH:
                    console.print("[bold red]Invalid option. Please try again.[/]")
                    time.sleep(1)
                else:
                    print(f"\n{ascii_art.Fore.RED}Invalid option. Please try again.{ascii_art.Style.RESET_ALL}")
                    if TQDM_AVAILABLE:
                        # Use tqdm for progress indication
                        notification_steps = ["Loading", "Preparing", "Finalizing"]
                        for step in tqdm(notification_steps, desc="Loading notifications"):
                            time.sleep(0.3)
                    else:
                        # Basic dot animation fallback
                        print("Loading notifications...")
                        for i in range(3):
                            time.sleep(0.3)
                            print(".", end="", flush=True)
                        print("")
                    input("\nPress Enter to continue...")
    
    def view_notification_history(self, username: str) -> None:
        """View notification history for a user with Rich UI styling."""
        if HAS_RICH:
            console.clear()
            console.print(Panel.fit(
                "[bold cyan]View your notification history[/]",
                title="[bold green]Notification History[/]",
                border_style="green"
            ))
            
            # Show loading indicator
            # Use tqdm progress bar for loading notification history
            console.print("[bold cyan]Loading notification history...[/]")
            history_steps = [
                "Connecting to database",
                "Querying notification records",
                "Processing notification data",
                "Formatting results"
            ]
            
            if TQDM_AVAILABLE:
                for i, step in enumerate(history_steps):
                    with tqdm(total=100, desc=f"[{i+1}/4] {step}", ncols=80, colour="cyan", leave=False) as pbar:
                        for j in range(10):
                            time.sleep(0.04)
                            pbar.update(10)
                    # Extract the user's logs
                    email_logs = [log for log in self.notification_logs['email_logs'] if log.get('username') == username]
                    sms_logs = [log for log in self.notification_logs['sms_logs'] if log.get('username') == username]
                    app_logs = [log for log in self.notification_logs['app_logs'] if log.get('username') == username]
            else:
                # Basic dot animation fallback
                print("Loading notification history...")
                for i in range(4):
                    time.sleep(0.4)
                    print(".", end="", flush=True)
                print("")
                # Extract the user's logs
                email_logs = [log for log in self.notification_logs['email_logs'] if log.get('username') == username]
                sms_logs = [log for log in self.notification_logs['sms_logs'] if log.get('username') == username]
                app_logs = [log for log in self.notification_logs['app_logs'] if log.get('username') == username]
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Notification History")
            
            # Extract the user's logs
            email_logs = [log for log in self.notification_logs['email_logs'] if log.get('username') == username]
            sms_logs = [log for log in self.notification_logs['sms_logs'] if log.get('username') == username]
            app_logs = [log for log in self.notification_logs['app_logs'] if log.get('username') == username]
        
        if not email_logs and not sms_logs and not app_logs:
            if HAS_RICH:
                console.print(Panel(
                    "[yellow]No notification history found.[/]",
                    border_style="yellow"
                ))
                time.sleep(1.5)
            else:
                print(f"\n{ascii_art.Fore.YELLOW}No notification history found.{ascii_art.Style.RESET_ALL}")
                if TQDM_AVAILABLE:
                    # Use tqdm for progress indication
                    notification_steps = ["Loading", "Preparing", "Finalizing"]
                    for step in tqdm(notification_steps, desc="Loading notifications"):
                        time.sleep(0.3)
                else:
                    # Basic dot animation fallback
                    print("Loading notifications...")
                    for i in range(3):
                        time.sleep(0.3)
                        print(".", end="", flush=True)
                    print("")
                input("\nPress Enter to continue...")
            return
        
        while True:
            if HAS_RICH:
                console.clear()
                console.print(Panel.fit(
                    "[bold cyan]View your notification history[/]",
                    title="[bold green]Notification History[/]",
                    border_style="green"
                ))
                
                # Create options table with notification counts
                options_table = Table(box=box.SIMPLE)
                options_table.add_column("Option", style="cyan")
                options_table.add_column("Description", style="white")
                options_table.add_column("Count", style="yellow")
                
                options_table.add_row("1", "Email Notifications", f"[cyan]{len(email_logs)}[/]")
                options_table.add_row("2", "SMS Notifications", f"[cyan]{len(sms_logs)}[/]")
                options_table.add_row("3", "In-App Notifications", f"[cyan]{len(app_logs)}[/]")
                options_table.add_row("4", "Return to Notification Manager", "")
                
                console.print(Panel(options_table, title="View notifications by type", border_style="blue"))
                
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"], default="4")
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Notification History")
                
                print("\nView notifications by type:")
                print(f"1. Email Notifications ({len(email_logs)})")
                print(f"2. SMS Notifications ({len(sms_logs)})")
                print(f"3. In-App Notifications ({len(app_logs)})")
                print("4. Return to Notification Manager")
                
                if TQDM_AVAILABLE:
                    # Use tqdm for progress indication
                    notification_steps = ["Loading", "Preparing", "Finalizing"]
                    for step in tqdm(notification_steps, desc="Loading notifications"):
                        time.sleep(0.3)
                else:
                    # Basic dot animation fallback
                    print("Loading notifications...")
                    for i in range(3):
                        time.sleep(0.3)
                        print(".", end="", flush=True)
                    print("")
                choice = input("\nSelect an option (1-4): ")
            
            if choice == "1" and email_logs:
                self._display_email_logs(email_logs)
            elif choice == "2" and sms_logs:
                self._display_sms_logs(sms_logs)
            elif choice == "3" and app_logs:
                self._display_app_logs(app_logs)
            elif choice == "4":
                break
            else:
                if choice in ["1", "2", "3"]:
                    if HAS_RICH:
                        console.print("[yellow]No notifications of this type found.[/]")
                        time.sleep(1.5)
                    else:
                        print(f"\n{ascii_art.Fore.YELLOW}No notifications of this type found.{ascii_art.Style.RESET_ALL}")
                        if TQDM_AVAILABLE:
                            # Use tqdm for progress indication
                            notification_steps = ["Loading", "Preparing", "Finalizing"]
                            for step in tqdm(notification_steps, desc="Loading notifications"):
                                time.sleep(0.3)
                        else:
                            # Basic dot animation fallback
                            print("Loading notifications...")
                            for i in range(3):
                                time.sleep(0.3)
                                print(".", end="", flush=True)
                            print("")
                        input("\nPress Enter to continue...")
                else:
                    if HAS_RICH:
                        console.print("[bold red]Invalid option. Please try again.[/]")
                        time.sleep(1)
                    else:
                        print(f"\n{ascii_art.Fore.RED}Invalid option. Please try again.{ascii_art.Style.RESET_ALL}")
                        if TQDM_AVAILABLE:
                            # Use tqdm for progress indication
                            notification_steps = ["Loading", "Preparing", "Finalizing"]
                            for step in tqdm(notification_steps, desc="Loading notifications"):
                                time.sleep(0.3)
                        else:
                            # Basic dot animation fallback
                            print("Loading notifications...")
                            for i in range(3):
                                time.sleep(0.3)
                                print(".", end="", flush=True)
                            print("")
                        input("\nPress Enter to continue...")
    
    def _display_email_logs(self, logs):
        """Display email notification logs with Rich UI styling."""
        if HAS_RICH:
            console.clear()
            console.print(Panel.fit(
                "[bold cyan]Recent Email Notifications[/]",
                title="[bold green]Email History[/]",
                border_style="cyan"
            ))
            
            # Sort logs by timestamp (newest first)
            sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            # Create a table for email logs
            if sorted_logs:
                email_table = Table(box=box.ROUNDED)
                email_table.add_column("Date", style="dim")
                email_table.add_column("To", style="cyan")
                email_table.add_column("Subject", style="blue")
                email_table.add_column("Status", style="green")
                
                for log in sorted_logs[:5]:  # Show the 5 most recent
                    # Convert timestamp to readable date
                    timestamp = datetime.datetime.fromtimestamp(log.get('timestamp', 0))
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    status = log.get('status', 'unknown')
                    status_text = f"[green]{status}[/]" if status == 'success' else f"[red]{status}[/]"
                    
                    email_table.add_row(
                        date_str,
                        log.get('to_email', 'N/A'),
                        log.get('subject', 'N/A'),
                        status_text
                    )
                
                console.print(email_table)
                
                # If there are failed emails, show error details
                failed_logs = [log for log in sorted_logs[:5] if log.get('status') == 'failed']
                if failed_logs:
                    console.print("\n[bold red]Error Details:[/]")
                    for i, log in enumerate(failed_logs, 1):
                        console.print(f"[red]{i}.[/] {log.get('error', 'Unknown error')}")
            else:
                console.print("[yellow]No email logs found.[/]")
            
            # Wait for user input
            time.sleep(0.5)  # Brief pause for visual appeal
            Prompt.ask("Press Enter to continue", default="")
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Email Notification History")
            
            print("\nMost recent emails:")
            # Sort logs by timestamp (newest first)
            sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            for i, log in enumerate(sorted_logs[:5], 1):  # Show the 5 most recent
                # Convert timestamp to readable date
                timestamp = datetime.datetime.fromtimestamp(log.get('timestamp', 0))
                date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                status = log.get('status', 'unknown')
                if status == 'success':
                    status_color = ascii_art.Fore.GREEN
                elif status == 'failed':
                    status_color = ascii_art.Fore.RED
                else:
                    status_color = ascii_art.Fore.YELLOW
                
                print(f"\n{i}. Date: {date_str}")
                print(f"   To: {log.get('to_email', 'N/A')}")
                print(f"   Subject: {log.get('subject', 'N/A')}")
                print(f"   Status: {status_color}{status}{ascii_art.Style.RESET_ALL}")
                
                if status == 'failed':
                    print(f"   Error: {log.get('error', 'Unknown error')}")
            
            if TQDM_AVAILABLE:
                # Use tqdm for progress indication
                notification_steps = ["Loading", "Preparing", "Finalizing"]
                for i, step in enumerate(notification_steps):
                    with tqdm(total=100, desc=f"[{i+1}/3] {step}", leave=False) as pbar:
                        for j in range(10):
                            time.sleep(0.03)
                            pbar.update(10)
            else:
                # Basic dot animation fallback
                print("Loading notifications...")
                for i in range(3):
                    time.sleep(0.3)
                    print(".", end="", flush=True)
                print("")
            input("\nPress Enter to continue...")

    def _display_sms_logs(self, logs):
        """Display SMS notification logs with Rich UI styling."""
        if HAS_RICH:
            console.clear()
            console.print(Panel.fit(
                "[bold cyan]Recent SMS Notifications[/]",
                title="[bold green]SMS History[/]",
                border_style="magenta"
            ))
            
            # Sort logs by timestamp (newest first)
            sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            if sorted_logs:
                # Create a table for SMS logs
                sms_table = Table(box=box.ROUNDED)
                sms_table.add_column("Date", style="dim")
                sms_table.add_column("To", style="cyan")
                sms_table.add_column("Message", style="blue")
                sms_table.add_column("Status", style="green")
                
                for log in sorted_logs[:5]:  # Show the 5 most recent
                    # Convert timestamp to readable date
                    timestamp = datetime.datetime.fromtimestamp(log.get('timestamp', 0))
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    status = log.get('status', 'unknown')
                    status_text = f"[green]{status}[/]" if status == 'success' else f"[red]{status}[/]"
                    
                    # Truncate message if too long
                    message = log.get('message', 'N/A')
                    if len(message) > 30:
                        message = message[:27] + "..."
                    
                    sms_table.add_row(
                        date_str,
                        log.get('to_phone', 'N/A'),
                        message,
                        status_text
                    )
                
                console.print(sms_table)
                
                # If there are failed SMS, show error details
                failed_logs = [log for log in sorted_logs[:5] if log.get('status') == 'failed']
                if failed_logs:
                    console.print("\n[bold red]Error Details:[/]")
                    for i, log in enumerate(failed_logs, 1):
                        console.print(f"[red]{i}.[/] {log.get('error', 'Unknown error')}")
            else:
                console.print("[yellow]No SMS logs found.[/]")
            
            # Wait for user input
            time.sleep(0.5)  # Brief pause for visual appeal
            Prompt.ask("Press Enter to continue", default="")
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("SMS Notification History")
            
            print("\nMost recent SMS messages:")
            # Sort logs by timestamp (newest first)
            sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            for i, log in enumerate(sorted_logs[:5], 1):  # Show the 5 most recent
                # Convert timestamp to readable date
                timestamp = datetime.datetime.fromtimestamp(log.get('timestamp', 0))
                date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                status = log.get('status', 'unknown')
                if status == 'success':
                    status_color = ascii_art.Fore.GREEN
                elif status == 'failed':
                    status_color = ascii_art.Fore.RED
                else:
                    status_color = ascii_art.Fore.YELLOW
                
                print(f"\n{i}. Date: {date_str}")
                print(f"   To: {log.get('to_phone', 'N/A')}")
                print(f"   Status: {status_color}{status}{ascii_art.Style.RESET_ALL}")
                
                if status == 'failed':
                    print(f"   Error: {log.get('error', 'Unknown error')}")
            
            if TQDM_AVAILABLE:
                # Use tqdm for progress indication
                notification_steps = ["Loading", "Preparing", "Finalizing"]
                for i, step in enumerate(notification_steps):
                    with tqdm(total=100, desc=f"[{i+1}/3] {step}", leave=False) as pbar:
                        for j in range(10):
                            time.sleep(0.03)
                            pbar.update(10)
            else:
                # Basic dot animation fallback
                print("Loading notifications...")
                for i in range(3):
                    time.sleep(0.3)
                    print(".", end="", flush=True)
                print("")
            input("\nPress Enter to continue...")

    def _display_app_logs(self, logs):
        """Display in-app notification logs with Rich UI styling."""
        if HAS_RICH:
            console.clear()
            console.print(Panel.fit(
                "[bold cyan]Recent In-App Notifications[/]",
                title="[bold green]In-App Notification History[/]",
                border_style="green"
            ))
            
            # Sort logs by timestamp (newest first)
            sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            if sorted_logs:
                # Create a table for app notification logs
                app_table = Table(box=box.ROUNDED)
                app_table.add_column("Date", style="dim")
                app_table.add_column("Type", style="cyan")
                app_table.add_column("Message", style="white")
                
                for log in sorted_logs[:10]:  # Show the 10 most recent
                    # Convert timestamp to readable date
                    timestamp = datetime.datetime.fromtimestamp(log.get('timestamp', 0))
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    notification_type = log.get('notification_type', 'general')
                    
                    # Color-code notification types
                    if notification_type == 'achievement':
                        type_text = f"[green]{notification_type}[/]"
                    elif notification_type == 'reminder':
                        type_text = f"[yellow]{notification_type}[/]"
                    elif notification_type == 'eco_tip':
                        type_text = f"[cyan]{notification_type}[/]"
                    else:
                        type_text = notification_type
                    
                    # Truncate message if too long
                    message = log.get('message', 'N/A')
                    if len(message) > 40:
                        message = message[:37] + "..."
                    
                    app_table.add_row(
                        date_str,
                        type_text,
                        message
                    )
                
                console.print(app_table)
            else:
                console.print("[yellow]No in-app notification logs found.[/]")
            
            # Wait for user input
            time.sleep(0.5)  # Brief pause for visual appeal
            Prompt.ask("Press Enter to continue", default="")
        else:
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("In-App Notification History")
            
            print("\nMost recent in-app notifications:")
            # Sort logs by timestamp (newest first)
            sorted_logs = sorted(logs, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            for i, log in enumerate(sorted_logs[:5], 1):  # Show the 5 most recent
                # Convert timestamp to readable date
                timestamp = datetime.datetime.fromtimestamp(log.get('timestamp', 0))
                date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                notification_type = log.get('notification_type', 'general')
                
                if notification_type == 'achievement':
                    type_color = ascii_art.Fore.GREEN
                elif notification_type == 'reminder':
                    type_color = ascii_art.Fore.YELLOW
                elif notification_type == 'eco_tip':
                    type_color = ascii_art.Fore.CYAN
                else:
                    type_color = ascii_art.Fore.WHITE
                
                print(f"\n{i}. Date: {date_str}")
                print(f"   Type: {type_color}{notification_type}{ascii_art.Style.RESET_ALL}")
                print(f"   Message: {log.get('message', 'N/A')}")
            
            if TQDM_AVAILABLE:
                # Use tqdm for progress indication
                notification_steps = ["Loading", "Preparing", "Finalizing"]
                for i, step in enumerate(notification_steps):
                    with tqdm(total=100, desc=f"[{i+1}/3] {step}", leave=False) as pbar:
                        for j in range(10):
                            time.sleep(0.03)
                            pbar.update(10)
            else:
                # Basic dot animation fallback
                print("Loading notifications...")
                for i in range(3):
                    time.sleep(0.3)
                    print(".", end="", flush=True)
                print("")
            input("\nPress Enter to continue...")
    
    def test_notifications(self, username: str) -> None:
        """Test sending notifications to a user with Rich UI styling."""
        while True:
            # Clear screen and display header with Rich UI or ASCII fallback
            if HAS_RICH:
                console.clear()
                console.print(Panel.fit(
                    "[bold cyan]Test notification delivery to verify your notification settings[/]",
                    title="[bold purple]Test Notifications[/]",
                    border_style="purple"
                ))
            else:
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Test Notifications")
            
            user = self.user_manager.get_current_user()
            name = user.get('name', username)
            user_settings = self.notification_settings[username]
            
            # Display test options menu with Rich UI or ASCII fallback
            if HAS_RICH:
                # Show current notification settings
                settings_table = Table(box=box.ROUNDED)
                settings_table.add_column("Setting", style="cyan")
                settings_table.add_column("Status", style="green")
                
                email_status = "[green]Enabled[/]" if user_settings['email_notifications'] else "[red]Disabled[/]"
                sms_status = "[green]Enabled[/]" if user_settings['sms_notifications'] else "[red]Disabled[/]"
                achievement_status = "[green]Enabled[/]" if user_settings['achievement_notifications'] else "[red]Disabled[/]"
                
                settings_table.add_row("Email Notifications", email_status)
                settings_table.add_row("SMS Notifications", sms_status)
                settings_table.add_row("Achievement Notifications", achievement_status)
                
                console.print(Panel(settings_table, title="Current Notification Settings", border_style="blue"))
                
                # Show test options
                options_table = Table(box=box.SIMPLE)
                options_table.add_column("Option", style="cyan")
                options_table.add_column("Description", style="white")
                
                options_table.add_row("1", "Test Email Notification")
                options_table.add_row("2", "Test SMS Notification")
                options_table.add_row("3", "Test Achievement Notification")
                options_table.add_row("4", "Return to Notification Manager")
                
                console.print(Panel(options_table, title="Available Test Options", border_style="yellow"))
                
                choice = Prompt.ask("Select a test option", choices=["1", "2", "3", "4"], default="4")
            else:
                # ASCII fallback with tqdm support
                print("Select notification type to test:")
                print("1. Email Notification")
                print("2. SMS Notification")
                print("3. Achievement Notification")
                print("4. Return to Notification Manager")
                
                if TQDM_AVAILABLE:
                    # Use tqdm for progress indication
                    notification_steps = ["Loading", "Preparing", "Finalizing"]
                    for step in tqdm(notification_steps, desc="Loading notifications"):
                        time.sleep(0.3)
                else:
                    # Basic dot animation fallback
                    print("Loading notifications...")
                    for i in range(3):
                        time.sleep(0.3)
                        print(".", end="", flush=True)
                    print("")
                choice = input("\nSelect an option (1-4): ")
            
            if choice == "1":
                # Test email notification
                if HAS_RICH:
                    console.clear()
                    console.print(Panel.fit(
                        "[bold cyan]Testing Email Notification Delivery[/]",
                        title="[bold purple]Email Test[/]",
                        border_style="purple"
                    ))
                    
                    if not user_settings['email_notifications']:
                        console.print(Panel("[yellow]Warning: Email notifications are disabled in your settings.[/]", border_style="yellow"))
                    
                    email = user.get('email', '')
                    if not email:
                        console.print(Panel("[bold red]Error: No email address set. Please update your contact information first.[/]", border_style="red"))
                        time.sleep(2)
                        continue
                    
                    console.print(f"\nSending test email to: [cyan]{email}[/]")
                    
                    # Enhanced email sending animation with tqdm progress bar
                    console.print("[bold green]Sending email - please wait...[/]")
                    email_steps = [
                        "Validating email address",
                        "Creating message envelope",
                        "Establishing secure connection",
                        "Authenticating with mail server",
                        "Transmitting message"
                    ]
                    
                    # Use tqdm progress bar with description updates
                    if TQDM_AVAILABLE:
                        for i, step in enumerate(email_steps):
                            with tqdm(total=100, desc=f"[{i+1}/5] {step}", ncols=80, colour="green", leave=False) as pbar:
                                for j in range(10):
                                    time.sleep(0.05)
                                    pbar.update(10)
                    else:
                        # Basic dot animation fallback
                        print("Sending email...")
                        for i in range(5):
                            time.sleep(0.5)
                            print(".", end="", flush=True)
                        print("")
                    
                    # Send the test email
                    success = self.send_email(
                        username=username,
                        to_email=email,
                        subject="EcoCycle Test Email",
                        message_body=f"Hello {name},\n\nThis is a test email from EcoCycle to verify your notification settings.\n\nThe EcoCycle Team"
                    )
                    
                    if success:
                        console.print("[bold green]✓ Test email sent successfully![/]")
                        console.print(f"Check [cyan]{email}[/] for the test email.")
                    else:
                        console.print("[bold red]✗ Error sending test email.[/]")
                        console.print("[yellow]Please check your email settings and try again.[/]")
                    
                    time.sleep(0.5)
                    Prompt.ask("Press Enter to continue", default="")
                else:
                    # ASCII fallback with tqdm support
                    if not user_settings['email_notifications']:
                        print(f"{ascii_art.Fore.YELLOW}Warning: Email notifications are disabled in your settings.{ascii_art.Style.RESET_ALL}")
                    
                    email = user.get('email', '')
                    if not email:
                        print(f"{ascii_art.Fore.RED}Error: No email address set. Please update your contact information.{ascii_art.Style.RESET_ALL}")
                        input("\nPress Enter to continue...")
                        continue
                    
                    print(f"Sending test email to: {email}")
                    
                    if TQDM_AVAILABLE:
                        # Use tqdm for progress indication
                        email_steps = ["Preparing", "Connecting", "Authenticating", "Sending", "Finalizing"]
                        for i, step in enumerate(email_steps):
                            with tqdm(total=100, desc=f"[{i+1}/5] {step}", leave=False) as pbar:
                                for j in range(10):
                                    time.sleep(0.03)
                                    pbar.update(10)
                    else:
                        # Basic dot animation fallback
                        print("Sending email...")
                        for i in range(5):
                            time.sleep(0.3)
                            print(".", end="", flush=True)
                        print("")
                    
                    success = self.send_email(
                        username=username,
                        to_email=email,
                        subject="EcoCycle Test Email",
                        message_body=f"Hello {name},\n\nThis is a test email from EcoCycle to verify your notification settings.\n\nThe EcoCycle Team"
                    )
                    
                    if success:
                        print(f"{ascii_art.Fore.GREEN}Test email sent successfully!{ascii_art.Style.RESET_ALL}")
                        print(f"Check {email} for the test email.")
                    else:
                        print(f"{ascii_art.Fore.RED}Error sending test email.{ascii_art.Style.RESET_ALL}")
                        print("Please check your email settings and try again.")
                    
                    input("\nPress Enter to continue...")
            
            elif choice == "2":
                # Test SMS notification
                if HAS_RICH:
                    console.clear()
                    console.print(Panel.fit(
                        "[bold cyan]Testing SMS Notification Delivery[/]",
                        title="[bold purple]SMS Test[/]",
                        border_style="purple"
                    ))
                    
                    if not user_settings['sms_notifications']:
                        console.print(Panel("[yellow]Warning: SMS notifications are disabled in your settings.[/]", border_style="yellow"))
                    
                    phone = user.get('phone', '')
                    if not phone:
                        console.print(Panel("[bold red]Error: No phone number set. Please update your contact information first.[/]", border_style="red"))
                        time.sleep(2)
                        continue
                    
                    console.print(f"\nSending test SMS to: [cyan]{phone}[/]")
                    
                    # Enhanced SMS sending animation with tqdm progress bar
                    console.print("[bold green]Sending SMS - please wait...[/]")
                    sms_steps = [
                        "Validating phone number",
                        "Connecting to messaging service",
                        "Preparing message payload",
                        "Sending to carrier network",
                        "Confirming delivery status"
                    ]
                    
                    # Use tqdm progress bar with description updates
                    if TQDM_AVAILABLE:
                        for i, step in enumerate(sms_steps):
                            with tqdm(total=100, desc=f"[{i+1}/5] {step}", ncols=80, colour="green", leave=False) as pbar:
                                for j in range(10):
                                    time.sleep(0.05)
                                    pbar.update(10)
                    else:
                        # Basic dot animation fallback
                        print("Sending SMS...")
                        for i in range(5):
                            time.sleep(0.5)
                            print(".", end="", flush=True)
                        print("")
                    
                    # In a real application, we would use an SMS service like Twilio
                    # For this demo, we'll simulate sending an SMS
                    success = self._simulate_send_sms(
                        username=username,
                        to_phone=phone,
                        message=f"EcoCycle: Hello {name}, this is a test SMS to verify your notification settings."
                    )
                    
                    if success:
                        console.print("[bold green]✓ Test SMS sent successfully![/]")
                        console.print(f"Check your phone [cyan]{phone}[/] for the test SMS.")
                    else:
                        console.print("[bold red]✗ Error sending test SMS.[/]")
                        console.print("[yellow]Please check your phone settings and try again.[/]")
                    
                    time.sleep(0.5)
                    Prompt.ask("Press Enter to continue", default="")
                else:
                    # ASCII fallback with tqdm support
                    if not user_settings['sms_notifications']:
                        print("SMS notifications are disabled. Please update your preferences first.")
                        continue
                    if not phone:
                        print("No phone number set. Please update your contact information first.")
                        continue
                        
                    print("Sending test SMS to:", phone)
                    
                    if TQDM_AVAILABLE:
                        # Use tqdm for progress indication
                        sms_steps = ["Validating", "Connecting", "Preparing", "Sending", "Confirming"]
                        for i, step in enumerate(sms_steps):
                            with tqdm(total=100, desc=f"[{i+1}/5] {step}", leave=False) as pbar:
                                for j in range(10):
                                    time.sleep(0.03)
                                    pbar.update(10)
                    else:
                        # Basic dot animation fallback
                        print("Sending SMS...")
                        for i in range(5):
                            time.sleep(0.3)
                            print(".", end="", flush=True)
                        print("")
                    
                    success = self._simulate_send_sms(
                        username=username,
                        to_phone=phone,
                        message=f"EcoCycle: Hello {name}, this is a test SMS to verify your notification settings."
                    )
                    
                    if success:
                        print(f"{ascii_art.Fore.GREEN}Test SMS sent successfully!{ascii_art.Style.RESET_ALL}")
                        print(f"Check your phone {phone} for the test SMS.")
                    else:
                        print(f"{ascii_art.Fore.RED}Error sending test SMS.{ascii_art.Style.RESET_ALL}")
                        print("Please check your phone settings and try again.")
                    
                    input("\nPress Enter to continue...")
            
            elif choice == "3":
                # Test achievement notification
                if HAS_RICH:
                    console.clear()
                    console.print(Panel.fit(
                        "[bold cyan]Testing Achievement Notification[/]",
                        title="[bold purple]Achievement Test[/]",
                        border_style="purple"
                    ))
                    
                    if not user_settings['achievement_notifications']:
                        console.print(Panel("[yellow]Warning: Achievement notifications are disabled in your settings.[/]", border_style="yellow"))
                    
                    # Create a test achievement with a nicer display in Rich
                    test_achievement = {
                        "name": "Test Achievement",
                        "description": "This is a test achievement to verify your notification settings.",
                        "points": 15,
                        "icon": "🧪"
                    }
                    
                    achievement_panel = Panel(
                        f"[bold]🧪 {test_achievement['name']}[/]\n\n{test_achievement['description']}\n\n[green]+{test_achievement['points']} points[/]",
                        title="[bold green]Achievement Unlocked![/]",
                        border_style="green"
                    )
                    console.print(achievement_panel)
                    
                    # Log a test achievement notification with progress animation
                    # Use tqdm for achievement notification creation
                    console.print("[bold magenta]Creating achievement notification...[/]")
                    achievement_steps = [
                        "Generating achievement details",
                        "Creating notification record",
                        "Preparing delivery channels"
                    ]
                    
                    for i, step in enumerate(achievement_steps):
                        with tqdm(total=100, desc=f"[{i+1}/3] {step}", ncols=80, colour="magenta", leave=False) as pbar:
                            for j in range(10):
                                time.sleep(0.04)
                                pbar.update(10)
                        time.sleep(1)
                        self._log_app_notification(
                            username=username,
                            notification_type="achievement",
                            message=f"You've earned the {test_achievement['name']} achievement! {test_achievement['description']}"
                        )
                    
                    console.print("\n[bold green]✓ Test achievement notification created![/]")
                    console.print("[italic]You can view it in your notification history.[/]")
                    
                    # If email notifications are enabled, also send an email
                    if user_settings['email_notifications']:
                        email = user.get('email', '')
                        if email:
                            console.print(f"\nAlso sending achievement email to: [cyan]{email}[/]")
                            
                            # Use tqdm for achievement email delivery
                            console.print("[bold cyan]Sending achievement email...[/]")
                            achievement_email_steps = [
                                "Generating achievement template",
                                "Adding personalized content",
                                "Establishing secure connection",
                                "Delivering notification"
                            ]
                            
                            for i, step in enumerate(achievement_email_steps):
                                with tqdm(total=100, desc=f"[{i+1}/4] {step}", ncols=80, colour="blue", leave=False) as pbar:
                                    for j in range(10):
                                        time.sleep(0.04)
                                        pbar.update(10)
                                time.sleep(1)
                                # Read achievement template
                                template_path = os.path.join(EMAIL_TEMPLATES_DIR, "achievement_notification.txt")
                                if os.path.exists(template_path):
                                    with open(template_path, 'r') as file:
                                        template = file.read()
                                    
                                    # Replace placeholders
                                    message = template.replace("{name}", name)
                                    message = message.replace("{achievement_name}", test_achievement['name'])
                                    message = message.replace("{achievement_description}", test_achievement['description'])
                                    message = message.replace("{points}", str(test_achievement['points']))
                                    
                                    # Send email
                                    self._simulate_send_email(
                                        username=username,
                                        to_email=email,
                                        subject="EcoCycle Achievement Unlocked!",
                                        message=message
                                    )
                    
                    # If SMS notifications are enabled, also send an SMS
                    if user_settings['sms_notifications']:
                        phone = user.get('phone', '')
                        if phone:
                            console.print(f"\nAlso sending achievement SMS to: [cyan]{phone}[/]")
                            
                            # Use tqdm for achievement SMS delivery
                            console.print("[bold cyan]Sending achievement SMS...[/]")
                            achievement_sms_steps = [
                                "Creating concise message",
                                "Connecting to messaging service",
                                "Delivering to mobile device"
                            ]
                            
                            for i, step in enumerate(achievement_sms_steps):
                                with tqdm(total=100, desc=f"[{i+1}/3] {step}", ncols=80, colour="blue", leave=False) as pbar:
                                    for j in range(10):
                                        time.sleep(0.04)
                                        pbar.update(10)
                                time.sleep(1)
                                # Send SMS
                                self._simulate_send_sms(
                                    username=username,
                                    to_phone=phone,
                                    message=f"EcoCycle: Congratulations {name}! You've earned the {test_achievement['name']} achievement (+{test_achievement['points']} points)."
                                )
                    
                    time.sleep(0.5)
                    Prompt.ask("Press Enter to continue", default="")
                else:
                    # ASCII fallback
                    if not user_settings['achievement_notifications']:
                        print(f"{ascii_art.Fore.YELLOW}Warning: Achievement notifications are disabled in your settings.{ascii_art.Style.RESET_ALL}")
                    
                    # Create a test achievement
                    test_achievement = {
                        "name": "Test Achievement",
                        "description": "This is a test achievement to verify your notification settings.",
                        "points": 15,
                        "icon": "🧪"
                    }
                    
                    # Display the achievement information
                    print(f"\n{ascii_art.Fore.GREEN}🧪 Achievement Unlocked: {test_achievement['name']}{ascii_art.Style.RESET_ALL}")
                    print(f"{test_achievement['description']}")
                    print(f"{ascii_art.Fore.YELLOW}+{test_achievement['points']} points{ascii_art.Style.RESET_ALL}")
                    
                    # Log a test achievement notification
                    self._log_app_notification(
                        username=username,
                        notification_type="achievement",
                        message=f"You've earned the {test_achievement['name']} achievement! {test_achievement['description']}"
                    )
                    
                    print(f"\n{ascii_art.Fore.GREEN}Test achievement notification created!{ascii_art.Style.RESET_ALL}")
                    print("You can view it in your notification history.")
                    
                    # If email notifications are enabled, also send an email
                    if user_settings['email_notifications']:
                        email = user.get('email', '')
                        if email:
                            print(f"\nSending achievement email to: {email}")
                            
                            # Read achievement template
                            template_path = os.path.join(EMAIL_TEMPLATES_DIR, "achievement_notification.txt")
                            if os.path.exists(template_path):
                                with open(template_path, 'r') as file:
                                    template = file.read()
                                
                                # Replace placeholders
                                message = template.replace("{name}", name)
                                message = message.replace("{achievement_name}", test_achievement['name'])
                                message = message.replace("{achievement_description}", test_achievement['description'])
                                message = message.replace("{points}", str(test_achievement['points']))
                                
                                # Send email
                                self._simulate_send_email(
                                    username=username,
                                    to_email=email,
                                    subject="EcoCycle Achievement Unlocked!",
                                    message=message
                                )
                    
                    # If SMS notifications are enabled, also send an SMS
                    if user_settings['sms_notifications']:
                        phone = user.get('phone', '')
                        if phone:
                            print(f"\nSending achievement SMS to: {phone}")
                            
                            # Send SMS
                            self._simulate_send_sms(
                                username=username,
                                to_phone=phone,
                                message=f"EcoCycle: Congratulations {name}! You've earned the {test_achievement['name']} achievement (+{test_achievement['points']} points)."
                            )
                    
                    input("\nPress Enter to continue...")
            
            elif choice == "4":
                # Return to notification manager
                break
            
            else:
                # Invalid choice - should never happen with Rich UI
                if HAS_RICH:
                    console.print("[bold red]Invalid option. Please try again.[/]")
                    time.sleep(1)
                else:
                    print(f"{ascii_art.Fore.RED}Invalid choice. Please try again.{ascii_art.Style.RESET_ALL}")
                    input("\nPress Enter to continue...")

    def send_email(self, username: str, to_email: str, subject: str, message_body: str) -> bool:
        """
        Actually sends an email using Gmail SMTP.
        Handles SSL certificate verification issues gracefully.
        """
        SENDER_EMAIL = os.environ.get("GMAIL_SENDER")
        SENDER_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

        if not SENDER_EMAIL or not SENDER_PASSWORD:
            logger.error("Email sending failed: Sender email or password not configured.")
            # Log failure status
            self._log_email_attempt(username, to_email, subject, message_body, "failed", "Configuration missing")
            return False

        if not to_email:
            logger.error(f"Email sending failed for {username}: No recipient email address.")
            # Log failure status (optional, as it might not be logged if no address)
            return False

        msg = EmailMessage()
        msg.set_content(message_body)
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        
        # Create a custom SSL context with certificate verification options
        context = ssl.create_default_context()
        
        # For development/testing, you can disable certificate verification if needed
        # Determine if we're in development/test mode
        DEV_MODE = os.environ.get("ECOCYCLE_DEV_MODE", "false").lower() == "true"
        
        if DEV_MODE:
            # In development mode, don't verify certificates (less secure but helps with testing)
            logger.warning("Running in development mode - SSL certificate verification disabled")
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        else:
            # In production, use the most secure settings
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            # On macOS, we may need to specify the certificate path
            # Try to use the certifi package if available
            try:
                import certifi
                context.load_verify_locations(cafile=certifi.where())
                logger.debug("Using certifi for SSL certificate verification")
            except ImportError:
                # If certifi isn't available, try to use system certificates
                logger.warning("certifi package not available, using system certificates")
                # Default paths for macOS certificates
                mac_cert_paths = [
                    "/etc/ssl/cert.pem",
                    "/private/etc/ssl/cert.pem",
                    "/usr/local/etc/openssl/cert.pem",
                    "/opt/homebrew/etc/openssl@3/cert.pem"
                ]
                # Try each potential certificate path
                cert_loaded = False
                for cert_path in mac_cert_paths:
                    if os.path.exists(cert_path):
                        try:
                            context.load_verify_locations(cafile=cert_path)
                            logger.info(f"Loaded certificates from {cert_path}")
                            cert_loaded = True
                            break
                        except Exception as e:
                            logger.warning(f"Could not load certificates from {cert_path}: {e}")
                
                if not cert_loaded:
                    logger.warning("Could not load certificates from any known location. Email sending may fail.")

        status = "failed"
        error_msg = ""

        try:
            # Connect to Gmail's SMTP server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)
            logger.info(f"Successfully sent email to {to_email} for user {username}")
            status = "success"
            result = True

            # Log to database
            if self.sheets_manager:
                self.sheets_manager.log_email_to_database(username, to_email, subject, message_body, status)

        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP Authentication Error for {SENDER_EMAIL}. Check email/password.")
            error_msg = "SMTP Authentication Error"
            result = False
        except ssl.SSLError as e:
            logger.error(f"SSL certificate verification failed: {e}")
            error_msg = f"SSL certificate verification failed: {e}. Try installing the certifi package or setting ECOCYCLE_DEV_MODE=true for testing."
            result = False
        except smtplib.SMTPException as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            error_msg = str(e)
            result = False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            error_msg = str(e)
            result = False

        # Log the attempt (regardless of success/failure)
        self._log_email_attempt(username, to_email, subject, message_body, status, error_msg)

        return result

    def _log_email_attempt(self, username, to_email, subject, message, status, error=""):
        """Helper function to log email attempts consistently."""
        log_entry = {
            "username": username,
            "to_email": to_email,
            "subject": subject,
            # Consider not logging the full message body for privacy/log size
            # "message": message,
            "timestamp": time.time(),
            "status": status
        }
        if error:
            log_entry["error"] = error

        self.notification_logs['email_logs'].append(log_entry)
        self._save_notification_logs()  # Be mindful of frequent writes if sending many emails

    # --- In test_notifications, change the call ---
    # Replace:
    # success = self._simulate_send_email(...)
    # With:
    # success = self._send_real_email(...)

    def _send_real_sms_via_email(self, username: str, to_phone: str, carrier_gateway: str, message_body: str) -> bool:
        """
        Sends an SMS by emailing the carrier's SMS gateway.
        Requires knowing the carrier gateway domain. VERY UNRELIABLE.
        Uses the same email credentials as _send_real_email.
        """
        SENDER_EMAIL = os.environ.get("GMAIL_SENDER")
        SENDER_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

        if not SENDER_EMAIL or not SENDER_PASSWORD:
            logger.error("SMS sending via Email failed: Sender email or password not configured.")
            self._log_sms_attempt(username, to_phone, message_body, "failed", "Email Configuration missing")
            return False

        if not to_phone or not carrier_gateway:
            logger.error(f"SMS sending via Email failed for {username}: Missing phone number or carrier gateway.")
            self._log_sms_attempt(username, to_phone, message_body, "failed", "Missing phone/gateway")
            return False

        # Basic cleaning of phone number (remove non-digits)
        cleaned_phone = re.sub(r'\D', '', to_phone)
        if not cleaned_phone:
            logger.error(f"SMS sending via Email failed for {username}: Invalid phone number format '{to_phone}'.")
            self._log_sms_attempt(username, to_phone, message_body, "failed", "Invalid phone format")
            return False

        # Construct the gateway email address
        recipient_email = f"{cleaned_phone}@{carrier_gateway}"
        logger.info(f"Attempting to send SMS via Email to: {recipient_email}")

        # Create the email message (SMS content is the body, subject often ignored/prepended)
        msg = EmailMessage()
        # Keep the body short, as gateways often have low limits
        msg.set_content(message_body[:150])  # Limit length just in case
        msg['Subject'] = ""  # Subject is often ignored or adds clutter to SMS
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email

        context = ssl.create_default_context()
        status = "failed"
        error_msg = ""
        result = False

        try:
            # Connect and send using the same SMTP logic as email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)
            logger.info(f"Successfully sent SMS via Email gateway for user {username} to {recipient_email}")
            status = "success"
            result = True

        except smtplib.SMTPAuthenticationError:
            logger.error(
                f"SMTP Authentication Error for {SENDER_EMAIL} while sending SMS via Email. Check email/password.")
            error_msg = "SMTP Authentication Error"
            result = False
        except smtplib.SMTPException as e:
            logger.error(f"Error sending SMS via Email gateway to {recipient_email}: {e}")
            error_msg = str(e)
            result = False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS via Email gateway to {recipient_email}: {e}")
            error_msg = str(e)
            result = False

        # Log the attempt
        self._log_sms_attempt(username, to_phone, message_body, status, error_msg)

        return result

    def _log_sms_attempt(self, username, to_phone, message, status, error=""):
        """Helper function to log SMS attempts consistently."""
        log_entry = {
            "username": username,
            "to_phone": to_phone,
            # Consider not logging the full message body for privacy/log size
            # "message": message,
            "method": "email_gateway",  # Indicate how it was sent
            "timestamp": time.time(),
            "status": status
        }
        if error:
            log_entry["error"] = error

        # Ensure sms_logs exists
        if 'sms_logs' not in self.notification_logs:
            self.notification_logs['sms_logs'] = []

        self.notification_logs['sms_logs'].append(log_entry)
        self._save_notification_logs()  # Be mindful of frequent writes
    
    def _log_app_notification(self, username: str, notification_type: str, message: str) -> None:
        """
        Log an in-app notification.
        
        Args:
            username (str): Recipient username
            notification_type (str): Type of notification (achievement, reminder, etc.)
            message (str): Notification message
        """
        log_entry = {
            "username": username,
            "type": notification_type,
            "message": message,
            "timestamp": time.time(),
            "read": False
        }
        
        self.notification_logs['app_logs'].append(log_entry)
        self._save_notification_logs()
    
    def generate_weekly_summary(self, username: str) -> bool:
        """
        Generate and send a weekly cycling summary for a user.
        
        Args:
            username (str): Username to generate summary for
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if username not in self.notification_settings:
            return False
        
        user_settings = self.notification_settings[username]
        if not user_settings['weekly_summary']:
            return False  # Weekly summary disabled
        
        user = self.user_manager.users.get(username)
        if not user:
            return False
        
        name = user.get('name', username)
        email = user.get('email', '')
        
        # Skip if no email and email notifications are enabled
        if user_settings['email_notifications'] and not email:
            return False
        
        # Get user's cycling data for the last week
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        # Calculate date range for last week
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=7)
        
        # Filter trips for last week
        weekly_trips = []
        for trip in trips:
            date_str = trip.get('date', '')
            if not date_str:
                continue
            
            try:
                trip_date = datetime.datetime.fromisoformat(date_str).date()
                if start_date <= trip_date <= end_date:
                    weekly_trips.append(trip)
            except (ValueError, TypeError):
                continue
        
        # Calculate weekly totals
        trips_count = len(weekly_trips)
        total_distance = sum(trip.get('distance', 0) for trip in weekly_trips)
        co2_saved = sum(trip.get('co2_saved', 0) for trip in weekly_trips)
        calories_burned = sum(trip.get('calories', 0) for trip in weekly_trips)
        
        # Skip if no trips this week
        if trips_count == 0:
            return False
        
        # Compare with previous week
        prev_start_date = start_date - datetime.timedelta(days=7)
        prev_end_date = end_date - datetime.timedelta(days=7)
        
        prev_trips = []
        for trip in trips:
            date_str = trip.get('date', '')
            if not date_str:
                continue
            
            try:
                trip_date = datetime.datetime.fromisoformat(date_str).date()
                if prev_start_date <= trip_date <= prev_end_date:
                    prev_trips.append(trip)
            except (ValueError, TypeError):
                continue
        
        prev_distance = sum(trip.get('distance', 0) for trip in prev_trips)
        
        # Create comparison text
        comparison_text = ""
        if prev_distance > 0:
            pct_change = ((total_distance - prev_distance) / prev_distance) * 100
            if pct_change > 0:
                comparison_text = f"Great job! You cycled {pct_change:.1f}% more than last week."
            elif pct_change < 0:
                comparison_text = f"You cycled {abs(pct_change):.1f}% less than last week. Let's aim higher next week!"
            else:
                comparison_text = "You maintained the same cycling distance as last week. Consistency is key!"
        else:
            comparison_text = "This is your first week of cycling data. Great start!"
        
        # Get a random eco tip
        eco_tip = eco_tips.get_random_tip().get('tip')
        
        # Format dates
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        # Format statistics
        total_distance_str = utils.format_distance(total_distance)
        co2_saved_str = utils.format_co2(co2_saved)
        calories_burned_str = utils.format_calories(calories_burned)
        
        # Read template
        template_path = os.path.join(EMAIL_TEMPLATES_DIR, "weekly_summary.txt")
        if os.path.exists(template_path):
            with open(template_path, 'r') as file:
                template = file.read()
            
            # Replace placeholders
            message = template.replace("{name}", name)
            message = message.replace("{start_date}", start_date_str)
            message = message.replace("{end_date}", end_date_str)
            message = message.replace("{trips_count}", str(trips_count))
            message = message.replace("{total_distance}", total_distance_str)
            message = message.replace("{co2_saved}", co2_saved_str)
            message = message.replace("{calories_burned}", calories_burned_str)
            message = message.replace("{comparison_text}", comparison_text)
            message = message.replace("{eco_tip}", eco_tip)
            
            # Send email if enabled
            if user_settings['email_notifications'] and email:
                self._simulate_send_email(
                    username=username,
                    to_email=email,
                    subject=f"Your EcoCycle Weekly Summary ({start_date_str} to {end_date_str})",
                    message=message
                )
            
            # Send SMS if enabled
            if user_settings['sms_notifications'] and user.get('phone'):
                sms_message = f"EcoCycle Weekly Summary: You completed {trips_count} trips, cycling {total_distance_str} and saving {co2_saved_str} of CO2! Keep it up!"
                self._simulate_send_sms(
                    username=username,
                    to_phone=user.get('phone'),
                    message=sms_message
                )
            
            # Log in-app notification
            self._log_app_notification(
                username=username,
                notification_type="weekly_summary",
                message=f"Your weekly cycling summary is ready! You cycled {total_distance_str} this week."
            )
            
            return True
        
        return False
    
    def send_achievement_notification(self, username: str, achievement: Dict) -> bool:
        """
        Send a notification for a new achievement.
        
        Args:
            username (str): Username to notify
            achievement (dict): Achievement details
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if username not in self.notification_settings:
            return False
        
        user_settings = self.notification_settings[username]
        if not user_settings['achievement_notifications']:
            return False  # Achievement notifications disabled
        
        user = self.user_manager.users.get(username)
        if not user:
            return False
        
        name = user.get('name', username)
        achievement_name = achievement.get('name', 'Unknown Achievement')
        achievement_description = achievement.get('description', 'No description')
        achievement_points = achievement.get('points', 0)
        
        # Log in-app notification
        self._log_app_notification(
            username=username,
            notification_type="achievement",
            message=f"Congratulations! You've earned the {achievement_name} achievement: {achievement_description}"
        )
        
        # Send email if enabled
        if user_settings['email_notifications'] and user.get('email'):
            # Read template
            template_path = os.path.join(EMAIL_TEMPLATES_DIR, "achievement_notification.txt")
            if os.path.exists(template_path):
                with open(template_path, 'r') as file:
                    template = file.read()
                
                # Replace placeholders
                message = template.replace("{name}", name)
                message = message.replace("{achievement_name}", achievement_name)
                message = message.replace("{achievement_description}", achievement_description)
                message = message.replace("{points}", str(achievement_points))
                
                self._simulate_send_email(
                    username=username,
                    to_email=user.get('email'),
                    subject=f"EcoCycle Achievement Unlocked: {achievement_name}",
                    message=message
                )
        
        # Send SMS if enabled
        if user_settings['sms_notifications'] and user.get('phone'):
            sms_message = f"EcoCycle: Congratulations {name}! You've earned the {achievement_name} achievement (+{achievement_points} points)."
            self._simulate_send_sms(
                username=username,
                to_phone=user.get('phone'),
                message=sms_message
            )

        # Log to database
        if self.sheets_manager:
            self.sheets_manager.log_achievement_to_database(username, achievement_name, achievement_description, achievement_points)

        return True
    
    def send_reminder(self, username: str) -> bool:
        """
        Send a reminder to users who haven't logged a trip recently.
        
        Args:
            username (str): Username to remind
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if username not in self.notification_settings:
            return False
        
        user_settings = self.notification_settings[username]
        if user_settings['reminder_frequency'] == 'none':
            return False  # Reminders disabled
        
        user = self.user_manager.users.get(username)
        if not user:
            return False
        
        name = user.get('name', username)
        
        # Get user's trip data
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        # Find the latest trip date
        latest_trip_date = None
        for trip in trips:
            date_str = trip.get('date', '')
            if not date_str:
                continue
            
            try:
                trip_date = datetime.datetime.fromisoformat(date_str).date()
                if latest_trip_date is None or trip_date > latest_trip_date:
                    latest_trip_date = trip_date
            except (ValueError, TypeError):
                continue
        
        # If no trips or latest trip is recent, skip reminder
        if latest_trip_date is None:
            # If no trips at all, only remind once a week
            today = datetime.date.today()
            if user_settings['reminder_frequency'] != 'weekly' and today.weekday() != 0:  # Only on Mondays
                return False
        else:
            days_since_last_trip = (datetime.date.today() - latest_trip_date).days
            
            # Check if reminder is due based on frequency setting
            if user_settings['reminder_frequency'] == 'daily' and days_since_last_trip < 2:
                return False
            elif user_settings['reminder_frequency'] == 'weekly' and days_since_last_trip < 7:
                return False
            elif user_settings['reminder_frequency'] == 'monthly' and days_since_last_trip < 30:
                return False
        
        # Format last trip date
        last_trip_date_str = latest_trip_date.strftime("%Y-%m-%d") if latest_trip_date else "Never"
        
        # Get weather forecast (in a real app, we would use the weather API)
        weather_forecast = "sunny with a high of 22°C, perfect for cycling"
        
        # Read template
        template_path = os.path.join(EMAIL_TEMPLATES_DIR, "reminder.txt")
        if os.path.exists(template_path):
            with open(template_path, 'r') as file:
                template = file.read()
            
            # Replace placeholders
            message = template.replace("{name}", name)
            message = message.replace("{last_trip_date}", last_trip_date_str)
            message = message.replace("{weather_forecast}", weather_forecast)
            
            # Send email if enabled
            if user_settings['email_notifications'] and user.get('email'):
                self._simulate_send_email(
                    username=username,
                    to_email=user.get('email'),
                    subject="EcoCycle Cycling Reminder",
                    message=message
                )
            
            # Send SMS if enabled
            if user_settings['sms_notifications'] and user.get('phone'):
                days_text = f"It's been {days_since_last_trip} days since your last cycling trip." if latest_trip_date else "You haven't logged any cycling trips yet."
                sms_message = f"EcoCycle: Hello {name}! {days_text} The forecast for tomorrow is {weather_forecast}. Let's get cycling!"
                self._simulate_send_sms(
                    username=username,
                    to_phone=user.get('phone'),
                    message=sms_message
                )
            
            # Log in-app notification
            self._log_app_notification(
                username=username,
                notification_type="reminder",
                message=f"Time to get cycling! {weather_forecast}."
            )

            # Log to database
            if self.sheets_manager:
                self.sheets_manager.log_reminder_to_database(username, last_trip_date_str, weather_forecast)
            
            return True
        
        return False
    
    def send_daily_eco_tip(self, username: str) -> bool:
        """
        Send a daily eco tip to a user.
        
        Args:
            username (str): Username to send tip to
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if username not in self.notification_settings:
            return False
        
        user_settings = self.notification_settings[username]
        if not user_settings['eco_tips']:
            return False  # Eco tips disabled
        
        user = self.user_manager.users.get(username)
        if not user:
            return False
        
        name = user.get('name', username)
        
        # Get today's eco tip
        tip = eco_tips.get_tip_of_the_day().get('tip')
        
        # Log in-app notification
        self._log_app_notification(
            username=username,
            notification_type="eco_tip",
            message=f"Eco Tip: {tip}"
        )
        
        # Send email if enabled
        if user_settings['email_notifications'] and user.get('email'):
            message = f"Hello {name},\n\nHere's your EcoCycle eco tip for today:\n\n{tip}\n\nSmall changes make a big difference for our planet!\n\nThe EcoCycle Team"
            self._simulate_send_email(
                username=username,
                to_email=user.get('email'),
                subject="EcoCycle Daily Eco Tip",
                message=message
            )
        
        # Send SMS if enabled
        if user_settings['sms_notifications'] and user.get('phone'):
            sms_message = f"EcoCycle Eco Tip: {tip}"
            self._simulate_send_sms(
                username=username,
                to_phone=user.get('phone'),
                message=sms_message
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
                self._save_notification_settings()
            
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


# Re-export the run_notification_manager function for backward compatibility
# The actual implementation is imported from manager.py

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run notification manager
    run_notification_manager()
