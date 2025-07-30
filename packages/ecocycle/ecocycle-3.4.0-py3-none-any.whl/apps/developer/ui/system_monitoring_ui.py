"""
EcoCycle - System Monitoring UI Component
Handles system diagnostics and health dashboard functionality.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Tree, Panel

if HAS_RICH:
    from rich.prompt import Prompt


class SystemMonitoringUI(BaseUI):
    """UI component for system monitoring and diagnostics."""

    def handle_system_diagnostics(self):
        """Handle system diagnostics display."""
        if HAS_RICH and console:
            with console.status("[bold green]Running system diagnostics..."):
                diagnostics = self.developer_tools.system_diagnostics()
        else:
            print("Running system diagnostics...")
            diagnostics = self.developer_tools.system_diagnostics()

        self._display_diagnostics(diagnostics)

    def _display_diagnostics(self, diagnostics: Dict[str, Any]):
        """Display system diagnostics in a formatted way."""
        if HAS_RICH and console:
            # Create a tree structure for diagnostics
            tree = Tree("🔍 System Diagnostics")

            # Environment info
            env_tree = tree.add("🌍 Environment")
            env_tree.add(f"Python: {diagnostics.get('python_version', 'Unknown')}")
            env_tree.add(f"Platform: {diagnostics.get('platform', 'Unknown')}")
            env_tree.add(f"Working Directory: {diagnostics.get('working_directory', 'Unknown')}")

            # Database status
            db_tree = tree.add("🗄️ Database")
            db_status = diagnostics.get('database_status', {})
            if db_status.get('file_exists'):
                db_tree.add(f"✅ Database file exists ({db_status.get('file_size', 0)} bytes)")
                db_tree.add(f"Tables: {len(db_status.get('tables', []))}")

                # Table counts
                table_counts = db_status.get('table_counts', {})
                for table, count in table_counts.items():
                    db_tree.add(f"  {table}: {count} rows")
            else:
                db_tree.add("❌ Database file not found")

            # File system
            fs_tree = tree.add("📁 File System")
            file_system = diagnostics.get('file_system', {})
            for path, info in file_system.items():
                if info.get('exists'):
                    status = "✅" if info.get('is_directory') else "📄"
                    fs_tree.add(f"{status} {path}")
                else:
                    fs_tree.add(f"❌ {path} (missing)")

            # Log files
            logs_tree = tree.add("📋 Log Files")
            log_files = diagnostics.get('log_files', {})
            for log_file, info in log_files.items():
                if 'error' not in info:
                    logs_tree.add(f"📄 {log_file} ({info.get('line_count', 0)} lines)")
                    if info.get('recent_errors'):
                        error_tree = logs_tree.add(f"⚠️ Recent errors in {log_file}")
                        for error in info['recent_errors'][-3:]:  # Show last 3 errors
                            error_tree.add(f"  {error[:80]}...")
                else:
                    logs_tree.add(f"❌ {log_file} (error: {info['error']})")

            console.print(tree)
        else:
            # Plain text display
            print("\n" + "=" * 60)
            print("SYSTEM DIAGNOSTICS")
            print("=" * 60)

            print(f"\nEnvironment:")
            print(f"  Python: {diagnostics.get('python_version', 'Unknown')}")
            print(f"  Platform: {diagnostics.get('platform', 'Unknown')}")
            print(f"  Working Directory: {diagnostics.get('working_directory', 'Unknown')}")

            print(f"\nDatabase Status:")
            db_status = diagnostics.get('database_status', {})
            if db_status.get('file_exists'):
                print(f"  ✅ Database file exists ({db_status.get('file_size', 0)} bytes)")
                print(f"  Tables: {len(db_status.get('tables', []))}")
                table_counts = db_status.get('table_counts', {})
                for table, count in table_counts.items():
                    print(f"    {table}: {count} rows")
            else:
                print("  ❌ Database file not found")

            print(f"\nFile System:")
            file_system = diagnostics.get('file_system', {})
            for path, info in file_system.items():
                status = "✅" if info.get('exists') else "❌"
                print(f"  {status} {path}")

            print(f"\nLog Files:")
            log_files = diagnostics.get('log_files', {})
            for log_file, info in log_files.items():
                if 'error' not in info:
                    print(f"  📄 {log_file} ({info.get('line_count', 0)} lines)")
                    if info.get('recent_errors'):
                        print(f"    ⚠️ Recent errors: {len(info['recent_errors'])}")
                else:
                    print(f"  ❌ {log_file} (error: {info['error']})")

    def handle_system_health_dashboard(self):
        """Handle system health dashboard interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 System Health Dashboard[/bold cyan]")

            with console.status("[bold green]Loading system health data..."):
                health_data = self.developer_tools.get_system_health()

            self._display_system_health(health_data)

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
            self._display_system_health(health_data)

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

    def _display_system_health(self, health_data: Dict[str, Any]):
        """Display system health dashboard."""
        if 'error' in health_data:
            self.display_error(health_data['error'])
            return

        overall_status = health_data.get('overall_status', 'unknown')
        status_color = self._get_status_color(overall_status)

        if HAS_RICH and console:
            # Overall status panel
            status_panel = Panel.fit(
                f"[bold {status_color}]{overall_status.upper()}[/bold {status_color}]\n"
                f"[dim]Last checked: {health_data.get('timestamp', 'N/A')}[/dim]",
                title="🏥 System Health Status",
                border_style=status_color
            )
            console.print(status_panel)

            # Component status
            components = health_data.get('components', {})
            if components:
                console.print("\n[bold cyan]Component Status:[/bold cyan]")
                for component, status_info in components.items():
                    if isinstance(status_info, dict):
                        status = status_info.get('status', 'unknown')
                        comp_color = self._get_status_color(status)
                        console.print(f"  {component}: [{comp_color}]{status}[/{comp_color}]")
                        # Show additional details if available
                        for key, value in status_info.items():
                            if key != 'status' and key != 'error':
                                console.print(f"    {key.replace('_', ' ').title()}: {value}")
                    else:
                        comp_color = self._get_status_color(status_info)
                        console.print(f"  {component}: [{comp_color}]{status_info}[/{comp_color}]")

            # Metrics summary
            metrics = health_data.get('metrics', {})
            if metrics:
                console.print("\n[bold cyan]Key Metrics:[/bold cyan]")
                for metric, value in metrics.items():
                    console.print(f"  {metric}: {value}")

        else:
            print(f"\nSystem Health Status: {overall_status.upper()}")
            print(f"Last checked: {health_data.get('timestamp', 'N/A')}")

            components = health_data.get('components', {})
            if components:
                print("\nComponent Status:")
                for component, status_info in components.items():
                    if isinstance(status_info, dict):
                        status = status_info.get('status', 'unknown')
                        print(f"  {component}: {status}")
                        # Show additional details if available
                        for key, value in status_info.items():
                            if key != 'status' and key != 'error':
                                print(f"    {key.replace('_', ' ').title()}: {value}")
                    else:
                        print(f"  {component}: {status_info}")

            metrics = health_data.get('metrics', {})
            if metrics:
                print("\nKey Metrics:")
                for metric, value in metrics.items():
                    print(f"  {metric}: {value}")

    def _get_status_color(self, status: str) -> str:
        """Get color for status display."""
        status_colors = {
            'healthy': 'green',
            'warning': 'yellow',
            'critical': 'red',
            'unknown': 'dim'
        }
        # Handle case where status might be a dict or other type
        if isinstance(status, dict):
            status = status.get('status', 'unknown')
        elif not isinstance(status, str):
            status = str(status)
        return status_colors.get(status.lower(), 'dim')

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

            # Get health data
            with console.status("[bold green]Generating health report..."):
                health_data = self.developer_tools.get_system_health()

            # Prepare export data
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'health_status': health_data,
                'export_format': format_choice
            }

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"health_report_{timestamp}.{format_choice}"

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
                        if isinstance(status, dict):
                            f.write(f"{component.title()}: {status.get('status', 'unknown')}\n")
                        else:
                            f.write(f"{component.title()}: {status}\n")

                print(f"✅ Health report exported to: {filename}")
            except Exception as e:
                print(f"❌ Export failed: {e}")

    def _export_health_csv(self, data: Dict[str, Any], filepath: str):
        """Export health data to CSV format."""
        import csv

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow(['Component', 'Status', 'Details'])

            # Health data
            health_data = data['health_status']
            components = health_data.get('components', {})

            for component, info in components.items():
                if isinstance(info, dict):
                    status = info.get('status', 'unknown')
                    details = ', '.join([f"{k}: {v}" for k, v in info.items() if k != 'status'])
                    writer.writerow([component, status, details])
                else:
                    writer.writerow([component, str(info), ''])

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
                if isinstance(info, dict):
                    f.write(f"{component.title()}: {info.get('status', 'unknown')}\n")
                    for key, value in info.items():
                        if key != 'status':
                            f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
                else:
                    f.write(f"{component.title()}: {info}\n")
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
            try:
                config_path = 'config/health_alerts.json'
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        current_thresholds = json.load(f)
                else:
                    current_thresholds = self._get_default_thresholds()
            except Exception:
                current_thresholds = self._get_default_thresholds()

            console.print("\n[bold yellow]Current Alert Thresholds:[/bold yellow]")
            for metric, thresholds in current_thresholds.items():
                console.print(f"  {metric.replace('_', ' ').title()}:")
                console.print(f"    Warning: {thresholds['warning']}%")
                console.print(f"    Critical: {thresholds['critical']}%")

            console.print("\n[bold yellow]Options:[/bold yellow]")
            console.print("1. Modify CPU usage thresholds")
            console.print("2. Modify memory usage thresholds")
            console.print("3. Modify disk usage thresholds")
            console.print("4. Reset to defaults")
            console.print("0. Back to dashboard")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"], default="0")

            if choice in ["1", "2", "3"]:
                metric_map = {"1": "cpu_usage", "2": "memory_usage", "3": "disk_usage"}
                metric = metric_map[choice]
                self._modify_threshold(metric, current_thresholds)
            elif choice == "4":
                self._reset_thresholds()
        else:
            print("\n⚠️ Configure Health Alerts")
            print("This feature requires Rich library for interactive configuration.")
            print("Current thresholds are set to default values.")

    def _get_default_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get default alert thresholds."""
        return {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0},
            'swap_usage': {'warning': 50.0, 'critical': 80.0}
        }

    def _modify_threshold(self, metric: str, current_thresholds: Dict):
        """Modify threshold for a specific metric."""
        if HAS_RICH and console:
            console.print(f"\n[bold cyan]Modify {metric.replace('_', ' ').title()} Thresholds[/bold cyan]")

            current = current_thresholds[metric]
            console.print(f"Current warning: {current['warning']}%")
            console.print(f"Current critical: {current['critical']}%")

            try:
                warning = float(Prompt.ask("New warning threshold (%)", default=str(current['warning'])))
                critical = float(Prompt.ask("New critical threshold (%)", default=str(current['critical'])))

                if warning >= critical:
                    console.print("[red]Warning threshold must be less than critical threshold[/red]")
                    return

                current_thresholds[metric]['warning'] = warning
                current_thresholds[metric]['critical'] = critical

                # Save to file
                os.makedirs('config', exist_ok=True)
                with open('config/health_alerts.json', 'w') as f:
                    json.dump(current_thresholds, f, indent=2)

                console.print("[green]✅ Thresholds updated successfully[/green]")
            except ValueError:
                console.print("[red]Invalid threshold values[/red]")

    def _reset_thresholds(self):
        """Reset thresholds to default values."""
        try:
            default_thresholds = self._get_default_thresholds()
            os.makedirs('config', exist_ok=True)
            with open('config/health_alerts.json', 'w') as f:
                json.dump(default_thresholds, f, indent=2)

            if HAS_RICH and console:
                console.print("[green]✅ Thresholds reset to defaults[/green]")
            else:
                print("✅ Thresholds reset to defaults")
        except Exception as e:
            if HAS_RICH and console:
                console.print(f"[red]❌ Failed to reset thresholds: {e}[/red]")
            else:
                print(f"❌ Failed to reset thresholds: {e}")

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
            console.print("5. Application Performance")
            console.print("6. All Metrics Summary")
            console.print("0. Back to health dashboard")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")

            if choice == "1":
                self._show_system_overview(all_metrics)
            elif choice == "2":
                self._show_cpu_metrics_detail(all_metrics)
            elif choice == "3":
                self._show_memory_analysis_detail(all_metrics)
            elif choice == "4":
                self._show_disk_monitoring_detail(all_metrics)
            elif choice == "5":
                self._show_app_performance_detail(all_metrics)
            elif choice == "6":
                self._show_all_metrics_summary(all_metrics)
        else:
            print("\n📊 Detailed System Metrics")
            print("Getting comprehensive metrics...")

            all_metrics = self.developer_tools.get_performance_metrics('all')
            self._show_all_metrics_summary(all_metrics)

    def _show_system_overview(self, metrics: Dict[str, Any]):
        """Show system overview metrics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🖥️ System Overview[/bold cyan]")

            system_metrics = metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                system_info = system_metrics.get('system', {})
                console.print(f"Platform: {system_info.get('platform', 'Unknown')}")
                console.print(f"Python Version: {system_info.get('python_version', 'Unknown')}")
                console.print(f"Uptime: {system_info.get('uptime_formatted', 'Unknown')}")

                cpu_info = system_metrics.get('cpu', {})
                console.print(f"CPU Usage: {cpu_info.get('usage_percent', 0):.1f}%")
                console.print(f"CPU Cores: {cpu_info.get('core_count', 'Unknown')}")

                memory_info = system_metrics.get('memory', {})
                console.print(f"Memory Usage: {memory_info.get('usage_percent', 0):.1f}%")
                console.print(f"Available Memory: {memory_info.get('available_gb', 0):.1f} GB")
            else:
                console.print(f"[red]Error: {system_metrics['error']}[/red]")
        else:
            print("\n🖥️ System Overview")
            system_metrics = metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                system_info = system_metrics.get('system', {})
                print(f"Platform: {system_info.get('platform', 'Unknown')}")
                print(f"Python Version: {system_info.get('python_version', 'Unknown')}")
                print(f"Uptime: {system_info.get('uptime_formatted', 'Unknown')}")
            else:
                print(f"Error: {system_metrics['error']}")

    def _show_cpu_metrics_detail(self, metrics: Dict[str, Any]):
        """Show detailed CPU metrics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🔧 CPU Metrics[/bold cyan]")

            system_metrics = metrics.get('system_metrics', {})
            cpu_info = system_metrics.get('cpu', {})

            if cpu_info:
                console.print(f"Usage: {cpu_info.get('usage_percent', 0):.1f}%")
                console.print(f"Core Count: {cpu_info.get('core_count', 'Unknown')}")
                console.print(f"Frequency: {cpu_info.get('frequency_mhz', 'Unknown')} MHz")
            else:
                console.print("[yellow]No CPU metrics available[/yellow]")
        else:
            print("\n🔧 CPU Metrics")
            system_metrics = metrics.get('system_metrics', {})
            cpu_info = system_metrics.get('cpu', {})
            if cpu_info:
                print(f"Usage: {cpu_info.get('usage_percent', 0):.1f}%")
                print(f"Core Count: {cpu_info.get('core_count', 'Unknown')}")

    def _show_memory_analysis_detail(self, metrics: Dict[str, Any]):
        """Show detailed memory analysis."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]💾 Memory Analysis[/bold cyan]")

            system_metrics = metrics.get('system_metrics', {})
            memory_info = system_metrics.get('memory', {})

            if memory_info:
                console.print(f"Usage: {memory_info.get('usage_percent', 0):.1f}%")
                console.print(f"Total: {memory_info.get('total_gb', 0):.1f} GB")
                console.print(f"Available: {memory_info.get('available_gb', 0):.1f} GB")
                console.print(f"Used: {memory_info.get('used_gb', 0):.1f} GB")
            else:
                console.print("[yellow]No memory metrics available[/yellow]")
        else:
            print("\n💾 Memory Analysis")
            system_metrics = metrics.get('system_metrics', {})
            memory_info = system_metrics.get('memory', {})
            if memory_info:
                print(f"Usage: {memory_info.get('usage_percent', 0):.1f}%")
                print(f"Total: {memory_info.get('total_gb', 0):.1f} GB")

    def _show_disk_monitoring_detail(self, metrics: Dict[str, Any]):
        """Show detailed disk monitoring."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]💽 Disk Monitoring[/bold cyan]")

            system_metrics = metrics.get('system_metrics', {})
            disk_info = system_metrics.get('disk', {})

            if disk_info:
                console.print(f"Usage: {disk_info.get('usage_percent', 0):.1f}%")
                console.print(f"Total: {disk_info.get('total_gb', 0):.1f} GB")
                console.print(f"Free: {disk_info.get('free_gb', 0):.1f} GB")
            else:
                console.print("[yellow]No disk metrics available[/yellow]")
        else:
            print("\n💽 Disk Monitoring")
            system_metrics = metrics.get('system_metrics', {})
            disk_info = system_metrics.get('disk', {})
            if disk_info:
                print(f"Usage: {disk_info.get('usage_percent', 0):.1f}%")
                print(f"Total: {disk_info.get('total_gb', 0):.1f} GB")

    def _show_app_performance_detail(self, metrics: Dict[str, Any]):
        """Show detailed application performance."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🚀 Application Performance[/bold cyan]")

            app_metrics = metrics.get('application_metrics', {})
            if app_metrics:
                console.print(f"Memory Usage: {app_metrics.get('memory_usage_mb', 0):.1f} MB")
                console.print(f"CPU Time: {app_metrics.get('cpu_time_seconds', 0):.2f} seconds")
                console.print(f"Thread Count: {app_metrics.get('thread_count', 'Unknown')}")
            else:
                console.print("[yellow]No application metrics available[/yellow]")
        else:
            print("\n🚀 Application Performance")
            app_metrics = metrics.get('application_metrics', {})
            if app_metrics:
                print(f"Memory Usage: {app_metrics.get('memory_usage_mb', 0):.1f} MB")
                print(f"CPU Time: {app_metrics.get('cpu_time_seconds', 0):.2f} seconds")

    def _show_all_metrics_summary(self, metrics: Dict[str, Any]):
        """Show summary of all metrics."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 All Metrics Summary[/bold cyan]")

            # System metrics
            system_metrics = metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                console.print("\n[bold yellow]System:[/bold yellow]")
                system_info = system_metrics.get('system', {})
                console.print(f"  Platform: {system_info.get('platform', 'Unknown')}")
                console.print(f"  Uptime: {system_info.get('uptime_formatted', 'Unknown')}")

                cpu_info = system_metrics.get('cpu', {})
                console.print(f"  CPU Usage: {cpu_info.get('usage_percent', 0):.1f}%")

                memory_info = system_metrics.get('memory', {})
                console.print(f"  Memory Usage: {memory_info.get('usage_percent', 0):.1f}%")

                disk_info = system_metrics.get('disk', {})
                console.print(f"  Disk Usage: {disk_info.get('usage_percent', 0):.1f}%")

            # Application metrics
            app_metrics = metrics.get('application_metrics', {})
            if app_metrics:
                console.print("\n[bold yellow]Application:[/bold yellow]")
                console.print(f"  Memory: {app_metrics.get('memory_usage_mb', 0):.1f} MB")
                console.print(f"  Threads: {app_metrics.get('thread_count', 'Unknown')}")

            # Alerts
            alerts = metrics.get('alerts', {})
            active_alerts = alerts.get('active_alerts', [])
            if active_alerts:
                console.print(f"\n[bold red]Active Alerts: {len(active_alerts)}[/bold red]")
                for alert in active_alerts[:5]:  # Show first 5 alerts
                    console.print(f"  • {alert.get('message', 'Unknown alert')}")
            else:
                console.print("\n[bold green]No active alerts[/bold green]")
        else:
            print("\n📊 All Metrics Summary")
            system_metrics = metrics.get('system_metrics', {})
            if 'error' not in system_metrics:
                print("\nSystem:")
                system_info = system_metrics.get('system', {})
                print(f"  Platform: {system_info.get('platform', 'Unknown')}")
                print(f"  Uptime: {system_info.get('uptime_formatted', 'Unknown')}")

                cpu_info = system_metrics.get('cpu', {})
                print(f"  CPU Usage: {cpu_info.get('usage_percent', 0):.1f}%")

                memory_info = system_metrics.get('memory', {})
                print(f"  Memory Usage: {memory_info.get('usage_percent', 0):.1f}%")
