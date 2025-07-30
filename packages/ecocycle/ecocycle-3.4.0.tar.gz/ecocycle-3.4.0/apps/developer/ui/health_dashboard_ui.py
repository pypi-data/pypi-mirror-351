"""
EcoCycle - Health Dashboard UI Component
Handles system health dashboard and monitoring functionality.
"""
import os
import json
from typing import Dict, Any
from datetime import datetime
from .base_ui import BaseUI, HAS_RICH, console, Prompt, Confirm, Table, Panel


class HealthDashboardUI(BaseUI):
    """UI component for system health dashboard."""

    def handle_system_health_dashboard(self):
        """Handle system health dashboard interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🏥 System Health Dashboard[/bold cyan]")
            console.print("1. Refresh dashboard")
            console.print("2. Export health report")
            console.print("3. Set health alerts")
            console.print("4. View detailed metrics")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"], default="0")
        else:
            print("\n🏥 System Health Dashboard")
            print("1. Refresh dashboard")
            print("2. Export health report")
            print("3. Set health alerts")
            print("4. View detailed metrics")
            print("0. Back to main menu")

            choice = input("Select option (0-4): ").strip()

        if choice == "1":
            self._refresh_dashboard()
        elif choice == "2":
            self._export_health_report()
        elif choice == "3":
            self._set_health_alerts()
        elif choice == "4":
            self._view_detailed_metrics()

    def _refresh_dashboard(self):
        """Refresh and display the health dashboard."""
        status = self.show_status("Loading system health data...")
        if status:
            with status:
                health_data = self.developer_tools.get_system_health()
        else:
            print("Loading system health data...")
            health_data = self.developer_tools.get_system_health()

        self._display_health_dashboard(health_data)

    def _display_health_dashboard(self, health_data: Dict[str, Any]):
        """Display the health dashboard."""
        if 'error' in health_data:
            self.display_error(f"Failed to load health data: {health_data['error']}")
            return

        overall_status = health_data.get('overall_status', 'unknown')
        components = health_data.get('components', {})
        metrics = health_data.get('metrics', {})

        if HAS_RICH and console:
            # Overall status panel
            status_colors = {
                'healthy': 'green',
                'warning': 'yellow',
                'critical': 'red',
                'unknown': 'dim'
            }
            status_color = status_colors.get(overall_status, 'dim')

            status_panel = Panel.fit(
                f"[bold {status_color}]System Status: {overall_status.upper()}[/bold {status_color}]\n"
                f"[dim]Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
                title="🏥 System Health",
                border_style=status_color
            )
            console.print(status_panel)

            # Components status table
            if components:
                table = Table(title="Component Health Status")
                table.add_column("Component", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Details", style="yellow")
                table.add_column("Last Check", style="dim")

                for component, data in components.items():
                    status = data.get('status', 'unknown')
                    details = data.get('details', 'No details')
                    last_check = data.get('last_check', 'Never')

                    status_icon = {
                        'healthy': '✅',
                        'warning': '⚠️',
                        'critical': '🔴',
                        'unknown': '❓'
                    }.get(status, '❓')

                    table.add_row(
                        component.replace('_', ' ').title(),
                        f"{status_icon} {status.title()}",
                        details[:50] + "..." if len(details) > 50 else details,
                        last_check
                    )

                console.print(table)

            # Key metrics
            if metrics:
                console.print("\n[bold cyan]📊 Key Metrics[/bold cyan]")
                for metric, value in metrics.items():
                    if isinstance(value, dict):
                        current = value.get('current', 'N/A')
                        unit = value.get('unit', '')
                        console.print(f"  {metric.replace('_', ' ').title()}: {current} {unit}")
                    else:
                        console.print(f"  {metric.replace('_', ' ').title()}: {value}")

        else:
            print(f"\n🏥 System Health Dashboard")
            print(f"Overall Status: {overall_status.upper()}")
            print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 50)

            if components:
                print("\nComponent Status:")
                for component, data in components.items():
                    status = data.get('status', 'unknown')
                    details = data.get('details', 'No details')

                    status_icon = {
                        'healthy': '✅',
                        'warning': '⚠️',
                        'critical': '🔴',
                        'unknown': '❓'
                    }.get(status, '❓')

                    print(f"  {status_icon} {component.replace('_', ' ').title()}: {status}")
                    print(f"    {details}")

            if metrics:
                print("\nKey Metrics:")
                for metric, value in metrics.items():
                    if isinstance(value, dict):
                        current = value.get('current', 'N/A')
                        unit = value.get('unit', '')
                        print(f"  {metric.replace('_', ' ').title()}: {current} {unit}")
                    else:
                        print(f"  {metric.replace('_', ' ').title()}: {value}")

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

    def _export_health_csv(self, export_data: Dict[str, Any], export_path: str):
        """Export health data to CSV format."""
        import csv
        
        with open(export_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Component', 'Status', 'Details', 'Timestamp'])
            
            # Write health data
            health_status = export_data.get('health_status', {})
            components = health_status.get('components', {})
            timestamp = export_data.get('timestamp', '')
            
            for component, data in components.items():
                writer.writerow([
                    component,
                    data.get('status', 'unknown'),
                    data.get('details', ''),
                    timestamp
                ])

    def _export_health_txt(self, export_data: Dict[str, Any], export_path: str):
        """Export health data to text format."""
        with open(export_path, 'w') as f:
            f.write("EcoCycle System Health Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {export_data.get('timestamp', 'Unknown')}\n\n")
            
            health_status = export_data.get('health_status', {})
            f.write(f"Overall Status: {health_status.get('overall_status', 'unknown')}\n\n")
            
            components = health_status.get('components', {})
            f.write("Component Status:\n")
            f.write("-" * 30 + "\n")
            for component, data in components.items():
                f.write(f"{component.title()}: {data.get('status', 'unknown')}\n")
                if data.get('details'):
                    f.write(f"  Details: {data['details']}\n")
                f.write("\n")

    def _set_health_alerts(self):
        """Configure health alert thresholds."""
        config_path = 'config/health_alerts.json'

        if HAS_RICH and console:
            console.print("\n[bold cyan]⚠️ Configure Health Alerts[/bold cyan]")

            # Load current thresholds
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        current_thresholds = json.load(f)
                else:
                    current_thresholds = self._get_default_thresholds()
            except Exception:
                current_thresholds = self._get_default_thresholds()

            # Display current thresholds
            console.print("\n[cyan]Current Alert Thresholds:[/cyan]")
            for metric, values in current_thresholds.items():
                console.print(f"  {metric.replace('_', ' ').title()}: Warning {values['warning']}%, Critical {values['critical']}%")

            if Confirm.ask("\nModify alert thresholds?"):
                console.print("\n[cyan]Available metrics:[/cyan]")
                metrics = list(current_thresholds.keys())
                for i, metric in enumerate(metrics, 1):
                    console.print(f"  {i}. {metric.replace('_', ' ').title()}")

                try:
                    choice = int(Prompt.ask("Select metric to modify (number)"))
                    if 1 <= choice <= len(metrics):
                        selected_metric = metrics[choice - 1]
                        current_warning = current_thresholds[selected_metric]['warning']
                        current_critical = current_thresholds[selected_metric]['critical']

                        console.print(f"\n[cyan]Current thresholds for {selected_metric}:[/cyan]")
                        console.print(f"  Warning: {current_warning}%")
                        console.print(f"  Critical: {current_critical}%")

                        new_warning = float(Prompt.ask(f"New warning threshold", default=str(current_warning)))
                        new_critical = float(Prompt.ask(f"New critical threshold", default=str(current_critical)))

                        if new_warning >= new_critical:
                            console.print("[red]❌ Warning threshold must be less than critical threshold[/red]")
                        else:
                            # Update and save
                            current_thresholds[selected_metric]['warning'] = new_warning
                            current_thresholds[selected_metric]['critical'] = new_critical

                            try:
                                os.makedirs('config', exist_ok=True)
                                with open(config_path, 'w') as f:
                                    json.dump(current_thresholds, f, indent=2)
                                console.print(f"[green]✅ Alert thresholds updated for {selected_metric}[/green]")
                                console.print(f"[cyan]Warning: {new_warning}%, Critical: {new_critical}%[/cyan]")

                            except Exception as e:
                                console.print(f"[red]❌ Failed to save thresholds: {e}[/red]")
                    else:
                        console.print("[red]❌ Invalid selection[/red]")
                except ValueError:
                    console.print("[red]❌ Invalid input[/red]")
        else:
            print("\n⚠️ Configure Health Alerts")
            print("Loading current alert thresholds...")

            # Load current thresholds
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
            'cpu_usage': {'warning': 80.0, 'critical': 95.0},
            'memory_usage': {'warning': 85.0, 'critical': 95.0},
            'disk_usage': {'warning': 80.0, 'critical': 90.0},
            'response_time': {'warning': 2000.0, 'critical': 5000.0},
            'error_rate': {'warning': 5.0, 'critical': 10.0}
        }

    def _view_detailed_metrics(self):
        """View detailed system metrics."""
        status = self.show_status("Loading detailed metrics...")
        if status:
            with status:
                metrics = self.developer_tools.get_performance_metrics('all')
        else:
            print("Loading detailed metrics...")
            metrics = self.developer_tools.get_performance_metrics('all')

        self._display_detailed_metrics(metrics)

    def _display_detailed_metrics(self, metrics: Dict[str, Any]):
        """Display detailed system metrics."""
        if 'error' in metrics:
            self.display_error(f"Failed to load metrics: {metrics['error']}")
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 Detailed System Metrics[/bold cyan]")

            for category, data in metrics.items():
                if isinstance(data, dict) and 'metrics' in data:
                    console.print(f"\n[bold yellow]{category.replace('_', ' ').title()}[/bold yellow]")

                    category_metrics = data['metrics']
                    for metric_name, metric_value in category_metrics.items():
                        if isinstance(metric_value, dict):
                            current = metric_value.get('current', 'N/A')
                            unit = metric_value.get('unit', '')
                            trend = metric_value.get('trend', '')
                            console.print(f"  {metric_name.replace('_', ' ').title()}: {current} {unit} {trend}")
                        else:
                            console.print(f"  {metric_name.replace('_', ' ').title()}: {metric_value}")
        else:
            print("\n📊 Detailed System Metrics")
            print("-" * 50)

            for category, data in metrics.items():
                if isinstance(data, dict) and 'metrics' in data:
                    print(f"\n{category.replace('_', ' ').title()}:")

                    category_metrics = data['metrics']
                    for metric_name, metric_value in category_metrics.items():
                        if isinstance(metric_value, dict):
                            current = metric_value.get('current', 'N/A')
                            unit = metric_value.get('unit', '')
                            print(f"  {metric_name.replace('_', ' ').title()}: {current} {unit}")
                        else:
                            print(f"  {metric_name.replace('_', ' ').title()}: {metric_value}")
