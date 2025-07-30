"""
EcoCycle - Eco Challenges Module
Provides functionality for creating and managing personalized eco-challenges.
"""
import os
import json
import random
import datetime
import logging
from typing import Dict, List, Optional, Any, Tuple

# Import configuration
from config.config import PREFERENCES_DIR

# Configure logging
logger = logging.getLogger(__name__)

# Import utilities
import utils.ascii_art as ascii_art
import utils.general_utils as utils

# Check if the rich module is available
try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.text import Text
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Challenge difficulty levels
DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

# Challenge categories
CHALLENGE_CATEGORIES = [
    "Cycling",
    "Transportation",
    "Energy",
    "Waste",
    "Food",
    "Community"
]

# Challenge duration options (in days)
CHALLENGE_DURATIONS = [7, 14, 30, 90]

# Pre-defined challenges by category and difficulty
PREDEFINED_CHALLENGES = {
    "Cycling": {
        "Beginner": [
            {
                "title": "Beginner Cyclist",
                "description": "Cycle at least 5km this week",
                "target": 5,
                "unit": "km",
                "duration": 7,
                "points": 100,
                "co2_impact": 1.0
            },
            {
                "title": "Short Trip Replacement",
                "description": "Replace 3 short car trips with cycling this week",
                "target": 3,
                "unit": "trips",
                "duration": 7,
                "points": 150,
                "co2_impact": 1.5
            }
        ],
        "Intermediate": [
            {
                "title": "Regular Rider",
                "description": "Cycle at least 20km this week",
                "target": 20,
                "unit": "km",
                "duration": 7,
                "points": 200,
                "co2_impact": 4.0
            },
            {
                "title": "Commute Changer",
                "description": "Cycle to work/school at least 2 days this week",
                "target": 2,
                "unit": "days",
                "duration": 7,
                "points": 250,
                "co2_impact": 5.0
            }
        ],
        "Advanced": [
            {
                "title": "Dedicated Cyclist",
                "description": "Cycle at least 50km this week",
                "target": 50,
                "unit": "km",
                "duration": 7,
                "points": 400,
                "co2_impact": 10.0
            },
            {
                "title": "Full Week Commuter",
                "description": "Cycle to work/school every day this week",
                "target": 5,
                "unit": "days",
                "duration": 7,
                "points": 500,
                "co2_impact": 15.0
            }
        ],
        "Expert": [
            {
                "title": "Century Rider",
                "description": "Complete a 100km ride this month",
                "target": 100,
                "unit": "km",
                "duration": 30,
                "points": 1000,
                "co2_impact": 20.0
            },
            {
                "title": "Car-Free Month",
                "description": "Replace all personal car trips with cycling for a month",
                "target": 30,
                "unit": "days",
                "duration": 30,
                "points": 1500,
                "co2_impact": 100.0
            }
        ]
    },
    "Transportation": {
        "Beginner": [
            {
                "title": "Public Transit Day",
                "description": "Use public transportation instead of a car once this week",
                "target": 1,
                "unit": "days",
                "duration": 7,
                "points": 100,
                "co2_impact": 2.0
            }
        ],
        "Intermediate": [
            {
                "title": "Carpool Week",
                "description": "Carpool to work/school at least 3 days this week",
                "target": 3,
                "unit": "days",
                "duration": 7,
                "points": 250,
                "co2_impact": 7.5
            }
        ],
        "Advanced": [
            {
                "title": "Multi-Modal Commuter",
                "description": "Use at least 3 different eco-friendly transport modes this week",
                "target": 3,
                "unit": "modes",
                "duration": 7,
                "points": 400,
                "co2_impact": 10.0
            }
        ],
        "Expert": [
            {
                "title": "Zero Emission Month",
                "description": "Only use zero-emission transportation for a month",
                "target": 30,
                "unit": "days",
                "duration": 30,
                "points": 1500,
                "co2_impact": 120.0
            }
        ]
    },
    "Energy": {
        "Beginner": [
            {
                "title": "Lights Out",
                "description": "Turn off lights when leaving rooms for a week",
                "target": 7,
                "unit": "days",
                "duration": 7,
                "points": 100,
                "co2_impact": 1.0
            }
        ],
        "Intermediate": [
            {
                "title": "Unplug Challenge",
                "description": "Unplug electronics when not in use for a week",
                "target": 7,
                "unit": "days",
                "duration": 7,
                "points": 200,
                "co2_impact": 3.0
            }
        ],
        "Advanced": [
            {
                "title": "Cold Wash Week",
                "description": "Use only cold water for laundry for a week",
                "target": 7,
                "unit": "days",
                "duration": 7,
                "points": 300,
                "co2_impact": 5.0
            }
        ],
        "Expert": [
            {
                "title": "Energy Audit",
                "description": "Conduct a home energy audit and implement 5 improvements",
                "target": 5,
                "unit": "improvements",
                "duration": 30,
                "points": 1000,
                "co2_impact": 50.0
            }
        ]
    },
    "Waste": {
        "Beginner": [
            {
                "title": "Reusable Bottle",
                "description": "Use only a reusable water bottle for a week",
                "target": 7,
                "unit": "days",
                "duration": 7,
                "points": 100,
                "co2_impact": 1.0
            }
        ],
        "Intermediate": [
            {
                "title": "Zero Plastic Bags",
                "description": "Avoid all single-use plastic bags for a week",
                "target": 7,
                "unit": "days",
                "duration": 7,
                "points": 250,
                "co2_impact": 2.0
            }
        ],
        "Advanced": [
            {
                "title": "Compost Champion",
                "description": "Compost all food waste for two weeks",
                "target": 14,
                "unit": "days",
                "duration": 14,
                "points": 500,
                "co2_impact": 10.0
            }
        ],
        "Expert": [
            {
                "title": "Zero Waste Month",
                "description": "Produce less than one small bag of landfill waste for a month",
                "target": 30,
                "unit": "days",
                "duration": 30,
                "points": 1500,
                "co2_impact": 50.0
            }
        ]
    },
    "Food": {
        "Beginner": [
            {
                "title": "Meatless Monday",
                "description": "Eat vegetarian meals every Monday for a month",
                "target": 4,
                "unit": "days",
                "duration": 30,
                "points": 200,
                "co2_impact": 8.0
            }
        ],
        "Intermediate": [
            {
                "title": "Local Food Week",
                "description": "Eat only locally produced food for a week",
                "target": 7,
                "unit": "days",
                "duration": 7,
                "points": 300,
                "co2_impact": 10.0
            }
        ],
        "Advanced": [
            {
                "title": "Plant-Based Week",
                "description": "Eat only plant-based meals for a week",
                "target": 7,
                "unit": "days",
                "duration": 7,
                "points": 500,
                "co2_impact": 20.0
            }
        ],
        "Expert": [
            {
                "title": "Zero Food Waste",
                "description": "Generate zero food waste for a month",
                "target": 30,
                "unit": "days",
                "duration": 30,
                "points": 1000,
                "co2_impact": 40.0
            }
        ]
    },
    "Community": {
        "Beginner": [
            {
                "title": "Eco Influence",
                "description": "Share 3 sustainability tips with friends/family",
                "target": 3,
                "unit": "shares",
                "duration": 7,
                "points": 100,
                "co2_impact": 3.0
            }
        ],
        "Intermediate": [
            {
                "title": "Group Ride Organizer",
                "description": "Organize a group cycling event this month",
                "target": 1,
                "unit": "events",
                "duration": 30,
                "points": 300,
                "co2_impact": 15.0
            }
        ],
        "Advanced": [
            {
                "title": "Environmental Volunteer",
                "description": "Volunteer for a local environmental cause this month",
                "target": 1,
                "unit": "events",
                "duration": 30,
                "points": 500,
                "co2_impact": 10.0
            }
        ],
        "Expert": [
            {
                "title": "Sustainability Leader",
                "description": "Lead a community sustainability project this month",
                "target": 1,
                "unit": "projects",
                "duration": 30,
                "points": 1000,
                "co2_impact": 100.0
            }
        ]
    }
}


class EcoChallenges:
    """Eco-Challenges creator and manager."""

    def __init__(self, user_manager=None, sheets_manager=None):
        """Initialize the eco-challenges module."""
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager
        self.challenges_file = os.path.join(PREFERENCES_DIR, "eco_challenges.json")
        self.user_challenges_file = os.path.join(PREFERENCES_DIR, "user_challenges.json")
        self.challenges = self._load_challenges()
        self.user_challenges = self._load_user_challenges()

    def _load_challenges(self) -> Dict:
        """Load challenges from file or initialize with predefined ones."""
        if os.path.exists(self.challenges_file):
            try:
                with open(self.challenges_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing challenges file: {self.challenges_file}")
                return PREDEFINED_CHALLENGES
        return PREDEFINED_CHALLENGES

    def _save_challenges(self) -> bool:
        """Save challenges to file."""
        try:
            with open(self.challenges_file, 'w') as f:
                json.dump(self.challenges, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving challenges: {e}")
            return False

    def _load_user_challenges(self) -> Dict:
        """Load user challenges from file."""
        if os.path.exists(self.user_challenges_file):
            try:
                with open(self.user_challenges_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing user challenges file: {self.user_challenges_file}")
                return {}
        return {}

    def _save_user_challenges(self) -> bool:
        """Save user challenges to file."""
        try:
            with open(self.user_challenges_file, 'w') as f:
                json.dump(self.user_challenges, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving user challenges: {e}")
            return False

    def run_eco_challenges(self) -> None:
        """Run the eco challenges interactive interface."""
        # Import necessary modules here to avoid circular imports
        # ascii_art is already imported at the top of the file

        if not self.user_manager or not self.user_manager.is_authenticated():
            if HAS_RICH:
                console.print(Panel(
                    "You need to be logged in to use Eco Challenges.",
                    title="Authentication Required",
                    border_style="red"
                ))
            else:
                print("You need to be logged in to use Eco Challenges.")
            return

        username = self.user_manager.get_current_user().get('username')

        while True:
            ascii_art.clear_screen()
            ascii_art.display_header()

            options = [
                "View active challenges",
                "Join new challenge",
                "Create custom challenge",
                "Challenge history & achievements",
                "Weekly sustainability goals",
                "Challenge impact dashboard",
                "Community leaderboard",
                "Return to main menu"
            ]

            if HAS_RICH:
                # Display header with Rich styling
                console.print(Panel.fit(
                    Text("Eco Challenges", style="bold cyan"),
                    border_style="cyan"
                ))

                # Display description with Rich styling
                console.print(Panel(
                    "Personalized sustainability challenges to reduce your carbon footprint.\n"
                    "Complete challenges to earn points and track your environmental impact.",
                    border_style="green"
                ))

                # Create a menu table
                menu_table = Table(show_header=False, box=rich.box.ROUNDED, border_style="blue")
                menu_table.add_column("Option", style="cyan")
                menu_table.add_column("Description", style="green")

                # Add exit option
                menu_table.add_row("0", "[yellow]Exit Program[/yellow]")

                # Add menu options
                for i, option in enumerate(options):
                    menu_table.add_row(f"{i+1}", option)

                # Display the menu
                console.print(Panel(menu_table, title="Eco Challenges Menu", border_style="blue"))
            else:
                # Fallback to ASCII art display
                ascii_art.display_section_header("Eco Challenges")
                print("\nPersonalized sustainability challenges to reduce your carbon footprint.")
                print("Complete challenges to earn points and track your environmental impact.")
                ascii_art.display_menu("Eco Challenges Menu", options)

            choice = input("\nSelect an option (0-8): ")

            if choice == '0':
                # Exit program
                print("\nExiting program...")
                import sys
                sys.exit(0)
            elif choice == '1':
                self.view_active_challenges(username)
            elif choice == '2':
                self.join_new_challenge(username)
            elif choice == '3':
                self.create_custom_challenge(username)
            elif choice == '4':
                self.view_challenge_history(username)
            elif choice == '5':
                self.manage_weekly_goals(username)
            elif choice == '6':
                self.display_impact_dashboard(username)
            elif choice == '7':
                self.view_community_leaderboard()
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

    def view_active_challenges(self, username: str) -> None:
        """View and update progress for active challenges."""
        # ascii_art is already imported at the top of the file

        ascii_art.clear_screen()

        # Get user's active challenges
        if username not in self.user_challenges:
            self.user_challenges[username] = {"active": [], "completed": [], "points": 0}

        active_challenges = self.user_challenges[username]["active"]

        if HAS_RICH:
            # Display header with Rich panel
            console.print(Panel.fit(
                Text("Active Challenges", style="bold cyan"),
                border_style="cyan"
            ))

            if not active_challenges:
                console.print(Panel(
                    "You don't have any active challenges.\nJoin a new challenge from the Eco Challenges menu.",
                    title="No Active Challenges",
                    border_style="yellow"
                ))
                input("\nPress Enter to continue...")
                return

            console.print(f"\nYou have [bold green]{len(active_challenges)}[/bold green] active challenges:")

            today = datetime.datetime.now().date()

            # Create a Rich table
            table = Table(show_header=True, header_style="bold cyan", border_style="cyan")
            table.add_column("#", style="dim", width=3)
            table.add_column("Challenge", style="green")
            table.add_column("Progress", justify="right")
            table.add_column("Deadline", justify="center")
            table.add_column("Status", justify="right")

            for i, challenge in enumerate(active_challenges):
                # Calculate days remaining
                start_date = datetime.datetime.strptime(challenge['start_date'], "%Y-%m-%d").date()
                end_date = start_date + datetime.timedelta(days=challenge['duration'])
                days_remaining = (end_date - today).days

                # Calculate progress percentage
                progress_pct = min(100, int((challenge['current_progress'] / challenge['target']) * 100))

                # Progress text with color based on percentage
                if progress_pct < 25:
                    progress_style = "red"
                elif progress_pct < 50:
                    progress_style = "yellow"
                elif progress_pct < 75:
                    progress_style = "blue"
                else:
                    progress_style = "green"

                progress_text = f"{challenge['current_progress']}/{challenge['target']} {challenge['unit']} ([{progress_style}]{progress_pct}%[/{progress_style}])"

                # Status with appropriate color
                if days_remaining < 0:
                    status = "[red]Expired[/red]"
                elif progress_pct >= 100:
                    status = "[green]Ready to complete[/green]"
                else:
                    status = f"[blue]{days_remaining} days left[/blue]"

                table.add_row(
                    str(i + 1),
                    challenge['title'],
                    progress_text,
                    end_date.strftime("%Y-%m-%d"),
                    status
                )

            console.print(table)

            # Display options in a panel
            console.print(Panel(
                "1. Update challenge progress\n2. Complete a challenge\n3. Abandon a challenge\n4. Return to Eco Challenges menu",
                title="Options",
                border_style="cyan"
            ))
        else:
            # Fallback to non-Rich display
            ascii_art.display_section_header("Active Challenges")

            if not active_challenges:
                print("\nYou don't have any active challenges.")
                print("Join a new challenge from the Eco Challenges menu.")
                input("\nPress Enter to continue...")
                return

            print(f"\nYou have {len(active_challenges)} active challenges:")

            today = datetime.datetime.now().date()

            from tabulate import tabulate
            headers = ["#", "Challenge", "Progress", "Deadline", "Status"]
            rows = []

            for i, challenge in enumerate(active_challenges):
                # Calculate days remaining
                start_date = datetime.datetime.strptime(challenge['start_date'], "%Y-%m-%d").date()
                end_date = start_date + datetime.timedelta(days=challenge['duration'])
                days_remaining = (end_date - today).days

                # Calculate progress percentage
                progress_pct = min(100, int((challenge['current_progress'] / challenge['target']) * 100))

                # Progress bar
                progress_bar = f"{progress_pct}% complete"

                # Status
                if days_remaining < 0:
                    status = "Expired"
                elif progress_pct >= 100:
                    status = "Ready to complete"
                else:
                    status = f"{days_remaining} days left"

                rows.append([
                    i + 1,
                    challenge['title'],
                    f"{challenge['current_progress']}/{challenge['target']} {challenge['unit']} ({progress_bar})",
                    end_date.strftime("%Y-%m-%d"),
                    status
                ])

            print(tabulate(rows, headers=headers, tablefmt="grid"))

            print("\nOptions:")
            print("  1. Update challenge progress")
            print("  2. Complete a challenge")
            print("  3. Abandon a challenge")
            print("  4. Return to Eco Challenges menu")

        choice = input("\nSelect an option (1-4): ")

        if choice == '1':
            self.update_challenge_progress(username, active_challenges)
        elif choice == '2':
            self.complete_challenge(username, active_challenges)
        elif choice == '3':
            self.abandon_challenge(username, active_challenges)
        elif choice == '4':
            return
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")

    def update_challenge_progress(self, username: str, active_challenges: List[Dict]) -> None:
        """Update progress for a selected challenge."""
        # ascii_art is already imported at the top of the file

        if not active_challenges:
            print("No active challenges to update.")
            input("Press Enter to continue...")
            return

        print("\nWhich challenge would you like to update?")
        for i, challenge in enumerate(active_challenges):
            print(f"  {i + 1}. {challenge['title']}")

        try:
            choice = int(input("\nEnter challenge number: ")) - 1
            if choice < 0 or choice >= len(active_challenges):
                print("Invalid selection.")
                input("Press Enter to continue...")
                return

            challenge = active_challenges[choice]

            print(f"\nCurrent progress: {challenge['current_progress']}/{challenge['target']} {challenge['unit']}")

            try:
                new_progress = float(input(f"Enter new progress value (0-{challenge['target']}): "))
                if new_progress < 0 or new_progress > challenge['target']:
                    print(f"Value must be between 0 and {challenge['target']}.")
                else:
                    challenge['current_progress'] = new_progress
                    self._save_user_challenges()
                    print("Progress updated successfully!")

                    # Check if challenge is now complete
                    if new_progress >= challenge['target']:
                        print("\nYou've reached your target! You can mark this challenge as completed from the active challenges menu.")
            except ValueError:
                print("Please enter a valid number.")

        except ValueError:
            print("Please enter a valid number.")

        input("Press Enter to continue...")

    def complete_challenge(self, username: str, active_challenges: List[Dict]) -> None:
        """Mark a challenge as completed."""
        # ascii_art is already imported at the top of the file

        if not active_challenges:
            print("No active challenges to complete.")
            input("Press Enter to continue...")
            return

        # Filter challenges that are ready to complete (progress >= target)
        completable = [(i, c) for i, c in enumerate(active_challenges) if c['current_progress'] >= c['target']]

        if not completable:
            print("You don't have any challenges ready to complete.")
            print("Keep working towards your targets!")
            input("Press Enter to continue...")
            return

        print("\nWhich challenge would you like to mark as completed?")
        for i, (idx, challenge) in enumerate(completable):
            print(f"  {i + 1}. {challenge['title']} - {challenge['current_progress']}/{challenge['target']} {challenge['unit']}")

        try:
            choice = int(input("\nEnter challenge number: ")) - 1
            if choice < 0 or choice >= len(completable):
                print("Invalid selection.")
                input("Press Enter to continue...")
                return

            # Get the actual index in the active_challenges list
            actual_idx, challenge = completable[choice]

            # Add completion date
            challenge['completion_date'] = datetime.datetime.now().strftime("%Y-%m-%d")

            # Move to completed challenges
            self.user_challenges[username]["completed"].append(challenge)

            # Add points
            self.user_challenges[username]["points"] += challenge['points']

            # Remove from active challenges
            self.user_challenges[username]["active"].pop(actual_idx)

            self._save_user_challenges()

            # Update user stats if sheets_manager is available
            if self.sheets_manager:
                # In a real implementation, this would update a 'challenges' sheet
                pass

            ascii_art.display_success_message(f"Challenge completed! You earned {challenge['points']} points!")
            print(f"You've saved approximately {challenge['co2_impact']:.2f} kg of CO2!")
            print(f"Total eco-points: {self.user_challenges[username]['points']}")

        except ValueError:
            print("Please enter a valid number.")

        input("Press Enter to continue...")

    def abandon_challenge(self, username: str, active_challenges: List[Dict]) -> None:
        """Abandon a challenge."""
        if not active_challenges:
            print("No active challenges to abandon.")
            input("Press Enter to continue...")
            return

        print("\nWhich challenge would you like to abandon?")
        for i, challenge in enumerate(active_challenges):
            print(f"  {i + 1}. {challenge['title']}")

        try:
            choice = int(input("\nEnter challenge number: ")) - 1
            if choice < 0 or choice >= len(active_challenges):
                print("Invalid selection.")
                input("Press Enter to continue...")
                return

            # Confirm abandonment
            confirm = input(f"Are you sure you want to abandon '{active_challenges[choice]['title']}'? (y/n): ")

            if confirm.lower() == 'y':
                # Remove from active challenges
                self.user_challenges[username]["active"].pop(choice)
                self._save_user_challenges()
                print("Challenge abandoned.")
            else:
                print("Challenge not abandoned.")

        except ValueError:
            print("Please enter a valid number.")

        input("Press Enter to continue...")

    def join_new_challenge(self, username: str) -> None:
        """Join a new predefined challenge."""
        # ascii_art is already imported at the top of the file

        if username not in self.user_challenges:
            self.user_challenges[username] = {"active": [], "completed": [], "points": 0}

        ascii_art.clear_screen()

        if HAS_RICH:
            # Enhanced UI with Rich
            console.print(Panel.fit(
                Text("🏆 Join New Challenge", style="bold cyan"),
                border_style="cyan"
            ))

            # Display categories in a visually appealing way
            console.print(Panel(
                "Choose a category that aligns with your sustainability goals!",
                title="Step 1: Select Challenge Category",
                border_style="blue",
                padding=(1, 2)
            ))

            # Create a grid of category options with icons
            category_icons = {
                "Cycling": "🚲",
                "Transportation": "🚌",
                "Energy": "⚡",
                "Waste": "♻️",
                "Food": "🍎",
                "Community": "👥"
            }

            # Display categories in a table
            category_table = Table(box=rich.box.ROUNDED, border_style="blue", show_header=False)
            category_table.add_column("Number", style="dim", width=8)
            category_table.add_column("Category", style="green bold")
            category_table.add_column("Description", style="cyan")

            category_descriptions = {
                "Cycling": "Bike-related challenges to reduce emissions",
                "Transportation": "Eco-friendly transport alternatives",
                "Energy": "Reduce your energy consumption",
                "Waste": "Minimize waste and increase recycling",
                "Food": "Sustainable eating and food choices",
                "Community": "Engage others in sustainability"
            }

            for i, category in enumerate(CHALLENGE_CATEGORIES):
                icon = category_icons.get(category, "🌱")
                description = category_descriptions.get(category, "")
                category_table.add_row(
                    f"{i + 1}",
                    f"{icon} {category}",
                    description
                )

            console.print(category_table)

            try:
                category_idx = int(input("\nEnter category number: ")) - 1
                if category_idx < 0 or category_idx >= len(CHALLENGE_CATEGORIES):
                    console.print("[bold red]Invalid selection.[/bold red]")
                    input("Press Enter to continue...")
                    return

                category = CHALLENGE_CATEGORIES[category_idx]
                category_icon = category_icons.get(category, "🌱")

                # Step 2: Select difficulty
                ascii_art.clear_screen()

                console.print(Panel.fit(
                    Text(f"{category_icon} Join {category} Challenge", style="bold cyan"),
                    border_style="cyan"
                ))

                # Display difficulty levels with visual indicators
                console.print(Panel(
                    "Choose a difficulty level that matches your experience and commitment level.",
                    title="Step 2: Select Difficulty Level",
                    border_style="blue",
                    padding=(1, 2)
                ))

                # Create a table for difficulty levels
                difficulty_table = Table(box=rich.box.ROUNDED, border_style="blue", show_header=False)
                difficulty_table.add_column("Number", style="dim", width=8)
                difficulty_table.add_column("Difficulty", style="green bold")
                difficulty_table.add_column("Indicator", justify="center")
                difficulty_table.add_column("Description", style="cyan")

                difficulty_descriptions = {
                    "Beginner": "Perfect for those just starting their sustainability journey",
                    "Intermediate": "For those with some experience in sustainable practices",
                    "Advanced": "Challenging goals for sustainability enthusiasts",
                    "Expert": "The highest level of commitment to environmental impact"
                }

                difficulty_indicators = {
                    "Beginner": "[green]●[/green][dim]○○○[/dim]",
                    "Intermediate": "[green]●●[/green][dim]○○[/dim]",
                    "Advanced": "[green]●●●[/green][dim]○[/dim]",
                    "Expert": "[green]●●●●[/green]"
                }

                for i, difficulty in enumerate(DIFFICULTY_LEVELS):
                    indicator = difficulty_indicators.get(difficulty, "")
                    description = difficulty_descriptions.get(difficulty, "")
                    difficulty_table.add_row(
                        f"{i + 1}",
                        difficulty,
                        indicator,
                        description
                    )

                console.print(difficulty_table)

                difficulty_idx = int(input("\nEnter difficulty number: ")) - 1
                if difficulty_idx < 0 or difficulty_idx >= len(DIFFICULTY_LEVELS):
                    console.print("[bold red]Invalid selection.[/bold red]")
                    input("Press Enter to continue...")
                    return

                difficulty = DIFFICULTY_LEVELS[difficulty_idx]

                # Step 3: Display available challenges for selected category and difficulty
                if category not in self.challenges or difficulty not in self.challenges[category]:
                    console.print(Panel(
                        f"No challenges found for {category} at {difficulty} level.\nTry a different category or difficulty level.",
                        title="No Challenges Available",
                        border_style="yellow"
                    ))
                    input("Press Enter to continue...")
                    return

                available_challenges = self.challenges[category][difficulty]

                ascii_art.clear_screen()

                console.print(Panel.fit(
                    Text(f"{category_icon} {difficulty} {category} Challenges", style="bold cyan"),
                    border_style="cyan"
                ))

                console.print(Panel(
                    "Review the available challenges and select one to join.",
                    title="Step 3: Select a Challenge",
                    border_style="blue",
                    padding=(1, 2)
                ))

                # Display challenges in cards
                for i, challenge in enumerate(available_challenges):
                    # Calculate end date
                    start_date = datetime.datetime.now()
                    end_date = start_date + datetime.timedelta(days=challenge['duration'])

                    # Create a panel for each challenge
                    challenge_panel = Panel(
                        f"[bold green]{challenge['title']}[/bold green]\n\n"
                        f"[cyan]Description:[/cyan] {challenge['description']}\n"
                        f"[cyan]Target:[/cyan] {challenge['target']} {challenge['unit']}\n"
                        f"[cyan]Duration:[/cyan] {challenge['duration']} days (until {end_date.strftime('%Y-%m-%d')})\n"
                        f"[cyan]Points:[/cyan] [yellow]{challenge['points']}[/yellow]\n"
                        f"[cyan]CO2 Impact:[/cyan] [green]{challenge['co2_impact']} kg[/green]",
                        title=f"Challenge {i + 1}",
                        border_style="blue",
                        padding=(1, 2)
                    )
                    console.print(challenge_panel)
                    print()  # Add space between panels

                # Step 4: Select challenge
                challenge_idx = int(input("\nEnter challenge number (0 to go back): ")) - 1
                if challenge_idx == -1:
                    return
                if challenge_idx < 0 or challenge_idx >= len(available_challenges):
                    console.print("[bold red]Invalid selection.[/bold red]")
                    input("Press Enter to continue...")
                    return

                # Step 5: Join the challenge
                selected_challenge = available_challenges[challenge_idx].copy()
                selected_challenge['start_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
                selected_challenge['current_progress'] = 0
                selected_challenge['category'] = category
                selected_challenge['difficulty'] = difficulty

                # Confirmation panel
                end_date = (datetime.datetime.now() + datetime.timedelta(days=selected_challenge['duration'])).strftime("%Y-%m-%d")

                console.print(Panel(
                    f"[bold green]Challenge:[/bold green] {selected_challenge['title']}\n"
                    f"[bold green]Target:[/bold green] {selected_challenge['target']} {selected_challenge['unit']}\n"
                    f"[bold green]Duration:[/bold green] {selected_challenge['duration']} days\n"
                    f"[bold green]Complete by:[/bold green] {end_date}\n\n"
                    f"Are you ready to commit to this challenge?",
                    title="Challenge Confirmation",
                    border_style="green",
                    padding=(1, 2)
                ))

                confirm = input("Join this challenge? (y/n): ")
                if confirm.lower() != 'y':
                    console.print("[yellow]Challenge not joined.[/yellow]")
                    input("Press Enter to continue...")
                    return

                # Add to user's active challenges
                self.user_challenges[username]["active"].append(selected_challenge)
                self._save_user_challenges()

                # Success message with tips
                console.print(Panel(
                    f"[bold green]✓ You've successfully joined the {selected_challenge['title']} challenge![/bold green]\n\n"
                    f"[cyan]Tips to succeed:[/cyan]\n"
                    f"• Track your progress regularly\n"
                    f"• Set reminders to stay on track\n"
                    f"• Share your challenge with friends for accountability\n"
                    f"• Break down your target into smaller daily goals",
                    title="Challenge Joined!",
                    border_style="green",
                    padding=(1, 2)
                ))

            except ValueError:
                console.print("[bold red]Please enter a valid number.[/bold red]")

        else:
            # Fallback to ASCII art display
            ascii_art.display_section_header("Join New Challenge")

            # Step 1: Select category
            print("\nSelect a challenge category:")
            for i, category in enumerate(CHALLENGE_CATEGORIES):
                print(f"  {i + 1}. {category}")

            try:
                category_idx = int(input("\nEnter category number: ")) - 1
                if category_idx < 0 or category_idx >= len(CHALLENGE_CATEGORIES):
                    print("Invalid selection.")
                    input("Press Enter to continue...")
                    return

                category = CHALLENGE_CATEGORIES[category_idx]

                # Step 2: Select difficulty
                ascii_art.clear_screen()
                ascii_art.display_section_header(f"Join {category} Challenge")

                print("\nSelect difficulty level:")
                for i, difficulty in enumerate(DIFFICULTY_LEVELS):
                    print(f"  {i + 1}. {difficulty}")

                difficulty_idx = int(input("\nEnter difficulty number: ")) - 1
                if difficulty_idx < 0 or difficulty_idx >= len(DIFFICULTY_LEVELS):
                    print("Invalid selection.")
                    input("Press Enter to continue...")
                    return

                difficulty = DIFFICULTY_LEVELS[difficulty_idx]

                # Step 3: Display available challenges for selected category and difficulty
                if category not in self.challenges or difficulty not in self.challenges[category]:
                    print(f"No challenges found for {category} at {difficulty} level.")
                    input("Press Enter to continue...")
                    return

                available_challenges = self.challenges[category][difficulty]

                ascii_art.clear_screen()
                ascii_art.display_section_header(f"{difficulty} {category} Challenges")

                print("\nAvailable challenges:")
                for i, challenge in enumerate(available_challenges):
                    print(f"  {i + 1}. {challenge['title']}")
                    print(f"     Description: {challenge['description']}")
                    print(f"     Target: {challenge['target']} {challenge['unit']}")
                    print(f"     Duration: {challenge['duration']} days")
                    print(f"     Points: {challenge['points']}")
                    print(f"     Estimated CO2 impact: {challenge['co2_impact']} kg")
                    print()

                # Step 4: Select challenge
                challenge_idx = int(input("\nEnter challenge number (0 to go back): ")) - 1
                if challenge_idx == -1:
                    return
                if challenge_idx < 0 or challenge_idx >= len(available_challenges):
                    print("Invalid selection.")
                    input("Press Enter to continue...")
                    return

                # Step 5: Join the challenge
                selected_challenge = available_challenges[challenge_idx].copy()
                selected_challenge['start_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
                selected_challenge['current_progress'] = 0
                selected_challenge['category'] = category
                selected_challenge['difficulty'] = difficulty

                # Add to user's active challenges
                self.user_challenges[username]["active"].append(selected_challenge)
                self._save_user_challenges()

                ascii_art.display_success_message(f"You've joined the {selected_challenge['title']} challenge!")
                print(f"Target: {selected_challenge['target']} {selected_challenge['unit']}")
                print(f"Duration: {selected_challenge['duration']} days")
                print(f"Complete by: {(datetime.datetime.strptime(selected_challenge['start_date'], '%Y-%m-%d') + datetime.timedelta(days=selected_challenge['duration'])).strftime('%Y-%m-%d')}")

            except ValueError:
                print("Please enter a valid number.")

        input("\nPress Enter to continue...")

    def create_custom_challenge(self, username: str) -> None:
        """Create a custom eco-challenge."""
        # ascii_art is already imported at the top of the file

        if username not in self.user_challenges:
            self.user_challenges[username] = {"active": [], "completed": [], "points": 0}

        ascii_art.clear_screen()

        if HAS_RICH:
            # Enhanced UI with Rich
            console.print(Panel.fit(
                Text("🛠️  Create Custom Challenge", style="bold cyan"),
                border_style="cyan"
            ))

            console.print(Panel(
                "Design your own personalized eco-challenge that matches your sustainability goals!",
                title="Custom Challenge Creator",
                border_style="green",
                padding=(1, 2)
            ))

            # Step 1: Challenge details with form-like UI
            console.print(Panel(
                "Let's start with the basic details of your challenge.",
                title="Step 1: Challenge Details",
                border_style="blue",
                padding=(1, 2)
            ))

            # Title input with validation
            while True:
                title = input("\n[1/6] Challenge title: ")
                if not title:
                    console.print("[bold red]Title cannot be empty.[/bold red]")
                    continue
                break

            # Description input with validation
            while True:
                description = input("\n[2/6] Challenge description: ")
                if not description:
                    console.print("[bold red]Description cannot be empty.[/bold red]")
                    continue
                break

            # Step 2: Category selection
            console.print(Panel(
                "Choose a category that best fits your challenge.",
                title="Step 2: Select Category",
                border_style="blue",
                padding=(1, 2)
            ))

            # Create a grid of category options with icons
            category_icons = {
                "Cycling": "🚲",
                "Transportation": "🚌",
                "Energy": "⚡",
                "Waste": "♻️",
                "Food": "🍎",
                "Community": "👥"
            }

            # Display categories in a table
            category_table = Table(box=rich.box.ROUNDED, border_style="blue", show_header=False)
            category_table.add_column("Number", style="dim", width=8)
            category_table.add_column("Category", style="green bold")
            category_table.add_column("Description", style="cyan")

            category_descriptions = {
                "Cycling": "Bike-related challenges to reduce emissions",
                "Transportation": "Eco-friendly transport alternatives",
                "Energy": "Reduce your energy consumption",
                "Waste": "Minimize waste and increase recycling",
                "Food": "Sustainable eating and food choices",
                "Community": "Engage others in sustainability"
            }

            for i, category in enumerate(CHALLENGE_CATEGORIES):
                icon = category_icons.get(category, "🌱")
                description = category_descriptions.get(category, "")
                category_table.add_row(
                    f"{i + 1}",
                    f"{icon} {category}",
                    description
                )

            console.print(category_table)

            try:
                category_idx = int(input("\n[3/6] Enter category number: ")) - 1
                if category_idx < 0 or category_idx >= len(CHALLENGE_CATEGORIES):
                    console.print("[bold red]Invalid selection.[/bold red]")
                    input("Press Enter to continue...")
                    return

                category = CHALLENGE_CATEGORIES[category_idx]
                category_icon = category_icons.get(category, "🌱")

                # Step 3: Target and unit with visual guidance
                console.print(Panel(
                    f"Define what you want to achieve with this {category} challenge.",
                    title="Step 3: Set Target and Unit",
                    border_style="blue",
                    padding=(1, 2)
                ))

                # Show examples based on category
                examples = {
                    "Cycling": "Examples: 50 km, 10 trips, 5 days",
                    "Transportation": "Examples: 5 trips, 7 days, 3 modes",
                    "Energy": "Examples: 10 kWh, 5 devices, 7 days",
                    "Waste": "Examples: 2 kg, 5 items, 14 days",
                    "Food": "Examples: 7 meals, 5 days, 3 recipes",
                    "Community": "Examples: 3 events, 5 people, 2 projects"
                }

                console.print(f"[italic cyan]{examples.get(category, 'Examples: 10 units, 7 days, 5 items')}[/italic cyan]")

                try:
                    # Target input with validation
                    while True:
                        try:
                            target = float(input("\n[4/6] Target value: "))
                            if target <= 0:
                                console.print("[bold red]Target must be greater than zero.[/bold red]")
                                continue
                            break
                        except ValueError:
                            console.print("[bold red]Please enter a valid number.[/bold red]")

                    # Unit input with suggestions
                    suggested_units = {
                        "Cycling": ["km", "trips", "days"],
                        "Transportation": ["trips", "days", "modes"],
                        "Energy": ["kWh", "devices", "days"],
                        "Waste": ["kg", "items", "days"],
                        "Food": ["meals", "days", "recipes"],
                        "Community": ["events", "people", "projects"]
                    }

                    category_units = suggested_units.get(category, ["units", "days", "items"])
                    console.print(f"[italic]Suggested units: {', '.join(category_units)}[/italic]")

                    while True:
                        unit = input("\nUnit: ")
                        if not unit:
                            console.print("[bold red]Unit cannot be empty.[/bold red]")
                            continue
                        break

                    # Step 4: Duration with visual timeline
                    console.print(Panel(
                        "How long do you want your challenge to last?",
                        title="Step 4: Set Duration",
                        border_style="blue",
                        padding=(1, 2)
                    ))

                    # Create a visual timeline
                    duration_table = Table(box=rich.box.ROUNDED, border_style="blue", show_header=False)
                    duration_table.add_column("Number", style="dim", width=8)
                    duration_table.add_column("Duration", style="green bold")
                    duration_table.add_column("Timeline", style="cyan")

                    for i, days in enumerate(CHALLENGE_DURATIONS):
                        # Create a visual representation of duration
                        if days <= 7:
                            timeline = "[green]■[/green]" * (days // 1) + " (1 week)"
                        elif days <= 14:
                            timeline = "[green]■[/green]" * (days // 2) + " (2 weeks)"
                        elif days <= 30:
                            timeline = "[green]■[/green]" * (days // 5) + " (1 month)"
                        else:
                            timeline = "[green]■[/green]" * (days // 10) + " (3 months)"

                        duration_table.add_row(
                            f"{i + 1}",
                            f"{days} days",
                            timeline
                        )

                    console.print(duration_table)

                    duration_idx = int(input("\n[5/6] Enter duration number: ")) - 1
                    if duration_idx < 0 or duration_idx >= len(CHALLENGE_DURATIONS):
                        console.print("[bold red]Invalid selection.[/bold red]")
                        input("Press Enter to continue...")
                        return

                    duration = CHALLENGE_DURATIONS[duration_idx]

                    # Step 5: Difficulty with visual indicators
                    console.print(Panel(
                        "Choose a difficulty level that matches your experience and commitment level.",
                        title="Step 5: Select Difficulty Level",
                        border_style="blue",
                        padding=(1, 2)
                    ))

                    # Create a table for difficulty levels
                    difficulty_table = Table(box=rich.box.ROUNDED, border_style="blue", show_header=False)
                    difficulty_table.add_column("Number", style="dim", width=8)
                    difficulty_table.add_column("Difficulty", style="green bold")
                    difficulty_table.add_column("Indicator", justify="center")
                    difficulty_table.add_column("Description", style="cyan")

                    difficulty_descriptions = {
                        "Beginner": "Perfect for those just starting their sustainability journey",
                        "Intermediate": "For those with some experience in sustainable practices",
                        "Advanced": "Challenging goals for sustainability enthusiasts",
                        "Expert": "The highest level of commitment to environmental impact"
                    }

                    difficulty_indicators = {
                        "Beginner": "[green]●[/green][dim]○○○[/dim]",
                        "Intermediate": "[green]●●[/green][dim]○○[/dim]",
                        "Advanced": "[green]●●●[/green][dim]○[/dim]",
                        "Expert": "[green]●●●●[/green]"
                    }

                    for i, difficulty in enumerate(DIFFICULTY_LEVELS):
                        indicator = difficulty_indicators.get(difficulty, "")
                        description = difficulty_descriptions.get(difficulty, "")
                        difficulty_table.add_row(
                            f"{i + 1}",
                            difficulty,
                            indicator,
                            description
                        )

                    console.print(difficulty_table)

                    difficulty_idx = int(input("\n[6/6] Enter difficulty number: ")) - 1
                    if difficulty_idx < 0 or difficulty_idx >= len(DIFFICULTY_LEVELS):
                        console.print("[bold red]Invalid selection.[/bold red]")
                        input("Press Enter to continue...")
                        return

                    difficulty = DIFFICULTY_LEVELS[difficulty_idx]

                    # Calculate points and CO2 impact based on difficulty and duration
                    points_multiplier = {
                        "Beginner": 10,
                        "Intermediate": 20,
                        "Advanced": 40,
                        "Expert": 100
                    }

                    co2_multiplier = {
                        "Beginner": 0.2,
                        "Intermediate": 0.5,
                        "Advanced": 1.0,
                        "Expert": 2.0
                    }

                    points = int(points_multiplier[difficulty] * target * (duration / 7))
                    co2_impact = co2_multiplier[difficulty] * target * (duration / 7)

                    # Create custom challenge
                    custom_challenge = {
                        "title": title,
                        "description": description,
                        "target": target,
                        "unit": unit,
                        "duration": duration,
                        "points": points,
                        "co2_impact": co2_impact,
                        "category": category,
                        "difficulty": difficulty,
                        "start_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "current_progress": 0,
                        "custom": True
                    }

                    # Preview challenge
                    ascii_art.clear_screen()

                    # Calculate end date
                    start_date = datetime.datetime.now()
                    end_date = start_date + datetime.timedelta(days=duration)

                    console.print(Panel.fit(
                        Text("🔍 Challenge Preview", style="bold cyan"),
                        border_style="cyan"
                    ))

                    # Create a visually appealing challenge preview
                    preview_panel = Panel(
                        f"[bold green]{title}[/bold green]\n\n"
                        f"[cyan]Description:[/cyan] {description}\n"
                        f"[cyan]Category:[/cyan] {category_icon} {category}\n"
                        f"[cyan]Difficulty:[/cyan] {difficulty} {difficulty_indicators.get(difficulty, '')}\n"
                        f"[cyan]Target:[/cyan] {target} {unit}\n"
                        f"[cyan]Duration:[/cyan] {duration} days (until {end_date.strftime('%Y-%m-%d')})\n"
                        f"[cyan]Points:[/cyan] [yellow]{points}[/yellow]\n"
                        f"[cyan]Estimated CO2 impact:[/cyan] [green]{co2_impact:.2f} kg[/green]",
                        title="Your Custom Challenge",
                        border_style="green",
                        padding=(1, 2)
                    )
                    console.print(preview_panel)

                    # Add impact visualization
                    console.print(Panel(
                        f"This challenge will earn you [bold yellow]{points}[/bold yellow] points and save approximately [bold green]{co2_impact:.2f}[/bold green] kg of CO2!\n\n"
                        f"That's equivalent to:\n"
                        f"🌳 The CO2 absorbed by [green]{co2_impact/10:.1f}[/green] trees in one month\n"
                        f"🚗 Emissions saved from [green]{co2_impact/0.2:.1f}[/green] km of driving",
                        title="Environmental Impact",
                        border_style="blue",
                        padding=(1, 2)
                    ))

                    # Confirmation with clear options
                    console.print(Panel(
                        "Ready to start this challenge? You can track your progress in the 'View active challenges' section.",
                        title="Confirmation",
                        border_style="yellow",
                        padding=(1, 2)
                    ))

                    confirm = input("\nCreate this challenge? (y/n): ")

                    if confirm.lower() == 'y':
                        # Add to user's active challenges
                        self.user_challenges[username]["active"].append(custom_challenge)
                        self._save_user_challenges()

                        # Also add to predefined challenges if it doesn't exist
                        if category not in self.challenges:
                            self.challenges[category] = {}

                        if difficulty not in self.challenges[category]:
                            self.challenges[category][difficulty] = []

                        # Check if a similar challenge already exists
                        exists = False
                        for c in self.challenges[category][difficulty]:
                            if c['title'] == title:
                                exists = True
                                break

                        if not exists:
                            challenge_template = {k: v for k, v in custom_challenge.items() if k not in ['start_date', 'current_progress', 'custom']}
                            self.challenges[category][difficulty].append(challenge_template)
                            self._save_challenges()

                        # Success message with next steps
                        console.print(Panel(
                            f"[bold green]✓ Custom challenge created successfully![/bold green]\n\n"
                            f"Your challenge [bold]{title}[/bold] has been added to your active challenges.\n\n"
                            f"[cyan]Next steps:[/cyan]\n"
                            f"• Track your progress in 'View active challenges'\n"
                            f"• Set reminders to update your progress regularly\n"
                            f"• Complete the challenge by {end_date.strftime('%Y-%m-%d')} to earn {points} points",
                            title="Challenge Created!",
                            border_style="green",
                            padding=(1, 2)
                        ))
                    else:
                        console.print("[yellow]Challenge creation cancelled.[/yellow]")

                except ValueError:
                    console.print("[bold red]Please enter valid numeric values.[/bold red]")

            except ValueError:
                console.print("[bold red]Please enter a valid number.[/bold red]")

        else:
            # Fallback to ASCII art display
            ascii_art.display_section_header("Create Custom Challenge")

            print("\nCreate your own personalized eco-challenge!")

            # Step 1: Challenge details
            title = input("\nChallenge title: ")
            if not title:
                print("Title cannot be empty.")
                input("Press Enter to continue...")
                return

            description = input("Challenge description: ")
            if not description:
                print("Description cannot be empty.")
                input("Press Enter to continue...")
                return

            # Step 2: Category
            print("\nSelect a category:")
            for i, category in enumerate(CHALLENGE_CATEGORIES):
                print(f"  {i + 1}. {category}")

            try:
                category_idx = int(input("\nEnter category number: ")) - 1
                if category_idx < 0 or category_idx >= len(CHALLENGE_CATEGORIES):
                    print("Invalid selection.")
                    input("Press Enter to continue...")
                    return

                category = CHALLENGE_CATEGORIES[category_idx]

                # Step 3: Target and unit
                try:
                    target = float(input("\nTarget value (e.g., 10 for 10 km): "))
                    if target <= 0:
                        print("Target must be greater than zero.")
                        input("Press Enter to continue...")
                        return

                    unit = input("Unit (e.g., km, trips, days): ")
                    if not unit:
                        print("Unit cannot be empty.")
                        input("Press Enter to continue...")
                        return

                    # Step 4: Duration
                    print("\nSelect challenge duration:")
                    for i, days in enumerate(CHALLENGE_DURATIONS):
                        print(f"  {i + 1}. {days} days")

                    duration_idx = int(input("\nEnter duration number: ")) - 1
                    if duration_idx < 0 or duration_idx >= len(CHALLENGE_DURATIONS):
                        print("Invalid selection.")
                        input("Press Enter to continue...")
                        return

                    duration = CHALLENGE_DURATIONS[duration_idx]

                    # Step 5: Difficulty
                    print("\nSelect difficulty level:")
                    for i, difficulty in enumerate(DIFFICULTY_LEVELS):
                        print(f"  {i + 1}. {difficulty}")

                    difficulty_idx = int(input("\nEnter difficulty number: ")) - 1
                    if difficulty_idx < 0 or difficulty_idx >= len(DIFFICULTY_LEVELS):
                        print("Invalid selection.")
                        input("Press Enter to continue...")
                        return

                    difficulty = DIFFICULTY_LEVELS[difficulty_idx]

                    # Calculate points and CO2 impact based on difficulty and duration
                    points_multiplier = {
                        "Beginner": 10,
                        "Intermediate": 20,
                        "Advanced": 40,
                        "Expert": 100
                    }

                    co2_multiplier = {
                        "Beginner": 0.2,
                        "Intermediate": 0.5,
                        "Advanced": 1.0,
                        "Expert": 2.0
                    }

                    points = int(points_multiplier[difficulty] * target * (duration / 7))
                    co2_impact = co2_multiplier[difficulty] * target * (duration / 7)

                    # Create custom challenge
                    custom_challenge = {
                        "title": title,
                        "description": description,
                        "target": target,
                        "unit": unit,
                        "duration": duration,
                        "points": points,
                        "co2_impact": co2_impact,
                        "category": category,
                        "difficulty": difficulty,
                        "start_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "current_progress": 0,
                        "custom": True
                    }

                    # Preview challenge
                    ascii_art.clear_screen()
                    ascii_art.display_section_header("Challenge Preview")

                    print(f"\nTitle: {title}")
                    print(f"Description: {description}")
                    print(f"Category: {category}")
                    print(f"Difficulty: {difficulty}")
                    print(f"Target: {target} {unit}")
                    print(f"Duration: {duration} days")
                    print(f"Points: {points}")
                    print(f"Estimated CO2 impact: {co2_impact:.2f} kg")

                    confirm = input("\nCreate this challenge? (y/n): ")

                    if confirm.lower() == 'y':
                        # Add to user's active challenges
                        self.user_challenges[username]["active"].append(custom_challenge)
                        self._save_user_challenges()

                        # Also add to predefined challenges if it doesn't exist
                        if category not in self.challenges:
                            self.challenges[category] = {}

                        if difficulty not in self.challenges[category]:
                            self.challenges[category][difficulty] = []

                        # Check if a similar challenge already exists
                        exists = False
                        for c in self.challenges[category][difficulty]:
                            if c['title'] == title:
                                exists = True
                                break

                        if not exists:
                            challenge_template = {k: v for k, v in custom_challenge.items() if k not in ['start_date', 'current_progress', 'custom']}
                            self.challenges[category][difficulty].append(challenge_template)
                            self._save_challenges()

                        ascii_art.display_success_message("Custom challenge created successfully!")
                    else:
                        print("Challenge creation cancelled.")

                except ValueError:
                    print("Please enter valid numeric values.")

            except ValueError:
                print("Please enter a valid number.")

        input("\nPress Enter to continue...")

    def view_challenge_history(self, username: str) -> None:
        """View challenge history and achievements."""
        # ascii_art is already imported at the top of the file
        from tabulate import tabulate

        if username not in self.user_challenges:
            self.user_challenges[username] = {"active": [], "completed": [], "points": 0}

        completed_challenges = self.user_challenges[username]["completed"]
        total_points = self.user_challenges[username]["points"]

        ascii_art.clear_screen()

        if HAS_RICH:
            # Enhanced UI with Rich
            console.print(Panel.fit(
                Text("🏆 Challenge History & Achievements", style="bold cyan"),
                border_style="cyan"
            ))

            # Calculate statistics
            total_co2_saved = sum(c['co2_impact'] for c in completed_challenges)

            # Display achievement levels
            achievement_levels = [
                ("Eco Beginner", 0, "🌱"),
                ("Eco Novice", 500, "🌿"),
                ("Green Enthusiast", 1000, "🌲"),
                ("Sustainability Advocate", 2500, "🌍"),
                ("Climate Champion", 5000, "⭐"),
                ("Eco Warrior", 10000, "🛡️"),
                ("Planet Protector", 25000, "🌟")
            ]

            # Find current level
            current_level_idx = 0
            for i, (level, points, _) in enumerate(achievement_levels):
                if total_points >= points:
                    current_level_idx = i

            current_level, _, current_icon = achievement_levels[current_level_idx]

            # Find next level if not at max
            next_level = None
            if current_level_idx < len(achievement_levels) - 1:
                next_level = achievement_levels[current_level_idx + 1]
                next_level_name, next_level_points, next_icon = next_level
                points_needed = next_level_points - total_points

            # Create a summary panel with achievement info
            summary_content = [
                f"[bold yellow]Total Eco-Points:[/bold yellow] [bold green]{total_points}[/bold green]",
                f"[bold yellow]Current Level:[/bold yellow] [bold cyan]{current_icon} {current_level}[/bold cyan]"
            ]

            if next_level:
                progress_percentage = min(100, int((total_points / next_level_points) * 100))
                progress_bar = f"[{'■' * (progress_percentage // 10)}{'□' * (10 - (progress_percentage // 10))}] {progress_percentage}%"
                summary_content.append(f"[bold yellow]Next Level:[/bold yellow] [bold magenta]{next_icon} {next_level_name}[/bold magenta] (need {points_needed} more points)")
                summary_content.append(f"[bold yellow]Progress:[/bold yellow] {progress_bar}")
            else:
                summary_content.append("[bold green]Congratulations! You've reached the maximum achievement level![/bold green]")

            summary_content.append(f"[bold yellow]Total CO2 Saved:[/bold yellow] [bold green]{total_co2_saved:.2f} kg[/bold green]")

            # Create achievement summary panel
            console.print(Panel(
                "\n".join(summary_content),
                title="Achievement Summary",
                border_style="green",
                padding=(1, 2)
            ))

            # Create achievement levels visualization
            console.print(Panel(
                "Your Achievement Journey",
                title="Achievement Levels",
                border_style="blue",
                padding=(1, 0)
            ))

            # Create a table for achievement levels
            levels_table = Table(box=rich.box.ROUNDED, border_style="blue", show_header=False)
            levels_table.add_column("Icon", justify="center", width=6)
            levels_table.add_column("Level", style="cyan bold")
            levels_table.add_column("Points", justify="right", style="yellow")
            levels_table.add_column("Status", justify="center")

            for i, (level, points, icon) in enumerate(achievement_levels):
                if i == current_level_idx:
                    status = "[bold green]CURRENT[/bold green]"
                    level_style = "bold green"
                elif i < current_level_idx:
                    status = "[green]✓[/green]"
                    level_style = "green"
                else:
                    status = f"[dim]{points - total_points} points needed[/dim]"
                    level_style = "dim"

                levels_table.add_row(
                    f"[{level_style}]{icon}[/{level_style}]",
                    f"[{level_style}]{level}[/{level_style}]",
                    f"[{level_style}]{points}[/{level_style}]",
                    status
                )

            console.print(levels_table)

            # Category breakdown
            challenge_counts = {}
            for challenge in completed_challenges:
                category = challenge.get('category', 'Unknown')
                if category not in challenge_counts:
                    challenge_counts[category] = 0
                challenge_counts[category] += 1

            if challenge_counts:
                # Create a category breakdown panel
                category_content = []
                category_icons = {
                    "Cycling": "🚲",
                    "Transportation": "🚌",
                    "Energy": "⚡",
                    "Waste": "♻️",
                    "Food": "🍎",
                    "Community": "👥",
                    "Unknown": "❓"
                }

                for category, count in challenge_counts.items():
                    icon = category_icons.get(category, "🌱")
                    category_content.append(f"{icon} [bold cyan]{category}:[/bold cyan] [green]{count}[/green] challenges completed")

                console.print(Panel(
                    "\n".join(category_content),
                    title="Category Breakdown",
                    border_style="blue",
                    padding=(1, 2)
                ))

            # Completed challenges table
            if completed_challenges:
                console.print(Panel(
                    "Your completed challenges are listed below, most recent first.",
                    title="Completed Challenges",
                    border_style="blue",
                    padding=(1, 2)
                ))

                # Create a table for completed challenges
                challenges_table = Table(
                    title="Challenge History",
                    box=rich.box.ROUNDED,
                    border_style="blue",
                    header_style="bold cyan",
                    show_lines=True
                )

                # Add columns
                challenges_table.add_column("Date", style="dim")
                challenges_table.add_column("Challenge", style="green")
                challenges_table.add_column("Category", style="cyan")
                challenges_table.add_column("Difficulty", style="magenta")
                challenges_table.add_column("Points", justify="right", style="yellow")
                challenges_table.add_column("CO2 Impact", justify="right", style="green")

                # Add rows with appropriate styling
                for challenge in sorted(completed_challenges, key=lambda x: x.get('completion_date', ''), reverse=True):
                    completion_date = challenge.get('completion_date', 'Unknown')
                    category = challenge.get('category', 'Unknown')
                    icon = category_icons.get(category, "🌱")

                    challenges_table.add_row(
                        completion_date,
                        challenge['title'],
                        f"{icon} {category}",
                        challenge.get('difficulty', 'Unknown'),
                        str(challenge['points']),
                        f"{challenge['co2_impact']:.2f} kg"
                    )

                console.print(challenges_table)

                # Add motivational message
                console.print(Panel(
                    f"[italic]Keep completing challenges to increase your impact and reach the next level![/italic]",
                    border_style="dim blue",
                    padding=(0, 1)
                ))
            else:
                console.print(Panel(
                    "You haven't completed any challenges yet.\nJoin some challenges and start making a difference!",
                    title="No Completed Challenges",
                    border_style="yellow",
                    padding=(1, 2)
                ))
        else:
            # Fallback to ASCII art display
            ascii_art.display_section_header("Challenge History & Achievements")

            print(f"\nTotal Eco-Points: {total_points}")

            # Calculate statistics
            total_co2_saved = sum(c['co2_impact'] for c in completed_challenges)

            challenge_counts = {}
            for challenge in completed_challenges:
                category = challenge.get('category', 'Unknown')
                if category not in challenge_counts:
                    challenge_counts[category] = 0
                challenge_counts[category] += 1

            # Display achievement levels
            achievement_levels = [
                ("Eco Novice", 500),
                ("Green Enthusiast", 1000),
                ("Sustainability Advocate", 2500),
                ("Climate Champion", 5000),
                ("Eco Warrior", 10000),
                ("Planet Protector", 25000)
            ]

            current_level = "Eco Beginner"
            next_level = None
            for level, points in achievement_levels:
                if total_points >= points:
                    current_level = level
                else:
                    next_level = (level, points)
                    break

            print(f"Current achievement level: {current_level}")

            if next_level:
                points_needed = next_level[1] - total_points
                print(f"Next level: {next_level[0]} (need {points_needed} more points)")

            print(f"\nTotal CO2 saved: {total_co2_saved:.2f} kg")
            print("\nCategory breakdown:")
            for category, count in challenge_counts.items():
                print(f"  {category}: {count} challenges completed")

            if completed_challenges:
                print("\nCompleted Challenges:")

                headers = ["Date", "Challenge", "Category", "Difficulty", "Points", "CO2 Impact"]
                rows = []

                for challenge in sorted(completed_challenges, key=lambda x: x.get('completion_date', ''), reverse=True):
                    completion_date = challenge.get('completion_date', 'Unknown')
                    rows.append([
                        completion_date,
                        challenge['title'],
                        challenge.get('category', 'Unknown'),
                        challenge.get('difficulty', 'Unknown'),
                        challenge['points'],
                        f"{challenge['co2_impact']:.2f} kg"
                    ])

                print(tabulate(rows, headers=headers, tablefmt="grid"))
            else:
                print("\nYou haven't completed any challenges yet.")

        input("\nPress Enter to continue...")

    def manage_weekly_goals(self, username: str) -> None:
        """Manage weekly sustainability goals."""
        # ascii_art is already imported at the top of the file
        from tabulate import tabulate

        if username not in self.user_challenges:
            self.user_challenges[username] = {"active": [], "completed": [], "points": 0}

        if "weekly_goals" not in self.user_challenges[username]:
            self.user_challenges[username]["weekly_goals"] = {
                "last_updated": None,
                "current_week": None,
                "goals": []
            }

        weekly_goals = self.user_challenges[username]["weekly_goals"]

        # Check if we need to update the week
        today = datetime.datetime.now()
        current_week = f"{today.year}-W{today.isocalendar()[1]}"

        if weekly_goals["current_week"] != current_week:
            # It's a new week, update goals
            weekly_goals["current_week"] = current_week
            weekly_goals["last_updated"] = today.strftime("%Y-%m-%d")

            # Keep old incomplete goals, but mark them as continued
            old_goals = [g for g in weekly_goals.get("goals", []) if not g.get("completed", False)]
            for goal in old_goals:
                goal["continued"] = True

            # Add new recommended goals if needed
            if len(old_goals) < 3:
                num_new_goals = 3 - len(old_goals)
                new_goals = self._generate_recommended_goals(username, num_new_goals)
                weekly_goals["goals"] = old_goals + new_goals
            else:
                weekly_goals["goals"] = old_goals

            self._save_user_challenges()

        while True:
            ascii_art.clear_screen()

            if HAS_RICH:
                # Enhanced UI with Rich
                # Header with calendar icon and week information
                week_info = f"{weekly_goals['current_week']} (starting {weekly_goals['last_updated']})"
                console.print(Panel.fit(
                    Text("🗓️  Weekly Sustainability Goals", style="bold cyan"),
                    border_style="cyan"
                ))

                # Week information panel
                console.print(Panel(
                    f"Current week: [bold green]{week_info}[/bold green]",
                    border_style="green",
                    padding=(0, 2)
                ))

                goals = weekly_goals.get("goals", [])

                if not goals:
                    console.print(Panel(
                        "You don't have any weekly goals set.\n"
                        "Add new goals or generate recommended ones to get started!",
                        title="No Goals Found",
                        border_style="yellow",
                        padding=(1, 2)
                    ))
                else:
                    # Create a table for goals
                    goals_table = Table(
                        title="Your Weekly Sustainability Goals",
                        box=rich.box.ROUNDED,
                        border_style="blue",
                        header_style="bold cyan",
                        show_lines=True,
                        padding=(0, 1)
                    )

                    # Add columns
                    goals_table.add_column("#", style="dim", width=3)
                    goals_table.add_column("Goal", style="green")
                    goals_table.add_column("Status", justify="center")
                    goals_table.add_column("Continued", justify="center", width=10)

                    # Add rows with appropriate styling
                    for i, goal in enumerate(goals):
                        # Status with icon and color
                        if goal.get("completed", False):
                            status = "[bold green]✓ Completed[/bold green]"
                        else:
                            status = "[blue]⟳ In progress[/blue]"

                        # Continued status with icon
                        continued = "[yellow]↻ Yes[/yellow]" if goal.get("continued", False) else "No"

                        # Add the row
                        goals_table.add_row(
                            str(i + 1),
                            goal["description"],
                            status,
                            continued
                        )

                    console.print(goals_table)

                # Create an options panel with icons
                options_panel = Panel(
                    "1. ➕ Add new goal\n"
                    "2. ✓ Mark goal as completed\n"
                    "3. ❌ Remove goal\n"
                    "4. 🔄 Generate recommended goals\n"
                    "5. ↩️ Return to Eco Challenges menu",
                    title="Options",
                    border_style="cyan",
                    padding=(1, 2)
                )
                console.print(options_panel)

                # Add a tip at the bottom
                console.print(Panel(
                    "[italic]Tip: Completing weekly goals earns you eco-points and helps build sustainable habits![/italic]",
                    border_style="dim blue",
                    padding=(0, 1)
                ))

                choice = input("\nSelect an option (1-5): ")
            else:
                # Fallback to ASCII art display
                ascii_art.display_section_header("Weekly Sustainability Goals")

                print(f"\nCurrent week: {weekly_goals['current_week']} (starting {weekly_goals['last_updated']})")

                goals = weekly_goals.get("goals", [])

                if not goals:
                    print("\nYou don't have any weekly goals set.")
                else:
                    print("\nYour weekly goals:")

                    headers = ["#", "Goal", "Status", "Continued"]
                    rows = []

                    for i, goal in enumerate(goals):
                        status = "✓ Completed" if goal.get("completed", False) else "In progress"
                        continued = "Yes" if goal.get("continued", False) else "No"

                        rows.append([
                            i + 1,
                            goal["description"],
                            status,
                            continued
                        ])

                    print(tabulate(rows, headers=headers, tablefmt="grid"))

                print("\nOptions:")
                print("  1. Add new goal")
                print("  2. Mark goal as completed")
                print("  3. Remove goal")
                print("  4. Generate recommended goals")
                print("  5. Return to Eco Challenges menu")

                choice = input("\nSelect an option (1-5): ")

            if choice == '1':
                self._add_weekly_goal(username)
            elif choice == '2':
                self._complete_weekly_goal(username)
            elif choice == '3':
                self._remove_weekly_goal(username)
            elif choice == '4':
                self._regenerate_weekly_goals(username)
            elif choice == '5':
                break
            else:
                if HAS_RICH:
                    console.print("[bold red]Invalid choice. Please try again.[/bold red]")
                else:
                    print("Invalid choice.")
                input("Press Enter to continue...")

    def _add_weekly_goal(self, username: str) -> None:
        """Add a new weekly goal."""
        weekly_goals = self.user_challenges[username]["weekly_goals"]

        print("\nAdd a new weekly sustainability goal:")
        description = input("Goal description: ")

        if not description:
            print("Goal description cannot be empty.")
            input("Press Enter to continue...")
            return

        new_goal = {
            "description": description,
            "completed": False,
            "continued": False,
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d")
        }

        weekly_goals["goals"].append(new_goal)
        self._save_user_challenges()

        print("New goal added successfully!")
        input("Press Enter to continue...")

    def _complete_weekly_goal(self, username: str) -> None:
        """Mark a weekly goal as completed."""
        weekly_goals = self.user_challenges[username]["weekly_goals"]
        goals = weekly_goals.get("goals", [])

        if not goals:
            print("You don't have any weekly goals to complete.")
            input("Press Enter to continue...")
            return

        # List incomplete goals
        incomplete_goals = [(i, g) for i, g in enumerate(goals) if not g.get("completed", False)]

        if not incomplete_goals:
            print("All your weekly goals are already completed! Great job!")
            input("Press Enter to continue...")
            return

        print("\nWhich goal would you like to mark as completed?")
        for i, (idx, goal) in enumerate(incomplete_goals):
            print(f"  {i + 1}. {goal['description']}")

        try:
            choice = int(input("\nEnter goal number: ")) - 1
            if choice < 0 or choice >= len(incomplete_goals):
                print("Invalid selection.")
                input("Press Enter to continue...")
                return

            # Get the actual index in the goals list
            actual_idx, goal = incomplete_goals[choice]

            # Mark as completed
            goal["completed"] = True
            goal["completion_date"] = datetime.datetime.now().strftime("%Y-%m-%d")

            # Award points
            points_earned = 50  # Base points for weekly goal completion
            if goal.get("continued", False):
                points_earned = 75  # Bonus for persisting on continued goals

            self.user_challenges[username]["points"] += points_earned

            self._save_user_challenges()

            print(f"Goal marked as completed! You earned {points_earned} eco-points!")

        except ValueError:
            print("Please enter a valid number.")

        input("Press Enter to continue...")

    def _remove_weekly_goal(self, username: str) -> None:
        """Remove a weekly goal."""
        weekly_goals = self.user_challenges[username]["weekly_goals"]
        goals = weekly_goals.get("goals", [])

        if not goals:
            print("You don't have any weekly goals to remove.")
            input("Press Enter to continue...")
            return

        print("\nWhich goal would you like to remove?")
        for i, goal in enumerate(goals):
            status = " (Completed)" if goal.get("completed", False) else ""

            print(f"  {i + 1}. {goal['description']}{status}")

        try:
            choice = int(input("\nEnter goal number: ")) - 1
            if choice < 0 or choice >= len(goals):
                print("Invalid selection.")
                input("Press Enter to continue...")
                return

            # Confirm removal
            confirm = input(f"Are you sure you want to remove this goal? (y/n): ")

            if confirm.lower() == 'y':
                weekly_goals["goals"].pop(choice)
                self._save_user_challenges()
                print("Goal removed successfully.")
            else:
                print("Goal not removed.")

        except ValueError:
            print("Please enter a valid number.")

        input("Press Enter to continue...")

    def _regenerate_weekly_goals(self, username: str) -> None:
        """Regenerate recommended weekly goals."""
        # ascii_art is already imported at the top of the file

        weekly_goals = self.user_challenges[username]["weekly_goals"]

        # Keep completed goals
        completed_goals = [g for g in weekly_goals.get("goals", []) if g.get("completed", False)]

        # Generate new recommended goals
        new_goals = self._generate_recommended_goals(username, 3)

        weekly_goals["goals"] = completed_goals + new_goals
        self._save_user_challenges()

        ascii_art.display_success_message("Weekly goals regenerated successfully!")
        input("Press Enter to continue...")

    def _generate_recommended_goals(self, username: str, num_goals: int) -> List[Dict]:
        """Generate recommended weekly goals based on user stats and preferences."""
        # In a real implementation, this would analyze past behavior and active challenges
        # For now, we'll just pick some from a predefined list

        suggested_goals = [
            "Cycle at least 3 times this week",
            "Try a new cycling route for your commute",
            "Properly inflate your bike tires for maximum efficiency",
            "Track your carbon savings from all cycling trips this week",
            "Replace at least one car trip with cycling",
            "Use reusable bags for all shopping trips",
            "Reduce shower time by 2 minutes each day",
            "Turn off electronic devices instead of leaving them on standby",
            "Meal plan to reduce food waste",
            "Buy locally-grown produce this week",
            "Go one day without using disposable plastics",
            "Air-dry clothes instead of using a dryer",
            "Share an eco-tip with a friend or family member",
            "Conduct a mini home energy audit and fix one issue",
            "Try one new vegetarian recipe this week",
            "Start collecting recyclables separately",
            "Clean out your excess possessions and donate usable items",
            "Use public transportation at least once this week",
            "Attend a community environmental event or webinar",
            "Calculate your carbon footprint and identify one improvement area"
        ]

        # Shuffle the list and pick the requested number of goals
        random.shuffle(suggested_goals)
        selected_goals = suggested_goals[:num_goals]

        return [
            {
                "description": description,
                "completed": False,
                "continued": False,
                "date_added": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            for description in selected_goals
        ]

    def display_impact_dashboard(self, username: str) -> None:
        """Display the challenge impact dashboard with visualizations."""
        # ascii_art is already imported at the top of the file

        try:
            # Try to import visualization libraries
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.ticker import MaxNLocator
            has_visualization = True
        except ImportError:
            has_visualization = False

        if username not in self.user_challenges:
            self.user_challenges[username] = {"active": [], "completed": [], "points": 0}

        completed_challenges = self.user_challenges[username]["completed"]
        active_challenges = self.user_challenges[username]["active"]

        ascii_art.clear_screen()

        if HAS_RICH:
            # Display header with Rich panel
            console.print(Panel.fit(
                Text("Challenge Impact Dashboard", style="bold cyan"),
                border_style="cyan"
            ))

            if not completed_challenges and not active_challenges:
                console.print(Panel(
                    "You haven't participated in any challenges yet.\n"
                    "Join some challenges to start tracking your environmental impact!",
                    title="No Challenge Data",
                    border_style="yellow"
                ))
                input("\nPress Enter to continue...")
                return

            # Calculate total statistics
            total_points = self.user_challenges[username]["points"]
            total_co2_saved = sum(c['co2_impact'] for c in completed_challenges)

            # Calculate potential additional impact from active challenges
            potential_co2 = sum(c['co2_impact'] for c in active_challenges)

            # Calculate real-world equivalents
            # Source: EPA estimates
            tree_months = total_co2_saved / 10.0  # Avg tree absorbs ~10kg CO2 per month
            car_km_saved = total_co2_saved / 0.2  # Avg car emits ~200g CO2 per km

            # Create a summary table
            summary_table = Table(title="Your Eco Impact Summary", box=rich.box.ROUNDED, border_style="green")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green", justify="right")

            summary_table.add_row("Total Eco-Points", f"[bold]{total_points}[/bold]")
            summary_table.add_row("CO2 Saved", f"[bold]{total_co2_saved:.2f}[/bold] kg")
            summary_table.add_row("Potential Additional CO2 Savings", f"[bold]{potential_co2:.2f}[/bold] kg")
            summary_table.add_row("Challenges Completed", f"[bold]{len(completed_challenges)}[/bold]")
            summary_table.add_row("Active Challenges", f"[bold]{len(active_challenges)}[/bold]")

            console.print(summary_table)

            # Create an equivalents panel
            equivalents_text = (
                f"🌳 CO2 absorbed by [bold green]{tree_months:.1f}[/bold green] trees in one month\n"
                f"🚗 Emissions saved from [bold green]{car_km_saved:.1f}[/bold green] km of driving"
            )

            console.print(Panel(
                equivalents_text,
                title="Your Impact Equivalents",
                border_style="blue"
            ))
        else:
            # Fallback to non-Rich display
            ascii_art.display_section_header("Challenge Impact Dashboard")

            if not completed_challenges and not active_challenges:
                print("\nYou haven't participated in any challenges yet.")
                print("Join some challenges to start tracking your environmental impact!")
                input("\nPress Enter to continue...")
                return

            # Calculate total statistics
            total_points = self.user_challenges[username]["points"]
            total_co2_saved = sum(c['co2_impact'] for c in completed_challenges)

            # Calculate potential additional impact from active challenges
            potential_co2 = sum(c['co2_impact'] for c in active_challenges)

            print(f"\nYour Eco Impact Summary:")
            print(f"Total Eco-Points: {total_points}")
            print(f"CO2 Saved from Completed Challenges: {total_co2_saved:.2f} kg")
            print(f"Potential Additional CO2 Savings: {potential_co2:.2f} kg")
            print(f"Total Challenges Completed: {len(completed_challenges)}")
            print(f"Active Challenges: {len(active_challenges)}")

            # Calculate real-world equivalents
            # Source: EPA estimates
            tree_months = total_co2_saved / 10.0  # Avg tree absorbs ~10kg CO2 per month
            car_km_saved = total_co2_saved / 0.2  # Avg car emits ~200g CO2 per km

            print("\nYour Impact Equivalents:")
            print(f"CO2 absorbed by {tree_months:.1f} trees in one month")
            print(f"Emissions saved from {car_km_saved:.1f} km of driving")

        if has_visualization and (completed_challenges or active_challenges):
            # Generate visualizations
            if HAS_RICH:
                with console.status("[bold green]Generating impact visualizations...[/bold green]"):
                    # Extract data for visualizations
                    categories = {}
                    for challenge in completed_challenges:
                        category = challenge.get('category', 'Other')
                        if category not in categories:
                            categories[category] = {
                                'count': 0,
                                'co2': 0,
                                'points': 0
                            }
                        categories[category]['count'] += 1
                        categories[category]['co2'] += challenge['co2_impact']
                        categories[category]['points'] += challenge['points']

                    # Create a temporary directory for visualizations if it doesn't exist
                    if not os.path.exists('temp'):
                        os.makedirs('temp')

                    # Create impact by category chart
                    if categories:
                        plt.figure(figsize=(10, 6))

                        # Extract data
                        cat_names = list(categories.keys())
                        co2_values = [categories[cat]['co2'] for cat in cat_names]

                        # Create bar chart with a more modern style
                        plt.style.use('ggplot')  # Use a more modern style
                        bars = plt.bar(cat_names, co2_values, color='green', alpha=0.7)

                        # Add data labels on top of bars
                        for bar in bars:
                            height = bar.get_height()
                            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                    f'{height:.1f}',
                                    ha='center', va='bottom', fontweight='bold')

                        plt.title('CO2 Savings by Challenge Category', fontsize=14, fontweight='bold')
                        plt.xlabel('Category', fontsize=12)
                        plt.ylabel('CO2 Saved (kg)', fontsize=12)
                        plt.xticks(rotation=45, ha='right')
                        plt.grid(axis='y', linestyle='--', alpha=0.7)
                        plt.tight_layout()

                        # Save the figure
                        plt.savefig('temp/co2_by_category.png')
                        plt.close()

                        # Display a message with the file path
                        console.print(Panel(
                            f"Visualization saved to [bold cyan]'temp/co2_by_category.png'[/bold cyan]\n"
                            f"You can view this file to see your CO2 savings by category.",
                            title="Visualization Created",
                            border_style="green"
                        ))
            else:
                # Fallback to non-Rich display
                print("\nGenerating impact visualizations...")

                # Extract data for visualizations
                categories = {}
                for challenge in completed_challenges:
                    category = challenge.get('category', 'Other')
                    if category not in categories:
                        categories[category] = {
                            'count': 0,
                            'co2': 0,
                            'points': 0
                        }
                    categories[category]['count'] += 1
                    categories[category]['co2'] += challenge['co2_impact']
                    categories[category]['points'] += challenge['points']

                # Create a temporary directory for visualizations if it doesn't exist
                if not os.path.exists('temp'):
                    os.makedirs('temp')

                # Create impact by category chart
                if categories:
                    plt.figure(figsize=(10, 6))

                    # Extract data
                    cat_names = list(categories.keys())
                    co2_values = [categories[cat]['co2'] for cat in cat_names]

                    # Create bar chart
                    plt.bar(cat_names, co2_values, color='green')
                    plt.title('CO2 Savings by Challenge Category')
                    plt.xlabel('Category')
                    plt.ylabel('CO2 Saved (kg)')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()

                    # Save the figure
                    plt.savefig('temp/co2_by_category.png')
                    plt.close()

                    print("\nVisualization saved to 'temp/co2_by_category.png'")

                # If there's time data, create a progress over time chart
                if len(completed_challenges) > 1:
                    # Sort challenges by completion date
                    time_sorted = sorted(
                        [c for c in completed_challenges if 'completion_date' in c],
                        key=lambda x: x['completion_date']
                    )

                    if time_sorted:
                        if HAS_RICH:
                            with console.status("[bold blue]Creating time series visualization...[/bold blue]"):
                                dates = [c['completion_date'] for c in time_sorted]
                                cumulative_co2 = np.cumsum([c['co2_impact'] for c in time_sorted])

                                plt.figure(figsize=(10, 6))
                                plt.style.use('ggplot')  # Use a more modern style

                                # Create a more visually appealing line plot
                                line, = plt.plot(dates, cumulative_co2, marker='o', linestyle='-',
                                               linewidth=3, markersize=8, color='#2ca02c')

                                # Add area under the curve with transparency
                                plt.fill_between(dates, cumulative_co2, alpha=0.3, color='#2ca02c')

                                # Add data labels for the last point
                                plt.annotate(f'{cumulative_co2[-1]:.1f} kg',
                                           xy=(dates[-1], cumulative_co2[-1]),
                                           xytext=(10, 10), textcoords='offset points',
                                           fontweight='bold', color='#2ca02c',
                                           bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", alpha=0.8))

                                plt.title('Cumulative CO2 Savings Over Time', fontsize=14, fontweight='bold')
                                plt.xlabel('Date', fontsize=12)
                                plt.ylabel('Cumulative CO2 Saved (kg)', fontsize=12)
                                plt.xticks(rotation=45, ha='right')
                                plt.grid(True, linestyle='--', alpha=0.7)
                                plt.tight_layout()

                                # Save the figure
                                plt.savefig('temp/co2_over_time.png')
                                plt.close()

                                # Display a message with the file path
                                console.print(Panel(
                                    f"Time series visualization saved to [bold cyan]'temp/co2_over_time.png'[/bold cyan]\n"
                                    f"This chart shows your cumulative CO2 savings progress over time.",
                                    title="Time Series Visualization",
                                    border_style="blue"
                                ))
                        else:
                            # Fallback to non-Rich display
                            dates = [c['completion_date'] for c in time_sorted]
                            cumulative_co2 = np.cumsum([c['co2_impact'] for c in time_sorted])

                            plt.figure(figsize=(10, 6))
                            plt.plot(dates, cumulative_co2, marker='o', linestyle='-', color='green')
                            plt.title('Cumulative CO2 Savings Over Time')
                            plt.xlabel('Date')
                            plt.ylabel('Cumulative CO2 Saved (kg)')
                            plt.xticks(rotation=45, ha='right')
                            plt.grid(True, linestyle='--', alpha=0.7)
                            plt.tight_layout()

                            # Save the figure
                            plt.savefig('temp/co2_over_time.png')
                            plt.close()

                            print("Visualization saved to 'temp/co2_over_time.png'")

        print("\nContinue participating in challenges to increase your positive environmental impact!")
        input("\nPress Enter to continue...")

    def view_community_leaderboard(self) -> None:
        """View the community leaderboard."""
        # ascii_art is already imported at the top of the file

        ascii_art.clear_screen()

        # Get all users with their points
        users_with_points = []
        for username, data in self.user_challenges.items():
            points = data.get("points", 0)
            completed = len(data.get("completed", []))
            active = len(data.get("active", []))

            # Get user display name if available
            display_name = username
            if self.user_manager:
                try:
                    user_data = self.user_manager.get_user_data(username)
                    if user_data and 'name' in user_data:
                        display_name = user_data['name']
                except:
                    pass

            users_with_points.append((username, display_name, points, completed, active))

        # Sort by points (descending)
        users_with_points.sort(key=lambda x: x[2], reverse=True)

        if HAS_RICH:
            # Display header with Rich panel
            console.print(Panel.fit(
                Text("Community Leaderboard", style="bold cyan"),
                border_style="cyan"
            ))

            if not users_with_points:
                console.print(Panel(
                    "No data available for the leaderboard yet.",
                    title="Empty Leaderboard",
                    border_style="yellow"
                ))
            else:
                # Create a Rich table for the leaderboard
                leaderboard_table = Table(
                    title="Top Eco-Challenge Participants",
                    box=rich.box.ROUNDED,
                    border_style="blue",
                    header_style="bold cyan"
                )

                # Add columns
                leaderboard_table.add_column("Rank", style="dim", justify="center")
                leaderboard_table.add_column("User", style="green")
                leaderboard_table.add_column("Eco-Points", style="yellow bold", justify="right")
                leaderboard_table.add_column("Completed", justify="center")
                leaderboard_table.add_column("Active", justify="center")

                # Add rows with medal emojis for top 3
                for i, (username, display_name, points, completed, active) in enumerate(users_with_points):
                    # Add medal emojis for top 3
                    if i == 0:
                        rank_display = "🥇 1"
                        style = "gold1"
                    elif i == 1:
                        rank_display = "🥈 2"
                        style = "grey70"
                    elif i == 2:
                        rank_display = "🥉 3"
                        style = "brown"
                    else:
                        rank_display = str(i + 1)
                        style = None

                    # Highlight current user
                    current_user = False
                    if self.user_manager:
                        current_user_data = self.user_manager.get_current_user()
                        if current_user_data and current_user_data.get('username') == username:
                            current_user = True

                    # Add the row with appropriate styling
                    if current_user:
                        leaderboard_table.add_row(
                            f"[bold cyan]{rank_display}[/bold cyan]",
                            f"[bold cyan]{display_name} (You)[/bold cyan]",
                            f"[bold cyan]{points}[/bold cyan]",
                            f"[bold cyan]{completed}[/bold cyan]",
                            f"[bold cyan]{active}[/bold cyan]"
                        )
                    elif style:
                        leaderboard_table.add_row(
                            f"[{style}]{rank_display}[/{style}]",
                            display_name,
                            str(points),
                            str(completed),
                            str(active)
                        )
                    else:
                        leaderboard_table.add_row(
                            rank_display,
                            display_name,
                            str(points),
                            str(completed),
                            str(active)
                        )

                # Display the table
                console.print(leaderboard_table)

                # Find and display current user's position
                if self.user_manager:
                    current_user = self.user_manager.get_current_user()
                    if current_user:
                        current_username = current_user.get('username')
                        for i, (username, _, _, _, _) in enumerate(users_with_points):
                            if username == current_username:
                                console.print(f"\nYour current rank: [bold cyan]{i + 1}[/bold cyan] of {len(users_with_points)}")
                                break

                # Display motivational message
                console.print(Panel(
                    "Keep completing challenges to climb the leaderboard and increase your environmental impact!",
                    border_style="green"
                ))
        else:
            # Fallback to non-Rich display
            from tabulate import tabulate
            ascii_art.display_section_header("Community Leaderboard")

            if not users_with_points:
                print("\nNo data available for the leaderboard yet.")
            else:
                print("\nTop Eco-Challenge Participants:")

                headers = ["Rank", "User", "Eco-Points", "Challenges Completed", "Active Challenges"]
                rows = []

                for i, (username, display_name, points, completed, active) in enumerate(users_with_points):
                    rows.append([
                        i + 1,
                        display_name,
                        points,
                        completed,
                        active
                    ])

                print(tabulate(rows, headers=headers, tablefmt="grid"))

                # Find current user's position
                if self.user_manager:
                    current_user = self.user_manager.get_current_user()
                    if current_user:
                        current_username = current_user.get('username')
                        for i, (username, _, _, _, _) in enumerate(users_with_points):
                            if username == current_username:
                                print(f"\nYour current rank: {i + 1} of {len(users_with_points)}")
                                break

                print("\nKeep completing challenges to climb the leaderboard!")

        input("\nPress Enter to continue...")


def run_eco_challenges(user_manager_instance=None, sheets_manager_instance=None):
    """
    Run the eco challenges as a standalone module.

    Args:
        user_manager_instance: Optional user manager instance
        sheets_manager_instance: Optional sheets manager instance
    """
    eco_challenges = EcoChallenges(user_manager_instance, sheets_manager_instance)
    eco_challenges.run_eco_challenges()


if __name__ == "__main__":
    run_eco_challenges()
