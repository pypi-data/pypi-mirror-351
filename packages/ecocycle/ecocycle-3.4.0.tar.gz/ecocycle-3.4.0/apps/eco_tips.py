"""
EcoCycle - Eco Tips Module
Contains a collection of eco-friendly and cycling tips to display to users.

This module provides backward compatibility for the new MVC architecture.
New code should use the classes in the models, controllers, and views packages.
"""
import random
import logging
import datetime
from typing import Dict, List, Any, Optional

# Import from MVC architecture
from models.eco_tip import EcoTip, EcoTipCollection
from controllers.eco_tip_controller import EcoTipController
from views.eco_tip_view import EcoTipView, display_eco_tip_in_menu

logger = logging.getLogger(__name__)

# Create instances of the MVC classes for backward compatibility
_tip_collection = EcoTipCollection()
_tip_controller = EcoTipController(_tip_collection)
_tip_view = EcoTipView(_tip_controller)

# Collection of eco-friendly and cycling tips
TIPS = [
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
    {
        "tip": "Stay hydrated! Drink water before, during, and after your ride.",
        "category": ["health", "cycling"],
        "impact": "medium"
    },
    {
        "tip": "Regular cycling can reduce the risk of heart disease by up to 50%.",
        "category": ["health", "stats"],
        "impact": "high"
    },
    {
        "tip": "Use hand signals when cycling on roads to communicate with other road users.",
        "category": ["safety", "cycling"],
        "impact": "high"
    },
    {
        "tip": "A properly adjusted bike can increase your efficiency by up to 15%.",
        "category": ["cycling", "efficiency", "maintenance"],
        "impact": "medium"
    },
    {
        "tip": "Cycling for 30 minutes burns approximately 300 calories for an average adult.",
        "category": ["health", "stats"],
        "impact": "medium"
    },
    {
        "tip": "Always wear a helmet when cycling, it reduces the risk of head injury by up to 70%.",
        "category": ["safety", "cycling"],
        "impact": "high"
    },
    {
        "tip": "Plan your routes to avoid heavy traffic areas for a safer and more enjoyable ride.",
        "category": ["safety", "planning"],
        "impact": "medium"
    },
    {
        "tip": "When climbing hills, shift to an easier gear before you start the ascent.",
        "category": ["cycling", "technique"],
        "impact": "medium"
    },
    {
        "tip": "Use lights and reflective clothing when cycling in low light conditions.",
        "category": ["safety", "equipment"],
        "impact": "high"
    },
    {
        "tip": "Lock your bike securely through the frame and both wheels when leaving it unattended.",
        "category": ["security", "equipment"],
        "impact": "high"
    },
    {
        "tip": "Regular bike maintenance extends the life of your bicycle and improves safety.",
        "category": ["maintenance", "safety"],
        "impact": "high"
    },
    {
        "tip": "Cycling to work just once a week can reduce your carbon footprint by over 50kg annually.",
        "category": ["environment", "stats"],
        "impact": "high"
    },
    {
        "tip": "Breathe deeply and rhythmically while cycling to optimize oxygen intake.",
        "category": ["health", "technique"],
        "impact": "medium"
    },
    {
        "tip": "Carry a basic repair kit including a pump, spare tube, and multi-tool on longer rides.",
        "category": ["maintenance", "equipment"],
        "impact": "medium"
    },
    {
        "tip": "Adjust your saddle height so your leg is almost fully extended at the bottom of the pedal stroke.",
        "category": ["cycling", "technique", "maintenance"],
        "impact": "high"
    },
    {
        "tip": "Stay visible to motorists by wearing bright colors during daytime rides.",
        "category": ["safety", "equipment"],
        "impact": "high"
    },
    {
        "tip": "Pedal in circles, not just down. Pull up on the backstroke for more efficient cycling.",
        "category": ["cycling", "technique"],
        "impact": "medium"
    },
    {
        "tip": "Cycling improves mental health by reducing stress and anxiety levels.",
        "category": ["health", "mental health"],
        "impact": "high"
    },
    {
        "tip": "The average person loses 13 pounds in their first year of regular cycling.",
        "category": ["health", "stats"],
        "impact": "medium"
    },
    {
        "tip": "Maintain a consistent cadence of 80-90 RPM for optimal efficiency.",
        "category": ["cycling", "technique"],
        "impact": "medium"
    },
    {
        "tip": "Regular cycling can improve your sleep quality and reduce insomnia.",
        "category": ["health", "mental health"],
        "impact": "medium"
    },
    {
        "tip": "Keep a cycling journal to track your progress and set achievable goals.",
        "category": ["motivation", "planning"],
        "impact": "medium"
    },
    {
        "tip": "To avoid knee pain, ensure your saddle is at the right height and position.",
        "category": ["health", "maintenance"],
        "impact": "high"
    },
    {
        "tip": "Replacing a 5-mile car commute with cycling saves about 300kg of carbon emissions per year.",
        "category": ["environment", "stats"],
        "impact": "high"
    },
    {
        "tip": "Cycling strengthens your immune system, reducing the incidence of upper respiratory infections.",
        "category": ["health"],
        "impact": "medium"
    },
    {
        "tip": "Use a bell or horn to alert pedestrians and other cyclists of your approach.",
        "category": ["safety", "equipment"],
        "impact": "medium"
    },
    {
        "tip": "Practice looking over your shoulder without swerving to improve road safety.",
        "category": ["safety", "technique"],
        "impact": "high"
    },
    {
        "tip": "Cycling is a low-impact exercise, making it ideal for people with joint problems.",
        "category": ["health"],
        "impact": "medium"
    },
    {
        "tip": "Stop at red lights and stop signs. Following traffic rules keeps everyone safer.",
        "category": ["safety", "rules"],
        "impact": "high"
    },
    {
        "tip": "Clean and lubricate your chain regularly for smoother shifting and longer component life.",
        "category": ["maintenance"],
        "impact": "medium"
    },
    {
        "tip": "Consider cycling with a friend or joining a cycling group for motivation and safety.",
        "category": ["motivation", "safety", "social"],
        "impact": "medium"
    },
    {
        "tip": "The global bicycle industry provides employment for over 1.5 million people worldwide.",
        "category": ["stats", "global impact"],
        "impact": "low"
    },
    {
        "tip": "For longer rides, eat small amounts regularly to maintain energy levels.",
        "category": ["health", "nutrition"],
        "impact": "medium"
    },
    {
        "tip": "Choose cycling routes with dedicated bike lanes when available for added safety.",
        "category": ["safety", "planning"],
        "impact": "high"
    },
    {
        "tip": "The most efficient cycling speed for most people is between 12-15 mph (19-24 km/h).",
        "category": ["cycling", "efficiency", "stats"],
        "impact": "medium"
    },
    {
        "tip": "Cycling improves balance, coordination, and overall body awareness.",
        "category": ["health"],
        "impact": "medium"
    },
    {
        "tip": "When cycling in a group, maintain a steady pace and communicate hazards to others.",
        "category": ["safety", "social", "technique"],
        "impact": "medium"
    },
    {
        "tip": "Regular cycling can add 2-3 years to your life expectancy.",
        "category": ["health", "stats"],
        "impact": "high"
    },
    {
        "tip": "Cycling to work can help you arrive more alert and productive than driving.",
        "category": ["health", "mental health", "productivity"],
        "impact": "medium"
    },
    {
        "tip": "Use bike sharing programs in cities to reduce the need for car travel.",
        "category": ["environment", "urban", "transportation"],
        "impact": "high"
    },
    {
        "tip": "Bicycles are the most energy-efficient form of transportation, using 5 times less energy than walking.",
        "category": ["environment", "efficiency", "stats"],
        "impact": "high"
    },
    {
        "tip": "Monitor your heart rate during rides to optimize training and track fitness improvements.",
        "category": ["health", "technology", "technique"],
        "impact": "medium"
    },
    {
        "tip": "A cyclist needs only 35 calories to travel one mile, while a car uses 1,860 calories (of fuel).",
        "category": ["environment", "stats"],
        "impact": "high"
    },
    {
        "tip": "Replace plastic water bottles with reusable ones to reduce waste during cycling.",
        "category": ["environment", "equipment"],
        "impact": "medium"
    },
    {
        "tip": "If you cycle regularly, consider offsetting other carbon emissions through verified programs.",
        "category": ["environment", "global impact"],
        "impact": "high"
    },
    {
        "tip": "Cycling communities often organize clean-up rides to collect trash along bike routes.",
        "category": ["environment", "social", "community"],
        "impact": "medium"
    },
    {
        "tip": "Cycling 10km each way to work would save 1500kg of greenhouse gas emissions each year.",
        "category": ["environment", "stats"],
        "impact": "high"
    },
    {
        "tip": "Cycle tourism contributes billions to local economies while having minimal environmental impact.",
        "category": ["environment", "economy", "tourism"],
        "impact": "medium"
    },
    {
        "tip": "Bicycle repair is a sustainable skill that extends the life of a highly efficient vehicle.",
        "category": ["environment", "maintenance", "skills"],
        "impact": "medium"
    },
    {
        "tip": "Making a new car creates as much carbon pollution as driving it for 20,000 miles (32,000 km).",
        "category": ["environment", "stats"],
        "impact": "high"
    },
    {
        "tip": "Electric bikes make cycling accessible to more people and still have a lower carbon footprint than cars.",
        "category": ["environment", "technology", "accessibility"],
        "impact": "high"
    }
]

# Daily tips based on day of week
DAILY_TIPS = {
    0: "Monday: Start your week right - plan your cycling routes in advance.",
    1: "Tuesday: Check your tire pressure today for maximum efficiency.",
    2: "Wednesday: Mid-week motivation - track your progress and celebrate small wins.",
    3: "Thursday: Try a new cycling route today to keep things interesting.",
    4: "Friday: Weekend prep - ensure your bike is ready for weekend adventures.",
    5: "Saturday: Explore new areas by bike and discover your community.",
    6: "Sunday: Rest and recover - gentle cycling today helps muscle recovery."
}


def get_random_tip() -> Dict[str, Any]:
    """Returns a random eco-friendly or cycling tip."""
    # Use the controller from the MVC architecture
    return _tip_controller.get_random_tip()


def get_all_tips() -> List[Dict[str, Any]]:
    """Returns all available tips."""
    # Use the controller from the MVC architecture
    return _tip_controller.get_all_tips()


def get_tips_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Returns tips filtered by category keywords.

    Args:
        category (str): Category to filter by (e.g., 'health', 'environment', 'safety')

    Returns:
        list: List of tips related to the specified category
    """
    # Use the controller from the MVC architecture
    return _tip_controller.get_tips_by_category(category)


def get_high_impact_tips() -> List[Dict[str, Any]]:
    """Returns tips with high impact."""
    # Use the controller from the MVC architecture
    return _tip_controller.get_high_impact_tips()


def get_daily_tip() -> str:
    """
    Returns a tip based on the day of the week, giving a sense of consistency.

    Returns:
        str: The tip for today
    """
    # Use the controller from the MVC architecture
    return _tip_controller.get_daily_tip()


def get_tip_of_the_day() -> Dict[str, Any]:
    """
    Returns a consistent tip for the day based on the date.

    Returns:
        dict: The tip for today
    """
    # Use the controller from the MVC architecture
    return _tip_controller.get_tip_of_the_day()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test tips functionality
    print("Daily tip:")
    print(get_daily_tip())
    print("\nRandom tip:")
    tip = get_random_tip()
    print(f"Tip: {tip['tip']}")
    print(f"Category: {', '.join(tip['category'])}")
    print(f"Impact: {tip['impact']}")

    print("\nHealth tips:")
    health_tips = get_tips_by_category("health")
    for i, tip in enumerate(health_tips[:3], 1):  # Show first 3 only
        print(f"{i}. {tip['tip']}")

    print("\nHigh impact tips:")
    high_impact_tips = get_high_impact_tips()
    for i, tip in enumerate(high_impact_tips[:3], 1):  # Show first 3 only
        print(f"{i}. {tip['tip']}")

    print("\nTip of the day:")
    daily_tip = get_tip_of_the_day()
    print(f"Tip: {daily_tip['tip']}")
    print(f"Category: {', '.join(daily_tip['category'])}")
