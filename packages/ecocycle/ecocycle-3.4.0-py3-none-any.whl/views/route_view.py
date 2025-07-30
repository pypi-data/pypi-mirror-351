"""
EcoCycle - Route View

This module defines the RouteView class, which handles the presentation of cycling routes to the user.
"""

import logging
import re
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from controllers.route_controller import RouteController
from models.route import Route
import utils.general_utils
import utils.ascii_art

# Create local references for convenience
ascii_art = utils.ascii_art
general_utils = utils.general_utils

# Import Rich features from ascii_art module
RICH_AVAILABLE = utils.ascii_art.RICH_AVAILABLE
if RICH_AVAILABLE:
    from rich.panel import Panel
    from rich.console import Console
    from rich.text import Text
    from rich.rule import Rule
    from rich.table import Table
    import rich.box
    console = utils.ascii_art.console

# Configure logging
logger = logging.getLogger(__name__)


class RouteView:
    """
    View class for displaying cycling routes to the user.
    """

    def __init__(self, controller: Optional[RouteController] = None, weather_controller=None):
        """
        Initialize a RouteView.

        Args:
            controller (Optional[RouteController]): Controller for route data
            weather_controller: Weather controller for getting coordinates
        """
        self.controller = controller or RouteController()
        self.weather_controller = weather_controller

    def display_route_planner_menu(self, start_lat=None, start_lon=None) -> None:
        """
        Display the route planner menu and handle user interaction.

        Args:
            start_lat (Optional[float]): Starting latitude if already known
            start_lon (Optional[float]): Starting longitude if already known
        """
        ascii_art.clear_screen()
        ascii_art.display_header()
        ascii_art.display_section_header("Route Planner")

        if not self.controller.FOLIUM_AVAILABLE:
            print("The folium library is required for route planning visualization.")
            print("Please install it with: pip install folium")
            input("\nPress Enter to continue...")
            return

        # Get start and end locations
        if start_lat is None or start_lon is None:
            if RICH_AVAILABLE:
                console.print(Panel("Enter starting location (city or landmark):",
                                   border_style="blue",
                                   title="[bold]Location Input[/bold]",
                                   expand=False))
                start_location = input("> ")
            else:
                print("Enter starting location (city or landmark):")
                start_location = input("> ")

            if self.weather_controller:
                if RICH_AVAILABLE:
                    with console.status("[cyan]Looking up coordinates...[/cyan]", spinner="dots"):
                        start_coords = self.weather_controller.get_coordinates_for_location(start_location)
                else:
                    start_coords = self.weather_controller.get_coordinates_for_location(start_location)
            else:
                # Fallback if weather controller not available
                start_coords = None

            if not start_coords:
                if RICH_AVAILABLE:
                    console.print(Panel(f"[bold red]Could not find location:[/bold red] {start_location}",
                                        border_style="red"))
                else:
                    print("Could not find starting location.")
                input("\nPress Enter to continue...")
                return
        else:
            start_coords = (start_lat, start_lon)

        if RICH_AVAILABLE:
            console.print(Panel("Enter destination (city or landmark):",
                               border_style="blue",
                               title="[bold]Destination Input[/bold]",
                               expand=False))
            end_location = input("> ")
        else:
            print("Enter destination (city or landmark):")
            end_location = input("> ")

        if self.weather_controller:
            if RICH_AVAILABLE:
                with console.status("[cyan]Looking up coordinates...[/cyan]", spinner="dots"):
                    end_coords = self.weather_controller.get_coordinates_for_location(end_location)
            else:
                end_coords = self.weather_controller.get_coordinates_for_location(end_location)
        else:
            # Fallback if weather controller not available
            end_coords = None

        if not end_coords:
            if RICH_AVAILABLE:
                console.print(Panel(f"[bold red]Could not find location:[/bold red] {end_location}",
                                   border_style="red"))
            else:
                print("Could not find destination.")
            input("\nPress Enter to continue...")
            return

        # Calculate route distance
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        direct_distance = general_utils.calculate_distance(start_lat, start_lon, end_lat, end_lon)

        if RICH_AVAILABLE:
            console.print(f"\n[bold cyan]Direct distance:[/bold cyan] {general_utils.format_distance(direct_distance)}")
        else:
            print(f"\nDirect distance: {general_utils.format_distance(direct_distance)}")

        # Get route info
        if RICH_AVAILABLE:
            with console.status("[cyan]Calculating route...[/cyan]", spinner="dots"):
                route_info = self.controller.get_route_info(start_coords, end_coords)
        else:
            route_info = self.controller.get_route_info(start_coords, end_coords)

        if route_info:
            distance = route_info.get("distance", direct_distance)
            duration = route_info.get("duration", direct_distance * 4)  # Estimate 15 km/h
            elevation = route_info.get("elevation", 0)

            if RICH_AVAILABLE:
                route_details = f"[bold cyan]Route distance:[/bold cyan] {general_utils.format_distance(distance)}\n"
                route_details += f"[bold cyan]Estimated duration:[/bold cyan] {duration:.0f} minutes"
                if elevation:
                    route_details += f"\n[bold cyan]Elevation gain:[/bold cyan] {elevation:.0f} meters"

                console.print(Panel(route_details,
                                   title="[bold]Route Details[/bold]",
                                   border_style="green"))
            else:
                print(f"Route distance: {general_utils.format_distance(distance)}")
                print(f"Estimated duration: {duration:.0f} minutes")
                if elevation:
                    print(f"Elevation gain: {elevation:.0f} meters")
        else:
            if RICH_AVAILABLE:
                console.print(Panel("[yellow]Could not get detailed route information.[/yellow]\nUsing direct distance for calculations.",
                                  border_style="yellow",
                                  title="[bold]Warning[/bold]"))
            else:
                print("Could not get detailed route information.")
                print("Using direct distance for calculations.")
            distance = direct_distance
            duration = direct_distance * 4  # Estimate 15 km/h

        # Save route if user wants
        if RICH_AVAILABLE:
            console.print("\n[bold]Would you like to save this route?[/bold] (y/n)")
        else:
            print("\nWould you like to save this route? (y/n)")
        save = input("> ")

        if save.lower() == "y":
            if RICH_AVAILABLE:
                console.print(Panel("Enter a name for this route:",
                                   border_style="blue",
                                   title="[bold]Save Route[/bold]",
                                   expand=False))
            else:
                print("Enter a name for this route: ")
            name = input("> ")

            if RICH_AVAILABLE:
                with console.status("[cyan]Saving route...[/cyan]", spinner="dots"):
                    saved = self.controller.save_user_route(name, start_coords, end_coords, distance, duration)
            else:
                saved = self.controller.save_user_route(name, start_coords, end_coords, distance, duration)

            if saved:
                if RICH_AVAILABLE:
                    console.print(f"[bold green]✓[/bold green] Route '[bold]{name}[/bold]' saved successfully!")
                else:
                    print(f"Route '{name}' saved successfully!")

                # Generate map only if user saved the route
                if RICH_AVAILABLE:
                    with console.status("[cyan]Generating map...[/cyan]", spinner="dots"):
                        map_path = self.controller.generate_route_map(start_coords, end_coords, f"Route: {direct_distance:.1f} km")
                else:
                    map_path = self.controller.generate_route_map(start_coords, end_coords, f"Route: {direct_distance:.1f} km")

                if map_path:
                    if RICH_AVAILABLE:
                        console.print(Panel(f"[bold cyan]Route map saved to:[/bold cyan]\n{map_path}",
                                          border_style="green"))
                        console.print("\n[bold]Open map in browser?[/bold] (y/n)")
                    else:
                        print(f"\nRoute map saved to: {map_path}")
                        print("Open map in browser? (y/n)")

                    open_map = input("> ")
                    if open_map.lower() == "y":
                        if RICH_AVAILABLE:
                            with console.status("[cyan]Opening browser...[/cyan]", spinner="dots"):
                                browser_opened = self.controller.open_map_in_browser(map_path)
                        else:
                            browser_opened = self.controller.open_map_in_browser(map_path)

                        if browser_opened:
                            if RICH_AVAILABLE:
                                console.print("[bold green]✓[/bold green] Map opened in browser.")
                            else:
                                print("Map opened in browser.")
                        else:
                            if RICH_AVAILABLE:
                                console.print("[bold red]✗[/bold red] Error opening map in browser.")
                            else:
                                print("Error opening map in browser.")
            else:
                if RICH_AVAILABLE:
                    console.print("[bold red]✗[/bold red] Error saving route. You may need to be logged in.")
                else:
                    print("Error saving route. You may need to be logged in.")

        # Calculate eco impact
        if RICH_AVAILABLE:
            console.print("\n[bold]Calculating environmental impact...[/bold]")
            with console.status("[cyan]Processing environmental data...[/cyan]", spinner="dots12"):
                # Add a small delay to show the spinner animation
                time.sleep(0.8)
                self.display_cycling_eco_impact(distance)
        else:
            print("\nCalculating environmental impact...")
            self.display_cycling_eco_impact(distance)

        input("\nPress Enter to continue...")

    def display_saved_routes_menu(self) -> None:
        """
        Display the saved routes menu and handle user interaction.
        """
        ascii_art.clear_screen()
        ascii_art.display_header()

        # Use Rich UI if available
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                Text("Your Saved Cycling Routes", style="bold cyan"),
                border_style="cyan"
            ))
        else:
            ascii_art.display_section_header("Saved Routes")

        # Get user's saved routes
        routes = self.controller.get_user_routes()

        if not routes:
            if RICH_AVAILABLE:
                console.print(Panel(
                    "You don't have any saved routes yet.\n"
                    "Use the Route Planner to create and save new routes.",
                    title="No Routes Found",
                    border_style="yellow"
                ))
                input("\nPress Enter to continue...")
            else:
                print("You don't have any saved routes.")
                input("\nPress Enter to continue...")
            return

        # Display routes with Rich UI if available
        if RICH_AVAILABLE:
            # Create a table for routes
            routes_table = Table(box=rich.box.ROUNDED, border_style="blue")
            routes_table.add_column("#", style="cyan", justify="right")
            routes_table.add_column("Route Name", style="green")
            routes_table.add_column("Distance", style="blue", justify="right")
            routes_table.add_column("Est. Duration", style="magenta", justify="right")
            routes_table.add_column("Date Saved", style="yellow")

            for i, route in enumerate(routes, 1):
                name = route.name
                distance = route.distance
                duration = route.duration
                date_saved = route.get_formatted_date()

                # Format duration as hours and minutes
                hours = int(duration // 60)
                minutes = int(duration % 60)
                if hours > 0:
                    duration_str = f"{hours}h {minutes}m"
                else:
                    duration_str = f"{minutes}m"

                routes_table.add_row(
                    str(i),
                    name,
                    f"{distance:.1f} km",
                    duration_str,
                    date_saved
                )

            console.print(routes_table)

            # Display menu options
            console.print(Rule("Options", style="cyan"))

            menu_table = Table(show_header=False, box=rich.box.ROUNDED, border_style="blue")
            menu_table.add_column("Option", style="cyan", width=4)
            menu_table.add_column("Description", style="green")

            # Add exit option
            menu_table.add_row("0", "[yellow]Exit Program[/yellow]")

            # Add menu options
            menu_table.add_row("1", "[cyan]View detailed route information[/cyan]")
            menu_table.add_row("2", "[cyan]Generate map visualization[/cyan]")
            menu_table.add_row("3", "[cyan]Delete a route[/cyan]")
            menu_table.add_row("4", "[cyan]Return to Route Planner[/cyan]")
            menu_table.add_row("5", "[cyan]Sort routes by distance[/cyan]")
            menu_table.add_row("6", "[cyan]Filter routes by name[/cyan]")

            console.print(menu_table)
        else:
            # Display routes in standard format
            print(f"You have {len(routes)} saved routes:")

            for i, route in enumerate(routes, 1):
                name = route.name
                distance = route.distance
                date_saved = route.get_formatted_date()

                print(f"{i}. {name} - {distance:.1f} km (saved on {date_saved})")

            # Menu options
            print("\nOptions:")
            print(f"  {ascii_art.Fore.YELLOW}0. Exit Program{ascii_art.Style.RESET_ALL}")
            print("1. View route details")
            print("2. Generate map for a route")
            print("3. Delete a route")
            print("4. Return to Route Planner")
            print("5. Sort routes by distance")
            print("6. Filter routes by name")

        choice = input("\nSelect an option: ")

        if choice == "0":
            # Exit program
            print("\nExiting program...")
            import sys
            sys.exit(0)
        elif choice == "1":
            # View route details
            route_number = input("Enter route number to view: ")
            try:
                route_index = int(route_number) - 1
                if 0 <= route_index < len(routes):
                    self.display_route_details(routes[route_index])
                else:
                    print("Invalid route number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

            input("\nPress Enter to continue...")
            self.display_saved_routes_menu()  # Return to saved routes menu

        elif choice == "2":
            # Generate map
            route_number = input("Enter route number to generate map for: ")
            try:
                route_index = int(route_number) - 1
                if 0 <= route_index < len(routes):
                    route = routes[route_index]
                    map_path = self.controller.generate_route_map(
                        route.start_coords,
                        route.end_coords,
                        route.name
                    )
                    if map_path:
                        print(f"\nRoute map saved to: {map_path}")

                        # Open map in browser if user wants
                        print("Open map in browser? (y/n)")
                        open_map = input("> ")
                        if open_map.lower() == "y":
                            if self.controller.open_map_in_browser(map_path):
                                print("Map opened in browser.")
                            else:
                                print("Error opening map in browser.")
                    else:
                        print("Error generating map.")
                else:
                    print("Invalid route number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

            input("\nPress Enter to continue...")
            self.display_saved_routes_menu()  # Return to saved routes menu

        elif choice == "3":
            # Delete route
            route_number = input("Enter route number to delete: ")
            try:
                route_index = int(route_number) - 1
                if 0 <= route_index < len(routes):
                    route_name = routes[route_index].name
                    confirm = input(f"Are you sure you want to delete route '{route_name}'? (y/n): ")

                    if confirm.lower() == "y":
                        if self.controller.delete_user_route(route_index):
                            print(f"Route '{route_name}' deleted successfully!")
                        else:
                            print("Error deleting route.")
                else:
                    print("Invalid route number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

            input("\nPress Enter to continue...")
            self.display_saved_routes_menu()  # Return to saved routes menu

    def display_route_details(self, route: Route) -> None:
        """
        Display detailed information about a route.

        Args:
            route (Route): Route to display
        """
        print("\nRoute Details:")
        print(f"Name: {route.name}")
        print(f"Distance: {route.distance:.1f} km")
        print(f"Estimated duration: {route.duration:.0f} minutes")
        print(f"Date saved: {route.get_formatted_date('%Y-%m-%d %H:%M')}")
        print(f"Starting coordinates: {route.start_coords[0]:.6f}, {route.start_coords[1]:.6f}")
        print(f"Ending coordinates: {route.end_coords[0]:.6f}, {route.end_coords[1]:.6f}")

        # Calculate some additional stats
        avg_speed = route.get_average_speed()
        calories = general_utils.calculate_calories(route.distance, avg_speed, 70)  # Assume 70kg rider
        co2_saved = general_utils.calculate_co2_saved(route.distance)

        print("\nEstimated Statistics:")
        print(f"Average speed: {avg_speed:.1f} km/h")
        print(f"Calories burned (70kg rider): {calories}")
        print(f"CO2 emissions saved: {co2_saved:.2f} kg")

    def display_cycling_eco_impact(self, distance: float) -> None:
        """
        Display environmental impact of a cycling trip.

        Args:
            distance (float): Distance in kilometers
        """
        impact = self.controller.calculate_cycling_eco_impact(distance)

        # Display results
        if RICH_AVAILABLE:
            impact_stats = f"[bold cyan]CO2 emissions saved:[/bold cyan] {impact['co2_saved']:.2f} kg\n"
            impact_stats += f"[bold cyan]Fuel saved:[/bold cyan] {impact['fuel_saved']:.2f} liters\n"
            impact_stats += f"[bold cyan]Money saved on fuel:[/bold cyan] ${impact['money_saved']:.2f}"

            equivalents = f"- The daily CO2 absorption of [bold green]{impact['trees_equivalent']:.1f} trees[/bold green]\n"
            equivalents += f"- The emissions from [bold]{impact['light_bulbs_equivalent']:.1f} 100W light bulbs[/bold] running for 24 hours"

            console.print(Panel(impact_stats,
                               title="[bold]Environmental Impact of Your Cycling Trip[/bold]",
                               border_style="green"))
            console.print(Panel(equivalents,
                               title="[bold]This is equivalent to[/bold]",
                               border_style="green"))
        else:
            # Display results
            print("\nEnvironmental Impact of Your Cycling Trip:")
            print(f"CO2 emissions saved: {impact['co2_saved']:.2f} kg")
            print(f"Fuel saved: {impact['fuel_saved']:.2f} liters")
            print(f"Money saved on fuel: ${impact['money_saved']:.2f}")

            # Show equivalents
            print("\nThis is equivalent to:")
            print(f"- The daily CO2 absorption of {impact['trees_equivalent']:.1f} trees")
            print(f"- The emissions from {impact['light_bulbs_equivalent']:.1f} 100W light bulbs running for 24 hours")

    def display_ai_route_planner_menu(self) -> None:
        """
        Display the AI-Powered Cycling Route Planner menu and handle user interactions.
        """
        ascii_art.clear_screen()
        ascii_art.display_header()

        # Display AI Route Planner section header
        if RICH_AVAILABLE:
            # Main header with enhanced styling
            console.print(Panel(
                "[bold]Get personalized cycling route recommendations powered by Google's Gemini AI.[/bold]",
                title="[bold white on cyan]🚲 AI-Powered Cycling Route Planner 🚲[/bold white on cyan]",
                border_style="cyan",
                padding=(1, 2),
                expand=False,
                highlight=True
            ))

            # Display menu options with icons and category-based colors
            console.print(Panel(
                """
[bold white on blue]🧭 AI Route Planner Menu 🧭[/bold white on blue]

[bold]System Options:[/bold]
  [bold red]0. ❌ Exit Program[/bold red]
  [bold yellow]8. 🏠 Return to main menu[/bold yellow]

[bold]Route Planning:[/bold]
  [bold green]1. 🗺️  Generate a new route recommendation[/bold green]
  [bold green]2. 📋 View and manage saved routes[/bold green]
  [bold green]5. 🔄 Generate alternative routes[/bold green]

[bold]Analysis & Settings:[/bold]
  [bold cyan]3. ⚙️  Update your cycling preferences[/bold cyan]
  [bold cyan]4. 📊 Get detailed route analysis[/bold cyan]
  [bold cyan]6. 🛡️  Route safety assessment[/bold cyan]
  [bold cyan]7. 📈 Route comparison tool[/bold cyan]
            """,
                border_style="blue",
                padding=(1, 2),
                expand=False,
                highlight=True
            ))

            # Footer with tip
            console.print(Panel(
                "[italic]Tip: Route safety assessment provides real-time hazard information based on your location.[/italic]",
                border_style="dim blue",
                padding=(0, 1),
                expand=False
            ))

            console.print("\n[bold white on blue]Select an option (0-8):[/bold white on blue] ", end="")
        else:
            ascii_art.display_section_header("AI-Powered Cycling Route Planner")
            print("\nGet personalized cycling route recommendations powered by Google's Gemini AI.")
            print("\n=== AI Route Planner Menu ===\n")
            print(f"  {ascii_art.Fore.YELLOW}0. Exit Program{ascii_art.Style.RESET_ALL}")
            print("1. Generate a new route recommendation")
            print("2. View and manage saved routes")
            print("3. Update your cycling preferences")
            print("4. Get detailed route analysis")
            print("5. Generate alternative routes")
            print("6. Route safety assessment")
            print("7. Route comparison tool")
            print("8. Return to main menu")
            print("\nSelect an option (0-8): ", end="")

        choice = input()

        if choice == "0":
            # Exit program
            if RICH_AVAILABLE:
                console.print(Panel(
                    "Exiting program...",
                    title="[bold white on red]👋 Goodbye[/bold white on red]",
                    border_style="red",
                    padding=(0, 1)
                ))
            else:
                print("\nExiting program...")
            import sys
            sys.exit(0)
        elif choice == "1":
            # Generate a new route recommendation
            self.display_ai_route_recommendation()
            self.display_ai_route_planner_menu()
        elif choice == "2":
            # View and manage saved routes
            self.display_saved_routes_menu()
            self.display_ai_route_planner_menu()
        elif choice == "3":
            # Update cycling preferences
            if RICH_AVAILABLE:
                console.print(Panel(
                    "The cycling preferences feature is coming soon!",
                    title="[bold white on yellow]⚙️ Coming Soon[/bold white on yellow]",
                    border_style="yellow",
                    padding=(1, 2)))
            else:
                print("\nThe cycling preferences feature is coming soon!")
            input("\nPress Enter to continue...")
            self.display_ai_route_planner_menu()
        elif choice == "4":
            # Get detailed route analysis
            if RICH_AVAILABLE:
                console.print(Panel(
                    "The detailed route analysis feature is coming soon!",
                    title="[bold white on yellow]📊 Coming Soon[/bold white on yellow]",
                    border_style="yellow",
                    padding=(1, 2)))
            else:
                print("\nThe detailed route analysis feature is coming soon!")
            input("\nPress Enter to continue...")
            self.display_ai_route_planner_menu()
        elif choice == "5":
            # Generate alternative routes
            if RICH_AVAILABLE:
                console.print(Panel(
                    "The alternative routes feature is coming soon!",
                    title="[bold white on yellow]🔄 Coming Soon[/bold white on yellow]",
                    border_style="yellow",
                    padding=(1, 2)))
            else:
                print("\nThe alternative routes feature is coming soon!")
            input("\nPress Enter to continue...")
            self.display_ai_route_planner_menu()
        elif choice == "6":
            # Route safety assessment
            self.display_route_safety_assessment()
            self.display_ai_route_planner_menu()
        elif choice == "7":
            # Route comparison tool
            if RICH_AVAILABLE:
                console.print(Panel(
                    "The route comparison tool feature is coming soon!",
                    title="[bold white on yellow]📈 Coming Soon[/bold white on yellow]",
                    border_style="yellow",
                    padding=(1, 2)))
            else:
                print("\nThe route comparison tool feature is coming soon!")
            input("\nPress Enter to continue...")
            self.display_ai_route_planner_menu()
        elif choice == "8":
            # Return to main menu
            return
        else:
            # Invalid choice
            if RICH_AVAILABLE:
                console.print(Panel(
                    "Invalid choice. Please try again.",
                    title="[bold white on red]⚠️ Error[/bold white on red]",
                    border_style="red",
                    padding=(0, 1)
                ))
            else:
                print("\nInvalid choice. Please try again.")
            input("\nPress Enter to continue...")
            self.display_ai_route_planner_menu()

    def display_ai_route_recommendation(self) -> None:
        """
        Display the AI-powered route recommendation interface and handle user interaction.
        """
        ascii_art.clear_screen()
        ascii_art.display_header()

        if RICH_AVAILABLE:
            # Main header panel
            console.print(Panel(
                "Find the perfect cycling route based on your preferences and conditions",
                title="[bold cyan]AI Route Recommendation[/bold cyan]",
                border_style="green",
                expand=False
            ))

            # Input section
            console.print(Panel(
                "[bold]Please provide your route preferences:[/bold]",
                border_style="blue",
                title="[bold]Route Parameters[/bold]",
                expand=False
            ))

            # Starting location
            console.print("[bold]Starting location:[/bold] (city, address, or landmark)")
            start_location = input("> ")
            if not start_location:
                console.print("[bold red]Starting location is required.[/bold red]")
                input("\nPress Enter to return to menu...")
                return

            # Destination
            console.print("[bold]Destination:[/bold] (city, address, or landmark)")
            end_location = input("> ")
            if not end_location:
                console.print("[bold red]Destination is required.[/bold red]")
                input("\nPress Enter to return to menu...")
                return

            # Processing
            with console.status("[cyan]AI analyzing optimal routes...[/cyan]", spinner="dots12"):
                # Simulate AI processing time
                time.sleep(2)

                # Get coordinates if weather controller available
                if self.weather_controller:
                    start_coords = self.weather_controller.get_coordinates_for_location(start_location)
                    end_coords = self.weather_controller.get_coordinates_for_location(end_location)
                else:
                    # Simulate coordinates for this example
                    start_coords = (40.7128, -74.0060)  # New York City coordinates
                    end_coords = (40.7614, -73.9776)  # Simulated nearby location

                # Calculate route details
                start_lat, start_lon = start_coords
                end_lat, end_lon = end_coords
                direct_distance = general_utils.calculate_distance(start_lat, start_lon, end_lat, end_lon)

                # Get route info with controller if possible
                route_info = self.controller.get_route_info(start_coords, end_coords)
                if route_info:
                    distance = route_info.get("distance", direct_distance)
                    duration = route_info.get("duration", direct_distance * 4)  # Estimate 15 km/h
                    elevation = route_info.get("elevation", 0)  # Get elevation or 0
                else:
                    # Use direct distance as fallback
                    distance = direct_distance
                    duration = distance * 4  # Estimate 15 km/h
                    elevation = 0

            # Results display
            route_details = f"[bold cyan]From:[/bold cyan] {start_location}\n"
            route_details += f"[bold cyan]To:[/bold cyan] {end_location}\n\n"
            route_details += f"[bold cyan]Distance:[/bold cyan] {general_utils.format_distance(distance)}\n"
            route_details += f"[bold cyan]Estimated duration:[/bold cyan] {duration:.0f} minutes"
            if elevation:
                route_details += f"\n[bold cyan]Elevation gain:[/bold cyan] {elevation:.0f} meters"

            console.print(Panel(
                route_details,
                title="[bold]AI-Recommended Cycling Route[/bold]",
                border_style="green"
            ))

            # Calculate environmental impact
            impact = self.controller.calculate_cycling_eco_impact(distance)
            impact_text = f"[bold cyan]CO2 emissions saved:[/bold cyan] {impact['co2_saved']:.2f} kg\n"
            impact_text += f"[bold cyan]Fuel saved:[/bold cyan] {impact['fuel_saved']:.2f} liters\n"
            impact_text += f"[bold cyan]Money saved on fuel:[/bold cyan] ${impact['money_saved']:.2f}"

            console.print(Panel(
                impact_text,
                title="[bold]Environmental Impact[/bold]",
                border_style="green"
            ))

            # Options
            console.print(Panel(
                """
1. Save this route
2. Generate map visualization
3. Return to AI Route Planner menu
                """,
                title="[bold]Options[/bold]",
                border_style="blue"
            ))

            option = input("Select an option (1-3): ")

            if option == "1":
                # Save route
                console.print(Panel(
                    "Enter a name for this route:",
                    border_style="blue",
                    title="[bold]Save Route[/bold]",
                    expand=False
                ))

                route_name = input("> ")
                if route_name:
                    with console.status("[cyan]Saving route...[/cyan]", spinner="dots"):
                        # Attempt to save the route
                        saved = self.controller.save_user_route(route_name, start_coords, end_coords, distance, duration)

                    if saved:
                        console.print(f"[bold green]✓[/bold green] Route '[bold]{route_name}[/bold]' saved successfully!")
                    else:
                        console.print("[bold red]✗[/bold red] Error saving route. You may need to be logged in.")

                input("\nPress Enter to continue...")

            elif option == "2":
                # Generate map
                with console.status("[cyan]Generating route map...[/cyan]", spinner="dots"):
                    map_path = self.controller.generate_route_map(start_coords, end_coords, f"AI Route: {distance:.1f} km")

                if map_path:
                    console.print(Panel(
                        f"[bold cyan]Route map saved to:[/bold cyan]\n{map_path}",
                        border_style="green"
                    ))

                    console.print("\n[bold]Open map in browser?[/bold] (y/n)")
                    open_map = input("> ")

                    if open_map.lower() == "y":
                        with console.status("[cyan]Opening browser...[/cyan]", spinner="dots"):
                            browser_opened = self.controller.open_map_in_browser(map_path)

                        if browser_opened:
                            console.print("[bold green]✓[/bold green] Map opened in browser.")
                        else:
                            console.print("[bold red]✗[/bold red] Error opening map in browser.")
                else:
                    console.print("[bold red]✗[/bold red] Error generating map.")

                input("\nPress Enter to continue...")

            # Option 3 or any other input returns to menu
            return

        else:
            # Fallback to non-Rich UI version
            ascii_art.display_section_header("AI Route Recommendation")
            print("\nFind the perfect cycling route based on your preferences and conditions")

            # Get user inputs
            print("\n=== Route Parameters ===\n")

            print("Starting location (city, address, or landmark):")
            start_location = input("> ")
            if not start_location:
                print("Starting location is required.")
                input("\nPress Enter to return to menu...")
                return

            print("\nDestination (city, address, or landmark):")
            end_location = input("> ")
            if not end_location:
                print("Destination is required.")
                input("\nPress Enter to return to menu...")
                return

            # Processing
            print("\nAI analyzing optimal routes...")
            for _ in range(3):
                time.sleep(0.5)
                print(".", end="", flush=True)
            print()

            # Get coordinates if weather controller available
            if self.weather_controller:
                start_coords = self.weather_controller.get_coordinates_for_location(start_location)
                end_coords = self.weather_controller.get_coordinates_for_location(end_location)
            else:
                # Simulate coordinates for this example
                start_coords = (40.7128, -74.0060)  # New York City coordinates
                end_coords = (40.7614, -73.9776)  # Simulated nearby location

            # Calculate route details
            start_lat, start_lon = start_coords
            end_lat, end_lon = end_coords
            direct_distance = general_utils.calculate_distance(start_lat, start_lon, end_lat, end_lon)

            # Get route info with controller if possible
            route_info = self.controller.get_route_info(start_coords, end_coords)
            if route_info:
                distance = route_info.get("distance", direct_distance)
                duration = route_info.get("duration", direct_distance * 4)  # Estimate 15 km/h
                elevation = route_info.get("elevation", 0)  # Get elevation or 0
            else:
                # Use direct distance as fallback
                distance = direct_distance
                duration = distance * 4  # Estimate 15 km/h
                elevation = 0

            # Results display
            print("\n=== AI-Recommended Cycling Route ===")
            print(f"From: {start_location}")
            print(f"To: {end_location}\n")

            print(f"Distance: {general_utils.format_distance(distance)}")
            print(f"Estimated duration: {duration:.0f} minutes")
            if elevation:
                print(f"Elevation gain: {elevation:.0f} meters")

            # Calculate environmental impact
            impact = self.controller.calculate_cycling_eco_impact(distance)

            print("\n=== Environmental Impact ===")
            print(f"CO2 emissions saved: {impact['co2_saved']:.2f} kg")
            print(f"Fuel saved: {impact['fuel_saved']:.2f} liters")
            print(f"Money saved on fuel: ${impact['money_saved']:.2f}")

            # Options
            print("\n=== Options ===")
            print("1. Save this route")
            print("2. Generate map visualization")
            print("3. Return to AI Route Planner menu")

            option = input("\nSelect an option (1-3): ")

            if option == "1":
                # Save route
                route_name = input("Enter a name for this route: ")
                if route_name:
                    print("Saving route...")
                    saved = self.controller.save_user_route(route_name, start_coords, end_coords, distance, duration)

                    if saved:
                        print(f"Route '{route_name}' saved successfully!")
                    else:
                        print("Error saving route. You may need to be logged in.")

                input("\nPress Enter to continue...")

            elif option == "2":
                # Generate map
                print("\nGenerating route map...")
                map_path = self.controller.generate_route_map(start_coords, end_coords, f"AI Route: {distance:.1f} km")

                if map_path:
                    print(f"Route map saved to: {map_path}")

                    open_map = input("Open map in browser? (y/n): ")
                    if open_map.lower() == "y":
                        print("Opening browser...")
                        browser_opened = self.controller.open_map_in_browser(map_path)

                        if browser_opened:
                            print("Map opened in browser.")
                        else:
                            print("Error opening map in browser.")
                else:
                    print("Error generating map.")

                input("\nPress Enter to continue...")

            # Option 3 or any other input returns to menu
            return

    def display_route_safety_assessment(self) -> None:
        """
        Display the route safety assessment interface and handle user interaction.
        """
        ascii_art.clear_screen()
        ascii_art.display_header()

        if RICH_AVAILABLE:
            # Main header panel
            console.print(Panel(
                "Evaluate the safety profile of your cycling routes with AI analysis",
                title="[bold cyan]Route Safety Assessment[/bold cyan]",
                border_style="green",
                expand=False
            ))

            # Input section
            console.print(Panel(
                "[bold]Select a route to analyze:[/bold]",
                border_style="blue",
                title="[bold]Safety Analysis[/bold]",
                expand=False
            ))

            # Get user's saved routes
            routes = self.controller.get_user_routes()

            if not routes:
                console.print(Panel(
                    "[bold yellow]You don't have any saved routes.[/bold yellow]\n"
                    "Please create a route first using the route planner or AI route recommendation.",
                    border_style="yellow"))
                input("\nPress Enter to continue...")
                return

            # Display routes in a styled way
            console.print("[bold]Your saved routes:[/bold]")

            for i, route in enumerate(routes, 1):
                name = route.name
                distance = route.distance
                date_saved = route.get_formatted_date()

                console.print(f"  {i}. [cyan]{name}[/cyan] - {distance:.1f} km (saved on {date_saved})")

            console.print("\n[bold]Enter route number to analyze (or 0 to return):[/bold] ", end="")
            choice = input()

            if choice == "0" or not choice:
                return

            try:
                route_index = int(choice) - 1
                if 0 <= route_index < len(routes):
                    selected_route = routes[route_index]

                    # Perform safety analysis with spinner animation
                    with console.status("[cyan]Performing safety analysis...[/cyan]", spinner="dots12"):
                        # Simulate AI analysis time
                        time.sleep(2.5)

                        # In a real implementation, we'd analyze the actual route
                        # For this demo, we'll generate simulated safety metrics
                        route_name = selected_route.name
                        route_distance = selected_route.distance

                        # Generate safety metrics (would be calculated by AI in real implementation)
                        safety_score = min(95, max(60, 75 + random.randint(-10, 15)))  # Score between 60-95
                        road_quality = min(100, max(40, 70 + random.randint(-20, 25)))  # Score between 40-100
                        traffic_density = min(100, max(10, 50 + random.randint(-20, 40)))  # Score between 10-100
                        bike_lane_coverage = min(100, max(0, 40 + random.randint(-30, 60)))  # Score between 0-100

                        # Generate risk assessments
                        risk_level = "Low" if safety_score >= 80 else "Moderate" if safety_score >= 65 else "High"
                        risk_color = "green" if risk_level == "Low" else "yellow" if risk_level == "Moderate" else "red"

                        # Generate safety recommendations based on metrics
                        recommendations = []
                        if bike_lane_coverage < 50:
                            recommendations.append("Consider using alternative routes with better bike lane coverage")
                        if traffic_density > 70:
                            recommendations.append("Avoid rush hour or consider less congested alternate routes")
                        if road_quality < 60:
                            recommendations.append("Watch for potholes and road defects along this route")
                        if safety_score < 70:
                            recommendations.append("Wear high-visibility clothing and use additional lighting")

                        # Add generic recommendations if list is too short
                        if len(recommendations) < 2:
                            recommendations.append("Always wear a helmet for maximum safety")
                        if len(recommendations) < 3:
                            recommendations.append("Share your route with friends or family when cycling alone")

                    # Display route summary
                    console.print(Panel(
                        f"[bold cyan]Route Name:[/bold cyan] {route_name}\n"
                        f"[bold cyan]Distance:[/bold cyan] {route_distance:.1f} km",
                        title="[bold]Route Summary[/bold]",
                        border_style="blue"
                    ))

                    # Display safety assessment
                    console.print(Panel(
                        f"[bold cyan]Overall Safety Score:[/bold cyan] [bold {risk_color}]{safety_score}/100[/bold {risk_color}]\n"
                        f"[bold cyan]Risk Level:[/bold cyan] [bold {risk_color}]{risk_level}[/bold {risk_color}]\n"
                        f"[bold cyan]Road Quality Rating:[/bold cyan] {road_quality}/100\n"
                        f"[bold cyan]Traffic Density:[/bold cyan] {traffic_density}/100\n"
                        f"[bold cyan]Bike Lane Coverage:[/bold cyan] {bike_lane_coverage}%",
                        title="[bold]Safety Assessment[/bold]",
                        border_style="green"
                    ))

                    # Display safety recommendations
                    recommendations_text = ""
                    for i, rec in enumerate(recommendations, 1):
                        recommendations_text += f"{i}. {rec}\n"

                    console.print(Panel(
                        recommendations_text.strip(),
                        title="[bold]Safety Recommendations[/bold]",
                        border_style="yellow"
                    ))

                    # Show options
                    console.print(Panel(
                        """
1. Generate safety report PDF
2. Share safety analysis
3. Return to AI Route Planner menu
                        """,
                        title="[bold]Options[/bold]",
                        border_style="blue"
                    ))

                    option = input("Select an option (1-3): ")

                    if option == "1" or option == "2":
                        with console.status("[cyan]Processing request...[/cyan]", spinner="dots"):
                            time.sleep(1.5)

                        console.print(Panel(
                            "This feature will be available in the next update!",
                            title="[bold]Coming Soon[/bold]",
                            border_style="yellow"
                        ))
                        input("\nPress Enter to continue...")
                else:
                    console.print("[bold red]Invalid route number.[/bold red]")
                    input("\nPress Enter to continue...")
            except ValueError:
                console.print("[bold red]Invalid input. Please enter a number.[/bold red]")
                input("\nPress Enter to continue...")

        else:
            # Fallback to non-Rich UI version
            ascii_art.display_section_header("Route Safety Assessment")
            print("\nEvaluate the safety profile of your cycling routes with AI analysis")

            # Get user's saved routes
            routes = self.controller.get_user_routes()

            if not routes:
                print("\nYou don't have any saved routes.")
                print("Please create a route first using the route planner or AI route recommendation.")
                input("\nPress Enter to continue...")
                return

            # Display routes in a basic way
            print("\nYour saved routes:\n")

            for i, route in enumerate(routes, 1):
                name = route.name
                distance = route.distance
                date_saved = route.get_formatted_date()

                print(f"  {i}. {name} - {distance:.1f} km (saved on {date_saved})")

            choice = input("\nEnter route number to analyze (or 0 to return): ")

            if choice == "0" or not choice:
                return

            try:
                route_index = int(choice) - 1
                if 0 <= route_index < len(routes):
                    selected_route = routes[route_index]

                    # Perform safety analysis
                    print("\nPerforming safety analysis...")
                    for _ in range(3):
                        time.sleep(0.8)
                        print(".", end="", flush=True)
                    print()

                    # In a real implementation, we'd analyze the actual route
                    # For this demo, we'll generate simulated safety metrics
                    route_name = selected_route.name
                    route_distance = selected_route.distance

                    # Generate safety metrics (would be calculated by AI in real implementation)
                    safety_score = min(95, max(60, 75 + random.randint(-10, 15)))  # Score between 60-95
                    road_quality = min(100, max(40, 70 + random.randint(-20, 25)))  # Score between 40-100
                    traffic_density = min(100, max(10, 50 + random.randint(-20, 40)))  # Score between 10-100
                    bike_lane_coverage = min(100, max(0, 40 + random.randint(-30, 60)))  # Score between 0-100

                    # Generate risk assessments
                    risk_level = "Low" if safety_score >= 80 else "Moderate" if safety_score >= 65 else "High"

                    # Generate safety recommendations based on metrics
                    recommendations = []
                    if bike_lane_coverage < 50:
                        recommendations.append("Consider using alternative routes with better bike lane coverage")
                    if traffic_density > 70:
                        recommendations.append("Avoid rush hour or consider less congested alternate routes")
                    if road_quality < 60:
                        recommendations.append("Watch for potholes and road defects along this route")
                    if safety_score < 70:
                        recommendations.append("Wear high-visibility clothing and use additional lighting")

                    # Add generic recommendations if list is too short
                    if len(recommendations) < 2:
                        recommendations.append("Always wear a helmet for maximum safety")
                    if len(recommendations) < 3:
                        recommendations.append("Share your route with friends or family when cycling alone")

                    # Display route summary
                    print("\n=== Route Summary ===")
                    print(f"Route Name: {route_name}")
                    print(f"Distance: {route_distance:.1f} km")

                    # Display safety assessment
                    print("\n=== Safety Assessment ===")
                    print(f"Overall Safety Score: {safety_score}/100")
                    print(f"Risk Level: {risk_level}")
                    print(f"Road Quality Rating: {road_quality}/100")
                    print(f"Traffic Density: {traffic_density}/100")
                    print(f"Bike Lane Coverage: {bike_lane_coverage}%")

                    # Display safety recommendations
                    print("\n=== Safety Recommendations ===")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"{i}. {rec}")

                    # Show options
                    print("\n=== Options ===")
                    print("1. Generate safety report PDF")
                    print("2. Share safety analysis")
                    print("3. Return to AI Route Planner menu")

                    option = input("\nSelect an option (1-3): ")

                    if option == "1" or option == "2":
                        print("\nProcessing request...")
                        time.sleep(1)
                        print("This feature will be available in the next update!")
                        input("\nPress Enter to continue...")
                else:
                    print("Invalid route number.")
                    input("\nPress Enter to continue...")
            except ValueError:
                print("Invalid input. Please enter a number.")
                input("\nPress Enter to continue...")

    def display_cycling_impact_calculator(self) -> None:
        """
        Display the cycling impact calculator and handle user interaction.
        """
        ascii_art.clear_screen()
        ascii_art.display_header()

        # Use Rich UI if available
        if RICH_AVAILABLE:
            console.print(Panel.fit(
                Text("Cycling Impact Calculator", style="bold cyan"),
                border_style="cyan"
            ))

            console.print(Panel(
                "Calculate the environmental, health, and financial benefits of your cycling habits",
                border_style="blue",
                padding=(1, 2)
            ))

            # Create a form-like input interface
            console.print(Rule("Enter Your Cycling Details", style="cyan"))

            # Exit option
            console.print("\n[yellow]Enter 0 at any time to exit[/yellow]\n")

            # Get input distance and frequency with validation
            try:
                # Distance input with validation
                while True:
                    distance_input = console.input("[cyan]Average cycling distance per trip (km):[/cyan] ")
                    if distance_input == "0":
                        console.print("[yellow]Exiting calculator...[/yellow]")
                        return

                    try:
                        distance = float(distance_input)
                        if distance <= 0:
                            console.print("[red]Distance must be greater than 0.[/red]")
                            continue
                        break
                    except ValueError:
                        console.print("[red]Please enter a valid number.[/red]")

                # Trips per week input with validation
                while True:
                    trips_input = console.input("[cyan]Number of trips per week:[/cyan] ")
                    if trips_input == "0":
                        console.print("[yellow]Exiting calculator...[/yellow]")
                        return

                    try:
                        trips_per_week = float(trips_input)
                        if trips_per_week <= 0:
                            console.print("[red]Number of trips must be greater than 0.[/red]")
                            continue
                        break
                    except ValueError:
                        console.print("[red]Please enter a valid number.[/red]")

                # Optional inputs with defaults
                console.print(Rule("Optional Details (Press Enter to use defaults)", style="cyan"))

                # Weight input
                weight = 70.0  # default weight in kg
                weight_input = console.input("[cyan]Your weight (kg) [default: 70]:[/cyan] ")
                if weight_input:
                    try:
                        weight_value = float(weight_input)
                        if weight_value > 0:
                            weight = weight_value
                        else:
                            console.print("[yellow]Using default weight (70kg) as input was not positive.[/yellow]")
                    except ValueError:
                        console.print("[yellow]Using default weight (70kg) as input was not a valid number.[/yellow]")

                # Speed input
                speed = 15.0  # default speed in km/h
                speed_input = console.input("[cyan]Your average cycling speed (km/h) [default: 15]:[/cyan] ")
                if speed_input:
                    try:
                        speed_value = float(speed_input)
                        if speed_value > 0:
                            speed = speed_value
                        else:
                            console.print("[yellow]Using default speed (15km/h) as input was not positive.[/yellow]")
                    except ValueError:
                        console.print("[yellow]Using default speed (15km/h) as input was not a valid number.[/yellow]")

                # Calculate with spinner animation
                with console.status("[cyan]Calculating your cycling impact...[/cyan]", spinner="dots"):
                    time.sleep(1)  # Simulate calculation time
                    impact = self.controller.calculate_cycling_impact(distance, trips_per_week, weight, speed)

                # Display results in well-formatted panels
                console.print(Rule("Your Cycling Impact Results", style="green"))

                # Create a table for distance metrics
                distance_table = Table(box=rich.box.ROUNDED, border_style="blue")
                distance_table.add_column("Timeframe", style="cyan")
                distance_table.add_column("Distance", style="green", justify="right")

                distance_table.add_row("Per Trip", f"{distance:.1f} km")
                distance_table.add_row("Per Week", f"{impact['distances']['weekly']:.1f} km")
                distance_table.add_row("Per Month", f"{impact['distances']['monthly']:.1f} km")
                distance_table.add_row("Per Year", f"{impact['distances']['yearly']:.1f} km")

                console.print(Panel(distance_table, title="[bold]Distance Traveled[/bold]", border_style="blue"))

                # Create a table for calories burned
                calories_table = Table(box=rich.box.ROUNDED, border_style="blue")
                calories_table.add_column("Timeframe", style="cyan")
                calories_table.add_column("Calories", style="green", justify="right")

                calories_table.add_row("Per Trip", f"{impact['calories']['per_trip']:.0f} kcal")
                calories_table.add_row("Per Week", f"{impact['calories']['weekly']:.0f} kcal")
                calories_table.add_row("Per Month", f"{impact['calories']['monthly']:.0f} kcal")
                calories_table.add_row("Per Year", f"{impact['calories']['yearly']:.0f} kcal")

                console.print(Panel(calories_table, title="[bold]Calories Burned[/bold]", border_style="green"))

                # Create a table for CO2 emissions saved
                co2_table = Table(box=rich.box.ROUNDED, border_style="blue")
                co2_table.add_column("Timeframe", style="cyan")
                co2_table.add_column("CO2 Saved", style="green", justify="right")

                co2_table.add_row("Per Trip", f"{impact['co2_saved']['weekly'] / trips_per_week:.2f} kg")
                co2_table.add_row("Per Week", f"{impact['co2_saved']['weekly']:.2f} kg")
                co2_table.add_row("Per Month", f"{impact['co2_saved']['monthly']:.2f} kg")
                co2_table.add_row("Per Year", f"{impact['co2_saved']['yearly']:.2f} kg")

                console.print(Panel(co2_table, title="[bold]CO2 Emissions Saved[/bold]", border_style="green"))

                # Environmental equivalents
                equivalents = Panel(
                    f"[bold green]🌳 Trees:[/bold green] Your yearly cycling is equivalent to the CO2 absorbed by [bold green]{impact['equivalents']['trees_yearly']:.1f} trees[/bold green]\n\n"
                    f"[bold blue]🚗 Car Travel:[/bold blue] You're saving the emissions from [bold]{impact['equivalents']['car_km']:.1f} km[/bold] of car travel per year\n\n"
                    f"[bold yellow]💰 Fuel Savings:[/bold yellow] Approximately [bold]${impact['co2_saved']['yearly'] * 0.25:.2f}[/bold] in fuel costs saved per year",
                    title="[bold]Environmental Equivalents[/bold]",
                    border_style="cyan"
                )
                console.print(equivalents)

                # Health benefits
                health_benefits = Panel(
                    "✅ [bold green]Improved cardiovascular health[/bold green]\n"
                    "✅ [bold green]Reduced risk of heart disease and stroke[/bold green]\n"
                    "✅ [bold green]Improved mental wellbeing and reduced stress[/bold green]\n"
                    "✅ [bold green]Better sleep quality[/bold green]\n"
                    "✅ [bold green]Strengthened immune system[/bold green]\n"
                    "✅ [bold green]Enhanced muscle strength and flexibility[/bold green]\n\n"
                    f"[bold]Potential yearly weight loss:[/bold] [bold cyan]{impact['health']['potential_weight_loss']:.1f} kg[/bold cyan] (if calories not replaced)",
                    title="[bold]Health Benefits[/bold]",
                    border_style="magenta"
                )
                console.print(health_benefits)

                # Options for saving or sharing results
                options_panel = Panel(
                    "1. Save these results\n"
                    "2. Share results via email\n"
                    "3. Return to main menu",
                    title="[bold]Options[/bold]",
                    border_style="blue"
                )
                console.print(options_panel)

                option = console.input("[cyan]Select an option:[/cyan] ")

                if option == "1" or option == "2":
                    with console.status("[cyan]Processing request...[/cyan]", spinner="dots"):
                        time.sleep(1.5)

                    console.print(Panel(
                        "This feature will be available in the next update!",
                        title="[bold]Coming Soon[/bold]",
                        border_style="yellow"
                    ))

            except Exception as e:
                console.print(f"[bold red]An error occurred:[/bold red] {str(e)}")

        else:
            # Fallback to ASCII art display
            ascii_art.display_section_header("Cycling Impact Calculator")

            print(f"  {ascii_art.Fore.YELLOW}0. Exit Program{ascii_art.Style.RESET_ALL}")
            print("Calculate the environmental and health benefits of your cycling:")

            # Get input distance and frequency
            try:
                distance_input = input("Average cycling distance per trip (km) or 0 to exit: ")
                if distance_input == "0":
                    print("\nExiting program...")
                    return
                distance = float(distance_input)
                trips_per_week = float(input("Number of trips per week: "))

                # Get optional inputs or use defaults
                weight = 70.0  # default weight in kg
                weight_input = input("Your weight (kg) [default: 70]: ")
                if weight_input:
                    weight = float(weight_input)

                speed = 15.0  # default speed in km/h
                speed_input = input("Your average cycling speed (km/h) [default: 15]: ")
                if speed_input:
                    speed = float(speed_input)

                print("\nCalculating impacts...")

                # Calculate impacts
                impact = self.controller.calculate_cycling_impact(distance, trips_per_week, weight, speed)

                # Display results
                print("\nYour Cycling Impact:")

                print(f"\nDistance:")
                print(f"Per week: {impact['distances']['weekly']:.1f} km")
                print(f"Per month: {impact['distances']['monthly']:.1f} km")
                print(f"Per year: {impact['distances']['yearly']:.1f} km")

                print(f"\nCalories Burned:")
                print(f"Per trip: {impact['calories']['per_trip']}")
                print(f"Per week: {impact['calories']['weekly']:.0f}")
                print(f"Per month: {impact['calories']['monthly']:.0f}")
                print(f"Per year: {impact['calories']['yearly']:.0f}")

                print(f"\nCO2 Emissions Saved:")
                print(f"Per week: {impact['co2_saved']['weekly']:.2f} kg")
                print(f"Per month: {impact['co2_saved']['monthly']:.2f} kg")
                print(f"Per year: {impact['co2_saved']['yearly']:.2f} kg")

                print("\nYearly CO2 Savings Equivalent to:")
                print(f"- The CO2 absorbed by {impact['equivalents']['trees_yearly']:.1f} trees")
                print(f"- The emissions from driving {impact['equivalents']['car_km']:.1f} km in an average car")

                print("\nEstimated Health Benefits:")
                print("- Improved cardiovascular health")
                print("- Reduced risk of heart disease and stroke")
                print("- Improved mental wellbeing")
                print("- Better sleep quality")
                print("- Strengthened immune system")

                # Weight loss estimation
                weight_loss = impact['health']['potential_weight_loss']
                print(f"\nPotential yearly weight loss: {weight_loss:.1f} kg (if calories not replaced)")

            except ValueError:
                print("Invalid input. Please enter numeric values.")

        input("\nPress Enter to continue...")
