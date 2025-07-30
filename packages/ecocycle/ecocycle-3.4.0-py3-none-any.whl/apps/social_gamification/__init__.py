"""
EcoCycle - Social Gamification Package
Provides functionality for social sharing, achievements, and gamification.
"""
from apps.social_gamification.social_gamification_manager import SocialGamificationManager

# Provide a simple accessor function
def get_social_gamification(user_manager=None, sheets_manager=None):
    """Return a configured instance of the SocialGamificationManager."""
    return SocialGamificationManager(user_manager, sheets_manager)
