"""
EcoCycle - Trip History Analysis Module
Provides functionality to analyze and visualize trip history data.
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
from rich.prompt import IntPrompt

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"


class TripHistoryViz:
    """Provides functionality for trip history analysis and visualization."""
    
    def __init__(self, user_manager=None, ui=None):
        """Initialize the trip history analysis module."""
        self.user_manager = user_manager
        self.ui = ui
    
    def analyze_trip_history(self):
        """Analyze trip history with detailed visualizations."""
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
            header_title = Text("Trip History Analysis", style="bold green")
            header_panel = Panel(
                Align.center(header_title),
                box=DOUBLE,
                border_style="green",
                padding=(1, 2)
            )
            layout["header"].update(header_panel)
            
            # Display the header
            console.print(layout["header"])
            
            # Add descriptive panel
            summary_description = Panel(
                "Analyze your cycling trip history with detailed visualizations and insights.",
                title="Analysis Description",
                border_style="green",
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(summary_description)
        else:
            ascii_art.display_section_header("Trip History Analysis")
            print("Analyze your cycling trip history with detailed visualizations and insights.")
        
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
                        ("No trip history available for analysis!\n\n", "bold red"),
                        ("You need to log some cycling trips before you can analyze trip history.\n", "yellow"),
                        ("Use the 'Log New Trip' feature from the main menu to get started.", "italic cyan")
                    ),
                    box=HEAVY,
                    border_style="yellow",
                    title="[bold red]No Trip Data[/bold red]",
                    title_align="center",
                    padding=(1, 2)
                )
                console.print(Align.center(no_data_panel))
                
                # Prompt to return
                self.ui.prompt_continue("Press Enter to return to the visualization menu")
                return
            else:
                print("\nNo trip history available for analysis.")
                print("You need to log some cycling trips before you can analyze trip history.")
                input("\nPress Enter to continue...")
                return
        
        try:
            # Process trip data for visualization
            if HAS_RICH:
                # Show processing progress
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold green]Processing trip history data...[/bold green]"),
                    BarColumn(bar_width=40),
                    expand=True
                ) as progress:
                    task = progress.add_task("Processing", total=len(trips) + 4)
                    
                    # Initialize data structures
                    progress.update(task, advance=1)
                    
                    # Sort trips by date (newest first)
                    trips_sorted = sorted(trips, key=lambda x: x.get('date', ''), reverse=True)
                    
                    # Extract data for visualization
                    dates = []
                    distances = []
                    durations = []
                    speed_estimates = []
                    
                    # Process each trip
                    for trip in trips:
                        date_str = trip.get('date', '')
                        try:
                            # Convert date string to datetime object
                            # Handle ISO format with T separator
                            if 'T' in date_str:
                                date_part = date_str.split('T')[0]
                                date = datetime.datetime.strptime(date_part, '%Y-%m-%d').date()
                            else:
                                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                            dates.append(date)
                            
                            # Extract distance and duration
                            distance = float(trip.get('distance', 0))
                            duration = float(trip.get('duration', 0))
                            
                            distances.append(distance)
                            durations.append(duration)
                            
                            # Calculate speed estimate (km/h) if duration > 0
                            if duration > 0:
                                # Convert duration from minutes to hours
                                speed = distance / (duration / 60)
                                speed_estimates.append(speed)
                            else:
                                speed_estimates.append(0)
                        except (ValueError, TypeError):
                            # Skip this trip but continue processing
                            continue
                        
                        # Update progress
                        progress.update(task, advance=1)
                    
                    # Create trip mapping for display
                    progress.update(task, advance=1)
                    trip_mapping = {}
                    for i, trip in enumerate(trips_sorted):
                        trip_mapping[i+1] = trip
                    
                    # Find trip trends
                    progress.update(task, advance=1)
                    avg_speed = sum(speed_estimates) / len(speed_estimates) if speed_estimates else 0
                    max_distance = max(distances) if distances else 0
                    max_duration = max(durations) if durations else 0
                    
                    # Calculate weekly totals
                    progress.update(task, advance=1)
                    weekly_totals = {}
                    for i, date in enumerate(dates):
                        week_num = date.isocalendar()[1]  # ISO week number
                        year = date.year
                        week_key = f"{year}-W{week_num:02d}"
                        
                        if week_key not in weekly_totals:
                            weekly_totals[week_key] = {
                                'distance': 0,
                                'duration': 0,
                                'count': 0
                            }
                        
                        weekly_totals[week_key]['distance'] += distances[i]
                        weekly_totals[week_key]['duration'] += durations[i]
                        weekly_totals[week_key]['count'] += 1
            else:
                # Process without progress visualization
                print("\nProcessing trip history data...")
                
                # Sort trips by date (newest first)
                trips_sorted = sorted(trips, key=lambda x: x.get('date', ''), reverse=True)
                
                # Extract data for visualization
                dates = []
                distances = []
                durations = []
                speed_estimates = []
                
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
                        
                        # Extract distance and duration
                        distance = float(trip.get('distance', 0))
                        duration = float(trip.get('duration', 0))
                        
                        distances.append(distance)
                        durations.append(duration)
                        
                        # Calculate speed estimate (km/h) if duration > 0
                        if duration > 0:
                            # Convert duration from minutes to hours
                            speed = distance / (duration / 60)
                            speed_estimates.append(speed)
                        else:
                            speed_estimates.append(0)
                    except (ValueError, TypeError):
                        # Skip this trip but continue processing
                        continue
                
                # Create trip mapping for display
                trip_mapping = {}
                for i, trip in enumerate(trips_sorted):
                    trip_mapping[i+1] = trip
                
                # Find trip trends
                avg_speed = sum(speed_estimates) / len(speed_estimates) if speed_estimates else 0
                max_distance = max(distances) if distances else 0
                max_duration = max(durations) if durations else 0
                
                # Calculate weekly totals
                weekly_totals = {}
                for i, date in enumerate(dates):
                    week_num = date.isocalendar()[1]  # ISO week number
                    year = date.year
                    week_key = f"{year}-W{week_num:02d}"
                    
                    if week_key not in weekly_totals:
                        weekly_totals[week_key] = {
                            'distance': 0,
                            'duration': 0,
                            'count': 0
                        }
                    
                    weekly_totals[week_key]['distance'] += distances[i]
                    weekly_totals[week_key]['duration'] += durations[i]
                    weekly_totals[week_key]['count'] += 1
            
            # Display recent trips table
            if HAS_RICH:
                console.print(Rule("Recent Trips", style="green"))
                
                # Create recent trips table
                recent_table = Table(
                    show_header=True,
                    header_style="bold green",
                    box=ROUNDED,
                    border_style="green",
                    title="Your Most Recent Cycling Trips",
                    title_style="bold green",
                    title_justify="center"
                )
                
                # Add columns
                recent_table.add_column("#", style="dim", width=4)
                recent_table.add_column("Date", style="cyan")
                recent_table.add_column("Distance (km)", style="yellow", justify="right")
                recent_table.add_column("Duration (min)", style="magenta", justify="right")
                recent_table.add_column("Speed (km/h)", style="green", justify="right")
                recent_table.add_column("Notes", style="blue")
                
                # Add rows for recent trips (up to 10)
                display_count = min(10, len(trips_sorted))
                for i in range(display_count):
                    trip = trips_sorted[i]
                    
                    # Extract trip data
                    date = trip.get('date', 'Unknown')
                    distance = float(trip.get('distance', 0))
                    duration = float(trip.get('duration', 0))
                    notes = trip.get('notes', '')
                    
                    # Calculate speed
                    speed = distance / (duration / 60) if duration > 0 else 0
                    
                    # Add row to table
                    recent_table.add_row(
                        f"{i+1}",
                        date,
                        f"{distance:.2f}",
                        f"{duration:.1f}",
                        f"{speed:.1f}",
                        notes[:30] + ('...' if len(notes) > 30 else '')
                    )
                
                console.print(recent_table)
                
                # Display trip stats
                console.print(Rule("Trip Statistics", style="green"))
                
                # Create stats table
                stats_table = Table(
                    show_header=True,
                    header_style="bold green",
                    box=ROUNDED,
                    border_style="green",
                    title="Trip Statistics Summary",
                    title_style="bold green",
                    title_justify="center"
                )
                
                # Add columns
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="yellow")
                stats_table.add_column("Details", style="green")
                
                # Add rows with statistics
                stats_table.add_row(
                    "Total Trips", 
                    f"{len(trips)}",
                    f"Lifetime cycling activities"
                )
                stats_table.add_row(
                    "Average Speed", 
                    f"{avg_speed:.1f} km/h",
                    f"Based on {len(speed_estimates)} trips with duration"
                )
                stats_table.add_row(
                    "Max Distance", 
                    f"{max_distance:.1f} km",
                    f"Your longest cycling trip"
                )
                stats_table.add_row(
                    "Max Duration", 
                    f"{max_duration:.1f} min",
                    f"Your longest cycling session"
                )
                stats_table.add_row(
                    "Weekly Average", 
                    f"{sum(d['count'] for d in weekly_totals.values()) / len(weekly_totals):.1f} trips" if weekly_totals else "0 trips",
                    f"Based on {len(weekly_totals)} weeks with activity"
                )
                
                console.print(stats_table)
            else:
                # Display in ASCII format
                print("\n=== Recent Trips ===")
                
                # Add header
                print("\n{:<5} {:<12} {:<15} {:<15} {:<15} {:<20}".format(
                    "#", "Date", "Distance (km)", "Duration (min)", "Speed (km/h)", "Notes"
                ))
                print("-" * 80)
                
                # Add rows for recent trips (up to 10)
                display_count = min(10, len(trips_sorted))
                for i in range(display_count):
                    trip = trips_sorted[i]
                    
                    # Extract trip data
                    date = trip.get('date', 'Unknown')
                    distance = float(trip.get('distance', 0))
                    duration = float(trip.get('duration', 0))
                    notes = trip.get('notes', '')
                    
                    # Calculate speed
                    speed = distance / (duration / 60) if duration > 0 else 0
                    
                    # Print row
                    print("{:<5} {:<12} {:<15.2f} {:<15.1f} {:<15.1f} {:<20}".format(
                        i+1,
                        date,
                        distance,
                        duration,
                        speed,
                        notes[:20] + ('...' if len(notes) > 20 else '')
                    ))
                
                # Display trip stats
                print("\n=== Trip Statistics ===")
                print(f"Total Trips: {len(trips)}")
                print(f"Average Speed: {avg_speed:.1f} km/h")
                print(f"Max Distance: {max_distance:.1f} km")
                print(f"Max Duration: {max_duration:.1f} min")
                if weekly_totals:
                    print(f"Weekly Average: {sum(d['count'] for d in weekly_totals.values()) / len(weekly_totals):.1f} trips")
                else:
                    print("Weekly Average: 0 trips")
            
            # Generate visualization
            try:
                # Create figure with multiple subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), dpi=100)
                
                # Sort data by date
                sorted_indices = sorted(range(len(dates)), key=lambda k: dates[k])
                sorted_dates = [dates[i] for i in sorted_indices]
                sorted_distances = [distances[i] for i in sorted_indices]
                sorted_speeds = [speed_estimates[i] for i in sorted_indices]
                
                # Create the top plot for distance over time
                ax1.plot(sorted_dates, sorted_distances, 'o-', color='#27ae60', linewidth=2, markersize=8)
                ax1.set_title('Trip Distances Over Time', fontsize=14, pad=10)
                ax1.set_ylabel('Distance (km)', fontsize=12)
                ax1.grid(True, linestyle='--', alpha=0.7)
                
                # Create the bottom plot for speed
                ax2.plot(sorted_dates, sorted_speeds, 'o-', color='#f39c12', linewidth=2, markersize=8)
                ax2.set_title('Cycling Speed Over Time', fontsize=14, pad=10)
                ax2.set_xlabel('Date', fontsize=12)
                ax2.set_ylabel('Speed (km/h)', fontsize=12)
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
                filename = os.path.join(VISUALIZATION_DIR, f"trip_history_{username}_{timestamp}.png")
                plt.savefig(filename, bbox_inches='tight')
                plt.close(fig)
                
                # Display the visualization
                if HAS_RICH:
                    console.print(Rule("Trip History Visualization", style="green"))
                    
                    # Create success message
                    viz_panel = Panel(
                        f"[bold green]Trip history visualization has been generated![/bold green]\n\n"
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
                    print("\nTrip history visualization has been generated!")
                    print(f"File saved as: {filename}")
                    
                    # Ask if user wants to open the visualization
                    open_choice = input("\nOpen visualization? (y/n): ")
                    if open_choice.lower() == 'y':
                        self.ui.open_file_browser(filename)
            
            except Exception as e:
                logger.error(f"Error generating trip history visualization: {e}")
                self.ui.display_error(f"Error generating visualization: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error processing trip history data: {e}")
            self.ui.display_error(f"Error processing trip history data: {str(e)}")
        
        # Final prompt to return to menu
        self.ui.prompt_continue()
