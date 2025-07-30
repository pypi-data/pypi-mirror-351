"""
EcoCycle - Social Gamification Manager
Central manager class for coordinating social gamification features.
"""
import logging
from typing import Dict, List, Optional, Any

from apps.social_gamification.base import SocialFeatureBase, console, RICH_AVAILABLE
from apps.social_gamification.achievements import AchievementManager
from apps.social_gamification.challenges import ChallengeManager
from apps.social_gamification.leaderboard import LeaderboardManager
from apps.social_gamification.sharing import SharingManager
from apps.social_gamification.community import CommunityImpactManager

import utils.general_utils as general_utils
import utils.ascii_art as ascii_art
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from rich.table import Table
from rich.text import Text
from rich.console import Group

logger = logging.getLogger(__name__)

class SocialGamificationManager(SocialFeatureBase):
    """
    Central manager for social gamification features.
    
    Coordinates between different social features like achievements,
    challenges, leaderboard, and social sharing.
    """
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the social gamification manager.
        
        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        super().__init__(user_manager, sheets_manager)
        
        # Initialize sub-managers
        self.achievement_manager = AchievementManager(user_manager, sheets_manager)
        self.challenge_manager = ChallengeManager(user_manager, sheets_manager)
        self.leaderboard_manager = LeaderboardManager(user_manager, sheets_manager)
        self.sharing_manager = SharingManager(user_manager, sheets_manager)
        self.community_manager = CommunityImpactManager(user_manager, sheets_manager)
    
    def run_social_features(self):
        """Run the social and gamification features interactive interface."""
        while True:
            if RICH_AVAILABLE:
                console.clear()
                
                # Create header with gradient border and enhanced styling
                header_text = Text("Connect with the cycling community and track your achievements", style="white")
                header = Panel(
                    header_text,
                    title="[bold cyan]EcoCycle Social Hub[/bold cyan]",
                    border_style="cyan",
                    box=box.DOUBLE_EDGE,
                    padding=(1, 2)
                )
                console.print(header)
                
                # Create a styled table for menu options
                menu_table = Table(
                    show_header=False,
                    box=box.ROUNDED,
                    border_style="blue",
                    padding=(0, 2),
                    expand=True
                )
                
                menu_table.add_column("Option", style="cyan", width=4, justify="center")
                menu_table.add_column("Feature", style="white")
                menu_table.add_column("Icon", style="yellow", width=4, justify="center")
                
                # Add rows with icons and descriptions
                menu_table.add_row("1", "View Your Achievements", "🏆")
                menu_table.add_row("2", "View Leaderboard", "🏅")
                menu_table.add_row("3", "Participate in Challenges", "🎯")
                menu_table.add_row("4", "Share Your Stats", "📊")
                menu_table.add_row("5", "Generate Achievement Card", "🎨")
                menu_table.add_row("6", "View Community Impact", "🌍")
                menu_table.add_row("7", "Return to Main Menu", "🔙")
                
                # Wrap table in a panel with a title
                menu_panel = Panel(
                    menu_table,
                    title="[bold blue]Social Features[/bold blue]",
                    border_style="blue",
                    box=box.ROUNDED,
                    padding=(1, 1)
                )
                
                console.print(menu_panel)
                
                # Add a footer with tip
                footer = Panel(
                    "[italic]Select a number to access the corresponding feature[/italic]",
                    border_style="dim cyan",
                    box=box.SIMPLE
                )
                console.print(footer)
                
                choice = Prompt.ask("\n[bold cyan]Select an option[/bold cyan]", 
                                    choices=["1", "2", "3", "4", "5", "6", "7"])
            else:
                # Fallback for non-Rich environments
                ascii_art.clear_screen()
                ascii_art.display_header()
                ascii_art.display_section_header("Social Hub")
                
                print("Social Features:")
                print("1. View Your Achievements 🏆")
                print("2. View Leaderboard 🏅")
                print("3. Participate in Challenges 🎯")
                print("4. Share Your Stats 📊")
                print("5. Generate Achievement Card 🎨")
                print("6. View Community Impact 🌍")
                print("7. Return to Main Menu 🔙")
                
                choice = input("\nSelect an option [1/2/3/4/5/6/7]: ")
            
            if choice == "1":
                self.achievement_manager.view_achievements()
            elif choice == "2":
                self.leaderboard_manager.view_leaderboard()
            elif choice == "3":
                self.challenge_manager.view_challenges()
            elif choice == "4":
                self.sharing_manager.share_stats()
            elif choice == "5":
                self.sharing_manager.generate_achievement_card()
            elif choice == "6":
                self.community_manager.view_community_impact()
            elif choice == "7":
                if RICH_AVAILABLE:
                    console.print(Panel(
                        "[italic]Returning to main menu...[/italic]",
                        border_style="dim",
                        box=box.SIMPLE
                    ))
                else:
                    print("\nReturning to main menu...")
                break
            else:
                if RICH_AVAILABLE:
                    console.print(Panel(
                        "[bold red]Invalid choice.[/bold red] Please select a valid option.",
                        border_style="red",
                        box=box.SIMPLE
                    ))
                else:
                    print("Invalid choice. Please select a valid option.")


def run_social_features(user_manager_instance=None, sheets_manager_instance=None):
    """
    Run the social gamification features as a standalone module.
    
    Args:
        user_manager_instance: Optional user manager
        sheets_manager_instance: Optional sheets manager
    """
    social = SocialGamificationManager(user_manager_instance, sheets_manager_instance)
    social.run_social_features()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run social features
    run_social_features()
