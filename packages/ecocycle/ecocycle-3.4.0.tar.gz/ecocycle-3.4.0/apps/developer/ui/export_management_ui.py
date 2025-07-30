"""
EcoCycle - Export Management UI Component
Handles data export functionality.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Panel, Prompt


class ExportManagementUI(BaseUI):
    """UI component for data export operations."""

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
            self.display_error(f"Export failed: {result['error']}")
        elif result.get('success'):
            if HAS_RICH and console:
                export_panel = Panel.fit(
                    f"[bold]Export Type:[/bold] {result.get('export_type', 'N/A')}\n"
                    f"[bold]Filename:[/bold] {result.get('filename', 'N/A')}\n"
                    f"[bold]Size:[/bold] {self.format_bytes(result.get('size', 0))}\n"
                    f"[bold]Records:[/bold] {result.get('records_exported', 0):,}\n"
                    f"[bold]Path:[/bold] {result.get('path', 'N/A')}",
                    title="✅ Export Successful"
                )
                console.print(export_panel)
            else:
                print("✅ Export Successful")
                print(f"Export Type: {result.get('export_type', 'N/A')}")
                print(f"Filename: {result.get('filename', 'N/A')}")
                print(f"Size: {self.format_bytes(result.get('size', 0))}")
                print(f"Records: {result.get('records_exported', 0):,}")
                print(f"Path: {result.get('path', 'N/A')}")

    def handle_custom_export(self):
        """Handle custom export with user-defined parameters."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Custom Data Export[/bold cyan]")
            
            # Get export format
            format_choice = Prompt.ask(
                "Select export format",
                choices=["json", "csv", "xml", "txt"],
                default="json"
            )
            
            # Get data types to include
            console.print("\nSelect data types to include:")
            console.print("1. User accounts")
            console.print("2. Trip data")
            console.print("3. Statistics")
            console.print("4. Configuration")
            console.print("5. Cache data")
            console.print("6. Log files")
            
            data_types = []
            type_mapping = {
                "1": "users",
                "2": "trips", 
                "3": "statistics",
                "4": "config",
                "5": "cache",
                "6": "logs"
            }
            
            selections = Prompt.ask("Enter numbers separated by commas (e.g., 1,2,3)", default="1,2,3")
            for selection in selections.split(','):
                selection = selection.strip()
                if selection in type_mapping:
                    data_types.append(type_mapping[selection])
            
            # Get date range if applicable
            include_date_filter = self.confirm_action("Apply date range filter?")
            date_range = None
            if include_date_filter:
                start_date = self.get_user_input("Start date (YYYY-MM-DD)", "")
                end_date = self.get_user_input("End date (YYYY-MM-DD)", "")
                if start_date and end_date:
                    date_range = {"start": start_date, "end": end_date}
            
            # Get filename
            default_filename = f"custom_export.{format_choice}"
            filename = self.get_user_input("Export filename", default_filename)
            
            # Perform export
            export_params = {
                "format": format_choice,
                "data_types": data_types,
                "date_range": date_range,
                "filename": filename
            }
            
            with console.status("[bold green]Performing custom export..."):
                result = self.developer_tools.custom_export(export_params)
                
        else:
            print("\nCustom Data Export")
            print("Available formats: json, csv, xml, txt")
            format_choice = input("Select export format [json]: ").strip() or "json"
            
            print("\nAvailable data types:")
            print("1. User accounts")
            print("2. Trip data") 
            print("3. Statistics")
            print("4. Configuration")
            print("5. Cache data")
            print("6. Log files")
            
            selections = input("Enter numbers separated by commas [1,2,3]: ").strip() or "1,2,3"
            data_types = []
            type_mapping = {
                "1": "users",
                "2": "trips",
                "3": "statistics", 
                "4": "config",
                "5": "cache",
                "6": "logs"
            }
            
            for selection in selections.split(','):
                selection = selection.strip()
                if selection in type_mapping:
                    data_types.append(type_mapping[selection])
            
            filename = input("Export filename [custom_export.json]: ").strip() or f"custom_export.{format_choice}"
            
            export_params = {
                "format": format_choice,
                "data_types": data_types,
                "filename": filename
            }
            
            print("Performing custom export...")
            result = self.developer_tools.custom_export(export_params)
        
        self._display_export_result(result)

    def handle_scheduled_exports(self):
        """Handle scheduled export management."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Scheduled Exports[/bold cyan]")
            console.print("1. View scheduled exports")
            console.print("2. Create new scheduled export")
            console.print("3. Modify scheduled export")
            console.print("4. Delete scheduled export")
            console.print("5. Run scheduled export now")
            console.print("0. Back to export menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            print("\nScheduled Exports")
            print("1. View scheduled exports")
            print("2. Create new scheduled export")
            print("3. Modify scheduled export")
            print("4. Delete scheduled export")
            print("5. Run scheduled export now")
            print("0. Back to export menu")

            choice = input("Select option (0-5): ").strip()

        if choice == "1":
            self._view_scheduled_exports()
        elif choice == "2":
            self._create_scheduled_export()
        elif choice == "3":
            self._modify_scheduled_export()
        elif choice == "4":
            self._delete_scheduled_export()
        elif choice == "5":
            self._run_scheduled_export()

    def _view_scheduled_exports(self):
        """View all scheduled exports."""
        if HAS_RICH and console:
            with console.status("[bold green]Loading scheduled exports..."):
                schedules = self.developer_tools.get_scheduled_exports()
        else:
            print("Loading scheduled exports...")
            schedules = self.developer_tools.get_scheduled_exports()

        if 'error' in schedules:
            self.display_error(schedules['error'])
            return

        scheduled_exports = schedules.get('schedules', [])
        
        if not scheduled_exports:
            self.display_info("No scheduled exports found")
            return

        if HAS_RICH and console:
            from rich.table import Table
            table = Table(title="Scheduled Exports")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Schedule", style="blue")
            table.add_column("Last Run", style="magenta")
            table.add_column("Status", style="red")

            for export in scheduled_exports:
                table.add_row(
                    str(export.get('id', 'N/A')),
                    export.get('name', 'N/A'),
                    export.get('export_type', 'N/A'),
                    export.get('schedule', 'N/A'),
                    self.format_timestamp(export.get('last_run', 'Never')),
                    export.get('status', 'N/A')
                )

            console.print(table)
        else:
            print("\nScheduled Exports:")
            print("-" * 80)
            for export in scheduled_exports:
                print(f"ID: {export.get('id', 'N/A')}")
                print(f"  Name: {export.get('name', 'N/A')}")
                print(f"  Type: {export.get('export_type', 'N/A')}")
                print(f"  Schedule: {export.get('schedule', 'N/A')}")
                print(f"  Last Run: {export.get('last_run', 'Never')}")
                print(f"  Status: {export.get('status', 'N/A')}")
                print()

    def _create_scheduled_export(self):
        """Create a new scheduled export."""
        self.display_info("🚧 Scheduled export creation - Implementation in progress")

    def _modify_scheduled_export(self):
        """Modify an existing scheduled export."""
        self.display_info("🚧 Scheduled export modification - Implementation in progress")

    def _delete_scheduled_export(self):
        """Delete a scheduled export."""
        self.display_info("🚧 Scheduled export deletion - Implementation in progress")

    def _run_scheduled_export(self):
        """Run a scheduled export immediately."""
        self.display_info("🚧 Manual scheduled export execution - Implementation in progress")
