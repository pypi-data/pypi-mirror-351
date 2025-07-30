"""
EcoCycle - Carbon Savings Visualization Module
Provides functionality to visualize carbon savings and environmental impact.
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
from rich.prompt import Prompt

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"


class CarbonSavingsViz:
    """Provides functionality for carbon savings visualization."""
    
    def __init__(self, user_manager=None, ui=None):
        """Initialize the carbon savings visualization module."""
        self.user_manager = user_manager
        self.ui = ui
    
    def visualize_carbon_savings(self):
        """Visualize carbon savings with comparisons and analytics."""
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
            header_title = Text("Carbon Savings Visualization", style="bold green")
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
            carbon_description = Panel(
                "Visualize your environmental impact and carbon savings from cycling activities.",
                title="Environmental Impact",
                border_style="green",
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(carbon_description)
        else:
            ascii_art.display_section_header("Carbon Savings Visualization")
            print("Visualize your environmental impact and carbon savings from cycling activities.")
        
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
                        ("No cycling data available for carbon analysis!\n\n", "bold red"),
                        ("You need to log some cycling trips before you can visualize carbon savings.\n", "yellow"),
                        ("Use the 'Log New Trip' feature from the main menu to get started.", "italic cyan")
                    ),
                    box=HEAVY,
                    border_style="yellow",
                    title="[bold red]No Carbon Data[/bold red]",
                    title_align="center",
                    padding=(1, 2)
                )
                console.print(Align.center(no_data_panel))
                
                # Prompt to return
                self.ui.prompt_continue("Press Enter to return to the visualization menu")
                return
            else:
                print("\nNo cycling data available for carbon analysis.")
                print("You need to log some cycling trips before you can visualize carbon savings.")
                input("\nPress Enter to continue...")
                return
        
        try:
            # Process carbon data for visualization
            if HAS_RICH:
                # Show processing progress
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold green]Processing carbon savings data...[/bold green]"),
                    BarColumn(bar_width=40),
                    expand=True
                ) as progress:
                    task = progress.add_task("Processing", total=len(trips) + 4)
                    
                    # Initialize data structures
                    progress.update(task, advance=1)
                    
                    dates = []
                    distances = []
                    carbon_saved = []
                    
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
                            
                            # Extract data
                            distances.append(float(trip.get('distance', 0)))
                            carbon_saved.append(float(trip.get('carbon_saved', 0)))
                        except (ValueError, TypeError):
                            # Skip this trip but continue processing
                            continue
                        
                        # Update progress
                        progress.update(task, advance=1)
                    
                    # Calculate aggregated data
                    progress.update(task, advance=1)
                    total_carbon_saved = sum(carbon_saved)
                    total_distance = sum(distances)
                    
                    # Calculate monthly data
                    progress.update(task, advance=1)
                    monthly_data = {}
                    for i, date in enumerate(dates):
                        month_key = f"{date.year}-{date.month:02d}"
                        
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {
                                'carbon': 0,
                                'distance': 0,
                                'count': 0
                            }
                        
                        monthly_data[month_key]['carbon'] += carbon_saved[i]
                        monthly_data[month_key]['distance'] += distances[i]
                        monthly_data[month_key]['count'] += 1
                    
                    # Calculate carbon equivalents
                    progress.update(task, advance=1)
                    # These are approximate equivalence values
                    trees_planted = total_carbon_saved / 21.8  # kg CO2 per tree per year
                    car_km_equivalent = total_carbon_saved / 0.12  # kg CO2 per km for average car
                    phone_charges = total_carbon_saved * 10000  # phone charges per kg CO2
                    
                    # Sort monthly data
                    sorted_months = sorted(monthly_data.keys())
                    monthly_carbon = [monthly_data[month]['carbon'] for month in sorted_months]
                    month_labels = [month.replace('-', '/') for month in sorted_months]
            else:
                # Process without progress visualization
                print("\nProcessing carbon savings data...")
                
                # Initialize data structures
                dates = []
                distances = []
                carbon_saved = []
                
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
                        
                        # Extract data
                        distances.append(float(trip.get('distance', 0)))
                        carbon_saved.append(float(trip.get('carbon_saved', 0)))
                    except (ValueError, TypeError):
                        # Skip this trip but continue processing
                        continue
                
                # Calculate aggregated data
                total_carbon_saved = sum(carbon_saved)
                total_distance = sum(distances)
                
                # Calculate monthly data
                monthly_data = {}
                for i, date in enumerate(dates):
                    month_key = f"{date.year}-{date.month:02d}"
                    
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {
                            'carbon': 0,
                            'distance': 0,
                            'count': 0
                        }
                    
                    monthly_data[month_key]['carbon'] += carbon_saved[i]
                    monthly_data[month_key]['distance'] += distances[i]
                    monthly_data[month_key]['count'] += 1
                
                # Calculate carbon equivalents
                # These are approximate equivalence values
                trees_planted = total_carbon_saved / 21.8  # kg CO2 per tree per year
                car_km_equivalent = total_carbon_saved / 0.12  # kg CO2 per km for average car
                phone_charges = total_carbon_saved * 10000  # phone charges per kg CO2
                
                # Sort monthly data
                sorted_months = sorted(monthly_data.keys())
                monthly_carbon = [monthly_data[month]['carbon'] for month in sorted_months]
                month_labels = [month.replace('-', '/') for month in sorted_months]
            
            # Display carbon savings information
            if HAS_RICH:
                console.print(Rule("Carbon Savings Impact", style="green"))
                
                # Create carbon savings summary panel
                impact_panel = Panel(
                    Text.assemble(
                        ("Your cycling activities have saved a total of ", "bold"),
                        (f"{total_carbon_saved:.2f} kg", "bold green"),
                        (" of CO₂ emissions!\n\n", "bold"),
                        ("This is equivalent to:\n", "italic"),
                        ("🌳 ", ""),
                        (f"Planting {trees_planted:.1f} trees for one year\n", "green"),
                        ("🚗 ", ""),
                        (f"Not driving {car_km_equivalent:.1f} km in an average car\n", "cyan"),
                        ("📱 ", ""),
                        (f"Charging your smartphone {phone_charges:.0f} times", "yellow")
                    ),
                    title="[bold green]Environmental Impact[/bold green]",
                    border_style="green",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(impact_panel)
                
                # Display monthly summary if available
                if monthly_data:
                    console.print(Rule("Monthly Carbon Savings", style="green"))
                    
                    # Create monthly data table
                    monthly_table = Table(
                        show_header=True,
                        header_style="bold green",
                        box=ROUNDED,
                        border_style="green",
                        title="Carbon Savings by Month",
                        title_style="bold green"
                    )
                    
                    # Add columns
                    monthly_table.add_column("Month", style="cyan")
                    monthly_table.add_column("Carbon Saved (kg)", style="green", justify="right")
                    monthly_table.add_column("Distance (km)", style="blue", justify="right")
                    monthly_table.add_column("Trips", style="yellow", justify="right")
                    
                    # Add rows with monthly data (most recent first)
                    for month in reversed(sorted_months):
                        data = monthly_data[month]
                        monthly_table.add_row(
                            month.replace('-', '/'),
                            f"{data['carbon']:.2f}",
                            f"{data['distance']:.1f}",
                            f"{data['count']}"
                        )
                    
                    console.print(monthly_table)
            else:
                # Display in plain text format
                print("\n=== Carbon Savings Impact ===")
                print(f"Your cycling activities have saved a total of {total_carbon_saved:.2f} kg of CO₂ emissions!")
                print("\nThis is equivalent to:")
                print(f"🌳 Planting {trees_planted:.1f} trees for one year")
                print(f"🚗 Not driving {car_km_equivalent:.1f} km in an average car")
                print(f"📱 Charging your smartphone {phone_charges:.0f} times")
                
                # Display monthly summary if available
                if monthly_data:
                    print("\n=== Monthly Carbon Savings ===")
                    print("\n{:<10} {:<20} {:<15} {:<10}".format(
                        "Month", "Carbon Saved (kg)", "Distance (km)", "Trips"
                    ))
                    print("-" * 60)
                    
                    # Add rows with monthly data (most recent first)
                    for month in reversed(sorted_months):
                        data = monthly_data[month]
                        print("{:<10} {:<20.2f} {:<15.1f} {:<10}".format(
                            month.replace('-', '/'),
                            data['carbon'],
                            data['distance'],
                            data['count']
                        ))
            
            # Generate visualization
            try:
                # Create figure with multiple subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), dpi=100)
                
                # Sort data by date for time series plot
                sorted_indices = sorted(range(len(dates)), key=lambda k: dates[k])
                sorted_dates = [dates[i] for i in sorted_indices]
                sorted_carbon = [carbon_saved[i] for i in sorted_indices]
                
                # Create the top plot for cumulative carbon savings
                cumulative_carbon = np.cumsum(sorted_carbon)
                ax1.plot(sorted_dates, cumulative_carbon, '-', color='#2ecc71', linewidth=3)
                ax1.set_title('Cumulative Carbon Savings Over Time', fontsize=14, pad=10)
                ax1.set_ylabel('Carbon Saved (kg)', fontsize=12)
                ax1.grid(True, linestyle='--', alpha=0.7)
                
                # Create the bottom plot for monthly carbon savings
                if monthly_data:
                    ax2.bar(month_labels, monthly_carbon, color='#27ae60')
                    ax2.set_title('Monthly Carbon Savings', fontsize=14, pad=10)
                    ax2.set_xlabel('Month', fontsize=12)
                    ax2.set_ylabel('Carbon Saved (kg)', fontsize=12)
                    ax2.grid(True, linestyle='--', alpha=0.7, axis='y')
                    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # Format the date axis for the top plot
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
                
                # Adjust layout
                plt.tight_layout()
                
                # Save the visualization
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.join(VISUALIZATION_DIR, f"carbon_savings_{username}_{timestamp}.png")
                plt.savefig(filename, bbox_inches='tight')
                plt.close(fig)
                
                # Display the visualization
                if HAS_RICH:
                    console.print(Rule("Carbon Savings Visualization", style="green"))
                    
                    # Create success message
                    viz_panel = Panel(
                        f"[bold green]Carbon savings visualization has been generated![/bold green]\n\n"
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
                    print("\nCarbon savings visualization has been generated!")
                    print(f"File saved as: {filename}")
                    
                    # Ask if user wants to open the visualization
                    open_choice = input("\nOpen visualization? (y/n): ")
                    if open_choice.lower() == 'y':
                        self.ui.open_file_browser(filename)
            
            except Exception as e:
                logger.error(f"Error generating carbon savings visualization: {e}")
                self.ui.display_error(f"Error generating visualization: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error processing carbon savings data: {e}")
            self.ui.display_error(f"Error processing carbon savings data: {str(e)}")
        
        # Final prompt to return to menu
        self.ui.prompt_continue()
    
    def generate_carbon_visualization(self, user, output_path):
        """Generate carbon savings visualization for reports."""
        # Get user stats
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        if not trips:
            return None
        
        try:
            # Process trip data
            dates = []
            carbon_saved = []
            
            for trip in trips:
                date_str = trip.get('date', '')
                try:
                    # Handle ISO format with T separator
                    date = datetime.datetime.strptime(date_str.split('T')[0] if 'T' in date_str else date_str, '%Y-%m-%d').date()
                    dates.append(date)
                    carbon_saved.append(float(trip.get('carbon_saved', 0)))
                except (ValueError, TypeError):
                    continue
            
            # Create visualization if we have data
            if dates:
                # Sort data by date
                sorted_indices = sorted(range(len(dates)), key=lambda k: dates[k])
                sorted_dates = [dates[i] for i in sorted_indices]
                sorted_carbon = [carbon_saved[i] for i in sorted_indices]
                
                # Calculate cumulative carbon savings
                cumulative_carbon = np.cumsum(sorted_carbon)
                
                # Create figure
                fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
                
                # Plot cumulative carbon savings
                ax.plot(sorted_dates, cumulative_carbon, '-', color='#2ecc71', linewidth=2)
                ax.set_title('Cumulative Carbon Savings', fontsize=12)
                ax.set_xlabel('Date', fontsize=10)
                ax.set_ylabel('Carbon Saved (kg)', fontsize=10)
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
            logger.error(f"Error generating carbon visualization for report: {e}")
        
        return None
