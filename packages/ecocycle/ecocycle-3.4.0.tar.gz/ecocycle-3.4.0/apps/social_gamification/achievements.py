"""
EcoCycle - Achievements Module
Handles user achievements, progress tracking, and rewards.
"""
import logging
import os
from typing import Dict, List, Optional, Any

from apps.social_gamification.base import (
    SocialFeatureBase, RICH_AVAILABLE, console, 
    COLOR_ACHIEVEMENT, ACHIEVEMENTS_FILE
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

# Define achievements
ACHIEVEMENTS = [
    {
        "id": "first_ride",
        "name": "First Pedal",
        "description": "Complete your first cycling trip",
        "requirement": {"total_trips": 1},
        "points": 10,
        "icon": "🚲"
    },
    {
        "id": "eco_warrior",
        "name": "Eco Warrior",
        "description": "Save 10kg of CO2 through cycling",
        "requirement": {"total_co2_saved": 10},
        "points": 25,
        "icon": "🌿"
    },
    {
        "id": "distance_10",
        "name": "Road Explorer",
        "description": "Cycle a total of 10km",
        "requirement": {"total_distance": 10},
        "points": 15,
        "icon": "🗺️"
    },
    {
        "id": "distance_50",
        "name": "Distance Champion",
        "description": "Cycle a total of 50km",
        "requirement": {"total_distance": 50},
        "points": 30,
        "icon": "🏆"
    },
    {
        "id": "distance_100",
        "name": "Century Rider",
        "description": "Cycle a total of 100km",
        "requirement": {"total_distance": 100},
        "points": 50,
        "icon": "💯"
    },
    {
        "id": "calories_1000",
        "name": "Calorie Burner",
        "description": "Burn 1000 calories through cycling",
        "requirement": {"total_calories": 1000},
        "points": 20,
        "icon": "🔥"
    },
    {
        "id": "co2_saved_50",
        "name": "Climate Guardian",
        "description": "Save 50kg of CO2 through cycling",
        "requirement": {"total_co2_saved": 50},
        "points": 40,
        "icon": "🌍"
    },
    {
        "id": "co2_saved_100",
        "name": "Carbon Crusher",
        "description": "Save 100kg of CO2 through cycling",
        "requirement": {"total_co2_saved": 100},
        "points": 75,
        "icon": "♻️"
    },
    {
        "id": "trips_10",
        "name": "Regular Rider",
        "description": "Complete 10 cycling trips",
        "requirement": {"total_trips": 10},
        "points": 25,
        "icon": "🚴"
    },
    {
        "id": "trips_50",
        "name": "Devoted Cyclist",
        "description": "Complete 50 cycling trips",
        "requirement": {"total_trips": 50},
        "points": 100,
        "icon": "👑"
    }
]


class AchievementManager(SocialFeatureBase):
    """Manages user achievements, progress tracking, and rewards."""
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the achievement manager.
        
        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        super().__init__(user_manager, sheets_manager)
        self.achievements = self._load_achievements()
    
    def _load_achievements(self):
        """Load achievements from file or use defaults."""
        achievements = self._load_json_file(ACHIEVEMENTS_FILE)
        if not achievements:
            achievements = ACHIEVEMENTS
            # Don't call _save_achievements() here to avoid circular dependency
            self._save_json_file(ACHIEVEMENTS_FILE, ACHIEVEMENTS)
        return achievements
    
    def _save_achievements(self):
        """Save achievements to file."""
        return self._save_json_file(ACHIEVEMENTS_FILE, self.achievements)
    
    def check_achievement_progress(self, username: str) -> Dict[str, Any]:
        """
        Check user's progress towards achievements.
        
        Args:
            username: Username to check
            
        Returns:
            Dictionary with achievement progress information
        """
        if not self.user_manager:
            logger.warning("User manager not initialized")
            return {}
            
        # Ensure we're working with the current user
        current_user = self.user_manager.get_current_user()
        # Only proceed if requested username matches current user
        if current_user.get('username') != username:
            logger.warning(f"Username mismatch: {username} vs {current_user.get('username')}")
            return {}
            
        # Use the current user data
        user = current_user
        if not user:
            logger.warning(f"User {username} not found")
            return {}
        
        # Get user stats
        stats = user.get('stats', {})
        total_distance = stats.get('total_distance', 0.0)
        total_trips = stats.get('total_trips', 0)
        total_calories = stats.get('total_calories', 0)
        total_co2_saved = stats.get('total_co2_saved', 0.0)
        
        # Get completed achievements
        completed_achievements = user.get('completed_achievements', [])
        
        # Check achievement progress
        achievements_progress = {}
        for achievement in self.achievements:
            achievement_id = achievement.get('id')
            
            # Skip already completed achievements
            if achievement_id in completed_achievements:
                achievements_progress[achievement_id] = 100
                continue
            
            # Check requirement progress
            requirement = achievement.get('requirement', {})
            progress = 0
            
            for req_key, req_value in requirement.items():
                if req_key == 'total_distance':
                    progress = min(100, (total_distance / req_value) * 100)
                elif req_key == 'total_trips':
                    progress = min(100, (total_trips / req_value) * 100)
                elif req_key == 'total_calories':
                    progress = min(100, (total_calories / req_value) * 100)
                elif req_key == 'total_co2_saved':
                    progress = min(100, (total_co2_saved / req_value) * 100)
            
            achievements_progress[achievement_id] = progress
        
        return achievements_progress
    
    def update_achievements(self, username: str) -> List[Dict]:
        """
        Check and update user achievements based on their stats.
        
        Args:
            username: Username to update achievements for
            
        Returns:
            List of newly completed achievements
        """
        if not self.user_manager:
            logger.warning("User manager not initialized")
            return []
            
        # Ensure we're working with the current user
        current_user = self.user_manager.get_current_user()
        # Only proceed if requested username matches current user
        if current_user.get('username') != username:
            logger.warning(f"Username mismatch: {username} vs {current_user.get('username')}")
            return []
            
        # Use the current user data
        user = current_user
        if not user:
            logger.warning(f"User {username} not found")
            return []
        
        # Get user stats
        stats = user.get('stats', {})
        total_distance = stats.get('total_distance', 0.0)
        total_trips = stats.get('total_trips', 0)
        total_calories = stats.get('total_calories', 0)
        total_co2_saved = stats.get('total_co2_saved', 0.0)
        
        # Get completed achievements
        completed_achievements = user.get('completed_achievements', [])
        if not completed_achievements:
            user['completed_achievements'] = []
            completed_achievements = []
        
        # Check for new achievements
        new_achievements = []
        
        for achievement in self.achievements:
            achievement_id = achievement.get('id')
            
            # Skip already completed achievements
            if achievement_id in completed_achievements:
                continue
            
            # Check if achievement requirements are met
            requirement = achievement.get('requirement', {})
            achievement_completed = True
            
            for req_key, req_value in requirement.items():
                if req_key == 'total_distance' and total_distance < req_value:
                    achievement_completed = False
                elif req_key == 'total_trips' and total_trips < req_value:
                    achievement_completed = False
                elif req_key == 'total_calories' and total_calories < req_value:
                    achievement_completed = False
                elif req_key == 'total_co2_saved' and total_co2_saved < req_value:
                    achievement_completed = False
            
            if achievement_completed:
                # Add to completed achievements
                user['completed_achievements'].append(achievement_id)
                
                # Add achievement points
                points = achievement.get('points', 0)
                user['eco_points'] = user.get('eco_points', 0) + points
                
                # Add to new achievements list
                new_achievements.append(achievement)
        
        # Save user data if there are new achievements
        if new_achievements and self.user_manager:
            self.user_manager.save_users()
        
        return new_achievements
    
    def view_achievements(self):
        """View user achievements and progress with Rich UI styling."""
        user = self.user_manager.get_current_user()
        username = user.get('username')
        
        # Update achievements
        new_achievements = self.update_achievements(username)
        
        # Get user stats
        stats = user.get('stats', {})
        total_distance = stats.get('total_distance', 0.0)
        total_trips = stats.get('total_trips', 0)
        total_calories = stats.get('total_calories', 0)
        total_co2_saved = stats.get('total_co2_saved', 0.0)
        
        # Get completed achievements
        completed_achievements = user.get('completed_achievements', [])
        eco_points = user.get('eco_points', 0)
        
        # Calculate level
        current_level, points_needed = self._calculate_level(eco_points)
        
        # Check progress for incomplete achievements
        progress_data = self.check_achievement_progress(username)
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                f"[bold]User: [/bold][cyan]{user.get('name', username)}[/cyan] | [bold]Eco Points: [/bold][{COLOR_ACHIEVEMENT}]{eco_points}[/{COLOR_ACHIEVEMENT}] | [bold]Level: [/bold][green]{current_level}[/green]",
                title=f"[bold {COLOR_ACHIEVEMENT}]Your Achievements[/bold {COLOR_ACHIEVEMENT}]",
                border_style=COLOR_ACHIEVEMENT,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Show any new achievements
            if new_achievements:
                new_table = Table(
                    title="[bold blue]New Achievements[/bold blue]",
                    box=box.ROUNDED,
                    border_style="gold1",
                    title_justify="center",
                    padding=(0, 1)
                )
                
                new_table.add_column("Achievement", style="cyan")
                new_table.add_column("Description", style="white")
                new_table.add_column("Points", style="gold1")
                
                for achievement in new_achievements:
                    new_table.add_row(
                        f"{achievement.get('icon', '🏆')} {achievement.get('name')}",
                        achievement.get('description', ''),
                        f"+{achievement.get('points', 0)}"
                    )
                
                console.print(new_table)
                console.print()
            
            # Create achievement tables
            completed_table = Table(
                title="[bold gold1]Completed Achievements[/bold gold1]",
                box=box.SIMPLE,
                show_header=True
            )
            
            completed_table.add_column("Achievement", style="cyan")
            completed_table.add_column("Description", style="white")
            completed_table.add_column("Points", style="gold1")
            
            progress_table = Table(
                title="[bold green]Achievements In Progress[/bold green]",
                box=box.SIMPLE
            )
            
            progress_table.add_column("Achievement", style="cyan")
            progress_table.add_column("Description", style="white")
            progress_table.add_column("Points", style="gold1")
            progress_table.add_column("Progress", style="green")
            
            # Populate tables
            has_completed = False
            has_in_progress = False
            
            for achievement in self.achievements:
                achievement_id = achievement.get('id')
                name = achievement.get('name')
                description = achievement.get('description')
                points = achievement.get('points', 0)
                icon = achievement.get('icon', '🏆')
                
                if achievement_id in completed_achievements:
                    has_completed = True
                    completed_table.add_row(
                        f"{icon} {name}",
                        description,
                        f"+{points}"
                    )
                else:
                    has_in_progress = True
                    progress = progress_data.get(achievement_id, 0)
                    progress_int = int(progress)
                    
                    progress_bar = f"[{'#' * (progress_int // 5)}{' ' * (20 - (progress_int // 5))}] {progress_int}%"
                    
                    progress_table.add_row(
                        f"{icon} {name}",
                        description,
                        f"+{points}",
                        progress_bar
                    )
            
            # Display tables
            if has_completed:
                console.print(completed_table)
                console.print()
            
            if has_in_progress:
                console.print(progress_table)
            
            # Show next level information
            if points_needed > 0:
                console.print(f"\n[bold]Next Level:[/bold] {points_needed} more points needed to reach Level {current_level + 1}")
            else:
                console.print("\n[bold]Congratulations![/bold] You've reached the maximum level!")
            
            console.print("\nPress Enter to continue...", style="dim")
            input()
            
        else:
            # Fallback for non-Rich environments
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Your Achievements")
            
            print(f"User: {user.get('name', username)}")
            print(f"Eco Points: {eco_points}")
            print(f"Level: {current_level}")
            print()
            
            # Show any new achievements
            if new_achievements:
                print(f"{ascii_art.Fore.YELLOW}{ascii_art.Style.BRIGHT}New Achievements Unlocked!{ascii_art.Style.RESET_ALL}")
                for achievement in new_achievements:
                    print(f"{achievement.get('icon', '🏆')} {achievement.get('name')} - {achievement.get('description')} (+{achievement.get('points', 0)} points)")
                print()
            
            # Show completed achievements
            print(f"{ascii_art.Fore.GREEN}{ascii_art.Style.BRIGHT}Completed Achievements:{ascii_art.Style.RESET_ALL}")
            found_completed = False
            
            for achievement in self.achievements:
                achievement_id = achievement.get('id')
                if achievement_id in completed_achievements:
                    found_completed = True
                    name = achievement.get('name')
                    description = achievement.get('description')
                    points = achievement.get('points', 0)
                    icon = achievement.get('icon', '🏆')
                    
                    print(f"{icon} {name} - {description} (+{points} points)")
            
            if not found_completed:
                print("No completed achievements yet.")
            
            # Show achievements in progress
            print(f"\n{ascii_art.Fore.BLUE}{ascii_art.Style.BRIGHT}Achievements In Progress:{ascii_art.Style.RESET_ALL}")
            found_in_progress = False
            
            for achievement in self.achievements:
                achievement_id = achievement.get('id')
                if achievement_id not in completed_achievements:
                    found_in_progress = True
                    name = achievement.get('name')
                    description = achievement.get('description')
                    points = achievement.get('points', 0)
                    icon = achievement.get('icon', '🏆')
                    
                    progress = progress_data.get(achievement_id, 0)
                    progress_int = int(progress)
                    
                    # Create a simple progress bar
                    progress_bar = f"[{'#' * (progress_int // 10)}{' ' * (10 - (progress_int // 10))}] {progress_int}%"
                    
                    print(f"{icon} {name} - {description} (+{points} points)")
                    print(f"   Progress: {progress_bar}")
            
            if not found_in_progress:
                print("All achievements completed!")
            
            # Show next level information
            if points_needed > 0:
                print(f"\nNext Level: {points_needed} more points needed to reach Level {current_level + 1}")
            else:
                print("\nCongratulations! You've reached the maximum level!")
            
            input("\nPress Enter to continue...")
