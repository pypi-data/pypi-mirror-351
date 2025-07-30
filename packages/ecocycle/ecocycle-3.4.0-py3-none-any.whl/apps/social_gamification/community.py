"""
EcoCycle - Community Impact Module
Visualizes the community's collective environmental impact.
"""
import logging
from typing import Dict, Any

from apps.social_gamification.base import (
    SocialFeatureBase, RICH_AVAILABLE, console, 
    COLOR_COMMUNITY
)

# Rich UI imports
if RICH_AVAILABLE:
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.text import Text
    from rich.console import Group

import utils.ascii_art as ascii_art
import utils.general_utils as general_utils
import apps.eco_tips

logger = logging.getLogger(__name__)


class CommunityImpactManager(SocialFeatureBase):
    """Manages community impact visualization and statistics."""
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the community impact manager.
        
        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        super().__init__(user_manager, sheets_manager)
    
    def view_community_impact(self):
        """View the community's collective environmental impact."""
        # Get community metrics
        metrics = self._get_community_metrics()
        
        # Get a random eco tip
        eco_tip_dict = apps.eco_tips.get_random_tip()
        # Extract the tip text from the dictionary
        eco_tip_text = eco_tip_dict.get('tip', 'Cycling regularly helps reduce your carbon footprint!')
        
        if RICH_AVAILABLE:
            console.clear()
            
            # Create header
            header = Panel(
                "Discover the environmental impact of the entire EcoCycle community",
                title=f"[bold {COLOR_COMMUNITY}]Community Environmental Impact[/bold {COLOR_COMMUNITY}]",
                border_style=COLOR_COMMUNITY,
                box=box.DOUBLE
            )
            console.print(header)
            
            # Community stats
            stats_table = Table(box=box.SIMPLE, show_header=False)
            stats_table.add_column("Metric", style="bold cyan", width=25)
            stats_table.add_column("Value", style="white")
            stats_table.add_column("Impact", style="green")
            
            total_distance = metrics.get('total_distance', 0.0)
            total_co2_saved = metrics.get('total_co2_saved', 0.0)
            total_trips = metrics.get('total_trips', 0)
            total_users = metrics.get('total_users', 0)
            total_challenges = metrics.get('total_challenges', 0)
            
            # Add rows with impact equivalents
            co2_trees = total_co2_saved / 20  # Approximate CO2 absorption per tree per year (kg)
            fuel_saved = total_distance * 0.07 / 1000  # Approximate fuel consumption (liters per km)
            
            stats_table.add_row(
                "🚲 Total Distance Cycled:",
                general_utils.format_distance(total_distance),
                f"Equivalent to {int(total_distance/40000*100)}% of Earth's circumference"
            )
            
            stats_table.add_row(
                "🌍 Total CO2 Saved:",
                general_utils.format_co2(total_co2_saved),
                f"Equivalent to planting {int(co2_trees)} trees"
            )
            
            stats_table.add_row(
                "⛽ Fuel Saved:",
                f"{fuel_saved:.2f} liters",
                f"Worth approximately ${fuel_saved * 1.5:.2f}"
            )
            
            stats_table.add_row(
                "🚗 Car Trips Avoided:",
                str(total_trips),
                "Reducing traffic and pollution"
            )
            
            stats_table.add_row(
                "👥 Active Community Members:",
                str(total_users),
                "Making a difference together"
            )
            
            stats_table.add_row(
                "🏆 Completed Challenges:",
                str(total_challenges),
                "Pushing our environmental impact further"
            )
            
            stats_panel = Panel(
                stats_table,
                title="[bold]Community Statistics[/bold]",
                border_style=COLOR_COMMUNITY,
                box=box.ROUNDED
            )
            
            # Create eco tip panel
            tip_panel = Panel(
                Group(
                    Text("Did you know?", style="bold yellow"),
                    Text(""),
                    Text(eco_tip_text, style="italic")
                ),
                title="[bold green]Eco Tip[/bold green]",
                border_style="green",
                box=box.ROUNDED
            )
            
            # Print panels
            console.print(stats_panel)
            console.print(tip_panel)
            
            # Individual contribution
            if self.user_manager:
                user = self.user_manager.get_current_user()
                if user:
                    username = user.get('username')
                    stats = user.get('stats', {})
                    user_distance = stats.get('total_distance', 0.0)
                    user_co2 = stats.get('total_co2_saved', 0.0)
                    
                    # Calculate percentage contribution
                    distance_percent = (user_distance / total_distance) * 100 if total_distance > 0 else 0
                    co2_percent = (user_co2 / total_co2_saved) * 100 if total_co2_saved > 0 else 0
                    
                    contribution_table = Table(box=box.SIMPLE, show_header=False)
                    contribution_table.add_column("Metric", style="bold cyan")
                    contribution_table.add_column("Your Contribution", style="yellow")
                    contribution_table.add_column("Percentage", style="green")
                    
                    contribution_table.add_row(
                        "Distance Contribution:",
                        general_utils.format_distance(user_distance),
                        f"{distance_percent:.1f}% of community total"
                    )
                    
                    contribution_table.add_row(
                        "CO2 Saving Contribution:",
                        general_utils.format_co2(user_co2),
                        f"{co2_percent:.1f}% of community total"
                    )
                    
                    contribution_panel = Panel(
                        contribution_table,
                        title="[bold]Your Contribution[/bold]",
                        border_style="yellow",
                        box=box.ROUNDED
                    )
                    
                    console.print(contribution_panel)
            
            console.print("\nPress Enter to continue...", style="dim")
            input()
            
        else:
            # Fallback for non-Rich environments
            ascii_art.clear_screen()
            ascii_art.display_header()
            ascii_art.display_section_header("Community Environmental Impact")
            
            total_distance = metrics.get('total_distance', 0.0)
            total_co2_saved = metrics.get('total_co2_saved', 0.0)
            total_trips = metrics.get('total_trips', 0)
            total_users = metrics.get('total_users', 0)
            total_challenges = metrics.get('total_challenges', 0)
            
            # Calculate impact equivalents
            co2_trees = total_co2_saved / 20  # Approximate CO2 absorption per tree per year (kg)
            fuel_saved = total_distance * 0.07 / 1000  # Approximate fuel consumption (liters per km)
            
            print(f"{ascii_art.Fore.CYAN}{ascii_art.Style.BRIGHT}Community Statistics:{ascii_art.Style.RESET_ALL}")
            print(f"🚲 Total Distance Cycled: {general_utils.format_distance(total_distance)}")
            print(f"   Equivalent to {int(total_distance/40000*100)}% of Earth's circumference")
            
            print(f"🌍 Total CO2 Saved: {general_utils.format_co2(total_co2_saved)}")
            print(f"   Equivalent to planting {int(co2_trees)} trees")
            
            print(f"⛽ Fuel Saved: {fuel_saved:.2f} liters")
            print(f"   Worth approximately ${fuel_saved * 1.5:.2f}")
            
            print(f"🚗 Car Trips Avoided: {total_trips}")
            print("   Reducing traffic and pollution")
            
            print(f"👥 Active Community Members: {total_users}")
            print("   Making a difference together")
            
            print(f"🏆 Completed Challenges: {total_challenges}")
            print("   Pushing our environmental impact further")
            
            # Print eco tip
            print(f"\n{ascii_art.Fore.GREEN}{ascii_art.Style.BRIGHT}Eco Tip:{ascii_art.Style.RESET_ALL}")
            print(f"Did you know? {eco_tip_text}")
            
            # Individual contribution
            if self.user_manager:
                user = self.user_manager.get_current_user()
                if user:
                    username = user.get('username')
                    stats = user.get('stats', {})
                    user_distance = stats.get('total_distance', 0.0)
                    user_co2 = stats.get('total_co2_saved', 0.0)
                    
                    # Calculate percentage contribution
                    distance_percent = (user_distance / total_distance) * 100 if total_distance > 0 else 0
                    co2_percent = (user_co2 / total_co2_saved) * 100 if total_co2_saved > 0 else 0
                    
                    print(f"\n{ascii_art.Fore.YELLOW}{ascii_art.Style.BRIGHT}Your Contribution:{ascii_art.Style.RESET_ALL}")
                    print(f"Distance Contribution: {general_utils.format_distance(user_distance)} ({distance_percent:.1f}% of community total)")
                    print(f"CO2 Saving Contribution: {general_utils.format_co2(user_co2)} ({co2_percent:.1f}% of community total)")
            
            input("\nPress Enter to continue...")
    
    def _get_community_metrics(self) -> Dict[str, Any]:
        """
        Get community metrics from the leaderboard.
        
        Returns:
            Dictionary of community metrics
        """
        metrics = {
            'total_distance': 0.0,
            'total_co2_saved': 0.0,
            'total_trips': 0,
            'total_users': 0,
            'total_challenges': 0
        }
        
        if not self.user_manager:
            return metrics
        
        # Load leaderboard data which contains accumulated metrics from all users
        try:
            leaderboard_data = self._load_json_file(LEADERBOARD_FILE, {})
            if leaderboard_data and 'metrics' in leaderboard_data:
                metrics.update(leaderboard_data['metrics'])
                metrics['total_users'] = len(leaderboard_data.get('users', {}))
                
                # Add the current user's challenges
                current_user = self.user_manager.get_current_user()
                if current_user:
                    completed_challenges = current_user.get('completed_challenges', [])
                    metrics['total_challenges'] = len(completed_challenges)
            
            # If we don't have leaderboard data, fall back to just current user data
            else:
                current_user = self.user_manager.get_current_user()
                if current_user:
                    stats = current_user.get('stats', {})
                    
                    # Get user stats
                    total_distance = stats.get('total_distance', 0.0)
                    total_co2_saved = stats.get('total_co2_saved', 0.0)
                    total_user_trips = stats.get('total_trips', 0)
                    
                    # Add to metrics
                    metrics['total_distance'] = total_distance
                    metrics['total_co2_saved'] = total_co2_saved
                    metrics['total_trips'] = total_user_trips
                    metrics['total_users'] = 1
                    
                    # Count completed challenges
                    completed_challenges = current_user.get('completed_challenges', [])
                    metrics['total_challenges'] = len(completed_challenges)
        except Exception as e:
            logger.error(f"Error getting community metrics: {e}")
            # If there's an error, just provide the current user's metrics
            current_user = self.user_manager.get_current_user()
            if current_user:
                stats = current_user.get('stats', {})
                metrics['total_distance'] = stats.get('total_distance', 0.0)
                metrics['total_co2_saved'] = stats.get('total_co2_saved', 0.0)
                metrics['total_trips'] = stats.get('total_trips', 0)
                metrics['total_users'] = 1
        
        return metrics
