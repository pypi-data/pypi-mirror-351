"""
EcoCycle - Leaderboard Module
Manages global leaderboard and user rankings.
"""
import logging
from typing import Dict, List, Optional, Any

from apps.social_gamification.base import (
    SocialFeatureBase, RICH_AVAILABLE, console, 
    COLOR_LEADERBOARD, LEADERBOARD_FILE
)

# Rich UI imports
if RICH_AVAILABLE:
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich import box
    from rich.text import Text

import utils.ascii_art as ascii_art
import utils.general_utils as general_utils

logger = logging.getLogger(__name__)


class LeaderboardManager(SocialFeatureBase):
    """Manages the global leaderboard and user rankings."""
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the leaderboard manager.
        
        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        super().__init__(user_manager, sheets_manager)
        self.leaderboard = self._load_leaderboard()
    
    def _load_leaderboard(self):
        """Load leaderboard from file."""
        leaderboard = self._load_json_file(LEADERBOARD_FILE, {})
        
        # Initialize leaderboard structure if empty
        if not leaderboard or 'users' not in leaderboard:
            leaderboard = {
                'users': {},
                'updated': '',  # ISO format date string
                'metrics': {
                    'total_distance': 0.0,
                    'total_co2_saved': 0.0,
                    'total_trips': 0,
                    'total_calories': 0
                }
            }
            # Don't call _save_leaderboard() here to avoid circular dependency
            self._save_json_file(LEADERBOARD_FILE, leaderboard)
        
        return leaderboard
    
    def _save_leaderboard(self):
        """Save leaderboard to file."""
        return self._save_json_file(LEADERBOARD_FILE, self.leaderboard)
    
    def update_leaderboard(self):
        """Update leaderboard with current user data."""
        if not self.user_manager:
            logger.warning("User manager not initialized")
            return False
        
        # Get current user data
        user = self.user_manager.get_current_user()
        if not user:
            logger.warning("No current user found")
            return False
            
        username = user.get('username')
        if not username:
            logger.warning("Username not found in user data")
            return False
        
        # Update leaderboard structure
        if 'users' not in self.leaderboard:
            self.leaderboard['users'] = {}
        
        if 'metrics' not in self.leaderboard:
            self.leaderboard['metrics'] = {
                'total_distance': 0.0,
                'total_co2_saved': 0.0,
                'total_trips': 0,
                'total_calories': 0
            }
        
        # Get user stats
        stats = user.get('stats', {})
        if not stats:
            logger.warning(f"No stats found for user {username}")
            return False
            
        # Extract user stats
        total_distance = stats.get('total_distance', 0.0)
        total_co2_saved = stats.get('total_co2_saved', 0.0)
        total_trips = stats.get('total_trips', 0)
        total_calories = stats.get('total_calories', 0)
        
        # Add or update user in leaderboard
        self.leaderboard['users'][username] = {
            'name': user.get('name', username),
            'stats': {
                'total_distance': total_distance,
                'total_co2_saved': total_co2_saved,
                'total_trips': total_trips,
                'total_calories': total_calories
            },
            'eco_points': user.get('eco_points', 0)
        }
        
        # Update metrics (we'll keep the accumulated metrics from all users over time)
        # This approach preserves the community impact data
        # We'll only update the metrics if the user has new or updated stats
        if username not in self.leaderboard.get('users', {}):
            # If this is a new user, add their stats to the metrics
            self.leaderboard['metrics']['total_distance'] += total_distance
            self.leaderboard['metrics']['total_co2_saved'] += total_co2_saved
            self.leaderboard['metrics']['total_trips'] += total_trips
            self.leaderboard['metrics']['total_calories'] += total_calories
        
        # Update timestamp
        self.leaderboard['updated'] = general_utils.get_current_date_str()
        
        # Save to file
        return self._save_leaderboard()
    
    def view_leaderboard(self):
        """View global leaderboard with Rich UI styling."""
        # Update leaderboard
        self.update_leaderboard()
        
        # Get current user
        current_user = self.user_manager.get_current_user()
        current_username = current_user.get('username')
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Compare your cycling achievements with the community", 
                title=f"[bold {COLOR_LEADERBOARD}]EcoCycle Leaderboard[/bold {COLOR_LEADERBOARD}]",
                border_style=COLOR_LEADERBOARD,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Initialize tabs for different metrics
            console.print(f"\n[bold]View Leaderboard By:[/bold]")
            console.print("1. Distance")
            console.print("2. CO2 Saved")
            console.print("3. Eco Points")
            console.print("4. Trip Count")
            console.print("5. Return to Social Hub")
            
            choice = Prompt.ask("Select a metric", choices=["1", "2", "3", "4", "5"])
            
            if choice == "5":
                return
            
            metric = ""
            title = ""
            
            if choice == "1":
                metric = "total_distance"
                title = "Distance Leaderboard"
                format_func = general_utils.format_distance
            elif choice == "2":
                metric = "total_co2_saved"
                title = "CO2 Saved Leaderboard"
                format_func = general_utils.format_co2
            elif choice == "3":
                metric = "eco_points"
                title = "Eco Points Leaderboard"
                format_func = lambda x: str(x)
            elif choice == "4":
                metric = "total_trips"
                title = "Trip Count Leaderboard"
                format_func = lambda x: str(x)
            
            # Get leaderboard data
            leaderboard_data = []
            for username, user_data in self.leaderboard['users'].items():
                if metric == "eco_points":
                    value = user_data.get(metric, 0)
                else:
                    value = user_data.get('stats', {}).get(metric, 0)
                
                leaderboard_data.append({
                    'username': username,
                    'name': user_data.get('name', username),
                    'value': value
                })
            
            # Sort by metric value (descending)
            leaderboard_data.sort(key=lambda x: x['value'], reverse=True)
            
            # Create leaderboard table
            table = Table(
                title=f"[bold {COLOR_LEADERBOARD}]{title}[/bold {COLOR_LEADERBOARD}]",
                box=box.ROUNDED,
                border_style=COLOR_LEADERBOARD,
                show_header=True,
                header_style=f"bold {COLOR_LEADERBOARD}"
            )
            
            table.add_column("Rank", style="dim", width=6)
            table.add_column("User", style="cyan")
            
            if metric == "total_distance":
                table.add_column("Distance", style="green")
            elif metric == "total_co2_saved":
                table.add_column("CO2 Saved", style="green")
            elif metric == "eco_points":
                table.add_column("Eco Points", style="gold1")
            elif metric == "total_trips":
                table.add_column("Trips", style="blue")
            
            # Add rows with user data
            for i, entry in enumerate(leaderboard_data[:10], 1):
                username = entry['username']
                name = entry['name']
                value = entry['value']
                
                # Format rank with medal for top 3
                rank_str = str(i)
                if i == 1:
                    rank_str = "🥇 1"
                elif i == 2:
                    rank_str = "🥈 2"
                elif i == 3:
                    rank_str = "🥉 3"
                
                # Highlight current user
                if username == current_username:
                    name = f"[bold white on blue]{name} (You)[/bold white on blue]"
                
                table.add_row(
                    rank_str,
                    name,
                    format_func(value)
                )
            
            console.print(table)
            
            # Show global metrics
            metrics = self.leaderboard.get('metrics', {})
            
            metrics_table = Table(
                title=f"[bold {COLOR_LEADERBOARD}]Community Stats[/bold {COLOR_LEADERBOARD}]",
                box=box.SIMPLE,
                show_header=False
            )
            
            metrics_table.add_column("Metric", style="white")
            metrics_table.add_column("Value", style="cyan")
            
            metrics_table.add_row(
                "Total Distance Cycled:",
                general_utils.format_distance(metrics.get('total_distance', 0.0))
            )
            
            metrics_table.add_row(
                "Total CO2 Saved:",
                general_utils.format_co2(metrics.get('total_co2_saved', 0.0))
            )
            
            metrics_table.add_row(
                "Total Trips:",
                str(metrics.get('total_trips', 0))
            )
            
            metrics_table.add_row(
                "Total Calories Burned:",
                general_utils.format_calories(metrics.get('total_calories', 0))
            )
            
            console.print(metrics_table)
            
            console.print("\nPress Enter to continue...", style="dim")
            input()
            
        else:
            # Fallback for non-Rich environments
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Leaderboard")
            
            print("View Leaderboard By:")
            print("1. Distance")
            print("2. CO2 Saved")
            print("3. Eco Points")
            print("4. Trip Count")
            print("5. Return to Social Hub")
            
            choice = input("\nSelect a metric (1-5): ")
            
            if choice == "5":
                return
            
            metric = ""
            title = ""
            
            if choice == "1":
                metric = "total_distance"
                title = "Distance Leaderboard"
                format_func = general_utils.format_distance
            elif choice == "2":
                metric = "total_co2_saved"
                title = "CO2 Saved Leaderboard"
                format_func = general_utils.format_co2
            elif choice == "3":
                metric = "eco_points"
                title = "Eco Points Leaderboard"
                format_func = lambda x: str(x)
            elif choice == "4":
                metric = "total_trips"
                title = "Trip Count Leaderboard"
                format_func = lambda x: str(x)
            
            # Get leaderboard data
            leaderboard_data = []
            for username, user_data in self.leaderboard['users'].items():
                if metric == "eco_points":
                    value = user_data.get(metric, 0)
                else:
                    value = user_data.get('stats', {}).get(metric, 0)
                
                leaderboard_data.append({
                    'username': username,
                    'name': user_data.get('name', username),
                    'value': value
                })
            
            # Sort by metric value (descending)
            leaderboard_data.sort(key=lambda x: x['value'], reverse=True)
            
            # Print header
            print(f"\n{ascii_art.Fore.BLUE}{ascii_art.Style.BRIGHT}{title}{ascii_art.Style.RESET_ALL}")
            print("-" * 60)
            
            # Format header row
            if metric == "total_distance":
                header = f"{'Rank':<6}{'User':<30}{'Distance':<20}"
            elif metric == "total_co2_saved":
                header = f"{'Rank':<6}{'User':<30}{'CO2 Saved':<20}"
            elif metric == "eco_points":
                header = f"{'Rank':<6}{'User':<30}{'Eco Points':<20}"
            elif metric == "total_trips":
                header = f"{'Rank':<6}{'User':<30}{'Trips':<20}"
            
            print(header)
            print("-" * 60)
            
            # Print rows
            for i, entry in enumerate(leaderboard_data, 1):
                username = entry['username']
                name = entry['name']
                value = entry['value']
                
                # Format rank with medal for top 3
                rank_str = str(i)
                if i == 1:
                    rank_str = "🥇 1"
                elif i == 2:
                    rank_str = "🥈 2"
                elif i == 3:
                    rank_str = "🥉 3"
                
                # Highlight current user
                if username == current_username:
                    name = f"{name} (You)"
                    name_display = f"{ascii_art.Fore.CYAN}{ascii_art.Style.BRIGHT}{name}{ascii_art.Style.RESET_ALL}"
                else:
                    name_display = name
                
                row = f"{rank_str:<6}{name_display:<30}{format_func(value):<20}"
                print(row)
            
            # Show global metrics
            metrics = self.leaderboard.get('metrics', {})
            
            print(f"\n{ascii_art.Fore.BLUE}{ascii_art.Style.BRIGHT}Community Stats{ascii_art.Style.RESET_ALL}")
            print(f"Total Distance Cycled: {general_utils.format_distance(metrics.get('total_distance', 0.0))}")
            print(f"Total CO2 Saved: {general_utils.format_co2(metrics.get('total_co2_saved', 0.0))}")
            print(f"Total Trips: {metrics.get('total_trips', 0)}")
            print(f"Total Calories Burned: {general_utils.format_calories(metrics.get('total_calories', 0))}")
            
            input("\nPress Enter to continue...")
