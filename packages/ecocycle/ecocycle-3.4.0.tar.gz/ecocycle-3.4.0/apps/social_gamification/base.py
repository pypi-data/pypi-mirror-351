"""
EcoCycle - Social Gamification Base Module
Provides base classes and common functionality for the social gamification features.
"""
import logging
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Union

# Import configuration
from config.config import ACHIEVEMENTS_FILE, CHALLENGES_FILE, LEADERBOARD_FILE

# Rich UI components
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn, TaskProgressColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.columns import Columns
    from rich import box
    from rich.style import Style
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import utilities
import utils.general_utils as general_utils
import utils.ascii_art as ascii_art

logger = logging.getLogger(__name__)

# Initialize Rich console if available
console = Console() if RICH_AVAILABLE else None

# Define theme colors
COLOR_ACHIEVEMENT = "gold1"
COLOR_CHALLENGE = "green"
COLOR_LEADERBOARD = "blue"
COLOR_COMMUNITY = "purple"
COLOR_SHARING = "cyan"
COLOR_ERROR = "red"
COLOR_SUCCESS = "green3"

# Constants are now imported from config.config


class SocialFeatureBase:
    """Base class for social gamification features."""
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """
        Initialize the social feature base.
        
        Args:
            user_manager: User manager instance
            sheets_manager: Sheets manager instance
        """
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager
    
    def _load_json_file(self, filename: str, default_data=None) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filename: Path to the JSON file
            default_data: Default data to return if file doesn't exist
            
        Returns:
            Loaded data or default_data
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return default_data
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return default_data
    
    def _save_json_file(self, filename: str, data: Any) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            filename: Path to the JSON file
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            return False
    
    def _calculate_level(self, points: int) -> Tuple[int, int]:
        """
        Calculate user level based on eco points.
        
        Args:
            points: User's eco points
            
        Returns:
            Tuple containing (current_level, points_needed_for_next_level)
        """
        # Level thresholds
        level_thresholds = [0, 50, 125, 225, 350, 500, 700, 950, 1250, 1600, 2000]
        
        # Find current level
        current_level = 1
        for i, threshold in enumerate(level_thresholds):
            if points >= threshold:
                current_level = i + 1
            else:
                break
        
        # Calculate points needed for next level
        if current_level < len(level_thresholds):
            next_threshold = level_thresholds[current_level]
            points_needed = next_threshold - points
        else:
            # At max level
            points_needed = 0
        
        return current_level, points_needed
