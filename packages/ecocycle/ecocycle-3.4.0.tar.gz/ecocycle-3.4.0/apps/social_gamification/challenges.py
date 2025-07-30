"""
EcoCycle - Challenges Module
Manages cycling challenges, progress tracking, and rewards.
"""
import logging
import datetime
from typing import Dict, List, Optional, Any

from apps.social_gamification.base import (
    SocialFeatureBase, RICH_AVAILABLE, console, 
    COLOR_CHALLENGE, CHALLENGES_FILE
)

# Rich UI imports
if RICH_AVAILABLE:
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import BarColumn
    from rich.prompt import Prompt
    from rich import box

import utils.ascii_art as ascii_art
import utils.general_utils as general_utils

logger = logging.getLogger(__name__)

# Define challenges
CHALLENGES = [
    {
        "id": "week_challenge_1",
        "name": "Weekly Distance Challenge",
        "description": "Cycle at least 20km this week",
        "requirement": {"weekly_distance": 20},
        "points": 30,
        "duration": 7,  # days
        "icon": "🚲"
    },
    {
        "id": "week_challenge_2",
        "name": "Weekly CO2 Challenge",
        "description": "Save at least 2kg of CO2 this week",
        "requirement": {"weekly_co2_saved": 2},
        "points": 25,
        "duration": 7,  # days
        "icon": "🌍"
    },
    {
        "id": "week_challenge_3",
        "name": "Weekly Trips Challenge",
        "description": "Complete at least 3 cycling trips this week",
        "requirement": {"weekly_trips": 3},
        "points": 20,
        "duration": 7,  # days
        "icon": "🏆"
    },
    {
        "id": "month_challenge_1",
        "name": "Monthly Cycling Streak",
        "description": "Cycle at least 15 times this month",
        "requirement": {"monthly_trips": 15},
        "points": 100,
        "duration": 30,  # days
        "icon": "📅"
    }
]


class ChallengeManager(SocialFeatureBase):
    """Manages cycling challenges, progress tracking, and rewards."""
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the challenge manager.
        
        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        super().__init__(user_manager, sheets_manager)
        self.challenges = self._load_challenges()
    
    def _load_challenges(self):
        """Load challenges from file or use defaults."""
        challenges = self._load_json_file(CHALLENGES_FILE)
        if not challenges:
            challenges = CHALLENGES
            # Don't call _save_challenges() here to avoid circular dependency
            self._save_json_file(CHALLENGES_FILE, CHALLENGES)
        return challenges
    
    def _save_challenges(self):
        """Save challenges to file."""
        return self._save_json_file(CHALLENGES_FILE, self.challenges)
    
    def _calculate_challenge_progress(self, username: str, challenge: Dict) -> float:
        """
        Calculate progress towards a challenge.
        
        Args:
            username: Username to check
            challenge: Challenge to check progress for
            
        Returns:
            Progress percentage (0-100)
        """
        if not self.user_manager:
            return 0
            
        # Ensure we're working with the current user
        current_user = self.user_manager.get_current_user()
        # Only proceed if requested username matches current user
        if current_user.get('username') != username:
            logger.warning(f"Username mismatch: {username} vs {current_user.get('username')}")
            return 0
            
        # Use the current user data
        user = current_user
        if not user:
            return 0
        
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        requirement = challenge.get('requirement', {})
        challenge_id = challenge.get('id')
        
        # Get challenge start date
        start_date_str = user.get('challenge_dates', {}).get(challenge_id)
        if not start_date_str:
            return 0
        
        try:
            start_date = datetime.datetime.fromisoformat(start_date_str)
            duration_days = challenge.get('duration', 7)
            end_date = start_date + datetime.timedelta(days=duration_days)
            
            # Filter trips within challenge period
            challenge_trips = []
            for trip in trips:
                trip_date_str = trip.get('date')
                if not trip_date_str:
                    continue
                
                try:
                    trip_date = datetime.datetime.fromisoformat(trip_date_str)
                    if start_date <= trip_date <= end_date:
                        challenge_trips.append(trip)
                except ValueError:
                    continue
            
            # Calculate progress based on requirement type
            for req_key, req_value in requirement.items():
                if req_key == 'weekly_distance':
                    # Calculate total distance in challenge period
                    total_distance = sum(trip.get('distance', 0) for trip in challenge_trips)
                    return min(100, (total_distance / req_value) * 100)
                
                elif req_key == 'weekly_co2_saved':
                    # Calculate total CO2 saved in challenge period
                    total_co2 = sum(trip.get('co2_saved', 0) for trip in challenge_trips)
                    return min(100, (total_co2 / req_value) * 100)
                
                elif req_key == 'weekly_trips':
                    # Count trips in challenge period
                    trip_count = len(challenge_trips)
                    return min(100, (trip_count / req_value) * 100)
                
                elif req_key == 'monthly_trips':
                    # Count trips in challenge period
                    trip_count = len(challenge_trips)
                    return min(100, (trip_count / req_value) * 100)
            
            return 0
        
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating challenge progress: {e}")
            return 0
    
    def view_challenges(self):
        """View and manage active challenges with Rich UI styling."""
        user = self.user_manager.get_current_user()
        username = user.get('username')
        
        # Get active and completed challenges
        active_challenges = user.get('active_challenges', [])
        completed_challenges = user.get('completed_challenges', [])
        
        # Find available challenges (not active or completed)
        available_challenges = []
        for challenge in self.challenges:
            challenge_id = challenge.get('id')
            if challenge_id not in active_challenges and challenge_id not in completed_challenges:
                available_challenges.append(challenge)
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Take on cycling challenges to earn eco points and track your progress",
                title=f"[bold {COLOR_CHALLENGE}]Cycling Challenges[/bold {COLOR_CHALLENGE}]",
                border_style=COLOR_CHALLENGE,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Display active challenges
            if active_challenges:
                active_table = Table(
                    title=f"[bold {COLOR_CHALLENGE}]Active Challenges[/bold {COLOR_CHALLENGE}]", 
                    box=box.SIMPLE, 
                    show_header=True,
                    header_style=f"bold {COLOR_CHALLENGE}"
                )
                
                active_table.add_column("Challenge", style="cyan")
                active_table.add_column("Description", style="white")
                active_table.add_column("Progress", style="green")
                active_table.add_column("Time Remaining", style="yellow")
                active_table.add_column("Points", style="gold1")
                
                for challenge_id in active_challenges:
                    # Find challenge details
                    challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
                    if not challenge:
                        continue
                    
                    name = challenge.get('name')
                    description = challenge.get('description')
                    points = challenge.get('points', 0)
                    icon = challenge.get('icon', '🏆')
                    
                    # Get start date and calculate end date
                    started_at = user.get('challenge_dates', {}).get(challenge_id, '')
                    date_str = "Date unknown"
                    
                    if started_at:
                        try:
                            started_date = datetime.datetime.fromisoformat(started_at)
                            duration_days = challenge.get('duration', 7)
                            end_date = started_date + datetime.timedelta(days=duration_days)
                            days_left = (end_date - datetime.datetime.now()).days + 1
                            
                            if days_left > 0:
                                date_str = f"{days_left} days left"
                            else:
                                date_str = "Ends today"
                        except ValueError:
                            pass
                    
                    # Calculate progress
                    progress = self._calculate_challenge_progress(username, challenge)
                    progress_int = int(progress)
                    
                    progress_bar = f"[{'#' * (progress_int // 5)}{' ' * (20 - (progress_int // 5))}] {progress_int}%"
                    
                    active_table.add_row(
                        f"{icon} {name}",
                        description,
                        progress_bar,
                        date_str,
                        f"+{points}"
                    )
                
                console.print(active_table)
                console.print()
            else:
                console.print(Panel(
                    "You have no active challenges. Join one below!",
                    title=f"[bold {COLOR_CHALLENGE}]Active Challenges[/bold {COLOR_CHALLENGE}]",
                    border_style=COLOR_CHALLENGE,
                    box=box.SIMPLE
                ))
                console.print()
            
            # Display completed challenges
            if completed_challenges:
                completed_table = Table(
                    title="[bold green]Completed Challenges[/bold green]", 
                    box=box.SIMPLE, 
                    show_header=True,
                    header_style="bold green"
                )
                
                completed_table.add_column("Challenge", style="cyan")
                completed_table.add_column("Description", style="white")
                completed_table.add_column("Completed On", style="green")
                completed_table.add_column("Points", style="gold1")
                
                for challenge_id in completed_challenges:
                    # Find challenge details
                    challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
                    if not challenge:
                        continue
                    
                    name = challenge.get('name')
                    description = challenge.get('description')
                    points = challenge.get('points', 0)
                    icon = challenge.get('icon', '🏆')
                    
                    # Get completion date
                    completed_at = user.get('challenge_completion_dates', {}).get(challenge_id, '')
                    if completed_at:
                        try:
                            completed_date = datetime.datetime.fromisoformat(completed_at)
                            date_str = completed_date.strftime("%Y-%m-%d")
                        except ValueError:
                            date_str = "Date unknown"
                    else:
                        date_str = "Date unknown"
                    
                    completed_table.add_row(
                        f"{icon} {name}",
                        description,
                        date_str,
                        f"+{points}"
                    )
                
                console.print(completed_table)
                console.print()
            
            # Available challenges to join
            if available_challenges:
                available_table = Table(
                    title="[bold yellow]Available Challenges[/bold yellow]", 
                    box=box.SIMPLE, 
                    show_header=True,
                    header_style="bold yellow"
                )
                
                available_table.add_column("#", style="dim", width=3)
                available_table.add_column("Challenge", style="cyan")
                available_table.add_column("Description", style="white")
                available_table.add_column("Duration", style="blue")
                available_table.add_column("Points", style="gold1")
                
                for i, challenge in enumerate(available_challenges, 1):
                    name = challenge.get('name')
                    description = challenge.get('description')
                    points = challenge.get('points', 0)
                    icon = challenge.get('icon', '🏆')
                    duration = challenge.get('duration', 7)
                    
                    available_table.add_row(
                        str(i),
                        f"{icon} {name}",
                        description,
                        f"{duration} days",
                        f"+{points}"
                    )
                
                console.print(available_table)
            else:
                console.print(Panel(
                    "No available challenges at the moment. Check back later!",
                    title="[bold yellow]Available Challenges[/bold yellow]",
                    border_style="yellow",
                    box=box.SIMPLE
                ))
            
            # Challenge options
            console.print("\n[bold]Options:[/bold]")
            options = []
            
            if available_challenges:
                console.print("1. Join a Challenge")
                options.append("1")
            if active_challenges:
                console.print("2. Abandon an Active Challenge")
                options.append("2")
            options.append("3")
            console.print("3. Return to Social Hub")
            
            choice = Prompt.ask("Select an option", choices=options)
            
        else:
            # Fallback for non-Rich environments
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Challenges")
            
            # Display active challenges
            if active_challenges:
                print(f"{ascii_art.Fore.CYAN}{ascii_art.Style.BRIGHT}Active Challenges:{ascii_art.Style.RESET_ALL}")
                
                for challenge_id in active_challenges:
                    # Find challenge details
                    challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
                    if not challenge:
                        continue
                    
                    name = challenge.get('name')
                    description = challenge.get('description')
                    points = challenge.get('points', 0)
                    icon = challenge.get('icon', '🏆')
                    requirement = challenge.get('requirement', {})
                    
                    # Get start date and calculate end date
                    started_at = user.get('challenge_dates', {}).get(challenge_id, '')
                    if started_at:
                        try:
                            started_date = datetime.datetime.fromisoformat(started_at)
                            duration_days = challenge.get('duration', 7)
                            end_date = started_date + datetime.timedelta(days=duration_days)
                            days_left = (end_date - datetime.datetime.now()).days + 1
                            
                            if days_left > 0:
                                date_str = f"{days_left} days left"
                            else:
                                date_str = "Ends today"
                        except ValueError:
                            date_str = "Date unknown"
                    else:
                        date_str = "Date unknown"
                    
                    # Calculate progress
                    progress = self._calculate_challenge_progress(username, challenge)
                    
                    print(f"{icon} {name} - {description} (+{points} points)")
                    print(f"   Progress: {progress}% - {date_str}")
            else:
                print("No active challenges.")
            
            # Display completed challenges
            if completed_challenges:
                print(f"\n{ascii_art.Fore.GREEN}{ascii_art.Style.BRIGHT}Completed Challenges:{ascii_art.Style.RESET_ALL}")
                
                for challenge_id in completed_challenges:
                    # Find challenge details
                    challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
                    if not challenge:
                        continue
                    
                    name = challenge.get('name')
                    description = challenge.get('description')
                    points = challenge.get('points', 0)
                    icon = challenge.get('icon', '🏆')
                    
                    # Get completion date
                    completed_at = user.get('challenge_completion_dates', {}).get(challenge_id, '')
                    if completed_at:
                        try:
                            completed_date = datetime.datetime.fromisoformat(completed_at)
                            date_str = completed_date.strftime("%Y-%m-%d")
                        except ValueError:
                            date_str = "Date unknown"
                    else:
                        date_str = "Date unknown"
                    
                    print(f"{icon} {name} - {description} (+{points} points)")
                    print(f"   Completed on: {date_str}")
            
            # Available challenges to join
            print(f"\n{ascii_art.Fore.YELLOW}{ascii_art.Style.BRIGHT}Available Challenges:{ascii_art.Style.RESET_ALL}")
            
            if available_challenges:
                for i, challenge in enumerate(available_challenges, 1):
                    name = challenge.get('name')
                    description = challenge.get('description')
                    points = challenge.get('points', 0)
                    icon = challenge.get('icon', '🏆')
                    duration = challenge.get('duration', 7)
                    
                    print(f"{i}. {icon} {name} - {description} (+{points} points)")
                    print(f"   Duration: {duration} days")
            else:
                print("No available challenges at the moment. Check back later!")
            
            # Challenge options
            print("\nOptions:")
            options = []
            if available_challenges:
                print("1. Join a Challenge")
                options.append("1")
            if active_challenges:
                print("2. Abandon an Active Challenge")
                options.append("2")
            print("3. Return to Social Hub")
            options.append("3")
            
            choice = input("\nSelect an option (1-3): ")
        
        # Handle user choice
        if choice == "1" and available_challenges:
            # Join a challenge
            if RICH_AVAILABLE:
                challenge_num = Prompt.ask(f"Enter challenge number to join", choices=[str(i) for i in range(1, len(available_challenges) + 1)])
            else:
                challenge_num = input(f"Enter challenge number to join (1-{len(available_challenges)}): ")
            
            try:
                idx = int(challenge_num) - 1
                if 0 <= idx < len(available_challenges):
                    challenge = available_challenges[idx]
                    challenge_id = challenge.get('id')
                    
                    # Add to active challenges
                    if 'active_challenges' not in user:
                        user['active_challenges'] = []
                    user['active_challenges'].append(challenge_id)
                    
                    # Record start date
                    if 'challenge_dates' not in user:
                        user['challenge_dates'] = {}
                    user['challenge_dates'][challenge_id] = datetime.datetime.now().isoformat()
                    
                    # Save user data
                    if self.user_manager.save_users():
                        if RICH_AVAILABLE:
                            console.print(f"[bold green]You've joined the '{challenge.get('name')}' challenge![/bold green]")
                        else:
                            print(f"You've joined the '{challenge.get('name')}' challenge!")
                    else:
                        if RICH_AVAILABLE:
                            console.print(f"[bold red]Error saving challenge data.[/bold red]")
                        else:
                            print("Error saving challenge data.")
                else:
                    if RICH_AVAILABLE:
                        console.print(f"[bold red]Invalid challenge number.[/bold red]")
                    else:
                        print("Invalid challenge number.")
            except ValueError:
                if RICH_AVAILABLE:
                    console.print(f"[bold red]Invalid input. Please enter a number.[/bold red]")
                else:
                    print("Invalid input. Please enter a number.")
        
        elif choice == "2" and active_challenges:
            # Abandon a challenge
            if RICH_AVAILABLE:
                console.print("\n[bold]Active Challenges:[/bold]")
                active_list = {}
                for i, challenge_id in enumerate(active_challenges, 1):
                    challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
                    if challenge:
                        console.print(f"{i}. {challenge.get('name')}")
                        active_list[str(i)] = challenge_id
                
                challenge_num = Prompt.ask(f"Enter challenge number to abandon", choices=list(active_list.keys()))
                challenge_id = active_list[challenge_num]
                challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
            else:
                print("\nActive Challenges:")
                for i, challenge_id in enumerate(active_challenges, 1):
                    challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
                    if challenge:
                        print(f"{i}. {challenge.get('name')}")
                
                challenge_num = input(f"Enter challenge number to abandon (1-{len(active_challenges)}): ")
                try:
                    idx = int(challenge_num) - 1
                    if 0 <= idx < len(active_challenges):
                        challenge_id = active_challenges[idx]
                        challenge = next((c for c in self.challenges if c.get('id') == challenge_id), None)
                    else:
                        if RICH_AVAILABLE:
                            console.print(f"[bold red]Invalid challenge number.[/bold red]")
                        else:
                            print("Invalid challenge number.")
                        return
                except (ValueError, IndexError):
                    if RICH_AVAILABLE:
                        console.print(f"[bold red]Invalid input. Please enter a number.[/bold red]")
                    else:
                        print("Invalid input. Please enter a number.")
                    return
            
            # Remove from active challenges
            if challenge:
                user['active_challenges'].remove(challenge_id)
                
                # Remove from challenge dates
                if 'challenge_dates' in user and challenge_id in user['challenge_dates']:
                    del user['challenge_dates'][challenge_id]
                
                # Save user data
                if self.user_manager.save_users():
                    if RICH_AVAILABLE:
                        console.print(f"[bold yellow]You've abandoned the '{challenge.get('name')}' challenge.[/bold yellow]")
                    else:
                        print(f"You've abandoned the '{challenge.get('name')}' challenge.")
                else:
                    if RICH_AVAILABLE:
                        console.print(f"[bold red]Error saving challenge data.[/bold red]")
                    else:
                        print("Error saving challenge data.")
        
        if RICH_AVAILABLE:
            console.print("\nPress Enter to continue...", style="dim")
            input()
        else:
            input("\nPress Enter to continue...")
