"""
Menu system for the EcoCycle application.

This module contains functions for displaying menus and handling user input.
"""

import os
import sys
import logging
from typing import Dict, Any

# Check if the rich module is available
try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Import from MVC architecture
from views.eco_tip_view import display_eco_tip_in_menu
# Import from app_functions to avoid circular imports
from utils.app_functions import (
    log_cycling_trip, view_statistics, eco_challenges,
    calculate_carbon_footprint, weather_route_planner,
    settings_preferences, social_sharing,
    admin_panel, import_local_modules
)

# Setup logger
logger = logging.getLogger(__name__)

def show_main_menu(user_manager_instance):
    """Display the main menu and handle user input."""

    modules = import_local_modules()
    ascii_art = modules['ascii_art']
    eco_tips = modules['eco_tips']

    while True:
        ascii_art.clear_screen()
        ascii_art.display_header()

        # Show daily eco tip using the MVC architecture
        daily_tip = display_eco_tip_in_menu()

        # Display user info
        user_info = "Not logged in"
        user_stats = ""

        if user_manager_instance.is_authenticated():
            user = user_manager_instance.get_current_user()
            if user_manager_instance.is_guest():
                user_info = "Logged in as: Guest User"
            else:
                name = user.get('name', user.get('username', 'Unknown'))
                user_info = f"Logged in as: {name}"

                # Format user stats if available
                stats = user.get('stats', {})
                if stats:
                    total_trips = stats.get('total_trips', 0)
                    total_distance = stats.get('total_distance', 0.0)
                    total_co2_saved = stats.get('total_co2_saved', 0.0)
                    total_calories = stats.get('total_calories', 0)

                    user_stats = f"Stats: {total_trips} trips, {total_distance:.1f} km, {total_co2_saved:.2f} kg CO2 saved, {total_calories} kcal burned"

        # Display menu options
        options = [
            "Log a cycling trip",
            "View statistics",
            "Calculate carbon footprint",
            "Weather and route planning",
            "Eco-challenges",
            "Settings and preferences",
            "Social sharing and achievements",
        ]

        # Add admin option for admin users
        if user_manager_instance.is_authenticated() and user_manager_instance.is_admin():
            options.append("Admin panel")

        # Add login/logout option
        if user_manager_instance.is_authenticated():
            options.append("Logout")
        else:
            options.append("Login")

        # Use Rich UI if available, otherwise fallback to ASCII art
        if HAS_RICH:
            # Display header with Rich styling
            console.print(Panel.fit(
                Text("EcoCycle", style="bold green"),
                border_style="green"
            ))

            # Display eco tip with Rich styling
            console.print(Panel(
                f"Eco Tip of the Day: {daily_tip}",
                title="Daily Tip",
                border_style="cyan"
            ))

            # Display user info with Rich styling
            user_panel_content = user_info
            if user_stats:
                user_panel_content = f"{user_info}\n{user_stats}"

            console.print(Panel(
                user_panel_content,
                title="User Profile",
                border_style="blue"
            ))

            # Create a menu table
            menu_table = Table(show_header=False, box=rich.box.ROUNDED, border_style="green")
            menu_table.add_column("Option", style="cyan")
            menu_table.add_column("Description", style="green")

            # Add exit option
            menu_table.add_row("0", "[yellow]Exit Program[/yellow]")

            # Add menu options
            for i, option in enumerate(options):
                menu_table.add_row(f"{i+1}", option)

            # Display the menu
            console.print(Panel(menu_table, title="Main Menu", border_style="green"))
        else:
            # Fallback to ASCII art display
            print(f"\n{ascii_art.Fore.GREEN}Eco Tip of the Day:{ascii_art.Style.RESET_ALL} {daily_tip}\n")
            print(user_info)
            if user_stats:
                print(user_stats)

            # Display menu with the yellow "0. Exit" option
            ascii_art.display_section_header("Main Menu")

            # Display "0. Exit Program" option first
            print(f"  {ascii_art.Fore.YELLOW}0. Exit Program{ascii_art.Style.RESET_ALL}")

            # Display other menu options
            for i, option in enumerate(options):
                print(f"  {i+1}. {option}")

            print()

        # Get user choice with KeyboardInterrupt handling
        try:
            choice = input("Select an option: ")
        except KeyboardInterrupt:
            print("\n")  # New line for better formatting
            print("Menu interrupted by user.")

            # Ask user if they want to exit or continue
            try:
                exit_choice = input("\nDo you want to exit EcoCycle? (y/n): ").lower().strip()
                if exit_choice in ['y', 'yes']:
                    ascii_art.clear_screen()
                    ascii_art.display_header()
                    print("\nThank you for using EcoCycle! Goodbye.")
                    print("With ♡ - the EcoCycle team.")
                    sys.exit(0)
                else:
                    print("Returning to main menu...")
                    continue
            except KeyboardInterrupt:
                # If user presses Ctrl+C again, force exit
                ascii_art.clear_screen()
                ascii_art.display_header()
                print("\n\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)

        try:
            choice = int(choice)
            if choice == 0:  # Exit option
                ascii_art.clear_screen()
                ascii_art.display_header()
                print("\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)
            elif 1 <= choice <= len(options):
                if options[choice-1] == "Log a cycling trip":
                    log_cycling_trip(user_manager_instance)
                elif options[choice-1] == "View statistics":
                    view_statistics(user_manager_instance)
                elif options[choice-1] == "Calculate carbon footprint":
                    calculate_carbon_footprint(user_manager_instance)
                elif options[choice-1] == "Weather and route planning":
                    weather_route_planner(user_manager_instance)
                elif options[choice-1] == "Eco-challenges":
                    eco_challenges(user_manager_instance)
                elif options[choice-1] == "Settings and preferences":
                    settings_preferences(user_manager_instance)
                elif options[choice-1] == "Social sharing and achievements":
                    social_sharing(user_manager_instance)

                elif options[choice-1] == "Admin panel":
                    admin_panel(user_manager_instance)
                elif options[choice-1] == "Login":
                    user_manager_instance.authenticate()
                elif options[choice-1] == "Logout":
                    user_manager_instance.logout()
                    if HAS_RICH:
                        console.print("[green]Logged out successfully.[/green]")
                    else:
                        print("Logged out successfully.")

                    input("Press Enter to continue to authentication...")

                    # Force the user to authenticate again
                    if not user_manager_instance.authenticate():
                        # Only exit if they explicitly cancel authentication
                        print("\nAuthentication cancelled. Exiting application.")
                        sys.exit(0)

                    # If authentication was successful, just continue in the menu loop
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")
        except ValueError:
            print("Invalid input. Please enter a number.")
            input("Press Enter to continue...")
