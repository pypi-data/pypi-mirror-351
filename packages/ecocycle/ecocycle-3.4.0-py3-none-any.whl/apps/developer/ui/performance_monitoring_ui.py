"""
EcoCycle - Performance Monitoring UI Component
Handles performance metrics, real-time monitoring, and alerts.
"""
from typing import Dict, Any
from datetime import datetime
from .base_ui import BaseUI, HAS_RICH, console, Panel, Table, Layout, Live, Prompt


class PerformanceMonitoringUI(BaseUI):
    """UI component for performance monitoring."""

    def handle_performance_monitoring(self):
        """Handle performance monitoring interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 Performance Monitoring[/bold cyan]")
            console.print("1. Real-time system dashboard")
            console.print("2. Memory usage analysis")
            console.print("3. CPU performance metrics")
            console.print("4. Disk I/O monitoring")
            console.print("5. Application performance")
            console.print("6. Historical trends")
            console.print("7. Performance alerts")
            console.print("8. Quick system overview")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"], default="0")
        else:
            print("\nPerformance Monitoring")
            print("1. Real-time system dashboard")
            print("2. Memory usage analysis")
            print("3. CPU performance metrics")
            print("4. Disk I/O monitoring")
            print("5. Application performance")
            print("6. Historical trends")
            print("7. Performance alerts")
            print("8. Quick system overview")
            print("0. Back to main menu")

            choice = input("Select option (0-8): ").strip()

        if choice == "1":
            self._show_realtime_dashboard()
        elif choice == "2":
            self._show_memory_analysis()
        elif choice == "3":
            self._show_cpu_metrics()
        elif choice == "4":
            self._show_disk_monitoring()
        elif choice == "5":
            self._show_app_performance()
        elif choice == "6":
            self._show_historical_trends()
        elif choice == "7":
            self._show_performance_alerts()
        elif choice == "8":
            # Quick system overview (original functionality)
            if HAS_RICH and console:
                with console.status("[bold green]Collecting performance metrics..."):
                    perf_data = self.developer_tools.monitor_performance()
            else:
                print("Collecting performance metrics...")
                perf_data = self.developer_tools.monitor_performance()

            self._display_performance_metrics(perf_data)

    def _display_performance_metrics(self, perf_data: Dict[str, Any]):
        """Display performance monitoring data."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Performance Metrics[/bold cyan]")

            # System metrics
            system_metrics = perf_data.get('system_metrics', {})
            if 'error' not in system_metrics:
                system_panel = Panel.fit(
                    f"[bold]CPU Usage:[/bold] {system_metrics.get('cpu_percent', 'N/A')}%\n"
                    f"[bold]Memory Usage:[/bold] {system_metrics.get('memory_percent', 'N/A')}%\n"
                    f"[bold]Disk Usage:[/bold] {system_metrics.get('disk_usage', 'N/A')}%\n"
                    f"[bold]Load Average:[/bold] {system_metrics.get('load_average', 'N/A')}",
                    title="System Metrics"
                )
                console.print(system_panel)
            else:
                console.print(f"[red]System Metrics Error: {system_metrics['error']}[/red]")

            # Application metrics
            app_metrics = perf_data.get('application_metrics', {})
            if 'error' not in app_metrics:
                app_panel = Panel.fit(
                    f"[bold]User Time:[/bold] {app_metrics.get('user_time', 'N/A')}s\n"
                    f"[bold]System Time:[/bold] {app_metrics.get('system_time', 'N/A')}s\n"
                    f"[bold]Max Memory:[/bold] {app_metrics.get('max_memory', 'N/A')} KB\n"
                    f"[bold]Page Faults:[/bold] {app_metrics.get('page_faults', 'N/A')}",
                    title="Application Metrics"
                )
                console.print(app_panel)
            else:
                console.print(f"[red]Application Metrics Error: {app_metrics['error']}[/red]")

            # Database metrics
            db_metrics = perf_data.get('database_metrics', {})
            if 'error' not in db_metrics:
                db_panel = Panel.fit(
                    f"[bold]Database Size:[/bold] {db_metrics.get('file_size_mb', 'N/A')} MB\n"
                    f"[bold]Total Tables:[/bold] {len(db_metrics.get('table_counts', {}))}\n"
                    f"[bold]Total Records:[/bold] {sum(db_metrics.get('table_counts', {}).values())}",
                    title="Database Metrics"
                )
                console.print(db_panel)
            else:
                console.print(f"[red]Database Metrics Error: {db_metrics['error']}[/red]")

        else:
            print("\nPerformance Metrics:")
            print("=" * 50)

            # System metrics
            system_metrics = perf_data.get('system_metrics', {})
            if 'error' not in system_metrics:
                print("System Metrics:")
                print(f"  CPU Usage: {system_metrics.get('cpu_percent', 'N/A')}%")
                print(f"  Memory Usage: {system_metrics.get('memory_percent', 'N/A')}%")
                print(f"  Disk Usage: {system_metrics.get('disk_usage', 'N/A')}%")
                print(f"  Load Average: {system_metrics.get('load_average', 'N/A')}")
            else:
                print(f"System Metrics Error: {system_metrics['error']}")

            # Application metrics
            app_metrics = perf_data.get('application_metrics', {})
            if 'error' not in app_metrics:
                print("\nApplication Metrics:")
                print(f"  User Time: {app_metrics.get('user_time', 'N/A')}s")
                print(f"  System Time: {app_metrics.get('system_time', 'N/A')}s")
                print(f"  Max Memory: {app_metrics.get('max_memory', 'N/A')} KB")
                print(f"  Page Faults: {app_metrics.get('page_faults', 'N/A')}")
            else:
                print(f"Application Metrics Error: {app_metrics['error']}")

            # Database metrics
            db_metrics = perf_data.get('database_metrics', {})
            if 'error' not in db_metrics:
                print("\nDatabase Metrics:")
                print(f"  Database Size: {db_metrics.get('file_size_mb', 'N/A')} MB")
                print(f"  Total Tables: {len(db_metrics.get('table_counts', {}))}")
                print(f"  Total Records: {sum(db_metrics.get('table_counts', {}).values())}")
            else:
                print(f"Database Metrics Error: {db_metrics['error']}")

    def _show_realtime_dashboard(self):
        """Show real-time performance dashboard."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 Real-time Performance Dashboard[/bold cyan]")
            console.print("[dim]Press Ctrl+C to exit[/dim]")

            # Create layout for real-time dashboard
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main"),
                Layout(name="footer", size=3)
            )
            layout["main"].split_row(
                Layout(name="left"),
                Layout(name="right")
            )

            try:
                with Live(layout, refresh_per_second=2, screen=True):
                    while True:
                        # Get fresh metrics
                        metrics = self.developer_tools.get_performance_metrics('all')

                        # Header
                        layout["header"].update(Panel.fit(
                            f"[bold]Real-time Dashboard[/bold] - Updated: {datetime.now().strftime('%H:%M:%S')}",
                            style="blue"
                        ))

                        # System info (left side)
                        system_metrics = metrics.get('system_metrics', {})
                        cpu_info = system_metrics.get('cpu', {})
                        system_info = system_metrics.get('system', {})

                        left_content = f"""[bold]CPU Usage:[/bold] {cpu_info.get('usage_percent', 'N/A')}%
[bold]CPU Cores:[/bold] {cpu_info.get('core_count', 'N/A')} physical, {cpu_info.get('logical_count', 'N/A')} logical
[bold]Uptime:[/bold] {system_info.get('uptime_formatted', 'N/A')}
[bold]Platform:[/bold] {system_info.get('platform', 'N/A')}
[bold]Python:[/bold] {system_info.get('python_version', 'N/A')}"""

                        layout["left"].update(Panel(left_content, title="System", border_style="green"))

                        # Memory and disk (right side)
                        memory_metrics = metrics.get('memory_metrics', {})
                        vmem = memory_metrics.get('virtual', {})
                        swap = memory_metrics.get('swap', {})

                        right_content = f"""[bold]Memory Usage:[/bold] {vmem.get('percent', 'N/A')}%
[bold]Available Memory:[/bold] {vmem.get('available_gb', 'N/A')} GB
[bold]Used Memory:[/bold] {vmem.get('used_gb', 'N/A')} GB
[bold]Swap Usage:[/bold] {swap.get('percent', 'N/A')}%"""

                        # Add disk usage
                        disk_metrics = metrics.get('disk_metrics', {})
                        disk_usage = disk_metrics.get('usage', {})
                        if disk_usage:
                            right_content += "\n\n[bold]Disk Usage:[/bold]"
                            for device, info in list(disk_usage.items())[:3]:  # Show first 3 disks
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

            except KeyboardInterrupt:
                console.print("\n[yellow]Dashboard stopped by user[/yellow]")
        else:
            print("\nReal-time dashboard requires Rich library")
            print("Showing current metrics instead:")
            perf_data = self.developer_tools.monitor_performance()
            self._display_performance_metrics(perf_data)

    def _show_memory_analysis(self):
        """Show detailed memory analysis."""
        if HAS_RICH and console:
            with console.status("[bold green]Analyzing memory usage..."):
                memory_data = self.developer_tools.get_performance_metrics('memory')
        else:
            print("Analyzing memory usage...")
            memory_data = self.developer_tools.get_performance_metrics('memory')

        self._display_memory_analysis(memory_data)

    def _show_cpu_metrics(self):
        """Show CPU performance metrics."""
        if HAS_RICH and console:
            with console.status("[bold green]Collecting CPU metrics..."):
                cpu_data = self.developer_tools.get_performance_metrics('cpu')
        else:
            print("Collecting CPU metrics...")
            cpu_data = self.developer_tools.get_performance_metrics('cpu')

        self._display_cpu_metrics(cpu_data)

    def _show_disk_monitoring(self):
        """Show disk I/O monitoring."""
        if HAS_RICH and console:
            with console.status("[bold green]Monitoring disk I/O..."):
                disk_data = self.developer_tools.get_performance_metrics('disk')
        else:
            print("Monitoring disk I/O...")
            disk_data = self.developer_tools.get_performance_metrics('disk')

        self._display_disk_monitoring(disk_data)

    def _show_app_performance(self):
        """Show application performance."""
        if HAS_RICH and console:
            with console.status("[bold green]Analyzing application performance..."):
                app_data = self.developer_tools.get_performance_metrics('application')
        else:
            print("Analyzing application performance...")
            app_data = self.developer_tools.get_performance_metrics('application')

        self._display_app_performance(app_data)

    def _show_historical_trends(self):
        """Show historical performance trends."""
        if HAS_RICH and console:
            with console.status("[bold green]Loading performance trends..."):
                trends_data = self.developer_tools.get_performance_metrics('trends')
        else:
            print("Loading performance trends...")
            trends_data = self.developer_tools.get_performance_metrics('trends')

        self._display_historical_trends(trends_data)

    def _show_performance_alerts(self):
        """Show performance alerts."""
        if HAS_RICH and console:
            with console.status("[bold green]Checking performance alerts..."):
                alerts_data = self.developer_tools.get_performance_metrics('alerts')
        else:
            print("Checking performance alerts...")
            alerts_data = self.developer_tools.get_performance_metrics('alerts')

        self._display_performance_alerts(alerts_data)

    def _display_memory_analysis(self, memory_data: Dict[str, Any]):
        """Display detailed memory analysis."""
        if 'error' in memory_data:
            self.display_error(memory_data['error'])
            return

        memory_metrics = memory_data.get('memory_metrics', {})
        if 'error' in memory_metrics:
            self.display_error(memory_metrics['error'])
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]💾 Memory Analysis[/bold cyan]")

            # Virtual Memory Analysis
            vmem = memory_metrics.get('virtual', {})
            if vmem:
                vmem_panel = Panel.fit(
                    f"[bold]Total Memory:[/bold] {vmem.get('total_gb', 'N/A')} GB\n"
                    f"[bold]Available:[/bold] {vmem.get('available_gb', 'N/A')} GB ({vmem.get('percent', 'N/A')}% used)\n"
                    f"[bold]Used:[/bold] {vmem.get('used_gb', 'N/A')} GB\n"
                    f"[bold]Free:[/bold] {vmem.get('free_gb', 'N/A')} GB\n"
                    f"[bold]Buffers:[/bold] {round(vmem.get('buffers', 0) / (1024**3), 2)} GB\n"
                    f"[bold]Cached:[/bold] {round(vmem.get('cached', 0) / (1024**3), 2)} GB",
                    title="🖥️ Virtual Memory",
                    border_style="green"
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
                    title="💿 Swap Memory",
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
                    title="🔧 Process Memory",
                    border_style="blue"
                )
                console.print(process_panel)

            # Memory recommendations
            recommendations = []
            if vmem.get('percent', 0) > 80:
                recommendations.append("High memory usage detected - consider closing unused applications")
            if swap.get('percent', 0) > 10:
                recommendations.append("Swap usage detected - consider adding more RAM")
            if process_mem.get('percent', 0) > 5:
                recommendations.append("High process memory usage - monitor for memory leaks")

            if recommendations:
                rec_text = "\n".join(recommendations)
                rec_panel = Panel.fit(rec_text, title="📋 Recommendations", border_style="yellow")
                console.print(rec_panel)

        else:
            print("\nMemory Analysis:")
            print("=" * 50)
            vmem = memory_metrics.get('virtual', {})
            if vmem:
                print(f"Virtual Memory:")
                print(f"  Total: {vmem.get('total_gb', 'N/A')} GB")
                print(f"  Available: {vmem.get('available_gb', 'N/A')} GB")
                print(f"  Used: {vmem.get('used_gb', 'N/A')} GB ({vmem.get('percent', 'N/A')}%)")

            swap = memory_metrics.get('swap', {})
            if swap:
                print(f"\nSwap Memory:")
                print(f"  Total: {swap.get('total_gb', 'N/A')} GB")
                print(f"  Used: {swap.get('used_gb', 'N/A')} GB ({swap.get('percent', 'N/A')}%)")

            process_mem = memory_metrics.get('process', {})
            if process_mem:
                print(f"\nProcess Memory:")
                print(f"  RSS: {process_mem.get('rss_mb', 'N/A')} MB")
                print(f"  VMS: {process_mem.get('vms_mb', 'N/A')} MB")
                print(f"  Usage: {process_mem.get('percent', 'N/A')}%")

    def _display_cpu_metrics(self, cpu_data: Dict[str, Any]):
        """Display detailed CPU metrics."""
        if 'error' in cpu_data:
            self.display_error(cpu_data['error'])
            return

        system_metrics = cpu_data.get('system_metrics', {})
        if 'error' in system_metrics:
            self.display_error(system_metrics['error'])
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]🖥️ CPU Performance Metrics[/bold cyan]")

            # CPU Usage and Information
            cpu_info = system_metrics.get('cpu', {})
            if cpu_info:
                cpu_usage = cpu_info.get('usage_percent', 0)
                cpu_color = "red" if cpu_usage > 80 else "yellow" if cpu_usage > 60 else "green"

                cpu_panel = Panel.fit(
                    f"[bold]Current Usage:[/bold] {cpu_usage}%\n"
                    f"[bold]Physical Cores:[/bold] {cpu_info.get('core_count', 'N/A')}\n"
                    f"[bold]Logical Cores:[/bold] {cpu_info.get('logical_count', 'N/A')}\n"
                    f"[bold]Context Switches:[/bold] {cpu_info.get('context_switches', 'N/A'):,}\n"
                    f"[bold]Interrupts:[/bold] {cpu_info.get('interrupts', 'N/A'):,}\n"
                    f"[bold]Load Average:[/bold] {cpu_info.get('load_average', 'N/A')}",
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
                        status = "High" if usage > 80 else "Medium" if usage > 60 else "Normal"
                        core_table.add_row(f"Core {i}", f"{usage:.1f}%", status)

                    console.print(core_table)

                # CPU Frequency
                freq_info = cpu_info.get('frequency', {})
                if freq_info and freq_info != 'N/A':
                    freq_panel = Panel.fit(
                        f"[bold]Current:[/bold] {freq_info.get('current', 'N/A')} MHz\n"
                        f"[bold]Minimum:[/bold] {freq_info.get('min', 'N/A')} MHz\n"
                        f"[bold]Maximum:[/bold] {freq_info.get('max', 'N/A')} MHz",
                        title="⚡ CPU Frequency",
                        border_style="blue"
                    )
                    console.print(freq_panel)

            # System Information
            system_info = system_metrics.get('system', {})
            if system_info:
                system_panel = Panel.fit(
                    f"[bold]Uptime:[/bold] {system_info.get('uptime_formatted', 'N/A')}\n"
                    f"[bold]Platform:[/bold] {system_info.get('platform', 'N/A')}\n"
                    f"[bold]Python Version:[/bold] {system_info.get('python_version', 'N/A')}\n"
                    f"[bold]Boot Time:[/bold] {system_info.get('boot_time', 'N/A')}",
                    title="🖥️ System Information",
                    border_style="green"
                )
                console.print(system_panel)

        else:
            print("\nCPU Performance Metrics:")
            print("=" * 50)
            cpu_info = system_metrics.get('cpu', {})
            if cpu_info:
                print(f"CPU Usage: {cpu_info.get('usage_percent', 'N/A')}%")
                print(f"Physical Cores: {cpu_info.get('core_count', 'N/A')}")
                print(f"Logical Cores: {cpu_info.get('logical_count', 'N/A')}")
                print(f"Load Average: {cpu_info.get('load_average', 'N/A')}")

                per_core = cpu_info.get('usage_per_core', [])
                if per_core:
                    print("\nPer-Core Usage:")
                    for i, usage in enumerate(per_core):
                        print(f"  Core {i}: {usage:.1f}%")

            system_info = system_metrics.get('system', {})
            if system_info:
                print(f"\nSystem Information:")
                print(f"  Uptime: {system_info.get('uptime_formatted', 'N/A')}")
                print(f"  Platform: {system_info.get('platform', 'N/A')}")
                print(f"  Python: {system_info.get('python_version', 'N/A')}")

    def _display_disk_monitoring(self, disk_data: Dict[str, Any]):
        """Display disk I/O monitoring data."""
        if 'error' in disk_data:
            self.display_error(disk_data['error'])
            return

        disk_metrics = disk_data.get('disk_metrics', {})
        if 'error' in disk_metrics:
            self.display_error(disk_metrics['error'])
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]💾 Disk I/O Monitoring[/bold cyan]")

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
                        usage_color = "red" if info.get('percent', 0) > 90 else "yellow" if info.get('percent', 0) > 75 else "green"
                        usage_table.add_row(
                            device,
                            info.get('mountpoint', 'N/A'),
                            info.get('fstype', 'N/A'),
                            f"{info.get('total_gb', 'N/A')} GB",
                            f"{info.get('used_gb', 'N/A')} GB",
                            f"{info.get('free_gb', 'N/A')} GB",
                            f"[{usage_color}]{info.get('percent', 'N/A')}%[/{usage_color}]"
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
                    title="📊 I/O Statistics",
                    border_style="blue"
                )
                console.print(io_panel)

        else:
            print("\nDisk I/O Monitoring:")
            print("=" * 50)
            disk_usage = disk_metrics.get('usage', {})
            if disk_usage:
                print("Disk Usage:")
                for device, info in disk_usage.items():
                    if 'error' not in info:
                        print(f"  {device}: {info.get('used_gb', 'N/A')}/{info.get('total_gb', 'N/A')} GB ({info.get('percent', 'N/A')}%)")

            disk_io = disk_metrics.get('io', {})
            if disk_io:
                print(f"\nI/O Statistics:")
                print(f"  Read Operations: {disk_io.get('read_count', 'N/A'):,}")
                print(f"  Write Operations: {disk_io.get('write_count', 'N/A'):,}")
                print(f"  Data Read: {disk_io.get('read_mb', 'N/A')} MB")
                print(f"  Data Written: {disk_io.get('write_mb', 'N/A')} MB")

    def _display_app_performance(self, app_data: Dict[str, Any]):
        """Display application performance metrics."""
        if 'error' in app_data:
            self.display_error(app_data['error'])
            return

        app_metrics = app_data.get('application_metrics', {})
        if 'error' in app_metrics:
            self.display_error(app_metrics['error'])
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]🚀 Application Performance[/bold cyan]")

            # Process Information
            process_info = app_metrics.get('process', {})
            if process_info:
                process_panel = Panel.fit(
                    f"[bold]Process ID:[/bold] {process_info.get('pid', 'N/A')}\n"
                    f"[bold]Process Name:[/bold] {process_info.get('name', 'N/A')}\n"
                    f"[bold]Status:[/bold] {process_info.get('status', 'N/A')}\n"
                    f"[bold]Create Time:[/bold] {process_info.get('create_time', 'N/A')}\n"
                    f"[bold]CPU Percent:[/bold] {process_info.get('cpu_percent', 'N/A')}%\n"
                    f"[bold]Memory Percent:[/bold] {process_info.get('memory_percent', 'N/A')}%\n"
                    f"[bold]Threads:[/bold] {process_info.get('num_threads', 'N/A')}",
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
                    border_style="magenta"
                )
                console.print(threading_panel)

        else:
            print("\nApplication Performance:")
            print("=" * 50)
            process_info = app_metrics.get('process', {})
            if process_info:
                print(f"Process ID: {process_info.get('pid', 'N/A')}")
                print(f"Process Name: {process_info.get('name', 'N/A')}")
                print(f"CPU Percent: {process_info.get('cpu_percent', 'N/A')}%")
                print(f"Memory Percent: {process_info.get('memory_percent', 'N/A')}%")

            resources = app_metrics.get('resources', {})
            if resources:
                print(f"\nResource Usage:")
                print(f"  User Time: {resources.get('user_time', 'N/A'):.2f}s")
                print(f"  System Time: {resources.get('system_time', 'N/A'):.2f}s")
                print(f"  Max Memory: {resources.get('max_memory_kb', 'N/A')} KB")

    def _display_historical_trends(self, trends_data: Dict[str, Any]):
        """Display historical performance trends."""
        if 'error' in trends_data:
            self.display_error(trends_data['error'])
            return

        trends = trends_data.get('trends', {})
        if 'error' in trends:
            self.display_error(trends['error'])
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]📈 Historical Performance Trends[/bold cyan]")

            # Display trend information
            info_panel = Panel.fit(
                f"[bold]Data Points:[/bold] {trends.get('data_points', 'N/A')}\n"
                f"[bold]Time Period:[/bold] {trends.get('period', 'N/A')}\n"
                f"[bold]Note:[/bold] {trends.get('note', 'N/A')}",
                title="📊 Trend Information",
                border_style="blue"
            )
            console.print(info_panel)

            # CPU Trend
            cpu_trend = trends.get('cpu_24h', [])
            if cpu_trend:
                console.print("\n[bold green]CPU Usage Trend (Last 24 Hours)[/bold green]")

                # Show recent data points
                recent_cpu = cpu_trend[-12:]  # Last 12 hours
                cpu_table = Table(title="Recent CPU Usage")
                cpu_table.add_column("Time", style="cyan")
                cpu_table.add_column("CPU %", style="green")
                cpu_table.add_column("Status", style="yellow")

                for i, usage in enumerate(recent_cpu):
                    hours_ago = len(recent_cpu) - i - 1
                    time_label = f"{hours_ago}h ago" if hours_ago > 0 else "Now"
                    status = "High" if usage > 80 else "Medium" if usage > 60 else "Normal"
                    status_color = "red" if usage > 80 else "yellow" if usage > 60 else "green"
                    cpu_table.add_row(
                        time_label,
                        f"{usage:.1f}%",
                        f"[{status_color}]{status}[/{status_color}]"
                    )

                console.print(cpu_table)

            # Memory Trend
            memory_trend = trends.get('memory_24h', [])
            if memory_trend:
                console.print("\n[bold blue]Memory Usage Trend (Last 24 Hours)[/bold blue]")

                recent_memory = memory_trend[-12:]  # Last 12 hours
                memory_table = Table(title="Recent Memory Usage")
                memory_table.add_column("Time", style="cyan")
                memory_table.add_column("Memory %", style="green")
                memory_table.add_column("Status", style="yellow")

                for i, usage in enumerate(recent_memory):
                    hours_ago = len(recent_memory) - i - 1
                    time_label = f"{hours_ago}h ago" if hours_ago > 0 else "Now"
                    status = "High" if usage > 85 else "Medium" if usage > 70 else "Normal"
                    status_color = "red" if usage > 85 else "yellow" if usage > 70 else "green"
                    memory_table.add_row(
                        time_label,
                        f"{usage:.1f}%",
                        f"[{status_color}]{status}[/{status_color}]"
                    )

                console.print(memory_table)

        else:
            print("\nHistorical Performance Trends:")
            print("=" * 50)
            print(f"Data Points: {trends.get('data_points', 'N/A')}")
            print(f"Time Period: {trends.get('period', 'N/A')}")

            cpu_trend = trends.get('cpu_24h', [])
            if cpu_trend:
                print(f"\nRecent CPU Usage:")
                recent_cpu = cpu_trend[-6:]  # Last 6 data points
                for i, usage in enumerate(recent_cpu):
                    hours_ago = len(recent_cpu) - i - 1
                    print(f"  {hours_ago}h ago: {usage:.1f}%")

            memory_trend = trends.get('memory_24h', [])
            if memory_trend:
                print(f"\nRecent Memory Usage:")
                recent_memory = memory_trend[-6:]  # Last 6 data points
                for i, usage in enumerate(recent_memory):
                    hours_ago = len(recent_memory) - i - 1
                    print(f"  {hours_ago}h ago: {usage:.1f}%")

    def _display_performance_alerts(self, alerts_data: Dict[str, Any]):
        """Display performance alerts and thresholds."""
        if 'error' in alerts_data:
            self.display_error(alerts_data['error'])
            return

        alerts_info = alerts_data.get('alerts', {})
        if 'error' in alerts_info:
            self.display_error(alerts_info['error'])
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]🚨 Performance Alerts[/bold cyan]")

            # Alert thresholds
            thresholds = alerts_info.get('thresholds', {})

            if thresholds:
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

            # Active alerts
            active_alerts = alerts_info.get('active_alerts', [])
            if active_alerts:
                alerts_table = Table(title="Current Performance Alerts")
                alerts_table.add_column("Type", style="cyan")
                alerts_table.add_column("Level", style="red")
                alerts_table.add_column("Current Value", style="yellow")
                alerts_table.add_column("Threshold", style="green")
                alerts_table.add_column("Message", style="white")

                for alert in active_alerts:
                    level_color = "red" if alert.get('level') == 'critical' else "yellow"
                    alerts_table.add_row(
                        alert.get('type', 'N/A'),
                        f"[{level_color}]{alert.get('level', 'N/A').upper()}[/{level_color}]",
                        f"{alert.get('current_value', 'N/A')}%",
                        f"{alert.get('threshold', 'N/A')}%",
                        alert.get('message', 'N/A')
                    )

                console.print(alerts_table)
            else:
                console.print(Panel("✅ No active performance alerts", title="Status", border_style="green"))

        else:
            print("\nPerformance Alerts:")
            print("=" * 50)
            thresholds = alerts_info.get('thresholds', {})
            if thresholds:
                print("Alert Thresholds:")
                print(f"  CPU Warning: {thresholds.get('cpu_warning', 'N/A')}%")
                print(f"  CPU Critical: {thresholds.get('cpu_critical', 'N/A')}%")
                print(f"  Memory Warning: {thresholds.get('memory_warning', 'N/A')}%")
                print(f"  Memory Critical: {thresholds.get('memory_critical', 'N/A')}%")

            active_alerts = alerts_info.get('active_alerts', [])
            if active_alerts:
                print(f"\nActive Alerts ({len(active_alerts)}):")
                for alert in active_alerts:
                    print(f"  {alert.get('type', 'N/A')}: {alert.get('level', 'N/A').upper()} - {alert.get('message', 'N/A')}")
            else:
                print("\n✅ No active performance alerts")
