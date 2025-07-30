"""
EcoCycle - Social Gamification Main Module
Provides the main entry point for the social gamification features.
"""
import logging
import os
from typing import Dict, List, Optional, Any

# Import from the modular components
from apps.social_gamification.social_gamification_manager import SocialGamificationManager

logger = logging.getLogger(__name__)

# Create a function to run the social features in standalone mode
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
