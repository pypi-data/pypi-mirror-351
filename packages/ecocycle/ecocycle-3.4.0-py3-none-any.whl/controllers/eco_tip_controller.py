"""
EcoCycle - Eco Tip Controller

This module defines the EcoTipController class, which handles the business logic for eco tips.
"""

import logging
from typing import List, Dict, Any, Optional

from models.eco_tip import EcoTip, EcoTipCollection

# Configure logging
logger = logging.getLogger(__name__)


class EcoTipController:
    """
    Controller class for handling eco tips business logic.
    """

    def __init__(self, tip_collection: Optional[EcoTipCollection] = None):
        """
        Initialize an EcoTipController.

        Args:
            tip_collection (Optional[EcoTipCollection]): Collection of eco tips to use
        """
        self.tip_collection = tip_collection or EcoTipCollection()

    def get_random_tip(self) -> Dict[str, Any]:
        """
        Get a random eco tip.

        Returns:
            Dict[str, Any]: Dictionary representation of a random eco tip
        """
        try:
            tip = self.tip_collection.get_random_tip()
            logger.debug(f"Random tip selected: {tip.tip}")
            return tip.to_dict()
        except Exception as e:
            logger.error(f"Error getting random tip: {e}")
            return {"tip": "Error retrieving tip", "category": ["error"], "impact": "low"}

    def get_all_tips(self) -> List[Dict[str, Any]]:
        """
        Get all eco tips.

        Returns:
            List[Dict[str, Any]]: List of dictionaries representing all eco tips
        """
        try:
            tips = self.tip_collection.get_all_tips()
            return [tip.to_dict() for tip in tips]
        except Exception as e:
            logger.error(f"Error getting all tips: {e}")
            return []

    def get_tips_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get eco tips filtered by category.

        Args:
            category (str): Category to filter by

        Returns:
            List[Dict[str, Any]]: List of dictionaries representing filtered eco tips
        """
        try:
            tips = self.tip_collection.get_tips_by_category(category)
            
            if not tips:
                logger.debug(f"No tips found for category: {category}")
                return []
            
            logger.debug(f"Found {len(tips)} tips for category: {category}")
            return [tip.to_dict() for tip in tips]
        except Exception as e:
            logger.error(f"Error getting tips by category: {e}")
            return []

    def get_high_impact_tips(self) -> List[Dict[str, Any]]:
        """
        Get high impact eco tips.

        Returns:
            List[Dict[str, Any]]: List of dictionaries representing high impact eco tips
        """
        try:
            tips = self.tip_collection.get_high_impact_tips()
            return [tip.to_dict() for tip in tips]
        except Exception as e:
            logger.error(f"Error getting high impact tips: {e}")
            return []

    def get_daily_tip(self) -> str:
        """
        Get the daily tip based on the day of the week.

        Returns:
            str: Daily tip text
        """
        try:
            return self.tip_collection.get_daily_tip()
        except Exception as e:
            logger.error(f"Error getting daily tip: {e}")
            return "Error retrieving daily tip"

    def get_tip_of_the_day(self) -> Dict[str, Any]:
        """
        Get the tip of the day based on the current date.

        Returns:
            Dict[str, Any]: Dictionary representation of the tip of the day
        """
        try:
            tip = self.tip_collection.get_tip_of_the_day()
            return tip.to_dict()
        except Exception as e:
            logger.error(f"Error getting tip of the day: {e}")
            return {"tip": "Error retrieving tip of the day", "category": ["error"], "impact": "low"}