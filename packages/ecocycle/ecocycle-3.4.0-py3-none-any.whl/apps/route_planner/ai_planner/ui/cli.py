"""
EcoCycle - AI Route Planner CLI Module
Provides the command line interface for the AI Route Planner
"""
import logging
import sys
from typing import Dict, List, Any, Optional, Callable

# Configure logging
logger = logging.getLogger(__name__)

# --- Rich Integration ---
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table
    from rich.rule import Rule
    from rich import print as rich_print

    # Create a console object for rich printing
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None
# -----------------------


class RoutePlannerCLI:
    """Command Line Interface for the AI Route Planner"""

    def __init__(self):
        """Initialize the CLI interface"""
        self.has_rich = HAS_RICH
        self.console = console if HAS_RICH else None

    def clear_screen(self) -> None:
        """Clear the terminal screen"""
        # Import necessary modules here to avoid circular imports
        try:
            # Try application-level import first
            from utils import ascii_art
        except ImportError:
            try:
                # Try absolute import
                from apps.route_planner.utils import ascii_art
            except ImportError:
                # Fallback to direct implementation
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                return

        ascii_art.clear_screen()

    def display_header(self) -> None:
        """Display the application header"""
        # Import necessary modules here to avoid circular imports
        try:
            # Try application-level import first
            from utils import ascii_art
        except ImportError:
            try:
                # Try absolute import
                from apps.route_planner.utils import ascii_art
            except ImportError:
                # Fallback to simple implementation
                print("\n===================================")
                print("  EcoCycle - AI Route Planner")
                print("===================================")
                return

        ascii_art.display_header()

    def display_main_menu(self) -> None:
        """Display the main menu"""
        self.clear_screen()
        self.display_header()

        # Display AI Route Planner section header with enhanced UI
        if self.has_rich:
            # Main header with enhanced styling
            self.console.print(Panel(
                "[bold]Get personalized cycling route recommendations powered by Google's Gemini AI.[/bold]",
                title="[bold white on cyan]🚲 AI-Powered Cycling Route Planner 🚲[/bold white on cyan]",
                border_style="cyan",
                padding=(1, 2),
                expand=False,
                highlight=True
            ))

            # Display menu options with icons and category-based colors
            self.console.print(Panel(
                """
[bold white on blue]🧭 AI Route Planner Menu 🧭[/bold white on blue]

[bold]Route Planning:[/bold]
  [bold green]1. 🗺️  Generate a new route recommendation[/bold green]
  [bold green]2. 🔄 Generate alternative routes[/bold green]
  [bold green]3. 📋 View and manage saved routes[/bold green]

[bold]Analysis & Tools:[/bold]
  [bold cyan]4. 📊 Get detailed route analysis[/bold cyan]
  [bold cyan]5. 🛡️  Route safety assessment[/bold cyan]
  [bold cyan]6. 📈 Route comparison tool[/bold cyan]

[bold]Settings & System:[/bold]
  [bold magenta]7. ⚙️  Update your cycling preferences[/bold magenta]
  [bold yellow]8. 🏠 Return to main menu[/bold yellow]
  [bold red]0. ❌ Exit Program[/bold red]
                """,
                border_style="blue",
                padding=(1, 2),
                expand=False,
                highlight=True
            ))

            # Footer with tip
            self.console.print(Panel(
                "[italic]Tip: Route safety assessment provides real-time hazard information based on your location.[/italic]",
                border_style="dim blue",
                padding=(0, 1),
                expand=False
            ))

            self.console.print("\n[bold white on blue]Select an option (0-8):[/bold white on blue] ", end="")
        else:
            # Try to use ascii_art if available, otherwise fallback to basic formatting
            try:
                # Try application-level import first
                from utils import ascii_art

                ascii_art.display_section_header("AI-Powered Cycling Route Planner")
                print("\nGet personalized cycling route recommendations powered by Google's Gemini AI.")
                print("\n=== AI Route Planner Menu ===\n")
                print(f"  {ascii_art.Fore.YELLOW}0. Exit Program{ascii_art.Style.RESET_ALL}")
            except ImportError:
                try:
                    # Try absolute import
                    from apps.route_planner.utils import ascii_art

                    ascii_art.display_section_header("AI-Powered Cycling Route Planner")
                    print("\nGet personalized cycling route recommendations powered by Google's Gemini AI.")
                    print("\n=== AI Route Planner Menu ===\n")
                    print(f"  {ascii_art.Fore.YELLOW}0. Exit Program{ascii_art.Style.RESET_ALL}")
                except ImportError:
                    # Fallback to basic formatting
                    print("\n=== AI-Powered Cycling Route Planner ===\n")
                    print("Get personalized cycling route recommendations powered by Google's Gemini AI.")
                    print("\n=== AI Route Planner Menu ===\n")
                    print("  0. Exit Program")
            print("  1. Generate a new route recommendation")
            print("  2. Generate alternative routes")
            print("  3. View and manage saved routes")
            print("  4. Get detailed route analysis")
            print("  5. Route safety assessment")
            print("  6. Route comparison tool")
            print("  7. Update your cycling preferences")
            print("  8. Return to main menu")
            print("\nSelect an option (0-8): ", end="")

    def display_route(self, route: Dict[str, Any]) -> None:
        """Display a route recommendation

        Args:
            route: The route dictionary to display
        """
        if self.has_rich:
            route_markdown = Markdown(route.get("raw_response", route.get("description", "No route description available.")))

            # Use rich Panel for the header
            self.console.print(Panel(
                "Your Personalized Cycling Route",
                style="bold green",
                title_align="left"
            ))
            self.console.print(route_markdown)
        else:
            # Import necessary modules here to avoid circular imports
            import utils.ascii_art as ascii_art

            ascii_art.clear_screen()
            ascii_art.display_section_header(f"Route: {route.get('name', 'AI Generated Route')}")
            print(f"\nLocation: {route.get('location', 'Unknown')}")
            print(f"Distance: {route.get('distance', 0)} km")
            print(f"Difficulty: {route.get('difficulty', 'Not specified')}")
            print(f"Terrain: {route.get('terrain', 'Not specified')}")
            print("\nDescription:")
            print(route.get('description', 'No route description available.'))

    def display_message(self, message: Any, title: str = None, style: str = "info") -> None:
        """Display a message to the user

        Args:
            message: The message to display (will be converted to string)
            title: Optional title for the message
            style: The style of the message (info, success, error, warning)
        """
        # Ensure message is a string to prevent attribute errors
        try:
            # Convert message to string to prevent any template substitution issues
            if message is None:
                safe_message = "No message available"
            elif isinstance(message, bool):
                # Handle boolean values explicitly to avoid 'substitute' method errors
                safe_message = "True" if message else "False"
            elif isinstance(message, (dict, list)):
                # Handle complex objects by converting them to string representations
                import json
                try:
                    safe_message = json.dumps(message, indent=2)
                except:
                    safe_message = str(message)
            else:
                # Convert any other type to string
                safe_message = str(message)
        except Exception as e:
            # Last resort fallback
            import logging
            logging.getLogger(__name__).error(f"Error converting message to string: {e}")
            safe_message = "Error displaying message"
        if self.has_rich:
            # Map style to colors
            style_map = {
                "info": "blue",
                "success": "green",
                "error": "red",
                "warning": "yellow"
            }

            border_style = style_map.get(style, "blue")
            title_style = f"bold white on {border_style}"

            # Add icons based on style
            icons = {
                "info": "ℹ️",
                "success": "✅",
                "error": "⚠️",
                "warning": "⚠️"
            }

            icon = icons.get(style, "")
            title_text = f"{icon} {title if title else style.capitalize()}"

            # Prepare title for logging and Panel
            panel_render_title = f"[{title_style}]{title_text}[/{title_style}]"
            logger.debug(f"Panel args: content='{safe_message}', title='{panel_render_title}', border_style='{border_style}'")
            logger.debug(f"Panel arg types: content_type={type(safe_message)}, title_type={type(panel_render_title)}, border_style_type={type(border_style)}")

            self.console.print(Panel(
            safe_message,
            title=panel_render_title, # Use the prepared variable
            border_style=border_style,
            padding=(1, 2)
        ))
        else:
            # No imports needed for fallback implementation
            if title:
                print(f"\n=== {title} ===\n")
            else:
                print("\n")
            print(f"{safe_message}") # Use safe_message instead of raw message

    def display_routes_table(self, routes: List[Dict[str, Any]]) -> None:
        """Display a table of routes

        Args:
            routes: List of route dictionaries to display
        """
        if not routes:
            self.display_message("No saved routes found.", "Routes", "info")
            return

        if self.has_rich:
            table = Table(title="Your Saved Routes")

            # Add columns
            table.add_column("#", style="dim")
            table.add_column("Name", style="bold")
            table.add_column("Location")
            table.add_column("Distance (km)")
            table.add_column("Difficulty")
            table.add_column("Terrain")

            # Add rows
            for i, route in enumerate(routes):
                table.add_row(
                    str(i + 1),
                    route.get("name", "Unnamed Route"),
                    route.get("location", "Unknown"),
                    str(route.get("distance", "")),
                    route.get("difficulty", ""),
                    route.get("terrain", "")
                )

            self.console.print(table)
        else:
            # Try to use ascii_art if available, otherwise fallback to basic formatting
            try:
                # Try application-level import first
                from utils import ascii_art
                ascii_art.display_section_header("Your Saved Routes")
            except ImportError:
                try:
                    # Try absolute import
                    from apps.route_planner.utils import ascii_art
                    ascii_art.display_section_header("Your Saved Routes")
                except ImportError:
                    # Fallback to basic formatting
                    print("\n=== Your Saved Routes ===")

            # Create a simple ASCII table
            print(f"\n{'#':<3} {'Name':<30} {'Location':<20} {'Distance':<10} {'Difficulty':<15} {'Terrain':<15}")
            print("-" * 100)

            for i, route in enumerate(routes):
                print(f"{i+1:<3} {route.get('name', 'Unnamed Route'):<30} {route.get('location', 'Unknown'):<20} "
                      f"{route.get('distance', ''):<10} {route.get('difficulty', ''):<15} {route.get('terrain', ''):<15}")

    def display_coming_soon(self, feature_name: str) -> None:
        """Display a coming soon message for a feature

        Args:
            feature_name: The name of the feature that's coming soon
        """
        if self.has_rich:
            self.console.print(Panel(
                f"{feature_name} feature is coming soon!",
                title="[bold white on yellow]⚙️ Coming Soon[/bold white on yellow]",
                border_style="yellow",
                padding=(1, 2)
            ))
        else:
            print(f"\n{feature_name} feature is coming soon!")

        input("\nPress Enter to continue...")

    def exit_program(self) -> None:
        """Exit the program"""
        if self.has_rich:
            self.console.print(Panel(
                "Exiting program...",
                title="[bold white on red]👋 Goodbye[/bold white on red]",
                border_style="red",
                padding=(0, 1)
            ))
        else:
            print("\nExiting program...")
        sys.exit(0)