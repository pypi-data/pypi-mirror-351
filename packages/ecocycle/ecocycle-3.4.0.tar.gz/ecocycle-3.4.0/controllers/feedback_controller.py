"""
EcoCycle Feedback Controller
===========================

This controller handles all feedback-related operations including collection,
display, and management of user feedback throughout the application.
"""

from typing import Dict, List, Optional, Any
import logging
from models.feedback import FeedbackManager
from models.user_manager import UserManager

logger = logging.getLogger(__name__)

class FeedbackController:
    """Controller responsible for handling feedback-related operations."""
    
    def __init__(self, user_manager: UserManager):
        """
        Initialize the FeedbackController.
        
        Args:
            user_manager: The user manager instance for authentication
        """
        self.feedback_manager = FeedbackManager()
        self.user_manager = user_manager
    
    def submit_feedback(self, username: str, content: str, 
                       category: str = "general", 
                       rating: Optional[int] = None,
                       context: Optional[Dict] = None,
                       feature: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit new feedback from a user.
        
        Args:
            username: Username of the feedback provider
            content: Feedback content
            category: Feedback category
            rating: Optional rating (1-5)
            context: Contextual information
            feature: Specific feature being rated
            
        Returns:
            Dict containing status and feedback_id if successful
        """
        try:
            # Verify user exists
            if not self.user_manager.user_exists(username):
                return {"status": "error", "message": "User not found"}
            
            # Validate content
            if not content or len(content.strip()) == 0:
                return {"status": "error", "message": "Feedback content cannot be empty"}
            
            # Validate rating if provided
            if rating is not None and (rating < 1 or rating > 5):
                return {"status": "error", "message": "Rating must be between 1 and 5"}
            
            # Submit the feedback
            feedback_id = self.feedback_manager.add_feedback(
                username=username,
                content=content,
                category=category,
                rating=rating,
                context=context,
                feature=feature
            )
            
            logger.info(f"Feedback submitted successfully: {feedback_id}")
            return {"status": "success", "feedback_id": feedback_id}
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return {"status": "error", "message": f"Failed to submit feedback: {str(e)}"}
    
    def get_user_feedback(self, username: str) -> Dict[str, Any]:
        """
        Get all feedback submitted by a specific user.
        
        Args:
            username: Username to retrieve feedback for
            
        Returns:
            Dict containing status and feedback items if successful
        """
        try:
            # Verify user exists
            if not self.user_manager.user_exists(username):
                return {"status": "error", "message": "User not found"}
            
            feedback_items = self.feedback_manager.get_feedback_by_user(username)
            return {
                "status": "success", 
                "items": feedback_items,
                "count": len(feedback_items)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving user feedback: {str(e)}")
            return {"status": "error", "message": f"Failed to retrieve feedback: {str(e)}"}
    
    def get_feature_feedback(self, feature: str) -> Dict[str, Any]:
        """
        Get all feedback for a specific feature.
        
        Args:
            feature: Feature to retrieve feedback for
            
        Returns:
            Dict containing status and feedback items if successful
        """
        try:
            feedback_items = self.feedback_manager.get_feedback_by_feature(feature)
            return {
                "status": "success", 
                "items": feedback_items,
                "count": len(feedback_items)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving feature feedback: {str(e)}")
            return {"status": "error", "message": f"Failed to retrieve feedback: {str(e)}"}
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive feedback statistics.
        
        Returns:
            Dict containing status and statistics if successful
        """
        try:
            stats = self.feedback_manager.get_feedback_statistics()
            return {"status": "success", "statistics": stats}
            
        except Exception as e:
            logger.error(f"Error retrieving feedback stats: {str(e)}")
            return {"status": "error", "message": f"Failed to retrieve statistics: {str(e)}"}
    
    def respond_to_feedback(self, feedback_id: str, responder: str, response: str) -> Dict[str, Any]:
        """
        Add a response to a feedback item.
        
        Args:
            feedback_id: ID of the feedback to respond to
            responder: Username of the person responding
            response: Response content
            
        Returns:
            Dict containing status and success message if successful
        """
        try:
            # Verify responder exists
            if not self.user_manager.user_exists(responder):
                return {"status": "error", "message": "Responder not found"}
            
            # Verify responder has permission (admins or moderators)
            user_role = self.user_manager.get_user_role(responder)
            if user_role not in ["admin", "moderator"]:
                return {"status": "error", "message": "Insufficient permissions to respond to feedback"}
            
            # Add the response
            result = self.feedback_manager.add_feedback_response(
                feedback_id=feedback_id,
                responder=responder,
                response=response
            )
            
            if result:
                return {"status": "success", "message": "Response added successfully"}
            else:
                return {"status": "error", "message": "Feedback not found"}
            
        except Exception as e:
            logger.error(f"Error responding to feedback: {str(e)}")
            return {"status": "error", "message": f"Failed to add response: {str(e)}"}
    
    def update_feedback_status(self, feedback_id: str, status: str, username: str) -> Dict[str, Any]:
        """
        Update the status of a feedback item.
        
        Args:
            feedback_id: ID of the feedback to update
            status: New status (new, in_progress, resolved, closed)
            username: Username of the person updating the status
            
        Returns:
            Dict containing status and success message if successful
        """
        try:
            # Verify user has permission
            user_role = self.user_manager.get_user_role(username)
            if user_role not in ["admin", "moderator"]:
                return {"status": "error", "message": "Insufficient permissions to update feedback status"}
            
            # Validate status
            valid_statuses = ["new", "in_progress", "resolved", "closed"]
            if status not in valid_statuses:
                return {"status": "error", "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
            
            # Update the status
            result = self.feedback_manager.update_feedback_status(
                feedback_id=feedback_id,
                status=status
            )
            
            if result:
                return {"status": "success", "message": f"Status updated to '{status}'"}
            else:
                return {"status": "error", "message": "Feedback not found"}
            
        except Exception as e:
            logger.error(f"Error updating feedback status: {str(e)}")
            return {"status": "error", "message": f"Failed to update status: {str(e)}"}
    
    def export_feedback(self, format_type: str = "json") -> Dict[str, Any]:
        """
        Export feedback data in various formats.
        
        Args:
            format_type: Format type ("json", "csv", "report")
            
        Returns:
            Dict containing status and exported data if successful
        """
        try:
            valid_formats = ["json", "csv", "report"]
            if format_type not in valid_formats:
                return {"status": "error", "message": f"Invalid format. Must be one of: {', '.join(valid_formats)}"}
            
            exported_data = self.feedback_manager.export_feedback(format_type)
            return {"status": "success", "data": exported_data, "format": format_type}
            
        except Exception as e:
            logger.error(f"Error exporting feedback: {str(e)}")
            return {"status": "error", "message": f"Failed to export feedback: {str(e)}"}
