"""
EcoCycle - Activity Summary Visualization Module
Provides functionality to generate and display activity summary visualizations.
"""
import os
import time
import datetime
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

# Import utilities
import utils.ascii_art as ascii_art
from .ui_utilities import HAS_RICH, console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.layout import Layout
from rich.table import Table
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"


class ActivitySummaryViz:
    """Provides functionality for activity summary visualizations."""
    
    def __init__(self, user_manager=None, ui=None):
        """Initialize the activity summary visualization module."""
        self.user_manager = user_manager
        self.ui = ui
    
    def show_activity_summary(self):
        """Show activity summary dashboard with key metrics and charts."""
        ascii_art.clear_screen()
        ascii_art.display_header()
        
        # Use Rich UI if available
        if HAS_RICH:
            # Create a layout for the header
            layout = Layout()
            layout.split(
                Layout(name="header", size=3),
                Layout(name="main")
            )
            
            # Create a stylish header
            header_title = Text("Activity Summary Dashboard", style="bold blue")
            header_panel = Panel(
                Align.center(header_title),
                box=DOUBLE,
                border_style="blue",
                padding=(1, 2)
            )
            layout["header"].update(header_panel)
            
            # Display the header
            console.print(layout["header"])
            
            # Add descriptive panel
            summary_description = Panel(
                "This dashboard provides a comprehensive overview of your cycling activity with key metrics and visualizations.",
                title="Activity Overview",
                border_style="blue",
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(summary_description)
        else:
            ascii_art.display_section_header("Activity Summary Dashboard")
            print("This dashboard provides a comprehensive overview of your cycling activity.")
        
        # Get user data
        user = self.user_manager.get_current_user()
        username = user.get('username')
        
        # Get user stats 
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        # Check if user has any trips
        if not trips:
            if HAS_RICH:
                no_data_panel = Panel(
                    Text.assemble(
                        ("No cycling data available for visualization!\n\n", "bold red"),
                        ("You need to log some cycling trips before you can view activity summaries.\n", "yellow"),
                        ("Use the 'Log New Trip' feature from the main menu to get started.", "italic cyan")
                    ),
                    box=HEAVY,
                    border_style="yellow",
                    title="[bold red]No Activity Data[/bold red]",
                    title_align="center",
                    padding=(1, 2)
                )
                console.print(Align.center(no_data_panel))
                
                # Prompt to return
                self.ui.prompt_continue("Press Enter to return to the visualization menu")
                return
            else:
                print("\nNo cycling data available for visualization.")
                print("You need to log some cycling trips before you can view activity summaries.")
                input("\nPress Enter to continue...")
                return
        
        try:
            # Process trip data for visualization
            if HAS_RICH:
                # Show processing progress
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold blue]Processing activity data...[/bold blue]"),
                    BarColumn(bar_width=40),
                    expand=True
                ) as progress:
                    task = progress.add_task("Processing", total=len(trips) + 3)
                    
                    # Initialize data structures
                    progress.update(task, advance=1)
                    
                    dates = []
                    distances = []
                    durations = []
                    carbon_saved = []
                    calories_burned = []
                    
                    # Process each trip
                    for trip in trips:
                        date_str = trip.get('date', '')
                        try:
                            # Convert date string to datetime object - handle ISO format with T separator
                            if 'T' in date_str:
                                # Split at T to handle ISO format
                                date_part = date_str.split('T')[0]
                                date = datetime.datetime.strptime(date_part, '%Y-%m-%d').date()
                            else:
                                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                            dates.append(date)
                            
                            # Extract other data
                            distances.append(float(trip.get('distance', 0)))
                            durations.append(float(trip.get('duration', 0)))
                            carbon_saved.append(float(trip.get('carbon_saved', 0)))
                            calories_burned.append(float(trip.get('calories_burned', 0)))
                        except (ValueError, TypeError) as e:
                            logging.error(f"Error processing trip date {date_str}: {e}")
                            # Skip this trip but continue processing
                            continue
                        
                        # Update progress
                        progress.update(task, advance=1)
                    
                    # Calculate summary metrics
                    progress.update(task, advance=1)
                    total_trips = len(dates)
                    total_distance = sum(distances)
                    total_duration = sum(durations)
                    total_carbon = sum(carbon_saved)
                    total_calories = sum(calories_burned)
                    
                    # Calculate averages
                    progress.update(task, advance=1)
                    avg_distance = total_distance / total_trips if total_trips > 0 else 0
                    avg_duration = total_duration / total_trips if total_trips > 0 else 0
                    avg_carbon = total_carbon / total_trips if total_trips > 0 else 0
                    avg_calories = total_calories / total_trips if total_trips > 0 else 0
            else:
                # Process without progress visualization
                print("\nProcessing activity data...")
                
                # Initialize data structures
                dates = []
                distances = []
                durations = []
                carbon_saved = []
                calories_burned = []
                
                # Process each trip
                for trip in trips:
                    date_str = trip.get('date', '')
                    try:
                        # Convert date string to datetime object - handle ISO format with T separator
                        if 'T' in date_str:
                            # Split at T to handle ISO format
                            date_part = date_str.split('T')[0]
                            date = datetime.datetime.strptime(date_part, '%Y-%m-%d').date()
                        else:
                            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                        dates.append(date)
                        
                        # Extract other data
                        distances.append(float(trip.get('distance', 0)))
                        durations.append(float(trip.get('duration', 0)))
                        carbon_saved.append(float(trip.get('carbon_saved', 0)))
                        calories_burned.append(float(trip.get('calories_burned', 0)))
                    except (ValueError, TypeError) as e:
                        logging.error(f"Error processing trip date {date_str}: {e}")
                        # Skip this trip but continue processing
                        continue
                
                # Calculate summary metrics
                total_trips = len(dates)
                total_distance = sum(distances)
                total_duration = sum(durations)
                total_carbon = sum(carbon_saved)
                total_calories = sum(calories_burned)
                
                # Calculate averages
                avg_distance = total_distance / total_trips if total_trips > 0 else 0
                avg_duration = total_duration / total_trips if total_trips > 0 else 0
                avg_carbon = total_carbon / total_trips if total_trips > 0 else 0
                avg_calories = total_calories / total_trips if total_trips > 0 else 0
            
            # Display summary metrics
            if HAS_RICH:
                console.print(Rule("Activity Summary Metrics", style="blue"))
                
                # Create summary metrics table
                metrics_table = Table(
                    show_header=True,
                    header_style="bold cyan",
                    box=ROUNDED,
                    border_style="blue",
                    title="Key Cycling Metrics",
                    title_style="bold blue",
                    title_justify="center"
                )
                
                # Add columns
                metrics_table.add_column("Metric", style="cyan")
                metrics_table.add_column("Total", style="green")
                metrics_table.add_column("Average (per trip)", style="yellow")
                
                # Add rows with formatted values
                metrics_table.add_row(
                    "🚲 Trips", 
                    f"{total_trips:,}", 
                    "—"
                )
                metrics_table.add_row(
                    "📏 Distance (km)", 
                    f"{total_distance:.2f}", 
                    f"{avg_distance:.2f}"
                )
                metrics_table.add_row(
                    "⏱️ Duration (min)", 
                    f"{total_duration:.1f}", 
                    f"{avg_duration:.1f}"
                )
                metrics_table.add_row(
                    "🌱 Carbon Saved (kg)", 
                    f"{total_carbon:.2f}", 
                    f"{avg_carbon:.2f}"
                )
                metrics_table.add_row(
                    "🔥 Calories Burned", 
                    f"{total_calories:.0f}", 
                    f"{avg_calories:.0f}"
                )
                
                console.print(metrics_table)
            else:
                # Display metrics in plain text
                print("\n=== Activity Summary Metrics ===")
                print(f"Total Trips: {total_trips}")
                print(f"Total Distance: {total_distance:.2f} km")
                print(f"Total Duration: {total_duration:.1f} minutes")
                print(f"Total Carbon Saved: {total_carbon:.2f} kg")
                print(f"Total Calories Burned: {total_calories:.0f}")
                print("\nAverages Per Trip:")
                print(f"Average Distance: {avg_distance:.2f} km")
                print(f"Average Duration: {avg_duration:.1f} minutes")
                print(f"Average Carbon Saved: {avg_carbon:.2f} kg")
                print(f"Average Calories Burned: {avg_calories:.0f}")
            
            # Generate visualization
            try:
                # Create figure with multiple subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), dpi=100)
                
                # Sort data by date
                sorted_indices = sorted(range(len(dates)), key=lambda k: dates[k])
                sorted_dates = [dates[i] for i in sorted_indices]
                sorted_distances = [distances[i] for i in sorted_indices]
                sorted_carbon = [carbon_saved[i] for i in sorted_indices]
                
                # Create the top plot for distance over time
                ax1.plot(sorted_dates, sorted_distances, 'o-', color='#3498db', linewidth=2, markersize=8)
                ax1.set_title('Distance Cycled Over Time', fontsize=14, pad=10)
                ax1.set_ylabel('Distance (km)', fontsize=12)
                ax1.grid(True, linestyle='--', alpha=0.7)
                
                # Create the bottom plot for carbon saved
                ax2.plot(sorted_dates, sorted_carbon, 'o-', color='#2ecc71', linewidth=2, markersize=8)
                ax2.set_title('Carbon Saved Over Time', fontsize=14, pad=10)
                ax2.set_xlabel('Date', fontsize=12)
                ax2.set_ylabel('Carbon Saved (kg)', fontsize=12)
                ax2.grid(True, linestyle='--', alpha=0.7)
                
                # Format the date axis for both plots
                for ax in [ax1, ax2]:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # Adjust layout
                plt.tight_layout()
                
                # Save the visualization
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.join(VISUALIZATION_DIR, f"activity_summary_{username}_{timestamp}.png")
                plt.savefig(filename, bbox_inches='tight')
                plt.close(fig)
                
                # Display the visualization
                if HAS_RICH:
                    console.print(Rule("Activity Visualization", style="blue"))
                    
                    # Create success message
                    viz_panel = Panel(
                        f"[bold green]Activity summary visualization has been generated![/bold green]\n\n"
                        f"File saved as: [italic]{filename}[/italic]",
                        title="[bold green]Visualization Created[/bold green]",
                        border_style="green",
                        box=ROUNDED,
                        padding=(1, 2)
                    )
                    console.print(viz_panel)
                    
                    # Ask if user wants to open the visualization
                    if self.ui.open_file_browser(filename):
                        pass
                else:
                    print("\nActivity summary visualization has been generated!")
                    print(f"File saved as: {filename}")
                    
                    # Ask if user wants to open the visualization
                    open_choice = input("\nOpen visualization? (y/n): ")
                    if open_choice.lower() == 'y':
                        self.ui.open_file_browser(filename)
            
            except Exception as e:
                logger.error(f"Error generating activity summary visualization: {e}")
                self.ui.display_error(f"Error generating visualization: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error processing activity data: {e}")
            self.ui.display_error(f"Error processing activity data: {str(e)}")
        
        # Final prompt to return to menu
        self.ui.prompt_continue()
    
    def generate_activity_summary(self, user, output_path):
        """Generate activity summary visualization for reports."""
        # Get user stats
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        if not trips:
            return None
        
        try:
            # Process trip data
            dates = []
            distances = []
            carbon_saved = []
            
            for trip in trips:
                date_str = trip.get('date', '')
                try:
                    # Handle ISO format with T separator
                    if 'T' in date_str:
                        # Split at T to handle ISO format
                        date_part = date_str.split('T')[0]
                        date = datetime.datetime.strptime(date_part, '%Y-%m-%d').date()
                    else:
                        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    dates.append(date)
                    distances.append(float(trip.get('distance', 0)))
                    carbon_saved.append(float(trip.get('carbon_saved', 0)))
                except (ValueError, TypeError):
                    continue
            
            # Create visualization if we have data
            if dates:
                # Sort data by date
                sorted_indices = sorted(range(len(dates)), key=lambda k: dates[k])
                sorted_dates = [dates[i] for i in sorted_indices]
                sorted_distances = [distances[i] for i in sorted_indices]
                
                # Create figure
                fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
                
                # Plot distance over time
                ax.plot(sorted_dates, sorted_distances, 'o-', color='#3498db', linewidth=2, markersize=6)
                ax.set_title('Distance Cycled Over Time', fontsize=12)
                ax.set_xlabel('Date', fontsize=10)
                ax.set_ylabel('Distance (km)', fontsize=10)
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Format the date axis
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # Adjust layout
                plt.tight_layout()
                
                # Save the visualization
                plt.savefig(output_path, bbox_inches='tight')
                plt.close(fig)
                
                return output_path
            
        except Exception as e:
            logger.error(f"Error generating activity summary for report: {e}")
        
        return None
