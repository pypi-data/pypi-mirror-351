"""
EcoCycle - AI Route Planner Module
Provides AI-powered cycling route recommendations using Google's Gemini API.

This is the main entry point for the AI Route Planner feature. This file has been
modularized for better code organization and maintenance.
"""
import os
import logging
import time
import importlib.util
import json
import datetime
import random
import sys
import warnings
from typing import Dict, List, Optional, Any, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)

# Check if our modular code structure is available
try:
    # First try absolute imports (suitable when running as a package)
    try:
        from apps.route_planner.ai_planner.planner import AIRoutePlanner as ModularAIRoutePlanner, run_ai_route_planner as modular_run
        from apps.route_planner.ai_planner.utils.constants import ROUTE_TYPES as MODULAR_ROUTE_TYPES, DIFFICULTY_LEVELS as MODULAR_DIFFICULTY_LEVELS
        MODULAR_CODE_AVAILABLE = True
        logger.info("Using modular AI Route Planner structure with absolute imports")
    except ImportError:
        # If that fails, try relative imports (suitable when imported as a local module)
        from ai_planner.planner import AIRoutePlanner as ModularAIRoutePlanner, run_ai_route_planner as modular_run
        from ai_planner.utils.constants import ROUTE_TYPES as MODULAR_ROUTE_TYPES, DIFFICULTY_LEVELS as MODULAR_DIFFICULTY_LEVELS
        MODULAR_CODE_AVAILABLE = True
        logger.info("Using modular AI Route Planner structure with relative imports")
except ImportError as e:
    MODULAR_CODE_AVAILABLE = False
    logger.warning(f"Modular AI Route Planner structure not found, using legacy code: {e}")

# Import configuration
from config.config import AI_ROUTES_FILE

# Import dependency_manager for ensuring packages
import core.dependency.dependency_manager
# Constants - These are kept here for backward compatibility
# The modular code uses these constants from ai_planner.utils.constants
DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced", "expert"]
TERRAIN_TYPES = ["flat", "hilly", "mixed", "mountain"]

# Sample points of interest categories
POI_CATEGORIES = [
    "historical_sites", "viewpoints", "parks", "cafes", "water_features",
    "nature_reserves", "cultural_sites", "rest_areas"
]

# API Retry Configuration
MAX_RETRY_ATTEMPTS = 3               # Maximum number of retry attempts for API calls
BASE_RETRY_DELAY = 2                 # Base delay in seconds between retries
MAX_RETRY_DELAY = 60                 # Maximum delay in seconds between retries
ROUTE_CACHE_EXPIRY = 60 * 60 * 24    # Route cache expiry time in seconds (24 hours)


# Main entry point function that will use modular code if available,
# otherwise fall back to legacy code
def run_ai_route_planner(user_manager_instance=None, sheets_manager_instance=None):
    """
    Run the AI route planner as a standalone module.

    Args:
        user_manager_instance: Optional user manager instance
        sheets_manager_instance: Optional sheets manager instance
    """
    if MODULAR_CODE_AVAILABLE:
        # Use the modular version of the code
        modular_run(user_manager_instance, sheets_manager_instance)
    else:
        # Use the legacy version (this is the original code)
        route_planner = AIRoutePlanner(user_manager_instance, sheets_manager_instance)
        route_planner.run_ai_route_planner()


# Legacy AIRoutePlanner class (kept for backwards compatibility)
class AIRoutePlanner:
    """AI-powered cycling route recommendation system."""

    def __init__(self, user_manager=None, sheets_manager=None):
        """Initialize the AI route planner."""
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager
        self.routes_file = AI_ROUTES_FILE
        self.saved_routes = self._load_routes()
        self.api_key = os.environ.get("GEMINI_API_KEY")

        # Initialize route cache
        self.route_cache = {}
        # Import the cache file path from config
        from config.config import CACHE_DIR
        self.cache_file_path = os.path.join(CACHE_DIR, 'ai_route_cache.json')
        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)

        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r") as cache_file:
                    self.route_cache = json.load(cache_file)
                # Clean expired cache entries
                self._clean_route_cache()
                logger.info(f"Loaded {len(self.route_cache)} cached routes")
            except Exception as e:
                logger.warning(f"Failed to load route cache: {e}")
                self.route_cache = {}

        # Try to ensure the google-generativeai package is installed if not available
        global GEMINI_AVAILABLE
        if not GEMINI_AVAILABLE:
            logger.info("Google Generative AI package not available, attempting to install it")
            print(f"{Fore.YELLOW}Installing required package for AI features...{Style.RESET_ALL}")
            success, _ = dependency_manager.ensure_package('google-generativeai', silent=False)
            if success:
                try:
                    import google.generativeai as genai
                    GEMINI_AVAILABLE = True
                    logger.info("Successfully installed google-generativeai package")
                    print(f"{Fore.GREEN}Successfully installed Google Generative AI package!{Style.RESET_ALL}")
                except ImportError as ie:
                    logger.warning(f"Failed to import google-generativeai even after installation attempt: {ie}")
                    print(f"{Fore.RED}Failed to import Google Generative AI package. AI features will be unavailable.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to install Google Generative AI package. AI features will use fallback mode.{Style.RESET_ALL}")

        # Initialize Gemini if available, with better error handling
        if GEMINI_AVAILABLE and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)

                # First check if the API is accessible by getting model list
                try:
                    models = genai.list_models()
                    supported_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                    logger.info(f"Available Gemini models: {supported_models}")

                    # Use the latest recommended model that's available
                    preferred_models = [
                        "models/gemini-2.0-flash-lite",
                    ]

                    self.default_model = None
                    for model in preferred_models:
                        if model in supported_models:
                            self.default_model = model
                            break

                    if not self.default_model:
                        logger.warning("No suitable Gemini model found. Using fallback.")
                        self.gemini_available = False
                    else:
                        # Set default generation config
                        self.generation_config = {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40,
                            "max_output_tokens": 2048,
                        }
                        self.gemini_available = True
                        logger.info(f"Gemini API initialized successfully using model {self.default_model}")
                except Exception as e:
                    logger.error(f"Error checking Gemini API models: {e}")
                    self.gemini_available = False
            except Exception as e:
                logger.error(f"Error initializing Gemini API: {e}")
                self.gemini_available = False
        else:
            # Store the specific reason for API unavailability for better error messages
            if not GEMINI_AVAILABLE:
                self.gemini_error = "Package not installed"
            elif not self.api_key:
                self.gemini_error = "API key not set"
            else:
                self.gemini_error = "Unknown error"

            self.gemini_available = False

    def _load_routes(self) -> Dict:
        """Load saved routes from file."""
        if os.path.exists(self.routes_file):
            try:
                with open(self.routes_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing routes file: {self.routes_file}")
                return {}
        return {}

    def _save_routes(self) -> bool:
        """Save routes to file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.routes_file), exist_ok=True)

        try:
            with open(self.routes_file, 'w') as f:
                json.dump(self.saved_routes, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving routes: {e}")

    def _clean_route_cache(self):
        """Remove expired entries from route cache."""
        current_time = time.time()
        expired_keys = []

        for key, entry in self.route_cache.items():
            if current_time - entry.get("timestamp", 0) > ROUTE_CACHE_EXPIRY:
                expired_keys.append(key)

        for key in expired_keys:
            del self.route_cache[key]

        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired route cache entries")

    def _save_route_cache(self):
        """Save route cache to file."""
        try:
            with open(self.cache_file_path, 'w') as f:
                json.dump(self.route_cache, f, indent=4)
            logger.debug(f"Route cache saved with {len(self.route_cache)} entries")
        except Exception as e:
            logger.error(f"Error saving route cache: {e}")

    def _get_cache_key(self, location, preferences):
        """Generate a cache key based on route parameters."""
        # Create a normalized representation of the request for cache keying with proper type handling
        try:
            # Ensure location is a string
            loc = str(location).lower() if location else ''

            # Handle preferred_difficulty - ensure it's a string
            preferred_difficulty = preferences.get('preferred_difficulty', '')
            if not isinstance(preferred_difficulty, str):
                preferred_difficulty = str(preferred_difficulty)

            # Handle preferred_terrain - ensure it's a string
            preferred_terrain = preferences.get('preferred_terrain', '')
            if not isinstance(preferred_terrain, str):
                preferred_terrain = str(preferred_terrain)

            # Handle route types - ensure it's a list and all items are strings
            route_types = preferences.get('preferred_route_types', [])
            if route_types is None:
                route_types = []
            elif not isinstance(route_types, list):
                route_types = [str(route_types)]

            # Handle points of interest - ensure it's a list and all items are strings
            poi = preferences.get('points_of_interest', [])
            if poi is None:
                poi = []
            elif not isinstance(poi, list):
                poi = [str(poi)]

            key_parts = [
                loc,
                str(preferences.get('preferred_distance', 0)),
                preferred_difficulty.lower(),
                preferred_terrain.lower(),
                ",".join(sorted([str(r).lower() for r in route_types])),
                ",".join(sorted([str(p).lower() for p in poi]))
            ]
            return "|".join(key_parts)
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            # Return a simple fallback cache key if there's an error
            return f"{str(location).lower() if location else 'unknown'}|error"

    def run_ai_route_planner(self) -> None:
        """Run the AI route planner interactive interface."""
        # Import necessary modules here to avoid circular imports
        import utils.ascii_art as ascii_art

        # Import Rich if available
        try:
            from rich.console import Console
            from rich.panel import Panel
            RICH_AVAILABLE = True
            console = Console()
        except ImportError:
            RICH_AVAILABLE = False

        if not self.user_manager or not self.user_manager.is_authenticated():
            print("You need to be logged in to use the AI Route Planner.")
            return

        username = self.user_manager.get_current_user().get('username')

        # Initialize user data if not present
        if username not in self.saved_routes:
            self.saved_routes[username] = {
                "preferences": {
                    "preferred_distance": 10,
                    "preferred_difficulty": "intermediate",
                    "preferred_terrain": "mixed",
                    "preferred_route_types": ["leisure", "nature"],
                    "points_of_interest": ["viewpoints", "cafes", "parks"]
                },
                "saved_routes": []
            }
            self._save_routes()

        while True:
            ascii_art.clear_screen()
            ascii_art.display_header()

            # Display AI Route Planner section header with enhanced UI
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
                print("  1. Generate a new route recommendation")
                print("  2. View and manage saved routes")
                print("  3. Update your cycling preferences")
                print("  4. Get detailed route analysis")
                print("  5. Generate alternative routes")
                print("  6. Route safety assessment")
                print("  7. Route comparison tool")
                print("  8. Return to main menu")
                print("\nSelect an option (0-8): ", end="")

            choice = input()

            if choice == '0':
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
            elif choice == '1':
                self.generate_route_recommendation(username)
            elif choice == '2':
                self.view_saved_routes(username)
            elif choice == '3':
                if RICH_AVAILABLE:
                    console.print(Panel(
                        "Update your cycling preferences feature is coming soon!",
                        title="[bold white on yellow]⚙️ Coming Soon[/bold white on yellow]",
                        border_style="yellow",
                        padding=(1, 2)))
                else:
                    print("\nUpdate your cycling preferences feature is coming soon!")
                input("\nPress Enter to continue...")
            elif choice == '4':
                if RICH_AVAILABLE:
                    console.print(Panel(
                        "Get detailed route analysis feature is coming soon!",
                        title="[bold white on yellow]📊 Coming Soon[/bold white on yellow]",
                        border_style="yellow",
                        padding=(1, 2)))
                else:
                    print("\nGet detailed route analysis feature is coming soon!")
                input("\nPress Enter to continue...")
            elif choice == '5':
                if RICH_AVAILABLE:
                    console.print(Panel(
                        "Generate alternative routes feature is coming soon!",
                        title="[bold white on yellow]🔄 Coming Soon[/bold white on yellow]",
                        border_style="yellow",
                        padding=(1, 2)))
                else:
                    print("\nGenerate alternative routes feature is coming soon!")
                input("\nPress Enter to continue...")
            elif choice == '6':
                self.assess_route_safety(username)
            elif choice == '7':
                if RICH_AVAILABLE:
                    console.print(Panel(
                        "Route comparison tool feature is coming soon!",
                        title="[bold white on yellow]📈 Coming Soon[/bold white on yellow]",
                        border_style="yellow",
                        padding=(1, 2)))
                else:
                    print("\nRoute comparison tool feature is coming soon!")
                input("\nPress Enter to continue...")
            elif choice == '8':
                break
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

    def generate_route_recommendation(self, username: str) -> None:
        """Generate a new AI-powered route recommendation."""
        import utils.ascii_art as ascii_art

        ascii_art.clear_screen()

        # Use Rich for better header formatting if available
        if HAS_RICH:
            try:
                console.print(Panel.fit(
                    "[bold green]Generate Your Personalized Cycling Route[/bold green]",
                    border_style="green",
                    padding=(1, 2),
                    title="EcoCycle",
                    title_align="left"
                ))
                console.print(Rule(style="green"))
            except Exception as e:
                # Fallback to ASCII art if Rich fails
                logger.warning(f"Error using Rich for header: {e}")
                ascii_art.display_section_header("Generate Route Recommendation")
        else:
            ascii_art.display_section_header("Generate Route Recommendation")

        def call_gemini_api(model, prompt, attempt=1):
            """Function to run the blocking call in a separate thread with retry logic."""
            try:
                return model.generate_content(prompt)
            except Exception as e:
                # Check if this is a rate limit error
                error_str = str(e)
                if "429" in error_str and "quota" in error_str.lower() and attempt < MAX_RETRY_ATTEMPTS:
                    # Calculate exponential backoff delay
                    delay = min(BASE_RETRY_DELAY * (2 ** (attempt - 1)), MAX_RETRY_DELAY)
                    logger.info(f"Rate limit hit, retrying in {delay} seconds (attempt {attempt}/{MAX_RETRY_ATTEMPTS})")
                    time.sleep(delay)
                    # Retry with incremented attempt counter
                    return call_gemini_api(model, prompt, attempt + 1)
                # Either not a rate limit error or we've exhausted retries
                return e

        if not self.gemini_available:
            print("\nThe Gemini API is not available.")

            # Check if it's because the package is missing
            if not GEMINI_AVAILABLE:
                print("The Google Generative AI package is required for AI-powered route recommendations.")
                install = input("Would you like to install the required package now? (y/n): ")
                if install.lower() == 'y':
                    success, _ = dependency_manager.ensure_package('google-generativeai', silent=False)
                    if success:
                        print("Successfully installed the required package!")
                        print("Please restart this function to use AI-powered route recommendations.")
                        input("\nPress Enter to continue...")
                        return
                    else:
                        print("Failed to install the required package.")
                        print("Please install it manually with: pip install google-generativeai")

            # Check if it's because the API key is missing
            if GEMINI_AVAILABLE and not self.api_key:
                print("The GEMINI_API_KEY environment variable is not set.")
                print("You'll need to create a Google AI Studio account and obtain an API key.")
                print("Then add it to your .env file as GEMINI_API_KEY=your_key_here")

            print("\nUsing fallback route generation instead.")
            self._fallback_route_generation(username)
            return

        # Get user preferences
        user_prefs = self.saved_routes[username]["preferences"]

        if HAS_RICH:
            try:
                # Display a welcome message
                console.print("\n[cyan]Generating a personalized cycling route just for you...[/cyan]")

                # Create a preference table with Rich
                table = Table(title="Your Cycling Preferences", show_header=True, header_style="bold cyan",
                             border_style="cyan", box=rich.box.ROUNDED)

                table.add_column("Preference", style="dim")
                table.add_column("Value", style="bold green")

                table.add_row("Distance", f"{user_prefs['preferred_distance']} km")
                table.add_row("Difficulty", user_prefs['preferred_difficulty'].title())
                table.add_row("Terrain", user_prefs['preferred_terrain'].title())
                table.add_row("Route Types", ", ".join([t.title() for t in user_prefs['preferred_route_types']]))
                table.add_row("Points of Interest", ", ".join([p.replace('_', ' ').title() for p in user_prefs['points_of_interest']]))

                console.print(table)
            except Exception as e:
                # Fall back to plain text
                logger.warning(f"Error using Rich for preferences display: {e}")
                print("\nGenerating a personalized cycling route recommendation...")
                print("\nYour current preferences:")
                print(f"• Preferred distance: {user_prefs['preferred_distance']} km")
                print(f"• Difficulty level: {user_prefs['preferred_difficulty']}")
                print(f"• Terrain type: {user_prefs['preferred_terrain']}")
                print(f"• Route types: {', '.join(user_prefs['preferred_route_types'])}")
                print(f"• Points of interest: {', '.join(user_prefs['points_of_interest'])}")
        else:
            print("\nGenerating a personalized cycling route recommendation...")
            print("\nYour current preferences:")
            print(f"• Preferred distance: {user_prefs['preferred_distance']} km")
            print(f"• Difficulty level: {user_prefs['preferred_difficulty']}")
            print(f"• Terrain type: {user_prefs['preferred_terrain']}")
            print(f"• Route types: {', '.join(user_prefs['preferred_route_types'])}")
            print(f"• Points of interest: {', '.join(user_prefs['points_of_interest'])}")

        # Ask for location with enhanced prompts and KeyboardInterrupt handling
        try:
            if HAS_RICH:
                try:
                    console.print("\n[bold blue]Where would you like to cycle?[/bold blue]")
                    location = console.input("[cyan]Enter your location (city or area): [/cyan]")
                except Exception as e:
                    logger.warning(f"Error using Rich for input: {e}")
                    location = input("\nEnter your location (city or area): ")
            else:
                location = input("\nEnter your location (city or area): ")
        except KeyboardInterrupt:
            print("\n")  # New line for better formatting
            print("Route planning cancelled by user.")
            return

        if not location:
            if HAS_RICH:
                try:
                    console.print("[bold red]Location is required. Please try again.[/bold red]")
                    console.input("\n[cyan]Press Enter to continue...[/cyan]")
                except Exception as e:
                    logger.warning(f"Error using Rich for error message: {e}")
                    print("Location is required. Please try again.")
                    input("\nPress Enter to continue...")
            else:
                print("Location is required. Please try again.")
                input("\nPress Enter to continue...")
            return

        # Ask for specific requirements for this route
        if HAS_RICH:
            try:
                console.print("\n[bold blue]Any specific requirements for this route?[/bold blue] [dim](optional)[/dim]")
                special_requirements = console.input("[cyan]Enter requirements (or press Enter to skip): [/cyan]")
            except Exception as e:
                logger.warning(f"Error using Rich for input: {e}")
                print("\nAny specific requirements for this route? (optional)")
                special_requirements = input("Enter any special requirements (or press Enter to skip): ")
        else:
            print("\nAny specific requirements for this route? (optional)")
            special_requirements = input("Enter any special requirements (or press Enter to skip): ")

        # Check cache first (only if no special requirements)
        cache_hit = False
        if not special_requirements:
            cache_key = self._get_cache_key(location, user_prefs)
            if cache_key in self.route_cache:
                cache_entry = self.route_cache[cache_key]
                # Verify the cache entry is still valid
                if time.time() - cache_entry.get("timestamp", 0) <= ROUTE_CACHE_EXPIRY:
                    logger.info(f"Route cache hit for {location} with preferences: {user_prefs}")
                    route_description = cache_entry["route_description"]
                    cache_hit = True

                if HAS_RICH:
                    try:
                        console.print(Panel(
                            "[green]A route matching your criteria has been found in the cache![/green]\n" +
                            "[cyan]This helps us reduce API calls and provide faster results.[/cyan]",
                            title="[bold green]Cache Hit![/bold green]",
                            border_style="green",
                            expand=False
                        ))
                    except Exception as e:
                        logger.warning(f"Error using Rich for cache hit message: {e}")
                        print("\nFound a previously generated route that matches your criteria!")
                else:
                    print("\nFound a previously generated route that matches your criteria!")

        # Get user cycling history if available
        user_history = ""
        if self.user_manager and not cache_hit:
            try:
                user_data = self.user_manager.get_current_user()
                if user_data and 'stats' in user_data:
                    stats = user_data['stats']
                    total_distance = stats.get('total_distance', 0)
                    total_trips = stats.get('total_trips', 0)

                    if total_trips > 0:
                        avg_distance = total_distance / total_trips
                        user_history = f"The user has logged {total_trips} cycling trips with a total distance of {total_distance} km. Their average trip is {avg_distance:.1f} km."
            except:
                pass

        # Prepare prompt for Gemini
        prompt = f"""
        Generate a detailed cycling route recommendation with the following requirements:

        Location: {location}
        Preferred distance: {user_prefs['preferred_distance']} km
        Difficulty level: {user_prefs['preferred_difficulty']}
        Terrain type: {user_prefs['preferred_terrain']}
        Route types: {', '.join(user_prefs['preferred_route_types'])}
        Points of interest to include: {', '.join(user_prefs['points_of_interest'])}
        Special requirements: {special_requirements}

        {user_history}

        Format the response as follows:
        1. A name for the route
        2. A one-paragraph summary of the route
        3. Starting point (be specific)
        4. Route description with turn-by-turn directions
        5. Key features along the route (3-5 points of interest)
        6. Difficulty assessment and why
        7. Safety considerations
        8. Best time to ride
        9. Estimated duration
        10. Elevation gain (in meters)
        11. Surface types (percentage of paved/unpaved)

        Structure the response in a clean, readable format with clear section headers.
        """

        try:
            # Skip API call if we got a cache hit
            if cache_hit:
                print("Using cached route data instead of making a new API call")
            else:
                # Set up the model with the dynamically detected model name
                model = genai.GenerativeModel(
                    model_name=self.default_model,  # Use the model we've confirmed is available
                    generation_config=self.generation_config
                )

                # --- Start spinner for API call ---
                response = None # Initialize response variable
                loading_desc = "💬 Generating route recommendation"

                with yaspin.yaspin(Spinners.dots, text=loading_desc, color="cyan") as spinner:
                    try:
                        # Make API request inside the yaspin context with retry logic
                        api_result = call_gemini_api(model, prompt)

                        # Check if the result is an exception or a valid response
                        if isinstance(api_result, Exception):
                            spinner.fail("💥 ")  # Mark as failure
                            raise api_result
                        else:
                            response = api_result
                            spinner.ok("✅ ")  # Mark as success
                    except Exception as api_error:
                        spinner.fail("💥 ")  # Mark as failure
                        logger.error(f"Gemini API call failed during '{loading_desc}': {api_error}")
                        # Re-raise the exception to be caught by the outer block
                        raise api_error

                # Check if response was successfully obtained
                if response is None:
                    raise RuntimeError("AI response was unexpectedly None after API call.")

                route_description = response.text

                # Cache the successful response if there were no special requirements
                if not special_requirements:
                    cache_key = self._get_cache_key(location, user_prefs)
                    self.route_cache[cache_key] = {
                        "route_description": route_description,
                        "timestamp": time.time(),
                        "location": location
                    }
                    self._save_route_cache()

            # Display the generated route with enhanced formatting
            ascii_art.clear_screen()

            if HAS_RICH:
                try:
                    # Create a visually appealing header
                    console.print(Panel(
                        "[bold green]Your Personalized Cycling Route[/bold green]\n" +
                        f"[cyan]Location: [bold]{location}[/bold][/cyan]",
                        border_style="green",
                        title="EcoCycle Route",
                        title_align="left"
                    ))

                    # Display route with markdown formatting in a panel
                    route_markdown = Markdown(route_description)
                    console.print(Panel.fit(
                        route_markdown,
                        border_style="green",
                        padding=(1, 2),
                        title="Route Details",
                        subtitle=f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}"
                    ))

                    # Ask user if they want to save the route with styled prompt
                    console.print("\n[bold blue]Would you like to save this route for future reference?[/bold blue]")
                    save = console.input("[cyan]Save route? (y/n): [/cyan]").lower()
                except Exception as e:
                    # Fallback to simpler formatting
                    logger.warning(f"Error using Rich for route display: {e}")
                    ascii_art.display_section_header("Your Personalized Cycling Route")
                    print(route_description)
                    save = input("\nWould you like to save this route? (y/n): ").lower()
            else:
                ascii_art.display_section_header("Your Personalized Cycling Route")
                print(route_description)
                save = input("\nWould you like to save this route? (y/n): ").lower()

            if save == 'y':
                # Enhanced route naming prompt
                if HAS_RICH:
                    try:
                        console.print("\n[bold blue]What would you like to name your route?[/bold blue]")
                        route_name = console.input("[cyan]Enter name (or press Enter for auto-name): [/cyan]")
                    except Exception as e:
                        logger.warning(f"Error using Rich for route naming: {e}")
                        route_name = input("Enter a name for this route (or press Enter to use AI-generated name): ")
                else:
                    route_name = input("Enter a name for this route (or press Enter to use AI-generated name): ")

                # If user didn't enter a name, extract it from the AI response
                if not route_name:
                    try:
                        # Try to extract the route name from the first line of the response
                        first_line = route_description.split('\n')[0]
                        if first_line and len(first_line) < 100:  # Reasonable length for a name
                            route_name = first_line.strip().replace('#', '').strip() # Remove markdown header syntax
                        else:
                            route_name = f"Route in {location} - {datetime.datetime.now().strftime('%Y-%m-%d')}"
                    except:
                        route_name = f"Route in {location} - {datetime.datetime.now().strftime('%Y-%m-%d')}"

                # Create route object
                new_route = {
                    "name": route_name,
                    "location": location,
                    "description": route_description,
                    "distance": user_prefs['preferred_distance'],
                    "difficulty": user_prefs['preferred_difficulty'],
                    "terrain": user_prefs['preferred_terrain'],
                    "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "ai_generated": True
                }

                # Add to saved routes
                self.saved_routes[username]["saved_routes"].append(new_route)
                self._save_routes()

                # Enhanced success message
                if HAS_RICH:
                    try:
                        console.print(Panel(
                            f"[bold green]Route '{route_name}' has been saved successfully![/bold green]\n" +
                            "[cyan]You can view or manage this route from the main menu.[/cyan]",
                            border_style="green",
                            title="✓ Success",
                            expand=False
                        ))
                    except Exception as e:
                        logger.warning(f"Error using Rich for success message: {e}")
                        ascii_art.display_success_message(f"Route '{route_name}' saved successfully!")
                else:
                    ascii_art.display_success_message(f"Route '{route_name}' saved successfully!")

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating route with Gemini: {e}")

            # Check if this is a rate limit error
            if "429" in error_str and "quota" in error_str.lower():
                if HAS_RICH:
                    try:
                        # Use rich formatting with error handling
                        console.print(Panel(
                            "You've reached the API rate limit for route generation.\n" +
                            "This typically happens if you've made too many requests in a short time.\n" +
                            "We'll use our offline route generator instead for now.\n\n" +
                            "The rate limit will reset automatically after some time.",
                            title="Rate Limit Reached",
                            border_style="yellow"
                        ))
                    except Exception as rich_error:
                        # Fallback to plain text if Rich fails
                        logger.warning(f"Error using Rich Panel for rate limit message: {rich_error}")
                        print("\n===== Rate Limit Reached =====")
                        print("You've reached the API rate limit for route generation.")
                        print("This typically happens if you've made too many requests in a short time.")
                        print("We'll use our offline route generator instead for now.")
                        print("The rate limit will reset automatically after some time.")
                        print("============================")
                else:
                    print("\n===== Rate Limit Reached =====")
                    print("You've reached the API rate limit for route generation.")
                    print("This typically happens if you've made too many requests in a short time.")
                    print("We'll use our offline route generator instead for now.")
                    print("The rate limit will reset automatically after some time.")
                    print("============================")
            else:
                # For other errors, just show the basic message
                print(f"\nError generating route: {e}")
                print("Using fallback route generation instead.")

            # Add a slight delay to let the user read the message
            time.sleep(1.5)

            # Switch to fallback generator
            self._fallback_route_generation(username)

        input("\nPress Enter to continue...")

        # Clean the route cache after we're done to avoid stale entries
        self._clean_route_cache()

    def _fallback_route_generation(self, username: str) -> None:
        """Generate a route recommendation using fallback method when AI is not available."""
        import utils.ascii_art as ascii_art

        if HAS_RICH:
            try:
                console.print(Panel(
                    "Generating route using our local route planner",
                    title="Offline Route Planner",
                    border_style="blue"
                ))
            except Exception as e:
                # Fallback if there's any issue with Rich
                logger.warning(f"Error using Rich Panel: {e}")
                ascii_art.display_section_header("Offline Route Planner")
                print("Generating route using our local route planner - no API connection needed")
        else:
            ascii_art.display_section_header("Offline Route Planner")
            print("Generating route using our local route planner - no API connection needed")

        user_prefs = self.saved_routes[username]["preferences"]

        # Ask for location
        if HAS_RICH:
            location = console.input("\n[blue]Enter your location (city or area):[/blue] ")
        else:
            location = input("\nEnter your location (city or area): ")

        if not location:
            if HAS_RICH:
                console.print("[red]Location is required. Please try again.[/red]")
            else:
                print("Location is required. Please try again.")
            return

        # Get route parameters with more detailed output
        distance = user_prefs['preferred_distance']
        difficulty = user_prefs['preferred_difficulty']
        terrain = user_prefs['preferred_terrain']
        route_types = user_prefs['preferred_route_types']
        poi_types = user_prefs['points_of_interest']

        # Show processing message
        if HAS_RICH:
            try:
                with console.status("[cyan]Building your personalized route...[/cyan]", spinner="dots"):
                    time.sleep(1.5)  # Add a slight delay to show the loading indicator
            except Exception as e:
                # Fallback if there's any issue with Rich
                logger.warning(f"Error using Rich status: {e}")
                with yaspin.yaspin(Spinners.dots, text="Building your personalized route...", color="cyan") as spinner:
                    time.sleep(1.5)
                    spinner.ok("✓")
        else:
            with yaspin.yaspin(Spinners.dots, text="Building your personalized route...", color="cyan") as spinner:
                time.sleep(1.5)  # Add a slight delay to show the loading indicator
                spinner.ok("✓")

        # Generate a route name
        route_name = f"{location} {random.choice(['Loop', 'Trail', 'Path', 'Greenway', 'Circuit'])}"

        # Generate a simple route description
        description = f"# {route_name}\n\n"
        description += f"## Summary\n"
        description += f"A {distance} km {difficulty} cycling route in {location} featuring {terrain} terrain. "
        description += f"This route is perfect for {', '.join(route_types)} riding and includes several points of interest.\n\n"

        description += f"## Starting Point\n"
        description += f"The route starts at the main square in {location}.\n\n"

        description += f"## Route Description\n"
        description += f"1. Begin at the main square and head north for 1 km\n"
        description += f"2. Turn right at the park entrance and follow the path for 2 km\n"
        description += f"3. At the intersection, turn left and continue for 1.5 km\n"
        description += f"4. Follow the riverside path for 3 km\n"
        description += f"5. Turn right at the bridge and head back towards the town center\n"
        description += f"6. Complete the loop by returning to the main square\n\n"

        description += f"## Key Features\n"
        for _ in range(3):
            poi = random.choice(poi_types)
            description += f"• {poi.replace('_', ' ').title()}: {random.choice(['Historic', 'Scenic', 'Popular', 'Hidden gem', 'Must-see'])} spot along the route\n"
        description += "\n"

        description += f"## Difficulty Assessment\n"
        if difficulty == "beginner":
            description += f"This is an easy route suitable for beginners with mostly flat terrain and minimal traffic.\n\n"
        elif difficulty == "intermediate":
            description += f"This moderate route has some hills and varied terrain but is manageable for regular cyclists.\n\n"
        elif difficulty == "advanced":
            description += f"This challenging route features significant climbs and technical sections suitable for experienced cyclists.\n\n"
        else:
            description += f"This expert route has steep climbs, technical descents, and requires advanced cycling skills and fitness.\n\n"

        description += f"## Safety Considerations\n"
        description += f"• Watch for traffic at the main road crossings\n"
        description += f"• Some sections may be slippery when wet\n"
        description += f"• Bring water and supplies as there are limited services along the route\n\n"

        description += f"## Best Time to Ride\n"
        description += f"Early morning or late afternoon to avoid peak temperatures and traffic.\n\n"

        # Calculate estimated duration based on difficulty
        if difficulty == "beginner":
            speed = 10  # km/h
        elif difficulty == "intermediate":
            speed = 15  # km/h
        elif difficulty == "advanced":
            speed = 20  # km/h
        else:  # expert
            speed = 25  # km/h

        duration = distance / speed
        hours = int(duration)
        minutes = int((duration - hours) * 60)

        description += f"## Estimated Duration\n"
        if hours > 0:
            description += f"{hours} hour{'s' if hours != 1 else ''} "
        description += f"{minutes} minutes\n\n"

        # Generate random elevation gain based on terrain and difficulty
        if terrain == "flat":
            elevation_multiplier = 5
        elif terrain == "mixed":
            elevation_multiplier = 15
        elif terrain == "hilly":
            elevation_multiplier = 30
        else:  # mountain
            elevation_multiplier = 50

        difficulty_multiplier = 1
        if difficulty == "intermediate":
            difficulty_multiplier = 1.5
        elif difficulty == "advanced":
            difficulty_multiplier = 2
        elif difficulty == "expert":
            difficulty_multiplier = 3

        elevation_gain = int(distance * elevation_multiplier * difficulty_multiplier)

        description += f"## Elevation Gain\n"
        description += f"{elevation_gain} meters\n\n"

        # Generate surface types
        if "nature" in route_types or "mountain" in terrain:
            paved = random.randint(30, 70)
        else:
            paved = random.randint(70, 100)

        description += f"## Surface Types\n"
        description += f"{paved}% paved, {100-paved}% unpaved\n"

        # Display the generated route
        ascii_art.clear_screen()
        ascii_art.display_section_header("Your Cycling Route (Fallback Generator)")

        print(description)

        # Ask user if they want to save the route
        save = input("\nWould you like to save this route? (y/n): ").lower()

        if save == 'y':
            custom_name = input("Enter a name for this route (or press Enter to use generated name): ")
            if custom_name:
                route_name = custom_name

            # Create route object
            new_route = {
                "name": route_name,
                "location": location,
                "description": description,
                "distance": distance,
                "difficulty": difficulty,
                "terrain": terrain,
                "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "ai_generated": False
            }

            # Add to saved routes
            self.saved_routes[username]["saved_routes"].append(new_route)
            self._save_routes()

            ascii_art.display_success_message(f"Route '{route_name}' saved successfully!")

    def view_saved_routes(self, username: str) -> None:
        """View and manage saved routes."""
        import utils.ascii_art as ascii_art
        from tabulate import tabulate

        user_routes = self.saved_routes[username]["saved_routes"]

        while True:
            ascii_art.clear_screen()

            # Enhanced header with Rich UI
            if HAS_RICH:
                try:
                    console.print(Panel.fit(
                        "[bold cyan]Your Cycling Route Collection[/bold cyan]",
                        border_style="cyan",
                        padding=(1, 2),
                        title="EcoCycle",
                        title_align="left"
                    ))
                    console.print(Rule(style="cyan"))
                except Exception as e:
                    logger.warning(f"Error using Rich for header: {e}")
                    ascii_art.display_section_header("Your Saved Routes")
            else:
                ascii_art.display_section_header("Your Saved Routes")

            # Handle empty collection with enhanced UI
            if not user_routes:
                if HAS_RICH:
                    try:
                        console.print(Panel(
                            "[yellow]Your route collection is currently empty[/yellow]\n\n" +
                            "[white]Routes help you plan your cycling adventures and track your favorite paths.[/white]\n\n" +
                            "[green]→ Generate a personalized route recommendation to get started[/green]\n" +
                            "[green]→ Save routes you enjoy for quick access later[/green]\n" +
                            "[green]→ Share your favorite cycling paths with friends[/green]",
                            title="No Saved Routes",
                            border_style="yellow",
                            expand=False,
                            padding=(1, 2)
                        ))

                        # Add a visual call-to-action
                        console.print("\n[bold cyan]Tip:[/bold cyan] Select 'Generate Route Recommendation' from the main menu to create your first route.")
                        console.input("\n[dim]Press Enter to continue...[/dim]")
                    except Exception as e:
                        logger.warning(f"Error using Rich for empty state: {e}")
                        print("\nYou don't have any saved routes.")
                        print("Generate a route recommendation to get started.")
                        input("\nPress Enter to continue...")
                else:
                    print("\nYou don't have any saved routes.")
                    print("Generate a route recommendation to get started.")
                    input("\nPress Enter to continue...")
                return

            # Show route count with enhanced styling
            if HAS_RICH:
                try:
                    console.print(f"\n[bold cyan]You have [green]{len(user_routes)}[/green] saved cycling routes:[/bold cyan]")
                except Exception as e:
                    logger.warning(f"Error using Rich for route count: {e}")
                    print(f"\nYou have {len(user_routes)} saved routes:")
            else:
                print(f"\nYou have {len(user_routes)} saved routes:")

            # Enhanced table with Rich UI
            if HAS_RICH:
                try:
                    # Create a visually enhanced table
                    table = Table(
                        title="Your Cycling Routes",
                        show_header=True,
                        header_style="bold cyan",
                        border_style="bright_blue",
                        box=rich.box.ROUNDED
                    )

                    table.add_column("#", style="dim", width=3, justify="right")
                    table.add_column("Route Name", style="bold green", min_width=20)
                    table.add_column("Location", style="cyan", min_width=15)
                    table.add_column("Distance", justify="right")
                    table.add_column("Difficulty", style="yellow")
                    table.add_column("Created Date", style="dim")
                    table.add_column("AI Gen", justify="center")

                    for i, route in enumerate(user_routes):
                        table.add_row(
                            str(i + 1),
                            route["name"],
                            route["location"],
                            f"{route.get('distance', 'N/A')} km",  # Use .get for safety
                            route.get("difficulty", "N/A").capitalize(),
                            route.get("created_date", "N/A"),
                            "[green]✓[/green]" if route.get("ai_generated", False) else "[red]✗[/red]"
                        )

                    console.print(table)
                except Exception as e:
                    logger.warning(f"Error using Rich for table: {e}")
                    # Fallback to tabulate
                    headers = ["#", "Route Name", "Location", "Distance", "Difficulty", "Created Date", "AI Generated"]
                    rows = []
                    for i, route in enumerate(user_routes):
                        rows.append([
                            i + 1,
                            route["name"],
                            route["location"],
                            f"{route.get('distance', 'N/A')} km",
                            route.get("difficulty", "N/A").capitalize(),
                            route.get("created_date", "N/A"),
                            "Yes" if route.get("ai_generated", False) else "No"
                        ])
                    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                # Fallback to tabulate
                headers = ["#", "Route Name", "Location", "Distance", "Difficulty", "Created Date", "AI Generated"]
                rows = []
                for i, route in enumerate(user_routes):
                    rows.append([
                        i + 1,
                        route["name"],
                        route["location"],
                        f"{route.get('distance', 'N/A')} km",
                        route.get("difficulty", "N/A").capitalize(),
                        route.get("created_date", "N/A"),
                        "Yes" if route.get("ai_generated", False) else "No"
                    ])
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

            # Enhanced options menu
            if HAS_RICH:
                try:
                    console.print("\n[bold]Options:[/bold]")
                    console.print("  [cyan]1[/cyan]. [bold]View[/bold] route details")
                    console.print("  [cyan]2[/cyan]. [bold]Share[/bold] a route")
                    console.print("  [cyan]3[/cyan]. [bold]Delete[/bold] a route")
                    console.print("  [cyan]4[/cyan]. [bold]Return[/bold] to AI Route Planner menu")

                    choice = console.input("\n[bold yellow]Select an option (1-4):[/bold yellow] ")
                except Exception as e:
                    logger.warning(f"Error using Rich for options: {e}")
                    print("\nOptions:")
                    print("  1. View route details")
                    print("  2. Share a route")
                    print("  3. Delete a route")
                    print("  4. Return to AI Route Planner menu")

                    choice = input("\nSelect an option (1-4): ")
            else:
                print("\nOptions:")
                print("  1. View route details")
                print("  2. Share a route")
                print("  3. Delete a route")
                print("  4. Return to AI Route Planner menu")

                choice = input("\nSelect an option (1-4): ")

            if choice == '1':
                self._view_route_details(username, user_routes)
            elif choice == '2':
                self._share_route(username, user_routes)
            elif choice == '3':
                self._delete_route(username, user_routes)
            elif choice == '4':
                break
            else:
                if HAS_RICH:
                    try:
                        console.print("[bold red]Invalid choice. Please select a number between 1-4.[/bold red]")
                        console.input("[dim]Press Enter to continue...[/dim]")
                    except Exception as e:
                        logger.warning(f"Error using Rich for error message: {e}")
                        print("Invalid choice.")
                        input("Press Enter to continue...")
                else:
                    print("Invalid choice.")
                    input("Press Enter to continue...")

    def _view_route_details(self, username: str, routes: List[Dict]) -> None:
        """View details of a selected route."""
        import utils.ascii_art as ascii_art

        try:
            route_idx = int(input("\nEnter the number of the route to view: ")) - 1
            if 0 <= route_idx < len(routes):
                route = routes[route_idx]

                ascii_art.clear_screen()
                ascii_art.display_section_header(f"Route Details: {route['name']}")

                print(route["description"])

                # Additional metadata
                print("\n--- Additional Information ---")
                print(f"Created: {route['created_date']}")
                print(f"AI Generated: {'Yes' if route.get('ai_generated', False) else 'No'}")

                input("\nPress Enter to continue...")
            else:
                print("Invalid selection.")
                input("Press Enter to continue...")
        except ValueError:
            print("Invalid input.")
            input("Press Enter to continue...")

    def _share_route(self, username: str, routes: List[Dict]) -> None:
        """Share a route with other users or export it."""
        import utils.ascii_art as ascii_art

        try:
            route_idx = int(input("\nEnter the number of the route to share: ")) - 1
            if 0 <= route_idx < len(routes):
                route = routes[route_idx]

                ascii_art.clear_screen()
                ascii_art.display_section_header(f"Share Route: {route['name']}")

                print("\nHow would you like to share this route?")
                print("  1. Export to text file")
                print("  2. Copy to clipboard (not implemented)")
                print("  3. Share with another EcoCycle user (not implemented)")
                print("  4. Cancel")

                share_choice = input("\nSelect an option (1-4): ")

                if share_choice == '1':
                    # Export to text file
                    filename = f"{route['name'].replace(' ', '_').lower()}_route.txt"
                    try:
                        with open(filename, 'w') as f:
                            f.write(f"EcoCycle Route: {route['name']}\n")
                            f.write(f"Generated on: {route['created_date']}\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(route["description"])

                        ascii_art.display_success_message(f"Route exported to {filename}")
                    except Exception as e:
                        print(f"Error exporting route: {e}")

                elif share_choice in ['2', '3']:
                    print("\nThis sharing option is not yet implemented.")

                elif share_choice == '4':
                    return
                else:
                    print("Invalid choice.")

                input("\nPress Enter to continue...")
            else:
                print("Invalid selection.")
                input("Press Enter to continue...")
        except ValueError:
            print("Invalid input.")
            input("Press Enter to continue...")

    def _delete_route(self, username: str, routes: List[Dict]) -> None:
        """Delete a saved route."""
        try:
            route_idx = int(input("\nEnter the number of the route to delete: ")) - 1
            if 0 <= route_idx < len(routes):
                route = routes[route_idx]

                confirm = input(f"Are you sure you want to delete '{route['name']}'? (y/n): ")
                if confirm.lower() == 'y':
                    routes.pop(route_idx)
                    self._save_routes()
                    print("Route deleted successfully.")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid selection.")

            input("\nPress Enter to continue...")
        except ValueError:
            print("Invalid input.")
            input("Press Enter to continue...")

    def update_cycling_preferences(self, username: str) -> None:
        """Update user's cycling preferences for route recommendations."""
        import utils.ascii_art as ascii_art

        user_prefs = self.saved_routes[username]["preferences"]

        ascii_art.clear_screen()
        ascii_art.display_section_header("Update Cycling Preferences")

        print("\nYour current preferences:")
        print(f"• Preferred distance: {user_prefs['preferred_distance']} km")
        print(f"• Difficulty level: {user_prefs['preferred_difficulty']}")
        print(f"• Terrain type: {user_prefs['preferred_terrain']}")
        print(f"• Route types: {', '.join(user_prefs['preferred_route_types'])}")
        print(f"• Points of interest: {', '.join(user_prefs['points_of_interest'])}")

        print("\nUpdate your preferences:")

        # Update preferred distance
        try:
            distance = input(f"\nPreferred distance in km [{user_prefs['preferred_distance']}]: ")
            if distance:
                user_prefs['preferred_distance'] = float(distance)
        except ValueError:
            print("Invalid input. Keeping current preference.")

        # Update difficulty level
        print("\nDifficulty levels:")
        for i, level in enumerate(DIFFICULTY_LEVELS):
            print(f"  {i + 1}. {level.capitalize()}")

        try:
            difficulty_idx = input(f"\nSelect difficulty level (1-4) [{DIFFICULTY_LEVELS.index(user_prefs['preferred_difficulty']) + 1}]: ")
            if difficulty_idx:
                difficulty_idx = int(difficulty_idx) - 1
                if 0 <= difficulty_idx < len(DIFFICULTY_LEVELS):
                    user_prefs['preferred_difficulty'] = DIFFICULTY_LEVELS[difficulty_idx]
                else:
                    print("Invalid selection. Keeping current preference.")
        except ValueError:
            print("Invalid input. Keeping current preference.")

        # Update terrain type
        print("\nTerrain types:")
        for i, terrain in enumerate(TERRAIN_TYPES):
            print(f"  {i + 1}. {terrain.capitalize()}")

        try:
            terrain_idx = input(f"\nSelect terrain type (1-4) [{TERRAIN_TYPES.index(user_prefs['preferred_terrain']) + 1}]: ")
            if terrain_idx:
                terrain_idx = int(terrain_idx) - 1
                if 0 <= terrain_idx < len(TERRAIN_TYPES):
                    user_prefs['preferred_terrain'] = TERRAIN_TYPES[terrain_idx]
                else:
                    print("Invalid selection. Keeping current preference.")
        except ValueError:
            print("Invalid input. Keeping current preference.")

        # Update route types
        print("\nRoute types (select up to 3):")
        for i, route_type in enumerate(ROUTE_TYPES):
            print(f"  {i + 1}. {route_type.capitalize()}")

        try:
            route_types_input = input("\nEnter up to 3 numbers separated by commas: ")
            if route_types_input:
                route_type_indices = [int(x.strip()) - 1 for x in route_types_input.split(',')]
                selected_types = []
                for idx in route_type_indices:
                    if 0 <= idx < len(ROUTE_TYPES):
                        selected_types.append(ROUTE_TYPES[idx])

                if selected_types:
                    user_prefs['preferred_route_types'] = selected_types[:3]  # Limit to 3
        except ValueError:
            print("Invalid input. Keeping current preferences.")

        # Update points of interest
        print("\nPoints of interest (select up to 3):")
        for i, poi in enumerate(POI_CATEGORIES):
            print(f"  {i + 1}. {poi.replace('_', ' ').title()}")

        try:
            poi_input = input("\nEnter up to 3 numbers separated by commas: ")
            if poi_input:
                poi_indices = [int(x.strip()) - 1 for x in poi_input.split(',')]
                selected_pois = []
                for idx in poi_indices:
                    if 0 <= idx < len(POI_CATEGORIES):
                        selected_pois.append(POI_CATEGORIES[idx])

                if selected_pois:
                    user_prefs['points_of_interest'] = selected_pois[:3]  # Limit to 3
        except ValueError:
            print("Invalid input. Keeping current preferences.")

        # Save preferences
        self._save_routes()

        ascii_art.display_success_message("Cycling preferences updated successfully!")
        input("\nPress Enter to continue...")

    def get_route_analysis(self, username: str) -> None:
        """Get detailed AI analysis of a saved route."""
        import utils.ascii_art as ascii_art

        user_routes = self.saved_routes[username]["saved_routes"]

        if not user_routes:
            print("\nYou don't have any saved routes to analyze.")
            input("\nPress Enter to continue...")
            return

        if not self.gemini_available:
            print("\nThe Gemini API is not available. Cannot perform route analysis.")
            input("\nPress Enter to continue...")
            return

        ascii_art.clear_screen()
        ascii_art.display_section_header("Route Analysis")

        print("\nSelect a route to analyze:")
        for i, route in enumerate(user_routes):
            print(f"  {i + 1}. {route['name']} ({route['location']}, {route['distance']} km)")

        try:
            route_idx = int(input("\nEnter route number: ")) - 1
            if 0 <= route_idx < len(user_routes):
                route = user_routes[route_idx]

                ascii_art.display_loading_message("Analyzing route with AI...")

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
                Name: {route['name']}
                Location: {route['location']}
                Distance: {route['distance']} km
                Difficulty: {route['difficulty']}
                Terrain: {route['terrain']}
                Description:
                {route['description']}

                Provide the analysis in a structured format with clear section headers.
                """

                try:
                    # Set up the model
                    model = genai.GenerativeModel(
                        model_name=self.default_model,  # Use the dynamically detected model
                        generation_config=self.generation_config
                    )

                    # Make API request
                    response = model.generate_content(prompt)
                    analysis = response.text

                    # Display the analysis
                    ascii_art.clear_screen()
                    ascii_art.display_section_header(f"Analysis of {route['name']}")

                    route_markdown = Markdown(analysis)

                    # Display the generated route using rich
                    ascii_art.clear_screen()
                    # Use rich Panel for the header (optional replacement for ascii_art)
                    console.print(Panel("Your Personalized Cycling Route Analysis", style="bold green", title_align="left"))
                    console.print(route_markdown)

                    # Option to save analysis
                    save = input("\nWould you like to save this analysis to a file? (y/n): ").lower()
                    if save == 'y':
                        filename = f"{route['name'].replace(' ', '_').lower()}_analysis.txt"
                        try:
                            with open(filename, 'w') as f:
                                f.write(f"EcoCycle Route Analysis: {route['name']}\n")
                                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
                                f.write("=" * 50 + "\n\n")
                                f.write(analysis)

                            ascii_art.display_success_message(f"Analysis exported to {filename}")
                        except Exception as e:
                            print(f"Error exporting analysis: {e}")

                except Exception as e:
                    logger.error(f"Error analyzing route with Gemini: {e}")
                    print(f"\nError analyzing route: {e}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

        input("\nPress Enter to continue...")

    def generate_alternative_routes(self, username: str) -> None:
        """Generate alternative versions of an existing route."""
        import utils.ascii_art as ascii_art

        user_routes = self.saved_routes[username]["saved_routes"]

        if not user_routes:
            print("\nYou don't have any saved routes to create alternatives for.")
            input("\nPress Enter to continue...")
            return

        if not self.gemini_available:
            print("\nThe Gemini API is not available. Cannot generate alternative routes.")
            input("\nPress Enter to continue...")
            return

        ascii_art.clear_screen()
        ascii_art.display_section_header("Generate Alternative Routes")

        print("\nSelect a route to create alternatives for:")
        for i, route in enumerate(user_routes):
            print(f"  {i + 1}. {route['name']} ({route['location']}, {route['distance']} km)")

        try:
            route_idx = int(input("\nEnter route number: ")) - 1
            if 0 <= route_idx < len(user_routes):
                route = user_routes[route_idx]

                print("\nWhat kind of alternative would you like to generate?")
                print("  1. Easier version (less difficult)")
                print("  2. More challenging version")
                print("  3. Shorter version")
                print("  4. Longer version")
                print("  5. More scenic version")
                print("  6. Family-friendly version")

                alt_choice = input("\nSelect option (1-6): ")

                if alt_choice in ['1', '2', '3', '4', '5', '6']:
                    variation_types = {
                        '1': "easier, less difficult version",
                        '2': "more challenging version",
                        '3': "shorter version",
                        '4': "longer version",
                        '5': "more scenic version with additional viewpoints and natural attractions",
                        '6': "family-friendly version suitable for children and casual cyclists"
                    }

                    variation_type = variation_types[alt_choice]

                    ascii_art.display_loading_message(f"Generating {variation_type}...")

                    # Prepare prompt for Gemini
                    prompt = f"""
                    Create a {variation_type} of this cycling route:

                    Original route:
                    Name: {route['name']}
                    Location: {route['location']}
                    Distance: {route['distance']} km
                    Difficulty: {route['difficulty']}
                    Terrain: {route['terrain']}
                    Description:
                    {route['description']}

                    Create a complete alternative route that maintains the general location and character but adjusts it to be a {variation_type}.

                    Format the response as follows:
                    1. A name for the alternative route
                    2. A one-paragraph summary of how this route differs from the original
                    3. Starting point (be specific)
                    4. Route description with turn-by-turn directions
                    5. Key features along the route (3-5 points of interest)
                    6. Difficulty assessment and why
                    7. Safety considerations
                    8. Best time to ride
                    9. Estimated duration
                    10. Elevation gain (in meters)
                    11. Surface types (percentage of paved/unpaved)
                    """

                    try:
                        # Set up the model
                        model = genai.GenerativeModel(
                            model_name=self.default_model,  # Use the dynamically detected model
                            generation_config=self.generation_config
                        )

                        # Make API request
                        response = model.generate_content(prompt)
                        alternative_route = response.text

                        # Display the alternative route
                        ascii_art.clear_screen()
                        ascii_art.display_section_header(f"Alternative Route for {route['name']}")

                        route_markdown = Markdown(response.text)

                        # Display the generated route using rich
                        ascii_art.clear_screen()
                        # Use rich Panel for the header (optional replacement for ascii_art)
                        console.print(Panel("Alternative Routes Generated", style="bold green", title_align="left"))
                        console.print(route_markdown)

                        # Ask user if they want to save the alternative route
                        save = input("\nWould you like to save this alternative route? (y/n): ").lower()

                        if save == 'y':
                            # Try to extract the route name from the AI response
                            try:
                                first_line = alternative_route.split('\n')[0]
                                if first_line and len(first_line) < 100:  # Reasonable length for a name
                                    alt_route_name = first_line.strip()
                                else:
                                    alt_route_name = f"{route['name']} ({variation_type.split(',')[0]})"
                            except:
                                alt_route_name = f"{route['name']} ({variation_type.split(',')[0]})"

                            custom_name = input(f"Enter a name for this route (or press Enter to use '{alt_route_name}'): ")
                            if custom_name:
                                alt_route_name = custom_name

                            # Adjust parameters based on the type of alternative
                            distance = route['distance']
                            difficulty = route['difficulty']

                            if alt_choice == '1':  # Easier
                                difficulty_idx = DIFFICULTY_LEVELS.index(difficulty)
                                if difficulty_idx > 0:
                                    difficulty = DIFFICULTY_LEVELS[difficulty_idx - 1]
                            elif alt_choice == '2':  # More challenging
                                difficulty_idx = DIFFICULTY_LEVELS.index(difficulty)
                                if difficulty_idx < len(DIFFICULTY_LEVELS) - 1:
                                    difficulty = DIFFICULTY_LEVELS[difficulty_idx + 1]
                            elif alt_choice == '3':  # Shorter
                                distance = route['distance'] * 0.7
                            elif alt_choice == '4':  # Longer
                                distance = route['distance'] * 1.3

                            # Create route object
                            new_route = {
                                "name": alt_route_name,
                                "location": route['location'],
                                "description": alternative_route,
                                "distance": distance,
                                "difficulty": difficulty,
                                "terrain": route['terrain'],
                                "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                                "ai_generated": True,
                                "alternative_to": route['name']
                            }

                            # Add to saved routes
                            self.saved_routes[username]["saved_routes"].append(new_route)
                            self._save_routes()

                            ascii_art.display_success_message(f"Alternative route '{alt_route_name}' saved successfully!")

                    except Exception as e:
                        logger.error(f"Error generating alternative route with Gemini: {e}")
                        print(f"\nError generating alternative route: {e}")
                else:
                    print("Invalid choice.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

        input("\nPress Enter to continue...")

    def assess_route_safety(self, username: str) -> None:
        """Assess the safety of a route and provide recommendations."""
        import utils.ascii_art as ascii_art

        user_routes = self.saved_routes[username]["saved_routes"]

        if not user_routes:
            print("\nYou don't have any saved routes to assess for safety.")
            input("\nPress Enter to continue...")
            return

        if not self.gemini_available:
            print("\nThe Gemini API is not available. Cannot perform safety assessment.")
            input("\nPress Enter to continue...")
            return

        ascii_art.clear_screen()
        ascii_art.display_section_header("Route Safety Assessment")

        print("\nSelect a route to assess for safety:")
        for i, route in enumerate(user_routes):
            print(f"  {i + 1}. {route['name']} ({route['location']}, {route['distance']} km)")

        try:
            route_idx = int(input("\nEnter route number: ")) - 1
            if 0 <= route_idx < len(user_routes):
                route = user_routes[route_idx]

                # Additional information for safety assessment
                print("\nPlease provide additional information for a more accurate safety assessment:")

                cyclist_type = ""
                print("\nWhat type of cyclist will be riding this route?")
                print("  1. Solo adult cyclist")
                print("  2. Group of adult cyclists")
                print("  3. Family with children")
                print("  4. Senior cyclist")
                print("  5. Beginner cyclist")

                type_choice = input("\nSelect option (1-5): ")
                if type_choice == '1':
                    cyclist_type = "Solo adult cyclist"
                elif type_choice == '2':
                    cyclist_type = "Group of adult cyclists"
                elif type_choice == '3':
                    cyclist_type = "Family with children"
                elif type_choice == '4':
                    cyclist_type = "Senior cyclist"
                elif type_choice == '5':
                    cyclist_type = "Beginner cyclist"
                else:
                    cyclist_type = "General cyclist"

                time_of_day = ""
                print("\nWhat time of day will the route typically be ridden?")
                print("  1. Early morning")
                print("  2. Daytime")
                print("  3. Evening/sunset")
                print("  4. Night")

                time_choice = input("\nSelect option (1-4): ")
                if time_choice == '1':
                    time_of_day = "Early morning"
                elif time_choice == '2':
                    time_of_day = "Daytime"
                elif time_choice == '3':
                    time_of_day = "Evening/sunset"
                elif time_choice == '4':
                    time_of_day = "Night"
                else:
                    time_of_day = "Various times"

                special_concerns = input("\nAny special safety concerns? (e.g., busy intersections, wildlife, weather): ")

                ascii_art.display_loading_message("Generating safety assessment with AI...")

                # Prepare prompt for Gemini
                prompt = f"""
                Perform a comprehensive safety assessment for this cycling route:

                Route details:
                Name: {route['name']}
                Location: {route['location']}
                Distance: {route['distance']} km
                Difficulty: {route['difficulty']}
                Terrain: {route['terrain']}
                Description:
                {route['description']}

                Additional context:
                Cyclist type: {cyclist_type}
                Time of day: {time_of_day}
                Special concerns: {special_concerns}

                Provide a detailed safety assessment including:

                1. Overall safety rating (1-10)
                2. Traffic safety analysis
                3. Road/trail condition safety
                4. Natural hazards assessment
                5. Time of day safety considerations
                6. Weather-related safety factors
                7. Recommended safety equipment and precautions
                8. Emergency options along the route
                9. Specific warnings for dangerous sections
                10. Suggestions to improve route safety

                Format your response with clear section headers and concise, practical advice.
                """

                try:
                    # Set up the model
                    model = genai.GenerativeModel(
                        model_name=self.default_model,  # Use the dynamically detected model
                        generation_config=self.generation_config
                    )

                    # Make API request
                    response = model.generate_content(prompt)
                    safety_assessment = response.text

                    # Display the safety assessment
                    ascii_art.clear_screen()
                    ascii_art.display_section_header(f"Safety Assessment: {route['name']}")

                    route_markdown = Markdown(response.text)

                    # Display the generated route using rich
                    ascii_art.clear_screen()
                    # Use rich Panel for the header (optional replacement for ascii_art)
                    console.print(Panel("Your Personalized Cycling Route Safety Assessment", style="bold green", title_align="left"))
                    console.print(route_markdown)

                    # Option to save assessment
                    save = input("\nWould you like to save this safety assessment to a file? (y/n): ").lower()
                    if save == 'y':
                        filename = f"{route['name'].replace(' ', '_').lower()}_safety.txt"
                        try:
                            with open(filename, 'w') as f:
                                f.write(f"EcoCycle Route Safety Assessment: {route['name']}\n")
                                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
                                f.write("=" * 50 + "\n\n")
                                f.write(safety_assessment)

                            ascii_art.display_success_message(f"Safety assessment exported to {filename}")
                        except Exception as e:
                            print(f"Error exporting assessment: {e}")

                except Exception as e:
                    logger.error(f"Error generating safety assessment with Gemini: {e}")
                    print(f"\nError generating safety assessment: {e}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

        input("\nPress Enter to continue...")

    def compare_routes(self, username: str) -> None:
        """Compare two saved routes and highlight differences."""
        import utils.ascii_art as ascii_art

        user_routes = self.saved_routes[username]["saved_routes"]

        if len(user_routes) < 2:
            print("\nYou need at least two saved routes to use the comparison tool.")
            input("\nPress Enter to continue...")
            return

        if not self.gemini_available:
            print("\nThe Gemini API is not available. Cannot perform route comparison.")
            input("\nPress Enter to continue...")
            return

        ascii_art.clear_screen()
        ascii_art.display_section_header("Route Comparison Tool")

        print("\nSelect the first route to compare:")
        for i, route in enumerate(user_routes):
            print(f"  {i + 1}. {route['name']} ({route['location']}, {route['distance']} km)")

        try:
            route1_idx = int(input("\nEnter first route number: ")) - 1
            if not (0 <= route1_idx < len(user_routes)):
                print("Invalid selection.")
                input("\nPress Enter to continue...")
                return

            route1 = user_routes[route1_idx]

            print("\nSelect the second route to compare:")
            for i, route in enumerate(user_routes):
                if i != route1_idx:
                    print(f"  {i + 1}. {route['name']} ({route['location']}, {route['distance']} km)")

            route2_idx = int(input("\nEnter second route number: ")) - 1
            if not (0 <= route2_idx < len(user_routes)) or route1_idx == route2_idx:
                print("Invalid selection.")
                input("\nPress Enter to continue...")
                return

            route2 = user_routes[route2_idx]

            ascii_art.display_loading_message("Comparing routes with AI...")

            # Prepare prompt for Gemini
            prompt = f"""
            Compare these two cycling routes and provide a detailed comparison:

            Route 1:
            Name: {route1['name']}
            Location: {route1['location']}
            Distance: {route1['distance']} km
            Difficulty: {route1['difficulty']}
            Terrain: {route1['terrain']}
            Description:
            {route1['description']}

            Route 2:
            Name: {route2['name']}
            Location: {route2['location']}
            Distance: {route2['distance']} km
            Difficulty: {route2['difficulty']}
            Terrain: {route2['terrain']}
            Description:
            {route2['description']}

            Provide a comprehensive comparison that includes:

            1. Summary of key differences
            2. Comparison table of main features
            3. Difficulty comparison
            4. Scenic value comparison
            5. Safety comparison
            6. Fitness benefit comparison
            7. Suitability for different cyclist types
            8. Recommended route based on different scenarios (e.g., "Route 1 is better for families, Route 2 is better for training")

            Format your response with clear section headers and a well-structured comparison.
            """

            try:
                # Set up the model
                model = genai.GenerativeModel(
                    model_name=self.default_model,  # Use the dynamically detected model
                    generation_config=self.generation_config
                )

                # Make API request
                response = model.generate_content(prompt)
                comparison = response.text

                # Display the comparison
                ascii_art.clear_screen()
                ascii_art.display_section_header(f"Route Comparison: {route1['name']} vs {route2['name']}")

                route_markdown = Markdown(response.text)

                # Display the generated route using rich
                ascii_art.clear_screen()
                # Use rich Panel for the header (optional replacement for ascii_art)
                console.print(Panel("Your Personalized Cycling Route Comparison", style="bold green", title_align="left"))
                console.print(route_markdown)

                # Option to save comparison
                save = input("\nWould you like to save this comparison to a file? (y/n): ").lower()
                if save == 'y':
                    filename = f"route_comparison_{route1['name'].replace(' ', '_').lower()}_vs_{route2['name'].replace(' ', '_').lower()}.txt"
                    try:
                        with open(filename, 'w') as f:
                            f.write(f"EcoCycle Route Comparison\n")
                            f.write(f"{route1['name']} vs {route2['name']}\n")
                            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(comparison)

                        ascii_art.display_success_message(f"Comparison exported to {filename}")
                    except Exception as e:
                        print(f"Error exporting comparison: {e}")

            except Exception as e:
                logger.error(f"Error comparing routes with Gemini: {e}")
                print(f"\nError comparing routes: {e}")
        except ValueError:
            print("Invalid input.")

        input("\nPress Enter to continue...")


# This function has been moved above to avoid duplication


if __name__ == "__main__":
    run_ai_route_planner()
