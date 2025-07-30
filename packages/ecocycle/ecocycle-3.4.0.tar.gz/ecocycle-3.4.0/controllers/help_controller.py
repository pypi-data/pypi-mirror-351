"""
EcoCycle Help Controller
======================

This controller manages the contextual help system throughout the application,
providing users with relevant guidance based on their current context.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class HelpController:
    """Controller responsible for managing contextual help throughout the application."""
    
    def __init__(self, help_content_path: str = None):
        """
        Initialize the HelpController.
        
        Args:
            help_content_path: Path to the help content directory
        """
        self.help_content_path = help_content_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'docs', 'contextual_help'
        )
        os.makedirs(self.help_content_path, exist_ok=True)
        
        # Load help content
        self.help_content = self._load_help_content()
        
        # Track help usage
        self.help_usage = {}
    
    def _load_help_content(self) -> Dict[str, Any]:
        """
        Load help content from the help content directory.
        
        Returns:
            Dict: Loaded help content
        """
        help_content = {
            "screens": {},
            "features": {},
            "elements": {},
            "tooltips": {}
        }
        
        # Load screen help
        screen_help_path = os.path.join(self.help_content_path, 'screens.json')
        if os.path.exists(screen_help_path):
            try:
                with open(screen_help_path, 'r', encoding='utf-8') as f:
                    help_content["screens"] = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading screen help content: {e}")
        
        # Load feature help
        feature_help_path = os.path.join(self.help_content_path, 'features.json')
        if os.path.exists(feature_help_path):
            try:
                with open(feature_help_path, 'r', encoding='utf-8') as f:
                    help_content["features"] = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading feature help content: {e}")
        
        # Load element help
        element_help_path = os.path.join(self.help_content_path, 'elements.json')
        if os.path.exists(element_help_path):
            try:
                with open(element_help_path, 'r', encoding='utf-8') as f:
                    help_content["elements"] = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading element help content: {e}")
        
        # Load tooltips
        tooltips_path = os.path.join(self.help_content_path, 'tooltips.json')
        if os.path.exists(tooltips_path):
            try:
                with open(tooltips_path, 'r', encoding='utf-8') as f:
                    help_content["tooltips"] = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading tooltips content: {e}")
        
        return help_content
    
    def _save_help_content(self) -> None:
        """Save help content to the help content directory."""
        # Save screen help
        screen_help_path = os.path.join(self.help_content_path, 'screens.json')
        with open(screen_help_path, 'w', encoding='utf-8') as f:
            json.dump(self.help_content["screens"], f, indent=2)
        
        # Save feature help
        feature_help_path = os.path.join(self.help_content_path, 'features.json')
        with open(feature_help_path, 'w', encoding='utf-8') as f:
            json.dump(self.help_content["features"], f, indent=2)
        
        # Save element help
        element_help_path = os.path.join(self.help_content_path, 'elements.json')
        with open(element_help_path, 'w', encoding='utf-8') as f:
            json.dump(self.help_content["elements"], f, indent=2)
        
        # Save tooltips
        tooltips_path = os.path.join(self.help_content_path, 'tooltips.json')
        with open(tooltips_path, 'w', encoding='utf-8') as f:
            json.dump(self.help_content["tooltips"], f, indent=2)
    
    def get_screen_help(self, screen_id: str) -> Dict[str, Any]:
        """
        Get help content for a specific screen.
        
        Args:
            screen_id: ID of the screen to get help for
            
        Returns:
            Dict: Help content for the screen
        """
        # Log help access
        self.help_usage[screen_id] = self.help_usage.get(screen_id, 0) + 1
        
        # Get help content
        screen_help = self.help_content["screens"].get(screen_id, {})
        
        # If no specific help found, try to find a fallback
        if not screen_help and "_" in screen_id:
            # Try to find a parent screen
            parent_id = screen_id.split("_")[0]
            screen_help = self.help_content["screens"].get(parent_id, {})
        
        # If still no help found, return default help
        if not screen_help:
            return {
                "title": "Help",
                "content": "No specific help is available for this screen.",
                "links": []
            }
        
        return screen_help
    
    def get_feature_help(self, feature_id: str) -> Dict[str, Any]:
        """
        Get help content for a specific feature.
        
        Args:
            feature_id: ID of the feature to get help for
            
        Returns:
            Dict: Help content for the feature
        """
        # Log help access
        self.help_usage[f"feature_{feature_id}"] = self.help_usage.get(f"feature_{feature_id}", 0) + 1
        
        # Get help content
        feature_help = self.help_content["features"].get(feature_id, {})
        
        # If no specific help found, return default help
        if not feature_help:
            return {
                "title": "Feature Help",
                "content": "No specific help is available for this feature.",
                "links": []
            }
        
        return feature_help
    
    def get_element_help(self, element_id: str) -> Dict[str, Any]:
        """
        Get help content for a specific UI element.
        
        Args:
            element_id: ID of the element to get help for
            
        Returns:
            Dict: Help content for the element
        """
        # Log help access
        self.help_usage[f"element_{element_id}"] = self.help_usage.get(f"element_{element_id}", 0) + 1
        
        # Get help content
        element_help = self.help_content["elements"].get(element_id, {})
        
        # If no specific help found, return default help
        if not element_help:
            return {
                "title": "Help",
                "content": "No specific help is available for this element.",
                "links": []
            }
        
        return element_help
    
    def get_tooltip(self, tooltip_id: str) -> str:
        """
        Get tooltip text for a specific UI element.
        
        Args:
            tooltip_id: ID of the tooltip to get
            
        Returns:
            str: Tooltip text
        """
        # Log tooltip access
        self.help_usage[f"tooltip_{tooltip_id}"] = self.help_usage.get(f"tooltip_{tooltip_id}", 0) + 1
        
        # Get tooltip content
        return self.help_content["tooltips"].get(tooltip_id, "")
    
    def get_contextual_help(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get contextual help based on the current user context.
        
        Args:
            context: Current user context, including screen_id, feature_id, etc.
            
        Returns:
            Dict: Contextual help content
        """
        help_result = {
            "primary_help": None,
            "related_help": [],
            "tooltips": {}
        }
        
        # Determine the primary help based on context priority
        if "screen_id" in context:
            help_result["primary_help"] = self.get_screen_help(context["screen_id"])
        elif "feature_id" in context:
            help_result["primary_help"] = self.get_feature_help(context["feature_id"])
        elif "element_id" in context:
            help_result["primary_help"] = self.get_element_help(context["element_id"])
        
        # Add related help
        if "screen_id" in context and "feature_id" in context:
            if "primary_help" not in help_result or help_result["primary_help"]["title"] != "Feature Help":
                help_result["related_help"].append(self.get_feature_help(context["feature_id"]))
        
        if "screen_id" in context and "element_id" in context:
            if "primary_help" not in help_result or help_result["primary_help"]["title"] != "Help":
                help_result["related_help"].append(self.get_element_help(context["element_id"]))
        
        # Add tooltips for visible elements
        if "visible_elements" in context:
            for element_id in context["visible_elements"]:
                tooltip = self.get_tooltip(element_id)
                if tooltip:
                    help_result["tooltips"][element_id] = tooltip
        
        return help_result
    
    def add_screen_help(self, screen_id: str, title: str, content: str, 
                      links: List[Dict[str, str]] = None) -> bool:
        """
        Add or update help content for a screen.
        
        Args:
            screen_id: ID of the screen
            title: Help title
            content: Help content text
            links: List of related links (dicts with 'text' and 'url' keys)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.help_content["screens"][screen_id] = {
                "title": title,
                "content": content,
                "links": links or []
            }
            
            self._save_help_content()
            return True
        except Exception as e:
            logger.error(f"Error adding screen help: {e}")
            return False
    
    def add_feature_help(self, feature_id: str, title: str, content: str, 
                       links: List[Dict[str, str]] = None) -> bool:
        """
        Add or update help content for a feature.
        
        Args:
            feature_id: ID of the feature
            title: Help title
            content: Help content text
            links: List of related links (dicts with 'text' and 'url' keys)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.help_content["features"][feature_id] = {
                "title": title,
                "content": content,
                "links": links or []
            }
            
            self._save_help_content()
            return True
        except Exception as e:
            logger.error(f"Error adding feature help: {e}")
            return False
    
    def add_element_help(self, element_id: str, title: str, content: str, 
                       links: List[Dict[str, str]] = None) -> bool:
        """
        Add or update help content for a UI element.
        
        Args:
            element_id: ID of the element
            title: Help title
            content: Help content text
            links: List of related links (dicts with 'text' and 'url' keys)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.help_content["elements"][element_id] = {
                "title": title,
                "content": content,
                "links": links or []
            }
            
            self._save_help_content()
            return True
        except Exception as e:
            logger.error(f"Error adding element help: {e}")
            return False
    
    def add_tooltip(self, tooltip_id: str, tooltip_text: str) -> bool:
        """
        Add or update a tooltip.
        
        Args:
            tooltip_id: ID of the tooltip
            tooltip_text: Tooltip text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.help_content["tooltips"][tooltip_id] = tooltip_text
            
            self._save_help_content()
            return True
        except Exception as e:
            logger.error(f"Error adding tooltip: {e}")
            return False
    
    def get_help_usage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about help usage.
        
        Returns:
            Dict: Help usage statistics
        """
        stats = {
            "total_accesses": sum(self.help_usage.values()),
            "by_item": self.help_usage,
            "most_viewed": sorted(self.help_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        
        # Calculate category totals
        screen_accesses = sum(count for item, count in self.help_usage.items() if not item.startswith(("feature_", "element_", "tooltip_")))
        feature_accesses = sum(count for item, count in self.help_usage.items() if item.startswith("feature_"))
        element_accesses = sum(count for item, count in self.help_usage.items() if item.startswith("element_"))
        tooltip_accesses = sum(count for item, count in self.help_usage.items() if item.startswith("tooltip_"))
        
        stats["by_category"] = {
            "screens": screen_accesses,
            "features": feature_accesses,
            "elements": element_accesses,
            "tooltips": tooltip_accesses
        }
        
        return stats
