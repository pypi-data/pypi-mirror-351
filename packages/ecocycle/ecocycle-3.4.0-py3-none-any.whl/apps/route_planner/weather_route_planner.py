"""
EcoCycle - Weather and Route Planner Module
Provides functionality for checking weather conditions and planning cycling routes.

This module provides backward compatibility for the new MVC architecture.
New code should use the classes in the models, controllers, and views packages.
"""
import os
import json
import time
import logging
import re
import webbrowser
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union

# Check if the rich module is available
try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn, SpinnerColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    from rich.prompt import Prompt
    from rich.rule import Rule
    from rich.box import ROUNDED, DOUBLE
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Import dependency_manager for ensuring packages
from core.dependency import dependency_manager

# Check for requests availability using the dependency manager
REQUESTS_AVAILABLE = dependency_manager.is_package_installed('requests')

try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Import utilities
import utils.general_utils as general_utils
import utils.ascii_art as ascii_art

# Import from MVC architecture
from models.weather_data import WeatherData, WeatherDataCollection, DEFAULT_COORDINATES
from models.route import Route, RouteCollection
from controllers.weather_controller import WeatherController
from controllers.route_controller import RouteController
from views.weather_view import WeatherView
from views.route_view import RouteView

# Import configuration
from config.config import WEATHER_CACHE_FILE, ROUTES_CACHE_FILE

logger = logging.getLogger(__name__)

# Constants
WEATHER_CACHE_EXPIRY = 60 * 60  # 1 hour in seconds
DEFAULT_COORDINATES = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Berlin": (52.5200, 13.4050),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (-33.8688, 151.2093),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Cairo": (30.0444, 31.2357)
}
# WEATHER_CACHE_FILE and ROUTES_CACHE_FILE are now imported from config.config
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "")
MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_ACCESS_TOKEN", "")


class WeatherRoutePlanner:
    """
    Weather and route planner for cyclists.
    Provides functionality to check weather conditions and plan cycling routes.

    This class provides backward compatibility for the new MVC architecture.
    New code should use the classes in the models, controllers, and views packages.
    """

    def __init__(self, user_manager=None):
        """Initialize the weather and route planner."""
        self.user_manager = user_manager

        # Create instances of the MVC classes for backward compatibility
        self.weather_collection = WeatherDataCollection()
        self.route_collection = RouteCollection()
        self.weather_controller = WeatherController(self.weather_collection)
        self.route_controller = RouteController(self.route_collection, user_manager)
        self.weather_view = WeatherView(self.weather_controller, user_manager, ascii_art)
        self.route_view = RouteView(self.route_controller, self.weather_controller)

        # For backward compatibility
        self.weather_cache = self._load_cache(WEATHER_CACHE_FILE)
        self.routes_cache = self._load_cache(ROUTES_CACHE_FILE)

    def _load_cache(self, cache_file: str) -> Dict:
        """Load cache from file."""
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Error loading cache from {cache_file}: {e}")
        return {}

    def _save_cache(self, cache_data: Dict, cache_file: str) -> bool:
        """Save cache to file."""
        try:
            with open(cache_file, 'w') as file:
                json.dump(cache_data, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving cache to {cache_file}: {e}")
            return False

    def _is_cache_valid(self, cache_key: str, cache_data: Dict) -> bool:
        """Check if cached data is still valid (not expired)."""
        if cache_key not in cache_data:
            return False

        cached_time = cache_data[cache_key].get("timestamp", 0)
        current_time = time.time()

        return current_time - cached_time < WEATHER_CACHE_EXPIRY

    def run_planner(self, user_manager_instance=None) -> None:
        """
        Run the weather and route planner interface.

        Args:
            user_manager_instance: Optional user manager instance
        """
        # Create a new instance of the weather route planner
        planner = WeatherRoutePlanner(user_manager_instance)

        while True:
            # Show the main menu and get user choice
            ascii_art.clear_screen()
            ascii_art.display_header()

            # Use Rich UI if available
            if HAS_RICH:
                # Display header with Rich styling
                console.print(Panel.fit(
                    Text("Weather and Route Planner", style="bold cyan"),
                    border_style="cyan"
                ))

                # Display description with Rich styling
                console.print(Panel(
                    "Plan your cycling routes with real-time weather updates and optimize your journey.\n"
                    "Get forecasts, map routes, and receive cycling condition recommendations.",
                    border_style="green"
                ))

                # Create a menu table
                menu_table = Table(show_header=False, box=rich.box.ROUNDED, border_style="blue")
                menu_table.add_column("Option", style="cyan")
                menu_table.add_column("Description", style="green")

                # Add exit option
                menu_table.add_row("0", "[yellow]Return to Main Menu[/yellow]")

                # Add menu options
                menu_table.add_row("1", "[cyan]Check Weather Forecast for Cycling[/cyan]")
                menu_table.add_row("2", "[cyan]Plan Cycling Route[/cyan]")
                menu_table.add_row("3", "[cyan]View Saved Routes[/cyan]")
                menu_table.add_row("4", "[cyan]Cycling Impact Calculator[/cyan]")

                # Display the menu
                console.print(Panel(menu_table, title="Route Planning Options", border_style="blue"))
                choice = console.input("[cyan]Select an option:[/cyan] ")
            else:
                # Fallback to ASCII art display
                ascii_art.display_section_header("Weather and Route Planner")

                print("\nPlan your cycling routes with real-time weather updates.")

                print("\nOptions:")
                print(f"  {ascii_art.Fore.YELLOW}0. Return to Main Menu{ascii_art.Style.RESET_ALL}")
                print(f"  {ascii_art.Fore.CYAN}1. Check Weather Forecast for Cycling{ascii_art.Style.RESET_ALL}")
                print(f"  {ascii_art.Fore.GREEN}2. Plan Cycling Route{ascii_art.Style.RESET_ALL}")
                print(f"  {ascii_art.Fore.BLUE}3. View Saved Routes{ascii_art.Style.RESET_ALL}")
                print(f"  {ascii_art.Fore.MAGENTA}4. Cycling Impact Calculator{ascii_art.Style.RESET_ALL}")

                choice = input("\nSelect an option (0-4): ")

            # Process the user's choice
            if choice == "0":
                # Return to main menu
                break
            elif choice == "1":
                # Get weather controller to handle API calls
                from controllers.weather_controller import WeatherController
                weather_controller = WeatherController()

                # Create a weather view to display results
                from views.weather_view import WeatherView
                weather_view = WeatherView(weather_controller, user_manager_instance, ascii_art)

                while True:
                    # Show weather menu and get user choice
                    option = weather_view.display_weather_menu()

                    if option == "0":
                        # Exit to route planner menu
                        break
                    elif option == "1":
                        # Get current weather & 3-hour forecast
                        if HAS_RICH:
                            with Progress(
                                SpinnerColumn(),
                                TextColumn("[bold blue]Getting current weather data...[/bold blue]"),
                                BarColumn(),
                                TimeElapsedColumn(),
                                transient=True
                            ) as progress:
                                task = progress.add_task("Loading...", total=100)
                                # Simulate progress
                                for i in range(0, 50, 5):
                                    time.sleep(0.05)
                                    progress.update(task, completed=i)

                                # Get weather data
                                weather_data = weather_controller.get_current_weather()

                                # Continue progress
                                for i in range(50, 101, 5):
                                    time.sleep(0.03)
                                    progress.update(task, completed=i)
                        else:
                            print("\nGetting current weather data...")
                            weather_data = weather_controller.get_current_weather()

                        # Clear screen for display
                        ascii_art.clear_screen()

                        # Display weather data
                        if weather_data:
                            if HAS_RICH:
                                console.print(Panel.fit(
                                    Text("Current Weather & 3-Hour Forecast", style="bold cyan"),
                                    border_style="cyan"
                                ))
                            else:
                                ascii_art.display_section_header("Current Weather & 3-Hour Forecast")

                            weather_view.display_weather_data(weather_data)
                        else:
                            if HAS_RICH:
                                console.print(Panel(
                                    "Could not retrieve weather data.\n"
                                    "Please check your internet connection and try again.",
                                    title="Error",
                                    border_style="red",
                                    box=rich.box.ROUNDED
                                ))
                            else:
                                print("\nCould not retrieve weather data.")
                                print("Please check your internet connection and try again.")

                        # Prompt to continue
                        if HAS_RICH:
                            console.input("\n[cyan]Press Enter to continue...[/cyan]")
                        else:
                            input("\nPress Enter to continue...")

                    elif option == "2":
                        # Get 2-day forecast
                        if HAS_RICH:
                            with Progress(
                                SpinnerColumn(),
                                TextColumn("[bold blue]Getting forecast data...[/bold blue]"),
                                BarColumn(),
                                TimeElapsedColumn(),
                                transient=True
                            ) as progress:
                                task = progress.add_task("Loading...", total=100)
                                # Simulate progress
                                for i in range(0, 50, 5):
                                    time.sleep(0.05)
                                    progress.update(task, completed=i)

                                # Get weather data
                                weather_data = weather_controller.get_current_weather()

                                # Continue progress
                                for i in range(50, 101, 5):
                                    time.sleep(0.03)
                                    progress.update(task, completed=i)
                        else:
                            print("\nGetting forecast data...")
                            weather_data = weather_controller.get_current_weather()

                        # Clear screen for display
                        ascii_art.clear_screen()

                        # Display weather data
                        if weather_data:
                            if HAS_RICH:
                                console.print(Panel.fit(
                                    Text("2-Day Weather Forecast", style="bold cyan"),
                                    border_style="cyan"
                                ))
                            else:
                                ascii_art.display_section_header("2-Day Weather Forecast")

                            weather_view.display_weather_data(weather_data)
                        else:
                            if HAS_RICH:
                                console.print(Panel(
                                    "Could not retrieve forecast data.\n"
                                    "Please check your internet connection and try again.",
                                    title="Error",
                                    border_style="red",
                                    box=rich.box.ROUNDED
                                ))
                            else:
                                print("\nCould not retrieve forecast data.")
                                print("Please check your internet connection and try again.")

                        # Prompt to continue
                        if HAS_RICH:
                            console.input("\n[cyan]Press Enter to continue...[/cyan]")
                        else:
                            input("\nPress Enter to continue...")

                    elif option == "3":
                        # Get cycling conditions
                        if HAS_RICH:
                            with Progress(
                                SpinnerColumn(),
                                TextColumn("[bold blue]Analyzing cycling conditions...[/bold blue]"),
                                BarColumn(),
                                TimeElapsedColumn(),
                                transient=True
                            ) as progress:
                                task = progress.add_task("Analyzing...", total=100)
                                # Simulate progress
                                for i in range(0, 50, 5):
                                    time.sleep(0.05)
                                    progress.update(task, completed=i)

                                # Get weather data
                                weather_data = weather_controller.get_current_weather()

                                # Continue progress
                                for i in range(50, 101, 5):
                                    time.sleep(0.03)
                                    progress.update(task, completed=i)
                        else:
                            print("\nAnalyzing cycling conditions...")
                            weather_data = weather_controller.get_current_weather()

                        # Clear screen for display
                        ascii_art.clear_screen()

                        # Display cycling conditions
                        if weather_data:
                            if HAS_RICH:
                                console.print(Panel.fit(
                                    Text("Cycling Conditions & Recommendations", style="bold cyan"),
                                    border_style="cyan"
                                ))

                                # Get recommendation
                                recommendation = weather_controller.get_cycling_recommendation(weather_data)
                                rec_color = "green" if "Good" in recommendation else "yellow" if "Fair" in recommendation else "red"

                                # Current weather
                                current_temp = weather_data.get_current_temperature()
                                weather_main = weather_data.get_current_weather_condition()
                                weather_desc = weather_data.get_current_weather_description()
                                wind_speed = weather_data.get_current_wind_speed()
                                wind_direction = weather_controller.get_wind_direction_text(weather_data.get_current_wind_direction())
                                humidity = weather_data.get_current_humidity()

                                # Display current conditions in a panel
                                current_panel = Panel(
                                    f"[bold cyan]{current_temp:.1f}°C[/bold cyan] [dim]with[/dim] [white]{weather_main}[/white]: {weather_desc}\n"
                                    f"Wind: {wind_speed:.1f} km/h {wind_direction}\n"
                                    f"Humidity: {humidity}%",
                                    title="Current Weather",
                                    border_style="blue",
                                    box=rich.box.ROUNDED
                                )
                                console.print(current_panel)

                                # Display recommendations in a panel
                                rec_panel = Panel(
                                    f"[{rec_color}]{recommendation}[/{rec_color}]",
                                    title="Cycling Recommendation",
                                    border_style=rec_color,
                                    box=rich.box.ROUNDED
                                )
                                console.print(rec_panel)

                                # Display detailed cycling tips
                                console.print(Rule("Detailed Cycling Tips", style="cyan"))

                                tips_table = Table(box=rich.box.ROUNDED, border_style="green")
                                tips_table.add_column("Category", style="cyan")
                                tips_table.add_column("Recommendation", style="green")

                                # Add clothing recommendation based on temperature
                                if current_temp < 5:
                                    tips_table.add_row("Clothing", "Heavy winter gear with thermal layers, full gloves, and face protection")
                                elif current_temp < 10:
                                    tips_table.add_row("Clothing", "Winter cycling jacket, thermal tights, full finger gloves")
                                elif current_temp < 15:
                                    tips_table.add_row("Clothing", "Long sleeve jersey, cycling pants, light gloves")
                                elif current_temp < 20:
                                    tips_table.add_row("Clothing", "Light long sleeve or short sleeve jersey, cycling shorts")
                                else:
                                    tips_table.add_row("Clothing", "Lightweight and breathable clothing, shorts, short sleeve jersey")

                                # Add visibility recommendation based on conditions
                                if "rain" in weather_desc.lower() or "fog" in weather_desc.lower() or "mist" in weather_desc.lower():
                                    tips_table.add_row("Visibility", "Use front and rear lights, wear high-visibility clothing")
                                else:
                                    tips_table.add_row("Visibility", "Standard visibility gear should be sufficient")

                                # Add hydration recommendation based on temperature
                                if current_temp > 25:
                                    tips_table.add_row("Hydration", "Bring extra water, hydrate every 15-20 minutes")
                                elif current_temp > 15:
                                    tips_table.add_row("Hydration", "Bring sufficient water, hydrate regularly")
                                else:
                                    tips_table.add_row("Hydration", "Standard hydration, warm drink recommended")

                                # Add route recommendation based on wind and conditions
                                if wind_speed > 20:
                                    tips_table.add_row("Route", "Choose sheltered routes, avoid open areas with crosswinds")
                                elif "rain" in weather_desc.lower():
                                    tips_table.add_row("Route", "Choose routes with good drainage, avoid dirt paths")
                                else:
                                    tips_table.add_row("Route", "All routes suitable based on current conditions")

                                console.print(tips_table)
                            else:
                                ascii_art.display_section_header("Cycling Conditions & Recommendations")

                                # Get recommendation
                                recommendation = weather_controller.get_cycling_recommendation(weather_data)

                                # Current weather
                                current_temp = weather_data.get_current_temperature()
                                weather_main = weather_data.get_current_weather_condition()
                                weather_desc = weather_data.get_current_weather_description()
                                wind_speed = weather_data.get_current_wind_speed()
                                wind_direction = weather_controller.get_wind_direction_text(weather_data.get_current_wind_direction())
                                humidity = weather_data.get_current_humidity()

                                # Display current conditions
                                print(f"\nCurrent Weather:")
                                print(f"Temperature: {current_temp:.1f}°C")
                                print(f"Conditions: {weather_main} - {weather_desc}")
                                print(f"Wind: {wind_speed:.1f} km/h {wind_direction}")
                                print(f"Humidity: {humidity}%")

                                # Display recommendation
                                print(f"\nCycling Recommendation:")
                                print(f"{recommendation}")

                                # Display detailed cycling tips
                                print("\nDetailed Cycling Tips:")

                                # Clothing recommendation based on temperature
                                print("\nClothing:")
                                if current_temp < 5:
                                    print("Heavy winter gear with thermal layers, full gloves, and face protection")
                                elif current_temp < 10:
                                    print("Winter cycling jacket, thermal tights, full finger gloves")
                                elif current_temp < 15:
                                    print("Long sleeve jersey, cycling pants, light gloves")
                                elif current_temp < 20:
                                    print("Light long sleeve or short sleeve jersey, cycling shorts")
                                else:
                                    print("Lightweight and breathable clothing, shorts, short sleeve jersey")

                                # Visibility recommendation
                                print("\nVisibility:")
                                if "rain" in weather_desc.lower() or "fog" in weather_desc.lower() or "mist" in weather_desc.lower():
                                    print("Use front and rear lights, wear high-visibility clothing")
                                else:
                                    print("Standard visibility gear should be sufficient")

                                # Hydration recommendation
                                print("\nHydration:")
                                if current_temp > 25:
                                    print("Bring extra water, hydrate every 15-20 minutes")
                                elif current_temp > 15:
                                    print("Bring sufficient water, hydrate regularly")
                                else:
                                    print("Standard hydration, warm drink recommended")

                                # Route recommendation
                                print("\nRoute:")
                                if wind_speed > 20:
                                    print("Choose sheltered routes, avoid open areas with crosswinds")
                                elif "rain" in weather_desc.lower():
                                    print("Choose routes with good drainage, avoid dirt paths")
                                else:
                                    print("All routes suitable based on current conditions")
                        else:
                            if HAS_RICH:
                                console.print(Panel(
                                    "Could not retrieve weather data for cycling conditions.\n"
                                    "Please check your internet connection and try again.",
                                    title="Error",
                                    border_style="red",
                                    box=rich.box.ROUNDED
                                ))
                            else:
                                print("\nCould not retrieve weather data for cycling conditions.")
                                print("Please check your internet connection and try again.")

                        # Prompt to continue
                        if HAS_RICH:
                            console.input("\n[cyan]Press Enter to continue...[/cyan]")
                        else:
                            input("\nPress Enter to continue...")

                    elif option == "4":
                        # Plan a cycling route - go back to main planner and select option 2
                        break

            elif choice == "2":
                # Plan a cycling route
                planner.plan_route()

            elif choice == "3":
                # View saved routes
                planner.view_saved_routes()

            elif choice == "4":
                # Cycling impact calculator
                planner.cycling_impact_calculator()

    def _get_sample_weather_data(self) -> Dict:
        """
        Return sample weather data for demonstration purposes.
        Used when API key is not available.
        """
        # Generate weather data based on the current date
        current_date = datetime.now()

        # Create sample current weather
        current_weather = {
            "name": "Sample City",
            "main": {
                "temp": 22.5,
                "feels_like": 23.0,
                "temp_min": 20.0,
                "temp_max": 25.0,
                "humidity": 65
            },
            "wind": {
                "speed": 3.5,
                "deg": 180
            },
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }
            ]
        }

        # Create sample forecast
        forecast_list = []
        weather_types = ["Clear", "Clouds", "Rain", "Clear", "Clear"]
        descriptions = ["clear sky", "scattered clouds", "light rain", "clear sky", "clear sky"]
        icons = ["01d", "03d", "10d", "01d", "01d"]

        for i in range(5):
            forecast_date = current_date + timedelta(days=i)

            # Morning forecast (9 AM)
            morning = forecast_date.replace(hour=9, minute=0, second=0)
            forecast_list.append({
                "dt": int(morning.timestamp()),
                "main": {
                    "temp": 20.0 + i,
                    "feels_like": 21.0 + i,
                    "temp_min": 18.0 + i,
                    "temp_max": 22.0 + i,
                    "humidity": 70 - i * 2
                },
                "wind": {
                    "speed": 3.0 + (i * 0.5),
                    "deg": 180 + (i * 10)
                },
                "weather": [
                    {
                        "main": weather_types[i],
                        "description": descriptions[i],
                        "icon": icons[i]
                    }
                ],
                "dt_txt": morning.strftime("%Y-%m-%d %H:%M:%S")
            })

            # Afternoon forecast (3 PM)
            afternoon = forecast_date.replace(hour=15, minute=0, second=0)
            forecast_list.append({
                "dt": int(afternoon.timestamp()),
                "main": {
                    "temp": 24.0 + i,
                    "feels_like": 25.0 + i,
                    "temp_min": 22.0 + i,
                    "temp_max": 27.0 + i,
                    "humidity": 60 - i * 2
                },
                "wind": {
                    "speed": 4.0 + (i * 0.5),
                    "deg": 200 + (i * 10)
                },
                "weather": [
                    {
                        "main": weather_types[i],
                        "description": descriptions[i],
                        "icon": icons[i]
                    }
                ],
                "dt_txt": afternoon.strftime("%Y-%m-%d %H:%M:%S")
            })

        return {
            "current": current_weather,
            "forecast": {"list": forecast_list}
        }

    def _display_weather(self, weather_data: Dict) -> None:
        """Display weather data in a formatted way."""
        try:
            # Display current weather
            current = weather_data.get("current", {})
            city_name = current.get("name", "Unknown Location")
            current_temp = current.get("main", {}).get("temp", 0)
            feels_like = current.get("main", {}).get("feels_like", 0)
            humidity = current.get("main", {}).get("humidity", 0)
            wind_speed = current.get("wind", {}).get("speed", 0)
            wind_direction = current.get("wind", {}).get("deg", 0)
            weather_main = current.get("weather", [{}])[0].get("main", "Unknown")
            weather_desc = current.get("weather", [{}])[0].get("description", "")

            # Convert to imperial if user preference is set
            use_imperial = False
            if self.user_manager and self.user_manager.is_authenticated():
                use_imperial = self.user_manager.get_user_preference("use_imperial", False)

            if use_imperial:
                temp_unit = "°F"
                speed_unit = "mph"
                current_temp = general_utils.celsius_to_fahrenheit(current_temp)
                feels_like = general_utils.celsius_to_fahrenheit(feels_like)
                wind_speed = general_utils.kmh_to_mph(wind_speed)
            else:
                temp_unit = "°C"
                speed_unit = "km/h"

            # Format wind direction
            direction = self._get_wind_direction(wind_direction)

            # Get cycling recommendation
            recommendation = self._get_cycling_recommendation(current_temp, weather_main, wind_speed)
            recommendation_color = "green"
            if "Not recommended" in recommendation:
                recommendation_color = "red"
            elif "Challenging" in recommendation:
                recommendation_color = "yellow"
            elif "Fair" in recommendation:
                recommendation_color = "blue"

            if HAS_RICH:
                # Create a layout for better organization
                layout = Layout()
                layout.split_column(
                    Layout(name="current"),
                    Layout(name="recommendation"),
                    Layout(name="forecast")
                )

                # Display current weather with Rich formatting
                current_table = Table(show_header=False, box=rich.box.ROUNDED, border_style="cyan")
                current_table.add_column("Property", style="cyan", justify="right")
                current_table.add_column("Value", style="white")

                # Add current weather info rows
                current_table.add_row("Location", f"{city_name}")
                current_table.add_row("Temperature", f"{current_temp:.1f}{temp_unit} (Feels like: {feels_like:.1f}{temp_unit})")
                current_table.add_row("Condition", f"{weather_main} - {weather_desc}")
                current_table.add_row("Humidity", f"{humidity}%")
                current_table.add_row("Wind", f"{wind_speed:.1f} {speed_unit} {direction}")

                # Create a panel with the current weather table
                current_panel = Panel(
                    current_table,
                    title=f"Current Weather for {city_name}",
                    border_style="cyan",
                    padding=(1, 2)
                )
                layout["current"].update(current_panel)

                # Display cycling recommendation
                rec_panel = Panel(
                    f"{recommendation}",
                    title="Cycling Recommendation",
                    border_style=recommendation_color,
                    padding=(1, 2)
                )
                layout["recommendation"].update(rec_panel)

                # Show forecast for next few days
                forecast = weather_data.get("forecast", {}).get("list", [])
                if forecast:
                    # Create a table for the forecast
                    forecast_table = Table(
                        title="5-Day Forecast",
                        box=rich.box.ROUNDED,
                        border_style="blue",
                        show_header=True,
                    )

                    forecast_table.add_column("Day", style="cyan")
                    forecast_table.add_column("Temp", justify="right", style="white")
                    forecast_table.add_column("Conditions", style="white")
                    forecast_table.add_column("Cycling", style="white")

                    # Group forecast by day
                    daily_forecast = {}
                    for item in forecast:
                        date_txt = item.get("dt_txt", "")
                        if not date_txt:
                            continue

                        # Extract date part
                        date = date_txt.split(" ")[0]

                        # Skip today (already shown in current weather)
                        if date == datetime.now().strftime("%Y-%m-%d"):
                            continue

                        if date not in daily_forecast:
                            daily_forecast[date] = []

                        daily_forecast[date].append(item)

                    # Show one item per day (preferably afternoon)
                    for date, items in sorted(daily_forecast.items()):
                        # Prefer afternoon forecast (around 12-15)
                        best_item = items[0]
                        for item in items:
                            time_txt = item.get("dt_txt", "")
                            if "12:" in time_txt or "15:" in time_txt:
                                best_item = item
                                break

                        # Display forecast for this day
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        day_name = date_obj.strftime("%A")
                        temp = best_item.get("main", {}).get("temp", 0)
                        weather = best_item.get("weather", [{}])[0].get("main", "Unknown")
                        desc = best_item.get("weather", [{}])[0].get("description", "")

                        if use_imperial:
                            temp = general_utils.celsius_to_fahrenheit(temp)

                        # Get cycling recommendation for this forecast
                        wind = best_item.get("wind", {}).get("speed", 0)
                        if use_imperial:
                            wind = general_utils.kmh_to_mph(wind)
                        day_recommendation = self._get_cycling_recommendation(temp, weather, wind)

                        # Simplify recommendation for forecast table
                        simple_rec = "Good"
                        rec_style = "green"
                        if "Not recommended" in day_recommendation or "Avoid" in day_recommendation:
                            simple_rec = "Avoid"
                            rec_style = "red"
                        elif "Challenging" in day_recommendation:
                            simple_rec = "Challenging"
                            rec_style = "yellow"
                        elif "Fair" in day_recommendation:
                            simple_rec = "Fair"
                            rec_style = "blue"

                        forecast_table.add_row(
                            day_name,
                            f"{temp:.1f}{temp_unit}",
                            f"{weather} ({desc})",
                            f"[{rec_style}]{simple_rec}[/{rec_style}]"
                        )

                    # Add the forecast table to the layout
                    layout["forecast"].update(forecast_table)

                # Print the entire layout
                console.print(layout)
            else:
                # Print current weather using ASCII formatting
                print(f"\n{ascii_art.Fore.CYAN}{ascii_art.Style.BRIGHT}Current Weather for {city_name}{ascii_art.Style.RESET_ALL}")
                print(f"Temperature: {current_temp:.1f}{temp_unit} (Feels like: {feels_like:.1f}{temp_unit})")
                print(f"Conditions: {weather_main} - {weather_desc}")
                print(f"Humidity: {humidity}%")
                print(f"Wind: {wind_speed:.1f} {speed_unit} {direction}")

                # Print cycling recommendation
                print(f"\n{ascii_art.Fore.YELLOW}Cycling Recommendation: {recommendation}{ascii_art.Style.RESET_ALL}")

                # Show forecast for next few days
                forecast = weather_data.get("forecast", {}).get("list", [])
                if forecast:
                    print(f"\n{ascii_art.Fore.CYAN}{ascii_art.Style.BRIGHT}5-Day Forecast{ascii_art.Style.RESET_ALL}")

                    # Group forecast by day
                    daily_forecast = {}
                    for item in forecast:
                        date_txt = item.get("dt_txt", "")
                        if not date_txt:
                            continue

                        # Extract date part
                        date = date_txt.split(" ")[0]

                        # Skip today (already shown in current weather)
                        if date == datetime.now().strftime("%Y-%m-%d"):
                            continue

                        if date not in daily_forecast:
                            daily_forecast[date] = []

                        daily_forecast[date].append(item)

                    # Show one item per day (preferably afternoon)
                    for date, items in sorted(daily_forecast.items()):
                        # Prefer afternoon forecast (around 12-15)
                        best_item = items[0]
                        for item in items:
                            time_txt = item.get("dt_txt", "").split(" ")[1]
                            if "12:" in time_txt or "15:" in time_txt:
                                best_item = item
                                break

                        # Display forecast for this day
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        day_name = date_obj.strftime("%A")
                        temp = best_item.get("main", {}).get("temp", 0)
                        weather = best_item.get("weather", [{}])[0].get("main", "Unknown")
                        desc = best_item.get("weather", [{}])[0].get("description", "")

                        if use_imperial:
                            temp = general_utils.celsius_to_fahrenheit(temp)

                        print(f"{day_name}: {temp:.1f}{temp_unit} - {weather} ({desc})")

        except Exception as e:
            logger.error(f"Error displaying weather data: {e}")
            print(f"Error displaying weather data: {str(e)}")

    def _get_wind_direction(self, degrees: float) -> str:
        """Convert wind direction in degrees to cardinal direction."""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

        index = round(degrees / 22.5) % 16
        return directions[index]

    def _get_cycling_recommendation(self, temp: float, weather: str, wind_speed: float) -> str:
        """Get cycling recommendation based on weather conditions."""
        # Bad weather conditions
        if weather in ["Thunderstorm", "Tornado", "Hurricane", "Snow", "Sleet", "Hail"]:
            return "Not recommended - Dangerous weather conditions"

        if weather in ["Heavy Rain", "Freezing Rain"]:
            return "Not recommended - Heavy rain conditions"

        # Temperature considerations
        if temp < 0:
            return "Challenging - Very cold, dress in layers and protect extremities"

        if temp < 5:
            return "Challenging - Cold conditions, dress warmly"

        if temp > 35:
            return "Challenging - Very hot, stay hydrated and avoid midday rides"

        # Wind considerations
        if wind_speed > 40:
            return "Not recommended - Dangerously high winds"

        if wind_speed > 25:
            return "Challenging - Strong winds, be cautious"

        # Light rain
        if weather in ["Rain", "Drizzle"]:
            return "Fair - Light rain, use fenders and water-resistant gear"

        # Ideal conditions
        if 10 <= temp <= 25 and weather in ["Clear", "Clouds", "Mist"] and wind_speed < 15:
            return "Excellent - Ideal conditions for cycling"

        # Good conditions
        if 5 <= temp <= 30 and weather not in ["Rain", "Drizzle"] and wind_speed < 20:
            return "Good - Favorable conditions for cycling"

        # Default
        return "Fair - Acceptable conditions but be prepared"

    def _get_cycling_recommendation_simple(self, temp: float, weather: str, wind_speed: float) -> str:
        """Get simplified cycling recommendation for hourly forecasts."""
        # Bad weather conditions
        if weather.lower() in ["thunderstorm", "tornado", "hurricane", "snow", "sleet", "hail"]:
            return "Avoid"

        if "heavy rain" in weather.lower() or "freezing rain" in weather.lower():
            return "Avoid"

        # Temperature considerations
        if temp < 0:
            return "Challenging"

        if temp < 5:
            return "Challenging"

        if temp > 35:
            return "Challenging"

        # Wind considerations
        if wind_speed > 40:
            return "Avoid"

        if wind_speed > 25:
            return "Challenging"

        # Light rain
        if "rain" in weather.lower() or "drizzle" in weather.lower():
            return "Fair"

        # Ideal conditions
        if 10 <= temp <= 25 and ("clear" in weather.lower() or "sunny" in weather.lower() or
                                "partly cloudy" in weather.lower()) and wind_speed < 15:
            return "Excellent"

        # Good conditions
        if 5 <= temp <= 30 and "rain" not in weather.lower() and "snow" not in weather.lower() and wind_speed < 20:
            return "Good"

        # Default
        return "Fair"

    def plan_route(self, start_lat=None, start_lon=None):
        """Plan a cycling route."""
        # Use the route view from the MVC architecture
        self.route_view.display_route_planner_menu(start_lat, start_lon)

    def _get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a location name."""
        # Check if this is a "Current Location" format with coordinates
        coords = self._parse_current_location_format(location)
        if coords:
            logger.info(f"Parsed coordinates from current location format: {coords}")
            return coords

        # Check if it's a default location
        if location in DEFAULT_COORDINATES:
            return DEFAULT_COORDINATES[location]

        # Try using OpenWeatherMap Geocoding API
        if OPENWEATHERMAP_API_KEY and REQUESTS_AVAILABLE:
            try:
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OPENWEATHERMAP_API_KEY}"
                geo_response = requests.get(geo_url)
                geo_data = geo_response.json()

                if geo_data and len(geo_data) > 0:
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]
                    return (lat, lon)
            except Exception as e:
                logger.error(f"Error getting coordinates: {e}")

        # If we get here, we couldn't get coordinates
        return None

    def _parse_current_location_format(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Parse coordinates from "Current Location (lat, lon)" format.

        Args:
            location (str): Location string to parse

        Returns:
            Optional[Tuple[float, float]]: Coordinates if successfully parsed, None otherwise
        """
        import re

        # Pattern to match "Current Location (lat, lon)" format
        pattern = r"Current Location \((-?\d+\.?\d*),\s*(-?\d+\.?\d*)\)"
        match = re.match(pattern, location)

        if match:
            try:
                lat = float(match.group(1))
                lon = float(match.group(2))
                logger.debug(f"Parsed coordinates from '{location}': {lat}, {lon}")
                return (lat, lon)
            except ValueError as e:
                logger.error(f"Error parsing coordinates from '{location}': {e}")
                return None

        return None

    def _get_route(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Optional[Dict]:
        """Get route information between two coordinates."""
        # Check cache first
        cache_key = f"{start_coords[0]},{start_coords[1]}-{end_coords[0]},{end_coords[1]}"
        if cache_key in self.routes_cache:
            return self.routes_cache[cache_key]

        # If we have MapBox API key, use their directions API
        if MAPBOX_ACCESS_TOKEN and REQUESTS_AVAILABLE:
            try:
                url = f"https://api.mapbox.com/directions/v5/mapbox/cycling/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?geometries=geojson&access_token={MAPBOX_ACCESS_TOKEN}"
                response = requests.get(url)
                data = response.json()

                if "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    distance = route["distance"] / 1000  # Convert to kilometers
                    duration = route["duration"] / 60    # Convert to minutes

                    # Get elevation data (this would require additional API calls in a real app)
                    elevation = 0  # Placeholder

                    route_info = {
                        "distance": distance,
                        "duration": duration,
                        "elevation": elevation
                    }

                    # Cache the route
                    self.routes_cache[cache_key] = route_info
                    self._save_cache(self.routes_cache, ROUTES_CACHE_FILE)

                    return route_info
            except Exception as e:
                logger.error(f"Error getting route: {e}")

        # Otherwise, provide a simple estimation
        direct_distance = general_utils.calculate_distance(start_coords[0], start_coords[1], end_coords[0], end_coords[1])
        route_distance = direct_distance * 1.3  # Add 30% for non-direct routes

        # Default speed of 15 km/h
        duration = route_distance / 15 * 60  # Convert to minutes

        route_info = {
            "distance": route_distance,
            "duration": duration,
            "elevation": 0
        }

        # Cache the route
        self.routes_cache[cache_key] = route_info
        self._save_cache(self.routes_cache, ROUTES_CACHE_FILE)

        return route_info

    def _save_route(self, name: str, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                   distance: float, duration: float) -> bool:
        """Save a route to the user's saved routes."""
        if not self.user_manager or not self.user_manager.is_authenticated():
            print("You need to be logged in to save routes.")
            return False

        # Get user's saved routes
        user = self.user_manager.get_current_user()
        if "saved_routes" not in user:
            user["saved_routes"] = []

        # Create route object
        route = {
            "name": name,
            "start_coords": start_coords,
            "end_coords": end_coords,
            "distance": distance,
            "duration": duration,
            "date_saved": datetime.now().isoformat()
        }

        # Add to saved routes
        user["saved_routes"].append(route)

        # Save user data
        if self.user_manager.save_users():
            print(f"Route '{name}' saved successfully!")
            return True
        else:
            print("Error saving route.")
            return False

    def view_saved_routes(self):
        """View and manage saved routes."""
        # Use the route view from the MVC architecture
        self.route_view.display_saved_routes_menu()

    def _display_route_details(self, route: Dict):
        """Display detailed information about a route."""
        name = route.get("name", "Unnamed Route")
        distance = route.get("distance", 0)
        duration = route.get("duration", 0)
        date_saved = route.get("date_saved", "Unknown date")
        start_coords = route.get("start_coords", (0, 0))
        end_coords = route.get("end_coords", (0, 0))

        # Format date if it's a valid ISO format
        if isinstance(date_saved, str) and re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', date_saved):
            try:
                date_obj = datetime.fromisoformat(date_saved)
                date_saved = date_obj.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass

        # Calculate some additional stats
        avg_speed = distance / (duration / 60) if duration > 0 else 0
        calories = general_utils.calculate_calories(distance, avg_speed, 70)  # Assume 70kg rider
        co2_saved = general_utils.calculate_co2_saved(distance)

        # Show equivalents
        trees_day = co2_saved / 0.055  # One tree absorbs about 20kg CO2 per year = 0.055kg per day
        light_bulbs = co2_saved / 0.1  # 100W light bulb for 24 hours ~ 0.1kg CO2

        if HAS_RICH:
            # Display the route details with rich formatting
            console.print()

            # Create a route details panel
            route_layout = Layout()
            route_layout.split_column(
                Layout(name="basic_info"),
                Layout(name="stats"),
                Layout(name="impact")
            )

            # Create a table for basic route info
            basic_table = Table(box=ROUNDED, border_style="cyan", show_header=False)
            basic_table.add_column("Parameter", style="cyan", justify="right")
            basic_table.add_column("Value", style="green")

            # Add route details to table
            basic_table.add_row("Name", f"[bold]{name}[/bold]")
            basic_table.add_row("Distance", f"{distance:.1f} km")
            basic_table.add_row("Duration", f"{duration:.0f} minutes")
            basic_table.add_row("Date saved", f"{date_saved}")
            basic_table.add_row("Starting point", f"{start_coords[0]:.6f}, {start_coords[1]:.6f}")
            basic_table.add_row("Ending point", f"{end_coords[0]:.6f}, {end_coords[1]:.6f}")

            # Create the panel for basic info
            basic_panel = Panel(
                basic_table,
                title="Route Details",
                border_style="cyan",
                box=ROUNDED
            )
            route_layout["basic_info"].update(basic_panel)

            # Create stats table
            stats_table = Table(box=ROUNDED, border_style="blue", show_header=False)
            stats_table.add_column("Stat", style="blue", justify="right")
            stats_table.add_column("Value", style="green")

            # Add stats
            stats_table.add_row("Average Speed", f"{avg_speed:.1f} km/h")
            stats_table.add_row("Calories Burned", f"{calories} (70kg rider)")
            stats_table.add_row("CO₂ Saved", f"{co2_saved:.2f} kg")

            # Create the panel for stats
            stats_panel = Panel(
                stats_table,
                title="Cycling Statistics",
                border_style="blue",
                box=ROUNDED
            )
            route_layout["stats"].update(stats_panel)

            # Create environmental impact panel
            impact_text = Text.from_markup(
                f"By cycling this route instead of driving, you save [bold green]{co2_saved:.2f} kg[/bold green] of CO₂ emissions.\n\n"
                f"This is equivalent to:\n"
                f"• The daily CO₂ absorption of [green]{trees_day:.1f} trees[/green]\n"
                f"• The emissions from [green]{light_bulbs:.1f} light bulbs[/green] (100W) running for 24 hours"
            )

            # Create the panel for environmental impact
            impact_panel = Panel(
                impact_text,
                title="Environmental Impact",
                border_style="green",
                box=ROUNDED
            )
            route_layout["impact"].update(impact_panel)

            # Display the complete layout
            console.print(route_layout)

            # Add action buttons
            console.print(Rule("Options", style="yellow"))
            console.print("[cyan]1.[/cyan] View on map")
            console.print("[cyan]2.[/cyan] Edit route name")
            console.print("[cyan]3.[/cyan] Return to saved routes")

        else:
            # Standard text output for non-Rich environments
            print("\nRoute Details:")
            print(f"Name: {name}")
            print(f"Distance: {distance:.1f} km")
            print(f"Estimated duration: {duration:.0f} minutes")
            print(f"Date saved: {date_saved}")
            print(f"Starting coordinates: {start_coords[0]:.6f}, {start_coords[1]:.6f}")
            print(f"Ending coordinates: {end_coords[0]:.6f}, {end_coords[1]:.6f}")

            print("\nEstimated Statistics:")
            print(f"Average speed: {avg_speed:.1f} km/h")
            print(f"Calories burned (70kg rider): {calories}")
            print(f"CO₂ Saved: {co2_saved:.2f} kg")

            print("\nThis is equivalent to:")
            print(f"- The daily CO₂ absorption of {trees_day:.1f} trees")
            print(f"- The emissions from {light_bulbs:.1f} 100W light bulbs running for 24 hours")

            print("\nOptions:")
            print("1. View on map")
            print("2. Edit route name")
            print("3. Return to saved routes")

    def _generate_route_map(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float],
                           title: str = "Cycling Route") -> Optional[str]:
        """Generate a route map between two points and save it as HTML."""
        if not FOLIUM_AVAILABLE:
            return None

        try:
            # Calculate center point
            center_lat = (start_coords[0] + end_coords[0]) / 2
            center_lon = (start_coords[1] + end_coords[1]) / 2

            # Create map
            cycling_map = folium.Map(location=[center_lat, center_lon], zoom_start=10)

            # Add markers
            folium.Marker(
                location=[start_coords[0], start_coords[1]],
                popup="Start",
                icon=folium.Icon(icon="play", color="green")
            ).add_to(cycling_map)

            folium.Marker(
                location=[end_coords[0], end_coords[1]],
                popup="End",
                icon=folium.Icon(icon="stop", color="red")
            ).add_to(cycling_map)

            # Add a simple line for the route
            folium.PolyLine(
                locations=[[start_coords[0], start_coords[1]], [end_coords[0], end_coords[1]]],
                color="blue",
                weight=5,
                opacity=0.8
            ).add_to(cycling_map)

            # Add title
            folium.map.Marker(
                [start_coords[0], start_coords[1]],
                icon=folium.DivIcon(
                    icon_size=(150, 36),
                    icon_anchor=(75, 60),
                    html=f'<div style="font-size: 14pt; font-weight: bold; color: blue">{title}</div>'
                )
            ).add_to(cycling_map)

            # Save map
            filename = f"route_map_{int(time.time())}.html"
            cycling_map.save(filename)

            return filename

        except Exception as e:
            logger.error(f"Error generating map: {e}")
            print(f"Error generating map: {str(e)}")
            return None

    def check_weather(self, location_override: Optional[str] = None):
        """
        Check weather for cycling with optional location override.

        Args:
            location_override (Optional[str]): Specific location to check weather for
        """
        # Get weather controller to handle API calls
        from controllers.weather_controller import WeatherController
        weather_controller = WeatherController()

        # Create a weather view to display results
        from views.weather_view import WeatherView
        weather_view = WeatherView(weather_controller, self.user_manager, ascii_art)

        # Clear screen and show header
        ascii_art.clear_screen()
        ascii_art.display_header()

        if location_override:
            # Get weather for specific location
            if HAS_RICH:
                with Progress(
                    SpinnerColumn(),
                    TextColumn(f"[bold blue]Getting weather data for {location_override}...[/bold blue]"),
                    BarColumn(),
                    TimeElapsedColumn(),
                    transient=True
                ) as progress:
                    task = progress.add_task("Loading...", total=100)
                    # Simulate progress
                    for i in range(0, 50, 5):
                        time.sleep(0.05)
                        progress.update(task, completed=i)

                    # Get weather data for specific location
                    weather_data = weather_controller.get_weather_for_city(location_override)

                    # Continue progress
                    for i in range(50, 101, 5):
                        time.sleep(0.03)
                        progress.update(task, completed=i)
            else:
                print(f"\nGetting weather data for {location_override}...")
                weather_data = weather_controller.get_weather_for_city(location_override)

            # Clear screen for display
            ascii_art.clear_screen()

            # Display weather data
            if weather_data:
                if HAS_RICH:
                    console.print(Panel.fit(
                        Text(f"Weather Forecast for {location_override}", style="bold cyan"),
                        border_style="cyan"
                    ))
                else:
                    ascii_art.display_section_header(f"Weather Forecast for {location_override}")

                weather_view.display_weather_data(weather_data)

                # Show cycling recommendation
                recommendation = weather_controller.get_cycling_recommendation(weather_data)
                if HAS_RICH:
                    rec_color = "green" if "Good" in recommendation else "yellow" if "Fair" in recommendation else "red"
                    rec_panel = Panel(
                        f"[{rec_color}]{recommendation}[/{rec_color}]",
                        title="Cycling Recommendation",
                        border_style=rec_color,
                        box=ROUNDED
                    )
                    console.print(rec_panel)
                else:
                    print(f"\nCycling Recommendation: {recommendation}")
            else:
                if HAS_RICH:
                    console.print(Panel(
                        f"Could not retrieve weather data for {location_override}.\n"
                        "Please check the location name and try again.",
                        title="Error",
                        border_style="red",
                        box=ROUNDED
                    ))
                else:
                    print(f"\nCould not retrieve weather data for {location_override}.")
                    print("Please check the location name and try again.")

            # Prompt to continue
            if HAS_RICH:
                console.input("\n[cyan]Press Enter to continue...[/cyan]")
            else:
                input("\nPress Enter to continue...")
        else:
            # Show weather menu for interactive selection
            while True:
                # Show weather menu and get user choice
                option = weather_view.display_weather_menu()

                if option == "0":
                    # Exit
                    break
                elif option == "1":
                    # Get current weather & 3-hour forecast
                    if HAS_RICH:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[bold blue]Getting current weather data...[/bold blue]"),
                            BarColumn(),
                            TimeElapsedColumn(),
                            transient=True
                        ) as progress:
                            task = progress.add_task("Loading...", total=100)
                            # Simulate progress
                            for i in range(0, 50, 5):
                                time.sleep(0.05)
                                progress.update(task, completed=i)

                            # Get weather data
                            weather_data = weather_controller.get_current_weather()

                            # Continue progress
                            for i in range(50, 101, 5):
                                time.sleep(0.03)
                                progress.update(task, completed=i)
                    else:
                        print("\nGetting current weather data...")
                        weather_data = weather_controller.get_current_weather()

                    # Clear screen for display
                    ascii_art.clear_screen()

                    # Display weather data
                    if weather_data:
                        if HAS_RICH:
                            console.print(Panel.fit(
                                Text("Current Weather & 3-Hour Forecast", style="bold cyan"),
                                border_style="cyan"
                            ))
                        else:
                            ascii_art.display_section_header("Current Weather & 3-Hour Forecast")

                        weather_view.display_weather_data(weather_data)
                    else:
                        if HAS_RICH:
                            console.print(Panel(
                                "Could not retrieve weather data.\n"
                                "Please check your internet connection and try again.",
                                title="Error",
                                border_style="red",
                                box=ROUNDED
                            ))
                        else:
                            print("\nCould not retrieve weather data.")
                            print("Please check your internet connection and try again.")

                    # Prompt to continue
                    if HAS_RICH:
                        console.input("\n[cyan]Press Enter to continue...[/cyan]")
                    else:
                        input("\nPress Enter to continue...")

                elif option == "2":
                    # Get 2-day forecast
                    if HAS_RICH:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[bold blue]Getting forecast data...[/bold blue]"),
                            BarColumn(),
                            TimeElapsedColumn(),
                            transient=True
                        ) as progress:
                            task = progress.add_task("Loading...", total=100)
                            # Simulate progress
                            for i in range(0, 50, 5):
                                time.sleep(0.05)
                                progress.update(task, completed=i)

                            # Get weather data
                            weather_data = weather_controller.get_current_weather()

                            # Continue progress
                            for i in range(50, 101, 5):
                                time.sleep(0.03)
                                progress.update(task, completed=i)
                    else:
                        print("\nGetting forecast data...")
                        weather_data = weather_controller.get_current_weather()

                    # Clear screen for display
                    ascii_art.clear_screen()

                    # Display weather data
                    if weather_data:
                        if HAS_RICH:
                            console.print(Panel.fit(
                                Text("2-Day Weather Forecast", style="bold cyan"),
                                border_style="cyan"
                            ))
                        else:
                            ascii_art.display_section_header("2-Day Weather Forecast")

                        weather_view.display_weather_data(weather_data)
                    else:
                        if HAS_RICH:
                            console.print(Panel(
                                "Could not retrieve forecast data.\n"
                                "Please check your internet connection and try again.",
                                title="Error",
                                border_style="red",
                                box=ROUNDED
                            ))
                        else:
                            print("\nCould not retrieve forecast data.")
                            print("Please check your internet connection and try again.")

                    # Prompt to continue
                    if HAS_RICH:
                        console.input("\n[cyan]Press Enter to continue...[/cyan]")
                    else:
                        input("\nPress Enter to continue...")

                elif option == "3":
                    # Get cycling conditions
                    if HAS_RICH:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[bold blue]Analyzing cycling conditions...[/bold blue]"),
                            BarColumn(),
                            TimeElapsedColumn(),
                            transient=True
                        ) as progress:
                            task = progress.add_task("Analyzing...", total=100)
                            # Simulate progress
                            for i in range(0, 50, 5):
                                time.sleep(0.05)
                                progress.update(task, completed=i)

                            # Get weather data
                            weather_data = weather_controller.get_current_weather()

                            # Continue progress
                            for i in range(50, 101, 5):
                                time.sleep(0.03)
                                progress.update(task, completed=i)
                    else:
                        print("\nAnalyzing cycling conditions...")
                        weather_data = weather_controller.get_current_weather()

                    # Clear screen for display
                    ascii_art.clear_screen()

                    # Display cycling conditions
                    if weather_data:
                        if HAS_RICH:
                            console.print(Panel.fit(
                                Text("Cycling Conditions & Recommendations", style="bold cyan"),
                                border_style="cyan"
                            ))

                            # Get recommendation
                            recommendation = weather_controller.get_cycling_recommendation(weather_data)
                            rec_color = "green" if "Good" in recommendation else "yellow" if "Fair" in recommendation else "red"

                            # Current weather
                            current_temp = weather_data.get_current_temperature()
                            weather_main = weather_data.get_current_weather_condition()
                            weather_desc = weather_data.get_current_weather_description()
                            wind_speed = weather_data.get_current_wind_speed()
                            wind_direction = weather_controller.get_wind_direction_text(weather_data.get_current_wind_direction())
                            humidity = weather_data.get_current_humidity()

                            # Display current conditions in a panel
                            current_panel = Panel(
                                f"[bold cyan]{current_temp:.1f}°C[/bold cyan] [dim]with[/dim] [white]{weather_main}[/white]: {weather_desc}\n"
                                f"Wind: {wind_speed:.1f} km/h {wind_direction}\n"
                                f"Humidity: {humidity}%",
                                title="Current Weather",
                                border_style="blue",
                                box=ROUNDED
                            )
                            console.print(current_panel)

                            # Display recommendations in a panel
                            rec_panel = Panel(
                                f"[{rec_color}]{recommendation}[/{rec_color}]",
                                title="Cycling Recommendation",
                                border_style=rec_color,
                                box=ROUNDED
                            )
                            console.print(rec_panel)
                        else:
                            ascii_art.display_section_header("Cycling Conditions & Recommendations")

                            # Get recommendation
                            recommendation = weather_controller.get_cycling_recommendation(weather_data)

                            # Current weather
                            current_temp = weather_data.get_current_temperature()
                            weather_main = weather_data.get_current_weather_condition()
                            weather_desc = weather_data.get_current_weather_description()
                            wind_speed = weather_data.get_current_wind_speed()
                            wind_direction = weather_controller.get_wind_direction_text(weather_data.get_current_wind_direction())
                            humidity = weather_data.get_current_humidity()

                            # Display current conditions
                            print(f"\nCurrent Weather:")
                            print(f"Temperature: {current_temp:.1f}°C")
                            print(f"Conditions: {weather_main} - {weather_desc}")
                            print(f"Wind: {wind_speed:.1f} km/h {wind_direction}")
                            print(f"Humidity: {humidity}%")

                            # Display recommendation
                            print(f"\nCycling Recommendation:")
                            print(f"{recommendation}")
                    else:
                        if HAS_RICH:
                            console.print(Panel(
                                "Could not retrieve weather data for cycling conditions.\n"
                                "Please check your internet connection and try again.",
                                title="Error",
                                border_style="red",
                                box=ROUNDED
                            ))
                        else:
                            print("\nCould not retrieve weather data for cycling conditions.")
                            print("Please check your internet connection and try again.")

                    # Prompt to continue
                    if HAS_RICH:
                        console.input("\n[cyan]Press Enter to continue...[/cyan]")
                    else:
                        input("\nPress Enter to continue...")

                elif option == "4":
                    # Plan a cycling route - go back to main planner and select option 2
                    break

    def cycling_impact_calculator(self):
        """Calculate environmental and health impact of cycling."""
        # Use the route view from the MVC architecture
        self.route_view.display_cycling_impact_calculator()

    def calculate_cycling_eco_impact(self, distance: float) -> None:
        """Calculate and display environmental impact of a cycling trip."""
        # Calculate CO2 savings
        co2_saved = general_utils.calculate_co2_saved(distance)

        # Calculate fuel savings (rough estimate - 7 liters per 100 km for average car)
        fuel_saved = distance * 0.07  # liters

        # Calculate money saved (rough estimate - average fuel price $1.5 per liter)
        money_saved = fuel_saved * 1.5  # dollars

        # Calculate equivalents
        trees_day = co2_saved / 0.055  # One tree absorbs about 20kg CO2 per year = 0.055kg per day
        light_bulbs = co2_saved / 0.1  # 100W light bulb for 24 hours ~ 0.1kg CO2
        car_km = distance  # Direct comparison - same distance by car

        if HAS_RICH:
            # Display results with Rich UI
            console.clear()

            # Create a layout for the header
            layout = Layout()
            layout.split(
                Layout(name="header", size=3),
                Layout(name="main")
            )

            # Create a stylish header
            title = Text("Cycling Environmental Impact", style="bold green")
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
                f"Environmental impact analysis for a {distance:.1f} km cycling trip",
                box=ROUNDED,
                border_style="blue",
                padding=(1, 2)
            ))

            # Create impact layout with two panels side by side
            impact_layout = Layout()
            impact_layout.split_row(
                Layout(name="savings"),
                Layout(name="equivalents")
            )

            # Create savings table
            savings_table = Table(box=ROUNDED, border_style="green", show_header=False)
            savings_table.add_column("Item", style="cyan", justify="right")
            savings_table.add_column("Value", style="green")

            # Add savings data
            savings_table.add_row("CO₂ Emissions Saved", f"{co2_saved:.2f} kg")
            savings_table.add_row("Fuel Saved", f"{fuel_saved:.2f} liters")
            savings_table.add_row("Money Saved", f"${money_saved:.2f}")

            # Create savings panel
            savings_panel = Panel(
                savings_table,
                title="Your Savings",
                border_style="green",
                box=ROUNDED
            )
            impact_layout["savings"].update(savings_panel)

            # Create equivalents table
            equiv_table = Table(box=ROUNDED, border_style="cyan", show_header=False)
            equiv_table.add_column("Equivalent To", style="cyan", justify="right")
            equiv_table.add_column("Value", style="green")

            # Add equivalents data
            equiv_table.add_row("Trees Filtering Air", f"{trees_day:.1f} trees for one day")
            equiv_table.add_row("Light Bulbs", f"{light_bulbs:.1f} 100W bulbs for 24 hours")
            equiv_table.add_row("Car Travel", f"{car_km:.1f} km not driven")

            # Create equivalents panel
            equiv_panel = Panel(
                equiv_table,
                title="Environmental Equivalents",
                border_style="cyan",
                box=ROUNDED
            )
            impact_layout["equivalents"].update(equiv_panel)

            # Display the impact layout
            console.print(impact_layout)

            # Add a visual comparison
            console.print(Rule("Visual Comparison", style="yellow"))

            # Display a simple bar chart showing emissions comparison
            car_emissions = distance * 0.2  # ~200g CO2 per km
            bike_emissions = 0  # Negligible emissions

            # Calculate bar lengths for visualization
            max_width = 50
            car_bar_width = max_width  # Full width for car
            bike_bar_width = int(bike_emissions / car_emissions * max_width) if car_emissions > 0 else 0  # Should be zero

            # Create visual bar chart
            console.print("[bold]Emissions Comparison:[/bold]")
            console.print(f"Car:  [red]{'█' * car_bar_width}[/red] {car_emissions:.2f} kg CO₂")
            console.print(f"Bike: [green]{'█' * bike_bar_width}[/green] {bike_emissions:.2f} kg CO₂")
            console.print(f"\n[green]By cycling, you reduced emissions by 100%![/green]")

            # Add yearly impact estimation
            console.print(Rule("Annual Impact", style="blue"))

            # Calculate annual impact if this trip was done weekly
            annual_co2 = co2_saved * 52
            annual_fuel = fuel_saved * 52
            annual_money = money_saved * 52

            annual_text = Text.from_markup(
                f"If you make this trip once a week for a year, you would save:\n\n"
                f"• [bold green]{annual_co2:.2f}[/bold green] kg of CO₂ emissions\n"
                f"• [bold green]{annual_fuel:.2f}[/bold green] liters of fuel\n"
                f"• [bold green]${annual_money:.2f}[/bold green] in fuel costs\n\n"
                f"This is the equivalent of planting [bold green]{annual_co2/20:.1f}[/bold green] trees!"
            )

            console.print(Panel(
                annual_text,
                title="Your Annual Environmental Impact",
                border_style="blue",
                box=ROUNDED
            ))

            # Display bottom prompt
            console.print()
            Prompt.ask("[cyan]Press Enter to continue[/cyan]")

        else:
            # Display results with simple text
            print("\nEnvironmental Impact of Your Cycling Trip:")
            print(f"CO2 emissions saved: {co2_saved:.2f} kg")
            print(f"Fuel saved: {fuel_saved:.2f} liters")
            print(f"Money saved on fuel: ${money_saved:.2f}")

            print("\nThis is equivalent to:")
            print(f"- The daily CO2 absorption of {trees_day:.1f} trees")
            print(f"- The emissions from {light_bulbs:.1f} 100W light bulbs running for 24 hours")

            # Calculate annual impact if this trip was done weekly
            annual_co2 = co2_saved * 52
            annual_fuel = fuel_saved * 52
            annual_money = money_saved * 52

            print("\nAnnual Impact (if done weekly):")
            print(f"- CO2 Saved: {annual_co2:.2f} kg")
            print(f"- Fuel Saved: {annual_fuel:.2f} liters")
            print(f"- Money Saved: ${annual_money:.2f}")

            input("\nPress Enter to continue...")


def run_planner(user_manager_instance=None):
    """
    Run the weather and route planner interface.

    Args:
        user_manager_instance: Optional user manager instance
    """
    # Create a new instance of the weather route planner
    planner = WeatherRoutePlanner(user_manager_instance)

    while True:
        # Show the main menu and get user choice
        ascii_art.clear_screen()
        ascii_art.display_header()

        # Use Rich UI if available
        if HAS_RICH:
            # Display header with Rich styling
            console.print(Panel.fit(
                Text("Weather and Route Planner", style="bold cyan"),
                border_style="cyan"
            ))

            # Display description with Rich styling
            console.print(Panel(
                "Plan your cycling routes with real-time weather updates and optimize your journey.\n"
                "Get forecasts, map routes, and receive cycling condition recommendations.",
                border_style="green"
            ))

            # Create a menu table
            menu_table = Table(show_header=False, box=rich.box.ROUNDED, border_style="blue")
            menu_table.add_column("Option", style="cyan")
            menu_table.add_column("Description", style="green")

            # Add exit option
            menu_table.add_row("0", "[yellow]Return to Main Menu[/yellow]")

            # Add menu options
            menu_table.add_row("1", "[cyan]Check Weather Forecast for Cycling[/cyan]")
            menu_table.add_row("2", "[cyan]Plan Cycling Route[/cyan]")
            menu_table.add_row("3", "[cyan]View Saved Routes[/cyan]")
            menu_table.add_row("4", "[cyan]Cycling Impact Calculator[/cyan]")

            # Display the menu
            console.print(Panel(menu_table, title="Route Planning Options", border_style="blue"))
            choice = console.input("[cyan]Select an option:[/cyan] ")
        else:
            # Fallback to ASCII art display
            ascii_art.display_section_header("Weather and Route Planner")

            print("\nPlan your cycling routes with real-time weather updates.")

            print("\nOptions:")
            print(f"  {ascii_art.Fore.YELLOW}0. Return to Main Menu{ascii_art.Style.RESET_ALL}")
            print(f"  {ascii_art.Fore.CYAN}1. Check Weather Forecast for Cycling{ascii_art.Style.RESET_ALL}")
            print(f"  {ascii_art.Fore.GREEN}2. Plan Cycling Route{ascii_art.Style.RESET_ALL}")
            print(f"  {ascii_art.Fore.BLUE}3. View Saved Routes{ascii_art.Style.RESET_ALL}")
            print(f"  {ascii_art.Fore.MAGENTA}4. Cycling Impact Calculator{ascii_art.Style.RESET_ALL}")

            choice = input("\nSelect an option (0-4): ")

        # Process the user's choice
        if choice == "0":
            # Return to main menu
            break
        elif choice == "1":
            # Get weather controller to handle API calls
            from controllers.weather_controller import WeatherController
            weather_controller = WeatherController()

            # Create a weather view to display results
            from views.weather_view import WeatherView
            weather_view = WeatherView(weather_controller, user_manager_instance, ascii_art)

            while True:
                # Show weather menu and get user choice
                option = weather_view.display_weather_menu()

                if option == "0":
                    # Exit to route planner menu
                    break
                elif option == "1":
                    # Get current weather & 3-hour forecast
                    if HAS_RICH:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[bold blue]Getting current weather data...[/bold blue]"),
                            BarColumn(),
                            TimeElapsedColumn(),
                            transient=True
                        ) as progress:
                            task = progress.add_task("Loading...", total=100)
                            # Simulate progress
                            for i in range(0, 50, 5):
                                time.sleep(0.05)
                                progress.update(task, completed=i)

                            # Get weather data
                            weather_data = weather_controller.get_current_weather()

                            # Continue progress
                            for i in range(50, 101, 5):
                                time.sleep(0.03)
                                progress.update(task, completed=i)
                    else:
                        print("\nGetting current weather data...")
                        weather_data = weather_controller.get_current_weather()

                    # Clear screen for display
                    ascii_art.clear_screen()

                    # Display weather data
                    if weather_data:
                        if HAS_RICH:
                            console.print(Panel.fit(
                                Text("Current Weather & 3-Hour Forecast", style="bold cyan"),
                                border_style="cyan"
                            ))
                        else:
                            ascii_art.display_section_header("Current Weather & 3-Hour Forecast")

                        weather_view.display_weather_data(weather_data)
                    else:
                        if HAS_RICH:
                            console.print(Panel(
                                "Could not retrieve weather data.\n"
                                "Please check your internet connection and try again.",
                                title="Error",
                                border_style="red",
                                box=rich.box.ROUNDED
                            ))
                        else:
                            print("\nCould not retrieve weather data.")
                            print("Please check your internet connection and try again.")

                    # Prompt to continue
                    if HAS_RICH:
                        console.input("\n[cyan]Press Enter to continue...[/cyan]")
                    else:
                        input("\nPress Enter to continue...")

                elif option == "2":
                    # Get 2-day forecast
                    if HAS_RICH:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[bold blue]Getting forecast data...[/bold blue]"),
                            BarColumn(),
                            TimeElapsedColumn(),
                            transient=True
                        ) as progress:
                            task = progress.add_task("Loading...", total=100)
                            # Simulate progress
                            for i in range(0, 50, 5):
                                time.sleep(0.05)
                                progress.update(task, completed=i)

                            # Get weather data
                            weather_data = weather_controller.get_current_weather()

                            # Continue progress
                            for i in range(50, 101, 5):
                                time.sleep(0.03)
                                progress.update(task, completed=i)
                    else:
                        print("\nGetting forecast data...")
                        weather_data = weather_controller.get_current_weather()

                    # Clear screen for display
                    ascii_art.clear_screen()

                    # Display weather data
                    if weather_data:
                        if HAS_RICH:
                            console.print(Panel.fit(
                                Text("2-Day Weather Forecast", style="bold cyan"),
                                border_style="cyan"
                            ))
                        else:
                            ascii_art.display_section_header("2-Day Weather Forecast")

                        weather_view.display_weather_data(weather_data)
                    else:
                        if HAS_RICH:
                            console.print(Panel(
                                "Could not retrieve forecast data.\n"
                                "Please check your internet connection and try again.",
                                title="Error",
                                border_style="red",
                                box=rich.box.ROUNDED
                            ))
                        else:
                            print("\nCould not retrieve forecast data.")
                            print("Please check your internet connection and try again.")

                    # Prompt to continue
                    if HAS_RICH:
                        console.input("\n[cyan]Press Enter to continue...[/cyan]")
                    else:
                        input("\nPress Enter to continue...")

                elif option == "3":
                    # Get cycling conditions
                    if HAS_RICH:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[bold blue]Analyzing cycling conditions...[/bold blue]"),
                            BarColumn(),
                            TimeElapsedColumn(),
                            transient=True
                        ) as progress:
                            task = progress.add_task("Analyzing...", total=100)
                            # Simulate progress
                            for i in range(0, 50, 5):
                                time.sleep(0.05)
                                progress.update(task, completed=i)

                            # Get weather data
                            weather_data = weather_controller.get_current_weather()

                            # Continue progress
                            for i in range(50, 101, 5):
                                time.sleep(0.03)
                                progress.update(task, completed=i)
                    else:
                        print("\nAnalyzing cycling conditions...")
                        weather_data = weather_controller.get_current_weather()

                    # Clear screen for display
                    ascii_art.clear_screen()

                    # Display cycling conditions
                    if weather_data:
                        if HAS_RICH:
                            console.print(Panel.fit(
                                Text("Cycling Conditions & Recommendations", style="bold cyan"),
                                border_style="cyan"
                            ))

                            # Get recommendation
                            recommendation = weather_controller.get_cycling_recommendation(weather_data)
                            rec_color = "green" if "Good" in recommendation else "yellow" if "Fair" in recommendation else "red"

                            # Current weather
                            current_temp = weather_data.get_current_temperature()
                            weather_main = weather_data.get_current_weather_condition()
                            weather_desc = weather_data.get_current_weather_description()
                            wind_speed = weather_data.get_current_wind_speed()
                            wind_direction = weather_controller.get_wind_direction_text(weather_data.get_current_wind_direction())
                            humidity = weather_data.get_current_humidity()

                            # Display current conditions in a panel
                            current_panel = Panel(
                                f"[bold cyan]{current_temp:.1f}°C[/bold cyan] [dim]with[/dim] [white]{weather_main}[/white]: {weather_desc}\n"
                                f"Wind: {wind_speed:.1f} km/h {wind_direction}\n"
                                f"Humidity: {humidity}%",
                                title="Current Weather",
                                border_style="blue",
                                box=rich.box.ROUNDED
                            )
                            console.print(current_panel)

                            # Display recommendations in a panel
                            rec_panel = Panel(
                                f"[{rec_color}]{recommendation}[/{rec_color}]",
                                title="Cycling Recommendation",
                                border_style=rec_color,
                                box=rich.box.ROUNDED
                            )
                            console.print(rec_panel)

                            # Display detailed cycling tips
                            console.print(Rule("Detailed Cycling Tips", style="cyan"))

                            tips_table = Table(box=rich.box.ROUNDED, border_style="green")
                            tips_table.add_column("Category", style="cyan")
                            tips_table.add_column("Recommendation", style="green")

                            # Add clothing recommendation based on temperature
                            if current_temp < 5:
                                tips_table.add_row("Clothing", "Heavy winter gear with thermal layers, full gloves, and face protection")
                            elif current_temp < 10:
                                tips_table.add_row("Clothing", "Winter cycling jacket, thermal tights, full finger gloves")
                            elif current_temp < 15:
                                tips_table.add_row("Clothing", "Long sleeve jersey, cycling pants, light gloves")
                            elif current_temp < 20:
                                tips_table.add_row("Clothing", "Light long sleeve or short sleeve jersey, cycling shorts")
                            else:
                                tips_table.add_row("Clothing", "Lightweight and breathable clothing, shorts, short sleeve jersey")

                            # Add visibility recommendation based on conditions
                            if "rain" in weather_desc.lower() or "fog" in weather_desc.lower() or "mist" in weather_desc.lower():
                                tips_table.add_row("Visibility", "Use front and rear lights, wear high-visibility clothing")
                            else:
                                tips_table.add_row("Visibility", "Standard visibility gear should be sufficient")

                            # Add hydration recommendation based on temperature
                            if current_temp > 25:
                                tips_table.add_row("Hydration", "Bring extra water, hydrate every 15-20 minutes")
                            elif current_temp > 15:
                                tips_table.add_row("Hydration", "Bring sufficient water, hydrate regularly")
                            else:
                                tips_table.add_row("Hydration", "Standard hydration, warm drink recommended")

                            # Add route recommendation based on wind and conditions
                            if wind_speed > 20:
                                tips_table.add_row("Route", "Choose sheltered routes, avoid open areas with crosswinds")
                            elif "rain" in weather_desc.lower():
                                tips_table.add_row("Route", "Choose routes with good drainage, avoid dirt paths")
                            else:
                                tips_table.add_row("Route", "All routes suitable based on current conditions")

                            console.print(tips_table)
                        else:
                            ascii_art.display_section_header("Cycling Conditions & Recommendations")

                            # Get recommendation
                            recommendation = weather_controller.get_cycling_recommendation(weather_data)

                            # Current weather
                            current_temp = weather_data.get_current_temperature()
                            weather_main = weather_data.get_current_weather_condition()
                            weather_desc = weather_data.get_current_weather_description()
                            wind_speed = weather_data.get_current_wind_speed()
                            wind_direction = weather_controller.get_wind_direction_text(weather_data.get_current_wind_direction())
                            humidity = weather_data.get_current_humidity()

                            # Display current conditions
                            print(f"\nCurrent Weather:")
                            print(f"Temperature: {current_temp:.1f}°C")
                            print(f"Conditions: {weather_main} - {weather_desc}")
                            print(f"Wind: {wind_speed:.1f} km/h {wind_direction}")
                            print(f"Humidity: {humidity}%")

                            # Display recommendation
                            print(f"\nCycling Recommendation:")
                            print(f"{recommendation}")

                            # Display detailed cycling tips
                            print("\nDetailed Cycling Tips:")

                            # Clothing recommendation based on temperature
                            print("\nClothing:")
                            if current_temp < 5:
                                print("Heavy winter gear with thermal layers, full gloves, and face protection")
                            elif current_temp < 10:
                                print("Winter cycling jacket, thermal tights, full finger gloves")
                            elif current_temp < 15:
                                print("Long sleeve jersey, cycling pants, light gloves")
                            elif current_temp < 20:
                                print("Light long sleeve or short sleeve jersey, cycling shorts")
                            else:
                                print("Lightweight and breathable clothing, shorts, short sleeve jersey")

                            # Visibility recommendation
                            print("\nVisibility:")
                            if "rain" in weather_desc.lower() or "fog" in weather_desc.lower() or "mist" in weather_desc.lower():
                                print("Use front and rear lights, wear high-visibility clothing")
                            else:
                                print("Standard visibility gear should be sufficient")

                            # Hydration recommendation
                            print("\nHydration:")
                            if current_temp > 25:
                                print("Bring extra water, hydrate every 15-20 minutes")
                            elif current_temp > 15:
                                print("Bring sufficient water, hydrate regularly")
                            else:
                                print("Standard hydration, warm drink recommended")

                            # Route recommendation
                            print("\nRoute:")
                            if wind_speed > 20:
                                print("Choose sheltered routes, avoid open areas with crosswinds")
                            elif "rain" in weather_desc.lower():
                                print("Choose routes with good drainage, avoid dirt paths")
                            else:
                                print("All routes suitable based on current conditions")
                    else:
                        if HAS_RICH:
                            console.print(Panel(
                                "Could not retrieve weather data for cycling conditions.\n"
                                "Please check your internet connection and try again.",
                                title="Error",
                                border_style="red",
                                box=rich.box.ROUNDED
                            ))
                        else:
                            print("\nCould not retrieve weather data for cycling conditions.")
                            print("Please check your internet connection and try again.")

                    # Prompt to continue
                    if HAS_RICH:
                        console.input("\n[cyan]Press Enter to continue...[/cyan]")
                    else:
                        input("\nPress Enter to continue...")

                elif option == "4":
                    # Plan a cycling route - go back to main planner and select option 2
                    break

        elif choice == "2":
            # Plan a cycling route
            planner.plan_route()

        elif choice == "3":
            # View saved routes
            planner.view_saved_routes()

        elif choice == "4":
            # Cycling impact calculator
            planner.cycling_impact_calculator()


def check_weather(user_manager_instance=None, location_override: Optional[str] = None):
    """
    Standalone function to check weather for cycling.

    Args:
        user_manager_instance: Optional user manager instance
        location_override (Optional[str]): Specific location to check weather for
    """
    # Create a weather route planner instance
    planner = WeatherRoutePlanner(user_manager_instance)

    # Call the check_weather method
    planner.check_weather(location_override)


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run the planner
    run_planner()
