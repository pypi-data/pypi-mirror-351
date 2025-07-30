"""
EcoCycle - Notification Templates Module
Manages notification templates for various channels.
"""
import os
import logging
from typing import Dict, List, Optional

from services.notifications.config import EMAIL_TEMPLATES_DIR

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages notification templates for various channels."""
    
    DEFAULT_TEMPLATES = {
        "welcome_email.txt": """Welcome to EcoCycle, {name}!
            
Thank you for joining our community of eco-friendly cyclists. Together, we're making a difference for our planet, one bike ride at a time.

Your EcoCycle account is now active and ready to use. You can start logging your cycling trips right away and track your positive environmental impact.

Here are some quick tips to get started:
1. Log your cycling trips regularly to track your progress
2. Check your carbon footprint reduction in the statistics section
3. Use the weather and route planning features to plan your rides
4. Share your achievements with friends and family

Happy cycling!

The EcoCycle Team
""",
        "achievement_notification.txt": """Congratulations, {name}!

You've earned a new achievement: {achievement_name}

{achievement_description}

You've earned {points} eco points for this achievement. Keep up the great work!

View all your achievements in the EcoCycle app.

The EcoCycle Team
""",
        "weekly_summary.txt": """Weekly Cycling Summary for {name}

Week: {start_date} to {end_date}

Your weekly stats:
- Trips completed: {trips_count}
- Total distance: {total_distance}
- CO2 saved: {co2_saved}
- Calories burned: {calories_burned}

{comparison_text}

Eco Tip of the Week:
{eco_tip}

Keep cycling for a greener planet!

The EcoCycle Team
""",
        "reminder.txt": """Hello {name},

It's been a while since your last cycle trip. Don't forget to log your cycling activities to track your environmental impact.

Your last recorded trip was on {last_trip_date}.

Ready to get back on the saddle? The weather forecast for today looks great for cycling!

Remember, every cycling trip contributes to a greener planet.

The EcoCycle Team
"""
    }
    
    @classmethod
    def create_default_templates(cls) -> None:
        """
        Create default email templates if they don't exist.
        """
        # Create templates directory if it doesn't exist
        os.makedirs(EMAIL_TEMPLATES_DIR, exist_ok=True)
        
        # Create default templates
        for template_name, template_content in cls.DEFAULT_TEMPLATES.items():
            template_path = os.path.join(EMAIL_TEMPLATES_DIR, template_name)
            if not os.path.exists(template_path):
                try:
                    with open(template_path, 'w') as file:
                        file.write(template_content)
                except Exception as e:
                    logger.error(f"Error creating template {template_name}: {e}")
    
    @classmethod
    def get_template_content(cls, template_name: str) -> Optional[str]:
        """
        Get the content of a template.
        
        Args:
            template_name (str): Name of the template
            
        Returns:
            Optional[str]: Template content or None if not found
        """
        template_path = os.path.join(EMAIL_TEMPLATES_DIR, template_name)
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading template {template_name}: {e}")
                return None
        else:
            # Return default template if available
            return cls.DEFAULT_TEMPLATES.get(template_name)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List[str]: List of template names
        """
        try:
            return os.listdir(EMAIL_TEMPLATES_DIR)
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []
