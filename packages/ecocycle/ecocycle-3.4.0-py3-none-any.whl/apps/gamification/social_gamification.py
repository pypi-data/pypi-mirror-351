"""
EcoCycle - Social Gamification Module (Legacy Compatibility Layer)
This file provides compatibility with the original SocialGamification class by
forwarding calls to the new modular implementation in the social_gamification package.
"""
import logging
import warnings

# Forward imports to maintain backward compatibility
from apps.social_gamification import get_social_gamification
from config.config import ACHIEVEMENTS_FILE, CHALLENGES_FILE, LEADERBOARD_FILE
from apps.social_gamification.base import (
    RICH_AVAILABLE, console, COLOR_ACHIEVEMENT, COLOR_CHALLENGE, 
    COLOR_LEADERBOARD, COLOR_COMMUNITY, COLOR_SHARING, COLOR_ERROR, COLOR_SUCCESS
)

# Import the original constants for backward compatibility
import os
import json
import time
import datetime
import webbrowser
from typing import Dict, List, Optional, Any, Tuple, Union

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# Import utilities
import utils.general_utils as general_utils
import utils.ascii_art as ascii_art
import apps.eco_tips

logger = logging.getLogger(__name__)

# Constants are now imported from config.config

# Import achievements and challenges from the new modules
from apps.social_gamification.achievements import ACHIEVEMENTS
from apps.social_gamification.challenges import CHALLENGES

class SocialGamification:
    """
    Social sharing and gamification features for EcoCycle.
    
    Legacy compatibility class that forwards to the modular implementation.
    Enhanced with Rich UI for a better user experience, including formatted tables,
    progress bars, and styled panels for different features.
    """
    
    # Display a deprecation warning
    warnings.warn(
        "This monolithic SocialGamification class is deprecated and will be removed in a future version. "
        "Please use the modular implementation in the social_gamification package instead.",
        DeprecationWarning, stacklevel=2
    )
    
    def __init__(self, user_manager=None, sheets_manager=None):
        """Initialize the social gamification module."""
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager
        
        # Create the modular implementation manager
        self._manager = get_social_gamification(user_manager, sheets_manager)
        
        # For backward compatibility, expose some properties directly
        self.achievements = self._manager.achievement_manager.achievements
        self.challenges = self._manager.challenge_manager.challenges
        self.leaderboard = self._manager.leaderboard_manager.leaderboard
        
        # Create data directory for backward compatibility
        self.data_dir = os.path.join("data", "social")
        os.makedirs(self.data_dir, exist_ok=True)
    
    # Forwarding methods to the new modular implementation
    
    def _load_achievements(self):
        """Forward to achievement manager."""
        return self._manager.achievement_manager._load_achievements()
    
    def _save_achievements(self):
        """Forward to achievement manager."""
        return self._manager.achievement_manager._save_achievements()
    
    def _load_challenges(self):
        """Forward to challenge manager."""
        return self._manager.challenge_manager._load_challenges()
    
    def _save_challenges(self):
        """Forward to challenge manager."""
        return self._manager.challenge_manager._save_challenges()
    
    def _load_leaderboard(self):
        """Forward to leaderboard manager."""
        return self._manager.leaderboard_manager._load_leaderboard()
    
    def _save_leaderboard(self):
        """Forward to leaderboard manager."""
        return self._manager.leaderboard_manager._save_leaderboard()
    
    def _update_leaderboard(self):
        """Forward to leaderboard manager."""
        return self._manager.leaderboard_manager.update_leaderboard()
    
    def run_social_features(self):
        """Run the social and gamification features interactive interface."""
        return self._manager.run_social_features()
    
    def view_achievements(self):
        """View user achievements and progress."""
        return self._manager.achievement_manager.view_achievements()
    
    def view_leaderboard(self):
        """View global leaderboard."""
        return self._manager.leaderboard_manager.view_leaderboard()
    
    def view_challenges(self):
        """View and manage challenges."""
        return self._manager.challenge_manager.view_challenges()
    
    def share_stats(self):
        """Share cycling stats."""
        return self._manager.sharing_manager.share_stats()
    
    def generate_achievement_card(self):
        """Generate an achievement card for sharing."""
        return self._manager.sharing_manager.generate_achievement_card()
    
    def view_community_impact(self):
        """View the community's collective environmental impact."""
        return self._manager.community_manager.view_community_impact()


# Standalone function for backward compatibility
def run_social_features(user_manager_instance=None, sheets_manager_instance=None):
    """
    Run the social gamification features as a standalone module.
    
    Args:
        user_manager_instance: Optional user manager
        sheets_manager_instance: Optional sheets manager
    """
    from apps.social_gamification import get_social_gamification
    social = get_social_gamification(user_manager_instance, sheets_manager_instance)
    social.run_social_features()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run social features
    run_social_features()
