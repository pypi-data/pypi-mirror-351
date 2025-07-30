"""
Developer Tools Coordinator - Main entry point for developer tools.
This module coordinates between different developer tool components.
"""

from typing import Optional

# Import modular components
from .ui.system_monitoring_ui import SystemMonitoringUI
from .ui.data_management_ui import DataManagementUI
from .ui.cache_management_ui import CacheManagementUI
from .ui.email_testing_ui import EmailTestingUI
from .ui.configuration_ui import ConfigurationUI
from .ui.export_management_ui import ExportManagementUI
from .ui.log_analysis_ui import LogAnalysisUI
from .ui.session_management_ui import SessionManagementUI
from .ui.api_testing_ui import APITestingUI
from .ui.security_audit_ui import SecurityAuditUI
from .ui.backup_restore_ui import BackupRestoreUI
from .ui.performance_monitoring_ui import PerformanceMonitoringUI

# Rich imports with fallbacks
try:
    from rich.console import Console
    from rich.prompt import Prompt
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None


class DeveloperCoordinator:
    """Main coordinator for developer tools."""

    def __init__(self, developer_auth, developer_tools):
        """Initialize the coordinator with all UI components."""
        self.developer_auth = developer_auth
        self.developer_tools = developer_tools

        # Initialize all UI components
        self.system_monitoring = SystemMonitoringUI(developer_auth, developer_tools)
        self.data_management = DataManagementUI(developer_auth, developer_tools)
        self.cache_management = CacheManagementUI(developer_auth, developer_tools)
        self.email_testing = EmailTestingUI(developer_auth, developer_tools)
        self.configuration = ConfigurationUI(developer_auth, developer_tools)
        self.export_management = ExportManagementUI(developer_auth, developer_tools)
        self.log_analysis = LogAnalysisUI(developer_auth, developer_tools)
        self.session_management = SessionManagementUI(developer_auth, developer_tools)
        self.api_testing = APITestingUI(developer_auth, developer_tools)
        self.security_audit = SecurityAuditUI(developer_auth, developer_tools)
        self.backup_restore = BackupRestoreUI(developer_auth, developer_tools)
        self.performance_monitoring = PerformanceMonitoringUI(developer_auth, developer_tools)

    def show_developer_mode_indicator(self):
        """Show developer mode indicator."""
        if HAS_RICH and console:
            console.print("\n[bold red]🔧 DEVELOPER MODE ACTIVE[/bold red]")
            console.print(f"[yellow]⚠️  You have elevated system privileges[/yellow]")
            console.print(f"[cyan]Session: {self.developer_auth.get_developer_username()}[/cyan]")
            console.print("=" * 50)
        else:
            print("\n" + "=" * 50)
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
            self.system_monitoring.handle_system_health_dashboard()
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
            self._handle_system_repair()

        if choice != "0":
            self.wait_for_user()

    def _handle_system_repair(self):
        """Handle system repair interface."""
        try:
            from utils.system_repair import SystemRepair

            if HAS_RICH and console:
                console.print("\n[bold cyan]🔧 System Repair[/bold cyan]")
                console.print("1. Run system diagnostics")
                console.print("2. Auto-repair system issues")
                console.print("3. View repair history")
                console.print("0. Back to main menu")

                choice = input("Select option (0-3): ").strip()
            else:
                print("\nSystem Repair")
                print("1. Run system diagnostics")
                print("2. Auto-repair system issues")
                print("3. View repair history")
                print("0. Back to main menu")

                choice = input("Select option (0-3): ").strip()

            if choice == "1":
                # Run system diagnostics with AI analysis
                if HAS_RICH and console:
                    console.print("\n[bold cyan]🔍 System Diagnostics Options[/bold cyan]")
                    console.print("1. Standard diagnostics")
                    console.print("2. AI-enhanced diagnostics (recommended)")
                    console.print("0. Back")

                    diag_choice = input("Select diagnostics type (0-2): ").strip()

                    if diag_choice == "1":
                        with console.status("[cyan]Running comprehensive system diagnostics..."):
                            system_repair = SystemRepair()
                            diagnostics = system_repair.run_comprehensive_diagnostics()
                    elif diag_choice == "2":
                        console.print("[yellow]Running AI-enhanced diagnostics...[/yellow]")
                        system_repair = SystemRepair()
                        diagnostics = system_repair.run_ai_enhanced_diagnostics()
                    else:
                        return
                else:
                    print("\nSystem Diagnostics Options:")
                    print("1. Standard diagnostics")
                    print("2. AI-enhanced diagnostics (recommended)")
                    print("0. Back")

                    diag_choice = input("Select diagnostics type (0-2): ").strip()

                    if diag_choice == "1":
                        print("Running comprehensive system diagnostics...")
                        system_repair = SystemRepair()
                        diagnostics = system_repair.run_comprehensive_diagnostics()
                    elif diag_choice == "2":
                        print("Running AI-enhanced diagnostics...")
                        system_repair = SystemRepair()
                        diagnostics = system_repair.run_ai_enhanced_diagnostics()
                    else:
                        return

                self._display_diagnostics_results_dev(diagnostics)

            elif choice == "2":
                # Auto-repair system issues with AI suggestions
                if HAS_RICH and console:
                    console.print("\n[bold cyan]🔧 Automated System Repair Options[/bold cyan]")
                    console.print("1. Standard auto-repair")
                    console.print("2. AI-enhanced auto-repair (recommended)")
                    console.print("0. Back")

                    repair_choice = input("Select repair type (0-2): ").strip()

                    if repair_choice == "0":
                        return

                    console.print("\n[yellow]⚠️ This will automatically diagnose and repair system issues.[/yellow]")
                    console.print("[yellow]⚠️ System files may be modified.[/yellow]")

                    if self._confirm_action("Proceed with automated system repair?"):
                        system_repair = SystemRepair()

                        if repair_choice == "2":
                            # AI-enhanced repair
                            console.print("[cyan]Running AI-enhanced system repair...[/cyan]")

                            # First get diagnostics with AI analysis
                            diagnostics = system_repair.run_ai_enhanced_diagnostics()

                            # Show AI analysis if available
                            if 'ai_analysis' in diagnostics and 'error' not in diagnostics['ai_analysis']:
                                console.print("\n[bold green]🤖 AI Analysis Complete[/bold green]")
                                ai_response = diagnostics['ai_analysis'].get('ai_response', '')
                                if ai_response:
                                    # Show first few lines of AI analysis
                                    lines = ai_response.split('\n')[:5]
                                    preview = '\n'.join(lines)
                                    console.print(f"[dim]{preview}...[/dim]")

                            # Generate AI repair suggestions
                            issues = diagnostics.get('issues_found', [])
                            if issues:
                                ai_suggestions = system_repair.generate_ai_repair_suggestions(issues)

                                if 'error' not in ai_suggestions:
                                    console.print("\n[bold green]🔧 AI Repair Suggestions Generated[/bold green]")

                                    # Show immediate actions if available
                                    immediate_actions = ai_suggestions.get('structured_data', {}).get('immediate_actions', [])
                                    if immediate_actions:
                                        console.print("\n[bold yellow]Immediate Actions Recommended:[/bold yellow]")
                                        for action in immediate_actions[:3]:
                                            console.print(f"  • {action}")

                            # Run standard repair
                            with console.status("[yellow]Applying automated repairs..."):
                                repair_result = system_repair.auto_repair_system(create_backup=True)

                            # Add AI data to repair result
                            repair_result['ai_analysis'] = diagnostics.get('ai_analysis', {})
                            repair_result['ai_suggestions'] = ai_suggestions if 'ai_suggestions' in locals() else {}
                        else:
                            # Standard repair
                            with console.status("[yellow]Running automated system repair..."):
                                repair_result = system_repair.auto_repair_system(create_backup=True)

                        self._display_repair_results_dev(repair_result)
                    else:
                        console.print("[yellow]System repair cancelled.[/yellow]")
                else:
                    print("\nAutomated System Repair Options:")
                    print("1. Standard auto-repair")
                    print("2. AI-enhanced auto-repair (recommended)")
                    print("0. Back")

                    repair_choice = input("Select repair type (0-2): ").strip()

                    if repair_choice == "0":
                        return

                    print("\n⚠️ This will automatically diagnose and repair system issues.")
                    print("⚠️ System files may be modified.")

                    if self._confirm_action("Proceed with automated system repair?"):
                        system_repair = SystemRepair()

                        if repair_choice == "2":
                            print("Running AI-enhanced system repair...")
                            # Get diagnostics with AI
                            diagnostics = system_repair.run_ai_enhanced_diagnostics()

                            # Generate AI suggestions
                            issues = diagnostics.get('issues_found', [])
                            if issues:
                                print("Generating AI repair suggestions...")
                                ai_suggestions = system_repair.generate_ai_repair_suggestions(issues)

                            # Run repair
                            print("Applying automated repairs...")
                            repair_result = system_repair.auto_repair_system(create_backup=True)

                            # Add AI data
                            repair_result['ai_analysis'] = diagnostics.get('ai_analysis', {})
                            repair_result['ai_suggestions'] = ai_suggestions if 'ai_suggestions' in locals() else {}
                        else:
                            print("Running automated system repair...")
                            repair_result = system_repair.auto_repair_system(create_backup=True)

                        self._display_repair_results_dev_basic(repair_result)
                    else:
                        print("System repair cancelled.")

            elif choice == "3":
                # View repair history
                if HAS_RICH and console:
                    with console.status("[cyan]Loading repair history..."):
                        system_repair = SystemRepair()
                        history = system_repair.get_repair_history()
                else:
                    print("Loading repair history...")
                    system_repair = SystemRepair()
                    history = system_repair.get_repair_history()

                self._display_repair_history_dev(history)

        except ImportError:
            if HAS_RICH and console:
                console.print("[red]System repair module not available. Please check your installation.[/red]")
            else:
                print("System repair module not available. Please check your installation.")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]Error in system repair: {str(e)}[/red]")
            else:
                print(f"Error in system repair: {str(e)}")

    def _confirm_action(self, message: str) -> bool:
        """Get user confirmation for potentially dangerous actions."""
        if HAS_RICH and console:
            from rich.prompt import Confirm
            return Confirm.ask(f"[yellow]{message}[/yellow]")
        else:
            response = input(f"{message} (y/N): ").strip().lower()
            return response == 'y'

    def wait_for_user(self):
        """Wait for user input to continue."""
        if HAS_RICH and console:
            Prompt.ask("\nPress Enter to continue", default="")
        else:
            input("\nPress Enter to continue...")

    def _display_diagnostics_results_dev(self, diagnostics):
        """Display diagnostics results for developer tools."""
        if diagnostics.get('status') == 'error':
            if HAS_RICH and console:
                console.print(f"[red]❌ Diagnostics Error: {diagnostics.get('error', 'Unknown error')}[/red]")
            else:
                print(f"❌ Diagnostics Error: {diagnostics.get('error', 'Unknown error')}")
            return

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

    def _display_repair_results_dev(self, repair_result):
        """Display repair results for developer tools (Rich UI)."""
        if repair_result.get('status') == 'error':
            if HAS_RICH and console:
                console.print(f"[red]❌ Repair Error: {repair_result.get('error', 'Unknown error')}[/red]")
            else:
                print(f"❌ Repair Error: {repair_result.get('error', 'Unknown error')}")
            return

        # Repair summary
        successful = len(repair_result.get('repairs_successful', []))
        failed = len(repair_result.get('repairs_failed', []))
        remaining = len(repair_result.get('issues_remaining', []))

        summary_color = "green" if failed == 0 else "yellow" if successful > 0 else "red"

        if HAS_RICH and console:
            console.print(f"\n[{summary_color}]🔧 Repair Summary:[/{summary_color}]")
            console.print(f"✅ Successful: {successful}")
            console.print(f"❌ Failed: {failed}")
            console.print(f"⚠️ Remaining Issues: {remaining}")

            # Backup info
            if repair_result.get('backup_created'):
                console.print(f"\n[blue]💾 Backup created at: {repair_result.get('backup_path', 'Unknown location')}[/blue]")
        else:
            print(f"\n🔧 Repair Summary:")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"⚠️ Remaining Issues: {remaining}")

            # Backup info
            if repair_result.get('backup_created'):
                print(f"\n💾 Backup created at: {repair_result.get('backup_path', 'Unknown location')}")

    def _display_repair_results_dev_basic(self, repair_result):
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

    def _display_repair_history_dev(self, history):
        """Display repair history for developer tools."""
        if 'error' in history:
            if HAS_RICH and console:
                console.print(f"[red]Error loading repair history: {history['error']}[/red]")
            else:
                print(f"Error loading repair history: {history['error']}")
            return

        repairs = history.get('repairs', [])
        if not repairs:
            if HAS_RICH and console:
                console.print("[yellow]No repair history found[/yellow]")
            else:
                print("No repair history found")
            return

        if HAS_RICH and console:
            from rich.table import Table
            table = Table(title="Repair History")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Issues Fixed", style="blue")

            for repair in repairs[-10:]:  # Show last 10 repairs
                table.add_row(
                    repair.get('timestamp', 'Unknown'),
                    repair.get('type', 'Unknown'),
                    repair.get('status', 'Unknown'),
                    str(len(repair.get('repairs_successful', [])))
                )

            console.print(table)
        else:
            print("\nRepair History:")
            print("-" * 80)
            for repair in repairs[-10:]:
                print(f"Date: {repair.get('timestamp', 'Unknown')}")
                print(f"Type: {repair.get('type', 'Unknown')}")
                print(f"Status: {repair.get('status', 'Unknown')}")
                print(f"Issues Fixed: {len(repair.get('repairs_successful', []))}")
                print("-" * 40)

    def run(self):
        """Main run loop for developer tools."""
        try:
            while True:
                choice = self.show_developer_menu()

                if choice == "0":
                    if HAS_RICH and console:
                        console.print("\n[bold green]Exiting Developer Mode...[/bold green]")
                    else:
                        print("\nExiting Developer Mode...")
                    break

                self.handle_choice(choice)

        except KeyboardInterrupt:
            if HAS_RICH and console:
                console.print("\n\n[bold yellow]Developer mode interrupted by user[/bold yellow]")
            else:
                print("\n\nDeveloper mode interrupted by user")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"\n[bold red]Error in developer mode: {e}[/bold red]")
            else:
                print(f"\nError in developer mode: {e}")
