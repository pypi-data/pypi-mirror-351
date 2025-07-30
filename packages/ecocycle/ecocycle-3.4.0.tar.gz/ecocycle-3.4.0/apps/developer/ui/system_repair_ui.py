"""
EcoCycle - System Repair UI Component
Handles system repair and diagnostics functionality.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Prompt, Confirm


class SystemRepairUI(BaseUI):
    """UI component for system repair and diagnostics."""

    def handle_system_repair(self):
        """Handle system repair interface."""
        try:
            from utils.system_repair import SystemRepair

            if HAS_RICH and console:
                console.print("\n[bold cyan]🔧 System Repair[/bold cyan]")
                console.print("1. Run system diagnostics")
                console.print("2. Auto-repair system issues")
                console.print("3. View repair history")
                console.print("0. Back to main menu")

                choice = Prompt.ask("Select option", choices=["0", "1", "2", "3"], default="0")
            else:
                print("\nSystem Repair")
                print("1. Run system diagnostics")
                print("2. Auto-repair system issues")
                print("3. View repair history")
                print("0. Back to main menu")

                choice = input("Select option (0-3): ").strip()

            if choice == "1":
                self._handle_diagnostics()
            elif choice == "2":
                self._handle_auto_repair()
            elif choice == "3":
                self._handle_repair_history()

        except ImportError:
            self.display_error("System repair module not available. Please check your installation.")
        except Exception as e:
            self.display_error(f"Error in system repair: {str(e)}")

    def _handle_diagnostics(self):
        """Handle system diagnostics."""
        from utils.system_repair import SystemRepair

        if HAS_RICH and console:
            console.print("\n[bold cyan]🔍 System Diagnostics Options[/bold cyan]")
            console.print("1. Standard diagnostics")
            console.print("2. AI-enhanced diagnostics (recommended)")
            console.print("0. Back")

            diag_choice = Prompt.ask("Select diagnostics type", choices=["0", "1", "2"], default="0")

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

    def _handle_auto_repair(self):
        """Handle automated system repair."""
        from utils.system_repair import SystemRepair

        if HAS_RICH and console:
            console.print("\n[bold cyan]🔧 Automated System Repair Options[/bold cyan]")
            console.print("1. Standard auto-repair")
            console.print("2. AI-enhanced auto-repair (recommended)")
            console.print("0. Back")

            repair_choice = Prompt.ask("Select repair type", choices=["0", "1", "2"], default="0")

            if repair_choice == "0":
                return

            console.print("\n[yellow]⚠️ This will automatically diagnose and repair system issues.[/yellow]")
            console.print("[yellow]⚠️ System files may be modified.[/yellow]")

            if self.confirm_action("Proceed with automated system repair?"):
                system_repair = SystemRepair()

                if repair_choice == "2":
                    self._run_ai_enhanced_repair(system_repair)
                else:
                    self._run_standard_repair(system_repair)
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

            if self.confirm_action("Proceed with automated system repair?"):
                system_repair = SystemRepair()

                if repair_choice == "2":
                    self._run_ai_enhanced_repair_basic(system_repair)
                else:
                    self._run_standard_repair_basic(system_repair)
            else:
                print("System repair cancelled.")

    def _handle_repair_history(self):
        """Handle repair history display."""
        from utils.system_repair import SystemRepair

        status = self.show_status("Loading repair history...")
        if status:
            with status:
                system_repair = SystemRepair()
                history = system_repair.get_repair_history()
        else:
            print("Loading repair history...")
            system_repair = SystemRepair()
            history = system_repair.get_repair_history()

        self._display_repair_history(history)

    def _run_ai_enhanced_repair(self, system_repair):
        """Run AI-enhanced repair with Rich UI."""
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
        ai_suggestions = {}
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
        repair_result['ai_suggestions'] = ai_suggestions

        self._display_repair_results(repair_result)

    def _run_standard_repair(self, system_repair):
        """Run standard repair with Rich UI."""
        with console.status("[yellow]Running automated system repair..."):
            repair_result = system_repair.auto_repair_system(create_backup=True)

        self._display_repair_results(repair_result)

    def _run_ai_enhanced_repair_basic(self, system_repair):
        """Run AI-enhanced repair with basic UI."""
        print("Running AI-enhanced system repair...")
        # Get diagnostics with AI
        diagnostics = system_repair.run_ai_enhanced_diagnostics()

        # Generate AI suggestions
        issues = diagnostics.get('issues_found', [])
        ai_suggestions = {}
        if issues:
            print("Generating AI repair suggestions...")
            ai_suggestions = system_repair.generate_ai_repair_suggestions(issues)

        # Run repair
        print("Applying automated repairs...")
        repair_result = system_repair.auto_repair_system(create_backup=True)

        # Add AI data
        repair_result['ai_analysis'] = diagnostics.get('ai_analysis', {})
        repair_result['ai_suggestions'] = ai_suggestions

        self._display_repair_results_basic(repair_result)

    def _run_standard_repair_basic(self, system_repair):
        """Run standard repair with basic UI."""
        print("Running automated system repair...")
        repair_result = system_repair.auto_repair_system(create_backup=True)

        self._display_repair_results_basic(repair_result)

    def _display_diagnostics_results(self, diagnostics: Dict[str, Any]):
        """Display diagnostics results."""
        if diagnostics.get('status') == 'error':
            self.display_error(f"Diagnostics Error: {diagnostics.get('error', 'Unknown error')}")
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

    def _display_repair_results(self, repair_result: Dict[str, Any]):
        """Display repair results with Rich UI."""
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
                console.print(f"  ... and {len(repair_result['issues_remaining']) - 5} more issues")

    def _display_repair_results_basic(self, repair_result: Dict[str, Any]):
        """Display repair results with basic UI."""
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
                print(f"  ... and {len(repair_result['issues_remaining']) - 5} more issues")

    def _display_repair_history(self, history: Dict[str, Any]):
        """Display repair history."""
        if 'error' in history:
            self.display_error(f"Failed to load repair history: {history['error']}")
            return

        repairs = history.get('repairs', [])
        if not repairs:
            self.display_info("No repair history found.")
            return

        if HAS_RICH and console:
            from rich.table import Table
            table = Table(title="System Repair History")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Issues Fixed", style="blue")
            table.add_column("Duration", style="magenta")

            for repair in repairs[-20:]:  # Show last 20 repairs
                table.add_row(
                    repair.get('date', 'Unknown'),
                    repair.get('type', 'Unknown'),
                    repair.get('status', 'Unknown'),
                    str(repair.get('issues_fixed', 0)),
                    repair.get('duration', 'Unknown')
                )

            console.print(table)
        else:
            print("\nSystem Repair History:")
            print("-" * 80)
            for repair in repairs[-10:]:  # Show last 10 repairs
                print(f"Date: {repair.get('date', 'Unknown')}")
                print(f"Type: {repair.get('type', 'Unknown')}")
                print(f"Status: {repair.get('status', 'Unknown')}")
                print(f"Issues Fixed: {repair.get('issues_fixed', 0)}")
                print(f"Duration: {repair.get('duration', 'Unknown')}")
                print("-" * 40)
