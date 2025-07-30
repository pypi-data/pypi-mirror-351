"""
EcoCycle - Weather View

This module defines the WeatherView class, which handles the presentation of weather data to the user.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from controllers.weather_controller import WeatherController
import utils.general_utils
import utils.ascii_art

# Check if the rich module is available
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.rule import Rule
    from rich.box import ROUNDED
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Configure logging
logger = logging.getLogger(__name__)


class WeatherView:
    """
    View class for displaying weather data to the user.
    """

    def __init__(self, controller: Optional[WeatherController] = None, user_manager=None, ascii_art=None):
        """
        Initialize a WeatherView.

        Args:
            controller (Optional[WeatherController]): Controller for weather data
            user_manager: User manager for accessing user preferences
            ascii_art: ASCII art module for display functions
        """
        self.controller = controller or WeatherController()
        self.user_manager = user_manager
        self.ascii_art = ascii_art

    def display_weather_menu(self) -> str:
        """
        Display the weather forecast menu and get user choice.

        Returns:
            str: User's choice
        """
        self.ascii_art.clear_screen()
        self.ascii_art.display_header()

        # Use Rich UI if available
        if HAS_RICH:
            console.print(Panel.fit(
                Text("Weather Forecast for Cycling", style="bold cyan"),
                border_style="cyan"
            ))

            console.print(Panel(
                "Check weather conditions for your cycling routes and get recommendations",
                border_style="blue",
                padding=(1, 2)
            ))
        else:
            self.ascii_art.display_section_header("Weather Forecast")

        # Check for WeatherAPI key
        import os
        weather_api_key = os.environ.get("WEATHER_API_KEY", "")
        if not weather_api_key:
            if HAS_RICH:
                console.print(Panel(
                    "No WeatherAPI key found. Using sample weather data.\n"
                    "To use actual weather data, set the WEATHER_API_KEY environment variable.\n"
                    "You can get a free API key from https://www.weatherapi.com/",
                    title="API Key Missing",
                    border_style="yellow"
                ))
                console.print("[cyan]Press Enter to continue with sample data...[/cyan]")
                input()
            else:
                print("\nNo WeatherAPI key found. Using sample weather data.")
                print("To use actual weather data, set the WEATHER_API_KEY environment variable.")
                print("You can get a free API key from https://www.weatherapi.com/")
                input("\nPress Enter to continue with sample data...")

        if not self.controller.requests_available:
            if HAS_RICH:
                console.print(Panel(
                    "The requests library is required for weather forecast functionality.\n"
                    "Would you like to install the required package now?",
                    title="Missing Dependency",
                    border_style="yellow"
                ))
                install = console.input("[cyan]Install requests? (y/n): [/cyan]")
            else:
                print("The requests library is required for weather forecast functionality.")
                install = input("Would you like to install the required package now? (y/n): ")

            if install.lower() == 'y':
                import core.dependency.dependency_manager
                success, _ = core.dependency.dependency_manager.ensure_feature('weather', silent=False)
                if success:
                    if HAS_RICH:
                        console.print("[green]Successfully installed the required package![/green]")
                        console.print("[cyan]Please restart the application to use this feature.[/cyan]")
                    else:
                        print("Successfully installed the required package!")
                        print("Please restart the application to use this feature.")
                else:
                    if HAS_RICH:
                        console.print("[red]Failed to install the required package.[/red]")
                        console.print("[yellow]Please install it manually with: pip install requests[/yellow]")
                    else:
                        print("Failed to install the required package.")
                        print("Please install it manually with: pip install requests")
            return "0"  # Exit if requests not available

        # Get location
        if HAS_RICH:
            console.print(Rule("Location", style="cyan"))
            location = console.input("[cyan]Enter location[/cyan] (city name or 'current' for current location): ")
        else:
            print("\nEnter location (city name or 'current' for current location):")
            location = input("> ").strip()

        location = location.strip()

        # Handle empty input
        if not location:
            if HAS_RICH:
                console.print("[yellow]No location provided. Using current location.[/yellow]")
            else:
                print("No location provided. Using current location.")
            location = "current"

        # Get coordinates
        if location.lower() == 'current':
            if HAS_RICH:
                with console.status("[cyan]Detecting current location...[/cyan]", spinner="dots"):
                    coords = self.controller.get_current_location_coordinates()
            else:
                print("Detecting current location...")
                coords = self.controller.get_current_location_coordinates()

            if coords:
                lat, lon = coords
                if HAS_RICH:
                    console.print(f"[green]✓[/green] Current location detected: [bold]{lat:.4f}, {lon:.4f}[/bold]")
                else:
                    print(f"✓ Current location detected: {lat:.4f}, {lon:.4f}")
                # Update location name to include coordinates for clarity
                location = f"Current Location ({lat:.4f}, {lon:.4f})"
            else:
                if HAS_RICH:
                    console.print("[yellow]⚠ Could not detect current location automatically.[/yellow]")
                    console.print("[yellow]This might be due to network restrictions or VPN usage.[/yellow]")
                    console.print("[yellow]Using New York as default location.[/yellow]")
                else:
                    print("⚠ Could not detect current location automatically.")
                    print("This might be due to network restrictions or VPN usage.")
                    print("Using New York as default location.")
                coords = (40.7128, -74.0060)  # New York
                location = "New York (Default)"
        else:
            if HAS_RICH:
                with console.status(f"[cyan]Looking up coordinates for {location}...[/cyan]", spinner="dots"):
                    coords = self.controller.get_coordinates_for_location(location)
            else:
                print(f"Looking up coordinates for {location}...")
                coords = self.controller.get_coordinates_for_location(location)

            if not coords:
                if HAS_RICH:
                    console.print(f"[yellow]Could not find coordinates for {location}. Using New York as default.[/yellow]")
                else:
                    print(f"Could not find coordinates for {location}. Using New York as default.")
                coords = (40.7128, -74.0060)  # New York

        lat, lon = coords

        # Create menu using Rich or ASCII art
        if HAS_RICH:
            console.print(Rule("Weather Options", style="cyan"))

            menu_table = Table(show_header=False, box=ROUNDED, border_style="blue")
            menu_table.add_column("Option", style="cyan", width=4)
            menu_table.add_column("Description", style="green")

            # Add exit option
            menu_table.add_row("0", "[yellow]Exit to Main Menu[/yellow]")

            # Add menu options
            menu_table.add_row("1", "[cyan]Current Weather & Next 3 Hours Forecast[/cyan]")
            menu_table.add_row("2", "[cyan]Detailed 2-Day Forecast[/cyan]")
            menu_table.add_row("3", "[cyan]Cycling Conditions & Recommendations[/cyan]")
            menu_table.add_row("4", "[cyan]Plan a Cycling Route for This Location[/cyan]")

            console.print(menu_table)
            option = console.input("[cyan]Select an option:[/cyan] ")
        else:
            print("\nWeather Options:")
            print(f"  {self.ascii_art.Fore.YELLOW}0. Exit to Main Menu{self.ascii_art.Style.RESET_ALL}")
            print(f"  {self.ascii_art.Fore.GREEN}1. Current Weather & Next 3 Hours Forecast{self.ascii_art.Style.RESET_ALL}")
            print(f"  {self.ascii_art.Fore.BLUE}2. Detailed 2-Day Forecast{self.ascii_art.Style.RESET_ALL}")
            print(f"  {self.ascii_art.Fore.CYAN}3. Cycling Conditions & Recommendations{self.ascii_art.Style.RESET_ALL}")
            print(f"  {self.ascii_art.Fore.MAGENTA}4. Plan a Cycling Route for This Location{self.ascii_art.Style.RESET_ALL}")

            option = input("> ")

        # Store coordinates for later use
        if hasattr(self, 'last_coords'):
            self.last_coords = coords

        return option

    def display_weather_data(self, weather_data) -> None:
        """
        Display weather data in a formatted way.

        Args:
            weather_data: WeatherData object to display
        """
        try:
            # Get data from weather_data object
            location = weather_data.location
            current_temp = weather_data.get_current_temperature()
            weather_main = weather_data.get_current_weather_condition()
            weather_desc = weather_data.get_current_weather_description()
            humidity = weather_data.get_current_humidity()
            wind_speed = weather_data.get_current_wind_speed()
            wind_direction = weather_data.get_current_wind_direction()

            # Get more details from current data
            feels_like = weather_data.current.get("feelslike_c", current_temp)
            pressure = weather_data.current.get("pressure_mb", 0)
            precipitation = weather_data.current.get("precip_mm", 0)
            visibility = weather_data.current.get("vis_km", 10)
            uv_index = weather_data.current.get("uv", 0)

            # Get local time
            local_time = weather_data.current.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M"))

            # Convert to imperial if user preference is set
            use_imperial = False
            if self.user_manager and self.user_manager.is_authenticated():
                use_imperial = self.user_manager.get_user_preference("use_imperial", False)

            if use_imperial:
                temp_unit = "°F"
                speed_unit = "mph"
                dist_unit = "miles"
                precip_unit = "in"
                current_temp = utils.general_utils.celsius_to_fahrenheit(current_temp)
                feels_like = utils.general_utils.celsius_to_fahrenheit(feels_like)
                wind_speed = utils.general_utils.mps_to_mph(wind_speed)
                visibility = utils.general_utils.km_to_miles(visibility)
                precipitation = utils.general_utils.mm_to_inches(precipitation)
            else:
                temp_unit = "°C"
                speed_unit = "km/h"
                dist_unit = "km"
                precip_unit = "mm"

            # Format wind direction
            direction = self.controller.get_wind_direction_text(wind_direction)

            # Get cycling recommendation
            recommendation = self.controller.get_cycling_recommendation(weather_data)

            # Display current weather with Rich UI if available
            if HAS_RICH:
                console.print(Rule(f"Current Weather for {location}", style="cyan"))

                # Current conditions panel
                current_panel = Panel(
                    f"[bold cyan]{current_temp:.1f}{temp_unit}[/bold cyan] [dim]feels like[/dim] [cyan]{feels_like:.1f}{temp_unit}[/cyan]\n"
                    f"[white]{weather_main}[/white]: {weather_desc}\n"
                    f"Wind: {wind_speed:.1f} {speed_unit} {direction}\n"
                    f"Humidity: {humidity}% | Pressure: {pressure} mb | UV Index: {uv_index}\n"
                    f"Visibility: {visibility} {dist_unit} | Precipitation: {precipitation} {precip_unit}\n"
                    f"[dim]Last updated: {local_time}[/dim]",
                    title="Current Conditions",
                    border_style="blue",
                    box=ROUNDED
                )
                console.print(current_panel)

                # Cycling recommendation panel
                rec_color = "green" if "Good" in recommendation else "yellow" if "Fair" in recommendation else "red"
                rec_panel = Panel(
                    f"[{rec_color}]{recommendation}[/{rec_color}]",
                    title="Cycling Recommendation",
                    border_style=rec_color,
                    box=ROUNDED
                )
                console.print(rec_panel)

                # Display next 3 hours forecast
                forecast_items = weather_data.get_forecast_items()

                if forecast_items and isinstance(forecast_items, list) and len(forecast_items) > 0:
                    # Check if we have hourly forecast
                    has_hourly = False
                    if 'time' in forecast_items[0]:
                        has_hourly = True

                    if has_hourly:
                        # Get the current time to filter forecast items
                        now = datetime.now()

                        # Filter forecast items for the next 3 hours
                        next_hours = []
                        for item in forecast_items:
                            item_time = item.get("time", "")
                            if not item_time:
                                continue

                            try:
                                hour_time = datetime.strptime(item_time, "%Y-%m-%d %H:%M")
                                if hour_time > now and len(next_hours) < 3:
                                    next_hours.append(item)
                            except ValueError:
                                continue

                        if next_hours:
                            console.print(Rule("Next 3 Hours Forecast", style="cyan"))

                            # Create a table for hourly forecast
                            hour_table = Table(box=ROUNDED, border_style="blue")
                            hour_table.add_column("Time", style="cyan")
                            hour_table.add_column("Temp", style="green")
                            hour_table.add_column("Conditions", style="white")
                            hour_table.add_column("Precip", style="blue")
                            hour_table.add_column("Wind", style="yellow")

                            for item in next_hours[:3]:  # Limit to 3 hours
                                hour_time = datetime.strptime(item.get("time", ""), "%Y-%m-%d %H:%M")
                                hour_temp = item.get("temp_c", 0)
                                hour_condition = item.get("condition", {}).get("text", "Unknown")
                                hour_precip = item.get("precip_mm", 0)
                                hour_wind = item.get("wind_kph", 0)
                                hour_wind_dir = item.get("wind_dir", "")

                                if use_imperial:
                                    hour_temp = utils.general_utils.celsius_to_fahrenheit(hour_temp)
                                    hour_precip = utils.general_utils.mm_to_inches(hour_precip)
                                    hour_wind = utils.general_utils.kmh_to_mph(hour_wind)

                                hour_table.add_row(
                                    hour_time.strftime("%H:%M"),
                                    f"{hour_temp:.1f}{temp_unit}",
                                    hour_condition,
                                    f"{hour_precip} {precip_unit}",
                                    f"{hour_wind:.1f} {speed_unit} {hour_wind_dir}"
                                )

                            console.print(hour_table)

                    # For 2-day forecast, if we have daily data
                    daily_forecast = []
                    if "forecastday" in weather_data.forecast:
                        daily_forecast = weather_data.forecast.get("forecastday", [])

                    if daily_forecast and len(daily_forecast) > 1:
                        # Show only first 2 days
                        console.print(Rule("2-Day Forecast", style="cyan"))

                        daily_table = Table(box=ROUNDED, border_style="blue")
                        daily_table.add_column("Date", style="cyan")
                        daily_table.add_column("High", style="red")
                        daily_table.add_column("Low", style="blue")
                        daily_table.add_column("Conditions", style="white")
                        daily_table.add_column("Precipitation", style="blue")
                        daily_table.add_column("Wind", style="yellow")
                        daily_table.add_column("Cycling", style="green")

                        for day in daily_forecast[:2]:
                            date = day.get("date", "")
                            date_obj = datetime.strptime(date, "%Y-%m-%d")
                            day_name = date_obj.strftime("%A")

                            day_data = day.get("day", {})
                            max_temp = day_data.get("maxtemp_c", 0)
                            min_temp = day_data.get("mintemp_c", 0)
                            condition = day_data.get("condition", {}).get("text", "Unknown")
                            rain = day_data.get("totalprecip_mm", 0)
                            max_wind = day_data.get("maxwind_kph", 0)

                            if use_imperial:
                                max_temp = utils.general_utils.celsius_to_fahrenheit(max_temp)
                                min_temp = utils.general_utils.celsius_to_fahrenheit(min_temp)
                                rain = utils.general_utils.mm_to_inches(rain)
                                max_wind = utils.general_utils.kmh_to_mph(max_wind)

                            # Determine cycling rating based on conditions
                            cycling_rating = "Good"
                            if "rain" in condition.lower() or "snow" in condition.lower() or rain > 5:
                                cycling_rating = "Poor"
                            elif "cloud" in condition.lower() or rain > 0:
                                cycling_rating = "Fair"

                            daily_table.add_row(
                                f"{day_name}",
                                f"{max_temp:.1f}{temp_unit}",
                                f"{min_temp:.1f}{temp_unit}",
                                condition,
                                f"{rain} {precip_unit}",
                                f"{max_wind:.1f} {speed_unit}",
                                cycling_rating
                            )

                        console.print(daily_table)
            else:
                # Fallback to ASCII art display
                print(f"\n{self.ascii_art.Fore.CYAN}{self.ascii_art.Style.BRIGHT}Current Weather for {location}{self.ascii_art.Style.RESET_ALL}")
                print(f"Temperature: {current_temp:.1f}{temp_unit} (Feels like: {feels_like:.1f}{temp_unit})")
                print(f"Conditions: {weather_main} - {weather_desc}")
                print(f"Humidity: {humidity}%")
                print(f"Wind: {wind_speed:.1f} {speed_unit} {direction}")
                print(f"Visibility: {visibility} {dist_unit} | UV Index: {uv_index}")
                print(f"Last updated: {local_time}")

                # Print cycling recommendation
                print(f"\n{self.ascii_art.Fore.YELLOW}Cycling Recommendation: {recommendation}{self.ascii_art.Style.RESET_ALL}")

                # Display next 3 hours forecast
                forecast_items = weather_data.get_forecast_items()

                if forecast_items and isinstance(forecast_items, list) and len(forecast_items) > 0:
                    # Check if we have hourly forecast
                    has_hourly = False
                    if 'time' in forecast_items[0]:
                        has_hourly = True

                    if has_hourly:
                        # Get the current time
                        now = datetime.now()

                        # Filter forecast items for the next 3 hours
                        next_hours = []
                        for item in forecast_items:
                            item_time = item.get("time", "")
                            if not item_time:
                                continue

                            try:
                                hour_time = datetime.strptime(item_time, "%Y-%m-%d %H:%M")
                                if hour_time > now and len(next_hours) < 3:
                                    next_hours.append(item)
                            except ValueError:
                                continue

                        if next_hours:
                            print(f"\n{self.ascii_art.Fore.CYAN}{self.ascii_art.Style.BRIGHT}Next 3 Hours Forecast{self.ascii_art.Style.RESET_ALL}")

                            for item in next_hours[:3]:  # Limit to 3 hours
                                hour_time = datetime.strptime(item.get("time", ""), "%Y-%m-%d %H:%M")
                                hour_temp = item.get("temp_c", 0)
                                hour_condition = item.get("condition", {}).get("text", "Unknown")
                                hour_precip = item.get("precip_mm", 0)
                                hour_wind = item.get("wind_kph", 0)
                                hour_wind_dir = item.get("wind_dir", "")

                                if use_imperial:
                                    hour_temp = utils.general_utils.celsius_to_fahrenheit(hour_temp)
                                    hour_precip = utils.general_utils.mm_to_inches(hour_precip)
                                    hour_wind = utils.general_utils.kmh_to_mph(hour_wind)

                                print(f"{hour_time.strftime('%H:%M')}: {hour_temp:.1f}{temp_unit}, {hour_condition}, "
                                      f"Precip {hour_precip} {precip_unit}, Wind {hour_wind:.1f} {speed_unit} {hour_wind_dir}")

                    # Show 2-day forecast if we have daily data
                    daily_forecast = []
                    if "forecastday" in weather_data.forecast:
                        daily_forecast = weather_data.forecast.get("forecastday", [])

                    if daily_forecast and len(daily_forecast) > 1:
                        print(f"\n{self.ascii_art.Fore.CYAN}{self.ascii_art.Style.BRIGHT}2-Day Forecast{self.ascii_art.Style.RESET_ALL}")

                        for day in daily_forecast[:2]:
                            date = day.get("date", "")
                            date_obj = datetime.strptime(date, "%Y-%m-%d")
                            day_name = date_obj.strftime("%A")

                            day_data = day.get("day", {})
                            max_temp = day_data.get("maxtemp_c", 0)
                            min_temp = day_data.get("mintemp_c", 0)
                            condition = day_data.get("condition", {}).get("text", "Unknown")
                            rain = day_data.get("totalprecip_mm", 0)
                            max_wind = day_data.get("maxwind_kph", 0)

                            if use_imperial:
                                max_temp = utils.general_utils.celsius_to_fahrenheit(max_temp)
                                min_temp = utils.general_utils.celsius_to_fahrenheit(min_temp)
                                rain = utils.general_utils.mm_to_inches(rain)
                                max_wind = utils.general_utils.kmh_to_mph(max_wind)

                            print(f"{day_name}: {min_temp:.1f}-{max_temp:.1f}{temp_unit}, {condition}, "
                                  f"Precip {rain} {precip_unit}, Wind up to {max_wind:.1f} {speed_unit}")

        except Exception as e:
            logger.error(f"Error displaying weather data: {e}")
            if HAS_RICH:
                console.print(f"[red]Error displaying weather data: {str(e)}[/red]")
            else:
                print(f"Error displaying weather data: {str(e)}")
