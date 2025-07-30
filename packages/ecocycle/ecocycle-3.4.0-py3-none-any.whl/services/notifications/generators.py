"""
EcoCycle - Notification Content Generators Module
Generates content for various types of notifications.
"""
import logging
import datetime
from typing import Dict, Any, Optional, List

import apps.eco_tips
from services.notifications.templates import TemplateManager

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates content for various types of notifications."""
    
    @staticmethod
    def generate_achievement_content(
            username: str,
            name: str,
            achievement: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate achievement notification content.
        
        Args:
            username (str): Username
            name (str): Display name
            achievement (Dict): Achievement details
            
        Returns:
            Dict[str, str]: Generated content with subject and body
        """
        # Get template content
        template = TemplateManager.get_template_content("achievement_notification.txt")
        if not template:
            logger.error(f"Achievement notification template not found for user {username}")
            return {"subject": "", "body": ""}
            
        # Format template
        achievement_name = achievement.get("name", "New Achievement")
        achievement_description = achievement.get("description", "")
        points = achievement.get("points", 0)
        
        subject = f"EcoCycle Achievement Unlocked: {achievement_name}"
        
        body = template.format(
            name=name,
            achievement_name=achievement_name,
            achievement_description=achievement_description,
            points=points
        )
        
        return {"subject": subject, "body": body}
    
    @staticmethod
    def generate_weekly_summary_content(
            username: str,
            name: str,
            user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate weekly summary notification content.
        
        Args:
            username (str): Username
            name (str): Display name
            user_data (Dict): User data with trip history
            
        Returns:
            Dict[str, str]: Generated content with subject and body
        """
        # Get template content
        template = TemplateManager.get_template_content("weekly_summary.txt")
        if not template:
            logger.error(f"Weekly summary template not found for user {username}")
            return {"subject": "", "body": ""}
            
        # Calculate date range for the past week
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=today.weekday() + 7)
        end_date = start_date + datetime.timedelta(days=6)
        
        # Filter trips for the past week
        trips = user_data.get("trips", [])
        weekly_trips = []
        
        if trips:
            for trip in trips:
                trip_date_str = trip.get("date")
                if not trip_date_str:
                    continue
                    
                try:
                    trip_date = datetime.datetime.strptime(trip_date_str, "%Y-%m-%d").date()
                    if start_date <= trip_date <= end_date:
                        weekly_trips.append(trip)
                except ValueError:
                    continue
        
        # Calculate statistics
        trips_count = len(weekly_trips)
        total_distance = sum(trip.get("distance", 0) for trip in weekly_trips)
        co2_saved = sum(trip.get("co2_saved", 0) for trip in weekly_trips)
        calories_burned = sum(trip.get("calories", 0) for trip in weekly_trips)
        
        # Compare with previous week
        prev_start = start_date - datetime.timedelta(days=7)
        prev_end = start_date - datetime.timedelta(days=1)
        prev_trips = []
        
        if trips:
            for trip in trips:
                trip_date_str = trip.get("date")
                if not trip_date_str:
                    continue
                    
                try:
                    trip_date = datetime.datetime.strptime(trip_date_str, "%Y-%m-%d").date()
                    if prev_start <= trip_date <= prev_end:
                        prev_trips.append(trip)
                except ValueError:
                    continue
        
        prev_total_distance = sum(trip.get("distance", 0) for trip in prev_trips)
        
        # Generate comparison text
        if prev_total_distance > 0:
            change_percent = ((total_distance - prev_total_distance) / prev_total_distance) * 100
            if change_percent > 0:
                comparison_text = f"Great job! You cycled {change_percent:.1f}% more than last week."
            elif change_percent < 0:
                comparison_text = f"You cycled {abs(change_percent):.1f}% less than last week. Let's get back on track!"
            else:
                comparison_text = "You cycled the same distance as last week. Consistency is key!"
        else:
            if total_distance > 0:
                comparison_text = "This is your first week logging trips. Great start!"
            else:
                comparison_text = "No cycling activity this week. Let's get moving next week!"
        
        # Get eco tip
        eco_tip = apps.eco_tips.get_tip_of_the_day().get('tip', "Every bit of cycling helps reduce your carbon footprint.")
        
        # Format template
        subject = f"EcoCycle Weekly Summary: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"
        
        body = template.format(
            name=name,
            start_date=start_date.strftime("%b %d, %Y"),
            end_date=end_date.strftime("%b %d, %Y"),
            trips_count=trips_count,
            total_distance=f"{total_distance:.1f} km",
            co2_saved=f"{co2_saved:.2f} kg",
            calories_burned=f"{calories_burned:.0f}",
            comparison_text=comparison_text,
            eco_tip=eco_tip
        )
        
        return {"subject": subject, "body": body}
    
    @staticmethod
    def generate_reminder_content(
            username: str,
            name: str,
            last_trip_date: Optional[str] = None) -> Dict[str, str]:
        """
        Generate reminder notification content.
        
        Args:
            username (str): Username
            name (str): Display name
            last_trip_date (Optional[str]): Date of last trip
            
        Returns:
            Dict[str, str]: Generated content with subject and body
        """
        # Get template content
        template = TemplateManager.get_template_content("reminder.txt")
        if not template:
            logger.error(f"Reminder template not found for user {username}")
            return {"subject": "", "body": ""}
            
        # Format date if available
        if last_trip_date:
            try:
                date_obj = datetime.datetime.strptime(last_trip_date, "%Y-%m-%d").date()
                formatted_date = date_obj.strftime("%B %d, %Y")
            except ValueError:
                formatted_date = last_trip_date
        else:
            formatted_date = "not recorded"
        
        # Format template
        subject = "EcoCycle Cycling Reminder"
        
        body = template.format(
            name=name,
            last_trip_date=formatted_date
        )
        
        return {"subject": subject, "body": body}
    
    @staticmethod
    def generate_eco_tip_content(
            username: str,
            name: str) -> Dict[str, str]:
        """
        Generate eco tip notification content.
        
        Args:
            username (str): Username
            name (str): Display name
            
        Returns:
            Dict[str, str]: Generated content with subject and body
        """
        # Get today's eco tip
        tip = apps.eco_tips.get_tip_of_the_day().get('tip', "Every bit of cycling helps reduce your carbon footprint.")
        
        # Format content
        subject = "EcoCycle Daily Eco Tip"
        
        body = f"Hello {name},\n\nHere's your EcoCycle eco tip for today:\n\n{tip}\n\nSmall changes make a big difference for our planet!\n\nThe EcoCycle Team"
        
        return {"subject": subject, "body": body}
