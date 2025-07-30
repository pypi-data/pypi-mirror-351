"""
EcoCycle - Log Analysis UI Component
Handles log analysis, pattern detection, and error tracking.
"""
from typing import Dict, Any, Optional
from .base_ui import BaseUI, HAS_RICH, console, Table, Panel, Prompt


class LogAnalysisUI(BaseUI):
    """UI component for log analysis."""

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

                self._display_log_analysis(log_data)

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
                        log_data = self.developer_tools.search_logs(pattern, lines)
                else:
                    print(f"Searching for pattern '{pattern}'...")
                    log_data = self.developer_tools.search_logs(pattern, lines)

                self._display_pattern_search_results(log_data, pattern)

        elif choice == "4":
            # View recent errors
            if HAS_RICH and console:
                with console.status("[bold green]Loading recent errors..."):
                    log_data = self.developer_tools.get_recent_errors()
            else:
                print("Loading recent errors...")
                log_data = self.developer_tools.get_recent_errors()

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

    def _display_log_analysis(self, log_data: Dict[str, Any]):
        """Display log analysis results."""
        if 'error' in log_data:
            self.display_error(log_data['error'])
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
            table.add_column("Debug", style="dim")

            for log_file, info in analysis.items():
                if 'error' not in info:
                    table.add_row(
                        log_file,
                        str(info.get('total_lines', 0)),
                        str(info.get('error_count', 0)),
                        str(info.get('warning_count', 0)),
                        str(info.get('info_count', 0)),
                        str(info.get('debug_count', 0))
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
            print("=" * 80)

            for log_file, info in analysis.items():
                if 'error' not in info:
                    print(f"Log File: {log_file}")
                    print(f"  Total Lines: {info.get('total_lines', 0)}")
                    print(f"  Errors: {info.get('error_count', 0)}")
                    print(f"  Warnings: {info.get('warning_count', 0)}")
                    print(f"  Info: {info.get('info_count', 0)}")
                    print(f"  Debug: {info.get('debug_count', 0)}")
                    print()

            # Error patterns
            if patterns:
                print("Error Patterns:")
                for log_file, pattern_data in patterns.items():
                    if pattern_data:
                        print(f"  {log_file}:")
                        for error_type, count in pattern_data.items():
                            print(f"    {error_type}: {count}")

    def _display_pattern_search_results(self, log_data: Dict[str, Any], pattern: str):
        """Display pattern search results."""
        if 'error' in log_data:
            self.display_error(log_data['error'])
            return

        matches = log_data.get('matches', [])

        if HAS_RICH and console:
            console.print(f"\n[bold cyan]Pattern Search Results for: '{pattern}'[/bold cyan]")

            if matches:
                table = Table(title=f"Found {len(matches)} matches")
                table.add_column("Log File", style="cyan")
                table.add_column("Entry", style="green")

                for match in matches[:50]:  # Show first 50 matches
                    table.add_row(
                        match.get('file', 'N/A'),
                        self.truncate_text(match.get('line', ''), 80)
                    )

                console.print(table)
            else:
                console.print("[yellow]No matches found[/yellow]")
        else:
            print(f"\nPattern Search Results for: '{pattern}'")
            print("=" * 60)

            if matches:
                print(f"Found {len(matches)} matches:")
                for match in matches[:20]:  # Show first 20 matches
                    print(f"  {match.get('file', 'N/A')}: {match.get('line', '')[:80]}")
            else:
                print("No matches found")

    def _display_recent_errors(self, log_data: Dict[str, Any]):
        """Display recent errors from logs."""
        if 'error' in log_data:
            self.display_error(log_data['error'])
            return

        errors = log_data.get('recent_errors', [])

        if HAS_RICH and console:
            console.print("\n[bold red]Recent Errors[/bold red]")

            if errors:
                table = Table(title=f"Found {len(errors)} recent errors")
                table.add_column("Log File", style="cyan")
                table.add_column("Error Message", style="red")

                for error in errors:
                    table.add_row(
                        error.get('file', 'N/A'),
                        self.truncate_text(error.get('message', ''), 80)
                    )

                console.print(table)
            else:
                console.print("[green]No recent errors found[/green]")
        else:
            print("\nRecent Errors:")
            print("=" * 50)

            if errors:
                for error in errors:
                    print(f"  {error.get('file', 'N/A')}: {error.get('message', '')}")
            else:
                print("No recent errors found")

    def _display_log_statistics(self, log_data: Dict[str, Any]):
        """Display log statistics."""
        if 'error' in log_data:
            self.display_error(log_data['error'])
            return

        analysis = log_data.get('analysis', {})
        
        # Calculate totals
        total_files = len([f for f, info in analysis.items() if 'error' not in info])
        total_lines = sum(info.get('total_lines', 0) for info in analysis.values() if 'error' not in info)
        total_errors = sum(info.get('error_count', 0) for info in analysis.values() if 'error' not in info)
        total_warnings = sum(info.get('warning_count', 0) for info in analysis.values() if 'error' not in info)

        if HAS_RICH and console:
            stats_panel = Panel.fit(
                f"[bold]Total Log Files:[/bold] {total_files}\n"
                f"[bold]Total Lines:[/bold] {total_lines:,}\n"
                f"[bold]Total Errors:[/bold] {total_errors:,}\n"
                f"[bold]Total Warnings:[/bold] {total_warnings:,}\n"
                f"[bold]Error Rate:[/bold] {(total_errors/total_lines*100):.2f}% of lines" if total_lines > 0 else "[bold]Error Rate:[/bold] N/A",
                title="📊 Log Statistics"
            )
            console.print(stats_panel)
        else:
            print("\nLog Statistics:")
            print(f"Total Log Files: {total_files}")
            print(f"Total Lines: {total_lines:,}")
            print(f"Total Errors: {total_errors:,}")
            print(f"Total Warnings: {total_warnings:,}")
            if total_lines > 0:
                print(f"Error Rate: {(total_errors/total_lines*100):.2f}% of lines")
