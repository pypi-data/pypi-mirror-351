"""
EcoCycle - Eco Tip View

This module defines the EcoTipView class, which handles the presentation of eco tips to the user.
"""

import logging
from typing import List, Dict, Any, Optional

from controllers.eco_tip_controller import EcoTipController

# Configure logging
logger = logging.getLogger(__name__)


class EcoTipView:
    """
    View class for displaying eco tips to the user.
    """

    def __init__(self, controller: Optional[EcoTipController] = None):
        """
        Initialize an EcoTipView.

        Args:
            controller (Optional[EcoTipController]): Controller for eco tips
        """
        self.controller = controller or EcoTipController()

    def display_random_tip(self) -> None:
        """
        Display a random eco tip to the user.
        """
        tip_data = self.controller.get_random_tip()
        self._display_tip(tip_data)

    def display_daily_tip(self) -> None:
        """
        Display the daily tip based on the day of the week.
        """
        daily_tip = self.controller.get_daily_tip()
        print(f"\nEco Tip of the Day: {daily_tip}\n")

    def display_tip_of_the_day(self) -> None:
        """
        Display the tip of the day based on the current date.
        """
        tip_data = self.controller.get_tip_of_the_day()
        print("\nEco Tip of the Day:")
        self._display_tip(tip_data)

    def display_tips_by_category(self, category: str) -> None:
        """
        Display eco tips filtered by category.

        Args:
            category (str): Category to filter by
        """
        tips = self.controller.get_tips_by_category(category)
        
        if not tips:
            print(f"\nNo tips found for category: {category}")
            return
        
        print(f"\n{len(tips)} tips found for category '{category}':")
        for i, tip_data in enumerate(tips, 1):
            print(f"\n{i}. ", end="")
            self._display_tip(tip_data, include_header=False)

    def display_high_impact_tips(self) -> None:
        """
        Display high impact eco tips.
        """
        tips = self.controller.get_high_impact_tips()
        
        if not tips:
            print("\nNo high impact tips found.")
            return
        
        print(f"\n{len(tips)} high impact tips found:")
        for i, tip_data in enumerate(tips, 1):
            print(f"\n{i}. ", end="")
            self._display_tip(tip_data, include_header=False)

    def display_all_tips(self) -> None:
        """
        Display all eco tips.
        """
        tips = self.controller.get_all_tips()
        
        if not tips:
            print("\nNo tips found.")
            return
        
        print(f"\nAll {len(tips)} eco tips:")
        for i, tip_data in enumerate(tips, 1):
            print(f"\n{i}. ", end="")
            self._display_tip(tip_data, include_header=False)

    def _display_tip(self, tip_data: Dict[str, Any], include_header: bool = True) -> None:
        """
        Helper method to display a tip.

        Args:
            tip_data (Dict[str, Any]): Dictionary containing tip data
            include_header (bool): Whether to include a header
        """
        if include_header:
            print("\nEco Tip:")
        
        print(f"{tip_data['tip']}")
        print(f"Category: {', '.join(tip_data['category'])}")
        print(f"Impact: {tip_data['impact']}")


def display_eco_tip_in_menu(controller: Optional[EcoTipController] = None) -> str:
    """
    Get a daily eco tip for display in the main menu.

    Args:
        controller (Optional[EcoTipController]): Controller for eco tips

    Returns:
        str: Daily tip text
    """
    controller = controller or EcoTipController()
    return controller.get_daily_tip()