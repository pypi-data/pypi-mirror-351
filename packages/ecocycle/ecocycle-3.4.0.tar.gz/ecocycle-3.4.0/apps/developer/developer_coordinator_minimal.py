"""
Developer Tools Coordinator - Minimal version with lazy loading.
This module coordinates between different developer tool components using lazy imports.
"""

from typing import Optional

# Rich imports with fallbacks
try:
    from rich.console import Console
    from rich.prompt import Prompt
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

    class Prompt:
        @staticmethod
        def ask(*args, **kwargs):
            return kwargs.get('default', '')


class DeveloperCoordinatorMinimal:
    """Main coordinator for developer tools with lazy loading."""

    def __init__(self, developer_auth, developer_tools):
        """Initialize the coordinator."""
        self.developer_auth = developer_auth
        self.developer_tools = developer_tools

        # UI components will be loaded lazily
        self._ui_components = {}

    def _get_ui_component(self, component_name: str):
        """Lazy load UI components."""
        if component_name not in self._ui_components:
            try:
                if component_name == 'system_monitoring':
                    from .ui.system_monitoring_ui import SystemMonitoringUI
                    self._ui_components[component_name] = SystemMonitoringUI(self.developer_auth, self.developer_tools)
                elif component_name == 'data_management':
                    from .ui.data_management_ui import DataManagementUI
                    self._ui_components[component_name] = DataManagementUI(self.developer_auth, self.developer_tools)
                elif component_name == 'cache_management':
                    from .ui.cache_management_ui import CacheManagementUI
                    self._ui_components[component_name] = CacheManagementUI(self.developer_auth, self.developer_tools)
                elif component_name == 'email_testing':
                    from .ui.email_testing_ui import EmailTestingUI
                    self._ui_components[component_name] = EmailTestingUI(self.developer_auth, self.developer_tools)
                elif component_name == 'configuration':
                    from .ui.configuration_ui import ConfigurationUI
                    self._ui_components[component_name] = ConfigurationUI(self.developer_auth, self.developer_tools)
                elif component_name == 'export_management':
                    from .ui.export_management_ui import ExportManagementUI
                    self._ui_components[component_name] = ExportManagementUI(self.developer_auth, self.developer_tools)
                elif component_name == 'log_analysis':
                    from .ui.log_analysis_ui import LogAnalysisUI
                    self._ui_components[component_name] = LogAnalysisUI(self.developer_auth, self.developer_tools)
                elif component_name == 'session_management':
                    from .ui.session_management_ui import SessionManagementUI
                    self._ui_components[component_name] = SessionManagementUI(self.developer_auth, self.developer_tools)
                elif component_name == 'api_testing':
                    from .ui.api_testing_ui import APITestingUI
                    self._ui_components[component_name] = APITestingUI(self.developer_auth, self.developer_tools)
                elif component_name == 'security_audit':
                    from .ui.security_audit_ui import SecurityAuditUI
                    self._ui_components[component_name] = SecurityAuditUI(self.developer_auth, self.developer_tools)
                elif component_name == 'backup_restore':
                    from .ui.backup_restore_ui import BackupRestoreUI
                    self._ui_components[component_name] = BackupRestoreUI(self.developer_auth, self.developer_tools)
                elif component_name == 'performance_monitoring':
                    from .ui.performance_monitoring_ui import PerformanceMonitoringUI
                    self._ui_components[component_name] = PerformanceMonitoringUI(self.developer_auth, self.developer_tools)
                elif component_name == 'system_repair':
                    # System repair is handled directly by the coordinator
                    self._ui_components[component_name] = self
                else:
                    return None
            except ImportError as e:
                if HAS_RICH and console:
                    console.print(f"[red]Failed to load {component_name}: {e}[/red]")
                else:
                    print(f"Failed to load {component_name}: {e}")
                return None

        return self._ui_components.get(component_name)

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
        component_map = {
            "1": ("system_monitoring", "handle_system_diagnostics"),
            "2": ("performance_monitoring", "handle_performance_monitoring"),
            "3": ("log_analysis", "handle_log_analysis"),
            "4": ("system_monitoring", "handle_system_health_dashboard"),
            "5": ("data_management", "handle_database_management"),
            "6": ("data_management", "handle_user_data_management"),
            "7": ("cache_management", "handle_cache_management"),
            "8": ("export_management", "handle_export_system_data"),
            "9": ("configuration", "handle_configuration_management"),
            "10": ("email_testing", "handle_email_system_testing"),
            "11": ("api_testing", "handle_api_testing"),
            "12": ("security_audit", "handle_security_audit"),
            "13": ("session_management", "handle_session_management"),
            "14": ("backup_restore", "handle_backup_restore"),
            "15": ("system_repair", "_handle_system_repair"),
        }

        if choice in component_map:
            component_name, method_name = component_map[choice]
            component = self._get_ui_component(component_name)

            if component and hasattr(component, method_name):
                try:
                    getattr(component, method_name)()
                except Exception as e:
                    if HAS_RICH and console:
                        console.print(f"[red]Error executing {method_name}: {e}[/red]")
                    else:
                        print(f"Error executing {method_name}: {e}")
            else:
                if HAS_RICH and console:
                    console.print(f"[yellow]Component {component_name} not available[/yellow]")
                else:
                    print(f"Component {component_name} not available")

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
                # Run system diagnostics
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

                self._display_diagnostics_results(diagnostics)

            elif choice == "2":
                # Auto-repair system issues
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
                            console.print("[cyan]Running AI-enhanced system repair...[/cyan]")
                            with console.status("[yellow]Applying automated repairs..."):
                                repair_result = system_repair.auto_repair_system(create_backup=True)
                        else:
                            with console.status("[yellow]Running automated system repair..."):
                                repair_result = system_repair.auto_repair_system(create_backup=True)

                        self._display_repair_results(repair_result)
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
                            repair_result = system_repair.auto_repair_system(create_backup=True)
                        else:
                            print("Running automated system repair...")
                            repair_result = system_repair.auto_repair_system(create_backup=True)

                        self._display_repair_results(repair_result)
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

                self._display_repair_history(history)

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

    def _display_diagnostics_results(self, diagnostics):
        """Display diagnostics results."""
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

    def _display_repair_results(self, repair_result):
        """Display repair results."""
        successful = len(repair_result.get('repairs_successful', []))
        failed = len(repair_result.get('repairs_failed', []))
        remaining = len(repair_result.get('issues_remaining', []))

        if HAS_RICH and console:
            summary_color = "green" if failed == 0 else "yellow" if successful > 0 else "red"
            console.print(f"\n[{summary_color}]🔧 Repair Summary:[/{summary_color}]")
            console.print(f"✅ Successful: {successful}")
            console.print(f"❌ Failed: {failed}")
            console.print(f"⚠️ Remaining Issues: {remaining}")

            if repair_result.get('backup_created'):
                console.print(f"\n[blue]💾 Backup created at: {repair_result.get('backup_path', 'Unknown location')}[/blue]")
        else:
            print(f"\n🔧 Repair Summary:")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"⚠️ Remaining Issues: {remaining}")

            if repair_result.get('backup_created'):
                print(f"\n💾 Backup created at: {repair_result.get('backup_path', 'Unknown location')}")

    def _display_repair_history(self, history):
        """Display repair history."""
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
            console.print("\n[bold cyan]Recent Repairs:[/bold cyan]")
            for repair in repairs[-5:]:  # Show last 5 repairs
                console.print(f"• {repair.get('timestamp', 'Unknown')} - {repair.get('type', 'Unknown')} - {len(repair.get('repairs_successful', []))} fixes")
        else:
            print("\nRecent Repairs:")
            for repair in repairs[-5:]:
                print(f"• {repair.get('timestamp', 'Unknown')} - {repair.get('type', 'Unknown')} - {len(repair.get('repairs_successful', []))} fixes")

    def wait_for_user(self):
        """Wait for user input to continue."""
        if HAS_RICH and console:
            Prompt.ask("\nPress Enter to continue", default="")
        else:
            input("\nPress Enter to continue...")

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
