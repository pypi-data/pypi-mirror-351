#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EcoCycle - Carbon Footprint Module
Provides functionality for calculating and tracking carbon footprint and savings from cycling.
"""

import logging
import random
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union

from core.dependency import dependency_manager

# Ensure required packages for carbon footprint module
dependency_manager.ensure_packages(['rich', 'tqdm', 'colorama', 'tabulate'], silent=True)

# Import Rich UI components
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    from rich.box import Box, DOUBLE, ROUNDED, HEAVY, SQUARE
    from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.syntax import Syntax
    from rich.rule import Rule
    from rich.columns import Columns
    from rich.tree import Tree
    from rich.markdown import Markdown
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False

# Auto-install and import visualization dependencies
success, failed = dependency_manager.ensure_feature('visualization', silent=False)
if success:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    VISUALIZATION_AVAILABLE = True
else:
    VISUALIZATION_AVAILABLE = False

# Import specific functions for convenience
from utils.ascii_art import display_section_header, display_success_message, display_error_message, display_info_message

# Create directories for storing charts and reports
CARBON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "carbon_footprint")
os.makedirs(CARBON_DIR, exist_ok=True)

class CarbonFootprint:
    """Calculator and tracker for carbon footprint and cycling-related savings."""
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """Initialize the carbon footprint calculator."""
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager
        
        # Constants for carbon calculations
        self.car_emissions_per_km = 0.192  # kg CO2 per km
        self.bus_emissions_per_km = 0.105  # kg CO2 per km
        self.train_emissions_per_km = 0.041  # kg CO2 per km
        self.plane_emissions_per_km = 0.255  # kg CO2 per km
        self.ev_emissions_per_km = 0.053   # kg CO2 per km (average for electric vehicles)
        
        # Average emissions for various activities (kg CO2 per unit)
        self.emissions_data = {
            'beef_meal': 6.6,      # per meal
            'chicken_meal': 1.8,   # per meal
            'vegetarian_meal': 0.5, # per meal
            'vegan_meal': 0.3,     # per meal
            'hot_shower': 2.5,     # per 10 min shower
            'washing_machine': 0.6, # per load
            'dishwasher': 0.4,     # per cycle
            'computer_usage': 0.1,  # per hour
            'tv_usage': 0.08,      # per hour
            'home_heating': 7.5,    # per day (average)
            'air_conditioning': 10.5, # per day (average)
            'renewable_energy': 0.0,  # per kWh
            'grid_electricity': 0.475, # per kWh (average)
        }
        
        # Panel styling for Rich UI (consistent with data visualization module)
        self.panel_styles = {
            'transportation': {'border_style': 'blue', 'title_style': 'bold blue', 'box': ROUNDED},
            'food': {'border_style': 'green', 'title_style': 'bold green', 'box': ROUNDED},
            'home': {'border_style': 'cyan', 'title_style': 'bold cyan', 'box': ROUNDED},
            'summary': {'border_style': 'magenta', 'title_style': 'bold magenta', 'box': DOUBLE},
            'recommendations': {'border_style': 'yellow', 'title_style': 'bold yellow', 'box': ROUNDED},
            'challenge': {'border_style': 'green', 'title_style': 'bold green', 'box': ROUNDED}
        }
        
        # User's carbon footprint data
        self.user_footprint = {}
        
        # User's historical carbon footprint data
        self.history = []
        
        # Chart colors - consistent with data visualization module
        self.chart_colors = {
            'transportation': '#3498db',  # Blue
            'food': '#2ecc71',           # Green
            'home': '#1abc9c',           # Teal
            'total': '#9b59b6',          # Purple
            'baseline': '#e74c3c',       # Red
            'target': '#2ecc71',         # Green
            'progress': '#f1c40f'         # Yellow
        }
        
    def calculate_carbon_footprint(self):
        """Calculate and display a user's carbon footprint.
        
        Returns:
            bool: True if completed normally, False if user chose to return to main menu early.
        """
        if not HAS_RICH:
            display_error_message("Required dependencies not available. Please install rich, tqdm, colorama and tabulate.")
            return False
        
        # Clear the screen for a better UI experience
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Create a layout for the header
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main")
        )
        
        # Create a stylish header
        title = Text("Carbon Footprint Calculator", style="bold green")
        header_panel = Panel(
            Align.center(title),
            box=DOUBLE,
            border_style="bright_green",
            padding=(1, 10)
        )
        layout["header"].update(header_panel)
        
        # Render the layout header
        console.print(layout["header"])
        
        # Show description
        console.print(Panel(
            "Calculate your environmental impact and discover ways to reduce it through cycling",
            box=ROUNDED,
            border_style="blue",
            padding=(1, 2)
        ))
        
        # Get username (default to last used if available)
        username = self._get_username()
        if not username:
            return
        
        # Initialize or retrieve user's footprint data
        self.user_footprint = self._get_user_footprint(username)
        
        # Display a menu for data collection options
        options_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=ROUNDED,
            border_style="cyan",
            expand=False,
            width=80
        )
        
        options_table.add_column("Option", style="cyan", justify="center")
        options_table.add_column("Method", style="green")
        options_table.add_column("Description", style="blue")
        
        options_table.add_row(
            "[bold]1[/bold]",
            "[green]Standard Calculation[/green]",
            "Complete assessment with detailed questions"
        )
        options_table.add_row(
            "[bold]2[/bold]",
            "[yellow]Quick Estimate[/yellow]",
            "Brief assessment with minimal questions"
        )
        options_table.add_row(
            "[bold]3[/bold]",
            "[cyan]Import Previous Data[/cyan]",
            "Use your previously saved assessment"
        )
        options_table.add_row(
            "[bold]4[/bold]",
            "[bright_white]Return to Main Menu[/bright_white]",
            "Go back to the main application menu"
        )
        
        console.print(options_table)
        console.print()
        
        choice = Prompt.ask("Select calculation method", choices=["1", "2", "3", "4"], default="1")
        
        # First collect the data without the progress bar interference
        if choice == "2":
            # Quick estimate mode
            console.print("\n[bold]Collecting data for quick estimate...[/bold]")
            self._quick_estimate_data()
        elif choice == "3":
            # Try to import previous data
            console.print("\n[bold]Importing previous data...[/bold]")
            if not self._import_previous_data(username):
                # If import fails, fall back to standard calculation
                console.print("\n[bold yellow]No previous data found. Using standard calculation instead.[/bold yellow]")
                self._standard_data_collection()
        elif choice == "4":
            # Return to main menu
            console.print("\n[bold]Returning to main menu...[/bold]")
            time.sleep(0.5)  # Brief pause for visual feedback
            return False
        else:
            # Standard detailed calculation
            console.print("\n[bold]Collecting detailed data...[/bold]")
            self._standard_data_collection()
        
        # Now show progress for calculation only (after all user input is complete)
        console.print("\n[bold]Calculating your carbon footprint...[/bold]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold green]Calculating...[/bold green]"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
        ) as progress:
            task = progress.add_task("Processing...", total=100)
            
            # Simulate calculation progress
            for i in range(60):
                time.sleep(0.02)
                progress.update(task, completed=i)
                
            total_footprint = self._calculate_total_footprint()
            
            # Finalize progress
            for i in range(60, 101):
                time.sleep(0.01)
                progress.update(task, completed=i)
        
        # Display the results with Rich UI
        self._display_footprint_results(total_footprint, username)
        
        # Try to save the footprint data
        self._try_save_footprint_data(username, total_footprint)
        
        # Generate and display personalized recommendations
        self._display_recommendations()
        
        # Offer to generate and save visualizations
        if VISUALIZATION_AVAILABLE:
            self._offer_visualization_options(username, total_footprint)
        
        # Allow user to set reduction targets
        self._set_reduction_targets(username, total_footprint)
        
        # Final prompt to return to menu
        console.print()
        Prompt.ask("Press Enter to return to the main menu", default="")
        return True
    
    def _get_username(self) -> str:
        """Get username with improved UI."""
        if self.user_manager and self.user_manager.get_current_user():
            # User is already logged in, directly use their username
            user_info = self.user_manager.get_current_user()
            username = user_info.get('username', '')
            if username:
                return username
        
        # If we reached here, either there's no user manager, no current user,
        # or the current user has no username, so prompt for one
        username = Prompt.ask("Enter your username", default="")
        
        if not username:
            console.print("[bold red]Username cannot be empty.[/bold red]")
            return ""
        
        return username
            
    def _standard_data_collection(self):
        """Collect detailed carbon footprint data."""
        console.print(Panel(
            "Please answer these questions to calculate your carbon footprint",
            title="Standard Assessment",
            border_style="blue",
            box=ROUNDED
        ))
        
        self._collect_transportation_data()
        self._collect_food_data()
        self._collect_home_data()
    
    def _quick_estimate_data(self):
        """Collect minimal data for a quick carbon footprint estimate."""
        console.print(Panel(
            "Quick assessment with minimal questions",
            title="Quick Carbon Footprint Estimate",
            border_style="yellow",
            box=ROUNDED
        ))
        
        try:
            # Transportation (single question)
            console.print(Panel(
                "What is your primary mode of transportation?",
                title="Transportation",
                border_style="blue",
                box=ROUNDED
            ))
            
            # Create a numbered table with clear input options
            options_table = Table(show_header=False, box=None, expand=False, width=60)
            options_table.add_column("Option", style="cyan", justify="right", width=10)
            options_table.add_column("Mode", style="blue")
            
            options_table.add_row("[1]", "Car (gasoline/diesel)")
            options_table.add_row("[2]", "Electric vehicle")
            options_table.add_row("[3]", "Public transit")
            options_table.add_row("[4]", "Bicycle/Walking")
            
            console.print(options_table)
            console.print("\n[bold cyan]Type 1, 2, 3, or 4 and press Enter:[/bold cyan]")
            
            mode = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1", show_choices=True)
            commute_distance = float(Prompt.ask("Average daily travel distance (km)", default="20"))
            
            # Set transportation data
            self.user_footprint['commute_mode'] = mode
            self.user_footprint['commute_distance'] = commute_distance
            self.user_footprint['flights_per_year'] = 2  # Default value
            self.user_footprint['avg_flight_distance'] = 2000  # Default value
            self.user_footprint['car_km_per_week'] = commute_distance * 5  # Rough estimate based on weekdays
            
            # Food (single question)
            console.print(Panel(
                "Which best describes your diet?",
                title="Diet",
                border_style="green",
                box=ROUNDED
            ))
            
            options_table = Table(show_header=False, box=None, expand=False, width=60)
            options_table.add_column("Option", style="cyan", justify="right", width=10)
            options_table.add_column("Diet Type", style="green")
            
            options_table.add_row("[1]", "Regular meat-eater (daily)")
            options_table.add_row("[2]", "Occasional meat-eater (few times per week)")
            options_table.add_row("[3]", "Pescatarian (fish but no meat)")
            options_table.add_row("[4]", "Vegetarian") 
            options_table.add_row("[5]", "Vegan")
            
            console.print(options_table)
            console.print("\n[bold cyan]Type 1, 2, 3, 4, or 5 and press Enter:[/bold cyan]")
            
            diet = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="2", show_choices=True)
            
            # Map diet choice to meal frequencies (default values based on selection)
            diet_mapping = {
                "1": {"beef_meals": 5, "chicken_meals": 9, "vegetarian_meals": 7, "vegan_meals": 0},
                "2": {"beef_meals": 2, "chicken_meals": 5, "vegetarian_meals": 9, "vegan_meals": 5},
                "3": {"beef_meals": 0, "chicken_meals": 4, "vegetarian_meals": 14, "vegan_meals": 3},
                "4": {"beef_meals": 0, "chicken_meals": 0, "vegetarian_meals": 16, "vegan_meals": 5},
                "5": {"beef_meals": 0, "chicken_meals": 0, "vegetarian_meals": 0, "vegan_meals": 21},
            }
            
            # Apply diet mapping
            self.user_footprint.update(diet_mapping.get(diet, diet_mapping["2"]))
            self.user_footprint['food_waste_percent'] = 15  # Default value
            
            # Home energy (simplified)
            console.print(Panel(
                "Home Energy Usage",
                title="Energy",
                border_style="cyan",
                box=ROUNDED
            ))
            
            heating_months = IntPrompt.ask(
                "How many months per year do you use heating?",
                default=5,
                show_default=True
            )
            
            ac_months = IntPrompt.ask(
                "How many months per year do you use air conditioning?",
                default=3,
                show_default=True
            )
            
            console.print("\n[bold cyan]Answer yes/no (y/n):[/bold cyan]")
            renewable = Confirm.ask(
                "Do you use renewable energy at home?",
                default=False,
                show_default=True
            )
            
            # Set home energy data
            self.user_footprint.update({
                'heating_months': heating_months,
                'ac_months': ac_months,
                'renewable_energy': renewable,
                'shower_minutes': 8,  # Default values for other parameters
                'showers_per_week': 7,
                'laundry_loads': 3,
                'dishwasher_cycles': 4,
                'computer_hours': 6,
                'tv_hours': 2
            })
            
        except ValueError as e:
            console.print(f"[bold red]Error in data input: {str(e)}[/bold red]")
            
            # Set fallback default values
            self._set_default_values()
    
    def _set_default_values(self):
        """Set default values for all footprint parameters."""
        # Transportation defaults
        self.user_footprint.update({
            'commute_mode': "1",
            'commute_distance': 15,
            'flights_per_year': 2,
            'avg_flight_distance': 2000,
            'car_km_per_week': 100,
        })
        
        # Food defaults
        self.user_footprint.update({
            'beef_meals': 3,
            'chicken_meals': 5,
            'vegetarian_meals': 7,
            'vegan_meals': 6,
            'food_waste_percent': 15,
        })
        
        # Home defaults
        self.user_footprint.update({
            'heating_months': 5,
            'ac_months': 3,
            'renewable_energy': False,
            'shower_minutes': 10,
            'showers_per_week': 7,
            'laundry_loads': 3,
            'dishwasher_cycles': 4,
            'computer_hours': 8,
            'tv_hours': 2
        })
    
    def _import_previous_data(self, username):
        """Try to import previous carbon footprint data."""
        if not self.sheets_manager:
            if HAS_RICH:
                console.print("[yellow]No sheets manager available to import previous data.[/yellow]")
            else:
                display_warning_message("No sheets manager available to import previous data.")
            return False
        
        try:
            # This is a placeholder - in a real implementation, would retrieve data from sheets
            # For now, return False to indicate import failed
            if HAS_RICH:
                console.print("[yellow]No previous data found. Using standard calculation.[/yellow]")
            else:
                display_warning_message("No previous data found. Using standard calculation.")
            return False
        except Exception as e:
            logging.error(f"Error importing previous data: {e}", exc_info=True)
            if HAS_RICH:
                console.print(f"[bold red]Error importing previous data: {str(e)}[/bold red]")
            else:
                display_error_message(f"Error importing previous data: {str(e)}")
            return False
    
    def _try_save_footprint_data(self, username, footprint):
        """Try to save footprint data with proper error handling."""
        if not self.sheets_manager:
            return
            
        try:
            self._save_footprint_data(username, footprint)
            if HAS_RICH:
                console.print("[bold green]Carbon footprint data saved successfully![/bold green]")
            else:
                display_success_message("Carbon footprint data saved.")
                
            # Add to history
            self.history.append({
                'username': username,
                'date': datetime.now().strftime("%Y-%m-%d"),
                'footprint': footprint
            })
            
        except Exception as e:
            logging.error(f"Error saving carbon footprint data: {e}", exc_info=True)
            if HAS_RICH:
                console.print(f"[bold red]Could not save carbon footprint data: {str(e)}[/bold red]")
            else:
                display_error_message("Could not save carbon footprint data.")
    
    def _offer_visualization_options(self, username, footprint):
        """Offer to generate and save visualizations."""
        if not VISUALIZATION_AVAILABLE:
            console.print("[yellow]Visualization packages not available. Install matplotlib and numpy to enable this feature.[/yellow]")
            return
            
        if Confirm.ask("\nWould you like to generate visualizations of your carbon footprint?", default=True):
            console.print()
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]Generating visualizations...[/bold cyan]"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
            ) as progress:
                task = progress.add_task("Generating...", total=100)
                
                # Generate the visualizations
                for i in range(20):
                    time.sleep(0.02)
                    progress.update(task, completed=i)
                
                visualization_dir = self._generate_visualizations(username, footprint)
                
                for i in range(20, 90):
                    time.sleep(0.02)
                    progress.update(task, completed=i)
                
                # Display the generated visualizations
                self._display_visualizations(username, visualization_dir)
                
                for i in range(90, 101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
                
            console.print(f"\n[green]Visualizations saved to: {visualization_dir}[/green]")
    
    def _generate_visualizations(self, username, footprint):
        """Generate visualizations of carbon footprint data."""
        # Check if visualization packages are available
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            console.print("[bold red]Required visualization packages not available.[/bold red]")
            console.print("[yellow]Please install matplotlib and numpy to generate visualizations.[/yellow]")
            return None

        # Create a directory for the user's visualizations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_dir = os.path.join(CARBON_DIR, f"{username}_{timestamp}")
        os.makedirs(user_dir, exist_ok=True)
        
        # Generate various charts
        self._generate_pie_chart(username, footprint, user_dir)
        self._generate_comparison_chart(username, footprint, user_dir)
        self._generate_savings_chart(username, footprint, user_dir)
        
        return user_dir
    
    def _generate_pie_chart(self, username, footprint, save_dir):
        """Generate a pie chart showing breakdown of carbon footprint by category."""
        import matplotlib.pyplot as plt
        
        # Extract data
        labels = ['Transportation', 'Food', 'Home Energy']
        sizes = [footprint['transportation'], footprint['food'], footprint['home']]
        colors = [self.chart_colors['transportation'], self.chart_colors['food'], self.chart_colors['home']]
        
        # Create the pie chart
        plt.figure(figsize=(10, 7))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=True)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(f"{username}'s Carbon Footprint Breakdown")
        
        # Save the chart
        file_path = os.path.join(save_dir, 'carbon_breakdown_pie.png')
        plt.savefig(file_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _generate_comparison_chart(self, username, footprint, save_dir):
        """Generate a bar chart comparing user's footprint with average."""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Data
        categories = ['Your Footprint', 'Average Footprint']
        values = [footprint['total'], 5000]  # Using 5000 kg as average
        
        # Create the bar chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories, values, color=[self.chart_colors['total'], self.chart_colors['baseline']])
        
        # Add labels and title
        plt.ylabel('Carbon Footprint (kg CO2)')
        plt.title('Your Carbon Footprint vs. Average')
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 100,
                    f'{height:.0f} kg',
                    ha='center', va='bottom')
        
        # Save the chart
        file_path = os.path.join(save_dir, 'carbon_comparison.png')
        plt.savefig(file_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return file_path
    
    def _generate_savings_chart(self, username, footprint, save_dir):
        """Generate a chart showing potential carbon savings from various actions."""
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Calculate potential savings
        savings = [
            ('Bike to work twice a week', 192 * 2 * 50 * 0.001),  # 2 days/week, 50 weeks, 10km round trip
            ('Reduce beef by 50%', self.emissions_data['beef_meal'] * self.user_footprint.get('beef_meals', 3) * 0.5 * 52),
            ('Use public transit more', 250 * 10 * (self.car_emissions_per_km - self.bus_emissions_per_km)),
            ('Install LED bulbs', 150),  # Rough estimate
            ('Take shorter showers', self.emissions_data['hot_shower'] * 0.3 * self.user_footprint.get('showers_per_week', 7) * 52),
            ('Reduce food waste', footprint['food'] * self.user_footprint.get('food_waste_percent', 15) / 100 * 0.5)
        ]
        
        # Sort by impact
        savings.sort(key=lambda x: x[1], reverse=True)
        
        # Extract data for chart
        actions = [item[0] for item in savings]
        impact = [item[1] for item in savings]
        
        # Create horizontal bar chart
        plt.figure(figsize=(12, 8))
        bars = plt.barh(actions, impact, color=self.chart_colors['target'])
        
        # Add labels and title
        plt.xlabel('Potential Annual CO2 Savings (kg)')
        plt.title('Potential Carbon Savings from Actions')
        
        # Add values at end of bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 20, i, f'{width:.1f} kg', va='center')
        
        # Save the chart
        file_path = os.path.join(save_dir, 'carbon_potential_savings.png')
        plt.savefig(file_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return file_path

    def _display_visualizations(self, username, visualization_dir):
        """Display the generated visualizations if possible."""
        if not HAS_RICH:
            return
            
        try:
            # Check if files exist
            pie_chart = os.path.join(visualization_dir, 'carbon_breakdown_pie.png')
            comparison_chart = os.path.join(visualization_dir, 'carbon_comparison.png')
            savings_chart = os.path.join(visualization_dir, 'carbon_potential_savings.png')
            
            files_exist = all(os.path.exists(f) for f in [pie_chart, comparison_chart, savings_chart])
            
            if not files_exist:
                console.print("[yellow]Some visualization files could not be found.[/yellow]")
                return
                
            # Ask if user wants to view the files
            if Confirm.ask("\n[bold]Would you like to open these visualizations?[/bold]", default=True):
                # Try to open with default application
                try:
                    import sys
                    if os.name == 'nt':  # Windows
                        os.startfile(visualization_dir)
                    elif os.name == 'posix':  # macOS and Linux
                        if sys.platform == 'darwin':  # macOS
                            os.system(f'open {visualization_dir}')
                        else:  # Linux
                            os.system(f'xdg-open {visualization_dir}')
                            
                    console.print("[green]Visualizations opened in file explorer.[/green]")
                except Exception as e:
                    console.print(f"[yellow]Could not open files automatically: {str(e)}[/yellow]")
                    console.print(f"[bold]Please navigate to: {visualization_dir}[/bold]")
        except Exception as e:
            console.print(f"[bold red]Error displaying visualizations: {str(e)}[/bold red]")

    def _set_reduction_targets(self, username, footprint):
        """Allow user to set reduction targets."""
        total = footprint.get('total', 0)
        
        console.print()
        console.print(Rule("Set Carbon Reduction Targets", style="bold green"))
        
        # Create a panel for the targets section
        console.print(Panel(
            "Set targets to reduce your carbon footprint and track your progress over time.",
            title="Carbon Reduction Planning",
            border_style="green",
            box=ROUNDED
        ))
        
        if not Confirm.ask("\nWould you like to set a carbon reduction target?", default=True):
            return
        
        # Default reduction targets by percentage
        options_table = Table(show_header=False, box=None)
        options_table.add_column("Option", style="cyan", justify="right")
        options_table.add_column("Target", style="green")
        options_table.add_column("Impact", style="yellow", justify="right")
        
        target_5_percent = total * 0.05
        target_10_percent = total * 0.10
        target_20_percent = total * 0.20
        
        options_table.add_row(
            "[1]", 
            f"5% reduction ({target_5_percent:.1f} kg CO2)",
            "[yellow]Moderate[/yellow]"
        )
        options_table.add_row(
            "[2]", 
            f"10% reduction ({target_10_percent:.1f} kg CO2)",
            "[green]Significant[/green]"
        )
        options_table.add_row(
            "[3]", 
            f"20% reduction ({target_20_percent:.1f} kg CO2)",
            "[bold green]Ambitious[/bold green]"
        )
        options_table.add_row(
            "[4]", 
            "Custom target",
            "[cyan]You decide[/cyan]"
        )
        
        console.print(options_table)
        console.print()
        
        choice = Prompt.ask("Select a target", choices=["1", "2", "3", "4"], default="2")
        
        if choice == "4":
            # Custom target
            valid_target = False
            while not valid_target:
                try:
                    target_percent = float(Prompt.ask(
                        "Enter your target reduction percentage",
                        default="15"
                    ))
                    if 0 < target_percent <= 100:
                        valid_target = True
                        target = total * (target_percent / 100)
                    else:
                        console.print("[bold red]Please enter a percentage between 0 and 100.[/bold red]")
                except ValueError:
                    console.print("[bold red]Please enter a valid number.[/bold red]")
        else:
            # Predefined targets
            if choice == "1":
                target = target_5_percent
                target_percent = 5
            elif choice == "2":
                target = target_10_percent
                target_percent = 10
            else:  # choice == "3"
                target = target_20_percent
                target_percent = 20
        
        # Calculate the new footprint after reduction
        new_footprint = total - target
        
        # Display the target summary
        summary_panel = Panel(
            f"You've set a target to reduce your carbon footprint by [bold green]{target_percent:.1f}%[/bold green]\n\n"
            f"Current footprint: [yellow]{total:.1f} kg CO2[/yellow]\n"
            f"Target reduction: [green]{target:.1f} kg CO2[/green]\n"
            f"New footprint goal: [bold cyan]{new_footprint:.1f} kg CO2[/bold cyan]\n\n"
            "We'll help you track your progress toward this goal.",
            title="Your Carbon Reduction Plan",
            border_style="green",
            box=DOUBLE
        )
        
        console.print(summary_panel)
        
        # Save the targets if user is logged in
        if self.user_manager and self.user_manager.get_current_user():
            user = self.user_manager.get_current_user()
            if not user.get('carbon_targets'):
                user['carbon_targets'] = []
                
            # Add the new target
            user['carbon_targets'].append({
                'date_set': datetime.now().strftime("%Y-%m-%d"),
                'baseline': total,
                'target_percent': target_percent,
                'target_reduction': target,
                'target_footprint': new_footprint
            })
            
            console.print("[green]Carbon reduction target saved to your profile![/green]")
    
    def _get_user_footprint(self, username):
        """Get or initialize user's footprint data."""
        # If we have a sheets manager, try to retrieve existing data
        if self.sheets_manager:
            try:
                # Try to get existing footprint data for this user
                # This would typically be stored in a separate sheet or table
                # For now, return an empty dictionary as placeholder
                return {}
            except Exception as e:
                logging.error(f"Error retrieving carbon footprint data: {e}", exc_info=True)
                return {}
        
        # If no data is available, return empty dictionary
        return {}
    
    def _collect_transportation_data(self):
        """Collect transportation-related carbon footprint data with enhanced UI."""
        if HAS_RICH:
            console.print(Panel(
                "Transportation has a significant impact on your carbon footprint. Let's gather information about your travel habits.",
                title="Transportation",
                border_style=self.panel_styles['transportation']['border_style'],
                title_align="left",
                box=self.panel_styles['transportation']['box']
            ))
        else:
            print(f"\n{Fore.CYAN}Transportation:{Style.RESET_ALL}")
        
        try:
            # Daily commute distance
            if HAS_RICH:
                commute_distance = float(Prompt.ask(
                    "How many kilometers do you commute daily (total round trip)?", 
                    default="10"
                ))
                
                console.print("\n[bold]What is your primary mode of transportation?[/bold]")
                console.print("1. Car (gasoline/diesel)")
                console.print("2. Electric vehicle")
                console.print("3. Public transportation (bus)")
                console.print("4. Public transportation (train/subway)")
                console.print("5. Bicycle or walking")
                
                mode_choice = Prompt.ask(
                    "Enter choice", 
                    choices=["1", "2", "3", "4", "5"], 
                    default="1"
                )
            else:
                commute_distance = float(input("How many kilometers do you commute daily (total round trip)? ").strip() or "10")
                
                print("\nWhat is your primary mode of transportation?")
                print("1. Car (gasoline/diesel)")
                print("2. Electric vehicle")
                print("3. Public transportation (bus)")
                print("4. Public transportation (train/subway)")
                print("5. Bicycle or walking")
                
                mode_choice = input("Enter choice (1-5): ").strip() or "1"
            
            self.user_footprint['commute_mode'] = mode_choice
            self.user_footprint['commute_distance'] = commute_distance
            
            # Long distance travel - air travel
            if HAS_RICH:
                flights_per_year = int(Prompt.ask(
                    "\nHow many one-way flights do you take per year?", 
                    default="2"
                ))
                
                avg_flight_distance = float(Prompt.ask(
                    "What's the average distance of your flights (in km)?", 
                    default="2000"
                ))
            else:
                flights_per_year = int(input("\nHow many one-way flights do you take per year? ").strip() or "2")
                avg_flight_distance = float(input("What's the average distance of your flights (in km)? ").strip() or "2000")
            
            self.user_footprint['flights_per_year'] = flights_per_year
            self.user_footprint['avg_flight_distance'] = avg_flight_distance
            
            # Car usage apart from commuting
            if HAS_RICH:
                car_km_per_week = float(Prompt.ask(
                    "\nHow many kilometers do you drive for non-commuting purposes per week?", 
                    default="50"
                ))
                
                # For EV users, ask about charging source
                if mode_choice == "2":  # Electric vehicle
                    renewable_charging = Confirm.ask(
                        "Do you charge your EV primarily with renewable energy?",
                        default=False
                    )
                    self.user_footprint['renewable_charging'] = renewable_charging
            else:
                car_km_per_week = float(input("\nHow many kilometers do you drive for non-commuting purposes per week? ").strip() or "50")
                
                # For EV users, ask about charging source
                if mode_choice == "2":  # Electric vehicle
                    renewable_charging = input("Do you charge your EV primarily with renewable energy? (y/n) [n]: ").strip().lower() == 'y'
                    self.user_footprint['renewable_charging'] = renewable_charging
            
            self.user_footprint['car_km_per_week'] = car_km_per_week
            
        except ValueError as e:
            if HAS_RICH:
                console.print(f"[bold red]Error in transportation data: {str(e)}[/bold red]")
            else:
                display_error_message(f"Please enter numeric values for distances: {str(e)}")
            
            # Set default values
            self.user_footprint['commute_mode'] = "1"
            self.user_footprint['commute_distance'] = 10
            self.user_footprint['flights_per_year'] = 2
            self.user_footprint['avg_flight_distance'] = 2000
            self.user_footprint['car_km_per_week'] = 50
            self.user_footprint['renewable_charging'] = False
    
    def _collect_food_data(self):
        """Collect food-related carbon footprint data with enhanced UI."""
        if HAS_RICH:
            console.print(Panel(
                "Food choices have a significant impact on your carbon footprint. Let's gather information about your diet.",
                title="Food Consumption",
                border_style=self.panel_styles['food']['border_style'],
                title_align="left",
                box=self.panel_styles['food']['box']
            ))
            console.print("[bold]How many meals per week do you eat that contain:[/bold]")
        else:
            print(f"\n{Fore.GREEN}Food Consumption:{Style.RESET_ALL}")
            print("How many meals per week do you eat that contain:")
            
        try:
            # Collect data on meal types
            if HAS_RICH:
                beef_meals = int(Prompt.ask(
                    "Beef", 
                    default="3"
                ))
                
                chicken_meals = int(Prompt.ask(
                    "Chicken or pork", 
                    default="5"
                ))
                
                vegetarian_meals = int(Prompt.ask(
                    "Vegetarian (with dairy/eggs)", 
                    default="7"
                ))
                
                vegan_meals = int(Prompt.ask(
                    "Vegan (plant-based only)", 
                    default="6"
                ))
                
                # Display impact information
                total_meals = beef_meals + chicken_meals + vegetarian_meals + vegan_meals
                beef_percent = (beef_meals / total_meals) * 100 if total_meals > 0 else 0
                plant_based_percent = ((vegetarian_meals + vegan_meals) / total_meals) * 100 if total_meals > 0 else 0
                
                console.print(f"[italic]Beef accounts for about {beef_percent:.1f}% of your meals.[/italic]")
                console.print(f"[italic]Plant-based meals make up {plant_based_percent:.1f}% of your diet.[/italic]")                
            else:
                beef_meals = int(input("Beef? ").strip() or "3")
                chicken_meals = int(input("Chicken or pork? ").strip() or "5")
                vegetarian_meals = int(input("Vegetarian (with dairy/eggs)? ").strip() or "7")
                vegan_meals = int(input("Vegan (plant-based only)? ").strip() or "6")
            
            self.user_footprint['beef_meals'] = beef_meals
            self.user_footprint['chicken_meals'] = chicken_meals
            self.user_footprint['vegetarian_meals'] = vegetarian_meals
            self.user_footprint['vegan_meals'] = vegan_meals
            
            # Food waste
            if HAS_RICH:
                console.print("\n[bold]Food Waste:[/bold]")
                food_waste_percent = int(Prompt.ask(
                    "What percentage of your food do you typically waste?", 
                    default="15"
                ))
                
                # Provide context based on response
                if food_waste_percent > 20:
                    console.print("[yellow]That's higher than the average of 15-20%. Reducing food waste is an easy way to lower your carbon footprint.[/yellow]")
                elif food_waste_percent < 10:
                    console.print("[green]That's lower than the average of 15-20%. Great job reducing food waste![/green]")
            else:
                food_waste_percent = int(input("\nWhat percentage of your food do you typically waste? ").strip() or "15")
            
            self.user_footprint['food_waste_percent'] = food_waste_percent
            
            # Additional food questions (local/organic)
            if HAS_RICH:
                console.print("\n[bold]Additional Food Choices:[/bold]")
                local_food_percent = int(Prompt.ask(
                    "Approximately what percentage of your food is locally sourced (within 100 miles)?", 
                    default="20"
                ))
                
                organic_food = Confirm.ask(
                    "Do you prioritize organic foods when shopping?",
                    default=False
                )
                
                self.user_footprint['local_food_percent'] = local_food_percent
                self.user_footprint['organic_food'] = organic_food
            else:
                try:
                    local_food_percent = int(input("\nApproximately what percentage of your food is locally sourced (within 100 miles)? [20]: ").strip() or "20")
                    organic_food = input("Do you prioritize organic foods when shopping? (y/n) [n]: ").strip().lower() == 'y'
                    
                    self.user_footprint['local_food_percent'] = local_food_percent
                    self.user_footprint['organic_food'] = organic_food
                except ValueError:
                    self.user_footprint['local_food_percent'] = 20
                    self.user_footprint['organic_food'] = False
            
        except ValueError as e:
            if HAS_RICH:
                console.print(f"[bold red]Error in food data: {str(e)}[/bold red]")
            else:
                display_error_message(f"Please enter numeric values for meal counts: {str(e)}")
            
            # Set default values
            self.user_footprint['beef_meals'] = 3
            self.user_footprint['chicken_meals'] = 5
            self.user_footprint['vegetarian_meals'] = 7
            self.user_footprint['vegan_meals'] = 6
            self.user_footprint['food_waste_percent'] = 15
            self.user_footprint['local_food_percent'] = 20
            self.user_footprint['organic_food'] = False
    
    def _collect_home_data(self):
        """Collect home-related carbon footprint data with enhanced UI."""
        if HAS_RICH:
            console.print(Panel(
                "Home energy usage is a major contributor to your carbon footprint. Let's assess your household energy patterns.",
                title="Home Energy Usage",
                border_style=self.panel_styles['home']['border_style'],
                title_align="left",
                box=self.panel_styles['home']['box']
            ))
        else:
            print(f"\n{Fore.CYAN}Home Energy Usage:{Style.RESET_ALL}")
        
        try:
            # Heating and cooling
            if HAS_RICH:
                console.print("\n[bold]Heating & Cooling:[/bold]")
                heating_months = int(Prompt.ask(
                    "How many months per year do you use heating?", 
                    default="5"
                ))
                
                ac_months = int(Prompt.ask(
                    "How many months per year do you use air conditioning?", 
                    default="3"
                ))
                
                # Ask about energy efficiency measures
                has_insulation = Confirm.ask(
                    "Is your home well-insulated?",
                    default=True
                )
                
                has_smart_thermostat = Confirm.ask(
                    "Do you use a programmable or smart thermostat?",
                    default=False
                )
                
                # Store efficiency data
                self.user_footprint['has_insulation'] = has_insulation
                self.user_footprint['has_smart_thermostat'] = has_smart_thermostat
                
                # Provide feedback based on responses
                if heating_months + ac_months > 9:
                    console.print("[yellow]You rely on climate control most of the year. Consider additional insulation to reduce energy needs.[/yellow]")
                
                if has_smart_thermostat:
                    console.print("[green]Smart thermostats can reduce heating/cooling energy use by 10-15%.[/green]")
            else:
                heating_months = int(input("How many months per year do you use heating? ").strip() or "5")
                ac_months = int(input("How many months per year do you use air conditioning? ").strip() or "3")
                
                # Simplified version of additional questions for non-Rich UI
                has_insulation = input("Is your home well-insulated? (y/n) [y]: ").strip().lower() != 'n'
                has_smart_thermostat = input("Do you use a programmable or smart thermostat? (y/n) [n]: ").strip().lower() == 'y'
                
                # Store efficiency data
                self.user_footprint['has_insulation'] = has_insulation
                self.user_footprint['has_smart_thermostat'] = has_smart_thermostat
            
            # Water usage
            if HAS_RICH:
                console.print("\n[bold]Water Usage:[/bold]")
                shower_minutes = float(Prompt.ask(
                    "How many minutes is your average shower?", 
                    default="10"
                ))
                
                showers_per_week = int(Prompt.ask(
                    "How many showers do you take per week?", 
                    default="7"
                ))
                
                # Ask about water-saving devices
                has_water_saving = Confirm.ask(
                    "Do you have water-saving shower heads or faucets?",
                    default=False
                )
                
                # Store water efficiency data
                self.user_footprint['has_water_saving'] = has_water_saving
                
                # Provide feedback based on responses
                if shower_minutes > 10:
                    console.print("[yellow]The average shower in the US is 8 minutes. Reducing your shower time can save water and energy.[/yellow]")
                elif shower_minutes < 5:
                    console.print("[green]Your short showers are helping save water and energy![/green]")
                    
                if has_water_saving:
                    console.print("[green]Water-saving fixtures can reduce water consumption by up to 30%.[/green]")
            else:
                shower_minutes = float(input("\nHow many minutes is your average shower? ").strip() or "10")
                showers_per_week = int(input("How many showers do you take per week? ").strip() or "7")
                
                # Simplified version for non-Rich UI
                has_water_saving = input("Do you have water-saving shower heads or faucets? (y/n) [n]: ").strip().lower() == 'y'
                self.user_footprint['has_water_saving'] = has_water_saving
            
            # Appliance usage
            if HAS_RICH:
                console.print("\n[bold]Appliance Usage:[/bold]")
                laundry_loads = int(Prompt.ask(
                    "How many loads of laundry do you do per week?", 
                    default="3"
                ))
                
                # Ask about energy-efficient appliances
                energy_efficient_washer = Confirm.ask(
                    "Do you use an energy-efficient washing machine?",
                    default=False
                )
                
                cold_water_wash = Confirm.ask(
                    "Do you typically wash clothes in cold water?",
                    default=False
                )
                
                dishwasher_cycles = int(Prompt.ask(
                    "How many dishwasher cycles do you run per week?", 
                    default="4"
                ))
                
                energy_efficient_dishwasher = Confirm.ask(
                    "Do you use an energy-efficient dishwasher?",
                    default=False
                )
                
                # Store appliance efficiency data
                self.user_footprint['energy_efficient_washer'] = energy_efficient_washer
                self.user_footprint['cold_water_wash'] = cold_water_wash
                self.user_footprint['energy_efficient_dishwasher'] = energy_efficient_dishwasher
                
                # Provide feedback based on responses
                if cold_water_wash:
                    console.print("[green]Washing clothes in cold water can reduce energy use by up to 90% compared to hot water.[/green]")
                    
                if energy_efficient_washer and energy_efficient_dishwasher:
                    console.print("[green]Energy-efficient appliances can reduce energy use by 10-50% compared to standard models.[/green]")
            else:
                laundry_loads = int(input("\nHow many loads of laundry do you do per week? ").strip() or "3")
                
                # Simplified version for non-Rich UI
                energy_efficient_washer = input("Do you use an energy-efficient washing machine? (y/n) [n]: ").strip().lower() == 'y'
                cold_water_wash = input("Do you typically wash clothes in cold water? (y/n) [n]: ").strip().lower() == 'y'
                
                dishwasher_cycles = int(input("How many dishwasher cycles do you run per week? ").strip() or "4")
                energy_efficient_dishwasher = input("Do you use an energy-efficient dishwasher? (y/n) [n]: ").strip().lower() == 'y'
                
                # Store appliance efficiency data
                self.user_footprint['energy_efficient_washer'] = energy_efficient_washer
                self.user_footprint['cold_water_wash'] = cold_water_wash
                self.user_footprint['energy_efficient_dishwasher'] = energy_efficient_dishwasher
            
            # Electronics
            if HAS_RICH:
                console.print("\n[bold]Electronics Usage:[/bold]")
                computer_hours = float(Prompt.ask(
                    "How many hours per day do you use computers/devices?", 
                    default="8"
                ))
                
                tv_hours = float(Prompt.ask(
                    "How many hours per day do you watch TV?", 
                    default="2"
                ))
                
                # Ask about energy-saving practices
                power_management = Confirm.ask(
                    "Do you use power management settings on your devices?",
                    default=False
                )
                
                energy_saving_tv = Confirm.ask(
                    "Is your TV an energy-efficient model?",
                    default=False
                )
                
                unplug_devices = Confirm.ask(
                    "Do you unplug electronics or use power strips to prevent standby power use?",
                    default=False
                )
                
                # Store electronics efficiency data
                self.user_footprint['power_management'] = power_management
                self.user_footprint['energy_saving_tv'] = energy_saving_tv
                self.user_footprint['unplug_devices'] = unplug_devices
                
                # Provide feedback based on responses
                if computer_hours + tv_hours > 10:
                    console.print("[yellow]You spend significant time using electronics. Consider taking regular breaks to reduce energy use.[/yellow]")
                    
                if unplug_devices:
                    console.print("[green]Eliminating standby power can save up to 10% on your electricity bill.[/green]")
            else:
                computer_hours = float(input("\nHow many hours per day do you use computers/devices? ").strip() or "8")
                tv_hours = float(input("How many hours per day do you watch TV? ").strip() or "2")
                
                # Simplified version for non-Rich UI
                power_management = input("Do you use power management settings on your devices? (y/n) [n]: ").strip().lower() == 'y'
                energy_saving_tv = input("Is your TV an energy-efficient model? (y/n) [n]: ").strip().lower() == 'y'
                unplug_devices = input("Do you unplug electronics or use power strips to prevent standby power use? (y/n) [n]: ").strip().lower() == 'y'
                
                # Store electronics efficiency data
                self.user_footprint['power_management'] = power_management
                self.user_footprint['energy_saving_tv'] = energy_saving_tv
                self.user_footprint['unplug_devices'] = unplug_devices
            
            # Additional home energy question - renewable energy
            if HAS_RICH:
                console.print("\n[bold]Energy Sources:[/bold]")
                renewable_percentage = int(Prompt.ask(
                    "What percentage of your home electricity comes from renewable sources?", 
                    default="0"
                ))
            else:
                renewable_percentage = int(input("\nWhat percentage of your home electricity comes from renewable sources? [0]: ").strip() or "0")
                
            # Store all the values
            self.user_footprint.update({
                'heating_months': heating_months,
                'ac_months': ac_months,
                'shower_minutes': shower_minutes,
                'showers_per_week': showers_per_week,
                'laundry_loads': laundry_loads,
                'dishwasher_cycles': dishwasher_cycles,
                'computer_hours': computer_hours,
                'tv_hours': tv_hours,
                'renewable_percentage': renewable_percentage
            })
            
            # Provide summary feedback if using Rich UI
            if HAS_RICH:
                # Calculate a rough efficiency score (0-100)
                efficiency_factors = [
                    30 if self.user_footprint.get('has_insulation', False) else 0,
                    20 if self.user_footprint.get('has_smart_thermostat', False) else 0,
                    15 if self.user_footprint.get('has_water_saving', False) else 0,
                    15 if self.user_footprint.get('energy_efficient_washer', False) else 0,
                    10 if self.user_footprint.get('energy_efficient_dishwasher', False) else 0,
                    10 if self.user_footprint.get('unplug_devices', False) else 0
                ]
                
                efficiency_score = sum(efficiency_factors) / 100  # Normalize to 0-1
                renewable_factor = renewable_percentage / 100  # Normalize to 0-1
                
                # Display a summary panel
                if renewable_percentage > 50 and efficiency_score > 0.5:
                    console.print(Panel(
                        "[green]Your home energy efficiency is excellent! Keep up the great work![/green]",
                        title="Energy Efficiency Summary",
                        border_style="green",
                        box=self.panel_styles['home']['box']
                    ))
                elif renewable_percentage > 20 or efficiency_score > 0.3:
                    console.print(Panel(
                        "[yellow]Your home has some good energy-saving features. There are still opportunities to improve efficiency.[/yellow]",
                        title="Energy Efficiency Summary",
                        border_style="yellow",
                        box=self.panel_styles['home']['box']
                    ))
                else:
                    console.print(Panel(
                        "[red]Consider implementing more energy-efficient practices and technologies to reduce your carbon footprint.[/red]",
                        title="Energy Efficiency Summary",
                        border_style="red",
                        box=self.panel_styles['home']['box']
                    ))
            
        except ValueError as e:
            if HAS_RICH:
                console.print(f"[bold red]Error in home energy data: {str(e)}[/bold red]")
            else:
                display_error_message(f"Please enter numeric values for all questions: {str(e)}")
                
            # Set default values
            self.user_footprint.update({
                'heating_months': 5,
                'ac_months': 3,
                'shower_minutes': 10,
                'showers_per_week': 7,
                'laundry_loads': 3,
                'dishwasher_cycles': 4,
                'computer_hours': 8,
                'tv_hours': 2,
                'has_insulation': False,
                'has_smart_thermostat': False,
                'has_water_saving': False,
                'energy_efficient_washer': False,
                'cold_water_wash': False,
                'energy_efficient_dishwasher': False,
                'power_management': False,
                'energy_saving_tv': False,
                'unplug_devices': False,
                'renewable_percentage': 0
            })
    
    def _calculate_total_footprint(self):
        """Calculate the total carbon footprint based on collected data."""
        # Transportation emissions
        transport_emissions = self._calculate_transportation_emissions()
        
        # Food emissions
        food_emissions = self._calculate_food_emissions()
        
        # Home emissions
        home_emissions = self._calculate_home_emissions()
        
        # Total annual footprint
        total = {
            'transportation': transport_emissions,
            'food': food_emissions,
            'home': home_emissions,
            'total': transport_emissions + food_emissions + home_emissions
        }
        
        return total
    
    def _calculate_transportation_emissions(self):
        """Calculate transportation-related emissions."""
        commute_emissions = 0
        commute_distance = self.user_footprint.get('commute_distance', 10)
        commute_mode = self.user_footprint.get('commute_mode', '1')
        
        # Calculate based on commute mode
        if commute_mode == '1':  # Car
            commute_emissions = commute_distance * self.car_emissions_per_km
        elif commute_mode == '2':  # Bus
            commute_emissions = commute_distance * self.bus_emissions_per_km
        elif commute_mode == '3':  # Train
            commute_emissions = commute_distance * self.train_emissions_per_km
        elif commute_mode == '4':  # Bicycle/walking
            commute_emissions = 0
        
        # Annual commute emissions (assuming 250 working days)
        annual_commute = commute_emissions * 250
        
        # Flight emissions
        flights_per_year = self.user_footprint.get('flights_per_year', 2)
        avg_flight_distance = self.user_footprint.get('avg_flight_distance', 2000)
        flight_emissions = flights_per_year * avg_flight_distance * self.plane_emissions_per_km
        
        # Other car usage
        car_km_per_week = self.user_footprint.get('car_km_per_week', 50)
        other_car_emissions = car_km_per_week * self.car_emissions_per_km * 52  # annual
        
        total_transport = annual_commute + flight_emissions + other_car_emissions
        return total_transport
    
    def _calculate_food_emissions(self):
        """Calculate food-related emissions."""
        # Get meal counts
        beef_meals = self.user_footprint.get('beef_meals', 3)
        chicken_meals = self.user_footprint.get('chicken_meals', 5)
        vegetarian_meals = self.user_footprint.get('vegetarian_meals', 7)
        vegan_meals = self.user_footprint.get('vegan_meals', 6)
        
        # Calculate weekly emissions
        weekly_emissions = (
            beef_meals * self.emissions_data['beef_meal'] +
            chicken_meals * self.emissions_data['chicken_meal'] +
            vegetarian_meals * self.emissions_data['vegetarian_meal'] +
            vegan_meals * self.emissions_data['vegan_meal']
        )
        
        # Account for food waste
        food_waste_percent = self.user_footprint.get('food_waste_percent', 15)
        food_waste_factor = 1 + (food_waste_percent / 100)
        
        # Calculate annual food emissions
        annual_food_emissions = weekly_emissions * 52 * food_waste_factor
        
        return annual_food_emissions
    
    def _calculate_home_emissions(self):
        """Calculate home-related emissions."""
        # Heating and cooling
        heating_months = self.user_footprint.get('heating_months', 5)
        ac_months = self.user_footprint.get('ac_months', 3)
        
        heating_emissions = heating_months * 30 * self.emissions_data['home_heating']
        ac_emissions = ac_months * 30 * self.emissions_data['air_conditioning']
        
        # Water usage
        shower_minutes = self.user_footprint.get('shower_minutes', 10)
        showers_per_week = self.user_footprint.get('showers_per_week', 7)
        
        shower_factor = shower_minutes / 10  # emissions are per 10 min shower
        shower_emissions = shower_factor * self.emissions_data['hot_shower'] * showers_per_week * 52
        
        # Appliance usage
        laundry_loads = self.user_footprint.get('laundry_loads', 3)
        dishwasher_cycles = self.user_footprint.get('dishwasher_cycles', 4)
        
        laundry_emissions = laundry_loads * self.emissions_data['washing_machine'] * 52
        dishwasher_emissions = dishwasher_cycles * self.emissions_data['dishwasher'] * 52
        
        # Electronics
        computer_hours = self.user_footprint.get('computer_hours', 8)
        tv_hours = self.user_footprint.get('tv_hours', 2)
        
        computer_emissions = computer_hours * self.emissions_data['computer_usage'] * 365
        tv_emissions = tv_hours * self.emissions_data['tv_usage'] * 365
        
        total_home = heating_emissions + ac_emissions + shower_emissions + laundry_emissions + dishwasher_emissions + computer_emissions + tv_emissions
        
        return total_home
    
    def _display_footprint_results(self, footprint, username):
        """Display the calculated carbon footprint results with enhanced visualizations."""
        # Extract data
        transportation = footprint.get('transportation', 0)
        food = footprint.get('food', 0)
        home = footprint.get('home', 0)
        total = footprint.get('total', 0)
        
        # Compare to average
        average_footprint = 5000  # kg CO2 per year (global average)
        percentage_diff = ((total - average_footprint) / average_footprint) * 100
        
        if percentage_diff <= -20:
            comparison_status = "significantly below"
            comparison_color = "green"
        elif percentage_diff < 0:
            comparison_status = "below"
            comparison_color = "green"
        elif percentage_diff <= 20:
            comparison_status = "slightly above"
            comparison_color = "yellow"
        else:
            comparison_status = "above"
            comparison_color = "red"
        
        # Display results in a styled panel
        console.print()
        console.print(Rule("Carbon Footprint Results", style="bold magenta"))
        
        # Create the summary panel
        summary = Text()
        summary.append(f"\nYour annual carbon footprint is ")
        summary.append(f"{total:.2f} kg CO2", style="bold white")
        summary.append(f", which is ")
        summary.append(f"{comparison_status} average", style=f"bold {comparison_color}")
        summary.append(".\n\n")
        
        # Create a table for the detailed breakdown
        results_table = Table(title="Emissions Breakdown", box=ROUNDED, border_style="magenta")
        
        results_table.add_column("Category", style="bold cyan")
        results_table.add_column("Emissions (kg CO2)", style="yellow")
        results_table.add_column("Percentage", style="green")
        
        results_table.add_row(
            "Transportation",
            f"{transportation:.2f}",
            f"{(transportation/total*100):.1f}%"
        )
        results_table.add_row(
            "Food",
            f"{food:.2f}",
            f"{(food/total*100):.1f}%"
        )
        results_table.add_row(
            "Home Energy",
            f"{home:.2f}",
            f"{(home/total*100):.1f}%"
        )
        results_table.add_row(
            "Total",
            f"{total:.2f}",
            "100.0%",
            style="bold white"
        )
        
        # Create visual bar chart using Rich
        def create_bar(percentage, color="green"):
            """Create a visual bar chart using ASCII characters."""
            bar_width = int(percentage / 2)  # Scale to make the bar reasonable length
            return f"[{color}]{'█' * bar_width}[/{color}] {percentage:.1f}%"

        # Create a comparison table with visual bars
        comparison_table = Table(title="Comparison to Average", box=ROUNDED, border_style="blue")
        comparison_table.add_column("Category", style="bold cyan")
        comparison_table.add_column("Visual Comparison", style="yellow")
        
        your_percentage = 100
        avg_percentage = (average_footprint / total) * 100
        
        comparison_table.add_row(
            "Your Footprint",
            create_bar(your_percentage, "green")
        )
        comparison_table.add_row(
            "Average Person",
            create_bar(avg_percentage, "yellow")
        )
        
        # Add cycling impact data if available
        if self.user_manager and self.user_manager.get_current_user():
            user_data = self.user_manager.get_current_user()
            cycling_stats = user_data.get('stats', {})
            total_distance = cycling_stats.get('total_distance', 0)
            total_co2_saved = cycling_stats.get('total_co2_saved', 0)
            
            if total_distance > 0:
                cycling_panel = Panel(
                    f"By cycling {total_distance:.1f} km, you've saved approximately "
                    f"[bold green]{total_co2_saved:.2f} kg CO2[/bold green] in emissions!",
                    title="Your Cycling Impact",
                    border_style="green",
                    box=ROUNDED
                )
            else:
                cycling_panel = Panel(
                    "Start tracking your cycling trips to see your CO2 emission savings!",
                    title="Cycling Impact",
                    border_style="yellow",
                    box=ROUNDED
                )
        else:
            cycling_panel = Panel(
                "Login and track your cycling trips to see your CO2 emission savings!",
                title="Cycling Impact",
                border_style="yellow",
                box=ROUNDED
            )
        
        # Display all components
        console.print(Panel(summary, title=f"{username}'s Carbon Footprint", border_style="magenta", box=DOUBLE))
        console.print(results_table)
        console.print(comparison_table)
        console.print(cycling_panel)
    
    def _save_footprint_data(self, username, footprint):
        """Save the carbon footprint data to Google Sheets."""
        if not self.sheets_manager:
            return
        
        # Format data for saving
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [
            username,
            timestamp,
            str(footprint['total']),
            str(footprint['transportation']),
            str(footprint['food']),
            str(footprint['home'])
        ]
        
        # Save to a specific sheet - in a real implementation, this would be saved to a dedicated sheet
        sheet_name = "CarbonFootprint"
        try:
            # Ensure the sheet exists
            # This would be implemented in a real application
            # self.sheets_manager._ensure_sheets_exist([sheet_name])
            
            # Append the data
            # self.sheets_manager.append_row(sheet_name, row_data)
            pass
        except Exception as e:
            logging.error(f"Error saving carbon footprint data: {e}", exc_info=True)
            raise
    
    def _display_recommendations(self):
        """Display personalized recommendations based on the carbon footprint calculation."""
        recommendations = self.generate_recommendations()
        
        # Organize recommendations by category
        by_category = {
            'transportation': [],
            'food': [],
            'home': [],
            'general': []
        }
        
        for rec in recommendations:
            category = rec.get('category', 'general')
            by_category[category].append(rec)
        
        # Display recommendations
        console.print()
        console.print(Rule("Carbon Footprint Recommendations", style="bold yellow"))
        
        # Create a Tree for hierarchical display
        rec_tree = Tree("🌍 [bold yellow]Personalized Recommendations[/bold yellow]")
        
        # Add transportation recommendations
        if by_category['transportation']:
            trans_branch = rec_tree.add("🚲 [bold blue]Transportation[/bold blue]")
            for rec in by_category['transportation']:
                impact = rec.get('impact', 'medium')
                impact_icon = "🔴" if impact == 'high' else "🟠" if impact == 'medium' else "🟡"
                trans_branch.add(f"{impact_icon} {rec['recommendation']}")
        
        # Add food recommendations
        if by_category['food']:
            food_branch = rec_tree.add("🥗 [bold green]Food Choices[/bold green]")
            for rec in by_category['food']:
                impact = rec.get('impact', 'medium')
                impact_icon = "🔴" if impact == 'high' else "🟠" if impact == 'medium' else "🟡"
                food_branch.add(f"{impact_icon} {rec['recommendation']}")
        
        # Add home recommendations
        if by_category['home']:
            home_branch = rec_tree.add("🏠 [bold cyan]Home Energy[/bold cyan]")
            for rec in by_category['home']:
                impact = rec.get('impact', 'medium')
                impact_icon = "🔴" if impact == 'high' else "🟠" if impact == 'medium' else "🟡"
                home_branch.add(f"{impact_icon} {rec['recommendation']}")
        
        # Add general recommendations
        if by_category['general']:
            general_branch = rec_tree.add("💡 [bold magenta]General Tips[/bold magenta]")
            for rec in by_category['general']:
                impact = rec.get('impact', 'medium')
                impact_icon = "🔴" if impact == 'high' else "🟠" if impact == 'medium' else "🟡"
                general_branch.add(f"{impact_icon} {rec['recommendation']}")
        
        # Display the recommendation tree
        console.print(rec_tree)
        
        # Display legend for impact indicators
        console.print()
        console.print(Panel(
            "🔴 High Impact   🟠 Medium Impact   🟡 Low Impact",
            title="Impact Legend",
            border_style="dim",
            box=ROUNDED
        ))
    
    def generate_recommendations(self):
        """Generate and display personalized carbon footprint reduction recommendations."""
        recommendations = []
        
        # Transportation recommendations
        commute_mode = self.user_footprint.get('commute_mode', '1')
        if commute_mode == '1':  # Car
            recommendations.append({
                'recommendation': "Switch to cycling for your daily commute. Could save ~3 kg CO2 per day.",
                'category': 'transportation',
                'impact': 'high'
            })
            recommendations.append({
                'recommendation': "Consider using public transportation. Could reduce emissions by up to 50%.",
                'category': 'transportation',
                'impact': 'medium'
            })
        
        flights_per_year = self.user_footprint.get('flights_per_year', 2)
        if flights_per_year >= 4:
            recommendations.append({
                'recommendation': "Consider reducing air travel or carbon offsetting. Air travel has high impact.",
                'category': 'transportation',
                'impact': 'high'
            })
        
        car_km_per_week = self.user_footprint.get('car_km_per_week', 50)
        if car_km_per_week > 100:
            recommendations.append({
                'recommendation': "Try to consolidate car trips and reduce non-essential travel.",
                'category': 'transportation',
                'impact': 'medium'
            })
        
        # Food recommendations
        beef_meals = self.user_footprint.get('beef_meals', 3)
        if beef_meals >= 3:
            recommendations.append({
                'recommendation': "Reducing beef consumption by 50% could save ~10 kg CO2 weekly.",
                'category': 'food',
                'impact': 'high'
            })
        
        food_waste_percent = self.user_footprint.get('food_waste_percent', 15)
        if food_waste_percent > 10:
            recommendations.append({
                'recommendation': "Reducing food waste has multiple benefits. Try meal planning.",
                'category': 'food',
                'impact': 'medium'
            })
        
        # Home recommendations
        shower_minutes = self.user_footprint.get('shower_minutes', 10)
        if shower_minutes > 8:
            recommendations.append({
                'recommendation': "Shorter showers can save water and energy. Aim for 5 minutes.",
                'category': 'home',
                'impact': 'medium'
            })
        
        heating_months = self.user_footprint.get('heating_months', 5)
        ac_months = self.user_footprint.get('ac_months', 3)
        if heating_months + ac_months > 6:
            recommendations.append({
                'recommendation': "Adjust thermostat by 1-2 degrees for significant savings.",
                'category': 'home',
                'impact': 'high'
            })
        
        laundry_loads = self.user_footprint.get('laundry_loads', 3)
        if laundry_loads > 2:
            recommendations.append({
                'recommendation': "Wash full loads of laundry and use cold water when possible.",
                'category': 'home',
                'impact': 'low'
            })
        
        computer_hours = self.user_footprint.get('computer_hours', 8)
        tv_hours = self.user_footprint.get('tv_hours', 2)
        if computer_hours + tv_hours > 8:
            recommendations.append({
                'recommendation': "Reduce device usage and ensure they're power-efficient.",
                'category': 'home',
                'impact': 'low'
            })
        
        # Add cycling-specific recommendations
        recommendations.append({
            'recommendation': "Each additional 10 km cycled instead of driving saves ~2 kg CO2.",
            'category': 'transportation',
            'impact': 'medium'
        })
        recommendations.append({
            'recommendation': "Join a local cycling advocacy group to promote sustainable transport.",
            'category': 'general',
            'impact': 'medium'
        })
        
        # Add tracking recommendation
        recommendations.append({
            'recommendation': "Track your carbon footprint monthly using EcoCycle's tools.",
            'category': 'general',
            'impact': 'medium'
        })
        
        # Add cycling challenge
        recommendations.append({
            'recommendation': "Try replacing 50% of your car trips under 5 km with cycling.",
            'category': 'transportation',
            'impact': 'high'
        })
        
        return recommendations

def run_calculator(user_manager=None, sheets_manager=None):
    """Convenience function to run the carbon footprint calculator."""
    try:
        # Ensure Rich and other required packages are available
        dependency_manager.ensure_packages(['rich', 'matplotlib', 'numpy'], silent=False)
        
        # Create and run the calculator
        calculator = CarbonFootprint(user_manager=user_manager, sheets_manager=sheets_manager)
        completed = calculator.calculate_carbon_footprint()
        
        # Only show the additional prompt if there was an error or special case
        # The calculator already shows a prompt on normal completion
        
    except ImportError as e:
        print(f"Error loading carbon footprint module: {e}")
        print("Please install required packages: pip install rich matplotlib numpy")
        input("\nPress Enter to return to the main menu...")
    except Exception as e:
        print(f"Error running carbon footprint calculator: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to return to the main menu...")

# Run the calculator if this script is executed directly
if __name__ == "__main__":
    run_calculator()
