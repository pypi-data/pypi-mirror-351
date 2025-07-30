"""
EcoCycle - Data Exporter Module
Provides functionality to export cycling data to various formats.
"""
import os
import json
import csv
import datetime
import logging
from typing import Dict, List, Any, Optional

# Import utilities
import utils.ascii_art as ascii_art
from .ui_utilities import HAS_RICH, console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.align import Align
from rich.layout import Layout
from rich.rule import Rule
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, SpinnerColumn, TextColumn

logger = logging.getLogger(__name__)

# Constants
REPORT_DIR = "reports"


class DataExporter:
    """Provides functionality to export cycling data to various formats."""
    
    def __init__(self, user_manager=None, ui=None):
        """Initialize the data exporter."""
        self.user_manager = user_manager
        self.ui = ui
    
    def export_data(self):
        """Export cycling data to various formats."""
        ascii_art.clear_screen()
        ascii_art.display_header()
        
        # Use Rich UI if available, otherwise fallback to ASCII art
        if HAS_RICH:
            # Create a layout for the header
            layout = Layout()
            layout.split(
                Layout(name="header", size=3),
                Layout(name="main")
            )
            
            # Create a stylish header
            title = Text("Export Cycling Data", style="bold green")
            header_panel = Panel(
                Align.center(title),
                box=DOUBLE,
                border_style="bright_green",
                padding=(1, 10)
            )
            layout["header"].update(header_panel)
            
            # Render the layout header
            console.print(layout["header"])
            
            # Add descriptive panel
            export_description = Panel(
                "Export your cycling data to various formats for use in other applications or for backup purposes.",
                title="Data Export Options",
                border_style="blue",
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(export_description)
        else:
            ascii_art.display_section_header("Export Data")

        # Get user data
        user = self.user_manager.get_current_user()
        username = user.get('username')

        # Get user stats
        stats = user.get('stats', {})
        trips = stats.get('trips', [])

        # Check if user has any trips
        if not trips:
            if HAS_RICH:
                # Create an attention-grabbing notification panel for no data
                no_data_panel = Panel(
                    Text.assemble(
                        ("No cycling data available to export!\n\n", "bold red"),
                        ("You need to log some cycling trips before you can export data.\n", "yellow"),
                        ("Use the 'Log New Trip' feature from the main menu to get started.", "italic cyan")
                    ),
                    box=HEAVY,
                    border_style="yellow",
                    title="[bold red]No Data Found[/bold red]",
                    title_align="center",
                    padding=(1, 2)
                )
                console.print(Align.center(no_data_panel))
                
                # Styled continue prompt
                console.print()
                self.ui.prompt_continue("Press Enter to return to the visualization menu")
                return
            else:
                print("No trip data available to export.")
                input("\nPress Enter to continue...")
            return

        # Display export options
        if HAS_RICH:
            console.print(Rule("Export Format Options", style="cyan"))
            
            # Create export options table
            options_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=ROUNDED,
                border_style="blue",
                expand=False,
                title="Select an Export Format",
                title_style="bold cyan",
                title_justify="center"
            )
            
            # Define columns with clear headers
            options_table.add_column("#", style="dim", justify="center", width=3)
            options_table.add_column("Format", style="green")
            options_table.add_column("Description", style="blue")
            options_table.add_column("File Type", style="magenta", justify="center")
            
            # Add rows with helpful descriptions
            options_table.add_row(
                "1", 
                "📄 CSV", 
                "Simple text format compatible with spreadsheet software", 
                ".csv"
            )
            options_table.add_row(
                "2", 
                "🔄 JSON", 
                "Structured format for data interchange and analysis", 
                ".json"
            )
            options_table.add_row(
                "3", 
                "↩️ Return", 
                "Go back to Data Visualization Menu", 
                ""
            )
            
            console.print(options_table)
            
            # Add styled prompt for selection
            choice = Prompt.ask(
                "[bold]Select an export format[/bold]",
                choices=["1", "2", "3"],
                default="1"
            )
            
        else:
            print("Export Format Options:")
            print("1. CSV (Comma Separated Values)")
            print("2. JSON (JavaScript Object Notation)")
            print("3. Return to Data Visualization Menu")

            choice = input("\nSelect an option (1-3): ")

        if choice == "1":
            # Export to CSV
            self._export_to_csv(username, stats, trips)
        elif choice == "2":
            # Export to JSON
            self._export_to_json(username, user, stats)
        elif choice == "3":
            # Return to menu - no action needed
            pass
    
    def _export_to_csv(self, username, stats, trips):
        """Export cycling data to CSV format."""
        filename = os.path.join(REPORT_DIR, f"cycling_data_{username}_{datetime.date.today().strftime('%Y_%m_%d')}.csv")

        try:
            if HAS_RICH:
                # Display CSV export progress
                console.print(Rule("CSV Export Progress", style="green"))
                
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold green]Exporting cycling data to CSV...[/bold green]"),
                    BarColumn(bar_width=40),
                    expand=True
                ) as progress:
                    task = progress.add_task("Exporting", total=len(trips) + 2)
                    
                    # Create CSV file
                    with open(filename, 'w', newline='') as csvfile:
                        # Update progress
                        progress.update(task, advance=1)
                        
                        # Create writer with field names
                        fieldnames = ['date', 'distance', 'duration', 'carbon_saved', 'calories_burned', 'notes']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        
                        # Write header
                        writer.writeheader()
                        
                        # Update progress
                        progress.update(task, advance=1)
                        
                        # Write trip data
                        for trip in trips:
                            # Create a clean trip dict with only relevant fields
                            clean_trip = {
                                'date': trip.get('date', ''),
                                'distance': trip.get('distance', 0),
                                'duration': trip.get('duration', 0),
                                'carbon_saved': trip.get('carbon_saved', 0),
                                'calories_burned': trip.get('calories_burned', 0),
                                'notes': trip.get('notes', '')
                            }
                            writer.writerow(clean_trip)
                            
                            # Update progress
                            progress.update(task, advance=1)
                
                # Show success message
                success_panel = Panel(
                    f"[bold green]Data successfully exported to CSV![/bold green]\n\n"
                    f"File location: [italic]{filename}[/italic]",
                    title="[bold green]Export Successful[/bold green]",
                    border_style="green",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(success_panel)
                
                # Ask if user wants to open the file
                if self.ui.open_file_browser(filename):
                    pass
            else:
                # Original code for systems without Rich
                print("\nExporting cycling data to CSV...")
                
                # Create CSV file
                with open(filename, 'w', newline='') as csvfile:
                    # Create writer with field names
                    fieldnames = ['date', 'distance', 'duration', 'carbon_saved', 'calories_burned', 'notes']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    # Write header
                    writer.writeheader()
                    
                    # Write trip data
                    for trip in trips:
                        # Create a clean trip dict with only relevant fields
                        clean_trip = {
                            'date': trip.get('date', ''),
                            'distance': trip.get('distance', 0),
                            'duration': trip.get('duration', 0),
                            'carbon_saved': trip.get('carbon_saved', 0),
                            'calories_burned': trip.get('calories_burned', 0),
                            'notes': trip.get('notes', '')
                        }
                        writer.writerow(clean_trip)
                
                print(f"\nData successfully exported to CSV: {filename}")
                
                # Ask if user wants to open the file
                open_choice = input("\nOpen CSV File in default application? (y/n): ")
                if open_choice.lower() == 'y':
                    self.ui.open_file_browser(filename)
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            self.ui.display_error(f"Error exporting data to CSV: {str(e)}")
        
        # Final prompt to return to menu
        self.ui.prompt_continue()
    
    def _export_to_json(self, username, user, stats):
        """Export cycling data to JSON format."""
        filename = os.path.join(REPORT_DIR, f"cycling_data_{username}_{datetime.date.today().strftime('%Y_%m_%d')}.json")

        try:
            if HAS_RICH:
                # Display JSON export progress
                console.print(Rule("JSON Export Progress", style="green"))
                
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold green]Exporting cycling data to JSON...[/bold green]"),
                    BarColumn(bar_width=40),
                    expand=True
                ) as progress:
                    task = progress.add_task("Exporting", total=3)
                    
                    # Prepare data
                    progress.update(task, advance=1)
                    export_data = {
                        "username": username,
                        "name": user.get('name', username),
                        "export_date": datetime.datetime.now().isoformat(),
                        "stats": stats
                    }
                    
                    # Write to file
                    progress.update(task, advance=1)
                    with open(filename, 'w') as f:
                        json.dump(export_data, f, indent=2)
                    
                    # Complete
                    progress.update(task, advance=1)
                
                # Show success message
                success_panel = Panel(
                    f"[bold green]Data successfully exported to JSON![/bold green]\n\n"
                    f"File location: [italic]{filename}[/italic]",
                    title="[bold green]Export Successful[/bold green]",
                    border_style="green",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(success_panel)
                
                # Ask if user wants to open the file
                if self.ui.open_file_browser(filename):
                    pass
            else:
                # Original code for systems without Rich
                # Prepare data
                export_data = {
                    "username": username,
                    "name": user.get('name', username),
                    "export_date": datetime.datetime.now().isoformat(),
                    "stats": stats
                }

                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)

                print(f"\nData successfully exported to JSON: {filename}")
                
                # Ask if user wants to open the file
                open_choice = input("\nOpen JSON File in default application? (y/n): ")
                if open_choice.lower() == 'y':
                    self.ui.open_file_browser(filename)
        
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            self.ui.display_error(f"Error exporting data to JSON: {str(e)}")
        
        # Final prompt to return to menu
        self.ui.prompt_continue()
