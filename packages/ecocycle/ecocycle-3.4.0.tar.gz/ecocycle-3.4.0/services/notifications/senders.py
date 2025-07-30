"""
EcoCycle - Notification Senders Module
Handles sending notifications through various channels (email, SMS, in-app).
"""
import smtplib
import ssl
import logging
from email.message import EmailMessage
from typing import Dict, Optional, Any, Tuple

from services.notifications.config import EMAIL_SENDER, EMAIL_PASSWORD

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles sending email notifications."""
    
    @staticmethod
    def send_email(to_email: str, subject: str, message_body: str) -> Tuple[bool, str]:
        """
        Actually sends an email using Gmail SMTP.
        Handles SSL certificate verification issues gracefully.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            message_body (str): Email body
            
        Returns:
            Tuple[bool, str]: Success status and error message if any
        """
        if not EMAIL_SENDER or not EMAIL_PASSWORD:
            return False, "Email credentials not configured"
            
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = EMAIL_SENDER
            message["To"] = to_email
            message.set_content(message_body)
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(message)
                
            return True, ""
        except ssl.SSLCertVerificationError as e:
            logger.warning(f"SSL Certificate verification failed: {e}")
            try:
                # Try with less secure context
                context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                context.verify_mode = ssl.CERT_NONE
                context.check_hostname = False
                
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    server.send_message(message)
                    
                return True, ""
            except Exception as fallback_e:
                logger.error(f"Failed to send email with fallback SSL context: {fallback_e}")
                return False, str(fallback_e)
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False, str(e)


class SmsSender:
    """Handles sending SMS notifications."""
    
    CARRIER_GATEWAYS = {
        "AT&T": "txt.att.net",
        "T-Mobile": "tmomail.net",
        "Verizon": "vtext.com",
        "Sprint": "messaging.sprintpcs.com",
        "Cricket": "sms.cricketwireless.net",
        "Boost Mobile": "sms.myboostmobile.com",
        "Metro PCS": "mymetropcs.com",
        "U.S. Cellular": "email.uscc.net",
        "Tracfone": "mmst5.tracfone.com"
    }
    
    @classmethod
    def send_sms_via_email(cls, to_phone: str, carrier: str, message_body: str) -> Tuple[bool, str]:
        """
        Sends an SMS by emailing the carrier's SMS gateway.
        Requires knowing the carrier gateway domain. VERY UNRELIABLE.
        Uses the same email credentials as send_email.
        
        Args:
            to_phone (str): Recipient phone number
            carrier (str): Mobile carrier name
            message_body (str): SMS message
            
        Returns:
            Tuple[bool, str]: Success status and error message if any
        """
        if not EMAIL_SENDER or not EMAIL_PASSWORD:
            return False, "Email credentials not configured"
            
        if carrier not in cls.CARRIER_GATEWAYS:
            return False, f"Unknown carrier: {carrier}"
            
        # Remove any non-digit characters from phone number
        clean_phone = ''.join(filter(str.isdigit, to_phone))
        if not clean_phone:
            return False, "Invalid phone number"
            
        carrier_gateway = cls.CARRIER_GATEWAYS[carrier]
        to_address = f"{clean_phone}@{carrier_gateway}"
        
        try:
            # Create message
            message = EmailMessage()
            message["From"] = EMAIL_SENDER
            message["To"] = to_address
            message.set_content(message_body[:160])  # SMS has 160 character limit
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(message)
                
            return True, ""
        except Exception as e:
            logger.error(f"Failed to send SMS via email: {e}")
            return False, str(e)


class AppNotifier:
    """Handles in-app notifications."""
    
    @staticmethod
    def create_notification(username: str, notification_type: str, message: str) -> Dict[str, Any]:
        """
        Create an in-app notification.
        
        Args:
            username (str): Recipient username
            notification_type (str): Type of notification
            message (str): Notification message
            
        Returns:
            Dict[str, Any]: Notification data
        """
        from datetime import datetime
        
        return {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "type": notification_type,
            "message": message,
            "read": False
        }
