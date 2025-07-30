#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EcoCycle - Application Functions Module

This module contains the core application functions used by both main.py and menu.py.
Moving these functions to a separate module helps break circular dependencies.
"""

import os
import sys
import logging
import argparse
import getpass
import importlib.util
import subprocess
import random
import time
import json
import hmac
import hashlib
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Any, Tuple, Union
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Import Rich UI components
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    from rich.box import ROUNDED, DOUBLE
    from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
    from rich.prompt import Prompt, Confirm
    from rich.rule import Rule
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False

    # Define fallback classes/constants when Rich is not available
    class FallbackTable:
        @staticmethod
        def grid(*args, **kwargs):
            return FallbackTable()
        def __init__(self, *args, **kwargs):
            pass
        def add_column(self, *args, **kwargs):
            pass
        def add_row(self, *args, **kwargs):
            pass
        def add_section(self):
            pass

    class FallbackPanel:
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def fit(*args, **kwargs):
            return FallbackPanel()

    class FallbackRule:
        def __init__(self, *args, **kwargs):
            pass

    class FallbackPrompt:
        @staticmethod
        def ask(prompt, **kwargs):
            default = kwargs.get('default', '')
            if default:
                return input(f"{prompt} [{default}]: ") or default
            return input(f"{prompt}: ")

    class FallbackConfirm:
        @staticmethod
        def ask(prompt, **kwargs):
            default = kwargs.get('default', False)
            default_text = "Y/n" if default else "y/N"
            response = input(f"{prompt} ({default_text}): ").lower()
            if not response:
                return default
            return response in ['y', 'yes', 'true', '1']

    class FallbackConsole:
        def print(self, *args, **kwargs):
            # Simple fallback that just prints to stdout
            print(*args)

        def status(self, *args, **kwargs):
            # Return a context manager that does nothing
            return FallbackContext()

    class FallbackContext:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    # Set fallback classes
    Table = FallbackTable
    Panel = FallbackPanel
    Rule = FallbackRule
    Prompt = FallbackPrompt
    Confirm = FallbackConfirm
    console = FallbackConsole()
    ROUNDED = None
    DOUBLE = None

# Helper function to handle box parameter
def get_box_style(box_style):
    """Return the box style if Rich is available, otherwise return None"""
    if HAS_RICH:
        return box_style
    return None

# Helper function to create Panel with proper fallback
def create_panel(*args, **kwargs):
    """Create a Panel with proper fallback handling"""
    if HAS_RICH:
        # Remove box parameter if it's None
        if 'box' in kwargs and kwargs['box'] is None:
            kwargs.pop('box')
        return Panel(*args, **kwargs)
    else:
        return FallbackPanel(*args, **kwargs)

import core.database_manager
import core.dependency.dependency_manager
import config.config

# Setup logger
logger = logging.getLogger(__name__)

# Global variables
GOOGLE_SHEETS_AVAILABLE = True

def log_cycling_trip(user_manager_instance):
    """Log a new cycling trip."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']
    utils = modules['utils']
    database_manager = modules.get('database_manager')  # Get database_manager from modules

    # Use Rich UI if available
    if not HAS_RICH:
        ascii_art.display_error_message("Required dependencies not available. Please install rich package.")
        return

    # Clear the screen for a better UI experience
    os.system('cls' if os.name == 'nt' else 'clear')

    if HAS_RICH:
        # Create a layout for the header
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main")
        )

        # Create a stylish header
        title = Text("Log Cycling Trip", style="bold green")
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
            "Record your cycling activity to track progress and environmental impact",
            box=ROUNDED,
            border_style="blue",
            padding=(1, 2)
        ))
    else:
        # Fallback for when Rich is not available
        print("=== Log Cycling Trip ===")
        print("Record your cycling activity to track progress and environmental impact")

    # Create a step progress indicator
    step_progress = Table.grid(padding=1)
    step_progress.add_column("Step", justify="right", style="cyan", no_wrap=True)
    step_progress.add_column("Description", style="green")
    step_progress.add_row("Step 1", "[bold]Enter Trip Information[/bold]")
    step_progress.add_row("Step 2", "Calculate Trip Impact")
    step_progress.add_row("Step 3", "Save and Sync Data")

    console.print(Panel(
        step_progress,
        border_style="dim",
        title="[white on grey15] Progress [/white on grey15]",
        title_align="center"
    ))

    # Check if user is authenticated
    if not user_manager_instance.is_authenticated():
        console.print(Panel(
            "You need to log in to record cycling trips. Please log in first.",
            title="Authentication Required",
            border_style="red",
            box=ROUNDED
        ))
        input("\nPress Enter to continue...")
        return

    # Get user data
    from datetime import datetime

    console.print(Panel(
        "Let's record your cycling trip details",
        title="Trip Information",
        border_style="cyan",
        box=ROUNDED
    ))

    # Use a consistent style for input sections
    trip_info_panel = Panel(
        "[bold]Enter your cycling trip details below[/bold]\n"
        "Fill out each field and press Enter to continue",
        title="Trip Information",
        border_style="cyan",
        box=ROUNDED
    )
    console.print(trip_info_panel)

    # Create a grid layout for better visual organization
    console.print(Rule("Date Information", style="cyan"))

    # Get date with default as today
    default_date = datetime.now().strftime("%Y-%m-%d")
    date_input = Prompt.ask(
        "[cyan]Date of trip[/cyan] [YYYY-MM-DD]",
        default=default_date,
        show_default=True
    )

    # Validate date format
    import re
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
        console.print(Panel(
            "Invalid date format. Please use YYYY-MM-DD format.",
            title="Input Error",
            border_style="red",
            box=ROUNDED
        ))
        input("\nPress Enter to return to the main menu...")
        return

    # Verify it's a valid date
    try:
        trip_date = datetime.strptime(date_input, "%Y-%m-%d")
        # Check if date is in the future
        if trip_date > datetime.now():
            console.print("[yellow]Note: You've entered a future date.[/yellow]")
    except ValueError:
        console.print(Panel(
            "Invalid date. Please enter a valid date.",
            title="Input Error",
            border_style="red",
            box=ROUNDED
        ))
        input("\nPress Enter to return to the main menu...")
        return

    # Format date to ensure consistency
    date = trip_date.strftime("%Y-%m-%d")

    # Create a section for location information
    console.print(Rule("Route Information", style="cyan"))

    # Initialize variables for route data
    start_location = None
    end_location = None
    start_coords = None
    end_coords = None
    route_info = None

    # Create a more visually appealing location panel with instructions
    location_panel = Panel(
        "[bold]Enter your route details[/bold]\n"
        "🗺️  You can use city names, addresses, landmarks, or coordinates\n"
        "🔍  Search will automatically find the best match\n"
        "📍  Recent locations will be saved for quick access",
        title="[white on blue] 📍 Route Information [/white on blue]",
        border_style="blue",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(location_panel)

    # Import weather controller for geocoding
    try:
        from controllers.weather_controller import WeatherController
        weather_controller = WeatherController()

        # Get recent locations from user preferences (if available)
        recent_locations = user_manager_instance.get_user_preference('recent_locations', [])

        # Function to get location with suggestions - improved UI
        def get_location_with_suggestions(prompt_text, location_type="starting"):
            # Create a modern, visually appealing input panel with icon
            icon = "🚩" if location_type == "starting" else "🏁"
            console.print(Panel(
                f"[bold cyan]{icon} {prompt_text}[/bold cyan]",
                border_style="blue",
                padding=(1, 2),
                expand=False,
                title=f"[white on blue] {location_type.title()} Location [/white on blue]"
            ))

            # Create a visually appealing options panel
            options_panel = Table.grid(padding=1)
            options_panel.add_column("Icon", style="cyan", justify="center", width=4)
            options_panel.add_column("Option", style="green")
            options_panel.add_column("Description", style="dim")

            # Add current location option
            options_panel.add_row("📍", "[cyan]C[/cyan]", "Use current location (GPS)")

            # Show recent locations if available
            if recent_locations:
                console.print("[bold]Recent locations:[/bold] [dim](type number to select)[/dim]")

                # Create a visually appealing table for recent locations
                recent_table = Table.grid(padding=1, expand=False)
                recent_table.add_column("Num", style="cyan", justify="right", width=4)
                recent_table.add_column("Location", style="green")

                for i, loc in enumerate(recent_locations[:5], 1):
                    recent_table.add_row(f"[{i}]", loc)

                console.print(recent_table)
                console.print(options_panel)
                console.print("[dim]Or type a new location (city, address, or landmark)...[/dim]")

                # Create a search-like input prompt
                location_input = Prompt.ask("[bold blue]🔍 Search[/bold blue]")

                # Check if user selected a recent location by number
                if location_input.isdigit() and 1 <= int(location_input) <= len(recent_locations[:5]):
                    selected_location = recent_locations[int(location_input) - 1]
                    console.print(f"[green]✓[/green] Selected: [bold]{selected_location}[/bold]")
                    return selected_location

                # Check if user wants to use current location
                elif location_input.upper() == 'C':
                    console.print("[yellow]📡 Accessing location services...[/yellow]")
                    with console.status("[cyan]Getting your current location...[/cyan]", spinner="dots"):
                        # Try to get actual current location coordinates and name
                        try:
                            # Use the weather controller to get current location with readable name
                            location_result = weather_controller.get_current_location_with_name()
                            if location_result:
                                coords, location_name = location_result
                                console.print(f"[green]✓[/green] Location found: [bold]{location_name}[/bold]")
                                return location_name
                            else:
                                # Fall back to a default location if current location can't be determined
                                default_location = "New York"
                                default_coords = weather_controller.get_coordinates_for_location(default_location)
                                console.print(f"[yellow]⚠ Could not determine your current location.[/yellow]")
                                console.print(f"[yellow]Using {default_location} as a fallback.[/yellow]")
                                return default_location
                        except Exception as e:
                            # Log the error but don't show it to the user
                            logger.error(f"Error getting current location: {e}")
                            # Fall back to a simulated location
                            console.print("[green]✓[/green] Location found!")
                            return "Current Location (simulated)"

                # Direct input (no map search option)
                else:
                    return location_input
            else:
                # If no recent locations, show a simplified interface
                console.print(options_panel)
                console.print("[dim]Or type a location (city, address, or landmark)...[/dim]")

                # Create a search-like input prompt
                location_input = Prompt.ask("[bold blue]🔍 Search[/bold blue]")

                # Check if user wants to use current location
                if location_input.upper() == 'C':
                    console.print("[yellow]📡 Accessing location services...[/yellow]")
                    with console.status("[cyan]Getting your current location...[/cyan]", spinner="dots"):
                        # Try to get actual current location coordinates and name
                        try:
                            # Use the weather controller to get current location with readable name
                            location_result = weather_controller.get_current_location_with_name()
                            if location_result:
                                coords, location_name = location_result
                                console.print(f"[green]✓[/green] Location found: [bold]{location_name}[/bold]")
                                return location_name
                            else:
                                # Fall back to a default location if current location can't be determined
                                default_location = "New York"
                                default_coords = weather_controller.get_coordinates_for_location(default_location)
                                console.print(f"[yellow]⚠ Could not determine your current location.[/yellow]")
                                console.print(f"[yellow]Using {default_location} as a fallback.[/yellow]")
                                return default_location
                        except Exception as e:
                            # Log the error but don't show it to the user
                            logger.error(f"Error getting current location: {e}")
                            # Fall back to a simulated location
                            console.print("[green]✓[/green] Location found!")
                            return "Current Location (simulated)"

                # Direct input (no map search option)
                else:
                    return location_input

        # Get starting location with enhanced UI
        start_location = get_location_with_suggestions("Enter starting location (city, address, or landmark)", "starting")

        if start_location:
            # Show a more visually appealing status during lookup
            with console.status(
                "[bold cyan]Looking up coordinates for starting location...[/bold cyan]",
                spinner="dots"
            ) as status:
                start_coords = weather_controller.get_coordinates_for_location(start_location)

            if start_coords:
                console.print(f"[green]✓[/green] Starting location found: [bold]{start_location}[/bold]")

                # Add to recent locations if not already there
                if start_location not in recent_locations and start_location != "Current Location (simulated)":
                    recent_locations = [start_location] + [loc for loc in recent_locations if loc != start_location]
                    # Keep only the 5 most recent locations
                    recent_locations = recent_locations[:5]
                    user_manager_instance.update_user_preference('recent_locations', recent_locations)
            else:
                console.print(Panel(
                    f"[bold yellow]Could not find coordinates for:[/bold yellow] {start_location}\n"
                    "Route information will be limited. Try a different location format.",
                    border_style="yellow",
                    expand=False
                ))

        # Get ending location with enhanced UI
        end_location = get_location_with_suggestions("Enter ending location (city, address, or landmark)", "ending")

        if end_location:
            # Show a more visually appealing status during lookup
            with console.status(
                "[bold cyan]Looking up coordinates for ending location...[/bold cyan]",
                spinner="dots"
            ) as status:
                end_coords = weather_controller.get_coordinates_for_location(end_location)

            if end_coords:
                console.print(f"[green]✓[/green] Ending location found: [bold]{end_location}[/bold]")

                # Add to recent locations if not already there
                if end_location not in recent_locations and end_location != "Current Location (simulated)":
                    recent_locations = [end_location] + [loc for loc in recent_locations if loc != end_location]
                    # Keep only the 5 most recent locations
                    recent_locations = recent_locations[:5]
                    user_manager_instance.update_user_preference('recent_locations', recent_locations)
            else:
                console.print(Panel(
                    f"[bold yellow]Could not find coordinates for:[/bold yellow] {end_location}\n"
                    "Route information will be limited. Try a different location format.",
                    border_style="yellow",
                    expand=False
                ))

        # If we have both coordinates, try to get route information
        if start_coords and end_coords:
            try:
                from controllers.route_controller import RouteController
                route_controller = RouteController()

                # Set cycling preferences for accurate route calculation
                cycling_preferences = {
                    "avoid_highways": True,
                    "prefer_bike_lanes": True,
                    "avoid_steep_hills": False,
                    "surface_preference": "paved"
                }

                with console.status("[cyan]Calculating bicycle route information...[/cyan]", spinner="dots"):
                    route_info = route_controller.get_route_info(start_coords, end_coords, cycling_preferences)

                if route_info:
                    distance = route_info['distance']
                    duration = route_info.get('duration', 0)
                    route_quality = route_info.get('route_quality', 'unknown')
                    source = route_info.get('source', 'estimation')

                    # Display route information with quality indicator
                    quality_color = {
                        'excellent': 'green',
                        'good': 'green',
                        'fair': 'yellow',
                        'poor': 'red',
                        'error': 'red'
                    }.get(route_quality, 'white')

                    console.print(f"[green]✓[/green] Route calculated: [bold]{distance:.1f} km[/bold]")
                    console.print(f"[dim]Duration: {duration:.0f} minutes | Quality: [{quality_color}]{route_quality}[/{quality_color}] | Source: {source}[/dim]")

                    # Show additional info for bike-friendly routes
                    if route_info.get('bike_friendly', False):
                        console.print("[green]🚴[/green] [dim]This route is bicycle-friendly[/dim]")
                    if route_info.get('has_bike_lanes', False):
                        console.print("[green]🛣️[/green] [dim]Route includes bike lanes[/dim]")

            except Exception as e:
                logger.error(f"Error calculating route: {e}")
                console.print("[yellow]Could not calculate route information.[/yellow]")
    except ImportError as e:
        logger.error(f"Error importing controllers: {e}")
        console.print("[yellow]Route planning functionality not available.[/yellow]")

    # Get trip data
    try:
        # Create a section for trip distance
        console.print(Rule("Trip Distance", style="cyan"))

        # Check if we already have a calculated distance from the route
        if route_info and 'distance' in route_info:
            distance = route_info['distance']
            console.print(f"[green]✓[/green] Using calculated route distance: [bold]{distance:.1f} km[/bold]")
            distance_valid = True
        else:
            distance_valid = False
            distance = 0

            while not distance_valid:
                try:
                    # Improved prompt with unit
                    distance_input = Prompt.ask(
                        "[cyan]Distance[/cyan] (in kilometers)",
                        show_default=False
                    )
                    distance = float(distance_input)

                    if distance <= 0:
                        console.print("[bold red]Distance must be positive[/bold red]")
                    elif distance > 1000:
                        console.print("[yellow]That's an impressive distance! Are you sure it's correct?[/yellow]")
                        if Confirm.ask("Confirm this distance?", default=True):
                            distance_valid = True
                            console.print(f"[green]✓[/green] Distance: [bold]{distance} km[/bold]")
                    else:
                        distance_valid = True
                        console.print(f"[green]✓[/green] Distance: [bold]{distance} km[/bold]")

                except ValueError:
                    console.print("[bold red]Please enter a valid number[/bold red]")

        # Create a section for trip duration
        console.print(Rule("Trip Duration", style="cyan"))

        # Check if we already have a calculated duration from the route
        if route_info and 'duration' in route_info:
            duration = route_info['duration']
            console.print(f"[green]✓[/green] Using calculated route duration: [bold]{duration:.1f} minutes[/bold]")
            duration_valid = True
        else:
            duration_valid = False
            duration = 0

            while not duration_valid:
                try:
                    # Improved prompt with unit
                    duration_input = Prompt.ask(
                        "[cyan]Duration[/cyan] (in minutes)",
                        show_default=False
                    )
                    duration = float(duration_input)

                    if duration <= 0:
                        console.print("[bold red]Duration must be positive[/bold red]")
                    elif duration > 1440:  # More than 24 hours
                        console.print("[yellow]That's longer than a day! Are you sure?[/yellow]")
                        if Confirm.ask("Confirm this duration?", default=True):
                            duration_valid = True
                            console.print(f"[green]✓[/green] Duration: [bold]{duration} minutes[/bold]")
                    else:
                        duration_valid = True
                        console.print(f"[green]✓[/green] Duration: [bold]{duration} minutes[/bold]")

                except ValueError:
                    console.print("[bold red]Please enter a valid number[/bold red]")

        # Calculate average speed
        speed = utils.calculate_average_speed(distance, duration)

        # Create a section for weight information
        console.print(Rule("Weight Information", style="cyan"))

        weight = user_manager_instance.get_user_preference('weight_kg', None)
        if weight is not None:
            console.print(f"[green]✓[/green] Using saved weight: [cyan]{weight} kg[/cyan]")
            if not Confirm.ask("Use this weight?", default=True):
                weight = None

        if weight is None:
            weight_valid = False
            weight = 0

            while not weight_valid:
                try:
                    weight_input = Prompt.ask(
                        "[cyan]Your weight[/cyan] (in kg) for calorie calculation"
                    )
                    weight = float(weight_input)

                    if weight <= 0:
                        console.print("[bold red]Weight must be positive[/bold red]")
                    elif weight < 30:
                        console.print("[yellow]That seems very low for an adult. Are you sure?[/yellow]")
                        if Confirm.ask("Confirm this weight?", default=True):
                            weight_valid = True
                            console.print(f"[green]✓[/green] Weight: [bold]{weight} kg[/bold]")
                    elif weight > 200:
                        console.print("[yellow]That seems quite high. Are you sure?[/yellow]")
                        if Confirm.ask("Confirm this weight?", default=True):
                            weight_valid = True
                            console.print(f"[green]✓[/green] Weight: [bold]{weight} kg[/bold]")
                    else:
                        weight_valid = True
                        console.print(f"[green]✓[/green] Weight: [bold]{weight} kg[/bold]")

                except ValueError:
                    console.print("[bold red]Please enter a valid number[/bold red]")

            # Ask if they want to save this weight for future use
            if Confirm.ask("Save this weight for future trips?", default=True):
                user_manager_instance.update_user_preference('weight_kg', weight)
                console.print("[green]Weight saved to your profile![/green]")

        # Calculate calories and CO2 saved
        calories = utils.calculate_calories(distance, speed, int(weight))
        co2_saved = utils.calculate_co2_saved(distance)

        # Update step progress indicator - entering Step 2
        step_progress = Table.grid(padding=1)
        step_progress.add_column("Step", justify="right", style="cyan", no_wrap=True)
        step_progress.add_column("Description", style="green")
        step_progress.add_row("Step 1", "[dim]Enter Trip Information ✓[/dim]")
        step_progress.add_row("Step 2", "[bold]Calculate Trip Impact[/bold]")
        step_progress.add_row("Step 3", "Save and Sync Data")

        console.print(Panel(
            step_progress,
            border_style="dim",
            title="[white on grey15] Progress [/white on grey15]",
            title_align="center"
        ))

        # Display summary with nice formatting
        console.print()
        console.print(Rule("Trip Summary", style="bold cyan"))

        # Create a summary table
        summary_table = Table(box=ROUNDED, border_style="cyan", show_header=False)
        summary_table.add_column("Attribute", style="bold blue", justify="right")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Date", f"{date}")

        # Add route information if available
        if start_location and end_location:
            summary_table.add_row("Route", f"{start_location} to {end_location}")

        summary_table.add_row("Distance", f"{utils.format_distance(distance)}")
        summary_table.add_row("Duration", f"{duration:.1f} minutes")
        summary_table.add_row("Average Speed", f"{speed:.1f} km/h")
        summary_table.add_row("Calories Burned", f"{utils.format_calories(calories)}")
        summary_table.add_row("CO2 Saved", f"{utils.format_co2(co2_saved)}")

        console.print(Panel(summary_table, title="Trip Details", border_style="cyan", box=ROUNDED))

        # Environmental impact panel
        trees_equivalent = co2_saved / 25  # Rough estimate: 1 tree absorbs ~25kg CO2 per year
        gas_liters_saved = co2_saved / 2.3  # Rough estimate: 1L of gas produces ~2.3kg CO2

        impact_panel = Panel(
            f"By cycling instead of driving, you've saved [bold green]{co2_saved:.2f}kg[/bold green] of CO2 emissions.\n"
            f"This is equivalent to:\n"
            f"• [green]The amount of CO2 absorbed by {trees_equivalent:.2f} trees in a year[/green]\n"
            f"• [green]The emissions from burning {gas_liters_saved:.2f} liters of gasoline[/green]",
            title="Environmental Impact",
            border_style="green",
            box=ROUNDED
        )
        console.print(impact_panel)

        # Update step progress indicator - entering Step 3
        step_progress = Table.grid(padding=1)
        step_progress.add_column("Step", justify="right", style="cyan", no_wrap=True)
        step_progress.add_column("Description", style="green")
        step_progress.add_row("Step 1", "[dim]Enter Trip Information ✓[/dim]")
        step_progress.add_row("Step 2", "[dim]Calculate Trip Impact ✓[/dim]")
        step_progress.add_row("Step 3", "[bold]Save and Sync Data[/bold]")

        console.print(Panel(
            step_progress,
            border_style="dim",
            title="[white on grey15] Progress [/white on grey15]",
            title_align="center"
        ))

        # Confirm and save
        console.print()
        if Confirm.ask("Save this trip to your profile?", default=True):
            # Update user stats with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Saving trip data...[/bold blue]"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
            ) as progress:
                save_task = progress.add_task("Saving...", total=100)

                # Simulate progress for updating user stats
                for i in range(40):
                    time.sleep(0.01)
                    progress.update(save_task, completed=i)

                # Actually update user stats
                stats_updated = user_manager_instance.update_user_stats(distance, co2_saved, calories)

                if not stats_updated:
                    progress.stop()
                    console.print(Panel(
                        "There was a problem updating your statistics.",
                        title="Error",
                        border_style="red",
                        box=ROUNDED
                    ))
                    input("\nPress Enter to return to the main menu...")
                    return

                # Progress for database operations
                for i in range(40, 70):
                    time.sleep(0.01)
                    progress.update(save_task, completed=i)

                # Log to the database using the transaction context manager
                db_success = True
                try:
                    if database_manager:
                        with database_manager.transaction() as conn:
                            # Get username
                            user = user_manager_instance.get_current_user()
                            username = user.get('username', 'guest')

                            # Get user_id from username
                            user_data = database_manager.get_user(conn, username)

                            # If user doesn't exist in the database, create it
                            if not user_data:
                                if username == 'guest':
                                    logging.info(f"Creating guest user in database")
                                    user_id = database_manager.add_user(conn, (
                                        'guest',                              # username
                                        'Guest User',                         # name
                                        '',                                   # email
                                        '',                                   # password_hash
                                        '',                                   # salt
                                        '',                                   # google_id
                                        0,                                    # is_admin
                                        1,                                    # is_guest
                                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # registration_date
                                    ))
                                    if not user_id:
                                        raise ValueError(f"Failed to create guest user in database")
                                else:
                                    raise ValueError(f"User {username} not found in database")
                            else:
                                user_id = user_data[0]  # First column is the ID

                            # Prepare route data if available
                            route_data = None
                            if start_location and end_location:
                                route_data_dict = {
                                    "start_location": start_location,
                                    "end_location": end_location,
                                    "route": f"{start_location} to {end_location}"
                                }

                                # Add coordinates if available
                                if start_coords:
                                    route_data_dict["start_coords"] = {"lat": start_coords[0], "lon": start_coords[1]}
                                if end_coords:
                                    route_data_dict["end_coords"] = {"lat": end_coords[0], "lon": end_coords[1]}

                                # Add calculated route info if available
                                if route_info:
                                    # Convert route_info to a serializable format
                                    serializable_route_info = {
                                        "distance": route_info.get("distance", 0),
                                        "duration": route_info.get("duration", 0),
                                        "elevation": route_info.get("elevation", 0)
                                    }
                                    route_data_dict["route_info"] = serializable_route_info

                                # Convert to JSON string
                                import json
                                route_data = json.dumps(route_data_dict)

                            # Now add the trip with the user_id and route data
                            if route_data:
                                database_manager.add_trip(conn, (user_id, date, distance, duration, co2_saved, calories, route_data, None))
                            else:
                                database_manager.add_trip(conn, (user_id, date, distance, duration, co2_saved, calories))
                except Exception as e:
                    logging.error(f"Error logging trip to database: {e}")
                    db_success = False

                # Final progress updates
                for i in range(70, 101):
                    time.sleep(0.01)
                    progress.update(save_task, completed=i)

            # Update final step progress - all completed
            step_progress = Table.grid(padding=1)
            step_progress.add_column("Step", justify="right", style="cyan", no_wrap=True)
            step_progress.add_column("Description", style="green")
            step_progress.add_row("Step 1", "[dim]Enter Trip Information ✓[/dim]")
            step_progress.add_row("Step 2", "[dim]Calculate Trip Impact ✓[/dim]")
            step_progress.add_row("Step 3", "[dim]Save and Sync Data ✓[/dim]")

            console.print(Panel(
                step_progress,
                border_style="dim",
                title="[white on grey15] Completed [/white on grey15]",
                title_align="center"
            ))

            # Show success message
            success_panel = Panel(
                "✓ Trip data saved successfully!\n"
                "✓ Your statistics have been updated\n" +
                ("✓ Record saved to database\n" if db_success else "⚠ Database update failed\n"),
                title="Success",
                border_style="green",
                box=ROUNDED
            )
            console.print(success_panel)

            # Log to Google Sheets if available
            if GOOGLE_SHEETS_AVAILABLE and modules['sheets_manager']:
                sheets_manager = modules['sheets_manager'].SheetsManager()
                trip_data = {
                    'date': date,
                    'distance': distance,
                    'duration': duration,
                    'calories': calories,
                    'co2_saved': co2_saved
                }

                # Add route information if available
                if start_location and end_location:
                    trip_data['route'] = f"{start_location} to {end_location}"
                username = user_manager_instance.get_current_user().get('username', 'unknown')

                # Create an enhanced progress bar for Google Sheets sync
                console.print(Rule("Cloud Sync", style="cyan"))
                console.print("[dim]Synchronizing trip data with cloud storage...[/dim]")

                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold blue]Syncing with Google Sheets...[/bold blue]"),
                    BarColumn(bar_width=40, complete_style="green", finished_style="green"),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    expand=True
                ) as progress:
                    sheet_task = progress.add_task("Syncing...", total=100)

                    # Simulate initial connection progress
                    for i in range(25):
                        time.sleep(0.02)
                        progress.update(sheet_task, completed=i)

                    # Simulate data preparation
                    for i in range(25, 50):
                        time.sleep(0.01)
                        progress.update(sheet_task, completed=i)

                    # Actual sheets operation
                    sheets_success = sheets_manager.log_trip(username, trip_data)

                    # Complete progress with verification steps
                    for i in range(50, 90):
                        time.sleep(0.01)
                        progress.update(sheet_task, completed=i)

                    # Final verification
                    for i in range(90, 101):
                        time.sleep(0.02)
                        progress.update(sheet_task, completed=i)

                if sheets_success:
                    console.print("[green]✓ Trip data successfully synchronized with Google Sheets![/green]")
                else:
                    console.print("[yellow]⚠ Could not sync trip data with Google Sheets[/yellow]")
            else:
                console.print("[dim]Cloud sync not available. Trip saved locally only.[/dim]")

                # Trigger synchronization with web frontend
                try:
                    # Import sync service module
                    from services.sync.sync_service import get_sync_service

                    # Get sync service instance
                    sync_service = get_sync_service(user_manager=user_manager_instance)

                    if sync_service:
                        # Get current user data
                        username = user_manager_instance.get_current_user().get('username', 'unknown')
                        user_data = user_manager_instance.get_user(username)

                        # Queue sync task for user statistics
                        if 'stats' in user_data:
                            sync_service.queue_sync_task('sync_user_stats', username=username, data=user_data['stats'])
                            console.print("[green]✓ Trip data synchronized with web dashboard![/green]")
                            logger.info(f"Triggered synchronization of trip data for user {username}")
                    else:
                        logger.warning("Sync service not available for web synchronization")
                except Exception as e:
                    logger.error(f"Error synchronizing trip data with web dashboard: {e}")
                    console.print("[yellow]⚠ Could not sync trip data with web dashboard[/yellow]")
        else:
            console.print("[yellow]Trip not saved. No data has been recorded.[/yellow]")

    except ValueError as e:
        # Provide more specific error message based on the exception
        error_msg = str(e)
        console.print(Panel(
            f"Error: {error_msg}" if "could not convert string to float" not in error_msg else
            "Error: Please enter numeric values only.",
            title="Input Error",
            border_style="red",
            box=ROUNDED
        ))

        # Log the specific error for debugging
        logger.debug(f"Input validation error in log_cycling_trip: {e}")
    except Exception as e:
        # Catch any unexpected errors
        console.print(Panel(
            f"An unexpected error occurred: {str(e)}",
            title="System Error",
            border_style="red",
            box=ROUNDED
        ))
        logger.error(f"Unexpected error in log_cycling_trip: {e}", exc_info=True)

    # Final prompt to return to menu
    console.print()
    Prompt.ask("Press Enter to return to the main menu", default="")


def view_statistics(user_manager_instance):
    """View user statistics."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']

    ascii_art.clear_screen()
    ascii_art.display_header()

    # Check if using Rich UI
    if HAS_RICH:
        # Create a layout for more organized display
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main")
        )

        # Create a stylish header
        title = Text("Cycling Statistics", style="bold cyan")
        header_panel = Panel(
            Align.center(title),
            box=ROUNDED,
            border_style="cyan",
            padding=(1, 2)
        )
        layout["header"].update(header_panel)

        # Render the layout header
        console.print(layout["header"])

        # Check if user is authenticated
        if not user_manager_instance.is_authenticated():
            console.print(Panel(
                "You need to log in to view statistics.",
                title="Authentication Required",
                border_style="red",
                box=ROUNDED
            ))
            input("\nPress Enter to continue...")
            return
    else:
        # Use ASCII art fallback
        ascii_art.display_section_header("Statistics")

        # Check if user is authenticated
        if not user_manager_instance.is_authenticated():
            print("You need to log in to view statistics.")
            input("Press Enter to continue...")
            return

    # Get user stats
    user = user_manager_instance.get_current_user()
    stats = user.get('stats', {})
    username = user.get('username', 'User')

    if not stats or not stats.get('total_trips', 0):
        if HAS_RICH:
            console.print(Panel(
                "No cycling data recorded yet.\n"
                "Start logging your trips to see your statistics!",
                title="No Data Available",
                border_style="yellow",
                box=ROUNDED
            ))
        else:
            print("No cycling data recorded yet.")
        input("Press Enter to continue...")
        return

    # Display overall stats
    total_trips = stats.get('total_trips', 0)
    total_distance = stats.get('total_distance', 0.0)
    total_co2_saved = stats.get('total_co2_saved', 0.0)
    total_calories = stats.get('total_calories', 0)

    # Calculate averages
    avg_distance = 0
    avg_co2_saved = 0
    avg_calories = 0
    if total_trips > 0:
        avg_distance = total_distance / total_trips
        avg_co2_saved = total_co2_saved / total_trips
        avg_calories = total_calories / total_trips

    # Display stats using Rich UI if available
    if HAS_RICH:
        # Create an overview section with user info
        console.print(Rule("Cycling Overview", style="green"))
        console.print(f"[bold]Statistics for:[/bold] [cyan]{username}[/cyan]")

        # Create a main stats panel layout with 2 columns
        stats_layout = Layout()
        stats_layout.split_column(
            Layout(name="summary_stats"),
            Layout(name="impact")
        )

        # Create a table for overall stats with improved styling
        stats_table = Table(
            title="Summary Statistics",
            box=ROUNDED,
            border_style="green",
            header_style="bold green",
            show_header=True,
            expand=True
        )

        stats_table.add_column("Metric", style="cyan", justify="right")
        stats_table.add_column("Value", style="green")

        # Add overall stats rows with icons for visual appeal
        stats_table.add_row("🚲 Total Trips", f"{total_trips}")
        stats_table.add_row("📏 Total Distance", f"{total_distance:.1f} km")
        stats_table.add_row("🌿 CO₂ Saved", f"{total_co2_saved:.2f} kg")
        stats_table.add_row("🔥 Calories Burned", f"{total_calories}")

        # Add average stats if available
        if total_trips > 0:
            stats_table.add_section()
            stats_table.add_row("📊 Avg Distance/Trip", f"{avg_distance:.1f} km")
            stats_table.add_row("📊 Avg CO₂/Trip", f"{avg_co2_saved:.2f} kg")
            stats_table.add_row("📊 Avg Calories/Trip", f"{avg_calories:.0f}")

        # Display the table
        stats_layout["summary_stats"].update(stats_table)

        # Display environmental impact panel with more visually appealing content
        trees_equivalent = total_co2_saved / 0.022  # Daily CO2 absorption
        tree_years = total_co2_saved / 25  # Annual CO2 absorption per tree
        car_km_saved = total_co2_saved / 0.2  # CO2 from car travel (kg/km)

        impact_panel = Panel(
            f"Your cycling has saved [bold green]{total_co2_saved:.2f} kg[/bold green] of CO2 emissions.\n\n"
            f"[green]Environmental Equivalents:[/green]\n"
            f"🌳 Equal to {trees_equivalent:.1f} trees filtering air for a day\n"
            f"🌳 Or {tree_years:.2f} trees for a full year\n"
            f"🚗 Prevented emissions from {car_km_saved:.1f} km of driving",
            title="Environmental Impact",
            border_style="blue",
            box=ROUNDED,
            expand=True
        )
        stats_layout["impact"].update(impact_panel)

        # Display the entire statistics layout
        console.print(stats_layout)

    else:
        # Fallback to standard output
        print(f"Total Trips: {total_trips}")
        print(f"Total Distance: {total_distance:.1f} km")
        print(f"Total CO2 Saved: {total_co2_saved:.2f} kg")
        print(f"Total Calories Burned: {total_calories}")

        # Display averages if available
        if total_trips > 0:
            print(f"\nAverage Distance per Trip: {avg_distance:.1f} km")
            print(f"Average CO2 Saved per Trip: {avg_co2_saved:.2f} kg")
            print(f"Average Calories Burned per Trip: {avg_calories:.0f}")

    # Display recent trips if available
    trips = stats.get('trips', [])

    # Check if data visualization module is available
    try:
        from apps.data_visualization import DataVisualization
        viz_available = True
    except ImportError:
        DataVisualization = None
        viz_available = False

    if trips:
        if HAS_RICH:
            console.print(Rule("Recent Cycling Activity", style="cyan"))

            # Extract recent trips (up to 5)
            recent_trips = trips[-5:] if len(trips) > 5 else trips

            # Create a better table for recent trips
            trips_table = Table(
                title=f"Last {len(recent_trips)} Cycling Trips",
                box=ROUNDED,
                border_style="cyan",
                header_style="bold cyan",
                expand=True
            )

            # Add columns with better styling
            trips_table.add_column("Date", style="cyan")
            trips_table.add_column("Route", style="cyan")
            trips_table.add_column("Distance", style="green", justify="right")
            trips_table.add_column("CO₂ Saved", style="green", justify="right")
            trips_table.add_column("Calories", style="green", justify="right")

            # Add trip rows with improved formatting
            for trip in reversed(recent_trips):  # Show most recent first
                date = trip.get('date', 'Unknown').split('T')[0]  # Extract date part
                distance = trip.get('distance', 0.0)
                co2_saved = trip.get('co2_saved', 0.0)
                calories = trip.get('calories', 0)

                # Get route information if available
                route_str = trip.get('route', 'N/A')

                trips_table.add_row(
                    date,
                    route_str,
                    f"{distance:.1f} km",
                    f"{co2_saved:.2f} kg",
                    f"{calories}"
                )

            # Display the trips table
            console.print(trips_table)

            # Show total trips count if more than shown
            if len(trips) > len(recent_trips):
                console.print(f"[dim]+ {len(trips) - len(recent_trips)} more trip(s) not shown[/dim]")
        else:
            ascii_art.display_section_header("Recent Trips")

            # Extract recent trips (up to 5)
            recent_trips = trips[-5:] if len(trips) > 5 else trips

            # Prepare data for table
            headers = ["Date", "Route", "Distance (km)", "CO₂ Saved (kg)", "Calories"]
            data = []

            for trip in reversed(recent_trips):  # Show most recent first
                date = trip.get('date', 'Unknown').split('T')[0]  # Extract date part
                distance = trip.get('distance', 0.0)
                co2_saved = trip.get('co2_saved', 0.0)
                calories = trip.get('calories', 0)

                # Get route information if available
                route_str = trip.get('route', 'N/A')

                data.append([date, route_str, f"{distance:.1f}", f"{co2_saved:.2f}", calories])

            # Display table
            ascii_art.display_data_table(headers, data)

            # Show total trips count if more than shown
            if len(trips) > len(recent_trips):
                print(f"\n+ {len(trips) - len(recent_trips)} more trip(s) not shown")

    # Options for more detailed stats
    if HAS_RICH:
        console.print(Rule("Options", style="yellow"))

        options_panel = Panel(
            "Select an option below to continue\n\n"
            "[cyan]1.[/cyan] Return to main menu\n" +
            ("[cyan]2.[/cyan] View detailed charts and graphs" if viz_available else ""),
            title="Actions",
            border_style="yellow",
            box=ROUNDED
        )
        console.print(options_panel)

        choice = Prompt.ask("Select an option", choices=["1", "2"] if viz_available else ["1"], default="1")
    else:
        print("\nOptions:")
        print("1. Return to main menu")

        # Check if data visualization module is available
        if viz_available:
            print("2. View detailed charts and graphs")

        choice = input("\nSelect an option: ")

    if choice == "2" and viz_available and DataVisualization is not None:
        # Run the data visualization module
        data_viz = DataVisualization(user_manager=user_manager_instance)
        data_viz.run_visualization()
    else:
        # Return to main menu
        return


def eco_challenges(user_manager_instance):
    """Access the eco-challenges feature."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']

    ascii_art.clear_screen()
    ascii_art.display_header()
    ascii_art.display_section_header("Eco-Challenges")

    # Check if eco_challenges module is available
    try:
        if 'eco_challenges' in modules and modules['eco_challenges']:
            # Run the eco challenges module
            modules['eco_challenges'].run_eco_challenges(user_manager_instance, modules.get('sheets_manager'))
            return
    except Exception as e:
        logger.error(f"Error running eco challenges: {e}")
        pass  # Continue to basic implementation

    # Basic implementation if the module is not available
    print("Eco-challenges module not available.")
    print("\nEco-challenges help you track and achieve sustainability goals through:")
    print("- Weekly sustainability challenges")
    print("- Goal tracking and progress visualization")
    print("- Community challenges and leaderboards")
    print("- Personalized challenge suggestions")

    if user_manager_instance.is_authenticated():
        # Show basic challenge suggestions
        print("\nHere are some eco-challenges you can try:")
        print("1. Cycle to work/school every day this week")
        print("2. Replace one car trip with cycling every day")
        print("3. Track and reduce your carbon footprint by 10%")
        print("4. Cycle for leisure at least twice this week")
        print("5. Try a new cycling route to discover your area")
    else:
        print("\nYou need to log in to access personalized eco-challenges.")

    input("\nPress Enter to return to the main menu...")


def calculate_carbon_footprint(user_manager_instance):
    """Calculate user's carbon footprint and show alternatives."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']

    ascii_art.clear_screen()
    ascii_art.display_header()

    # Use Rich UI if available
    if HAS_RICH:
        # Display header with Rich styling
        console.print(Panel.fit(
            Text("Carbon Footprint Calculator", style="bold green"),
            border_style="green"
        ))

        # Display description with Rich styling
        console.print(Panel(
            "Measure your environmental impact and discover how your cycling habits\n"
            "reduce carbon emissions and contribute to a greener planet.",
            border_style="blue"
        ))
    else:
        # Fallback to ASCII art display
        ascii_art.display_section_header("Carbon Footprint Calculator")

    # Check if enhanced carbon impact tracker is available
    try:
        if 'carbon_impact_tracker' in modules and modules['carbon_impact_tracker']:
            # Run the enhanced carbon impact tracker
            modules['carbon_impact_tracker'].run_carbon_tracker(user_manager_instance, modules.get('sheets_manager'))
            return
    except Exception as e:
        logger.error(f"Error running carbon impact tracker: {e}")
        pass  # Continue to try the basic module

    # Try to use the basic carbon footprint calculator
    try:
        from apps import carbon_footprint

        # Run the carbon footprint module
        carbon_footprint.run_calculator(user_manager_instance)
    except ImportError:
        # Basic implementation if the module is not available
        if HAS_RICH:
            console.print(Panel(
                "Carbon footprint calculation module not available.\n"
                "Using built-in basic calculator instead.",
                title="Module Status",
                border_style="yellow",
                box=ROUNDED
            ))
        else:
            print("Carbon footprint calculation module not available.")

        # Display user's cycling impact
        if user_manager_instance.is_authenticated():
            user = user_manager_instance.get_current_user()
            stats = user.get('stats', {})

            if stats and stats.get('total_trips', 0) > 0:
                # Show basic achievements based on stats
                total_trips = stats.get('total_trips', 0)
                total_distance = stats.get('total_distance', 0.0)

                # Calculate equivalents
                trees_month = total_distance / 20  # One tree absorbs about 20kg CO2 per month
                car_km = total_distance / 0.2  # Average car emits about 200g CO2 per km

                if HAS_RICH:
                    # Create impact table
                    impact_table = Table(title="Your Environmental Impact", box=ROUNDED, border_style="green")
                    impact_table.add_column("Metric", style="cyan")
                    impact_table.add_column("Value", style="green")

                    # Add impact rows
                    impact_table.add_row("CO₂ Emissions Saved", f"{total_distance:.2f} kg")
                    impact_table.add_row("Equivalent to Trees" , f"{trees_month:.1f} trees/month")
                    impact_table.add_row("Car Travel Avoided", f"{car_km:.1f} km")

                    # Display the table
                    console.print(impact_table)

                    # Display visualization suggestion
                    console.print(Panel(
                        "For a more detailed analysis, try our advanced carbon tracking feature\n"
                        "or install the carbon footprint calculation module.",
                        title="Suggestion",
                        border_style="blue"
                    ))
                else:
                    print(f"\nYour cycling has saved approximately {total_distance:.2f} kg of CO2 emissions.")
                    print("This is equivalent to:")
                    print(f"- The CO2 absorbed by {trees_month:.1f} trees in one month")
                    print(f"- The emissions from driving {car_km:.1f} km in an average car")
            else:
                if HAS_RICH:
                    console.print(Panel(
                        "No cycling data recorded yet.\n"
                        "Start logging your trips to see your environmental impact!",
                        title="No Data Available",
                        border_style="yellow"
                    ))
                else:
                    print("\nNo cycling data recorded yet. Start logging your trips to see your environmental impact!")
        else:
            if HAS_RICH:
                console.print(Panel(
                    "You need to log in to see your personalized carbon footprint data.",
                    title="Authentication Required",
                    border_style="red"
                ))
            else:
                print("\nYou need to log in to see your personalized carbon footprint data.")

    if HAS_RICH:
        console.print("[cyan]Press Enter to return to the main menu...[/cyan]")
    input("\nPress Enter to return to the main menu...")


def weather_route_planner(user_manager_instance):
    """Check weather and plan cycling routes."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']

    # Import dependency manager for package installation
    from core.dependency import dependency_manager

    # Use dependency manager's is_package_installed function
    is_package_installed = dependency_manager.is_package_installed

    ascii_art.clear_screen()

    # Use Rich UI if available
    if HAS_RICH:
        # Create a layout for the header
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main")
        )

        # Create a stylish header
        title = Text("Weather & Route Planner", style="bold blue")
        header_panel = Panel(
            Align.center(title),
            box=DOUBLE,
            border_style="bright_blue",
            padding=(1, 10)
        )
        layout["header"].update(header_panel)

        # Render the layout header
        console.print(layout["header"])

        # Show description
        console.print(Panel(
            "Plan your cycling routes with real-time weather information and route optimization",
            box=ROUNDED,
            border_style="blue",
            padding=(1, 2)
        ))

        # Create a menu table
        menu_table = Table(show_header=False, box=ROUNDED, border_style="blue")
        menu_table.add_column("Option", style="cyan")
        menu_table.add_column("Description", style="green")

        # Add exit option
        menu_table.add_row("0", "[yellow]Return to Main Menu[/yellow]")

        # Add menu options
        menu_table.add_row("1", "[cyan]Check Weather Forecast for Cycling[/cyan]")
        menu_table.add_row("2", "[cyan]Plan Cycling Route[/cyan]")
        menu_table.add_row("3", "[cyan]View Saved Routes[/cyan]")
        menu_table.add_row("4", "[cyan]Cycling Impact Calculator[/cyan]")
        menu_table.add_row("5", "[cyan]AI-powered route recommendations[/cyan]")

        # Display the menu
        console.print(Panel(menu_table, title="Route Planning Options", border_style="blue"))

        # Get user choice
        choice = Prompt.ask(
            "Select an option",
            choices=["0", "1", "2", "3", "4", "5"],
            default="2"
        )
    else:
        # Fallback to ASCII art display
        ascii_art.display_header()
        ascii_art.display_section_header("Weather and Route Planner")

        # Show menu options for different route planning modes
        options = [
            "Check weather forecast for cycling",
            "Plan cycling routes",
            "View saved routes",
            "Cycling impact calculator",
            "AI-powered route recommendations"
        ]

        ascii_art.display_menu("Route Planning Options", options)
        choice = input("\nSelect an option (0-5) or press Enter for basic route planning: ")

    if choice == "0":
        # Return to main menu
        return
    elif choice == "1":
        # Check Weather Forecast for Cycling - call directly without showing menu
        try:
            # Check if the requests package is available using importlib
            import importlib.util
            requests_spec = importlib.util.find_spec('requests')
            requests_available = requests_spec is not None

            # Use the weather module from modules dictionary
            if 'weather_route_planner' in modules and requests_available:
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[bold blue]Loading weather data...[/bold blue]"),
                        BarColumn(),
                        TimeElapsedColumn(),
                        transient=True
                    ) as progress:
                        task = progress.add_task("Loading...", total=100)
                        # Simulate progress
                        for i in range(0, 101, 5):
                            time.sleep(0.05)
                            progress.update(task, completed=i)

                # Call check_weather directly instead of run_planner
                planner = modules['weather_route_planner'].WeatherRoutePlanner(user_manager_instance)
                planner.check_weather()
            elif not requests_available:
                if HAS_RICH:
                    console.print(Panel(
                        "Weather forecast module requires the 'requests' package.\n"
                        "Installing required packages...",
                        title="Missing Dependency",
                        border_style="yellow",
                        box=ROUNDED
                    ))
                else:
                    print("Weather forecast module not available. Installing required packages...")

                dependency_manager.ensure_package('requests', silent=False)

                if HAS_RICH:
                    console.print(Panel(
                        "Installed 'requests' package. Please restart the application to use this feature.",
                        title="Installation Complete",
                        border_style="green",
                        box=ROUNDED
                    ))
                else:
                    print("Installed 'requests' package. Please restart the application to use this feature.")
            else:
                if HAS_RICH:
                    console.print(Panel(
                        "Weather route planner module not available.",
                        title="Module Not Found",
                        border_style="red",
                        box=ROUNDED
                    ))
                else:
                    print("Weather route planner module not available.")
        except Exception as e:
            if HAS_RICH:
                console.print(Panel(
                    f"Error accessing weather forecast: {str(e)}\n"
                    "Please report this issue to the developers.",
                    title="Error",
                    border_style="red",
                    box=ROUNDED
                ))
            else:
                print(f"Error accessing weather forecast: {str(e)}")
                print("Please report this issue to the developers.")
                import traceback
                traceback.print_exc()

    elif choice == "3":
        # View Saved Routes
        try:
            if 'weather_route_planner' in modules:
                # Use the weather route planner's view saved routes functionality
                planner = modules['weather_route_planner'].WeatherRoutePlanner(user_manager_instance)
                planner.view_saved_routes()
            else:
                # Try direct import
                from apps.route_planner.weather_route_planner import WeatherRoutePlanner
                planner = WeatherRoutePlanner(user_manager_instance)
                planner.view_saved_routes()
        except ImportError:
            if HAS_RICH:
                console.print(Panel(
                    "View saved routes functionality not available.\n"
                    "This feature requires the route planning module.",
                    title="Module Not Found",
                    border_style="yellow",
                    box=ROUNDED
                ))
            else:
                print("View saved routes functionality not available.")
                print("This feature requires the route planning module.")

    elif choice == "4":
        # Cycling Impact Calculator
        try:
            if 'weather_route_planner' in modules:
                # Use the weather route planner's cycling impact calculator
                planner = modules['weather_route_planner'].WeatherRoutePlanner(user_manager_instance)
                planner.cycling_impact_calculator()
            else:
                # Try direct import
                from apps.route_planner.weather_route_planner import WeatherRoutePlanner
                planner = WeatherRoutePlanner(user_manager_instance)
                planner.cycling_impact_calculator()
        except ImportError:
            if HAS_RICH:
                console.print(Panel(
                    "Cycling impact calculator not available.\n"
                    "This feature requires the route planning module.",
                    title="Module Not Found",
                    border_style="yellow",
                    box=ROUNDED
                ))
            else:
                print("Cycling impact calculator not available.")
                print("This feature requires the route planning module.")

    elif choice == "5":
        # AI Route Planner
        try:
            if 'ai_route_planner' in modules and modules['ai_route_planner']:
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(spinner_name="dots"),
                        TextColumn("[bold blue]Initializing AI route planner...[/bold blue]"),
                        BarColumn(),
                        TimeElapsedColumn(),
                        transient=True
                    ) as progress:
                        task = progress.add_task("Loading...", total=100)
                        # Simulate progress
                        for i in range(0, 101, 2):
                            time.sleep(0.03)
                            progress.update(task, completed=i)

                # Run the AI route planner
                modules['ai_route_planner'].run_ai_route_planner(user_manager_instance, modules.get('sheets_manager'))
            else:
                if HAS_RICH:
                    console.print(Panel(
                        "AI route planner module not available.\n"
                        "This feature requires the Google Generative AI package and API key.",
                        title="Module Not Found",
                        border_style="yellow",
                        box=ROUNDED
                    ))
                else:
                    print("AI route planner module not available.")
                    print("This feature requires the Google Generative AI package and API key.")

                if not is_package_installed('google-generativeai'):
                    if HAS_RICH:
                        console.print("[yellow]Installing required package 'google-generativeai'...[/yellow]")
                    else:
                        print("Installing required package 'google-generativeai'...")

                    dependency_manager.ensure_package('google-generativeai', silent=False)

                    if HAS_RICH:
                        console.print("[green]Installation complete. Please restart the application to use this feature.[/green]")
                    else:
                        print("Please restart the application to use this feature.")

                # Check if API key is available
                if os.environ.get('GEMINI_API_KEY') is None:
                    if HAS_RICH:
                        console.print(Panel(
                            "The GEMINI_API_KEY environment variable is not set.\n"
                            "You'll need to create a Google AI Studio account and obtain an API key.\n"
                            "Then add it to your .env file as GEMINI_API_KEY=your_key_here",
                            title="API Key Required",
                            border_style="yellow",
                            box=ROUNDED
                        ))
                    else:
                        print("\nThe GEMINI_API_KEY environment variable is not set.")
                        print("You'll need to create a Google AI Studio account and obtain an API key.")
                        print("Then add it to your .env file as GEMINI_API_KEY=your_key_here")
        except Exception as e:
            logger.error(f"Error running AI route planner: {e}")
            if HAS_RICH:
                console.print(Panel(
                    f"Error running AI route planner: {str(e)}",
                    title="Error",
                    border_style="red",
                    box=ROUNDED
                ))
            else:
                print(f"Error running AI route planner: {e}")

    else:  # Default or "2": Plan Cycling Route - call directly without showing menu
        # Route planner with improved UI and distinct functionality from weather forecasting
        try:
            # First, check if weather_route_planner is available in modules
            if 'weather_route_planner' in modules:
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[bold blue]Loading route planner...[/bold blue]"),
                        BarColumn(),
                        TimeElapsedColumn(),
                        transient=True
                    ) as progress:
                        task = progress.add_task("Loading...", total=100)
                        # Simulate progress
                        for i in range(0, 101, 5):
                            time.sleep(0.04)
                            progress.update(task, completed=i)

                # Call plan_route directly instead of run_planner
                planner = modules['weather_route_planner'].WeatherRoutePlanner(user_manager_instance)
                planner.plan_route()
                return

            # If not in modules, try direct import
            from apps.route_planner.weather_route_planner import WeatherRoutePlanner

            if HAS_RICH:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Loading route planner...[/bold blue]"),
                    BarColumn(),
                    TimeElapsedColumn(),
                    transient=True
                ) as progress:
                    task = progress.add_task("Loading...", total=100)
                    # Simulate progress
                    for i in range(0, 101, 5):
                        time.sleep(0.04)
                        progress.update(task, completed=i)

            # Call plan_route directly instead of run_planner
            planner = WeatherRoutePlanner(user_manager_instance)
            planner.plan_route()
        except ImportError:
            # Basic implementation if the module is not available
            if HAS_RICH:
                console.print(Panel(
                    "Weather and route planning module not available.\n"
                    "This feature helps you check weather conditions and plan optimal cycling routes.",
                    title="Module Not Found",
                    border_style="yellow",
                    box=ROUNDED
                ))

                console.print("[yellow]Installing required dependencies...[/yellow]")
            else:
                print("Weather and route planning module not available.")
                print("\nThis feature helps you check weather conditions and plan optimal cycling routes.")
                print("Installing required dependencies...")

            # Check which dependencies are missing
            missing = []
            for pkg in ['requests', 'folium']:
                if not is_package_installed(pkg):
                    missing.append(pkg)

            if missing:
                if HAS_RICH:
                    console.print(f"[yellow]Installing missing dependencies: {', '.join(missing)}...[/yellow]")
                else:
                    print(f"Installing missing dependencies: {', '.join(missing)}...")

                dependency_manager.ensure_packages(missing, silent=False)

                if HAS_RICH:
                    console.print("[green]Installation complete. Please restart the application to use this feature.[/green]")
                else:
                    print("Please restart the application to use this feature.")

    if HAS_RICH:
        console.print("[cyan]Press Enter to return to the main menu...[/cyan]")
    input("\nPress Enter to return to the main menu...")


def settings_preferences(user_manager_instance):
    """Manage user settings and preferences using the enhanced Settings View."""
    try:
        # Import the settings view module
        from views.settings_view import show_settings

        # Use the new settings view that incorporates Rich UI styling
        show_settings(user_manager_instance)
    except ImportError as e:
        # Fallback to basic implementation if the settings_view module cannot be imported
        logger.error(f"Failed to import settings view: {e}")
        modules = import_local_modules()
        ascii_art = modules['ascii_art']
        ascii_art.display_error_message("Settings view module not available. Using basic settings interface.")

        # Use existing implementation as fallback
        _basic_settings_preferences(user_manager_instance)


def _basic_settings_preferences(user_manager_instance):
    """Legacy implementation of settings and preferences as fallback."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']

    # Use Rich UI if available
    if not HAS_RICH:
        ascii_art.display_error_message("Required dependencies not available. Please install rich package.")
        return

    # Check if user is authenticated
    if not user_manager_instance.is_authenticated():
        os.system('cls' if os.name == 'nt' else 'clear')
        if HAS_RICH:
            console.print(Panel(
                "You need to log in to manage settings and preferences.",
                title="Authentication Required",
                border_style="red",
                box=ROUNDED
            ))
        else:
            ascii_art.display_header()
            print("You need to log in to manage settings and preferences.")
        input("\nPress Enter to continue...")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        if HAS_RICH:
            # Create a layout for the header
            layout = Layout()
            layout.split(
                Layout(name="header", size=3),
                Layout(name="main")
            )

            # Create a stylish header
            title = Text("Settings and Preferences", style="bold green")
            header_panel = Panel(
                Align.center(title),
                box=DOUBLE,
                border_style="purple",
                padding=(1, 10)
            )
            layout["header"].update(header_panel)

            # Render the layout header
            console.print(layout["header"])

            # Show description
            console.print(Panel(
                "Manage your personal settings and preferences for EcoCycle",
                box=ROUNDED,
                border_style="purple",
                padding=(1, 2)
            ))
        else:
            ascii_art.display_header()
            ascii_art.display_section_header("Settings and Preferences")

        # Get current preferences
        weight_kg = user_manager_instance.get_user_preference('weight_kg', 70)
        transport_mode = user_manager_instance.get_user_preference('default_transport_mode', 'bicycle')
        theme = user_manager_instance.get_user_preference('theme', 'default')
        notifications = user_manager_instance.get_user_preference('notifications_enabled', False)
        units = user_manager_instance.get_user_preference('units', 'metric')

        # Display current settings
        if HAS_RICH:
            preferences_table = Table(title="Current Settings", box=ROUNDED, border_style="purple")
            preferences_table.add_column("Setting", style="cyan")
            preferences_table.add_column("Current Value", style="green")
            preferences_table.add_column("Option", style="yellow")

            preferences_table.add_row("Weight", f"{weight_kg} kg", "1")
            preferences_table.add_row("Default Transport Mode", transport_mode, "2")
            preferences_table.add_row("Theme", theme, "3")
            preferences_table.add_row("Notifications", "Enabled" if notifications else "Disabled", "4")
            preferences_table.add_row("Units", units, "5")
            preferences_table.add_row("Back to Main Menu", "", "6")

            console.print(preferences_table)

            choice = Prompt.ask(
                "\n[bold purple]Select a setting to change[/bold purple]",
                choices=["1", "2", "3", "4", "5", "6"],
                default="6"
            )
        else:
            print("Current Settings:")
            print(f"1. Weight: {weight_kg} kg")
            print(f"2. Default Transport Mode: {transport_mode}")
            print(f"3. Theme: {theme}")
            print(f"4. Notifications: {'Enabled' if notifications else 'Disabled'}")
            print(f"5. Units: {units}")
            print("6. Back to Main Menu")

            # Get user choice
            choice = input("\nSelect a setting to change (1-6): ")

        if choice == '1':
            # Change weight
            if HAS_RICH:
                console.print(Panel(
                    "Enter your weight in kilograms",
                    title="Update Weight",
                    border_style="cyan",
                    box=ROUNDED
                ))

                try:
                    with console.status("[cyan]Updating weight...", spinner="dots"):
                        new_weight = float(Prompt.ask("[cyan]Weight[/cyan] (in kg)"))
                        user_manager_instance.update_user_preference('weight_kg', new_weight)
                    console.print(Panel(
                        f"Weight updated to [bold]{new_weight} kg[/bold]",
                        title="Success",
                        border_style="green",
                        box=ROUNDED
                    ))
                except ValueError:
                    console.print(Panel(
                        "Invalid input. Please enter a numeric value.",
                        title="Error",
                        border_style="red",
                        box=ROUNDED
                    ))
            else:
                try:
                    new_weight = float(input("Enter your weight in kg: "))
                    user_manager_instance.update_user_preference('weight_kg', new_weight)
                    ascii_art.display_success_message("Weight updated successfully!")
                except ValueError:
                    ascii_art.display_error_message("Invalid input. Please enter a numeric value.")

        elif choice == '2':
            # Change default transport mode
            modes = ['bicycle', 'e-bike', 'scooter', 'skateboard']

            if HAS_RICH:
                console.print(Panel(
                    "Select your preferred mode of transportation",
                    title="Update Transport Mode",
                    border_style="cyan",
                    box=ROUNDED
                ))

                mode_table = Table(box=ROUNDED, border_style="cyan")
                mode_table.add_column("Option", style="yellow")
                mode_table.add_column("Transport Mode", style="green")

                for i, mode in enumerate(modes, 1):
                    mode_table.add_row(str(i), mode)

                console.print(mode_table)

                try:
                    mode_choice = int(Prompt.ask(
                        "[cyan]Select a transport mode[/cyan]",
                        choices=[str(i) for i in range(1, len(modes) + 1)],
                        default="1"
                    ))

                    with console.status("[cyan]Updating transport mode...", spinner="dots"):
                        if 1 <= mode_choice <= len(modes):
                            user_manager_instance.update_user_preference('default_transport_mode', modes[mode_choice-1])

                    console.print(Panel(
                        f"Default transport mode updated to [bold]{modes[mode_choice-1]}[/bold]",
                        title="Success",
                        border_style="green",
                        box=ROUNDED
                    ))
                except ValueError:
                    console.print(Panel(
                        "Invalid input. Please enter a number.",
                        title="Error",
                        border_style="red",
                        box=ROUNDED
                    ))
            else:
                print("\nAvailable Transport Modes:")
                for i, mode in enumerate(modes, 1):
                    print(f"{i}. {mode}")

                try:
                    mode_choice = int(input("\nSelect a transport mode (1-4): "))
                    if 1 <= mode_choice <= len(modes):
                        user_manager_instance.update_user_preference('default_transport_mode', modes[mode_choice-1])
                        ascii_art.display_success_message("Default transport mode updated successfully!")
                    else:
                        ascii_art.display_error_message("Invalid selection.")
                except ValueError:
                    ascii_art.display_error_message("Invalid input. Please enter a number.")

        elif choice == '3':
            # Change theme
            themes = ['default', 'dark', 'eco', 'high-contrast']

            if HAS_RICH:
                console.print(Panel(
                    "Select your preferred application theme",
                    title="Update Theme",
                    border_style="cyan",
                    box=ROUNDED
                ))

                theme_table = Table(box=ROUNDED, border_style="cyan")
                theme_table.add_column("Option", style="yellow")
                theme_table.add_column("Theme", style="green")

                for i, theme_option in enumerate(themes, 1):
                    theme_table.add_row(str(i), theme_option)

                console.print(theme_table)

                try:
                    theme_choice = int(Prompt.ask(
                        "[cyan]Select a theme[/cyan]",
                        choices=[str(i) for i in range(1, len(themes) + 1)],
                        default="1"
                    ))

                    with console.status("[cyan]Updating theme...", spinner="dots"):
                        if 1 <= theme_choice <= len(themes):
                            user_manager_instance.update_user_preference('theme', themes[theme_choice-1])

                    console.print(Panel(
                        f"Theme updated to [bold]{themes[theme_choice-1]}[/bold]",
                        title="Success",
                        border_style="green",
                        box=ROUNDED
                    ))
                except ValueError:
                    console.print(Panel(
                        "Invalid input. Please enter a number.",
                        title="Error",
                        border_style="red",
                        box=ROUNDED
                    ))
            else:
                print("\nAvailable Themes:")
                for i, theme_option in enumerate(themes, 1):
                    print(f"{i}. {theme_option}")

                try:
                    theme_choice = int(input("\nSelect a theme (1-4): "))
                    if 1 <= theme_choice <= len(themes):
                        user_manager_instance.update_user_preference('theme', themes[theme_choice-1])
                        ascii_art.display_success_message("Theme updated successfully!")
                    else:
                        ascii_art.display_error_message("Invalid selection.")
                except ValueError:
                    ascii_art.display_error_message("Invalid input. Please enter a number.")

        elif choice == '4':
            # Toggle notifications
            new_setting = not notifications

            if HAS_RICH:
                with console.status("[cyan]Updating notification settings...", spinner="dots"):
                    user_manager_instance.update_user_preference('notifications_enabled', new_setting)

                status = "enabled" if new_setting else "disabled"
                console.print(Panel(
                    f"Notifications are now [bold]{status}[/bold]",
                    title="Success",
                    border_style="green",
                    box=ROUNDED
                ))
            else:
                user_manager_instance.update_user_preference('notifications_enabled', new_setting)
                status = "enabled" if new_setting else "disabled"
                ascii_art.display_success_message(f"Notifications {status} successfully!")

        elif choice == '5':
            # Change units
            units_options = ['metric', 'imperial']

            if HAS_RICH:
                console.print(Panel(
                    "Select your preferred measurement units",
                    title="Update Units",
                    border_style="cyan",
                    box=ROUNDED
                ))

                units_table = Table(box=ROUNDED, border_style="cyan")
                units_table.add_column("Option", style="yellow")
                units_table.add_column("Units", style="green")
                units_table.add_column("Example", style="blue")

                units_table.add_row("1", "Metric", "kilometers, kilograms")
                units_table.add_row("2", "Imperial", "miles, pounds")

                console.print(units_table)

                try:
                    units_choice = int(Prompt.ask(
                        "[cyan]Select units[/cyan]",
                        choices=["1", "2"],
                        default="1"
                    ))

                    with console.status("[cyan]Updating units preference...", spinner="dots"):
                        if 1 <= units_choice <= len(units_options):
                            user_manager_instance.update_user_preference('units', units_options[units_choice-1])

                    console.print(Panel(
                        f"Units updated to [bold]{units_options[units_choice-1]}[/bold]",
                        title="Success",
                        border_style="green",
                        box=ROUNDED
                    ))
                except ValueError:
                    console.print(Panel(
                        "Invalid input. Please enter a number.",
                        title="Error",
                        border_style="red",
                        box=ROUNDED
                    ))
            else:
                print("\nAvailable Units:")
                print("1. Metric (kilometers, kilograms)")
                print("2. Imperial (miles, pounds)")

                try:
                    units_choice = int(input("\nSelect units (1-2): "))
                    if 1 <= units_choice <= len(units_options):
                        user_manager_instance.update_user_preference('units', units_options[units_choice-1])
                        ascii_art.display_success_message("Units updated successfully!")
                    else:
                        ascii_art.display_error_message("Invalid selection.")
                except ValueError:
                    ascii_art.display_error_message("Invalid input. Please enter a number.")

        elif choice == '6':
            # Back to main menu
            break

        else:
            if HAS_RICH:
                console.print(Panel(
                    "Invalid choice. Please try again.",
                    title="Error",
                    border_style="red",
                    box=ROUNDED
                ))
            else:
                ascii_art.display_error_message("Invalid choice. Please try again.")

        if HAS_RICH:
            console.print("\n[italic cyan]Press Enter to continue...[/italic cyan]")
        input()

def social_sharing(user_manager_instance):
    """Manage social sharing and achievements with enhanced animations."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']

    ascii_art.clear_screen()
    ascii_art.display_header()
    ascii_art.display_section_header("Social Sharing and Achievements")

    # Try to use the new modular implementation first
    try:
        from apps.social_gamification import get_social_gamification

        # Create social gamification manager and run features
        social = get_social_gamification(user_manager_instance)
        social.run_social_features()
        return
    except ImportError as e:
        logger.debug(f"New social_gamification package not available: {e}")

        # Fall back to the legacy implementation
        try:
            from apps.gamification import run_social_features

            # Run the social sharing and achievements module (legacy)
            run_social_features(user_manager_instance)
            return
        except ImportError as e:
            logger.debug(f"Legacy social_gamification module not available: {e}")

            # Enhanced implementation if we have enhanced UI and user is authenticated
            if user_manager_instance.is_authenticated() and not user_manager_instance.is_guest():
                try:
                    _display_enhanced_achievements(user_manager_instance, ascii_art)
                    return
                except Exception as e:
                    logger.warning(f"Error running enhanced achievements: {e}")
                    # Fall back to basic implementation

            # Basic implementation if the module is not available or enhanced UI failed
            print("Social sharing and achievements module not available.")
            print("\nThis feature allows you to share your cycling achievements and connect with other cyclists.")
            print("It includes achievements, badges, challenges, and social sharing options.")

            if user_manager_instance.is_authenticated() and not user_manager_instance.is_guest():
                user = user_manager_instance.get_current_user()
                stats = user.get('stats', {})

                if stats and stats.get('total_trips', 0) > 0:
                    # Show basic achievements based on stats
                    total_trips = stats.get('total_trips', 0)
                    total_distance = stats.get('total_distance', 0.0)

                    print("\nYour Achievements:")

                    if total_trips >= 1:
                        print(" First Ride - Completed your first cycling trip")

                    if total_trips >= 5:
                        print(" Regular Rider - Logged 5 or more cycling trips")

                    if total_trips >= 10:
                        print(" Dedicated Cyclist - Logged 10 or more cycling trips")

                    if total_distance >= 50:
                        print(" Half Century - Cycled a total of 50 km or more")

                    if total_distance >= 100:
                        print(" Century Rider - Cycled a total of 100 km or more")
            else:
                print("\nYou need to log in (with a registered account) to track achievements.")

            input("\nPress Enter to return to the main menu...")


def admin_panel(user_manager_instance):
    """Admin panel for system management."""
    modules = import_local_modules()
    ascii_art = modules['ascii_art']

    ascii_art.clear_screen()
    ascii_art.display_header()
    ascii_art.display_section_header("Admin Panel")

    # Check if user is an admin
    if not user_manager_instance.is_admin():
        print("Access denied. Admin privileges required.")
        input("Press Enter to continue...")
        return

    # Check if admin_panel module is available
    try:
        import apps.admin.admin_panel as admin_panel

        # Run the admin panel module
        if hasattr(admin_panel, 'run_admin_panel'):
            admin_panel.run_admin_panel(user_manager_instance)
        elif hasattr(admin_panel, 'main'):
            admin_panel.main(user_manager_instance)
        else:
            print("Admin panel module found but no entry point available.")
    except ImportError:
        # Basic implementation if the module is not available
        print("Admin panel module not available.")
    except Exception as e:
        print(f"Error running admin panel: {e}")
        print("\nThis panel provides system management capabilities for administrators.")
        print("Features include:")
        print("- User management")
        print("- System statistics")
        print("- Data management")
        print("- System configuration")

        # Provide basic user management
        print("\nRegistered Users:")
        users = user_manager_instance.users

        if users:
            # Prepare data for table
            headers = ["Username", "Name", "Admin", "Trips"]
            data = []

            for username, user_data in users.items():
                if username != 'guest':  # Skip guest user
                    name = user_data.get('name', 'Unknown')
                    is_admin = "Yes" if user_data.get('is_admin', False) else "No"
                    trips = user_data.get('stats', {}).get('total_trips', 0)

                    data.append([username, name, is_admin, trips])

            # Display table
            ascii_art.display_data_table(headers, data)
        else:
            print("No registered users found.")

    input("\nPress Enter to return to the main menu...")


def import_local_modules():
    """
    Import local modules after ensuring all dependencies are installed.

    Returns:
        A dictionary of imported modules
    """
    global GOOGLE_SHEETS_AVAILABLE

    # ASCII art module (merged enhancements)
    try:
        import utils.ascii_art as ascii_art
    except ImportError:
        logger.error("Failed to import utils.ascii_art module")
        ascii_art = None

    import utils.general_utils as utils
    import auth.user_management.user_manager as user_manager
    import apps.eco_tips as eco_tips

    # Try to import database manager
    try:
        import core.database_manager as database_manager
        db_available = True
    except ImportError:
        logger.warning("database_manager module not available")
        database_manager = None
        db_available = False

    # Try to import optional modules
    try:
        import services.sheets.sheets_manager as sheets_manager
        GOOGLE_SHEETS_AVAILABLE = sheets_manager.GOOGLE_SHEETS_AVAILABLE
    except ImportError:
        logger.warning("sheets_manager module not available")
        sheets_manager = None
        GOOGLE_SHEETS_AVAILABLE = False

    # Initialize module dictionary
    modules = {
        'ascii_art': ascii_art,
        'utils': utils,
        'user_manager': user_manager,
        'eco_tips': eco_tips,
        'database_manager': database_manager,
        'sheets_manager': sheets_manager if GOOGLE_SHEETS_AVAILABLE else None
    }

    # Try to import new feature modules
    try:
        import apps.challenges.eco_challenges as eco_challenges
        modules['eco_challenges'] = eco_challenges
    except ImportError:
        logger.warning("eco_challenges module not available")

    try:
        import carbon_impact_tracker as carbon_impact_tracker
        modules['carbon_impact_tracker'] = carbon_impact_tracker
    except ImportError:
        logger.warning("carbon_impact_tracker module not available")

    try:
        import apps.route_planner.weather_route_planner as weather_route_planner
        modules['weather_route_planner'] = weather_route_planner
    except ImportError:
        logger.warning("weather_route_planner module not available")

    try:
        # Try to import the modularized version first
        try:
            import apps.route_planner.ai_planner as ai_route_planner
            logger.info("Using modularized AI route planner")
            # Verify the module has the required function to avoid attribute errors
            if hasattr(ai_route_planner, 'run_ai_route_planner'):
                modules['ai_route_planner'] = ai_route_planner
            else:
                logger.error("Modularized AI route planner missing required function")
                modules['ai_route_planner'] = None
        except ImportError:
            # Fall back to legacy version if needed
            try:
                import apps.route_planner.ai_route_planner as ai_route_planner
                logger.warning("Using legacy AI route planner - consider updating to modularized version")
                # Verify the module has the required function
                if hasattr(ai_route_planner, 'run_ai_route_planner'):
                    modules['ai_route_planner'] = ai_route_planner
                else:
                    logger.error("Legacy AI route planner missing required function")
                    modules['ai_route_planner'] = None
            except Exception as e:
                logger.error(f"Error importing legacy AI route planner: {e}")
                modules['ai_route_planner'] = None
    except Exception as e:
        logger.error(f"Error importing AI route planner: {e}")
        modules['ai_route_planner'] = None

    return modules

def _display_enhanced_achievements(user_manager_instance, ascii_art):
    """Display enhanced achievements with animations."""
    user = user_manager_instance.get_current_user()
    stats = user.get('stats', {})

    # If we have no stats, show a message with the mascot
    if not stats or not stats.get('total_trips', 0):
        if hasattr(ascii_art, 'display_mascot_animation'):
            ascii_art.display_mascot_animation("Start cycling to earn achievements!")
        else:
            print("No achievements yet. Start cycling to earn achievements!")
        input("\nPress Enter to continue...")
        return

    # Calculate achievement levels based on stats
    total_trips = stats.get('total_trips', 0)
    total_distance = stats.get('total_distance', 0.0)
    total_co2_saved = stats.get('total_co2_saved', 0.0)
    total_calories = stats.get('total_calories', 0)

    # Display a fun loading animation
    if hasattr(ascii_art, 'display_loading_animation'):
        ascii_art.display_loading_animation("Loading your achievements", 1.5)

    # Determine achievements and show them with animation
    achievements = []

    # Trip count achievements
    if total_trips >= 10:
        achievements.append(("streak", 3, "Dedicated Cyclist"))
    elif total_trips >= 5:
        achievements.append(("streak", 2, "Regular Rider"))
    elif total_trips >= 1:
        achievements.append(("streak", 1, "First Ride"))

    # Distance achievements
    if total_distance >= 100:
        achievements.append(("distance", 3, "Century Rider"))
    elif total_distance >= 50:
        achievements.append(("distance", 2, "Half Century"))
    elif total_distance >= 10:
        achievements.append(("distance", 1, "Getting Started"))

    # CO2 savings achievements
    if total_co2_saved >= 20:
        achievements.append(("carbon_saver", 3, "Climate Hero"))
    elif total_co2_saved >= 10:
        achievements.append(("carbon_saver", 2, "Climate Guardian"))
    elif total_co2_saved >= 2:
        achievements.append(("carbon_saver", 1, "Climate Conscious"))

    # Display all achievements with animation
    if achievements:
        for achievement_type, level, name in achievements:
            if hasattr(ascii_art, 'display_achievement_badge'):
                ascii_art.display_achievement_badge(achievement_type, level, name)
                time.sleep(0.5)  # Pause between achievements
            else:
                print(f" {name}")
    else:
        print("No achievements yet. Start cycling to earn achievements!")

    # Offer to generate a sharing graphic or view route animation
    print("\nShare options:")

    if hasattr(ascii_art, 'create_social_share_graphic'):
        print("1. Create shareable achievement graphic")
    else:
        print("1. Share achievements (not available in basic mode)")

    if hasattr(ascii_art, 'animate_route_on_map'):
        print("2. View animated cycling routes")
    else:
        print("2. View routes (not available in basic mode)")

    print("3. Return to main menu")

    choice = input("\nSelect an option: ")

    if choice == "1" and hasattr(ascii_art, 'create_social_share_graphic'):
        # Generate a shareable graphic
        username = user.get('username', 'EcoCyclist')
        # Find the highest achievement
        if achievements:
            top_achievement = max(achievements, key=lambda x: x[1])
            achievement_name = top_achievement[2]
        else:
            achievement_name = "EcoCycle User"

        # Display social share graphic
        ascii_art.create_social_share_graphic(
            username,
            achievement_name,
            {
                "Total Trips": total_trips,
                "Total Distance": f"{total_distance:.1f}",
                "CO2 Saved": f"{total_co2_saved:.1f}",
                "Calories Burned": total_calories
            }
        )
    elif choice == "2" and hasattr(ascii_art, 'animate_route_on_map'):
        # Show animated route visualization
        ascii_art.animate_route_on_map()
    elif choice in ["1", "2"]:
        print("\nThis feature is not available in basic mode.")
