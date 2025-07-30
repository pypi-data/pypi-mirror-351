"""
EcoCycle - Progress Tracker Visualization Module
Provides functionality to visualize progress over time with trend analysis.
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
from rich.prompt import Prompt, IntPrompt

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"


class ProgressViz:
    """Provides functionality for progress tracking and visualization."""
    
    def __init__(self, user_manager=None, ui=None):
        """Initialize the progress visualization module."""
        self.user_manager = user_manager
        self.ui = ui
    
    def show_progress_over_time(self):
        """Show progress metrics over time with trend analysis."""
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
            header_title = Text("Progress Over Time", style="bold blue")
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
            progress_description = Panel(
                "Track your cycling progress over time with trend analysis and goal comparisons.",
                title="Progress Tracking",
                border_style="blue",
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(progress_description)
        else:
            ascii_art.display_section_header("Progress Over Time")
            print("Track your cycling progress over time with trend analysis and goal comparisons.")
        
        # Get user data
        user = self.user_manager.get_current_user()
        username = user.get('username')
        
        # Get user stats and goals
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        goals = user.get('goals', {})
        
        # Check if user has any trips
        if not trips:
            if HAS_RICH:
                no_data_panel = Panel(
                    Text.assemble(
                        ("No cycling data available for progress analysis!\n\n", "bold red"),
                        ("You need to log some cycling trips before you can track progress.\n", "yellow"),
                        ("Use the 'Log New Trip' feature from the main menu to get started.", "italic cyan")
                    ),
                    box=HEAVY,
                    border_style="yellow",
                    title="[bold red]No Progress Data[/bold red]",
                    title_align="center",
                    padding=(1, 2)
                )
                console.print(Align.center(no_data_panel))
                
                # Prompt to return
                self.ui.prompt_continue("Press Enter to return to the visualization menu")
                return
            else:
                print("\nNo cycling data available for progress analysis.")
                print("You need to log some cycling trips before you can track progress.")
                input("\nPress Enter to continue...")
                return
        
        try:
            # Process progress data for visualization
            if HAS_RICH:
                # Show processing progress
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold blue]Processing progress data...[/bold blue]"),
                    BarColumn(bar_width=40),
                    expand=True
                ) as progress:
                    task = progress.add_task("Processing", total=len(trips) + 5)
                    
                    # Initialize data structures
                    progress.update(task, advance=1)
                    
                    # Sort trips by date
                    trips_sorted = sorted(trips, key=lambda x: x.get('date', ''))
                    
                    # Extract data for visualization
                    dates = []
                    distances = []
                    durations = []
                    carbon_saved = []
                    calories_burned = []
                    
                    # Process each trip
                    for trip in trips_sorted:
                        date_str = trip.get('date', '')
                        try:
                            # Convert date string to datetime object - handle ISO format with T separator
                            date = datetime.datetime.strptime(date_str.split('T')[0] if 'T' in date_str else date_str, '%Y-%m-%d').date()
                            dates.append(date)
                            
                            # Extract trip data
                            distances.append(float(trip.get('distance', 0)))
                            durations.append(float(trip.get('duration', 0)))
                            carbon_saved.append(float(trip.get('carbon_saved', 0)))
                            calories_burned.append(float(trip.get('calories_burned', 0)))
                        except (ValueError, TypeError):
                            # Skip this trip but continue processing
                            continue
                        
                        # Update progress
                        progress.update(task, advance=1)
                    
                    # Calculate weekly data
                    progress.update(task, advance=1)
                    weekly_data = {}
                    for i, date in enumerate(dates):
                        week_key = f"{date.year}-W{date.isocalendar()[1]:02d}"
                        
                        if week_key not in weekly_data:
                            weekly_data[week_key] = {
                                'distance': 0,
                                'duration': 0,
                                'carbon': 0,
                                'calories': 0,
                                'count': 0,
                                'start_date': date,
                                'end_date': date
                            }
                        else:
                            # Update date range
                            weekly_data[week_key]['start_date'] = min(weekly_data[week_key]['start_date'], date)
                            weekly_data[week_key]['end_date'] = max(weekly_data[week_key]['end_date'], date)
                        
                        # Add data to weekly aggregation
                        weekly_data[week_key]['distance'] += distances[i]
                        weekly_data[week_key]['duration'] += durations[i]
                        weekly_data[week_key]['carbon'] += carbon_saved[i]
                        weekly_data[week_key]['calories'] += calories_burned[i]
                        weekly_data[week_key]['count'] += 1
                    
                    # Calculate moving averages
                    progress.update(task, advance=1)
                    window_size = min(4, len(distances))  # Use up to 4 weeks for moving average
                    distance_ma = []
                    
                    # Calculate simple moving average for each point
                    for i in range(len(distances)):
                        start_idx = max(0, i - window_size + 1)
                        distance_ma.append(sum(distances[start_idx:i+1]) / (i - start_idx + 1))
                    
                    # Calculate progress trends
                    progress.update(task, advance=1)
                    if len(distances) >= 2:
                        # Calculate linear regression for trend line
                        x = np.arange(len(distances))
                        y = np.array(distances)
                        z = np.polyfit(x, y, 1)
                        trend_slope = z[0]
                        
                        # Calculate improvement/decline
                        if len(distances) >= 8:  # If we have enough data
                            first_half = distances[:len(distances)//2]
                            second_half = distances[len(distances)//2:]
                            avg_first = sum(first_half) / len(first_half)
                            avg_second = sum(second_half) / len(second_half)
                            pct_change = ((avg_second / avg_first) - 1) * 100 if avg_first > 0 else 0
                        else:
                            pct_change = 0
                    else:
                        trend_slope = 0
                        pct_change = 0
                    
                    # Analyze goal progress
                    progress.update(task, advance=1)
                    weekly_distance_goal = float(goals.get('weekly_distance', 0))
                    weekly_trips_goal = int(goals.get('weekly_trips', 0))
                    
                    # Get current week data
                    now = datetime.datetime.now().date()
                    current_week = f"{now.year}-W{now.isocalendar()[1]:02d}"
                    current_week_data = weekly_data.get(current_week, {
                        'distance': 0, 'count': 0, 'duration': 0,
                        'carbon': 0, 'calories': 0
                    })
                    
                    # Calculate goal completion percentages
                    distance_goal_pct = (current_week_data['distance'] / weekly_distance_goal * 100) if weekly_distance_goal > 0 else 0
                    trips_goal_pct = (current_week_data['count'] / weekly_trips_goal * 100) if weekly_trips_goal > 0 else 0
            else:
                # Process without progress visualization
                print("\nProcessing progress data...")
                
                # Sort trips by date
                trips_sorted = sorted(trips, key=lambda x: x.get('date', ''))
                
                # Extract data for visualization
                dates = []
                distances = []
                durations = []
                carbon_saved = []
                calories_burned = []
                
                # Process each trip
                for trip in trips_sorted:
                    date_str = trip.get('date', '')
                    try:
                        # Convert date string to datetime object - handle ISO format with T separator
                        date = datetime.datetime.strptime(date_str.split('T')[0] if 'T' in date_str else date_str, '%Y-%m-%d').date()
                        dates.append(date)
                        
                        # Extract trip data
                        distances.append(float(trip.get('distance', 0)))
                        durations.append(float(trip.get('duration', 0)))
                        carbon_saved.append(float(trip.get('carbon_saved', 0)))
                        calories_burned.append(float(trip.get('calories_burned', 0)))
                    except (ValueError, TypeError):
                        # Skip this trip but continue processing
                        continue
                
                # Calculate weekly data
                weekly_data = {}
                for i, date in enumerate(dates):
                    week_key = f"{date.year}-W{date.isocalendar()[1]:02d}"
                    
                    if week_key not in weekly_data:
                        weekly_data[week_key] = {
                            'distance': 0,
                            'duration': 0,
                            'carbon': 0,
                            'calories': 0,
                            'count': 0,
                            'start_date': date,
                            'end_date': date
                        }
                    else:
                        # Update date range
                        weekly_data[week_key]['start_date'] = min(weekly_data[week_key]['start_date'], date)
                        weekly_data[week_key]['end_date'] = max(weekly_data[week_key]['end_date'], date)
                    
                    # Add data to weekly aggregation
                    weekly_data[week_key]['distance'] += distances[i]
                    weekly_data[week_key]['duration'] += durations[i]
                    weekly_data[week_key]['carbon'] += carbon_saved[i]
                    weekly_data[week_key]['calories'] += calories_burned[i]
                    weekly_data[week_key]['count'] += 1
                
                # Calculate moving averages
                window_size = min(4, len(distances))  # Use up to 4 weeks for moving average
                distance_ma = []
                
                # Calculate simple moving average for each point
                for i in range(len(distances)):
                    start_idx = max(0, i - window_size + 1)
                    distance_ma.append(sum(distances[start_idx:i+1]) / (i - start_idx + 1))
                
                # Calculate progress trends
                if len(distances) >= 2:
                    # Calculate linear regression for trend line
                    x = np.arange(len(distances))
                    y = np.array(distances)
                    z = np.polyfit(x, y, 1)
                    trend_slope = z[0]
                    
                    # Calculate improvement/decline
                    if len(distances) >= 8:  # If we have enough data
                        first_half = distances[:len(distances)//2]
                        second_half = distances[len(distances)//2:]
                        avg_first = sum(first_half) / len(first_half)
                        avg_second = sum(second_half) / len(second_half)
                        pct_change = ((avg_second / avg_first) - 1) * 100 if avg_first > 0 else 0
                    else:
                        pct_change = 0
                else:
                    trend_slope = 0
                    pct_change = 0
                
                # Analyze goal progress
                weekly_distance_goal = float(goals.get('weekly_distance', 0))
                weekly_trips_goal = int(goals.get('weekly_trips', 0))
                
                # Get current week data
                now = datetime.datetime.now().date()
                current_week = f"{now.year}-W{now.isocalendar()[1]:02d}"
                current_week_data = weekly_data.get(current_week, {
                    'distance': 0, 'count': 0, 'duration': 0,
                    'carbon': 0, 'calories': 0
                })
                
                # Calculate goal completion percentages
                distance_goal_pct = (current_week_data['distance'] / weekly_distance_goal * 100) if weekly_distance_goal > 0 else 0
                trips_goal_pct = (current_week_data['count'] / weekly_trips_goal * 100) if weekly_trips_goal > 0 else 0
            
            # Display progress analysis
            if HAS_RICH:
                console.print(Rule("Progress Analysis", style="blue"))
                
                # Create progress trend panel with color based on trend
                trend_color = "green" if trend_slope > 0 else "red" if trend_slope < 0 else "yellow"
                trend_icon = "📈" if trend_slope > 0 else "📉" if trend_slope < 0 else "➡️"
                trend_description = "improving" if trend_slope > 0 else "declining" if trend_slope < 0 else "stable"
                
                trend_panel = Panel(
                    Text.assemble(
                        (f"{trend_icon} Your cycling distance is ", "bold"),
                        (f"{trend_description}", f"bold {trend_color}"),
                        (".\n\n", "bold"),
                        (f"Overall distance trend: ", ""),
                        (f"{pct_change:+.1f}% ", f"{trend_color}"),
                        ("change between first and second half of your data.\n", ""),
                        ("\nLong-term consistency is key to achieving your fitness goals!", "italic")
                    ),
                    title="[bold blue]Trend Analysis[/bold blue]",
                    border_style="blue",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(trend_panel)
                
                # Display current week's goal progress
                if weekly_distance_goal > 0 or weekly_trips_goal > 0:
                    console.print(Rule("Weekly Goal Progress", style="blue"))
                    
                    goal_panel = Panel(
                        Text.assemble(
                            ("This Week's Progress:\n\n", "bold"),
                            ("Distance Goal: ", "bold"),
                            (f"{current_week_data['distance']:.1f} km", "cyan"),
                            (" of ", ""),
                            (f"{weekly_distance_goal:.1f} km", "green"),
                            (f" ({distance_goal_pct:.1f}%)\n", "yellow"),
                            ("Trips Goal: ", "bold"),
                            (f"{current_week_data['count']}", "cyan"),
                            (" of ", ""),
                            (f"{weekly_trips_goal}", "green"),
                            (f" ({trips_goal_pct:.1f}%)", "yellow")
                        ),
                        title="[bold blue]Goal Tracking[/bold blue]",
                        border_style="blue",
                        box=ROUNDED,
                        padding=(1, 2)
                    )
                    console.print(goal_panel)
                
                # Display weekly summary
                if weekly_data:
                    console.print(Rule("Weekly Activity Summary", style="blue"))
                    
                    # Create weekly data table
                    weekly_table = Table(
                        show_header=True,
                        header_style="bold blue",
                        box=ROUNDED,
                        border_style="blue",
                        title="Weekly Activity Breakdown",
                        title_style="bold blue"
                    )
                    
                    # Add columns
                    weekly_table.add_column("Week", style="cyan")
                    weekly_table.add_column("Distance (km)", style="green", justify="right")
                    weekly_table.add_column("Trips", style="yellow", justify="right")
                    weekly_table.add_column("Duration (min)", style="magenta", justify="right")
                    weekly_table.add_column("Calories", style="red", justify="right")
                    
                    # Add rows with weekly data (most recent first)
                    for week in sorted(weekly_data.keys(), reverse=True)[:10]:  # Show last 10 weeks
                        data = weekly_data[week]
                        weekly_table.add_row(
                            week,
                            f"{data['distance']:.1f}",
                            f"{data['count']}",
                            f"{data['duration']:.0f}",
                            f"{data['calories']:.0f}"
                        )
                    
                    console.print(weekly_table)
            else:
                # Display in plain text format
                print("\n=== Progress Analysis ===")
                
                # Display trend information
                trend_description = "improving" if trend_slope > 0 else "declining" if trend_slope < 0 else "stable"
                print(f"Your cycling distance is {trend_description}.")
                print(f"Overall distance trend: {pct_change:+.1f}% change between first and second half.")
                print("Long-term consistency is key to achieving your fitness goals!")
                
                # Display current week's goal progress
                if weekly_distance_goal > 0 or weekly_trips_goal > 0:
                    print("\n=== Weekly Goal Progress ===")
                    print(f"Distance Goal: {current_week_data['distance']:.1f} km of {weekly_distance_goal:.1f} km ({distance_goal_pct:.1f}%)")
                    print(f"Trips Goal: {current_week_data['count']} of {weekly_trips_goal} ({trips_goal_pct:.1f}%)")
                
                # Display weekly summary
                if weekly_data:
                    print("\n=== Weekly Activity Summary ===")
                    
                    # Print header
                    print("\n{:<12} {:<15} {:<10} {:<15} {:<15}".format(
                        "Week", "Distance (km)", "Trips", "Duration (min)", "Calories"
                    ))
                    print("-" * 70)
                    
                    # Print weekly data (most recent first)
                    for week in sorted(weekly_data.keys(), reverse=True)[:10]:  # Show last 10 weeks
                        data = weekly_data[week]
                        print("{:<12} {:<15.1f} {:<10} {:<15.0f} {:<15.0f}".format(
                            week,
                            data['distance'],
                            data['count'],
                            data['duration'],
                            data['calories']
                        ))
            
            # Generate visualization
            try:
                # Create figure with multiple subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), dpi=100)
                
                # Create the top plot for distance over time
                ax1.plot(dates, distances, 'o-', color='#3498db', linewidth=2, alpha=0.6, label='Distance')
                ax1.plot(dates, distance_ma, '--', color='#e74c3c', linewidth=2, label='Moving Avg (4 trips)')
                
                # Add trend line if we have enough data
                if len(distances) >= 2:
                    x = np.arange(len(distances))
                    z = np.polyfit(x, distances, 1)
                    p = np.poly1d(z)
                    ax1.plot(dates, p(x), '-', color='#2ecc71', linewidth=2, label='Trend')
                
                ax1.set_title('Distance Progression Over Time', fontsize=14, pad=10)
                ax1.set_ylabel('Distance (km)', fontsize=12)
                ax1.grid(True, linestyle='--', alpha=0.7)
                ax1.legend(loc='upper left')
                
                # Create the bottom plot for weekly activity
                if weekly_data:
                    weeks = sorted(weekly_data.keys())
                    week_labels = weeks
                    weekly_distances = [weekly_data[week]['distance'] for week in weeks]
                    weekly_counts = [weekly_data[week]['count'] for week in weeks]
                    
                    # Plot both distance and trip count
                    ax2_dist = ax2
                    ax2_dist.bar(week_labels, weekly_distances, color='#3498db', alpha=0.7, label='Distance')
                    ax2_dist.set_ylabel('Distance (km)', fontsize=12, color='#3498db')
                    ax2_dist.tick_params(axis='y', labelcolor='#3498db')
                    
                    # Create a twin axis for trip count
                    ax2_count = ax2.twinx()
                    ax2_count.plot(week_labels, weekly_counts, 'o-', color='#e74c3c', linewidth=2, label='Trips')
                    ax2_count.set_ylabel('Number of Trips', fontsize=12, color='#e74c3c')
                    ax2_count.tick_params(axis='y', labelcolor='#e74c3c')
                    
                    # Add legend and title
                    lines1, labels1 = ax2_dist.get_legend_handles_labels()
                    lines2, labels2 = ax2_count.get_legend_handles_labels()
                    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
                    
                    ax2.set_title('Weekly Activity Summary', fontsize=14, pad=10)
                    ax2.set_xlabel('Week', fontsize=12)
                    ax2.grid(True, linestyle='--', alpha=0.7)
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # Format the date axis for the top plot
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # Adjust layout
                plt.tight_layout()
                
                # Save the visualization
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.join(VISUALIZATION_DIR, f"progress_analysis_{username}_{timestamp}.png")
                plt.savefig(filename, bbox_inches='tight')
                plt.close(fig)
                
                # Display the visualization
                if HAS_RICH:
                    console.print(Rule("Progress Visualization", style="blue"))
                    
                    # Create success message
                    viz_panel = Panel(
                        f"[bold green]Progress visualization has been generated![/bold green]\n\n"
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
                    print("\nProgress visualization has been generated!")
                    print(f"File saved as: {filename}")
                    
                    # Ask if user wants to open the visualization
                    open_choice = input("\nOpen visualization? (y/n): ")
                    if open_choice.lower() == 'y':
                        self.ui.open_file_browser(filename)
            
            except Exception as e:
                logger.error(f"Error generating progress analysis visualization: {e}")
                self.ui.display_error(f"Error generating visualization: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error processing progress data: {e}")
            self.ui.display_error(f"Error processing progress data: {str(e)}")
        
        # Final prompt to return to menu
        self.ui.prompt_continue()
    
    def generate_progress_visualization(self, user, output_path):
        """Generate progress visualization for reports."""
        # Get user stats
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        if not trips:
            return None
        
        try:
            # Process trip data
            trips_sorted = sorted(trips, key=lambda x: x.get('date', ''))
            
            dates = []
            distances = []
            
            for trip in trips_sorted:
                date_str = trip.get('date', '')
                try:
                    # Handle ISO format with T separator
                    date = datetime.datetime.strptime(date_str.split('T')[0] if 'T' in date_str else date_str, '%Y-%m-%d').date()
                    dates.append(date)
                    distances.append(float(trip.get('distance', 0)))
                except (ValueError, TypeError):
                    continue
            
            # Create visualization if we have data
            if dates:
                # Calculate moving average
                window_size = min(4, len(distances))
                distance_ma = []
                
                for i in range(len(distances)):
                    start_idx = max(0, i - window_size + 1)
                    distance_ma.append(sum(distances[start_idx:i+1]) / (i - start_idx + 1))
                
                # Create figure
                fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
                
                # Plot distance and moving average
                ax.plot(dates, distances, 'o-', color='#3498db', linewidth=2, alpha=0.6, label='Distance')
                ax.plot(dates, distance_ma, '--', color='#e74c3c', linewidth=2, label='Moving Avg')
                
                # Add trend line if we have enough data
                if len(distances) >= 2:
                    x = np.arange(len(distances))
                    z = np.polyfit(x, distances, 1)
                    p = np.poly1d(z)
                    ax.plot(dates, p(x), '-', color='#2ecc71', linewidth=2, label='Trend')
                
                ax.set_title('Distance Progression', fontsize=12)
                ax.set_xlabel('Date', fontsize=10)
                ax.set_ylabel('Distance (km)', fontsize=10)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend(loc='upper left')
                
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
            logger.error(f"Error generating progress visualization for report: {e}")
        
        return None
