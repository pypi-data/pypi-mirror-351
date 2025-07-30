"""
EcoCycle - AI Route Planner Main Module
Provides the main AI Route Planner functionality
"""
import os
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

# Import from submodules
from .utils.cache import RouteCache
from .api.gemini_api import GeminiAPI
from .models.route import RouteManager
from .ui.cli import RoutePlannerCLI

# Configure logging
logger = logging.getLogger(__name__)


class AIRoutePlanner:
    """AI-powered cycling route recommendation system."""

    def __init__(self, user_manager=None, sheets_manager=None, routes_file=None):
        """Initialize the AI route planner.

        Args:
            user_manager: Optional user manager instance
            sheets_manager: Optional sheets manager instance
            routes_file: Path to the routes file
        """
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager

        # Initialize components
        self.api = GeminiAPI()
        self.cache = RouteCache()
        self.routes = RouteManager(routes_file if routes_file else os.path.join('data', 'routes', 'ai_routes.json'))
        self.cli = RoutePlannerCLI()

    def run_ai_route_planner(self) -> None:
        """Run the AI route planner interactive interface."""
        if not self.user_manager or not self.user_manager.is_authenticated():
            self.cli.display_message("You need to be logged in to use the AI Route Planner.", "Access Denied", "error")
            return

        username = self.user_manager.get_current_user().get('username')

        # Initialize user data if not present
        self.routes.initialize_user(username)

        while True:
            self.cli.display_main_menu()
            choice = input()

            if choice == '0':
                # Exit program
                self.cli.exit_program()
            elif choice == '1':
                self.generate_route_recommendation(username)
            elif choice == '2':
                self.generate_alternative_routes(username)
            elif choice == '3':
                self.view_saved_routes(username)
            elif choice == '4':
                self.get_detailed_route_analysis(username)
            elif choice == '5':
                self.assess_route_safety(username)
            elif choice == '6':
                self.compare_routes(username)
            elif choice == '7':
                self.update_cycling_preferences(username)
            elif choice == '8':
                break
            else:
                # Invalid choice
                self.cli.display_message("Invalid choice. Please try again.", "Error", "error")
                input("\nPress Enter to continue...")

    def generate_route_recommendation(self, username: str) -> None:
        """Generate a new AI-powered route recommendation.

        Args:
            username: Username of the current user
        """
        self.cli.clear_screen()
        self.cli.display_message("Let's generate a new cycling route recommendation", "New Route", "info")

        # Get user preferences
        preferences = self.routes.get_user_preferences(username)

        # Ask for location
        print("\nWhere would you like to cycle? (city, area, or region)")
        location = input("> ").strip()

        if not location:
            self.cli.display_message("Location cannot be empty. Returning to menu.", "Error", "error")
            input("\nPress Enter to continue...")
            return

        # Generate route using cache if available
        cache_key = self.cache.get_cache_key(location, preferences)
        cached_route = self.cache.get(cache_key)

        if cached_route and not cached_route.get("error"):
            self.cli.display_message("Found a cached route recommendation!", "Cache Hit", "success")
            route = cached_route
        else:
            # Generate new route
            self.cli.display_message(f"Generating a personalized cycling route in {location}...", "Please Wait", "info")

            if self.api.is_available():
                # Use AI to generate route with progress indication
                success, route_data = self.api.generate_route(location, preferences)

                if success:
                    route = route_data
                    # Cache the successful result
                    self.cache.set(cache_key, route)
                    self.cli.display_message("Route generated successfully!", "Success", "success")
                else:
                    error_msg = route_data.get('error', 'Unknown error') if isinstance(route_data, dict) else str(route_data)
                    self.cli.display_message(f"Error generating route with AI: {error_msg}", "Error", "error")
                    route = self._fallback_route_generation(location, preferences)
            else:
                # Use fallback method
                self.cli.display_message(f"AI route generation not available: {self.api.get_error()}", "Using Fallback", "warning")
                route = self._fallback_route_generation(location, preferences)

        # Display the route
        self.cli.display_route(route)

        # Ask if user wants to save the route
        save = input("\nWould you like to save this route? (y/n): ").lower()
        if save == 'y':
            self.routes.save_route(username, route)
            self.cli.display_message("Route saved successfully!", "Success", "success")

        input("\nPress Enter to continue...")

    def _fallback_route_generation(self, location: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a route recommendation using fallback method when AI is not available.

        Args:
            location: The cycling location
            preferences: User preferences dictionary

        Returns:
            A route dictionary
        """
        # Import modules here to avoid circular imports
        import random
        from .utils.constants import POI_CATEGORIES

        # Create a simple template-based route as fallback
        distance = preferences.get('preferred_distance', 10) + random.randint(-2, 2)
        difficulty = preferences.get('preferred_difficulty', 'intermediate')
        terrain = preferences.get('preferred_terrain', 'mixed')
        route_types = preferences.get('preferred_route_types', ['leisure', 'nature'])
        poi_categories = preferences.get('points_of_interest', ['viewpoints', 'cafes', 'parks'])

        # Create route names
        name_prefixes = ["Scenic", "Beautiful", "Adventurous", "Relaxing", "Challenging", "Historic", "Coastal", "Forest", "Urban", "Rural"]
        name_suffixes = ["Loop", "Trail", "Route", "Path", "Circuit", "Trek", "Ride", "Journey", "Adventure", "Excursion"]

        route_name = f"{random.choice(name_prefixes)} {location} {random.choice(name_suffixes)}"

        # Create a template description
        description = f"""
# {route_name}

## Overview
A {difficulty} {terrain} cycling route in {location}, perfect for {', '.join(route_types)} cycling.

## Distance and Difficulty
- Total distance: approximately {distance} km
- Difficulty level: {difficulty}
- Terrain type: {terrain}
- Estimated time: {int(distance * 4)} to {int(distance * 5)} minutes

## Route Description
This route offers a great cycling experience in {location}. You'll encounter varied terrain and beautiful scenery throughout your journey.

## Points of Interest
Look out for these highlights along your route:
{', '.join([f'- {poi.replace("_", " ").title()}' for poi in random.sample(POI_CATEGORIES, min(3, len(POI_CATEGORIES)))])}

## Safety Tips
- Always wear a helmet
- Stay hydrated
- Follow local traffic rules
- Use lights in low visibility conditions

## Best Time to Ride
Early morning or late afternoon for optimal conditions and less traffic.
        """

        return {
            "name": route_name,
            "location": location,
            "description": description,
            "distance": distance,
            "difficulty": difficulty,
            "terrain": terrain,
            "route_types": route_types,
            "points_of_interest": poi_categories,
            "generated_at": time.time(),
            "generated_by": "fallback"
        }

    def view_saved_routes(self, username: str) -> None:
        """View and manage saved routes.

        Args:
            username: Username of the current user
        """
        while True:
            routes = self.routes.get_user_routes(username)

            self.cli.clear_screen()
            self.cli.display_header()

            # Display a nice header for the saved routes section
            if self.cli.has_rich:
                from rich.panel import Panel
                from rich.console import Console

                console = Console()

                # Header panel
                console.print(Panel(
                    "[bold]View and manage your saved cycling routes[/bold]",
                    title="[bold white on cyan]📋 Saved Routes[/bold white on cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                ))
            else:
                self.cli.display_message("View and manage your saved cycling routes", "Saved Routes", "info")

            # Display routes table
            self.cli.display_routes_table(routes)

            if not routes:
                self.cli.display_message("You don't have any saved routes yet. Generate a route first!", "No Routes", "warning")
                input("\nPress Enter to continue...")
                return

            # Display options with enhanced UI
            if self.cli.has_rich:
                from rich.panel import Panel
                from rich.console import Console

                console = Console()
                console.print(Panel(
                    """
[bold]Available Actions:[/bold]

[bold green]1. 🔍 View route details[/bold green] - See full information about a selected route
[bold blue]2. 📤 Export route[/bold blue] - Export a route to share with others
[bold red]3. 🗑️ Delete route[/bold red] - Remove a route from your collection
[bold yellow]4. 🔄 Refresh list[/bold yellow] - Refresh the routes list
[bold magenta]5. 🏠 Return to menu[/bold magenta] - Go back to the main menu
                    """,
                    title="[bold white on blue]🛠️ Options[/bold white on blue]",
                    border_style="blue",
                    padding=(1, 2)
                ))

                console.print("\n[bold white on blue]Select an option (1-5):[/bold white on blue] ", end="")
            else:
                print("\nOptions:")
                print("  1. 🔍 View route details")
                print("  2. 📤 Export route")
                print("  3. 🗑️ Delete route")
                print("  4. 🔄 Refresh list")
                print("  5. 🏠 Return to menu")
                print("\nSelect an option (1-5): ", end="")

            choice = input().strip()

            if choice == '1':
                # View route details
                self._view_route_details(username, routes)
            elif choice == '2':
                # Export/share route
                self._share_route(username, routes)
            elif choice == '3':
                # Delete route
                self._delete_route(username, routes)
            elif choice == '4':
                # Refresh list - just continue the loop
                continue
            elif choice == '5':
                # Return to menu
                return
            else:
                self.cli.display_message("Invalid choice. Please try again.", "Error", "error")
                input("\nPress Enter to continue...")

    def _view_route_details(self, username: str, routes: List[Dict]) -> None:
        """View details of a selected route.

        Args:
            username: Username of the current user
            routes: List of routes to select from
        """
        # Display prompt with enhanced UI
        if self.cli.has_rich:
            from rich.console import Console

            console = Console()
            console.print("\n[bold]Enter the number of the route to view (1-{}, or 0 to cancel):[/bold] ".format(len(routes)), end="")
        else:
            print("\nEnter the number of the route to view (1-{}, or 0 to cancel): ".format(len(routes)), end="")

        try:
            index = int(input()) - 1
            if index == -1:
                return
            if 0 <= index < len(routes):
                selected_route = routes[index]

                self.cli.clear_screen()
                self.cli.display_header()

                # Enhanced route display with Rich UI
                if self.cli.has_rich:
                    from rich.console import Console
                    from rich.panel import Panel
                    from rich.markdown import Markdown
                    from rich.table import Table

                    console = Console()

                    # Header panel
                    console.print(Panel(
                        f"[bold]{selected_route.get('name', 'Unnamed Route')}[/bold]",
                        title="[bold white on green]🗺️ Route Details[/bold white on green]",
                        border_style="green",
                        padding=(1, 2)
                    ))

                    # Route metadata table
                    metadata_table = Table(show_header=False, box=None, padding=(0, 2))
                    metadata_table.add_column("Property", style="cyan")
                    metadata_table.add_column("Value", style="yellow")

                    metadata_table.add_row("Location", selected_route.get('location', 'Unknown'))
                    metadata_table.add_row("Distance", f"{selected_route.get('distance', 0)} km")
                    metadata_table.add_row("Difficulty", selected_route.get('difficulty', 'Not specified'))
                    metadata_table.add_row("Terrain", selected_route.get('terrain', 'Not specified'))

                    # Add route types if available
                    route_types = selected_route.get('route_types', [])
                    if route_types:
                        metadata_table.add_row("Route Types", ", ".join(route_types))

                    # Add points of interest if available
                    pois = selected_route.get('points_of_interest', [])
                    if pois:
                        metadata_table.add_row("Points of Interest", ", ".join([p.replace('_', ' ').title() for p in pois]))

                    # Add generation info if available
                    if 'generated_at' in selected_route:
                        import datetime
                        generated_time = datetime.datetime.fromtimestamp(selected_route['generated_at']).strftime('%Y-%m-%d %H:%M')
                        metadata_table.add_row("Generated", generated_time)

                    console.print(metadata_table)

                    # Route description
                    description = selected_route.get('raw_response', selected_route.get('description', 'No route description available.'))
                    console.print(Panel(
                        Markdown(description),
                        title="[bold white on blue]📝 Description[/bold white on blue]",
                        border_style="blue",
                        padding=(1, 2)
                    ))

                    # Footer with actions
                    console.print(Panel(
                        "[bold]Press Enter to return to the routes menu[/bold]",
                        border_style="dim",
                        padding=(0, 1)
                    ))
                else:
                    # Fallback to basic display
                    self.cli.display_route(selected_route)

                input("\nPress Enter to continue...")
            else:
                self.cli.display_message("Invalid selection", "Error", "error")
                input("\nPress Enter to continue...")
        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")
            input("\nPress Enter to continue...")

    def _share_route(self, username: str, routes: List[Dict]) -> None:
        """Share a route with other users or export it.

        Args:
            username: Username of the current user
            routes: List of routes to select from
        """
        # Display prompt with enhanced UI
        if self.cli.has_rich:
            from rich.console import Console

            console = Console()
            console.print("\n[bold]Enter the number of the route to export (1-{}, or 0 to cancel):[/bold] ".format(len(routes)), end="")
        else:
            print("\nEnter the number of the route to export (1-{}, or 0 to cancel): ".format(len(routes)), end="")

        try:
            index = int(input()) - 1
            if index == -1:
                return
            if 0 <= index < len(routes):
                selected_route = routes[index]

                self.cli.clear_screen()
                self.cli.display_header()

                # Display export options
                if self.cli.has_rich:
                    from rich.console import Console
                    from rich.panel import Panel

                    console = Console()

                    # Header panel
                    console.print(Panel(
                        f"[bold]Export Route: {selected_route.get('name', 'Unnamed Route')}[/bold]",
                        title="[bold white on blue]📤 Export Options[/bold white on blue]",
                        border_style="blue",
                        padding=(1, 2)
                    ))

                    # Export options panel
                    console.print(Panel(
                        """
[bold]Available Export Formats:[/bold]

[bold green]1. 📝 Text File[/bold green] - Export route details to a text file
[bold blue]2. 📋 Copy to Clipboard[/bold blue] - Copy route details to clipboard
[bold yellow]3. 🔙 Back[/bold yellow] - Return to routes menu
                        """,
                        border_style="blue",
                        padding=(1, 2)
                    ))

                    console.print("\n[bold]Select an export option (1-3):[/bold] ", end="")
                else:
                    print(f"\n=== Export Route: {selected_route.get('name', 'Unnamed Route')} ===\n")
                    print("Available Export Formats:")
                    print("  1. 📝 Text File - Export route details to a text file")
                    print("  2. 📋 Copy to Clipboard - Copy route details to clipboard")
                    print("  3. 🔙 Back - Return to routes menu")
                    print("\nSelect an export option (1-3): ", end="")

                export_choice = input().strip()

                if export_choice == '1':
                    # Export to text file
                    import os

                    # Create export directory if it doesn't exist
                    export_dir = os.path.join('data', 'exports')
                    os.makedirs(export_dir, exist_ok=True)

                    # Generate filename
                    route_name = selected_route.get('name', 'route').replace(' ', '_').lower()
                    filename = f"{route_name}_{username}.txt"
                    filepath = os.path.join(export_dir, filename)

                    # Format route data
                    route_text = self._format_route_for_export(selected_route)

                    # Write to file
                    try:
                        with open(filepath, 'w') as f:
                            f.write(route_text)

                        self.cli.display_message(
                            f"Route exported successfully to {filepath}",
                            "Export Successful",
                            "success"
                        )
                    except Exception as e:
                        self.cli.display_message(
                            f"Failed to export route: {str(e)}",
                            "Export Failed",
                            "error"
                        )

                elif export_choice == '2':
                    # Copy to clipboard
                    try:
                        # Format route data
                        route_text = self._format_route_for_export(selected_route)

                        # Try to use pyperclip if available (optional dependency)
                        try:
                            # pyperclip is an optional dependency that may not be installed
                            import pyperclip
                            pyperclip.copy(route_text)
                            self.cli.display_message(
                                "Route details copied to clipboard!",
                                "Copy Successful",
                                "success"
                            )
                        except ImportError:
                            # Fallback to OS-specific clipboard commands
                            import subprocess
                            import platform

                            system = platform.system()

                            if system == 'Darwin':  # macOS
                                process = subprocess.Popen(
                                    'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE
                                )
                                process.communicate(route_text.encode('utf-8'))
                                self.cli.display_message(
                                    "Route details copied to clipboard!",
                                    "Copy Successful",
                                    "success"
                                )
                            elif system == 'Windows':
                                process = subprocess.Popen(
                                    'clip', stdin=subprocess.PIPE
                                )
                                process.communicate(route_text.encode('utf-8'))
                                self.cli.display_message(
                                    "Route details copied to clipboard!",
                                    "Copy Successful",
                                    "success"
                                )
                            else:
                                self.cli.display_message(
                                    "Clipboard functionality requires pyperclip package. Please install it with: pip install pyperclip",
                                    "Copy Failed",
                                    "error"
                                )
                    except Exception as e:
                        self.cli.display_message(
                            f"Failed to copy to clipboard: {str(e)}",
                            "Copy Failed",
                            "error"
                        )

                # Option 3 or any other input returns to menu

            else:
                self.cli.display_message("Invalid selection", "Error", "error")
        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")

        input("\nPress Enter to continue...")

    def _format_route_for_export(self, route: Dict[str, Any]) -> str:
        """Format a route for export to text.

        Args:
            route: The route dictionary to format

        Returns:
            Formatted route text
        """
        # Build the formatted text
        lines = []

        # Header
        lines.append("=" * 50)
        lines.append(f"ROUTE: {route.get('name', 'Unnamed Route')}")
        lines.append("=" * 50)
        lines.append("")

        # Metadata
        lines.append(f"Location: {route.get('location', 'Unknown')}")
        lines.append(f"Distance: {route.get('distance', 0)} km")
        lines.append(f"Difficulty: {route.get('difficulty', 'Not specified')}")
        lines.append(f"Terrain: {route.get('terrain', 'Not specified')}")

        # Add route types if available
        route_types = route.get('route_types', [])
        if route_types:
            lines.append(f"Route Types: {', '.join(route_types)}")

        # Add points of interest if available
        pois = route.get('points_of_interest', [])
        if pois:
            lines.append(f"Points of Interest: {', '.join([p.replace('_', ' ').title() for p in pois])}")

        # Add generation info if available
        if 'generated_at' in route:
            import datetime
            generated_time = datetime.datetime.fromtimestamp(route['generated_at']).strftime('%Y-%m-%d %H:%M')
            lines.append(f"Generated: {generated_time}")

        lines.append("")
        lines.append("-" * 50)
        lines.append("")

        # Description
        lines.append("DESCRIPTION:")
        lines.append("")
        description = route.get('description', 'No route description available.')
        lines.append(description)

        # Footer
        lines.append("")
        lines.append("-" * 50)
        lines.append("Generated by EcoCycle AI Route Planner")

        return "\n".join(lines)

    def _delete_route(self, username: str, routes: List[Dict]) -> None:
        """Delete a saved route.

        Args:
            username: Username of the current user
            routes: List of routes to select from
        """
        # Display prompt with enhanced UI
        if self.cli.has_rich:
            from rich.console import Console

            console = Console()
            console.print("\n[bold]Enter the number of the route to delete (1-{}, or 0 to cancel):[/bold] ".format(len(routes)), end="")
        else:
            print("\nEnter the number of the route to delete (1-{}, or 0 to cancel): ".format(len(routes)), end="")

        try:
            index = int(input()) - 1
            if index == -1:
                return
            if 0 <= index < len(routes):
                # Get route details
                route_name = routes[index].get('name', 'Unnamed Route')

                # Display confirmation with enhanced UI
                if self.cli.has_rich:
                    from rich.console import Console
                    from rich.panel import Panel

                    console = Console()

                    # Warning panel
                    console.print(Panel(
                        f"[bold red]You are about to delete the route:[/bold red] [bold yellow]{route_name}[/bold yellow]\n\n"
                        "[bold]This action cannot be undone![/bold]",
                        title="[bold white on red]⚠️ Warning[/bold white on red]",
                        border_style="red",
                        padding=(1, 2)
                    ))

                    console.print("\n[bold]Are you sure you want to delete this route? (y/n):[/bold] ", end="")
                else:
                    print(f"\n⚠️ WARNING: You are about to delete the route: {route_name}")
                    print("This action cannot be undone!")
                    print("\nAre you sure you want to delete this route? (y/n): ", end="")

                confirm = input().lower().strip()

                if confirm == 'y':
                    # Show deletion in progress
                    if self.cli.has_rich:
                        from rich.console import Console

                        console = Console()
                        with console.status("[bold cyan]Deleting route...[/bold cyan]") as status:
                            success = self.routes.delete_route(username, index)
                    else:
                        print("\nDeleting route...")
                        success = self.routes.delete_route(username, index)

                    # Show result
                    if success:
                        self.cli.display_message(f"Route '{route_name}' deleted successfully", "Success", "success")
                    else:
                        self.cli.display_message("Failed to delete route", "Error", "error")
                else:
                    # User canceled deletion
                    self.cli.display_message("Deletion canceled", "Canceled", "info")
            else:
                self.cli.display_message("Invalid selection", "Error", "error")
        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")

        input("\nPress Enter to continue...")

    def update_cycling_preferences(self, username: str) -> None:
        """Update user's cycling preferences for route recommendations.

        Args:
            username: Username of the current user
        """
        # Import constants for validation
        from .utils.constants import DIFFICULTY_LEVELS, TERRAIN_TYPES, ROUTE_TYPES, POI_CATEGORIES

        self.cli.clear_screen()
        self.cli.display_header()

        # Get current preferences
        current_prefs = self.routes.get_user_preferences(username)

        # Enhanced UI with Rich if available
        if self.cli.has_rich:
            try:
                from rich.console import Console
                from rich.panel import Panel
                from rich.table import Table
                from rich.status import Status
                from rich import print as rich_print

                console = Console()

                # Header panel
                console.print(Panel(
                    "[bold]Customize your cycling preferences for personalized route recommendations[/bold]",
                    title="[bold white on purple]🚲 Cycling Preferences [/bold white on purple]",
                    border_style="purple",
                    padding=(1, 2)
                ))

                # Current preferences table
                # Use rich.box.ROUNDED instead of True for the box parameter
                from rich.box import ROUNDED
                prefs_table = Table(title="Current Preferences", show_header=False, box=ROUNDED, expand=False, highlight=True)
                prefs_table.add_column("Preference", style="cyan", no_wrap=True)
                prefs_table.add_column("Value", style="yellow")

                prefs_table.add_row("Preferred Distance", f"{current_prefs.get('preferred_distance', 10)} km")
                prefs_table.add_row("Difficulty Level", current_prefs.get('preferred_difficulty', 'intermediate').title())
                prefs_table.add_row("Terrain Type", current_prefs.get('preferred_terrain', 'mixed').title())
                prefs_table.add_row("Route Types", ", ".join([rt.title() for rt in current_prefs.get('preferred_route_types', ['leisure', 'nature'])]))
                prefs_table.add_row("Points of Interest", ", ".join([p.replace('_', ' ').title() for p in current_prefs.get('points_of_interest', ['viewpoints', 'cafes', 'parks'])]))

                console.print(prefs_table)

                # Update section header
                console.print(Panel(
                    "[italic]Enter new values or press Enter to keep current values[/italic]",
                    title="[bold white on blue]✏️ Update Preferences[/bold white on blue]",
                    border_style="blue",
                    padding=(1, 2)
                ))

                # Distance input with validation - using standard input instead of Rich Prompt
                console.print("[bold cyan]Preferred Distance[/bold cyan]")
                console.print(f"Current value: [yellow]{current_prefs.get('preferred_distance', 10)} km[/yellow]")

                # Use standard input for getting values to avoid Rich Prompt issues
                while True:
                    try:
                        distance_input = input("Enter preferred cycling distance in km (or press Enter to keep current): ").strip()
                        if distance_input:
                            current_prefs['preferred_distance'] = float(distance_input)
                        break
                    except ValueError:
                        console.print("[bold red]Invalid input. Please enter a number.[/bold red]")

                # Difficulty level
                console.print("\n[bold cyan]Difficulty Level[/bold cyan]")
                console.print(f"Available options: [green]{', '.join([level.title() for level in DIFFICULTY_LEVELS])}[/green]")
                console.print(f"Current value: [yellow]{current_prefs.get('preferred_difficulty', 'intermediate').title()}[/yellow]")

                difficulty_input = input("Enter preferred difficulty level (or press Enter to keep current): ").strip().lower()
                if difficulty_input in DIFFICULTY_LEVELS:
                    current_prefs['preferred_difficulty'] = difficulty_input
                elif difficulty_input:
                    console.print("[bold yellow]Invalid difficulty level. Keeping current value.[/bold yellow]")

                # Terrain type
                console.print("\n[bold cyan]Terrain Type[/bold cyan]")
                console.print(f"Available options: [green]{', '.join([terrain.title() for terrain in TERRAIN_TYPES])}[/green]")
                console.print(f"Current value: [yellow]{current_prefs.get('preferred_terrain', 'mixed').title()}[/yellow]")

                terrain_input = input("Enter preferred terrain type (or press Enter to keep current): ").strip().lower()
                if terrain_input in TERRAIN_TYPES:
                    current_prefs['preferred_terrain'] = terrain_input
                elif terrain_input:
                    console.print("[bold yellow]Invalid terrain type. Keeping current value.[/bold yellow]")

                # Route types
                console.print("\n[bold cyan]Route Types[/bold cyan]")
                console.print(f"Available options: [green]{', '.join([rt.title() for rt in ROUTE_TYPES])}[/green]")
                console.print(f"Current value: [yellow]{', '.join([rt.title() for rt in current_prefs.get('preferred_route_types', ['leisure', 'nature'])])}[/yellow]")

                route_types_input = input("Enter preferred route types, comma-separated (or press Enter to keep current): ").strip().lower()
                if route_types_input:
                    route_types = [rt.strip() for rt in route_types_input.split(',')]
                    valid_types = [rt for rt in route_types if rt in ROUTE_TYPES]
                    invalid_types = [rt for rt in route_types if rt not in ROUTE_TYPES and rt]

                    if invalid_types:
                        console.print(f"[bold yellow]Some route types were invalid and will be ignored: {', '.join(invalid_types)}[/bold yellow]")

                    if valid_types:  # Only update if there are valid types
                        current_prefs['preferred_route_types'] = valid_types

                # Points of interest
                console.print("\n[bold cyan]Points of Interest[/bold cyan]")
                console.print(f"Available options: [green]{', '.join([p.replace('_', ' ').title() for p in POI_CATEGORIES])}[/green]")
                console.print(f"Current value: [yellow]{', '.join([p.replace('_', ' ').title() for p in current_prefs.get('points_of_interest', ['viewpoints', 'cafes', 'parks'])])}[/yellow]")

                poi_input = input("Enter preferred points of interest, comma-separated (or press Enter to keep current): ").strip().lower()
                if poi_input:
                    pois = [poi.strip().replace(' ', '_') for poi in poi_input.split(',')]
                    valid_pois = [poi for poi in pois if poi in POI_CATEGORIES]
                    invalid_pois = [poi.replace('_', ' ') for poi in pois if poi not in POI_CATEGORIES and poi]

                    if invalid_pois:
                        console.print(f"[bold yellow]Some points of interest were invalid and will be ignored: {', '.join(invalid_pois)}[/bold yellow]")

                    if valid_pois:  # Only update if there are valid points of interest
                        current_prefs['points_of_interest'] = valid_pois

                # Save preferences with visual indicator
                with console.status("[bold green]Saving preferences...[/bold green]") as status:
                    try:
                        # Call the update_preferences method and explicitly convert the result to a boolean
                        # to avoid the "'bool' object has no attribute 'substitute'" error
                        result = self.routes.update_preferences(username, current_prefs)
                        # Ensure we have a simple boolean value, not an object that might cause template issues
                        success = True if result else False
                    except Exception as e:
                        logger.error(f"Error updating preferences: {e}")
                        success = False

                if success:
                    # Updated preferences summary
                    # Use the already imported ROUNDED box
                    summary_table = Table(title="Updated Preferences", show_header=False, box=ROUNDED, expand=False, highlight=True)
                    summary_table.add_column("Preference", style="cyan", no_wrap=True)
                    summary_table.add_column("Value", style="green")

                    summary_table.add_row("Preferred Distance", f"{current_prefs.get('preferred_distance', 10)} km")
                    summary_table.add_row("Difficulty Level", current_prefs.get('preferred_difficulty', 'intermediate').title())
                    summary_table.add_row("Terrain Type", current_prefs.get('preferred_terrain', 'mixed').title())
                    summary_table.add_row("Route Types", ", ".join([rt.title() for rt in current_prefs.get('preferred_route_types', ['leisure', 'nature'])]))
                    summary_table.add_row("Points of Interest", ", ".join([p.replace('_', ' ').title() for p in current_prefs.get('points_of_interest', ['viewpoints', 'cafes', 'parks'])]))

                    console.print(Panel(
                        "[bold green]Your cycling preferences have been updated successfully![/bold green]\n\n" +
                        "These preferences will be used to generate personalized route recommendations that match your cycling style.",
                        title="[bold white on green]✅ Success[/bold white on green]",
                        border_style="green",
                        padding=(1, 2)
                    ))

                    console.print(summary_table)
                else:
                    console.print(Panel(
                        "[bold red]Unable to save your preferences. Please try again later.[/bold red]",
                        title="[bold white on red]❌ Error[/bold white on red]",
                        border_style="red",
                        padding=(1, 2)
                    ))

            except ImportError:
                # Fall back to basic display if Rich isn't available
                self._update_cycling_preferences_basic(username, current_prefs)
                return
        else:
            # Basic text UI if Rich is not available
            self._update_cycling_preferences_basic(username, current_prefs)
            return

        input("\nPress Enter to continue...")

    def _update_cycling_preferences_basic(self, username: str, current_prefs: Dict[str, Any]) -> None:
        """Basic text interface for updating cycling preferences when Rich UI is not available.

        Args:
            username: Username of the current user
            current_prefs: Dictionary of current user preferences
        """
        from .utils.constants import DIFFICULTY_LEVELS, TERRAIN_TYPES, ROUTE_TYPES, POI_CATEGORIES

        # Display current preferences
        print("\n==== Current Preferences ====\n")
        print(f"  Preferred distance: {current_prefs.get('preferred_distance', 10)} km")
        print(f"  Difficulty level: {current_prefs.get('preferred_difficulty', 'intermediate')}")
        print(f"  Terrain type: {current_prefs.get('preferred_terrain', 'mixed')}")
        print(f"  Route types: {', '.join(current_prefs.get('preferred_route_types', ['leisure', 'nature']))}")
        print(f"  Points of interest: {', '.join([p.replace('_', ' ') for p in current_prefs.get('points_of_interest', ['viewpoints', 'cafes', 'parks'])])}")

        # Ask for updates
        print("\n==== Update Preferences ====\n")
        print("Enter new values (or leave blank to keep current):")

        # Distance
        try:
            distance_input = input(f"Preferred distance (km) [{current_prefs.get('preferred_distance', 10)}]: ").strip()
            if distance_input:
                current_prefs['preferred_distance'] = float(distance_input)
        except ValueError:
            print("Invalid input for distance. Keeping current value.")

        # Difficulty
        print(f"\nDifficulty levels: {', '.join(DIFFICULTY_LEVELS)}")
        difficulty_input = input(f"Preferred difficulty [{current_prefs.get('preferred_difficulty', 'intermediate')}]: ").strip().lower()
        if difficulty_input in DIFFICULTY_LEVELS:
            current_prefs['preferred_difficulty'] = difficulty_input
        elif difficulty_input:
            print("Invalid difficulty level. Keeping current value.")

        # Terrain
        print(f"\nTerrain types: {', '.join(TERRAIN_TYPES)}")
        terrain_input = input(f"Preferred terrain [{current_prefs.get('preferred_terrain', 'mixed')}]: ").strip().lower()
        if terrain_input in TERRAIN_TYPES:
            current_prefs['preferred_terrain'] = terrain_input
        elif terrain_input:
            print("Invalid terrain type. Keeping current value.")

        # Route types
        print(f"\nRoute types: {', '.join(ROUTE_TYPES)}")
        print("Enter preferred route types, comma-separated")
        route_types_input = input(f"[{', '.join(current_prefs.get('preferred_route_types', ['leisure', 'nature']))}]: ").strip().lower()
        if route_types_input:
            route_types = [rt.strip() for rt in route_types_input.split(',')]
            current_prefs['preferred_route_types'] = [rt for rt in route_types if rt in ROUTE_TYPES]

        # Points of interest
        print(f"\nPoints of interest categories: {', '.join([p.replace('_', ' ') for p in POI_CATEGORIES])}")
        print("Enter preferred points of interest, comma-separated")
        poi_input = input(f"[{', '.join([p.replace('_', ' ') for p in current_prefs.get('points_of_interest', ['viewpoints', 'cafes', 'parks'])])}]: ").strip().lower()
        if poi_input:
            pois = [poi.strip().replace(' ', '_') for poi in poi_input.split(',')]
            current_prefs['points_of_interest'] = [poi for poi in pois if poi in POI_CATEGORIES]

        # Save updated preferences
        print("\nSaving preferences...")
        # Explicitly convert the result to a boolean to avoid template substitution issues
        result = self.routes.update_preferences(username, current_prefs)
        success = True if result else False

        if success:
            print("\n==== Updated Successfully! ====\n")
            print("Your cycling preferences have been updated:")
            print(f"  Preferred distance: {current_prefs.get('preferred_distance', 10)} km")
            print(f"  Difficulty level: {current_prefs.get('preferred_difficulty', 'intermediate')}")
            print(f"  Terrain type: {current_prefs.get('preferred_terrain', 'mixed')}")
            print(f"  Route types: {', '.join(current_prefs.get('preferred_route_types', ['leisure', 'nature']))}")
            print(f"  Points of interest: {', '.join([p.replace('_', ' ') for p in current_prefs.get('points_of_interest', ['viewpoints', 'cafes', 'parks'])])}")
        else:
            print("\nError: Failed to update preferences.")

        input("\nPress Enter to continue...")

    def get_detailed_route_analysis(self, username: str) -> None:
        """Get detailed analysis of a selected route.

        Args:
            username: Username of the current user
        """
        self.cli.clear_screen()
        self.cli.display_header()

        # Get user's saved routes
        routes = self.routes.get_user_routes(username)

        if not routes:
            self.cli.display_message("You don't have any saved routes to analyze.", "No Routes", "warning")
            input("\nPress Enter to continue...")
            return

        # Check if the API is available
        if not self.api.is_available():
            error_message = self.api.get_error()

            # Check if the error is due to missing package
            if error_message == "Package not installed":
                # Import dependency manager
                import core.dependency.dependency_manager as dependency_manager

                self.cli.display_message(
                    "Route analysis requires the Google Generative AI package which is not installed.",
                    "Package Required",
                    "warning"
                )

                # Ask user if they want to install the package
                install = input("\nWould you like to install the required package now? (y/n): ")
                if install.lower() == 'y':
                    self.cli.display_message("Installing Google Generative AI package...", "Installing", "info")

                    # Install the package
                    success = dependency_manager.ensure_package('google-generativeai', silent=False)

                    if success:
                        self.cli.display_message(
                            "Package installed successfully! Initializing API...",
                            "Success",
                            "success"
                        )

                        # Reinitialize the API
                        self.api._initialize_gemini()

                        # Check if initialization was successful
                        if self.api.is_available():
                            self.cli.display_message(
                                "API initialized successfully! You can now analyze routes.",
                                "API Ready",
                                "success"
                            )
                            input("\nPress Enter to continue...")
                            # Restart the function to continue with route analysis
                            self.get_detailed_route_analysis(username)
                            return
                        else:
                            # API still not available, might be missing API key
                            self.cli.display_message(
                                f"Package installed but API initialization failed: {self.api.get_error()}",
                                "API Not Available",
                                "error"
                            )
                    else:
                        self.cli.display_message(
                            "Failed to install the required package. Please install it manually with: pip install google-generativeai",
                            "Installation Failed",
                            "error"
                        )
                input("\nPress Enter to continue...")
                return
            else:
                # Other API error
                self.cli.display_message(
                    f"Route analysis requires the Gemini API which is currently unavailable.\n\nError: {error_message}",
                    "API Not Available",
                    "error"
                )
                input("\nPress Enter to continue...")
                return

        # Display routes for selection
        self.cli.display_message("Select a route to analyze", "Route Analysis", "info")
        self.cli.display_routes_table(routes)

        # Get user selection
        print("\nEnter the number of the route to analyze (1-{}, or 0 to cancel): ".format(len(routes)), end="")
        try:
            index = int(input()) - 1
            if index == -1:
                return
            if 0 <= index < len(routes):
                selected_route = routes[index]

                # Show loading message
                self.cli.display_message(f"Analyzing route '{selected_route.get('name')}'. This may take a moment...", "Analyzing", "info")

                # Prepare prompt for Gemini
                prompt = f"""
                Analyze this cycling route and provide detailed insights about it.
                Give me a professional analysis including:

                1. Overall assessment of the route quality
                2. Fitness benefits analysis
                3. Environmental impact (CO2 saved if cycling instead of driving)
                4. Seasonal considerations (when is best to ride this route)
                5. Suggested improvements or variations
                6. Training value for different cyclist types
                7. Points of special interest that might be missed

                Route details:
                Name: {selected_route.get('name', 'Unnamed Route')}
                Location: {selected_route.get('location', 'Unknown')}
                Distance: {selected_route.get('distance', 0)} km
                Difficulty: {selected_route.get('difficulty', 'Not specified')}
                Terrain: {selected_route.get('terrain', 'Not specified')}

                Route description:
                {selected_route.get('description', 'No description available')}

                Format your response in clear sections with descriptive headers.
                """

                # Call the API with progress indication
                success, response = self.api.call_gemini_api(prompt, progress_message="📊 Analyzing route details")

                if success:
                    # Display the analysis
                    self.cli.clear_screen()
                    self.cli.display_header()

                    if self.cli.has_rich:
                        from rich.markdown import Markdown
                        from rich.panel import Panel
                        from rich.console import Console

                        console = Console()
                        console.print(Panel(
                            f"[bold]Detailed Analysis: {selected_route.get('name', 'Unnamed Route')}[/bold]",
                            border_style="green",
                            padding=(1, 2)
                        ))

                        analysis_markdown = Markdown(str(response))
                        console.print(analysis_markdown)
                    else:
                        print(f"\n=== Detailed Analysis: {selected_route.get('name', 'Unnamed Route')} ===\n")
                        print(response)
                else:
                    # Display error
                    self.cli.display_message(f"Failed to analyze route: {response}", "Analysis Failed", "error")
            else:
                self.cli.display_message("Invalid selection", "Error", "error")
        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")

        input("\nPress Enter to continue...")

    def assess_route_safety(self, username: str) -> None:
        """Assess the safety of a route and provide recommendations.

        Args:
            username: Username of the current user
        """
        self.cli.clear_screen()
        self.cli.display_header()

        # Get user's saved routes
        routes = self.routes.get_user_routes(username)

        if not routes:
            self.cli.display_message("You don't have any saved routes to assess.", "No Routes", "warning")
            input("\nPress Enter to continue...")
            return

        # Check if the API is available
        if not self.api.is_available():
            error_message = self.api.get_error()

            # Check if the error is due to missing package
            if error_message == "Package not installed":
                # Import dependency manager
                import core.dependency.dependency_manager as dependency_manager

                self.cli.display_message(
                    "Safety assessment requires the Google Generative AI package which is not installed.",
                    "Package Required",
                    "warning"
                )

                # Ask user if they want to install the package
                install = input("\nWould you like to install the required package now? (y/n): ")
                if install.lower() == 'y':
                    self.cli.display_message("Installing Google Generative AI package...", "Installing", "info")

                    # Install the package
                    success = dependency_manager.ensure_package('google-generativeai', silent=False)

                    if success:
                        self.cli.display_message(
                            "Package installed successfully! Initializing API...",
                            "Success",
                            "success"
                        )

                        # Reinitialize the API
                        self.api._initialize_gemini()

                        # Check if initialization was successful
                        if self.api.is_available():
                            self.cli.display_message(
                                "API initialized successfully! You can now assess route safety.",
                                "API Ready",
                                "success"
                            )
                            input("\nPress Enter to continue...")
                            # Restart the function to continue with safety assessment
                            self.assess_route_safety(username)
                            return
                        else:
                            # API still not available, might be missing API key
                            self.cli.display_message(
                                f"Package installed but API initialization failed: {self.api.get_error()}",
                                "API Not Available",
                                "error"
                            )
                    else:
                        self.cli.display_message(
                            "Failed to install the required package. Please install it manually with: pip install google-generativeai",
                            "Installation Failed",
                            "error"
                        )
                input("\nPress Enter to continue...")
                return
            else:
                # Other API error
                self.cli.display_message(
                    f"Safety assessment requires the Gemini API which is currently unavailable.\n\nError: {error_message}",
                    "API Not Available",
                    "error"
                )
                input("\nPress Enter to continue...")
                return

        # Display routes for selection
        self.cli.display_message("Select a route to assess for safety", "Safety Assessment", "info")
        self.cli.display_routes_table(routes)

        # Get user selection
        print("\nEnter the number of the route to assess (1-{}, or 0 to cancel): ".format(len(routes)), end="")
        try:
            index = int(input()) - 1
            if index == -1:
                return
            if 0 <= index < len(routes):
                selected_route = routes[index]

                # Show loading message
                self.cli.display_message(f"Assessing safety of route '{selected_route.get('name')}'. This may take a moment...", "Analyzing", "info")

                # Prepare prompt for Gemini
                prompt = f"""
                Perform a detailed safety assessment of this cycling route.
                Provide a comprehensive safety analysis including:

                1. Overall safety rating (on a scale of 1-10)
                2. Traffic density assessment
                3. Road quality and infrastructure
                4. Potential hazards and danger points
                5. Visibility considerations
                6. Weather impact on safety
                7. Emergency access points
                8. Specific safety recommendations for cyclists
                9. Required safety equipment for this route

                Route details:
                Name: {selected_route.get('name', 'Unnamed Route')}
                Location: {selected_route.get('location', 'Unknown')}
                Distance: {selected_route.get('distance', 0)} km
                Difficulty: {selected_route.get('difficulty', 'Not specified')}
                Terrain: {selected_route.get('terrain', 'Not specified')}

                Route description:
                {selected_route.get('description', 'No description available')}

                Format your response in clear sections with descriptive headers.
                Include a summary safety scorecard at the beginning with ratings for different safety aspects.
                """

                # Call the API with progress indication
                success, response = self.api.call_gemini_api(prompt, progress_message="🛡️ Assessing route safety")

                if success:
                    # Display the safety assessment
                    self.cli.clear_screen()
                    self.cli.display_header()

                    if self.cli.has_rich:
                        from rich.markdown import Markdown
                        from rich.panel import Panel
                        from rich.console import Console

                        console = Console()
                        console.print(Panel(
                            f"[bold]Safety Assessment: {selected_route.get('name', 'Unnamed Route')}[/bold]",
                            border_style="blue",
                            padding=(1, 2)
                        ))

                        safety_markdown = Markdown(str(response))
                        console.print(safety_markdown)
                    else:
                        print(f"\n=== Safety Assessment: {selected_route.get('name', 'Unnamed Route')} ===\n")
                        print(response)
                else:
                    # Display error
                    self.cli.display_message(f"Failed to assess route safety: {response}", "Assessment Failed", "error")
            else:
                self.cli.display_message("Invalid selection", "Error", "error")
        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")

        input("\nPress Enter to continue...")

    def compare_routes(self, username: str) -> None:
        """Compare two saved routes and highlight differences.

        Args:
            username: Username of the current user
        """
        self.cli.clear_screen()
        self.cli.display_header()

        # Get user's saved routes
        routes = self.routes.get_user_routes(username)

        if len(routes) < 2:
            self.cli.display_message(
                "You need at least two saved routes to use the comparison tool.",
                "Not Enough Routes",
                "warning"
            )
            input("\nPress Enter to continue...")
            return

        # Check if the API is available
        if not self.api.is_available():
            error_message = self.api.get_error()

            # Check if the error is due to missing package
            if error_message == "Package not installed":
                # Import dependency manager
                import core.dependency.dependency_manager as dependency_manager

                self.cli.display_message(
                    "Route comparison requires the Google Generative AI package which is not installed.",
                    "Package Required",
                    "warning"
                )

                # Ask user if they want to install the package
                install = input("\nWould you like to install the required package now? (y/n): ")
                if install.lower() == 'y':
                    self.cli.display_message("Installing Google Generative AI package...", "Installing", "info")

                    # Install the package
                    success = dependency_manager.ensure_package('google-generativeai', silent=False)

                    if success:
                        self.cli.display_message(
                            "Package installed successfully! Initializing API...",
                            "Success",
                            "success"
                        )

                        # Reinitialize the API
                        self.api._initialize_gemini()

                        # Check if initialization was successful
                        if self.api.is_available():
                            self.cli.display_message(
                                "API initialized successfully! You can now compare routes.",
                                "API Ready",
                                "success"
                            )
                            input("\nPress Enter to continue...")
                            # Restart the function to continue with route comparison
                            self.compare_routes(username)
                            return
                        else:
                            # API still not available, might be missing API key
                            self.cli.display_message(
                                f"Package installed but API initialization failed: {self.api.get_error()}",
                                "API Not Available",
                                "error"
                            )
                    else:
                        self.cli.display_message(
                            "Failed to install the required package. Please install it manually with: pip install google-generativeai",
                            "Installation Failed",
                            "error"
                        )
                input("\nPress Enter to continue...")
                return
            else:
                # Other API error
                self.cli.display_message(
                    f"Route comparison requires the Gemini API which is currently unavailable.\n\nError: {error_message}",
                    "API Not Available",
                    "error"
                )
                input("\nPress Enter to continue...")
                return

        # Display routes for selection
        self.cli.display_message("Select the first route to compare", "Route Comparison", "info")
        self.cli.display_routes_table(routes)

        # Get first route selection
        print("\nEnter the number of the first route (1-{}, or 0 to cancel): ".format(len(routes)), end="")
        try:
            index1 = int(input()) - 1
            if index1 == -1:
                return
            if 0 <= index1 < len(routes):
                route1 = routes[index1]

                # Display routes for second selection
                self.cli.clear_screen()
                self.cli.display_header()
                self.cli.display_message(f"First route selected: {route1.get('name')}", "Route Comparison", "info")
                self.cli.display_message("Now select the second route to compare", "Route Comparison", "info")
                self.cli.display_routes_table(routes)

                # Get second route selection
                print("\nEnter the number of the second route (1-{}, or 0 to cancel): ".format(len(routes)), end="")
                try:
                    index2 = int(input()) - 1
                    if index2 == -1:
                        return
                    if 0 <= index2 < len(routes) and index1 != index2:
                        route2 = routes[index2]

                        # Show loading message
                        self.cli.display_message(
                            f"Comparing routes '{route1.get('name')}' and '{route2.get('name')}'. This may take a moment...",
                            "Comparing",
                            "info"
                        )

                        # Prepare prompt for Gemini
                        prompt = f"""
                        Compare these two cycling routes and provide a detailed comparison analysis.

                        ROUTE 1:
                        Name: {route1.get('name', 'Unnamed Route')}
                        Location: {route1.get('location', 'Unknown')}
                        Distance: {route1.get('distance', 0)} km
                        Difficulty: {route1.get('difficulty', 'Not specified')}
                        Terrain: {route1.get('terrain', 'Not specified')}
                        Description: {route1.get('description', 'No description available')}

                        ROUTE 2:
                        Name: {route2.get('name', 'Unnamed Route')}
                        Location: {route2.get('location', 'Unknown')}
                        Distance: {route2.get('distance', 0)} km
                        Difficulty: {route2.get('difficulty', 'Not specified')}
                        Terrain: {route2.get('terrain', 'Not specified')}
                        Description: {route2.get('description', 'No description available')}

                        Please provide a comprehensive comparison including:
                        1. Side-by-side comparison of key metrics (distance, difficulty, terrain, etc.)
                        2. Strengths and weaknesses of each route
                        3. Suitability for different types of cyclists
                        4. Scenic value comparison
                        5. Safety comparison
                        6. Training value comparison
                        7. Seasonal considerations
                        8. Recommendation on which route is better for different purposes

                        Format your response in clear sections with descriptive headers.
                        Include a comparison table at the beginning summarizing the key differences.
                        """

                        # Call the API with progress indication
                        success, response = self.api.call_gemini_api(prompt, progress_message="🔍 Comparing routes")

                        if success:
                            # Display the comparison
                            self.cli.clear_screen()
                            self.cli.display_header()

                            if self.cli.has_rich:
                                from rich.markdown import Markdown
                                from rich.panel import Panel
                                from rich.console import Console

                                console = Console()
                                console.print(Panel(
                                    f"[bold]Route Comparison: {route1.get('name', 'Route 1')} vs {route2.get('name', 'Route 2')}[/bold]",
                                    border_style="magenta",
                                    padding=(1, 2)
                                ))

                                comparison_markdown = Markdown(str(response))
                                console.print(comparison_markdown)
                            else:
                                print(f"\n=== Route Comparison: {route1.get('name', 'Route 1')} vs {route2.get('name', 'Route 2')} ===\n")
                                print(response)
                        else:
                            # Display error
                            self.cli.display_message(f"Failed to compare routes: {response}", "Comparison Failed", "error")
                    elif index1 == index2:
                        self.cli.display_message("You selected the same route twice. Please select two different routes.", "Error", "error")
                    else:
                        self.cli.display_message("Invalid selection", "Error", "error")
                except ValueError:
                    self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")
            else:
                self.cli.display_message("Invalid selection", "Error", "error")
        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")

        input("\nPress Enter to continue...")

    def generate_alternative_routes(self, username: str) -> None:
        """Generate alternative route options based on an existing route.

        This feature allows users to see multiple route variations for the same
        location with different characteristics such as more scenic routes,
        safer routes, faster routes, etc.

        Args:
            username: Username of the current user
        """
        self.cli.clear_screen()
        self.cli.display_header()

        # Make sure the API is available
        if not self.api.is_available():
            error_message = self.api.get_error()

            # Check if the error is due to missing package
            if error_message == "Package not installed":
                # Import dependency manager
                import core.dependency.dependency_manager as dependency_manager

                self.cli.display_message(
                    "Alternative routes require the Google Generative AI package which is not installed.",
                    "Package Required",
                    "warning"
                )

                # Ask user if they want to install the package
                install = input("\nWould you like to install the required package now? (y/n): ")
                if install.lower() == 'y':
                    self.cli.display_message("Installing Google Generative AI package...", "Installing", "info")

                    # Install the package
                    success = dependency_manager.ensure_package('google-generativeai', silent=False)

                    if success:
                        self.cli.display_message(
                            "Package installed successfully! Initializing API...",
                            "Success",
                            "success"
                        )

                        # Reinitialize the API
                        self.api._initialize_gemini()

                        # Check if initialization was successful
                        if self.api.is_available():
                            self.cli.display_message(
                                "API initialized successfully! You can now generate alternative routes.",
                                "API Ready",
                                "success"
                            )
                            input("\nPress Enter to continue...")
                            # Restart the function to continue with route generation
                            self.generate_alternative_routes(username)
                            return
                        else:
                            # API still not available, might be missing API key
                            self.cli.display_message(
                                f"Package installed but API initialization failed: {self.api.get_error()}",
                                "API Not Available",
                                "error"
                            )
                    else:
                        self.cli.display_message(
                            "Failed to install the required package. Please install it manually with: pip install google-generativeai",
                            "Installation Failed",
                            "error"
                        )
                input("\nPress Enter to continue...")
                return
            else:
                # Other API error
                self.cli.display_message(
                    f"Alternative routes require the Gemini API which is currently unavailable.\n\nError: {error_message}",
                    "API Not Available",
                    "error"
                )
                input("\nPress Enter to continue...")
                return

        # Get user preferences
        preferences = self.routes.get_user_preferences(username)

        # Ask for location
        self.cli.display_message("Generate multiple route options for your cycling adventure!", "Alternative Routes", "info")

        print("\nWhere would you like to cycle? (city, area, or region)")
        location = input("> ").strip()

        if not location:
            self.cli.display_message("Location cannot be empty. Returning to menu.", "Error", "error")
            input("\nPress Enter to continue...")
            return

        # Ask which priorities to include
        print("\nSelect route priorities to generate (separate multiple choices with commas):")
        print("1. Scenic - Emphasizes beautiful views and landscapes")
        print("2. Quick - Focuses on efficient, direct routes")
        print("3. Safe - Prioritizes cyclist safety with bike lanes and low traffic")
        print("4. Family - Designed for cycling with children")
        print("5. Challenging - For more experienced cyclists seeking a workout")
        print("\nDefault: 1,2,3 (Scenic, Quick, Safe)")

        priority_input = input("> ").strip()

        # Process priority selection
        available_priorities = ['scenic', 'quick', 'safe', 'family', 'challenging']
        selected_priorities = []

        if priority_input:
            try:
                # Handle comma-separated numbers
                selections = [int(x.strip()) for x in priority_input.split(',')]
                for selection in selections:
                    if 1 <= selection <= len(available_priorities):
                        selected_priorities.append(available_priorities[selection-1])
            except ValueError:
                # Handle direct priority names
                for p in priority_input.lower().split(','):
                    p = p.strip()
                    if p in available_priorities:
                        selected_priorities.append(p)

        # Use default if nothing valid was selected
        if not selected_priorities:
            selected_priorities = ['scenic', 'quick', 'safe']

        # Show generating message with rich formatting
        if self.cli.has_rich:
            try:
                from rich.console import Console
                from rich.panel import Panel
                from rich.progress import Progress, SpinnerColumn, TextColumn
                from rich import print as rich_print

                console = Console()

                # Display generating message
                console.print(Panel(
                    f"[bold]Generating alternative routes for {location} with the following priorities:[/bold]\n\n" +
                    "\n".join([f"[green]• {priority.title()}[/green]" for priority in selected_priorities]) +
                    "\n\n[italic]This may take a minute as we craft multiple personalized routes...[/italic]",
                    title="[bold white on blue]🔄 Generating Routes[/bold white on blue]",
                    border_style="blue",
                    padding=(1, 2)
                ))

                # Visual progress bar while generating routes
                from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

                with Progress(
                    TextColumn("[bold blue]Generating alternative routes[/bold blue]"),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    console=console,
                    transient=True
                ) as progress:
                    # Create a task for the overall progress
                    total_routes = len(selected_priorities)
                    task = progress.add_task("Generating routes", total=total_routes)

                    # Call API to generate alternative routes (the API will handle individual route progress)
                    success, routes_data = self.api.generate_alternative_routes(location, preferences, selected_priorities)

                    # Complete the progress bar
                    progress.update(task, completed=total_routes)
            except ImportError:
                # Fallback to basic display if rich fails
                print("\nGenerating alternative routes...")
                success, routes_data = self.api.generate_alternative_routes(location, preferences, selected_priorities)
        else:
            # Basic ASCII version
            print("\n===================================")
            print("🔄 GENERATING ALTERNATIVE ROUTES 🔄")
            print("===================================")
            print(f"\nCreating multiple route options for {location} with priorities:")
            for priority in selected_priorities:
                print(f"• {priority.title()}")
            print("\nPlease wait, this may take a minute...")

            # Call API to generate alternative routes
            success, routes_data = self.api.generate_alternative_routes(location, preferences, selected_priorities)

        # Handle results with robust error handling
        if not success:
            # Ensure routes_data is properly processed before string interpolation
            try:
                # Make sure routes_data is a dictionary with an 'error' key
                if isinstance(routes_data, dict) and 'error' in routes_data:
                    error_message = str(routes_data.get('error', 'Unknown error'))
                elif isinstance(routes_data, str):
                    error_message = routes_data
                elif isinstance(routes_data, bool):
                    # Handle the case where routes_data is a boolean
                    error_message = "Failed to generate routes (boolean value returned)"
                    logger.error(f"Unexpected boolean value in routes_data: {routes_data}")
                else:
                    error_message = f"Unknown error (type: {type(routes_data).__name__})"

                # Use safe string conversion for display
                safe_error_message = str(error_message)
                self.cli.display_message(
                    f"Failed to generate alternative routes: {safe_error_message}",
                    "Generation Failed",
                    "error"
                )
            except Exception as e:
                # Absolute fallback if anything goes wrong in error handling
                logger.error(f"Error while displaying route generation error: {str(e)}")
                print("\nFailed to generate alternative routes due to an unexpected error.")

            input("\nPress Enter to continue...")
            return

        # Display alternative routes for comparison
        if isinstance(routes_data, list):
            self._display_alternative_routes(username, routes_data)
        else:
            # This shouldn't happen if success is True, but handle it just in case
            self.cli.display_message("Unexpected response format from route generation.", "Error", "error")
            input("\nPress Enter to continue...")
            return

    def _display_alternative_routes(self, username: str, routes: List[Dict[str, Any]]) -> None:
        """Display alternative routes for comparison and allow saving favorites.

        Args:
            username: Username of the current user
            routes: List of route dictionaries
        """
        self.cli.clear_screen()
        self.cli.display_header()

        if not routes:
            self.cli.display_message("No alternative routes were generated.", "No Routes", "warning")
            input("\nPress Enter to continue...")
            return

        # Display route comparison UI
        if self.cli.has_rich:
            try:
                from rich.console import Console
                from rich.panel import Panel
                from rich.table import Table
                from rich.text import Text
                from rich import print as rich_print

                console = Console()

                # Create a header
                console.print(Panel(
                    "[bold]Compare these alternative routes and choose your favorite![/bold]",
                    title="[bold white on green]🚲 Alternative Routes Comparison 🚲[/bold white on green]",
                    border_style="green",
                    padding=(1, 2)
                ))

                # Create comparison table
                table = Table(title="Route Comparison")

                # Add columns
                table.add_column("#", style="dim")
                table.add_column("Name", style="bold cyan")
                table.add_column("Priority", style="bold yellow")
                table.add_column("Distance", style="bold green")
                table.add_column("Difficulty", style="bold red")
                table.add_column("Terrain", style="bold blue")

                # Add rows
                for i, route in enumerate(routes):
                    # Format the distance with km
                    distance = f"{route.get('distance', 0)} km"

                    table.add_row(
                        str(i + 1),
                        route.get("name", "Unnamed Route"),
                        route.get("priority", "balanced").title(),
                        distance,
                        route.get("difficulty", "").title(),
                        route.get("terrain", "").title()
                    )

                console.print(table)

                # Show detailed view options
                console.print(Panel(
                    "[bold]Options:[/bold]\n\n"
                    "[yellow]V[/yellow] - View detailed route information\n"
                    "[green]S[/green] - Save your favorite route\n"
                    "[blue]C[/blue] - Compare elevation profiles\n"
                    "[red]X[/red] - Return to menu",
                    title="[bold white on blue]🛠️ Actions[/bold white on blue]",
                    border_style="blue",
                    padding=(1, 2)
                ))
            except ImportError:
                # Fallback to basic table
                self._display_alternative_routes_basic(routes)
        else:
            # Basic ASCII version
            self._display_alternative_routes_basic(routes)

        # Handle user interaction
        self._handle_alternative_routes_selection(username, routes)

    def _display_alternative_routes_basic(self, routes: List[Dict[str, Any]]) -> None:
        """Display alternative routes in a basic ASCII format.

        Args:
            routes: List of route dictionaries
        """
        print("\n===================================")
        print("🚲 ALTERNATIVE ROUTES COMPARISON 🚲")
        print("===================================")

        print(f"\n{'#':<3} {'Name':<35} {'Priority':<12} {'Distance':<12} {'Difficulty':<15} {'Terrain':<15}")
        print("-" * 100)

        for i, route in enumerate(routes):
            # Format the distance with km
            distance = f"{route.get('distance', 0)} km"

            print(f"{i+1:<3} {route.get('name', 'Unnamed Route'):<35} {route.get('priority', 'balanced').title():<12} "
                  f"{distance:<12} {route.get('difficulty', '').title():<15} {route.get('terrain', '').title():<15}")

        print("\nOptions:")
        print("V - View detailed route information")
        print("S - Save your favorite route")
        print("C - Compare elevation profiles")
        print("X - Return to menu")

    def _handle_alternative_routes_selection(self, username: str, routes: List[Dict[str, Any]]) -> None:
        """Handle user interaction with alternative routes.

        Args:
            username: Username of the current user
            routes: List of route dictionaries
        """
        while True:
            choice = input("\nEnter your choice: ").lower().strip()

            if choice == 'x':
                # Return to menu
                return
            elif choice == 'v':
                # View detailed route
                self._view_alternative_route_details(routes)
            elif choice == 's':
                # Save favorite route
                self._save_favorite_route(username, routes)
            elif choice == 'c':
                # Compare elevation profiles
                self._compare_elevation_profiles(routes)
            else:
                self.cli.display_message("Invalid choice. Please try again.", "Error", "error")

    def _view_alternative_route_details(self, routes: List[Dict[str, Any]]) -> None:
        """View detailed information for a selected alternative route.

        Args:
            routes: List of route dictionaries
        """
        # Ask for route number
        try:
            route_num = int(input("\nEnter route number to view: "))
            if route_num < 1 or route_num > len(routes):
                self.cli.display_message("Invalid route number.", "Error", "error")
                return

            # Get selected route
            route = routes[route_num - 1]

            # Display route details
            self.cli.clear_screen()
            self.cli.display_route(route)
            input("\nPress Enter to return to route comparison...")

            # Redisplay the comparison after viewing details
            self.cli.clear_screen()
            self.cli.display_header()
            self._display_alternative_routes_basic(routes) if not self.cli.has_rich else None

        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")

    def _save_favorite_route(self, username: str, routes: List[Dict[str, Any]]) -> None:
        """Save a favorite route from the alternatives.

        Args:
            username: Username of the current user
            routes: List of route dictionaries
        """
        # Ask for route number
        try:
            route_num = int(input("\nEnter route number to save: "))
            if route_num < 1 or route_num > len(routes):
                self.cli.display_message("Invalid route number.", "Error", "error")
                return

            # Get selected route
            route = routes[route_num - 1]

            # Add a note that this was an alternative route
            if 'notes' not in route:
                route['notes'] = ""
            route['notes'] += f"Alternative {route.get('priority', 'balanced')} route generated on {time.strftime('%Y-%m-%d')}."

            # Save the route
            success = self.routes.save_route(username, route)

            if success:
                self.cli.display_message(f"Route '{route.get('name')}' saved successfully!", "Success", "success")
            else:
                self.cli.display_message("Failed to save route.", "Error", "error")

        except ValueError:
            self.cli.display_message("Invalid input. Please enter a number.", "Error", "error")

    def _compare_elevation_profiles(self, routes: List[Dict[str, Any]]) -> None:
        """Display a comparison of elevation profiles for all routes.

        Args:
            routes: List of route dictionaries
        """
        self.cli.clear_screen()
        self.cli.display_header()

        # Extract elevation profile descriptions from routes
        elevation_data = []
        for i, route in enumerate(routes):
            # Extract elevation profile from the route description or use a default message
            # Since we don't have actual elevation data, we'll use the route descriptions to simulate this
            priority = route.get('priority', 'balanced')

            # Simulated elevation profiles based on route priority
            if priority == 'scenic':
                profile = "Moderate hills with some climbs to viewing points"
                elevation = "Medium"
            elif priority == 'quick':
                profile = "Relatively flat with minimal elevation changes"
                elevation = "Low"
            elif priority == 'safe':
                profile = "Gentle slopes on dedicated paths"
                elevation = "Low-Medium"
            elif priority == 'family':
                profile = "Very flat and easy terrain for all ages"
                elevation = "Very Low"
            elif priority == 'challenging':
                profile = "Significant climbs and technical descents"
                elevation = "High"
            else:
                profile = "Mixed terrain with some hills"
                elevation = "Medium"

            elevation_data.append({
                "index": i + 1,
                "name": route.get('name', f"Route {i+1}"),
                "profile": profile,
                "elevation": elevation,
                "priority": priority
            })

        # Display the comparison using rich UI if available
        if self.cli.has_rich:
            try:
                from rich.console import Console
                from rich.panel import Panel
                from rich.table import Table
                from rich import print as rich_print

                console = Console()

                # Create a header
                console.print(Panel(
                    "[bold]Compare the elevation profiles of your alternative routes[/bold]",
                    title="[bold white on cyan]⛰️ Elevation Profile Comparison ⛰️[/bold white on cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                ))

                # Create table for elevation data
                table = Table(title="Elevation Profiles")

                # Add columns
                table.add_column("#", style="dim")
                table.add_column("Route Name", style="bold cyan")
                table.add_column("Priority", style="bold yellow")
                table.add_column("Elevation", style="bold red")
                table.add_column("Description", style="bold green")

                # Add rows
                for data in elevation_data:
                    table.add_row(
                        str(data["index"]),
                        data["name"],
                        data["priority"].title(),
                        data["elevation"],
                        data["profile"]
                    )

                console.print(table)

                # Show a visualization representation with ASCII art
                console.print(Panel(
                    "[bold cyan]Elevation Visualization:[/bold cyan]\n\n"
                    "Route 1: " + self._get_elevation_ascii(elevation_data[0]["priority"]) + "\n"
                    "Route 2: " + self._get_elevation_ascii(elevation_data[1]["priority"]) + "\n" +
                    (f"Route 3: {self._get_elevation_ascii(elevation_data[2]['priority'])}\n" if len(elevation_data) > 2 else ""),
                    title="[bold white on blue]Visualization[/bold white on blue]",
                    border_style="blue",
                    padding=(1, 2)
                ))
            except (ImportError, IndexError):
                # Fallback to basic display
                self._display_elevation_profiles_basic(elevation_data)
        else:
            # Basic ASCII version
            self._display_elevation_profiles_basic(elevation_data)

        input("\nPress Enter to return to route comparison...")

        # Redisplay the comparison after viewing elevation profiles
        self.cli.clear_screen()
        self.cli.display_header()
        self._display_alternative_routes_basic(routes) if not self.cli.has_rich else None

    def _display_elevation_profiles_basic(self, elevation_data: List[Dict[str, Any]]) -> None:
        """Display elevation profiles in a basic ASCII format.

        Args:
            elevation_data: List of dictionaries with elevation information
        """
        print("\n===================================")
        print("⛰️ ELEVATION PROFILE COMPARISON ⛰️")
        print("===================================")

        print(f"\n{'#':<3} {'Route Name':<35} {'Priority':<12} {'Elevation':<12} {'Description':<40}")
        print("-" * 100)

        for data in elevation_data:
            print(f"{data['index']:<3} {data['name']:<35} {data['priority'].title():<12} "
                  f"{data['elevation']:<12} {data['profile']:<40}")

        print("\nElevation Visualization:")
        for data in elevation_data:
            print(f"Route {data['index']}: {self._get_elevation_ascii(data['priority'])}")

    def _get_elevation_ascii(self, priority: str) -> str:
        """Get ASCII art representation of elevation profile based on route priority.

        Args:
            priority: The route priority (scenic, quick, safe, etc.)

        Returns:
            ASCII art string representing the elevation profile
        """
        if priority == 'scenic':
            return "    /\\      /\\       "
        elif priority == 'quick':
            return "___/--\\___/--\\______"
        elif priority == 'safe':
            return "___/---\\___/---\\____"
        elif priority == 'family':
            return "_____/-\\______/-\\____"
        elif priority == 'challenging':
            return "/\\_/\\__/\\___/\\___"
        else:
            return "___/--\\___/---\\____"


def run_ai_route_planner(user_manager_instance=None, sheets_manager_instance=None):
    """
    Run the AI route planner as a standalone module.

    Args:
        user_manager_instance: Optional user manager instance
        sheets_manager_instance: Optional sheets manager instance
    """
    route_planner = AIRoutePlanner(user_manager_instance, sheets_manager_instance)
    route_planner.run_ai_route_planner()
