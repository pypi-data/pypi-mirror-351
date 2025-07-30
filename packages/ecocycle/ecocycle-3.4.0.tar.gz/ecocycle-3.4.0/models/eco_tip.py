"""
EcoCycle - Eco Tip Model

This module defines the EcoTip model class, which represents an eco-friendly or cycling tip.
"""

from typing import List, Dict, Any, Optional
import datetime
import random


class EcoTip:
    """
    Model class representing an eco-friendly or cycling tip.
    """

    def __init__(self, tip: str, category: List[str], impact: str):
        """
        Initialize an EcoTip object.

        Args:
            tip (str): The text content of the tip
            category (List[str]): List of categories this tip belongs to
            impact (str): Impact level of the tip (high, medium, low)
        """
        self.tip = tip
        self.category = category
        self.impact = impact

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the EcoTip object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the EcoTip
        """
        return {
            "tip": self.tip,
            "category": self.category,
            "impact": self.impact
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EcoTip':
        """
        Create an EcoTip object from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing tip data

        Returns:
            EcoTip: New EcoTip object
        """
        return cls(
            tip=data["tip"],
            category=data["category"],
            impact=data["impact"]
        )


class EcoTipCollection:
    """
    Model class representing a collection of eco tips.
    """

    # Collection of eco-friendly and cycling tips
    _TIPS_DATA = [
        {
            "tip": "Keep your tires properly inflated to reduce rolling resistance and save energy.",
            "category": ["cycling", "efficiency", "maintenance"],
            "impact": "high"
        },
        {
            "tip": "Cycling 10km instead of driving saves approximately 1.3kg of CO2 emissions.",
            "category": ["environment", "stats"],
            "impact": "high"
        },
        # ... more tips would be here, but for brevity we'll include just a few
        {
            "tip": "Stay hydrated! Drink water before, during, and after your ride.",
            "category": ["health", "cycling"],
            "impact": "medium"
        },
        {
            "tip": "Regular cycling can reduce the risk of heart disease by up to 50%.",
            "category": ["health", "stats"],
            "impact": "high"
        }
    ]

    # Daily tips based on day of week
    _DAILY_TIPS = {
        0: "Monday: Start your week right - plan your cycling routes in advance.",
        1: "Tuesday: Check your tire pressure today for maximum efficiency.",
        2: "Wednesday: Mid-week motivation - track your progress and celebrate small wins.",
        3: "Thursday: Try a new cycling route today to keep things interesting.",
        4: "Friday: Weekend prep - ensure your bike is ready for weekend adventures.",
        5: "Saturday: Explore new areas by bike and discover your community.",
        6: "Sunday: Rest and recover - gentle cycling today helps muscle recovery."
    }

    def __init__(self, tips_data: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize an EcoTipCollection.

        Args:
            tips_data (Optional[List[Dict[str, Any]]]): Optional list of tip dictionaries to use instead of default
        """
        if tips_data is None:
            # Use the default tips data
            self.tips = [EcoTip.from_dict(tip_data) for tip_data in self._TIPS_DATA]
        else:
            # Use the provided tips data
            self.tips = [EcoTip.from_dict(tip_data) for tip_data in tips_data]

    def get_random_tip(self) -> EcoTip:
        """
        Returns a random eco-friendly or cycling tip.

        Returns:
            EcoTip: A random tip
        """
        return random.choice(self.tips)

    def get_all_tips(self) -> List[EcoTip]:
        """
        Returns all available tips.

        Returns:
            List[EcoTip]: All tips in the collection
        """
        return self.tips

    def get_tips_by_category(self, category: str) -> List[EcoTip]:
        """
        Returns tips filtered by category keywords.
        
        Args:
            category (str): Category to filter by (e.g., 'health', 'environment', 'safety')
            
        Returns:
            List[EcoTip]: List of tips related to the specified category
        """
        category = category.lower()
        return [tip for tip in self.tips if category in [cat.lower() for cat in tip.category]]

    def get_high_impact_tips(self) -> List[EcoTip]:
        """
        Returns tips with high impact.

        Returns:
            List[EcoTip]: List of high impact tips
        """
        return [tip for tip in self.tips if tip.impact == "high"]

    def get_daily_tip(self) -> str:
        """
        Returns a tip based on the day of the week, giving a sense of consistency.
        
        Returns:
            str: The tip for today
        """
        day_of_week = datetime.datetime.now().weekday()
        return self._DAILY_TIPS[day_of_week]

    def get_tip_of_the_day(self) -> EcoTip:
        """
        Returns a consistent tip for the day based on the date.
        
        Returns:
            EcoTip: The tip for today
        """
        # Use the date as a seed for the random generator to get consistent results
        day_of_year = datetime.datetime.now().timetuple().tm_yday
        random.seed(day_of_year)
        
        # Get a random tip using the seeded generator
        tip = random.choice(self.tips)
        
        # Reset the random seed to ensure other random functions are not affected
        random.seed()
        
        return tip