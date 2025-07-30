"""
EcoCycle - Display Utilities
Common display methods for developer UI components.
"""
from typing import Dict, Any, Optional
from .base_ui import BaseUI, HAS_RICH, console, Table, Panel


class DisplayUtils(BaseUI):
    """Utility class for common display methods."""

    def display_database_overview(self, db_data: Dict[str, Any]):
        """Display database overview."""
        if 'error' in db_data:
            self.display_error(f"Error: {db_data['error']}")
            return

        if HAS_RICH and console:
            table = Table(title="Database Tables Overview")
            table.add_column("Table Name", style="cyan")
            table.add_column("Columns", style="green")
            table.add_column("Total Rows", style="yellow")
            table.add_column("Sample Data", style="dim")

            for table_name, table_info in db_data.items():
                columns = ", ".join(table_info.get('columns', []))
                total_rows = str(table_info.get('total_count', 0))
                sample_rows = len(table_info.get('sample_rows', []))

                table.add_row(
                    table_name,
                    columns[:50] + "..." if len(columns) > 50 else columns,
                    total_rows,
                    f"{sample_rows} rows shown"
                )

            console.print(table)
        else:
            print("\nDatabase Tables Overview:")
            print("-" * 80)
            for table_name, table_info in db_data.items():
                print(f"Table: {table_name}")
                print(f"  Columns: {', '.join(table_info.get('columns', []))}")
                print(f"  Total Rows: {table_info.get('total_count', 0)}")
                print(f"  Sample Rows: {len(table_info.get('sample_rows', []))}")
                print()

    def display_table_data(self, table_name: str, table_data: Dict[str, Any]):
        """Display specific table data."""
        if 'error' in table_data:
            self.display_error(f"Error: {table_data['error']}")
            return

        if table_name not in table_data:
            self.display_error(f"Table '{table_name}' not found")
            return

        data = table_data[table_name]
        columns = data.get('columns', [])
        rows = data.get('rows', [])

        if HAS_RICH and console:
            table = Table(title=f"Table: {table_name}")

            # Add columns
            for col in columns:
                table.add_column(col, style="cyan")

            # Add rows
            for row in rows:
                # Convert all values to strings and truncate if too long
                str_row = [str(val)[:50] + "..." if len(str(val)) > 50 else str(val) for val in row]
                table.add_row(*str_row)

            console.print(table)
        else:
            print(f"\nTable: {table_name}")
            print("-" * 80)
            print(" | ".join(columns))
            print("-" * 80)
            for row in rows:
                print(" | ".join(str(val)[:30] for val in row))

    def display_table_statistics(self, db_data: Dict[str, Any]):
        """Display table statistics."""
        if 'error' in db_data:
            self.display_error(f"Error: {db_data['error']}")
            return

        total_tables = len(db_data)
        total_rows = sum(table_info.get('total_count', 0) for table_info in db_data.values())

        if HAS_RICH and console:
            stats_panel = Panel.fit(
                f"[bold]Database Statistics[/bold]\n"
                f"Total Tables: {total_tables}\n"
                f"Total Rows: {total_rows}\n"
                f"Average Rows per Table: {total_rows // total_tables if total_tables > 0 else 0}",
                title="📊 Statistics"
            )
            console.print(stats_panel)
        else:
            print("\nDatabase Statistics:")
            print(f"Total Tables: {total_tables}")
            print(f"Total Rows: {total_rows}")
            print(f"Average Rows per Table: {total_rows // total_tables if total_tables > 0 else 0}")

    def display_log_analysis(self, log_data: Dict[str, Any], specific_file: Optional[str] = None):
        """Display log analysis results."""
        if 'error' in log_data:
            self.display_error(f"Log analysis failed: {log_data['error']}")
            return

        analysis = log_data.get('analysis', {})
        recent_entries = log_data.get('recent_entries', {})

        if HAS_RICH and console:
            # Analysis summary
            console.print("\n[bold cyan]📊 Log Analysis Summary[/bold cyan]")

            if analysis:
                summary_table = Table(title="Log File Analysis")
                summary_table.add_column("Log File", style="cyan")
                summary_table.add_column("Total Lines", style="green")
                summary_table.add_column("Error Count", style="red")
                summary_table.add_column("Warning Count", style="yellow")
                summary_table.add_column("Info Count", style="blue")

                for log_file, stats in analysis.items():
                    if specific_file and log_file != specific_file:
                        continue

                    summary_table.add_row(
                        log_file,
                        str(stats.get('total_lines', 0)),
                        str(stats.get('error_count', 0)),
                        str(stats.get('warning_count', 0)),
                        str(stats.get('info_count', 0))
                    )

                console.print(summary_table)

            # Recent entries
            if recent_entries:
                console.print("\n[bold cyan]📋 Recent Log Entries[/bold cyan]")
                for log_file, entries in recent_entries.items():
                    if specific_file and log_file != specific_file:
                        continue

                    console.print(f"\n[bold yellow]{log_file}[/bold yellow]")
                    for i, entry in enumerate(entries[-10:], 1):  # Show last 10 entries
                        # Truncate long entries
                        display_entry = entry[:100] + "..." if len(entry) > 100 else entry
                        console.print(f"  {i}. {display_entry}")

        else:
            print("\n📊 Log Analysis Summary")
            print("-" * 50)

            if analysis:
                print("\nLog File Analysis:")
                for log_file, stats in analysis.items():
                    if specific_file and log_file != specific_file:
                        continue

                    print(f"\n{log_file}:")
                    print(f"  Total Lines: {stats.get('total_lines', 0)}")
                    print(f"  Errors: {stats.get('error_count', 0)}")
                    print(f"  Warnings: {stats.get('warning_count', 0)}")
                    print(f"  Info: {stats.get('info_count', 0)}")

            if recent_entries:
                print("\nRecent Log Entries:")
                for log_file, entries in recent_entries.items():
                    if specific_file and log_file != specific_file:
                        continue

                    print(f"\n{log_file}:")
                    for i, entry in enumerate(entries[-5:], 1):  # Show last 5 entries
                        display_entry = entry[:80] + "..." if len(entry) > 80 else entry
                        print(f"  {i}. {display_entry}")

    def display_session_statistics(self, session_data: Dict[str, Any]):
        """Display session statistics."""
        if 'error' in session_data:
            self.display_error(f"Session data error: {session_data['error']}")
            return

        statistics = session_data.get('statistics', {})
        active_sessions = session_data.get('active_sessions', [])

        if HAS_RICH and console:
            # Statistics panel
            stats_text = []
            for key, value in statistics.items():
                stats_text.append(f"{key.replace('_', ' ').title()}: {value}")

            stats_panel = Panel.fit(
                "\n".join(stats_text),
                title="📊 Session Statistics"
            )
            console.print(stats_panel)

            # Active sessions table
            if active_sessions:
                sessions_table = Table(title="Active Sessions")
                sessions_table.add_column("Session ID", style="cyan")
                sessions_table.add_column("User", style="green")
                sessions_table.add_column("Started", style="yellow")
                sessions_table.add_column("Last Activity", style="blue")
                sessions_table.add_column("IP Address", style="dim")

                for session in active_sessions:
                    sessions_table.add_row(
                        session.get('session_id', 'Unknown')[:8] + "...",
                        session.get('username', 'Unknown'),
                        session.get('created_at', 'Unknown'),
                        session.get('last_activity', 'Unknown'),
                        session.get('ip_address', 'Unknown')
                    )

                console.print(sessions_table)
        else:
            print("\n📊 Session Statistics")
            print("-" * 30)
            for key, value in statistics.items():
                print(f"{key.replace('_', ' ').title()}: {value}")

            if active_sessions:
                print("\nActive Sessions:")
                for i, session in enumerate(active_sessions, 1):
                    print(f"{i}. User: {session.get('username', 'Unknown')}")
                    print(f"   Started: {session.get('created_at', 'Unknown')}")
                    print(f"   Last Activity: {session.get('last_activity', 'Unknown')}")

    def display_recent_errors(self, log_data: Dict[str, Any]):
        """Display recent errors from logs."""
        recent_entries = log_data.get('recent_entries', {})

        errors = []
        for log_file, entries in recent_entries.items():
            for entry in entries:
                if any(keyword in entry.lower() for keyword in ['error', 'exception', 'failed', 'critical']):
                    errors.append((log_file, entry))

        if HAS_RICH and console:
            if errors:
                console.print("\n[bold red]🚨 Recent Errors[/bold red]")
                error_table = Table(title="Recent Error Entries")
                error_table.add_column("Log File", style="cyan")
                error_table.add_column("Error Message", style="red")

                for log_file, error_msg in errors[-20:]:  # Show last 20 errors
                    truncated_msg = error_msg[:80] + "..." if len(error_msg) > 80 else error_msg
                    error_table.add_row(log_file, truncated_msg)

                console.print(error_table)
            else:
                console.print("\n[green]✅ No recent errors found[/green]")
        else:
            if errors:
                print("\n🚨 Recent Errors:")
                print("-" * 50)
                for i, (log_file, error_msg) in enumerate(errors[-10:], 1):  # Show last 10 errors
                    truncated_msg = error_msg[:60] + "..." if len(error_msg) > 60 else error_msg
                    print(f"{i}. [{log_file}] {truncated_msg}")
            else:
                print("\n✅ No recent errors found")

    def display_performance_metrics(self, metrics: Dict[str, Any]):
        """Display performance metrics."""
        if 'error' in metrics:
            self.display_error(f"Performance metrics error: {metrics['error']}")
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]📊 Performance Metrics[/bold cyan]")

            for category, data in metrics.items():
                if isinstance(data, dict):
                    console.print(f"\n[bold yellow]{category.replace('_', ' ').title()}[/bold yellow]")

                    if 'metrics' in data:
                        for metric_name, metric_value in data['metrics'].items():
                            if isinstance(metric_value, dict):
                                current = metric_value.get('current', 'N/A')
                                unit = metric_value.get('unit', '')
                                console.print(f"  {metric_name.replace('_', ' ').title()}: {current} {unit}")
                            else:
                                console.print(f"  {metric_name.replace('_', ' ').title()}: {metric_value}")
                    else:
                        for key, value in data.items():
                            console.print(f"  {key.replace('_', ' ').title()}: {value}")
        else:
            print("\n📊 Performance Metrics")
            print("-" * 30)

            for category, data in metrics.items():
                if isinstance(data, dict):
                    print(f"\n{category.replace('_', ' ').title()}:")

                    if 'metrics' in data:
                        for metric_name, metric_value in data['metrics'].items():
                            if isinstance(metric_value, dict):
                                current = metric_value.get('current', 'N/A')
                                unit = metric_value.get('unit', '')
                                print(f"  {metric_name.replace('_', ' ').title()}: {current} {unit}")
                            else:
                                print(f"  {metric_name.replace('_', ' ').title()}: {metric_value}")
                    else:
                        for key, value in data.items():
                            print(f"  {key.replace('_', ' ').title()}: {value}")

    def display_export_result(self, result: Dict[str, Any], export_type: str):
        """Display export operation result."""
        if 'error' in result:
            self.display_error(f"{export_type} export failed: {result['error']}")
            return

        if result.get('success'):
            if HAS_RICH and console:
                console.print(f"[green]✅ {export_type} export completed successfully[/green]")
                if 'file_path' in result:
                    console.print(f"[cyan]📁 File: {result['file_path']}[/cyan]")
                if 'file_size' in result:
                    console.print(f"[cyan]📊 Size: {result['file_size']:,} bytes[/cyan]")
                if 'records_exported' in result:
                    console.print(f"[cyan]📋 Records: {result['records_exported']:,}[/cyan]")
            else:
                print(f"✅ {export_type} export completed successfully")
                if 'file_path' in result:
                    print(f"📁 File: {result['file_path']}")
                if 'file_size' in result:
                    print(f"📊 Size: {result['file_size']:,} bytes")
                if 'records_exported' in result:
                    print(f"📋 Records: {result['records_exported']:,}")
        else:
            self.display_warning(f"{export_type} export completed with warnings")

    def display_cache_statistics(self, cache_data: Dict[str, Any]):
        """Display cache statistics."""
        if 'error' in cache_data:
            self.display_error(f"Cache data error: {cache_data['error']}")
            return

        if HAS_RICH and console:
            stats = cache_data.get('statistics', {})
            
            stats_panel = Panel.fit(
                f"[bold]Cache Statistics[/bold]\n"
                f"Total Entries: {stats.get('total_entries', 0)}\n"
                f"Total Size: {self.format_bytes(stats.get('total_size_bytes', 0))}\n"
                f"Hit Rate: {stats.get('hit_rate', 0):.1f}%\n"
                f"Miss Rate: {stats.get('miss_rate', 0):.1f}%",
                title="🗄️ Cache Overview"
            )
            console.print(stats_panel)

            # Cache files table
            files = cache_data.get('cache_files', [])
            if files:
                files_table = Table(title="Cache Files")
                files_table.add_column("File", style="cyan")
                files_table.add_column("Size", style="green")
                files_table.add_column("Entries", style="yellow")
                files_table.add_column("Last Modified", style="dim")

                for file_info in files:
                    files_table.add_row(
                        file_info.get('name', 'Unknown'),
                        self.format_bytes(file_info.get('size', 0)),
                        str(file_info.get('entries', 0)),
                        file_info.get('modified', 'Unknown')
                    )

                console.print(files_table)
        else:
            stats = cache_data.get('statistics', {})
            print("\n🗄️ Cache Statistics")
            print("-" * 30)
            print(f"Total Entries: {stats.get('total_entries', 0)}")
            print(f"Total Size: {self.format_bytes(stats.get('total_size_bytes', 0))}")
            print(f"Hit Rate: {stats.get('hit_rate', 0):.1f}%")
            print(f"Miss Rate: {stats.get('miss_rate', 0):.1f}%")

            files = cache_data.get('cache_files', [])
            if files:
                print("\nCache Files:")
                for file_info in files:
                    print(f"  {file_info.get('name', 'Unknown')}: {self.format_bytes(file_info.get('size', 0))}")
