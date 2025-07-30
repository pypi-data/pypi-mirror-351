"""
EcoCycle - Gamification Package
Provides gamification features including achievements, challenges, and social features.
"""

# Import legacy class for backward compatibility
from apps.gamification.social_gamification import SocialGamification

# Import new modular functionality
from apps.social_gamification import get_social_gamification

# Provide convenience function for creating a social gamification instance
def create_social_gamification(user_manager=None, sheets_manager=None):
    """
    Create a social gamification instance.
    
    This function provides a unified entry point for creating either a legacy
    SocialGamification instance or the new modular implementation based on
    your preference.
    
    Args:
        user_manager: Optional user manager instance
        sheets_manager: Optional sheets manager instance
        
    Returns:
        SocialGamification instance (legacy) by default for backward compatibility
    """
    return SocialGamification(user_manager, sheets_manager)


# Function to run social features standalone
def run_social_features(user_manager=None, sheets_manager=None):
    """
    Run the social gamification features as a standalone module.
    
    Args:
        user_manager: Optional user manager instance
        sheets_manager: Optional sheets manager instance
    """
    social = create_social_gamification(user_manager, sheets_manager)
    social.run_social_features()