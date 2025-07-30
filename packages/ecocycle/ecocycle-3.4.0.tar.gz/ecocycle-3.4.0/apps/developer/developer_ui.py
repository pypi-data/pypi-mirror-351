"""
EcoCycle - Developer UI Module (Refactored)
Main coordinator for developer tools with modular architecture.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
import json

# Import base UI functionality
from .ui.base_ui import BaseUI, HAS_RICH, console

# Rich imports with fallbacks - import from base_ui for consistency
from .ui.base_ui import Prompt, Confirm, Table, Panel

# Import specialized UI components
from .ui.system_monitoring_ui import SystemMonitoringUI
from .ui.performance_monitoring_ui import PerformanceMonitoringUI
from .ui.log_analysis_ui import LogAnalysisUI
from .ui.data_management_ui import DataManagementUI
from .ui.cache_management_ui import CacheManagementUI
from .ui.export_management_ui import ExportManagementUI
from .ui.configuration_ui import ConfigurationUI
from .ui.email_testing_ui import EmailTestingUI
from .ui.api_testing_ui import APITestingUI
from .ui.security_audit_ui import SecurityAuditUI
from .ui.session_management_ui import SessionManagementUI
from .ui.backup_restore_ui import BackupRestoreUI
from .ui.system_repair_ui import SystemRepairUI
from .ui.health_dashboard_ui import HealthDashboardUI
from .ui.display_utils import DisplayUtils

logger = logging.getLogger(__name__)


class DeveloperUI(BaseUI):
    """Main coordinator for developer tools with modular architecture."""

    def __init__(self, developer_auth, developer_tools):
        """Initialize the developer UI with modular components."""
        super().__init__(developer_auth, developer_tools)

        # Initialize modular UI components
        self.system_monitoring = SystemMonitoringUI(developer_auth, developer_tools)
        self.performance_monitoring = PerformanceMonitoringUI(developer_auth, developer_tools)
        self.log_analysis = LogAnalysisUI(developer_auth, developer_tools)
        self.data_management = DataManagementUI(developer_auth, developer_tools)
        self.cache_management = CacheManagementUI(developer_auth, developer_tools)
        self.export_management = ExportManagementUI(developer_auth, developer_tools)
        self.configuration = ConfigurationUI(developer_auth, developer_tools)
        self.email_testing = EmailTestingUI(developer_auth, developer_tools)
        self.api_testing = APITestingUI(developer_auth, developer_tools)
        self.security_audit = SecurityAuditUI(developer_auth, developer_tools)
        self.session_management = SessionManagementUI(developer_auth, developer_tools)
        self.backup_restore = BackupRestoreUI(developer_auth, developer_tools)
        self.system_repair = SystemRepairUI(developer_auth, developer_tools)
        self.health_dashboard = HealthDashboardUI(developer_auth, developer_tools)
        self.display_utils = DisplayUtils(developer_auth, developer_tools)

    def show_developer_mode_indicator(self):
        """Display visual indicator that developer mode is active."""
        from .ui.base_ui import Panel
        if HAS_RICH and console:
            console.print(Panel.fit(
                "[bold red]🔧 DEVELOPER MODE ACTIVE[/bold red]\n"
                "[yellow]⚠️  You have elevated system privileges[/yellow]\n"
                f"[dim]Session: {self.developer_auth.get_developer_username()}[/dim]",
                border_style="red",
                title="[bold red]DEBUG MODE[/bold red]"
            ))
        else:
            print("=" * 50)
            print("🔧 DEVELOPER MODE ACTIVE")
            print("⚠️  You have elevated system privileges")
            print(f"Session: {self.developer_auth.get_developer_username()}")
            print("=" * 50)

    def show_developer_menu(self) -> str:
        """Display the main developer tools menu."""
        self.show_developer_mode_indicator()

        if HAS_RICH and console:
            console.print("\n[bold cyan]🔧 Developer Tools Menu[/bold cyan]")

            # Create a more organized menu layout
            console.print("\n[bold yellow]📊 System & Monitoring[/bold yellow]")
            console.print("1. System Diagnostics")
            console.print("2. Performance Monitoring")
            console.print("3. Log Analysis")
            console.print("4. System Health Dashboard")

            console.print("\n[bold green]🗄️ Data Management[/bold green]")
            console.print("5. Database Management")
            console.print("6. User Data Management")
            console.print("7. Cache Management")
            console.print("8. Export System Data")

            console.print("\n[bold blue]⚙️ Configuration & Testing[/bold blue]")
            console.print("9. Configuration Management")
            console.print("10. Email System Testing")
            console.print("11. API Testing Tools")
            console.print("12. Security Audit")

            console.print("\n[bold magenta]🔐 Session & Security[/bold magenta]")
            console.print("13. Session Management")
            console.print("14. Backup & Restore")
            console.print("15. System Repair")

            console.print("\n[bold red]🚪 Exit[/bold red]")
            console.print("0. Exit Developer Mode")

            choice = Prompt.ask(
                "\nSelect an option",
                choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"],
                default="0"
            )
        else:
            print("\nDeveloper Tools Menu")
            print("\nSystem & Monitoring:")
            print("1. System Diagnostics")
            print("2. Performance Monitoring")
            print("3. Log Analysis")
            print("4. System Health Dashboard")
            print("\nData Management:")
            print("5. Database Management")
            print("6. User Data Management")
            print("7. Cache Management")
            print("8. Export System Data")
            print("\nConfiguration & Testing:")
            print("9. Configuration Management")
            print("10. Email System Testing")
            print("11. API Testing Tools")
            print("12. Security Audit")
            print("\nSession & Security:")
            print("13. Session Management")
            print("14. Backup & Restore")
            print("15. System Repair")
            print("\n0. Exit Developer Mode")

            choice = input("\nSelect an option (0-15): ").strip()

        return choice

    def handle_choice(self, choice: str):
        """Handle the user's menu choice by delegating to modular components."""
        if choice == "1":
            self.system_monitoring.handle_system_diagnostics()
        elif choice == "2":
            self.performance_monitoring.handle_performance_monitoring()
        elif choice == "3":
            self.log_analysis.handle_log_analysis()
        elif choice == "4":
            self.health_dashboard.handle_system_health_dashboard()
        elif choice == "5":
            self.data_management.handle_database_management()
        elif choice == "6":
            self.data_management.handle_user_data_management()
        elif choice == "7":
            self.cache_management.handle_cache_management()
        elif choice == "8":
            self.export_management.handle_export_system_data()
        elif choice == "9":
            self.configuration.handle_configuration_management()
        elif choice == "10":
            self.email_testing.handle_email_system_testing()
        elif choice == "11":
            self.api_testing.handle_api_testing()
        elif choice == "12":
            self.security_audit.handle_security_audit()
        elif choice == "13":
            self.session_management.handle_session_management()
        elif choice == "14":
            self.backup_restore.handle_backup_restore()
        elif choice == "15":
            self.system_repair.handle_system_repair()

        if choice != "0":
            self.wait_for_user()

    # System repair now handled by SystemRepairUI component
    # Database management now handled by DataManagementUI component

    def _display_database_overview(self, db_data: Dict[str, Any]):
        """Display database overview."""
        self.display_utils.display_database_overview(db_data)

    def _display_table_data(self, table_name: str, table_data: Dict[str, Any]):
        """Display specific table data."""
        self.display_utils.display_table_data(table_name, table_data)

    def _display_table_statistics(self, db_data: Dict[str, Any]):
        """Display table statistics."""
        self.display_utils.display_table_statistics(db_data)

    def wait_for_user(self):
        """Wait for user input to continue."""
        if HAS_RICH and console:
            Prompt.ask("\nPress Enter to continue", default="")
        else:
            input("\nPress Enter to continue...")

    def confirm_action(self, message: str) -> bool:
        """Get user confirmation for potentially dangerous actions."""
        if HAS_RICH and console:
            return Confirm.ask(f"[yellow]{message}[/yellow]")
        else:
            response = input(f"{message} (y/N): ").strip().lower()
            return response == 'y'

    # User data management now handled by DataManagementUI component
    # Cache management now handled by CacheManagementUI component
    # Email system testing now handled by EmailTestingUI component

    def _display_user_list(self, user_data: Dict[str, Any]):
        """Display list of users."""
        if 'error' in user_data:
            if HAS_RICH and console:
                console.print(f"[red]Error: {user_data['error']}[/red]")
            else:
                print(f"Error: {user_data['error']}")
            return

        users = user_data.get('users', [])
        total_count = user_data.get('total_count', 0)

        if HAS_RICH and console:
            table = Table(title=f"User List ({total_count} users)")
            table.add_column("Username", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Email", style="blue")
            table.add_column("Type", style="yellow")
            table.add_column("Trips", style="magenta")
            table.add_column("Distance", style="red")

            for user in users:
                user_type = "Admin" if user.get('is_admin') else ("Guest" if user.get('is_guest') else "User")
                table.add_row(
                    user.get('username', 'N/A'),
                    user.get('name', 'N/A'),
                    user.get('email', 'N/A')[:30] + "..." if len(user.get('email', '')) > 30 else user.get('email', 'N/A'),
                    user_type,
                    str(user.get('total_trips', 0)),
                    f"{user.get('total_distance', 0):.1f} km"
                )

            console.print(table)
        else:
            print(f"\nUser List ({total_count} users):")
            print("-" * 80)
            for user in users:
                user_type = "Admin" if user.get('is_admin') else ("Guest" if user.get('is_guest') else "User")
                print(f"Username: {user.get('username', 'N/A')}")
                print(f"  Name: {user.get('name', 'N/A')}")
                print(f"  Email: {user.get('email', 'N/A')}")
                print(f"  Type: {user_type}")
                print(f"  Trips: {user.get('total_trips', 0)}")
                print(f"  Distance: {user.get('total_distance', 0):.1f} km")
                print()

    def _display_user_details(self, username: str, user_data: Dict[str, Any]):
        """Display detailed user information."""
        if 'error' in user_data:
            if HAS_RICH and console:
                console.print(f"[red]Error: {user_data['error']}[/red]")
            else:
                print(f"Error: {user_data['error']}")
            return

        user_info = user_data.get('user_data', {})

        if HAS_RICH and console:
            # Create a detailed view
            console.print(f"\n[bold cyan]User Details: {username}[/bold cyan]")

            # Basic info
            basic_panel = Panel.fit(
                f"[bold]Name:[/bold] {user_info.get('name', 'N/A')}\n"
                f"[bold]Email:[/bold] {user_info.get('email', 'N/A')}\n"
                f"[bold]Admin:[/bold] {user_info.get('is_admin', False)}\n"
                f"[bold]Guest:[/bold] {user_info.get('is_guest', False)}",
                title="Basic Information"
            )
            console.print(basic_panel)

            # Statistics
            stats = user_info.get('stats', {})
            stats_panel = Panel.fit(
                f"[bold]Total Trips:[/bold] {stats.get('total_trips', 0)}\n"
                f"[bold]Total Distance:[/bold] {stats.get('total_distance', 0):.1f} km\n"
                f"[bold]CO2 Saved:[/bold] {stats.get('total_co2_saved', 0):.1f} kg\n"
                f"[bold]Calories:[/bold] {stats.get('total_calories', 0):.0f}",
                title="Statistics"
            )
            console.print(stats_panel)

        else:
            print(f"\nUser Details: {username}")
            print("=" * 50)
            print(f"Name: {user_info.get('name', 'N/A')}")
            print(f"Email: {user_info.get('email', 'N/A')}")
            print(f"Admin: {user_info.get('is_admin', False)}")
            print(f"Guest: {user_info.get('is_guest', False)}")

            stats = user_info.get('stats', {})
            print(f"\nStatistics:")
            print(f"  Total Trips: {stats.get('total_trips', 0)}")
            print(f"  Total Distance: {stats.get('total_distance', 0):.1f} km")
            print(f"  CO2 Saved: {stats.get('total_co2_saved', 0):.1f} kg")
            print(f"  Calories: {stats.get('total_calories', 0):.0f}")

    def _handle_user_edit(self, username: str):
        """Handle user editing interface."""
        if HAS_RICH and console:
            console.print(f"\n[bold yellow]Edit User: {username}[/bold yellow]")
            console.print("Available fields to edit:")
            console.print("1. name")
            console.print("2. email")
            console.print("3. is_admin")
            console.print("4. is_guest")

            field = Prompt.ask("Enter field to edit", choices=["name", "email", "is_admin", "is_guest"])

            if field in ["is_admin", "is_guest"]:
                value = Confirm.ask(f"Set {field} to True?")
            else:
                value = Prompt.ask(f"Enter new value for {field}")
        else:
            print(f"\nEdit User: {username}")
            print("Available fields: name, email, is_admin, is_guest")
            field = input("Enter field to edit: ").strip()

            if field in ["is_admin", "is_guest"]:
                value = input(f"Set {field} to True? (y/N): ").strip().lower() == 'y'
            else:
                value = input(f"Enter new value for {field}: ").strip()

        if field:
            data = {field: value}
            if HAS_RICH and console:
                with console.status(f"[bold green]Updating {field} for {username}..."):
                    result = self.developer_tools.manage_user_data('edit', username, data)
            else:
                print(f"Updating {field} for {username}...")
                result = self.developer_tools.manage_user_data('edit', username, data)

            self._display_operation_result(result, f"Edit {field} for {username}")

    def _display_operation_result(self, result: Dict[str, Any], operation: str):
        """Display the result of an operation."""
        if 'error' in result:
            if HAS_RICH and console:
                console.print(f"[red]❌ {operation} failed: {result['error']}[/red]")
            else:
                print(f"❌ {operation} failed: {result['error']}")
        elif result.get('success'):
            if HAS_RICH and console:
                console.print(f"[green]✅ {operation} completed successfully[/green]")
            else:
                print(f"✅ {operation} completed successfully")
        else:
            if HAS_RICH and console:
                console.print(f"[yellow]⚠️ {operation} completed with warnings[/yellow]")
            else:
                print(f"⚠️ {operation} completed with warnings")

    def _display_cache_overview(self, cache_data: Dict[str, Any]):
        """Display cache overview."""
        if HAS_RICH and console:
            table = Table(title="Cache Overview")
            table.add_column("Cache Type", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Entries", style="magenta")
            table.add_column("Last Modified", style="blue")

            for cache_name, cache_info in cache_data.items():
                if cache_info.get('exists'):
                    status = "✅ Exists"
                    size = f"{cache_info.get('size', 0)} bytes"
                    entries = str(cache_info.get('entries', 'N/A'))
                    modified = cache_info.get('modified', 'N/A')[:19] if cache_info.get('modified') else 'N/A'
                else:
                    status = "❌ Missing"
                    size = "0 bytes"
                    entries = "0"
                    modified = "N/A"

                table.add_row(cache_name, status, size, entries, modified)

            console.print(table)
        else:
            print("\nCache Overview:")
            print("-" * 80)
            for cache_name, cache_info in cache_data.items():
                print(f"Cache: {cache_name}")
                if cache_info.get('exists'):
                    print(f"  Status: ✅ Exists")
                    print(f"  Size: {cache_info.get('size', 0)} bytes")
                    print(f"  Entries: {cache_info.get('entries', 'N/A')}")
                    print(f"  Modified: {cache_info.get('modified', 'N/A')}")
                else:
                    print(f"  Status: ❌ Missing")
                print()

    def _display_cache_details(self, cache_type: str, cache_data: Dict[str, Any]):
        """Display detailed cache information."""
        cache_info = cache_data.get(cache_type, {})

        if 'error' in cache_info:
            if HAS_RICH and console:
                console.print(f"[red]Error: {cache_info['error']}[/red]")
            else:
                print(f"Error: {cache_info['error']}")
            return

        if HAS_RICH and console:
            console.print(f"\n[bold cyan]Cache Details: {cache_type}[/bold cyan]")

            if cache_info.get('exists'):
                details_panel = Panel.fit(
                    f"[bold]Size:[/bold] {cache_info.get('size', 0)} bytes\n"
                    f"[bold]Entries:[/bold] {cache_info.get('entries', 'N/A')}\n"
                    f"[bold]Modified:[/bold] {cache_info.get('modified', 'N/A')}\n"
                    f"[bold]Sample Keys:[/bold] {', '.join(cache_info.get('sample_keys', [])[:5])}",
                    title=f"{cache_type} Cache"
                )
                console.print(details_panel)
            else:
                console.print(f"[red]Cache {cache_type} does not exist[/red]")
        else:
            print(f"\nCache Details: {cache_type}")
            print("=" * 50)
            if cache_info.get('exists'):
                print(f"Size: {cache_info.get('size', 0)} bytes")
                print(f"Entries: {cache_info.get('entries', 'N/A')}")
                print(f"Modified: {cache_info.get('modified', 'N/A')}")
                print(f"Sample Keys: {', '.join(cache_info.get('sample_keys', [])[:5])}")
            else:
                print(f"Cache {cache_type} does not exist")

    def _display_email_config(self, email_data: Dict[str, Any]):
        """Display email configuration status."""
        smtp_config = email_data.get('smtp_config', {})
        template_check = email_data.get('template_check', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Email Configuration Status[/bold cyan]")

            # SMTP Configuration
            smtp_panel = Panel.fit(
                "\n".join([f"[bold]{key}:[/bold] {'✅ SET' if value == 'SET' else '❌ NOT SET'}"
                          for key, value in smtp_config.items()]),
                title="SMTP Configuration"
            )
            console.print(smtp_panel)

            # Template Status
            if 'error' not in template_check:
                template_status = "\n".join([f"[bold]{template}:[/bold] ✅ {info['size']} bytes"
                                           for template, info in template_check.items()
                                           if isinstance(info, dict)])
                template_panel = Panel.fit(template_status or "No templates found", title="Email Templates")
                console.print(template_panel)
            else:
                console.print(f"[red]Template Error: {template_check['error']}[/red]")

        else:
            print("\nEmail Configuration Status:")
            print("=" * 50)
            print("SMTP Configuration:")
            for key, value in smtp_config.items():
                status = "✅ SET" if value == 'SET' else "❌ NOT SET"
                print(f"  {key}: {status}")

            print("\nEmail Templates:")
            if 'error' not in template_check:
                for template, info in template_check.items():
                    if isinstance(info, dict):
                        print(f"  {template}: ✅ {info['size']} bytes")
            else:
                print(f"  Error: {template_check['error']}")

    def _display_email_test_result(self, result: Dict[str, Any]):
        """Display email test results."""
        test_results = result.get('test_results', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Email Test Results[/bold cyan]")

            if 'error' in test_results:
                console.print(f"[red]❌ Test failed: {test_results['error']}[/red]")
            else:
                success = test_results.get('email_sent', False)
                status = "✅ SUCCESS" if success else "❌ FAILED"

                result_panel = Panel.fit(
                    f"[bold]Status:[/bold] {status}\n"
                    f"[bold]Recipient:[/bold] {test_results.get('recipient', 'N/A')}\n"
                    f"[bold]Test Code:[/bold] {test_results.get('test_code', 'N/A')}",
                    title="Test Results"
                )
                console.print(result_panel)

        else:
            print("\nEmail Test Results:")
            print("=" * 50)
            if 'error' in test_results:
                print(f"❌ Test failed: {test_results['error']}")
            else:
                success = test_results.get('email_sent', False)
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"Status: {status}")
                print(f"Recipient: {test_results.get('recipient', 'N/A')}")
                print(f"Test Code: {test_results.get('test_code', 'N/A')}")

    def _display_email_templates(self, template_data: Dict[str, Any]):
        """Display email template validation results."""
        template_check = template_data.get('template_check', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Email Template Validation[/bold cyan]")

            if 'error' in template_check:
                console.print(f"[red]Error: {template_check['error']}[/red]")
            else:
                table = Table(title="Email Templates")
                table.add_column("Template", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Size", style="yellow")

                for template, info in template_check.items():
                    if isinstance(info, dict):
                        table.add_row(
                            template,
                            "✅ Valid",
                            f"{info['size']} bytes"
                        )

                console.print(table)

        else:
            print("\nEmail Template Validation:")
            print("=" * 50)
            if 'error' in template_check:
                print(f"Error: {template_check['error']}")
            else:
                for template, info in template_check.items():
                    if isinstance(info, dict):
                        print(f"{template}: ✅ Valid ({info['size']} bytes)")

    def handle_configuration_management(self):
        """Handle configuration management interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Configuration Management[/bold cyan]")
            console.print("1. View current configuration")
            console.print("2. Set configuration value")
            console.print("3. Unset configuration value")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3"], default="0")
        else:
            print("\nConfiguration Management")
            print("1. View current configuration")
            print("2. Set configuration value")
            print("3. Unset configuration value")
            print("0. Back to main menu")

            choice = input("Select option (0-3): ").strip()

        if choice == "1":
            # View configuration
            if HAS_RICH and console:
                with console.status("[bold green]Loading configuration..."):
                    config_data = self.developer_tools.manage_configuration('view')
            else:
                print("Loading configuration...")
                config_data = self.developer_tools.manage_configuration('view')

            self._display_configuration(config_data)

        elif choice == "2":
            # Set configuration value
            if HAS_RICH and console:
                key = Prompt.ask("Enter configuration key")
                value = Prompt.ask("Enter configuration value")
            else:
                key = input("Enter configuration key: ").strip()
                value = input("Enter configuration value: ").strip()

            if key and value:
                if HAS_RICH and console:
                    with console.status(f"[bold green]Setting {key}..."):
                        result = self.developer_tools.manage_configuration('set', key, value)
                else:
                    print(f"Setting {key}...")
                    result = self.developer_tools.manage_configuration('set', key, value)

                self._display_operation_result(result, f"Set configuration {key}")

        elif choice == "3":
            # Unset configuration value
            if HAS_RICH and console:
                key = Prompt.ask("Enter configuration key to unset")
            else:
                key = input("Enter configuration key to unset: ").strip()

            if key and self.confirm_action(f"Unset configuration key '{key}'?"):
                if HAS_RICH and console:
                    with console.status(f"[bold yellow]Unsetting {key}..."):
                        result = self.developer_tools.manage_configuration('unset', key)
                else:
                    print(f"Unsetting {key}...")
                    result = self.developer_tools.manage_configuration('unset', key)

                self._display_operation_result(result, f"Unset configuration {key}")

    def _display_configuration(self, config_data: Dict[str, Any]):
        """Display configuration data."""
        config = config_data.get('config', {})

        if HAS_RICH and console:
            table = Table(title="Application Configuration")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Status", style="yellow")

            for key, value in config.items():
                if value == 'NOT SET':
                    status = "❌ Missing"
                elif value == '***HIDDEN***':
                    status = "🔒 Hidden"
                else:
                    status = "✅ Set"

                display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                table.add_row(key, display_value, status)

            console.print(table)
        else:
            print("\nApplication Configuration:")
            print("-" * 80)
            for key, value in config.items():
                if value == 'NOT SET':
                    status = "❌ Missing"
                elif value == '***HIDDEN***':
                    status = "🔒 Hidden"
                else:
                    status = "✅ Set"

                print(f"{key}: {value} ({status})")

    def handle_export_system_data(self):
        """Handle system data export interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Export System Data[/bold cyan]")
            console.print("1. Export all data")
            console.print("2. Export user data only")
            console.print("3. Export database only")
            console.print("4. Export cache data only")
            console.print("5. Export logs only")
            console.print("6. Export configuration only")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")
        else:
            print("\nExport System Data")
            print("1. Export all data")
            print("2. Export user data only")
            print("3. Export database only")
            print("4. Export cache data only")
            print("5. Export logs only")
            print("6. Export configuration only")
            print("0. Back to main menu")

            choice = input("Select option (0-6): ").strip()

        export_types = {
            "1": "all",
            "2": "users",
            "3": "database",
            "4": "cache",
            "5": "logs",
            "6": "config"
        }

        if choice in export_types:
            export_type = export_types[choice]

            if HAS_RICH and console:
                with console.status(f"[bold green]Exporting {export_type} data..."):
                    result = self.developer_tools.export_system_data(export_type)
            else:
                print(f"Exporting {export_type} data...")
                result = self.developer_tools.export_system_data(export_type)

            self._display_export_result(result)

    def _display_export_result(self, result: Dict[str, Any]):
        """Display export operation results."""
        if 'error' in result:
            if HAS_RICH and console:
                console.print(f"[red]❌ Export failed: {result['error']}[/red]")
            else:
                print(f"❌ Export failed: {result['error']}")
        elif result.get('success'):
            if HAS_RICH and console:
                export_panel = Panel.fit(
                    f"[bold]Export Type:[/bold] {result.get('export_type', 'N/A')}\n"
                    f"[bold]Filename:[/bold] {result.get('filename', 'N/A')}\n"
                    f"[bold]Size:[/bold] {result.get('size', 0)} bytes\n"
                    f"[bold]Records:[/bold] {result.get('records_exported', 0)}\n"
                    f"[bold]Path:[/bold] {result.get('path', 'N/A')}",
                    title="✅ Export Successful"
                )
                console.print(export_panel)
            else:
                print("✅ Export Successful")
                print(f"Export Type: {result.get('export_type', 'N/A')}")
                print(f"Filename: {result.get('filename', 'N/A')}")
                print(f"Size: {result.get('size', 0)} bytes")
                print(f"Records: {result.get('records_exported', 0)}")
                print(f"Path: {result.get('path', 'N/A')}")

    def handle_log_analysis(self):
        """Handle log analysis interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Log Analysis[/bold cyan]")
            console.print("1. Analyze all logs")
            console.print("2. Analyze specific log file")
            console.print("3. Search log patterns")
            console.print("4. View recent errors")
            console.print("5. Log statistics")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            print("\nLog Analysis")
            print("1. Analyze all logs")
            print("2. Analyze specific log file")
            print("3. Search log patterns")
            print("4. View recent errors")
            print("5. Log statistics")
            print("0. Back to main menu")

            choice = input("Select option (0-5): ").strip()

        if choice == "1":
            # Analyze all logs
            if HAS_RICH and console:
                with console.status("[bold green]Analyzing all log files..."):
                    log_data = self.developer_tools.analyze_logs()
            else:
                print("Analyzing all log files...")
                log_data = self.developer_tools.analyze_logs()

            self._display_log_analysis(log_data)

        elif choice == "2":
            # Analyze specific log file
            if HAS_RICH and console:
                log_file = Prompt.ask("Enter log filename (e.g., app.log)")
            else:
                log_file = input("Enter log filename (e.g., app.log): ").strip()

            if log_file:
                if HAS_RICH and console:
                    with console.status(f"[bold green]Analyzing {log_file}..."):
                        log_data = self.developer_tools.analyze_logs(log_file)
                else:
                    print(f"Analyzing {log_file}...")
                    log_data = self.developer_tools.analyze_logs(log_file)

                self._display_log_analysis(log_data, log_file)

        elif choice == "3":
            # Search log patterns
            if HAS_RICH and console:
                pattern = Prompt.ask("Enter search pattern (regex supported)")
                lines = int(Prompt.ask("Number of lines to analyze", default="1000"))
            else:
                pattern = input("Enter search pattern (regex supported): ").strip()
                lines = int(input("Number of lines to analyze [1000]: ").strip() or "1000")

            if pattern:
                if HAS_RICH and console:
                    with console.status(f"[bold green]Searching for pattern '{pattern}'..."):
                        log_data = self.developer_tools.analyze_logs(lines=lines)
                else:
                    print(f"Searching for pattern '{pattern}'...")
                    log_data = self.developer_tools.analyze_logs(lines=lines)

                self._display_pattern_search(log_data, pattern)

        elif choice == "4":
            # View recent errors
            if HAS_RICH and console:
                with console.status("[bold green]Loading recent errors..."):
                    log_data = self.developer_tools.analyze_logs(lines=500)
            else:
                print("Loading recent errors...")
                log_data = self.developer_tools.analyze_logs(lines=500)

            self._display_recent_errors(log_data)

        elif choice == "5":
            # Log statistics
            if HAS_RICH and console:
                with console.status("[bold green]Calculating log statistics..."):
                    log_data = self.developer_tools.analyze_logs()
            else:
                print("Calculating log statistics...")
                log_data = self.developer_tools.analyze_logs()

            self._display_log_statistics(log_data)

    def handle_session_management(self):
        """Handle session management interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Session Management[/bold cyan]")
            console.print("1. View active sessions")
            console.print("2. View session history")
            console.print("3. Terminate specific session")
            console.print("4. Clear all sessions")
            console.print("5. Session statistics")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            print("\nSession Management")
            print("1. View active sessions")
            print("2. View session history")
            print("3. Terminate specific session")
            print("4. Clear all sessions")
            print("5. Session statistics")
            print("0. Back to main menu")

            choice = input("Select option (0-5): ").strip()

        if choice == "1":
            # View active sessions
            if HAS_RICH and console:
                with console.status("[bold green]Loading active sessions..."):
                    session_data = self.developer_tools.manage_sessions('list_active')
            else:
                print("Loading active sessions...")
                session_data = self.developer_tools.manage_sessions('list_active')

            self._display_active_sessions(session_data)

        elif choice == "2":
            # View session history
            if HAS_RICH and console:
                with console.status("[bold green]Loading session history..."):
                    session_data = self.developer_tools.manage_sessions('history')
            else:
                print("Loading session history...")
                session_data = self.developer_tools.manage_sessions('history')

            self._display_session_history(session_data)

        elif choice == "3":
            # Terminate specific session
            if HAS_RICH and console:
                session_id = Prompt.ask("Enter session ID to terminate")
            else:
                session_id = input("Enter session ID to terminate: ").strip()

            if session_id and self.confirm_action(f"Terminate session '{session_id}'?"):
                if HAS_RICH and console:
                    with console.status(f"[bold yellow]Terminating session {session_id}..."):
                        result = self.developer_tools.manage_sessions('terminate', session_id)
                else:
                    print(f"Terminating session {session_id}...")
                    result = self.developer_tools.manage_sessions('terminate', session_id)

                self._display_operation_result(result, f"Terminate session {session_id}")

        elif choice == "4":
            # Clear all sessions
            if self.confirm_action("Clear all sessions? This will log out all users."):
                if HAS_RICH and console:
                    with console.status("[bold yellow]Clearing all sessions..."):
                        result = self.developer_tools.manage_sessions('clear_all')
                else:
                    print("Clearing all sessions...")
                    result = self.developer_tools.manage_sessions('clear_all')

                self._display_operation_result(result, "Clear all sessions")

        elif choice == "5":
            # Session statistics
            if HAS_RICH and console:
                with console.status("[bold green]Calculating session statistics..."):
                    session_data = self.developer_tools.manage_sessions('statistics')
            else:
                print("Calculating session statistics...")
                session_data = self.developer_tools.manage_sessions('statistics')

            self._display_session_statistics(session_data)

    def _display_log_analysis(self, log_data: Dict[str, Any], specific_file: Optional[str] = None):
        """Display log analysis results."""
        if 'error' in log_data:
            if HAS_RICH and console:
                console.print(f"[red]Error: {log_data['error']}[/red]")
            else:
                print(f"Error: {log_data['error']}")
            return

        analysis = log_data.get('analysis', {})
        patterns = log_data.get('patterns', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Log Analysis Results[/bold cyan]")

            # Analysis summary table
            table = Table(title="Log File Analysis")
            table.add_column("Log File", style="cyan")
            table.add_column("Total Lines", style="green")
            table.add_column("Errors", style="red")
            table.add_column("Warnings", style="yellow")
            table.add_column("Info", style="blue")
            table.add_column("Size", style="magenta")

            for log_file, info in analysis.items():
                if 'error' not in info:
                    table.add_row(
                        log_file,
                        str(info.get('total_lines', 0)),
                        str(info.get('error_count', 0)),
                        str(info.get('warning_count', 0)),
                        str(info.get('info_count', 0)),
                        f"{info.get('file_size', 0)} bytes"
                    )

            console.print(table)

            # Error patterns
            if patterns:
                console.print("\n[bold yellow]Error Patterns[/bold yellow]")
                for log_file, pattern_data in patterns.items():
                    if pattern_data:
                        pattern_panel = Panel.fit(
                            "\n".join([f"[bold]{error_type}:[/bold] {count}"
                                     for error_type, count in pattern_data.items()]),
                            title=f"Patterns in {log_file}"
                        )
                        console.print(pattern_panel)

        else:
            print("\nLog Analysis Results:")
            print("-" * 80)
            for log_file, info in analysis.items():
                if 'error' not in info:
                    print(f"Log File: {log_file}")
                    print(f"  Total Lines: {info.get('total_lines', 0)}")
                    print(f"  Errors: {info.get('error_count', 0)}")
                    print(f"  Warnings: {info.get('warning_count', 0)}")
                    print(f"  Info: {info.get('info_count', 0)}")
                    print(f"  Size: {info.get('file_size', 0)} bytes")
                    print()

    def _display_pattern_search(self, log_data: Dict[str, Any], pattern: str):
        """Display pattern search results."""
        import re

        recent_entries = log_data.get('recent_entries', {})
        matches = []

        for log_file, entries in recent_entries.items():
            for entry in entries:
                try:
                    if re.search(pattern, entry, re.IGNORECASE):
                        matches.append((log_file, entry))
                except re.error:
                    # If regex is invalid, do simple string search
                    if pattern.lower() in entry.lower():
                        matches.append((log_file, entry))

        if HAS_RICH and console:
            console.print(f"\n[bold cyan]Pattern Search Results for: '{pattern}'[/bold cyan]")

            if matches:
                table = Table(title=f"Found {len(matches)} matches")
                table.add_column("Log File", style="cyan")
                table.add_column("Entry", style="green")

                for log_file, entry in matches[:50]:  # Limit to 50 results
                    table.add_row(log_file, entry[:100] + "..." if len(entry) > 100 else entry)

                console.print(table)
            else:
                console.print("[yellow]No matches found[/yellow]")
        else:
            print(f"\nPattern Search Results for: '{pattern}'")
            print("-" * 80)
            if matches:
                for log_file, entry in matches[:50]:
                    print(f"{log_file}: {entry[:100]}...")
            else:
                print("No matches found")

    def _display_recent_errors(self, log_data: Dict[str, Any]):
        """Display recent errors from logs."""
        analysis = log_data.get('analysis', {})
        recent_entries = log_data.get('recent_entries', {})

        errors = []
        for log_file, entries in recent_entries.items():
            for entry in entries:
                if 'ERROR' in entry.upper():
                    errors.append((log_file, entry))

        if HAS_RICH and console:
            console.print("\n[bold red]Recent Errors[/bold red]")

            if errors:
                table = Table(title=f"Found {len(errors)} recent errors")
                table.add_column("Log File", style="cyan")
                table.add_column("Error Message", style="red")

                for log_file, error in errors[-20:]:  # Show last 20 errors
                    table.add_row(log_file, error[:100] + "..." if len(error) > 100 else error)

                console.print(table)
            else:
                console.print("[green]No recent errors found[/green]")
        else:
            print("\nRecent Errors:")
            print("-" * 80)
            if errors:
                for log_file, error in errors[-20:]:
                    print(f"{log_file}: {error[:100]}...")
            else:
                print("No recent errors found")

    def _display_log_statistics(self, log_data: Dict[str, Any]):
        """Display log statistics."""
        analysis = log_data.get('analysis', {})

        total_lines = sum(info.get('total_lines', 0) for info in analysis.values() if 'error' not in info)
        total_errors = sum(info.get('error_count', 0) for info in analysis.values() if 'error' not in info)
        total_warnings = sum(info.get('warning_count', 0) for info in analysis.values() if 'error' not in info)
        total_info = sum(info.get('info_count', 0) for info in analysis.values() if 'error' not in info)
        total_files = len([f for f, info in analysis.items() if 'error' not in info])

        if HAS_RICH and console:
            stats_panel = Panel.fit(
                f"[bold]Total Log Files:[/bold] {total_files}\n"
                f"[bold]Total Lines:[/bold] {total_lines:,}\n"
                f"[bold]Total Errors:[/bold] {total_errors:,}\n"
                f"[bold]Total Warnings:[/bold] {total_warnings:,}\n"
                f"[bold]Total Info:[/bold] {total_info:,}\n"
                f"[bold]Error Rate:[/bold] {(total_errors/total_lines*100):.2f}% of all lines" if total_lines > 0 else "[bold]Error Rate:[/bold] N/A",
                title="📊 Log Statistics"
            )
            console.print(stats_panel)
        else:
            print("\nLog Statistics:")
            print(f"Total Log Files: {total_files}")
            print(f"Total Lines: {total_lines:,}")
            print(f"Total Errors: {total_errors:,}")
            print(f"Total Warnings: {total_warnings:,}")
            print(f"Total Info: {total_info:,}")
            if total_lines > 0:
                print(f"Error Rate: {(total_errors/total_lines*100):.2f}% of all lines")

    def _display_active_sessions(self, session_data: Dict[str, Any]):
        """Display active sessions."""
        if 'error' in session_data:
            if HAS_RICH and console:
                console.print(f"[red]Error: {session_data['error']}[/red]")
            else:
                print(f"Error: {session_data['error']}")
            return

        sessions = session_data.get('active_sessions', [])

        if HAS_RICH and console:
            console.print("\n[bold cyan]Active Sessions[/bold cyan]")

            if sessions:
                table = Table(title=f"Active Sessions ({len(sessions)})")
                table.add_column("Session ID", style="cyan")
                table.add_column("Username", style="green")
                table.add_column("Start Time", style="yellow")
                table.add_column("Last Activity", style="blue")
                table.add_column("Status", style="magenta")

                for session in sessions:
                    table.add_row(
                        session.get('session_id', 'N/A')[:16] + "...",
                        session.get('username', 'N/A'),
                        session.get('start_time', 'N/A'),
                        session.get('last_activity', 'N/A'),
                        session.get('status', 'N/A')
                    )

                console.print(table)
            else:
                console.print("[yellow]No active sessions found[/yellow]")
        else:
            print("\nActive Sessions:")
            print("-" * 80)
            if sessions:
                for session in sessions:
                    print(f"Session ID: {session.get('session_id', 'N/A')}")
                    print(f"  Username: {session.get('username', 'N/A')}")
                    print(f"  Start Time: {session.get('start_time', 'N/A')}")
                    print(f"  Last Activity: {session.get('last_activity', 'N/A')}")
                    print(f"  Status: {session.get('status', 'N/A')}")
                    print()
            else:
                print("No active sessions found")

    def _display_session_history(self, session_data: Dict[str, Any]):
        """Display session history."""
        if 'error' in session_data:
            if HAS_RICH and console:
                console.print(f"[red]Error: {session_data['error']}[/red]")
            else:
                print(f"Error: {session_data['error']}")
            return

        history = session_data.get('session_history', [])

        if HAS_RICH and console:
            console.print("\n[bold cyan]Session History[/bold cyan]")

            if history:
                table = Table(title=f"Session History ({len(history)} sessions)")
                table.add_column("Session ID", style="cyan")
                table.add_column("Username", style="green")
                table.add_column("Start Time", style="yellow")
                table.add_column("End Time", style="blue")
                table.add_column("Duration", style="magenta")

                for session in history[-20:]:  # Show last 20 sessions
                    table.add_row(
                        session.get('session_id', 'N/A')[:16] + "...",
                        session.get('username', 'N/A'),
                        session.get('start_time', 'N/A'),
                        session.get('end_time', 'N/A'),
                        session.get('duration', 'N/A')
                    )

                console.print(table)
            else:
                console.print("[yellow]No session history found[/yellow]")
        else:
            print("\nSession History:")
            print("-" * 80)
            if history:
                for session in history[-20:]:
                    print(f"Session ID: {session.get('session_id', 'N/A')}")
                    print(f"  Username: {session.get('username', 'N/A')}")
                    print(f"  Start Time: {session.get('start_time', 'N/A')}")
                    print(f"  End Time: {session.get('end_time', 'N/A')}")
                    print(f"  Duration: {session.get('duration', 'N/A')}")
                    print()
            else:
                print("No session history found")

    def _display_session_statistics(self, session_data: Dict[str, Any]):
        """Display session statistics."""
        self.display_utils.display_session_statistics(session_data)

    # Performance monitoring now handled by PerformanceMonitoringUI component

    def _display_performance_metrics(self, perf_data: Dict[str, Any]):
        """Display performance monitoring data."""
        self.display_utils.display_performance_metrics(perf_data)



    def _display_session_status(self, session_data: Dict[str, Any]):
        """Display session status information."""
        dev_session = session_data.get('developer_session', {})
        user_sessions = session_data.get('user_sessions', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Session Status[/bold cyan]")

            # Developer session
            dev_panel = Panel.fit(
                f"[bold]Username:[/bold] {dev_session.get('username', 'N/A')}\n"
                f"[bold]Authenticated:[/bold] {'✅ Yes' if dev_session.get('authenticated') else '❌ No'}\n"
                f"[bold]Session Start:[/bold] {dev_session.get('session_start', 'N/A')}\n"
                f"[bold]Time Remaining:[/bold] {dev_session.get('time_remaining', 'N/A')} seconds",
                title="Developer Session"
            )
            console.print(dev_panel)

            # User sessions
            if 'error' not in user_sessions:
                user_panel = Panel.fit(
                    f"[bold]Current User:[/bold] {user_sessions.get('current_user', 'None')}\n"
                    f"[bold]Login Time:[/bold] {user_sessions.get('login_time', 'N/A')}\n"
                    f"[bold]Last Activity:[/bold] {user_sessions.get('last_activity', 'N/A')}",
                    title="User Sessions"
                )
                console.print(user_panel)
            else:
                console.print(f"[yellow]User Sessions: {user_sessions['error']}[/yellow]")

    # API testing now handled by APITestingUI component
    # Security audit now handled by SecurityAuditUI component
    # Backup & restore now handled by BackupRestoreUI component

    def handle_system_health_dashboard(self):
        """Handle system health dashboard interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 System Health Dashboard[/bold cyan]")

            with console.status("[bold green]Loading system health data..."):
                health_data = self.developer_tools.get_system_health()

            self._display_health_dashboard(health_data)

            console.print("\n[bold yellow]Dashboard Options[/bold yellow]")
            console.print("1. Refresh dashboard")
            console.print("2. Export health report")
            console.print("3. Set health alerts")
            console.print("4. View detailed metrics")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"], default="0")
        else:
            print("\nSystem Health Dashboard")
            print("Loading system health data...")
            health_data = self.developer_tools.get_system_health()
            self._display_health_dashboard(health_data)

            print("\nDashboard Options:")
            print("1. Refresh dashboard")
            print("2. Export health report")
            print("3. Set health alerts")
            print("4. View detailed metrics")
            print("0. Back to main menu")

            choice = input("Select option (0-4): ").strip()

        if choice == "1":
            self.handle_system_health_dashboard()  # Refresh
        elif choice == "2":
            self._export_health_report()
        elif choice == "3":
            self._set_health_alerts()
        elif choice == "4":
            self._view_detailed_metrics()

    # API testing methods now handled by APITestingUI component

    # All API testing methods now handled by APITestingUI component

    # All security audit methods now handled by SecurityAuditUI component

    def _display_health_dashboard(self, health_data: Dict[str, Any]):
        """Display system health dashboard."""
        if 'error' in health_data:
            if HAS_RICH and console:
                console.print(f"[red]Error loading health data: {health_data['error']}[/red]")
            else:
                print(f"Error loading health data: {health_data['error']}")
            return

        overall_status = health_data.get('overall_status', 'unknown')
        components = health_data.get('components', {})
        alerts = health_data.get('alerts', [])

        if HAS_RICH and console:
            # Overall status
            status_colors = {
                'healthy': 'green',
                'warning': 'yellow',
                'critical': 'red',
                'unknown': 'white'
            }
            status_color = status_colors.get(overall_status, 'white')

            console.print(f"\n[bold]System Status:[/bold] [{status_color}]{overall_status.upper()}[/{status_color}]")

            # Components status
            if components:
                for component, status_info in components.items():
                    if isinstance(status_info, dict):
                        comp_status = status_info.get('status', 'unknown')
                        comp_color = status_colors.get(comp_status, 'white')

                        details = []
                        for key, value in status_info.items():
                            if key != 'status':
                                details.append(f"{key.replace('_', ' ').title()}: {value}")

                        details_text = "\n".join(details) if details else "No additional details"

                        comp_panel = Panel(
                            details_text,
                            title=f"{component.title()} - [{comp_color}]{comp_status.upper()}[/{comp_color}]",
                            border_style=comp_color
                        )
                        console.print(comp_panel)

            # Alerts
            if alerts:
                alerts_text = "\n".join([f"• {alert}" for alert in alerts])
                alerts_panel = Panel(alerts_text, title="🚨 Active Alerts", border_style="red")
                console.print(alerts_panel)
            else:
                console.print(Panel("✅ No active alerts", title="Alerts", border_style="green"))
        else:
            print(f"\nSystem Status: {overall_status.upper()}")

            if components:
                print("\nComponent Status:")
                for component, status_info in components.items():
                    if isinstance(status_info, dict):
                        comp_status = status_info.get('status', 'unknown')
                        print(f"  {component.title()}: {comp_status.upper()}")

                        for key, value in status_info.items():
                            if key != 'status':
                                print(f"    {key.replace('_', ' ').title()}: {value}")

            if alerts:
                print("\nActive Alerts:")
                for alert in alerts:
                    print(f"  • {alert}")
            else:
                print("\n✅ No active alerts")

    def _create_full_backup(self):
        """Create full system backup."""
        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self.developer_tools)

            if HAS_RICH and console:
                console.print("\n[bold cyan]🔄 Creating Full System Backup[/bold cyan]")

                # Get backup options
                include_sensitive = Prompt.ask("Include sensitive data (passwords, keys)?", choices=["y", "n"], default="n") == "y"
                encrypt_backup = Prompt.ask("Encrypt backup?", choices=["y", "n"], default="y") == "y"

                encryption_key = None
                if encrypt_backup:
                    encryption_key = Prompt.ask("Enter encryption password", password=True)
                    if not encryption_key:
                        console.print("[red]❌ Encryption password required[/red]")
                        return

                with console.status("[bold green]Creating full system backup..."):
                    result = backup_manager.create_full_backup(
                        include_sensitive=include_sensitive,
                        encryption_key=encryption_key
                    )

                if result.get('success'):
                    console.print(f"[green]✅ Full system backup created successfully[/green]")
                    console.print(f"[cyan]📁 Backup file: {result['backup_path']}[/cyan]")
                    console.print(f"[cyan]📊 Backup size: {result['size_mb']:.2f} MB[/cyan]")
                    console.print(f"[cyan]📦 Components: {', '.join(result['components'])}[/cyan]")
                else:
                    console.print(f"[red]❌ Backup failed: {result.get('error', 'Unknown error')}[/red]")
            else:
                print("\n🔄 Creating Full System Backup")
                include_sensitive = input("Include sensitive data (passwords, keys)? (y/n): ").lower() == 'y'
                encrypt_backup = input("Encrypt backup? (y/n): ").lower() == 'y'

                encryption_key = None
                if encrypt_backup:
                    import getpass
                    encryption_key = getpass.getpass("Enter encryption password: ")
                    if not encryption_key:
                        print("❌ Encryption password required")
                        return

                print("Creating full system backup...")
                result = backup_manager.create_full_backup(
                    include_sensitive=include_sensitive,
                    encryption_key=encryption_key
                )

                if result.get('success'):
                    print(f"✅ Full system backup created successfully")
                    print(f"📁 Backup file: {result['backup_path']}")
                    print(f"📊 Backup size: {result['size_mb']:.2f} MB")
                    print(f"📦 Components: {', '.join(result['components'])}")
                else:
                    print(f"❌ Backup failed: {result.get('error', 'Unknown error')}")

        except ImportError:
            if HAS_RICH and console:
                console.print("[red]❌ Backup manager not available[/red]")
            else:
                print("❌ Backup manager not available")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]❌ Error creating backup: {e}[/red]")
            else:
                print(f"❌ Error creating backup: {e}")

    def _create_user_backup(self):
        """Create user data backup."""
        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self.developer_tools)

            if HAS_RICH and console:
                console.print("\n[bold cyan]👤 Creating User Data Backup[/bold cyan]")

                # Get user selection
                users_data = self.developer_tools.manage_user_data('list')
                if 'error' in users_data:
                    console.print(f"[red]❌ Error getting users: {users_data['error']}[/red]")
                    return

                users = list(users_data.get('users', {}).keys())
                if not users:
                    console.print("[yellow]⚠️ No users found[/yellow]")
                    return

                console.print("[cyan]Available users:[/cyan]")
                for i, user in enumerate(users, 1):
                    console.print(f"  {i}. {user}")
                console.print(f"  {len(users) + 1}. All users")

                choice = Prompt.ask("Select user", choices=[str(i) for i in range(1, len(users) + 2)])

                if int(choice) == len(users) + 1:
                    selected_users = users
                else:
                    selected_users = [users[int(choice) - 1]]

                encrypt_backup = Prompt.ask("Encrypt backup?", choices=["y", "n"], default="y") == "y"
                encryption_key = None
                if encrypt_backup:
                    encryption_key = Prompt.ask("Enter encryption password", password=True)

                with console.status("[bold green]Creating user data backup..."):
                    result = backup_manager.create_user_backup(
                        usernames=selected_users,
                        encryption_key=encryption_key
                    )

                if result.get('success'):
                    console.print(f"[green]✅ User data backup created successfully[/green]")
                    console.print(f"[cyan]📁 Backup file: {result['backup_path']}[/cyan]")
                    console.print(f"[cyan]👥 Users backed up: {len(result['users_backed_up'])}[/cyan]")
                else:
                    console.print(f"[red]❌ Backup failed: {result.get('error', 'Unknown error')}[/red]")
            else:
                print("\n👤 Creating User Data Backup")
                print("🚧 Feature under development - User data backup")

        except ImportError:
            if HAS_RICH and console:
                console.print("[red]❌ Backup manager not available[/red]")
            else:
                print("❌ Backup manager not available")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]❌ Error creating backup: {e}[/red]")
            else:
                print(f"❌ Error creating backup: {e}")

    def _create_database_backup(self):
        """Create database backup."""
        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self.developer_tools)

            if HAS_RICH and console:
                console.print("\n[bold cyan]🗄️ Creating Database Backup[/bold cyan]")

                include_integrity_check = Prompt.ask("Include integrity check?", choices=["y", "n"], default="y") == "y"
                compress_backup = Prompt.ask("Compress backup?", choices=["y", "n"], default="y") == "y"

                with console.status("[bold green]Creating database backup..."):
                    result = backup_manager.create_database_backup(
                        include_integrity_check=include_integrity_check,
                        compress=compress_backup
                    )

                if result.get('success'):
                    console.print(f"[green]✅ Database backup created successfully[/green]")
                    console.print(f"[cyan]📁 Backup file: {result['backup_path']}[/cyan]")
                    console.print(f"[cyan]📊 Database size: {result['database_size_mb']:.2f} MB[/cyan]")
                    if result.get('integrity_check'):
                        console.print(f"[green]✅ Integrity check: {result['integrity_status']}[/green]")
                else:
                    console.print(f"[red]❌ Backup failed: {result.get('error', 'Unknown error')}[/red]")
            else:
                print("\n🗄️ Creating Database Backup")
                print("Creating database backup...")
                result = backup_manager.create_database_backup()

                if result.get('success'):
                    print(f"✅ Database backup created successfully")
                    print(f"📁 Backup file: {result['backup_path']}")
                else:
                    print(f"❌ Backup failed: {result.get('error', 'Unknown error')}")

        except ImportError:
            if HAS_RICH and console:
                console.print("[red]❌ Backup manager not available[/red]")
            else:
                print("❌ Backup manager not available")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]❌ Error creating backup: {e}[/red]")
            else:
                print(f"❌ Error creating backup: {e}")

    def _restore_from_backup(self):
        """Restore from backup."""
        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self.developer_tools)

            if HAS_RICH and console:
                console.print("\n[bold cyan]🔄 Restore from Backup[/bold cyan]")

                # List available backups
                backups = backup_manager.list_backups()
                if not backups:
                    console.print("[yellow]⚠️ No backups found[/yellow]")
                    return

                console.print("[cyan]Available backups:[/cyan]")
                for i, backup in enumerate(backups, 1):
                    backup_type = backup.get('type', 'Unknown')
                    created = backup.get('created', 'Unknown')
                    size = backup.get('size_mb', 0)
                    console.print(f"  {i}. [{backup_type}] {backup['filename']} ({size:.2f} MB) - {created}")

                choice = Prompt.ask("Select backup to restore", choices=[str(i) for i in range(1, len(backups) + 1)])
                selected_backup = backups[int(choice) - 1]

                # Confirm restore
                console.print(f"\n[yellow]⚠️ This will restore from: {selected_backup['filename']}[/yellow]")
                console.print("[yellow]⚠️ Current data may be overwritten![/yellow]")

                if not Prompt.ask("Continue with restore?", choices=["y", "n"], default="n") == "y":
                    console.print("[yellow]Restore cancelled[/yellow]")
                    return

                # Get decryption key if needed
                encryption_key = None
                if selected_backup.get('encrypted'):
                    encryption_key = Prompt.ask("Enter decryption password", password=True)

                with console.status("[bold green]Restoring from backup..."):
                    result = backup_manager.restore_backup(
                        backup_path=selected_backup['path'],
                        encryption_key=encryption_key
                    )

                if result.get('success'):
                    console.print(f"[green]✅ Restore completed successfully[/green]")
                    console.print(f"[cyan]📦 Restored components: {', '.join(result.get('restored_components', []))}[/cyan]")
                    if result.get('warnings'):
                        console.print(f"[yellow]⚠️ Warnings: {', '.join(result['warnings'])}[/yellow]")
                else:
                    console.print(f"[red]❌ Restore failed: {result.get('error', 'Unknown error')}[/red]")
            else:
                print("\n🔄 Restore from Backup")
                print("🚧 Feature under development - Restore from backup")

        except ImportError:
            if HAS_RICH and console:
                console.print("[red]❌ Backup manager not available[/red]")
            else:
                print("❌ Backup manager not available")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]❌ Error restoring backup: {e}[/red]")
            else:
                print(f"❌ Error restoring backup: {e}")

    def _list_backups(self):
        """List available backups."""
        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self.developer_tools)

            if HAS_RICH and console:
                console.print("\n[bold cyan]📋 Available Backups[/bold cyan]")

                backups = backup_manager.list_backups()
                if not backups:
                    console.print("[yellow]⚠️ No backups found[/yellow]")
                    return

                # Create table
                table = Table(title="Backup Files")
                table.add_column("Type", style="cyan")
                table.add_column("Filename", style="white")
                table.add_column("Size", style="green")
                table.add_column("Created", style="yellow")
                table.add_column("Encrypted", style="red")
                table.add_column("Status", style="blue")

                for backup in backups:
                    backup_type = backup.get('type', 'Unknown')
                    filename = backup.get('filename', 'Unknown')
                    size = f"{backup.get('size_mb', 0):.2f} MB"
                    created = backup.get('created', 'Unknown')
                    encrypted = "Yes" if backup.get('encrypted') else "No"
                    status = backup.get('status', 'Unknown')

                    table.add_row(backup_type, filename, size, created, encrypted, status)

                console.print(table)

                # Show summary
                total_backups = len(backups)
                total_size = sum(backup.get('size_mb', 0) for backup in backups)
                encrypted_count = sum(1 for backup in backups if backup.get('encrypted'))

                console.print(f"\n[cyan]📊 Summary:[/cyan]")
                console.print(f"  Total backups: {total_backups}")
                console.print(f"  Total size: {total_size:.2f} MB")
                console.print(f"  Encrypted backups: {encrypted_count}")
            else:
                print("\n📋 Available Backups")
                backups = backup_manager.list_backups()
                if not backups:
                    print("⚠️ No backups found")
                    return

                for i, backup in enumerate(backups, 1):
                    print(f"{i}. {backup.get('filename', 'Unknown')} ({backup.get('size_mb', 0):.2f} MB)")

        except ImportError:
            if HAS_RICH and console:
                console.print("[red]❌ Backup manager not available[/red]")
            else:
                print("❌ Backup manager not available")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]❌ Error listing backups: {e}[/red]")
            else:
                print(f"❌ Error listing backups: {e}")

    def _manage_backup_schedule(self):
        """Manage backup schedule."""
        try:
            from apps.developer.backup_manager import BackupManager
            backup_manager = BackupManager(self.developer_tools)

            if HAS_RICH and console:
                console.print("\n[bold cyan]⏰ Backup Schedule Management[/bold cyan]")

                # Show current schedule status
                schedule_info = backup_manager.get_schedule_info()

                if schedule_info.get('enabled'):
                    console.print(f"[green]✅ Automatic backups: Enabled[/green]")
                    console.print(f"[cyan]📅 Frequency: {schedule_info.get('frequency', 'Unknown')}[/cyan]")
                    console.print(f"[cyan]🕐 Next backup: {schedule_info.get('next_backup', 'Unknown')}[/cyan]")
                    console.print(f"[cyan]📊 Last backup: {schedule_info.get('last_backup', 'Never')}[/cyan]")
                else:
                    console.print("[yellow]⚠️ Automatic backups: Disabled[/yellow]")

                console.print("\n[cyan]Schedule Options:[/cyan]")
                console.print("1. Enable automatic backups")
                console.print("2. Disable automatic backups")
                console.print("3. Set backup frequency")
                console.print("4. Set backup time")
                console.print("5. Configure backup types")
                console.print("6. View backup history")
                console.print("7. Run backup now")
                console.print("0. Back to backup menu")

                choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7"], default="0")

                if choice == "1":
                    # Enable automatic backups
                    frequency = Prompt.ask("Backup frequency", choices=["hourly", "daily", "weekly", "monthly"], default="daily")
                    backup_time = Prompt.ask("Backup time (HH:MM)", default="02:00")
                    backup_types = Prompt.ask("Backup types (comma-separated)", default="full,user,database").split(',')

                    result = backup_manager.enable_schedule(
                        frequency=frequency,
                        backup_time=backup_time,
                        backup_types=[t.strip() for t in backup_types]
                    )

                    if result.get('success'):
                        console.print("[green]✅ Automatic backups enabled[/green]")
                    else:
                        console.print(f"[red]❌ Failed to enable: {result.get('error')}[/red]")

                elif choice == "2":
                    # Disable automatic backups
                    result = backup_manager.disable_schedule()
                    if result.get('success'):
                        console.print("[green]✅ Automatic backups disabled[/green]")
                    else:
                        console.print(f"[red]❌ Failed to disable: {result.get('error')}[/red]")

                elif choice == "3":
                    # Set backup frequency
                    current_freq = schedule_info.get('frequency', 'daily')
                    console.print(f"[cyan]Current frequency: {current_freq}[/cyan]")
                    new_frequency = Prompt.ask("New backup frequency", choices=["hourly", "daily", "weekly", "monthly"], default=current_freq)

                    result = backup_manager.set_frequency(new_frequency)
                    if result.get('success'):
                        console.print(f"[green]✅ Backup frequency set to {new_frequency}[/green]")
                    else:
                        console.print(f"[red]❌ Failed to set frequency: {result.get('error')}[/red]")

                elif choice == "4":
                    # Set backup time
                    current_time = schedule_info.get('backup_time', '02:00')
                    console.print(f"[cyan]Current backup time: {current_time}[/cyan]")
                    new_time = Prompt.ask("New backup time (HH:MM)", default=current_time)

                    result = backup_manager.set_backup_time(new_time)
                    if result.get('success'):
                        console.print(f"[green]✅ Backup time set to {new_time}[/green]")
                    else:
                        console.print(f"[red]❌ Failed to set time: {result.get('error')}[/red]")

                elif choice == "5":
                    # Configure backup types
                    current_types = schedule_info.get('backup_types', ['full'])
                    console.print(f"[cyan]Current backup types: {', '.join(current_types)}[/cyan]")

                    console.print("\n[cyan]Available backup types:[/cyan]")
                    console.print("- full: Complete system backup")
                    console.print("- user: User data only")
                    console.print("- database: Database only")
                    console.print("- config: Configuration files only")

                    new_types = Prompt.ask("Backup types (comma-separated)", default=','.join(current_types)).split(',')

                    result = backup_manager.set_backup_types([t.strip() for t in new_types])
                    if result.get('success'):
                        console.print(f"[green]✅ Backup types updated[/green]")
                    else:
                        console.print(f"[red]❌ Failed to update types: {result.get('error')}[/red]")

                elif choice == "6":
                    # View backup history
                    history = backup_manager.get_backup_history()

                    if history:
                        table = Table(title="Backup History")
                        table.add_column("Date", style="cyan")
                        table.add_column("Type", style="green")
                        table.add_column("Status", style="yellow")
                        table.add_column("Size", style="blue")
                        table.add_column("Duration", style="magenta")

                        for entry in history[-20:]:  # Last 20 entries
                            table.add_row(
                                entry.get('date', 'Unknown'),
                                entry.get('type', 'Unknown'),
                                entry.get('status', 'Unknown'),
                                f"{entry.get('size_mb', 0):.2f} MB",
                                entry.get('duration', 'Unknown')
                            )

                        console.print(table)
                    else:
                        console.print("[yellow]⚠️ No backup history found[/yellow]")

                elif choice == "7":
                    # Run backup now
                    backup_type = Prompt.ask("Backup type", choices=["full", "user", "database"], default="full")

                    with console.status(f"[bold green]Running {backup_type} backup..."):
                        if backup_type == "full":
                            result = backup_manager.create_full_backup()
                        elif backup_type == "user":
                            result = backup_manager.create_user_backup()
                        else:
                            result = backup_manager.create_database_backup()

                    if result.get('success'):
                        console.print(f"[green]✅ {backup_type.title()} backup completed[/green]")
                        console.print(f"[cyan]📁 File: {result.get('backup_path', 'Unknown')}[/cyan]")
                    else:
                        console.print(f"[red]❌ Backup failed: {result.get('error')}[/red]")
            else:
                print("\n⏰ Backup Schedule Management")
                print("Getting schedule information...")

                schedule_info = backup_manager.get_schedule_info()

                if schedule_info.get('enabled'):
                    print("✅ Automatic backups: Enabled")
                    print(f"📅 Frequency: {schedule_info.get('frequency', 'Unknown')}")
                    print(f"🕐 Next backup: {schedule_info.get('next_backup', 'Unknown')}")
                else:
                    print("⚠️ Automatic backups: Disabled")

                print("\nSchedule Options:")
                print("1. Enable automatic backups")
                print("2. Disable automatic backups")
                print("3. View backup history")
                print("0. Back to backup menu")

                choice = input("Select option (0-3): ").strip()

                if choice == "1":
                    frequency = input("Backup frequency (daily/weekly/monthly) [daily]: ").strip() or "daily"
                    result = backup_manager.enable_schedule(frequency=frequency)
                    if result.get('success'):
                        print("✅ Automatic backups enabled")
                    else:
                        print(f"❌ Failed to enable: {result.get('error')}")

                elif choice == "2":
                    result = backup_manager.disable_schedule()
                    if result.get('success'):
                        print("✅ Automatic backups disabled")
                    else:
                        print(f"❌ Failed to disable: {result.get('error')}")

                elif choice == "3":
                    history = backup_manager.get_backup_history()
                    if history:
                        print("\nBackup History:")
                        for i, entry in enumerate(history[-10:], 1):
                            print(f"{i}. {entry.get('date', 'Unknown')} - {entry.get('type', 'Unknown')} - {entry.get('status', 'Unknown')}")
                    else:
                        print("⚠️ No backup history found")

        except ImportError:
            if HAS_RICH and console:
                console.print("[red]❌ Backup manager not available[/red]")
            else:
                print("❌ Backup manager not available")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]❌ Error managing schedule: {e}[/red]")
            else:
                print(f"❌ Error managing schedule: {e}")

    def _export_health_report(self):
        """Export health report to file."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 Export Health Report[/bold cyan]")

            # Get export format choice
            format_choice = Prompt.ask(
                "Select export format",
                choices=["json", "csv", "txt"],
                default="json"
            )

            # Get filename
            default_filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_choice}"
            filename = Prompt.ask("Enter filename", default=default_filename)

            with console.status("[bold green]Generating health report..."):
                # Get comprehensive health data
                health_data = self.developer_tools.get_system_health()
                performance_data = self.developer_tools.get_performance_metrics('all')

                # Combine data for export
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'health_status': health_data,
                    'performance_metrics': performance_data,
                    'export_format': format_choice
                }

                # Export based on format
                try:
                    export_path = os.path.join('exports', filename)
                    os.makedirs('exports', exist_ok=True)

                    if format_choice == 'json':
                        with open(export_path, 'w') as f:
                            json.dump(export_data, f, indent=2, default=str)
                    elif format_choice == 'csv':
                        self._export_health_csv(export_data, export_path)
                    else:  # txt
                        self._export_health_txt(export_data, export_path)

                    file_size = os.path.getsize(export_path)
                    console.print(f"[green]✅ Health report exported successfully[/green]")
                    console.print(f"[cyan]📁 File: {export_path}[/cyan]")
                    console.print(f"[cyan]📊 Size: {file_size:,} bytes[/cyan]")

                except Exception as e:
                    console.print(f"[red]❌ Export failed: {e}[/red]")
        else:
            print("\n📊 Export Health Report")
            print("Generating health report...")

            # Get health data
            health_data = self.developer_tools.get_system_health()

            # Simple text export
            filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(filename, 'w') as f:
                    f.write(f"EcoCycle System Health Report\n")
                    f.write(f"Generated: {datetime.now().isoformat()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Overall Status: {health_data.get('overall_status', 'unknown')}\n\n")

                    components = health_data.get('components', {})
                    for component, status in components.items():
                        f.write(f"{component.title()}: {status.get('status', 'unknown')}\n")

                print(f"✅ Health report exported to: {filename}")
            except Exception as e:
                print(f"❌ Export failed: {e}")

    def _display_diagnostics_results_dev(self, diagnostics: Dict[str, Any]) -> None:
        """Display diagnostics results for developer tools."""
        if diagnostics.get('status') == 'error':
            if HAS_RICH and console:
                console.print(f"[red]❌ Diagnostics Error: {diagnostics.get('error', 'Unknown error')}[/red]")
            else:
                print(f"❌ Diagnostics Error: {diagnostics.get('error', 'Unknown error')}")
            return

        # System health overview
        health = diagnostics.get('system_health', 'unknown')
        issues_count = len(diagnostics.get('issues_found', []))

        if HAS_RICH and console:
            health_colors = {
                'excellent': 'green',
                'good': 'green',
                'fair': 'yellow',
                'poor': 'red',
                'critical': 'red'
            }
            health_color = health_colors.get(health, 'white')

            console.print(f"\n[{health_color}]🏥 System Health: {health.upper()}[/{health_color}]")
            console.print(f"📊 Issues Found: {issues_count}")
        else:
            print(f"\n🏥 System Health: {health.upper()}")
            print(f"📊 Issues Found: {issues_count}")

        # Show issues if any
        issues = diagnostics.get('issues_found', [])
        if issues:
            if HAS_RICH and console:
                console.print("\n[red]🚨 Issues Found:[/red]")
                for i, issue in enumerate(issues[:10], 1):
                    console.print(f"  {i}. {issue}")
                if len(issues) > 10:
                    console.print(f"  ... and {len(issues) - 10} more issues")
            else:
                print("\n🚨 Issues Found:")
                for i, issue in enumerate(issues[:10], 1):
                    print(f"  {i}. {issue}")
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more issues")
        else:
            if HAS_RICH and console:
                console.print("\n[green]✅ No issues found! System is healthy.[/green]")
            else:
                print("\n✅ No issues found! System is healthy.")

        # Show check summary
        checks = diagnostics.get('checks_performed', [])
        if HAS_RICH and console:
            console.print(f"\n[cyan]📋 Checks Performed: {len(checks)}[/cyan]")
            for check in checks:
                check_data = diagnostics.get(check, {})
                status = check_data.get('status', 'unknown')
                check_issues = len(check_data.get('issues', []))

                status_icon = {
                    'healthy': '✅',
                    'issues_found': '⚠️',
                    'error': '❌'
                }.get(status, '❓')

                console.print(f"  {status_icon} {check.replace('_', ' ').title()}: {check_issues} issues")
        else:
            print(f"\n📋 Checks Performed: {len(checks)}")
            for check in checks:
                check_data = diagnostics.get(check, {})
                status = check_data.get('status', 'unknown')
                check_issues = len(check_data.get('issues', []))

                status_icon = {
                    'healthy': '✅',
                    'issues_found': '⚠️',
                    'error': '❌'
                }.get(status, '❓')

                print(f"  {status_icon} {check.replace('_', ' ').title()}: {check_issues} issues")

    def _display_repair_results_dev(self, repair_result: Dict[str, Any]) -> None:
        """Display repair results for developer tools (Rich UI)."""
        if repair_result.get('status') == 'error':
            console.print(f"[red]❌ Repair Error: {repair_result.get('error', 'Unknown error')}[/red]")
            return

        # Repair summary
        successful = len(repair_result.get('repairs_successful', []))
        failed = len(repair_result.get('repairs_failed', []))
        remaining = len(repair_result.get('issues_remaining', []))

        summary_color = "green" if failed == 0 else "yellow" if successful > 0 else "red"

        console.print(f"\n[{summary_color}]🔧 Repair Summary:[/{summary_color}]")
        console.print(f"✅ Successful: {successful}")
        console.print(f"❌ Failed: {failed}")
        console.print(f"⚠️ Remaining Issues: {remaining}")

        # Backup info
        if repair_result.get('backup_created'):
            console.print(f"\n[blue]💾 Backup created at: {repair_result.get('backup_path', 'Unknown location')}[/blue]")

        # Show details
        if repair_result.get('repairs_successful'):
            console.print("\n[green]✅ Successful Repairs:[/green]")
            for repair in repair_result['repairs_successful']:
                console.print(f"  • {repair.replace('_', ' ').title()}")

        if repair_result.get('repairs_failed'):
            console.print("\n[red]❌ Failed Repairs:[/red]")
            for repair in repair_result['repairs_failed']:
                console.print(f"  • {repair.replace('_', ' ').title()}")

        if repair_result.get('issues_remaining'):
            console.print("\n[yellow]⚠️ Remaining Issues:[/yellow]")
            for issue in repair_result['issues_remaining'][:5]:
                console.print(f"  • {issue}")
            if len(repair_result['issues_remaining']) > 5:
                console.print(f"  ... and {len(repair_result['issues_remaining']) - 5} more")

    def _display_repair_results_dev_basic(self, repair_result: Dict[str, Any]) -> None:
        """Display repair results for developer tools (Basic UI)."""
        if repair_result.get('status') == 'error':
            print(f"❌ Repair Error: {repair_result.get('error', 'Unknown error')}")
            return

        # Repair summary
        successful = len(repair_result.get('repairs_successful', []))
        failed = len(repair_result.get('repairs_failed', []))
        remaining = len(repair_result.get('issues_remaining', []))

        print(f"\n🔧 Repair Summary:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Remaining Issues: {remaining}")

        # Backup info
        if repair_result.get('backup_created'):
            print(f"\n💾 Backup created at: {repair_result.get('backup_path', 'Unknown location')}")

        # Show details
        if repair_result.get('repairs_successful'):
            print("\n✅ Successful Repairs:")
            for repair in repair_result['repairs_successful']:
                print(f"  • {repair.replace('_', ' ').title()}")

        if repair_result.get('repairs_failed'):
            print("\n❌ Failed Repairs:")
            for repair in repair_result['repairs_failed']:
                print(f"  • {repair.replace('_', ' ').title()}")

        if repair_result.get('issues_remaining'):
            print("\n⚠️ Remaining Issues:")
            for issue in repair_result['issues_remaining'][:5]:
                print(f"  • {issue}")
            if len(repair_result['issues_remaining']) > 5:
                print(f"  ... and {len(repair_result['issues_remaining']) - 5} more")

    def _display_repair_history_dev(self, history) -> None:
        """Display repair history for developer tools."""
        if not history:
            if HAS_RICH and console:
                console.print("[yellow]📋 No repair history found.[/yellow]")
            else:
                print("📋 No repair history found.")
            return

        if HAS_RICH and console:
            console.print(f"\n[cyan]📋 System Repair History ({len(history)} entries):[/cyan]")
        else:
            print(f"\n📋 System Repair History ({len(history)} entries):")

        # Show last 10 repairs
        for repair in history[-10:]:
            timestamp = repair.get('timestamp', 'Unknown')
            if timestamp != 'Unknown':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = timestamp[:16]
            else:
                date_str = 'Unknown'

            status = repair.get('status', 'unknown')
            successful = len(repair.get('repairs_successful', []))
            failed = len(repair.get('repairs_failed', []))
            remaining = len(repair.get('issues_remaining', []))

            status_icon = {
                'completed': '✅',
                'error': '❌',
                'running': '🔄'
            }.get(status, '❓')

            if HAS_RICH and console:
                console.print(f"  {status_icon} {date_str} - Success: {successful}, Failed: {failed}, Remaining: {remaining}")
            else:
                print(f"  {status_icon} {date_str} - Success: {successful}, Failed: {failed}, Remaining: {remaining}")

        # Show latest repair details
        if history:
            latest = history[-1]
            if HAS_RICH and console:
                console.print(f"\n[blue]🔍 Latest Repair:[/blue]")
                console.print(f"  Timestamp: {latest.get('timestamp', 'Unknown')}")
                console.print(f"  Backup Created: {'Yes' if latest.get('backup_created') else 'No'}")
                console.print(f"  Status: {latest.get('status', 'unknown')}")
            else:
                print(f"\n🔍 Latest Repair:")
                print(f"  Timestamp: {latest.get('timestamp', 'Unknown')}")
                print(f"  Backup Created: {'Yes' if latest.get('backup_created') else 'No'}")
                print(f"  Status: {latest.get('status', 'unknown')}")

    def _export_health_csv(self, data: Dict[str, Any], filepath: str):
        """Export health data to CSV format."""
        import csv

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow(['Timestamp', data['timestamp']])
            writer.writerow(['Overall Status', data['health_status'].get('overall_status', 'unknown')])
            writer.writerow([])

            # Components
            writer.writerow(['Component', 'Status', 'Details'])
            components = data['health_status'].get('components', {})
            for component, info in components.items():
                if isinstance(info, dict):
                    status = info.get('status', 'unknown')
                    details = ', '.join([f"{k}: {v}" for k, v in info.items() if k != 'status'])
                    writer.writerow([component, status, details])

            writer.writerow([])

            # Performance metrics summary
            writer.writerow(['Metric Type', 'Key', 'Value'])
            perf_data = data['performance_metrics']
            for metric_type, metrics in perf_data.items():
                if isinstance(metrics, dict) and 'error' not in metrics:
                    for key, value in metrics.items():
                        if not isinstance(value, dict):
                            writer.writerow([metric_type, key, str(value)])

    def _export_health_txt(self, data: Dict[str, Any], filepath: str):
        """Export health data to text format."""
        with open(filepath, 'w') as f:
            f.write("EcoCycle System Health Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {data['timestamp']}\n\n")

            # Health status
            health_data = data['health_status']
            f.write(f"Overall Status: {health_data.get('overall_status', 'unknown')}\n\n")

            # Components
            f.write("Component Status:\n")
            f.write("-" * 30 + "\n")
            components = health_data.get('components', {})
            for component, info in components.items():
                f.write(f"{component.title()}: {info.get('status', 'unknown')}\n")
                if isinstance(info, dict):
                    for key, value in info.items():
                        if key != 'status':
                            f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
                f.write("\n")

            # Alerts
            alerts = health_data.get('alerts', [])
            if alerts:
                f.write("Active Alerts:\n")
                f.write("-" * 30 + "\n")
                for alert in alerts:
                    f.write(f"• {alert}\n")
            else:
                f.write("No active alerts\n")

    def _set_health_alerts(self):
        """Configure health alert thresholds."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]⚠️ Configure Health Alerts[/bold cyan]")

            # Load current thresholds
            config_path = 'config/health_alerts.json'
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        current_thresholds = json.load(f)
                else:
                    current_thresholds = self._get_default_thresholds()
            except Exception:
                current_thresholds = self._get_default_thresholds()

            console.print("\n[bold yellow]Current Alert Thresholds:[/bold yellow]")

            # Display current thresholds
            threshold_table = Table(title="Alert Thresholds")
            threshold_table.add_column("Metric", style="cyan")
            threshold_table.add_column("Warning", style="yellow")
            threshold_table.add_column("Critical", style="red")

            for metric, values in current_thresholds.items():
                threshold_table.add_row(
                    metric.replace('_', ' ').title(),
                    f"{values['warning']}%",
                    f"{values['critical']}%"
                )

            console.print(threshold_table)

            # Ask if user wants to modify
            if Confirm.ask("\nModify alert thresholds?"):
                console.print("\n[bold]Select metric to modify:[/bold]")
                metrics = list(current_thresholds.keys())
                for i, metric in enumerate(metrics, 1):
                    console.print(f"{i}. {metric.replace('_', ' ').title()}")

                choice = Prompt.ask("Select metric", choices=[str(i) for i in range(1, len(metrics) + 1)])
                selected_metric = metrics[int(choice) - 1]

                # Get new thresholds
                current_warning = current_thresholds[selected_metric]['warning']
                current_critical = current_thresholds[selected_metric]['critical']

                new_warning = float(Prompt.ask(f"Warning threshold for {selected_metric}", default=str(current_warning)))
                new_critical = float(Prompt.ask(f"Critical threshold for {selected_metric}", default=str(current_critical)))

                # Validate thresholds
                if new_warning >= new_critical:
                    console.print("[red]❌ Warning threshold must be less than critical threshold[/red]")
                    return

                # Update thresholds
                current_thresholds[selected_metric]['warning'] = new_warning
                current_thresholds[selected_metric]['critical'] = new_critical

                # Save to file
                try:
                    os.makedirs('config', exist_ok=True)
                    with open(config_path, 'w') as f:
                        json.dump(current_thresholds, f, indent=2)

                    console.print(f"[green]✅ Alert thresholds updated for {selected_metric}[/green]")
                    console.print(f"[cyan]Warning: {new_warning}%, Critical: {new_critical}%[/cyan]")

                except Exception as e:
                    console.print(f"[red]❌ Failed to save thresholds: {e}[/red]")
        else:
            print("\n⚠️ Configure Health Alerts")
            print("Loading current alert thresholds...")

            # Load current thresholds
            config_path = 'config/health_alerts.json'
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        current_thresholds = json.load(f)
                else:
                    current_thresholds = self._get_default_thresholds()
            except Exception:
                current_thresholds = self._get_default_thresholds()

            print("\nCurrent Alert Thresholds:")
            for metric, values in current_thresholds.items():
                print(f"  {metric.replace('_', ' ').title()}: Warning {values['warning']}%, Critical {values['critical']}%")

            modify = input("\nModify alert thresholds? (y/N): ").strip().lower()
            if modify == 'y':
                print("\nAvailable metrics:")
                metrics = list(current_thresholds.keys())
                for i, metric in enumerate(metrics, 1):
                    print(f"  {i}. {metric.replace('_', ' ').title()}")

                try:
                    choice = int(input("Select metric to modify (number): ").strip())
                    if 1 <= choice <= len(metrics):
                        selected_metric = metrics[choice - 1]
                        current_warning = current_thresholds[selected_metric]['warning']
                        current_critical = current_thresholds[selected_metric]['critical']

                        print(f"\nCurrent thresholds for {selected_metric}:")
                        print(f"  Warning: {current_warning}%")
                        print(f"  Critical: {current_critical}%")

                        new_warning = float(input(f"New warning threshold [{current_warning}]: ").strip() or current_warning)
                        new_critical = float(input(f"New critical threshold [{current_critical}]: ").strip() or current_critical)

                        if new_warning >= new_critical:
                            print("❌ Warning threshold must be less than critical threshold")
                        else:
                            # Update and save
                            current_thresholds[selected_metric]['warning'] = new_warning
                            current_thresholds[selected_metric]['critical'] = new_critical

                            try:
                                os.makedirs('config', exist_ok=True)
                                with open(config_path, 'w') as f:
                                    json.dump(current_thresholds, f, indent=2)
                                print(f"✅ Alert thresholds updated for {selected_metric}")
                                print(f"Warning: {new_warning}%, Critical: {new_critical}%")
                            except Exception as e:
                                print(f"❌ Failed to save thresholds: {e}")
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Invalid input")

    def _get_default_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get default alert thresholds."""
        return {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0},
            'swap_usage': {'warning': 50.0, 'critical': 80.0}
        }

    def _view_detailed_metrics(self):
        """View detailed system metrics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 Detailed System Metrics[/bold cyan]")

            # Get comprehensive metrics
            with console.status("[bold green]Collecting detailed metrics..."):
                all_metrics = self.developer_tools.get_performance_metrics('all')

            # Create menu for different metric categories
            console.print("\n[bold yellow]Select metric category to view:[/bold yellow]")
            console.print("1. System Overview")
            console.print("2. CPU Metrics")
            console.print("3. Memory Analysis")
            console.print("4. Disk I/O")
            console.print("5. Network Statistics")
            console.print("6. Application Performance")
            console.print("7. Performance Trends")
            console.print("8. Performance Alerts")
            console.print("9. All Metrics Summary")
            console.print("0. Back to health dashboard")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], default="0")

            if choice == "1":
                self._show_system_overview(all_metrics)
            elif choice == "2":
                self._show_cpu_metrics()
            elif choice == "3":
                self._show_memory_analysis()
            elif choice == "4":
                self._show_disk_monitoring()
            elif choice == "5":
                self._show_network_stats(all_metrics)
            elif choice == "6":
                self._show_app_performance()
            elif choice == "7":
                self._show_historical_trends()
            elif choice == "8":
                self._show_performance_alerts()
            elif choice == "9":
                self._show_all_metrics_summary(all_metrics)
        else:
            print("\n📊 Detailed System Metrics")
            print("Getting comprehensive metrics...")

            all_metrics = self.developer_tools.get_performance_metrics('all')

            # Show basic summary
            print("\nSystem Overview:")
            system_metrics = all_metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                cpu_info = system_metrics.get('cpu', {})
                print(f"  CPU Usage: {cpu_info.get('usage_percent', 'N/A')}%")
                print(f"  CPU Cores: {cpu_info.get('core_count', 'N/A')}")

            memory_metrics = all_metrics.get('memory_metrics', {})
            if 'error' not in memory_metrics:
                vmem = memory_metrics.get('virtual', {})
                print(f"  Memory Usage: {vmem.get('percent', 'N/A')}%")
                print(f"  Available Memory: {vmem.get('available_gb', 'N/A')} GB")

    def _show_system_overview(self, metrics: Dict[str, Any]):
        """Show system overview metrics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]💻 System Overview[/bold cyan]")

            system_metrics = metrics.get('system_metrics', {})

            if 'error' in system_metrics:
                console.print(f"[red]Error: {system_metrics['error']}[/red]")
                return

            # System information
            system_info = system_metrics.get('system', {})
            if system_info:
                system_panel = Panel.fit(
                    f"[bold]Platform:[/bold] {system_info.get('platform', 'N/A')}\n"
                    f"[bold]Python Version:[/bold] {system_info.get('python_version', 'N/A')}\n"
                    f"[bold]Uptime:[/bold] {system_info.get('uptime_formatted', 'N/A')}\n"
                    f"[bold]Boot Time:[/bold] {system_info.get('boot_time', 'N/A')}\n"
                    f"[bold]Working Directory:[/bold] {system_info.get('working_directory', 'N/A')}",
                    title="🖥️ System Information",
                    border_style="blue"
                )
                console.print(system_panel)

            # Quick resource summary
            cpu_info = system_metrics.get('cpu', {})
            memory_metrics = metrics.get('memory_metrics', {})
            disk_metrics = metrics.get('disk_metrics', {})

            if cpu_info and memory_metrics and disk_metrics:
                vmem = memory_metrics.get('virtual', {})

                # Get primary disk usage
                disk_usage = disk_metrics.get('usage', {})
                primary_disk = None
                if disk_usage:
                    # Find root disk or first available
                    for device, info in disk_usage.items():
                        if info.get('mountpoint') == '/' or not primary_disk:
                            primary_disk = info
                            break

                resource_panel = Panel.fit(
                    f"[bold]CPU Usage:[/bold] {cpu_info.get('usage_percent', 'N/A')}%\n"
                    f"[bold]Memory Usage:[/bold] {vmem.get('percent', 'N/A')}%\n"
                    f"[bold]Disk Usage:[/bold] {primary_disk.get('percent', 'N/A') if primary_disk else 'N/A'}%\n"
                    f"[bold]Available Memory:[/bold] {vmem.get('available_gb', 'N/A')} GB\n"
                    f"[bold]Free Disk Space:[/bold] {primary_disk.get('free_gb', 'N/A') if primary_disk else 'N/A'} GB",
                    title="📊 Resource Summary",
                    border_style="green"
                )
                console.print(resource_panel)
        else:
            print("\nSystem Overview")
            print("=" * 50)

            system_metrics = metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                system_info = system_metrics.get('system', {})
                print(f"Platform: {system_info.get('platform', 'N/A')}")
                print(f"Python: {system_info.get('python_version', 'N/A')}")
                print(f"Uptime: {system_info.get('uptime_formatted', 'N/A')}")

    def _show_network_stats(self, metrics: Dict[str, Any]):
        """Show network statistics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🌐 Network Statistics[/bold cyan]")

            network_metrics = metrics.get('network_metrics', {})

            if 'error' in network_metrics:
                console.print(f"[red]Error: {network_metrics['error']}[/red]")
                return

            # Network I/O
            net_io = network_metrics.get('io', {})
            if net_io:
                io_panel = Panel.fit(
                    f"[bold]Bytes Sent:[/bold] {net_io.get('bytes_sent_mb', 'N/A')} MB\n"
                    f"[bold]Bytes Received:[/bold] {net_io.get('bytes_recv_mb', 'N/A')} MB\n"
                    f"[bold]Packets Sent:[/bold] {net_io.get('packets_sent', 'N/A'):,}\n"
                    f"[bold]Packets Received:[/bold] {net_io.get('packets_recv', 'N/A'):,}\n"
                    f"[bold]Errors In:[/bold] {net_io.get('errin', 'N/A')}\n"
                    f"[bold]Errors Out:[/bold] {net_io.get('errout', 'N/A')}\n"
                    f"[bold]Dropped In:[/bold] {net_io.get('dropin', 'N/A')}\n"
                    f"[bold]Dropped Out:[/bold] {net_io.get('dropout', 'N/A')}",
                    title="📈 Network I/O Statistics",
                    border_style="cyan"
                )
                console.print(io_panel)

            # Network interfaces
            interfaces = network_metrics.get('interfaces', {})
            if interfaces:
                interface_table = Table(title="Network Interfaces")
                interface_table.add_column("Interface", style="cyan")
                interface_table.add_column("Status", style="green")
                interface_table.add_column("Speed", style="yellow")
                interface_table.add_column("MTU", style="blue")

                for interface, info in interfaces.items():
                    if isinstance(info, dict) and 'error' not in info:
                        status = "🟢 Up" if info.get('is_up') else "🔴 Down"
                        speed = f"{info.get('speed', 'N/A')} Mbps" if info.get('speed') else "N/A"
                        mtu = str(info.get('mtu', 'N/A'))

                        interface_table.add_row(interface, status, speed, mtu)

                console.print(interface_table)
        else:
            print("\nNetwork Statistics")
            print("=" * 50)

            network_metrics = metrics.get('network_metrics', {})
            if 'error' not in network_metrics:
                net_io = network_metrics.get('io', {})
                if net_io:
                    print(f"Bytes Sent: {net_io.get('bytes_sent_mb', 'N/A')} MB")
                    print(f"Bytes Received: {net_io.get('bytes_recv_mb', 'N/A')} MB")
                    print(f"Packets Sent: {net_io.get('packets_sent', 'N/A'):,}")
                    print(f"Packets Received: {net_io.get('packets_recv', 'N/A'):,}")

    def _show_all_metrics_summary(self, metrics: Dict[str, Any]):
        """Show summary of all metrics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📋 All Metrics Summary[/bold cyan]")

            # Create a comprehensive summary table
            summary_table = Table(title="System Metrics Summary")
            summary_table.add_column("Category", style="cyan")
            summary_table.add_column("Metric", style="green")
            summary_table.add_column("Value", style="yellow")
            summary_table.add_column("Status", style="red")

            # System metrics
            system_metrics = metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                cpu_info = system_metrics.get('cpu', {})
                if cpu_info:
                    cpu_usage = cpu_info.get('usage_percent', 0)
                    cpu_status = "🔴 High" if cpu_usage > 80 else "🟡 Medium" if cpu_usage > 60 else "🟢 Normal"
                    summary_table.add_row("System", "CPU Usage", f"{cpu_usage}%", cpu_status)
                    summary_table.add_row("System", "CPU Cores", str(cpu_info.get('core_count', 'N/A')), "ℹ️ Info")

            # Memory metrics
            memory_metrics = metrics.get('memory_metrics', {})
            if 'error' not in memory_metrics:
                vmem = memory_metrics.get('virtual', {})
                if vmem:
                    mem_usage = vmem.get('percent', 0)
                    mem_status = "🔴 High" if mem_usage > 90 else "🟡 Medium" if mem_usage > 70 else "🟢 Normal"
                    summary_table.add_row("Memory", "Usage", f"{mem_usage}%", mem_status)
                    summary_table.add_row("Memory", "Available", f"{vmem.get('available_gb', 'N/A')} GB", "ℹ️ Info")

                swap = memory_metrics.get('swap', {})
                if swap:
                    swap_usage = swap.get('percent', 0)
                    swap_status = "🔴 High" if swap_usage > 50 else "🟡 Medium" if swap_usage > 20 else "🟢 Normal"
                    summary_table.add_row("Memory", "Swap Usage", f"{swap_usage}%", swap_status)

            # Disk metrics
            disk_metrics = metrics.get('disk_metrics', {})
            if 'error' not in disk_metrics:
                disk_usage = disk_metrics.get('usage', {})
                for device, info in list(disk_usage.items())[:3]:  # Show first 3 disks
                    if 'error' not in info:
                        disk_percent = info.get('percent', 0)
                        disk_status = "🔴 High" if disk_percent > 90 else "🟡 Medium" if disk_percent > 80 else "🟢 Normal"
                        summary_table.add_row("Disk", f"{device} Usage", f"{disk_percent}%", disk_status)

            # Application metrics
            app_metrics = metrics.get('application_metrics', {})
            if 'error' not in app_metrics:
                process_info = app_metrics.get('process', {})
                if process_info:
                    summary_table.add_row("Application", "Process CPU", f"{process_info.get('cpu_percent', 'N/A')}%", "ℹ️ Info")
                    summary_table.add_row("Application", "Process Memory", f"{process_info.get('memory_percent', 'N/A')}%", "ℹ️ Info")
                    summary_table.add_row("Application", "Threads", str(process_info.get('num_threads', 'N/A')), "ℹ️ Info")

            console.print(summary_table)

            # Show alerts summary
            alerts = metrics.get('alerts', {}).get('active_alerts', [])
            if alerts:
                console.print(f"\n[bold red]🚨 Active Alerts: {len(alerts)}[/bold red]")
                for alert in alerts[:5]:  # Show first 5 alerts
                    console.print(f"  • {alert.get('type', 'Unknown')}: {alert.get('message', 'No message')}")
            else:
                console.print("\n[bold green]✅ No active alerts[/bold green]")
        else:
            print("\nAll Metrics Summary")
            print("=" * 50)

            # Basic summary for non-rich mode
            system_metrics = metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                cpu_info = system_metrics.get('cpu', {})
                print(f"CPU Usage: {cpu_info.get('usage_percent', 'N/A')}%")

            memory_metrics = metrics.get('memory_metrics', {})
            if 'error' not in memory_metrics:
                vmem = memory_metrics.get('virtual', {})
                print(f"Memory Usage: {vmem.get('percent', 'N/A')}%")

            alerts = metrics.get('alerts', {}).get('active_alerts', [])
            print(f"Active Alerts: {len(alerts)}")

    # Performance monitoring placeholder methods
    def _show_realtime_dashboard(self):
        """Show real-time system dashboard."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 Real-time System Dashboard[/bold cyan]")

            # Create a live updating dashboard
            from rich.live import Live
            from rich.layout import Layout

            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main", ratio=1),
                Layout(name="footer", size=3)
            )

            layout["main"].split_row(
                Layout(name="left"),
                Layout(name="right")
            )

            def update_dashboard():
                # Get current metrics
                metrics = self.developer_tools.get_performance_metrics('all')

                # Header
                layout["header"].update(Panel.fit(
                    f"[bold]Real-time Dashboard[/bold] - Updated: {datetime.now().strftime('%H:%M:%S')}",
                    style="blue"
                ))

                # System metrics (left side)
                system_metrics = metrics.get('system_metrics', {})
                cpu_info = system_metrics.get('cpu', {})
                system_info = system_metrics.get('system', {})

                left_content = f"""[bold cyan]System Overview[/bold cyan]
[bold]CPU Usage:[/bold] {cpu_info.get('usage_percent', 'N/A')}%
[bold]CPU Cores:[/bold] {cpu_info.get('core_count', 'N/A')} physical, {cpu_info.get('logical_count', 'N/A')} logical
[bold]Uptime:[/bold] {system_info.get('uptime_formatted', 'N/A')}
[bold]Platform:[/bold] {system_info.get('platform', 'N/A')}
[bold]Python:[/bold] {system_info.get('python_version', 'N/A')}"""

                layout["left"].update(Panel(left_content, title="System", border_style="green"))

                # Memory and disk (right side)
                memory_metrics = metrics.get('memory_metrics', {})
                disk_metrics = metrics.get('disk_metrics', {})

                vmem = memory_metrics.get('virtual', {})
                disk_usage = disk_metrics.get('usage', {})

                right_content = f"""[bold cyan]Resources[/bold cyan]
[bold]Memory Usage:[/bold] {vmem.get('percent', 'N/A')}%
[bold]Memory Available:[/bold] {vmem.get('available_gb', 'N/A')} GB
[bold]Memory Used:[/bold] {vmem.get('used_gb', 'N/A')} GB
[bold]Swap Usage:[/bold] {memory_metrics.get('swap', {}).get('percent', 'N/A')}%"""

                if disk_usage:
                    for device, info in list(disk_usage.items())[:2]:  # Show first 2 disks
                        if 'error' not in info:
                            right_content += f"\n[bold]{device}:[/bold] {info.get('percent', 'N/A')}% ({info.get('free_gb', 'N/A')} GB free)"

                layout["right"].update(Panel(right_content, title="Resources", border_style="yellow"))

                # Footer with alerts
                alerts = metrics.get('alerts', {}).get('active_alerts', [])
                if alerts:
                    alert_text = f"🚨 {len(alerts)} Active Alerts: " + ", ".join([f"{a['type']}: {a['level']}" for a in alerts[:3]])
                    layout["footer"].update(Panel(alert_text, style="red"))
                else:
                    layout["footer"].update(Panel("✅ All systems normal", style="green"))

                return layout

            # Show live dashboard for 30 seconds
            try:
                with Live(update_dashboard(), refresh_per_second=2, screen=True) as live:
                    import time
                    for _ in range(60):  # 30 seconds at 2 FPS
                        time.sleep(0.5)
                        live.update(update_dashboard())
            except KeyboardInterrupt:
                console.print("\n[yellow]Dashboard stopped by user[/yellow]")

        else:
            print("\nReal-time System Dashboard")
            print("=" * 50)

            # Get current metrics
            metrics = self.developer_tools.get_performance_metrics('all')

            # Display basic metrics
            system_metrics = metrics.get('system_metrics', {})
            memory_metrics = metrics.get('memory_metrics', {})

            if 'error' not in system_metrics:
                cpu_info = system_metrics.get('cpu', {})
                print(f"CPU Usage: {cpu_info.get('usage_percent', 'N/A')}%")
                print(f"CPU Cores: {cpu_info.get('core_count', 'N/A')}")

            if 'error' not in memory_metrics:
                vmem = memory_metrics.get('virtual', {})
                print(f"Memory Usage: {vmem.get('percent', 'N/A')}%")
                print(f"Memory Available: {vmem.get('available_gb', 'N/A')} GB")

            # Show alerts
            alerts = metrics.get('alerts', {}).get('active_alerts', [])
            if alerts:
                print(f"\n🚨 {len(alerts)} Active Alerts:")
                for alert in alerts[:5]:
                    print(f"  - {alert['type']}: {alert['message']}")
            else:
                print("\n✅ All systems normal")

    def _show_memory_analysis(self):
        """Show memory usage analysis."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🧠 Memory Usage Analysis[/bold cyan]")

            with console.status("[bold green]Analyzing memory usage..."):
                memory_data = self.developer_tools.get_performance_metrics('memory')

            memory_metrics = memory_data.get('memory_metrics', {})

            if 'error' in memory_metrics:
                console.print(f"[red]Error: {memory_metrics['error']}[/red]")
                return

            # Virtual Memory Analysis
            vmem = memory_metrics.get('virtual', {})
            if vmem:
                vmem_panel = Panel.fit(
                    f"[bold]Total Memory:[/bold] {vmem.get('total_gb', 'N/A')} GB\n"
                    f"[bold]Available:[/bold] {vmem.get('available_gb', 'N/A')} GB ({vmem.get('percent', 'N/A')}% used)\n"
                    f"[bold]Used:[/bold] {vmem.get('used_gb', 'N/A')} GB\n"
                    f"[bold]Free:[/bold] {round(vmem.get('free', 0) / (1024**3), 2)} GB\n"
                    f"[bold]Cached:[/bold] {round(vmem.get('cached', 0) / (1024**3), 2) if 'cached' in vmem else 'N/A'} GB",
                    title="💾 Virtual Memory",
                    border_style="blue"
                )
                console.print(vmem_panel)

            # Swap Memory Analysis
            swap = memory_metrics.get('swap', {})
            if swap:
                swap_color = "red" if swap.get('percent', 0) > 50 else "yellow" if swap.get('percent', 0) > 20 else "green"
                swap_panel = Panel.fit(
                    f"[bold]Total Swap:[/bold] {swap.get('total_gb', 'N/A')} GB\n"
                    f"[bold]Used:[/bold] {swap.get('used_gb', 'N/A')} GB ({swap.get('percent', 'N/A')}%)\n"
                    f"[bold]Free:[/bold] {round(swap.get('free', 0) / (1024**3), 2)} GB",
                    title="🔄 Swap Memory",
                    border_style=swap_color
                )
                console.print(swap_panel)

            # Process Memory Analysis
            process_mem = memory_metrics.get('process', {})
            if process_mem:
                process_panel = Panel.fit(
                    f"[bold]RSS (Physical):[/bold] {process_mem.get('rss_mb', 'N/A')} MB\n"
                    f"[bold]VMS (Virtual):[/bold] {process_mem.get('vms_mb', 'N/A')} MB\n"
                    f"[bold]Process Usage:[/bold] {process_mem.get('percent', 'N/A')}% of system memory",
                    title="🔧 Current Process Memory",
                    border_style="cyan"
                )
                console.print(process_panel)

            # Memory Usage Recommendations
            total_percent = vmem.get('percent', 0)
            swap_percent = swap.get('percent', 0)

            recommendations = []
            if total_percent > 90:
                recommendations.append("🚨 Critical: Memory usage is very high. Consider closing applications or adding more RAM.")
            elif total_percent > 80:
                recommendations.append("⚠️ Warning: Memory usage is high. Monitor for performance issues.")
            elif total_percent > 70:
                recommendations.append("💡 Info: Memory usage is moderate. Consider optimizing if performance is affected.")
            else:
                recommendations.append("✅ Good: Memory usage is within normal range.")

            if swap_percent > 20:
                recommendations.append("🔄 Swap usage detected. This may slow down system performance.")

            if recommendations:
                rec_text = "\n".join(recommendations)
                rec_panel = Panel.fit(rec_text, title="📋 Recommendations", border_style="yellow")
                console.print(rec_panel)

        else:
            print("\nMemory Usage Analysis")
            print("=" * 50)

            memory_data = self.developer_tools.get_performance_metrics('memory')
            memory_metrics = memory_data.get('memory_metrics', {})

            if 'error' in memory_metrics:
                print(f"Error: {memory_metrics['error']}")
                return

            # Virtual Memory
            vmem = memory_metrics.get('virtual', {})
            if vmem:
                print("Virtual Memory:")
                print(f"  Total: {vmem.get('total_gb', 'N/A')} GB")
                print(f"  Available: {vmem.get('available_gb', 'N/A')} GB")
                print(f"  Used: {vmem.get('used_gb', 'N/A')} GB ({vmem.get('percent', 'N/A')}%)")

            # Swap Memory
            swap = memory_metrics.get('swap', {})
            if swap:
                print("\nSwap Memory:")
                print(f"  Total: {swap.get('total_gb', 'N/A')} GB")
                print(f"  Used: {swap.get('used_gb', 'N/A')} GB ({swap.get('percent', 'N/A')}%)")

            # Process Memory
            process_mem = memory_metrics.get('process', {})
            if process_mem:
                print("\nCurrent Process:")
                print(f"  RSS: {process_mem.get('rss_mb', 'N/A')} MB")
                print(f"  VMS: {process_mem.get('vms_mb', 'N/A')} MB")
                print(f"  Usage: {process_mem.get('percent', 'N/A')}%")

    def _show_cpu_metrics(self):
        """Show CPU performance metrics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]⚡ CPU Performance Metrics[/bold cyan]")

            with console.status("[bold green]Analyzing CPU performance..."):
                cpu_data = self.developer_tools.get_performance_metrics('cpu')

            system_metrics = cpu_data.get('system_metrics', {})

            if 'error' in system_metrics:
                console.print(f"[red]Error: {system_metrics['error']}[/red]")
                return

            cpu_info = system_metrics.get('cpu', {})
            system_info = system_metrics.get('system', {})

            # CPU Overview
            if cpu_info:
                cpu_usage = cpu_info.get('usage_percent', 0)
                cpu_color = "red" if cpu_usage > 80 else "yellow" if cpu_usage > 60 else "green"

                cpu_panel = Panel.fit(
                    f"[bold]Current Usage:[/bold] {cpu_usage}%\n"
                    f"[bold]Physical Cores:[/bold] {cpu_info.get('core_count', 'N/A')}\n"
                    f"[bold]Logical Cores:[/bold] {cpu_info.get('logical_count', 'N/A')}\n"
                    f"[bold]Context Switches:[/bold] {cpu_info.get('context_switches', 'N/A'):,}\n"
                    f"[bold]Interrupts:[/bold] {cpu_info.get('interrupts', 'N/A'):,}",
                    title="🔧 CPU Overview",
                    border_style=cpu_color
                )
                console.print(cpu_panel)

                # Per-core usage
                per_core = cpu_info.get('usage_per_core', [])
                if per_core:
                    core_table = Table(title="Per-Core CPU Usage")
                    core_table.add_column("Core", style="cyan")
                    core_table.add_column("Usage %", style="green")
                    core_table.add_column("Status", style="yellow")

                    for i, usage in enumerate(per_core):
                        status = "🔥 High" if usage > 80 else "⚠️ Medium" if usage > 60 else "✅ Normal"
                        core_table.add_row(f"Core {i}", f"{usage:.1f}%", status)

                    console.print(core_table)

                # CPU Frequency
                freq_info = cpu_info.get('frequency', {})
                if freq_info and freq_info != 'N/A':
                    freq_panel = Panel.fit(
                        f"[bold]Current:[/bold] {freq_info.get('current', 'N/A')} MHz\n"
                        f"[bold]Minimum:[/bold] {freq_info.get('min', 'N/A')} MHz\n"
                        f"[bold]Maximum:[/bold] {freq_info.get('max', 'N/A')} MHz",
                        title="📊 CPU Frequency",
                        border_style="blue"
                    )
                    console.print(freq_panel)

            # System Information
            if system_info:
                system_panel = Panel.fit(
                    f"[bold]Uptime:[/bold] {system_info.get('uptime_formatted', 'N/A')}\n"
                    f"[bold]Platform:[/bold] {system_info.get('platform', 'N/A')}\n"
                    f"[bold]Python Version:[/bold] {system_info.get('python_version', 'N/A')}\n"
                    f"[bold]Boot Time:[/bold] {system_info.get('boot_time', 'N/A')}",
                    title="💻 System Information",
                    border_style="magenta"
                )
                console.print(system_panel)

        else:
            print("\nCPU Performance Metrics")
            print("=" * 50)

            cpu_data = self.developer_tools.get_performance_metrics('cpu')
            system_metrics = cpu_data.get('system_metrics', {})

            if 'error' in system_metrics:
                print(f"Error: {system_metrics['error']}")
                return

            cpu_info = system_metrics.get('cpu', {})
            if cpu_info:
                print(f"CPU Usage: {cpu_info.get('usage_percent', 'N/A')}%")
                print(f"Physical Cores: {cpu_info.get('core_count', 'N/A')}")
                print(f"Logical Cores: {cpu_info.get('logical_count', 'N/A')}")

                per_core = cpu_info.get('usage_per_core', [])
                if per_core:
                    print("\nPer-Core Usage:")
                    for i, usage in enumerate(per_core):
                        print(f"  Core {i}: {usage:.1f}%")

    def _show_disk_monitoring(self):
        """Show disk I/O monitoring."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]💾 Disk I/O Monitoring[/bold cyan]")

            with console.status("[bold green]Analyzing disk usage..."):
                disk_data = self.developer_tools.get_performance_metrics('disk')

            disk_metrics = disk_data.get('disk_metrics', {})

            if 'error' in disk_metrics:
                console.print(f"[red]Error: {disk_metrics['error']}[/red]")
                return

            # Disk Usage Table
            disk_usage = disk_metrics.get('usage', {})
            if disk_usage:
                usage_table = Table(title="Disk Usage by Device")
                usage_table.add_column("Device", style="cyan")
                usage_table.add_column("Mount Point", style="blue")
                usage_table.add_column("File System", style="green")
                usage_table.add_column("Total", style="yellow")
                usage_table.add_column("Used", style="red")
                usage_table.add_column("Free", style="green")
                usage_table.add_column("Usage %", style="magenta")

                for device, info in disk_usage.items():
                    if 'error' not in info:
                        usage_percent = info.get('percent', 0)
                        usage_color = "🔴" if usage_percent > 90 else "🟡" if usage_percent > 80 else "🟢"

                        usage_table.add_row(
                            device,
                            info.get('mountpoint', 'N/A'),
                            info.get('fstype', 'N/A'),
                            f"{info.get('total_gb', 'N/A')} GB",
                            f"{info.get('used_gb', 'N/A')} GB",
                            f"{info.get('free_gb', 'N/A')} GB",
                            f"{usage_color} {usage_percent}%"
                        )

                console.print(usage_table)

            # Disk I/O Statistics
            disk_io = disk_metrics.get('io', {})
            if disk_io:
                io_panel = Panel.fit(
                    f"[bold]Read Operations:[/bold] {disk_io.get('read_count', 'N/A'):,}\n"
                    f"[bold]Write Operations:[/bold] {disk_io.get('write_count', 'N/A'):,}\n"
                    f"[bold]Data Read:[/bold] {disk_io.get('read_mb', 'N/A')} MB\n"
                    f"[bold]Data Written:[/bold] {disk_io.get('write_mb', 'N/A')} MB\n"
                    f"[bold]Read Time:[/bold] {disk_io.get('read_time', 'N/A')} ms\n"
                    f"[bold]Write Time:[/bold] {disk_io.get('write_time', 'N/A')} ms",
                    title="📈 I/O Statistics",
                    border_style="cyan"
                )
                console.print(io_panel)

        else:
            print("\nDisk I/O Monitoring")
            print("=" * 50)

            disk_data = self.developer_tools.get_performance_metrics('disk')
            disk_metrics = disk_data.get('disk_metrics', {})

            if 'error' in disk_metrics:
                print(f"Error: {disk_metrics['error']}")
                return

            # Disk Usage
            disk_usage = disk_metrics.get('usage', {})
            if disk_usage:
                print("Disk Usage:")
                for device, info in disk_usage.items():
                    if 'error' not in info:
                        print(f"  {device}: {info.get('used_gb', 'N/A')} GB / {info.get('total_gb', 'N/A')} GB ({info.get('percent', 'N/A')}%)")

    def _show_app_performance(self):
        """Show application performance."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🚀 Application Performance[/bold cyan]")

            with console.status("[bold green]Analyzing application performance..."):
                app_data = self.developer_tools.get_performance_metrics('application')

            app_metrics = app_data.get('application_metrics', {})

            if 'error' in app_metrics:
                console.print(f"[red]Error: {app_metrics['error']}[/red]")
                return

            # Process Information
            process_info = app_metrics.get('process', {})
            if process_info:
                process_panel = Panel.fit(
                    f"[bold]Process ID:[/bold] {process_info.get('pid', 'N/A')}\n"
                    f"[bold]Process Name:[/bold] {process_info.get('name', 'N/A')}\n"
                    f"[bold]Status:[/bold] {process_info.get('status', 'N/A')}\n"
                    f"[bold]CPU Usage:[/bold] {process_info.get('cpu_percent', 'N/A')}%\n"
                    f"[bold]Memory Usage:[/bold] {process_info.get('memory_percent', 'N/A')}%\n"
                    f"[bold]Threads:[/bold] {process_info.get('num_threads', 'N/A')}\n"
                    f"[bold]Created:[/bold] {process_info.get('create_time', 'N/A')}",
                    title="🔧 Process Information",
                    border_style="blue"
                )
                console.print(process_panel)

            # Resource Usage
            resources = app_metrics.get('resources', {})
            if resources:
                resource_panel = Panel.fit(
                    f"[bold]User Time:[/bold] {resources.get('user_time', 'N/A'):.2f}s\n"
                    f"[bold]System Time:[/bold] {resources.get('system_time', 'N/A'):.2f}s\n"
                    f"[bold]Max Memory:[/bold] {resources.get('max_memory_kb', 'N/A')} KB\n"
                    f"[bold]Page Faults (Major):[/bold] {resources.get('page_faults_major', 'N/A')}\n"
                    f"[bold]Page Faults (Minor):[/bold] {resources.get('page_faults_minor', 'N/A')}\n"
                    f"[bold]Context Switches (Vol):[/bold] {resources.get('context_switches_voluntary', 'N/A')}\n"
                    f"[bold]Context Switches (Invol):[/bold] {resources.get('context_switches_involuntary', 'N/A')}",
                    title="📊 Resource Usage",
                    border_style="green"
                )
                console.print(resource_panel)

            # Python-specific metrics
            python_info = app_metrics.get('python', {})
            if python_info:
                python_panel = Panel.fit(
                    f"[bold]Garbage Collections:[/bold] {python_info.get('garbage_collections', 'N/A')}\n"
                    f"[bold]Tracked Objects:[/bold] {python_info.get('garbage_objects', 'N/A')}\n"
                    f"[bold]Reference Cycles:[/bold] {python_info.get('reference_cycles', 'N/A')}",
                    title="🐍 Python Metrics",
                    border_style="yellow"
                )
                console.print(python_panel)

            # Threading information
            threading_info = app_metrics.get('threading', {})
            if threading_info:
                threading_panel = Panel.fit(
                    f"[bold]Active Threads:[/bold] {threading_info.get('active_threads', 'N/A')}\n"
                    f"[bold]Main Thread Alive:[/bold] {threading_info.get('main_thread_alive', 'N/A')}",
                    title="🧵 Threading",
                    border_style="cyan"
                )
                console.print(threading_panel)

        else:
            print("\nApplication Performance")
            print("=" * 50)

            app_data = self.developer_tools.get_performance_metrics('application')
            app_metrics = app_data.get('application_metrics', {})

            if 'error' in app_metrics:
                print(f"Error: {app_metrics['error']}")
                return

            # Process Information
            process_info = app_metrics.get('process', {})
            if process_info:
                print("Process Information:")
                print(f"  PID: {process_info.get('pid', 'N/A')}")
                print(f"  Name: {process_info.get('name', 'N/A')}")
                print(f"  CPU Usage: {process_info.get('cpu_percent', 'N/A')}%")
                print(f"  Memory Usage: {process_info.get('memory_percent', 'N/A')}%")

    def _show_historical_trends(self):
        """Show historical performance trends."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📈 Historical Performance Trends[/bold cyan]")

            with console.status("[bold green]Loading historical data..."):
                trends_data = self.developer_tools.get_performance_metrics('trends')

            trends = trends_data.get('trends', {})

            if 'error' in trends:
                console.print(f"[red]Error: {trends['error']}[/red]")
                return

            # Display trend information
            info_panel = Panel.fit(
                f"[bold]Data Points:[/bold] {trends.get('data_points', 'N/A')}\n"
                f"[bold]Time Period:[/bold] {trends.get('period', 'N/A')}\n"
                f"[bold]Note:[/bold] {trends.get('note', 'N/A')}",
                title="📊 Trend Information",
                border_style="blue"
            )
            console.print(info_panel)

            # CPU Trend (last few hours)
            cpu_trend = trends.get('cpu_24h', [])
            if cpu_trend:
                console.print("\n[bold yellow]CPU Usage Trend (Last 24 Hours)[/bold yellow]")

                # Show recent data points
                recent_cpu = cpu_trend[-12:]  # Last 12 hours
                cpu_table = Table(title="Recent CPU Usage")
                cpu_table.add_column("Time", style="cyan")
                cpu_table.add_column("CPU %", style="green")
                cpu_table.add_column("Status", style="yellow")

                for point in recent_cpu:
                    timestamp = point.get('timestamp', 'N/A')
                    cpu_percent = point.get('cpu_percent', 0)
                    status = "🔥 High" if cpu_percent > 80 else "⚠️ Medium" if cpu_percent > 60 else "✅ Normal"

                    # Format timestamp to show only time
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M')
                    except:
                        time_str = timestamp

                    cpu_table.add_row(time_str, f"{cpu_percent}%", status)

                console.print(cpu_table)

            # Memory Trend
            memory_trend = trends.get('memory_24h', [])
            if memory_trend:
                console.print("\n[bold green]Memory Usage Trend (Last 24 Hours)[/bold green]")

                recent_memory = memory_trend[-12:]  # Last 12 hours
                memory_table = Table(title="Recent Memory Usage")
                memory_table.add_column("Time", style="cyan")
                memory_table.add_column("Memory %", style="green")
                memory_table.add_column("Status", style="yellow")

                for point in recent_memory:
                    timestamp = point.get('timestamp', 'N/A')
                    memory_percent = point.get('memory_percent', 0)
                    status = "🔥 High" if memory_percent > 80 else "⚠️ Medium" if memory_percent > 60 else "✅ Normal"

                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M')
                    except:
                        time_str = timestamp

                    memory_table.add_row(time_str, f"{memory_percent:.1f}%", status)

                console.print(memory_table)

        else:
            print("\nHistorical Performance Trends")
            print("=" * 50)

            trends_data = self.developer_tools.get_performance_metrics('trends')
            trends = trends_data.get('trends', {})

            if 'error' in trends:
                print(f"Error: {trends['error']}")
                return

            print(f"Data Points: {trends.get('data_points', 'N/A')}")
            print(f"Period: {trends.get('period', 'N/A')}")
            print(f"Note: {trends.get('note', 'N/A')}")

    def _show_performance_alerts(self):
        """Show performance alerts."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🚨 Performance Alerts[/bold cyan]")

            with console.status("[bold green]Checking performance alerts..."):
                alerts_data = self.developer_tools.get_performance_metrics('alerts')

            alerts_info = alerts_data.get('alerts', {})

            if 'error' in alerts_info:
                console.print(f"[red]Error: {alerts_info['error']}[/red]")
                return

            active_alerts = alerts_info.get('active_alerts', [])
            thresholds = alerts_info.get('thresholds', {})

            # Display thresholds
            threshold_panel = Panel.fit(
                f"[bold]CPU Warning:[/bold] {thresholds.get('cpu_warning', 'N/A')}%\n"
                f"[bold]CPU Critical:[/bold] {thresholds.get('cpu_critical', 'N/A')}%\n"
                f"[bold]Memory Warning:[/bold] {thresholds.get('memory_warning', 'N/A')}%\n"
                f"[bold]Memory Critical:[/bold] {thresholds.get('memory_critical', 'N/A')}%\n"
                f"[bold]Disk Warning:[/bold] {thresholds.get('disk_warning', 'N/A')}%\n"
                f"[bold]Disk Critical:[/bold] {thresholds.get('disk_critical', 'N/A')}%",
                title="⚙️ Alert Thresholds",
                border_style="blue"
            )
            console.print(threshold_panel)

            # Display active alerts
            if active_alerts:
                console.print(f"\n[bold red]🚨 Active Alerts ({len(active_alerts)})[/bold red]")

                alerts_table = Table(title="Current Performance Alerts")
                alerts_table.add_column("Type", style="cyan")
                alerts_table.add_column("Level", style="red")
                alerts_table.add_column("Current Value", style="yellow")
                alerts_table.add_column("Threshold", style="green")
                alerts_table.add_column("Message", style="white")

                for alert in active_alerts:
                    level_color = "🔴" if alert.get('level') == 'CRITICAL' else "🟡"
                    alerts_table.add_row(
                        alert.get('type', 'N/A'),
                        f"{level_color} {alert.get('level', 'N/A')}",
                        f"{alert.get('value', 'N/A')}%",
                        f"{alert.get('threshold', 'N/A')}%",
                        alert.get('message', 'N/A')
                    )

                console.print(alerts_table)
            else:
                console.print("\n[bold green]✅ No Active Alerts[/bold green]")
                console.print("All performance metrics are within normal thresholds.")

            # Last check time
            last_check = alerts_info.get('last_check', 'N/A')
            console.print(f"\n[dim]Last checked: {last_check}[/dim]")

        else:
            print("\nPerformance Alerts")
            print("=" * 50)

            alerts_data = self.developer_tools.get_performance_metrics('alerts')
            alerts_info = alerts_data.get('alerts', {})

            if 'error' in alerts_info:
                print(f"Error: {alerts_info['error']}")
                return

            active_alerts = alerts_info.get('active_alerts', [])

            if active_alerts:
                print(f"Active Alerts ({len(active_alerts)}):")
                for alert in active_alerts:
                    print(f"  {alert.get('type', 'N/A')}: {alert.get('message', 'N/A')}")
            else:
                print("✅ No active alerts - all systems normal")
