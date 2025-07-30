"""
EcoCycle - Notification UI Module
Provides UI components for the notification system.
"""
import logging
from typing import Dict, List, Any, Optional

# Import Rich for enhanced UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.prompt import Prompt, Confirm
    from rich import box
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Import tqdm for progress bars (fallback)
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Import utilities
import utils.ascii_art as ascii_art

logger = logging.getLogger(__name__)


class NotificationUI:
    """UI components for the notification system."""
    
    @classmethod
    def display_email_logs(cls, logs: List[Dict[str, Any]]) -> None:
        """
        Display email notification logs with Rich UI styling.
        
        Args:
            logs (List[Dict]): Email logs to display
        """
        if not logs:
            cls.print_message("No email notification logs found.", "yellow")
            return
            
        cls.print_header("Email Notification Logs")
        
        if HAS_RICH:
            table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            table.add_column("Timestamp", style="dim")
            table.add_column("Recipient")
            table.add_column("Subject")
            table.add_column("Status", style="bold")
            
            for log in logs:
                status_style = "green" if log.get("status") == "success" else "red"
                
                table.add_row(
                    log.get("timestamp", "N/A"),
                    log.get("to_email", "N/A"),
                    log.get("subject", "N/A"),
                    Text(log.get("status", "N/A"), style=status_style)
                )
            
            console.print(Panel(table, title="Email Logs", border_style="blue"))
        else:
            # ASCII art fallback
            print(ascii_art.section_header("Email Notification Logs"))
            print(f"{'Timestamp':<25} {'Recipient':<30} {'Subject':<40} {'Status':<10}")
            print("-" * 105)
            
            for log in logs:
                status = log.get("status", "N/A")
                status_formatted = f"✓ {status}" if status == "success" else f"✗ {status}"
                
                print(f"{log.get('timestamp', 'N/A'):<25} {log.get('to_email', 'N/A'):<30} "
                      f"{log.get('subject', 'N/A'):<40} {status_formatted:<10}")
            
            print("-" * 105)
            
    @classmethod
    def display_sms_logs(cls, logs: List[Dict[str, Any]]) -> None:
        """
        Display SMS notification logs with Rich UI styling.
        
        Args:
            logs (List[Dict]): SMS logs to display
        """
        if not logs:
            cls.print_message("No SMS notification logs found.", "yellow")
            return
            
        cls.print_header("SMS Notification Logs")
        
        if HAS_RICH:
            table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            table.add_column("Timestamp", style="dim")
            table.add_column("Recipient")
            table.add_column("Message")
            table.add_column("Status", style="bold")
            
            for log in logs:
                status_style = "green" if log.get("status") == "success" else "red"
                message = log.get("message", "")
                # Truncate message if too long
                message = message[:50] + "..." if len(message) > 50 else message
                
                table.add_row(
                    log.get("timestamp", "N/A"),
                    log.get("to_phone", "N/A"),
                    message,
                    Text(log.get("status", "N/A"), style=status_style)
                )
            
            console.print(Panel(table, title="SMS Logs", border_style="blue"))
        else:
            # ASCII art fallback
            print(ascii_art.section_header("SMS Notification Logs"))
            print(f"{'Timestamp':<25} {'Recipient':<20} {'Message':<50} {'Status':<10}")
            print("-" * 105)
            
            for log in logs:
                status = log.get("status", "N/A")
                status_formatted = f"✓ {status}" if status == "success" else f"✗ {status}"
                message = log.get("message", "")
                message = message[:50] + "..." if len(message) > 50 else message
                
                print(f"{log.get('timestamp', 'N/A'):<25} {log.get('to_phone', 'N/A'):<20} "
                      f"{message:<50} {status_formatted:<10}")
            
            print("-" * 105)
    
    @classmethod
    def display_app_logs(cls, logs: List[Dict[str, Any]]) -> None:
        """
        Display in-app notification logs with Rich UI styling.
        
        Args:
            logs (List[Dict]): App logs to display
        """
        if not logs:
            cls.print_message("No in-app notification logs found.", "yellow")
            return
            
        cls.print_header("In-App Notification Logs")
        
        if HAS_RICH:
            table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            table.add_column("Timestamp", style="dim")
            table.add_column("Type")
            table.add_column("Message")
            
            for log in logs:
                message = log.get("message", "")
                # Truncate message if too long
                message = message[:60] + "..." if len(message) > 60 else message
                
                table.add_row(
                    log.get("timestamp", "N/A"),
                    log.get("type", "N/A"),
                    message
                )
            
            console.print(Panel(table, title="In-App Logs", border_style="blue"))
        else:
            # ASCII art fallback
            print(ascii_art.section_header("In-App Notification Logs"))
            print(f"{'Timestamp':<25} {'Type':<20} {'Message':<60}")
            print("-" * 105)
            
            for log in logs:
                message = log.get("message", "")
                message = message[:60] + "..." if len(message) > 60 else message
                
                print(f"{log.get('timestamp', 'N/A'):<25} {log.get('type', 'N/A'):<20} {message:<60}")
            
            print("-" * 105)
    
    @classmethod
    def get_string_input(cls, prompt: str, default: str = "") -> str:
        """
        Get string input from user with Rich UI styling.
        
        Args:
            prompt (str): Input prompt
            default (str): Default value
            
        Returns:
            str: User input
        """
        if HAS_RICH:
            return Prompt.ask(prompt, default=default)
        else:
            return input(f"{prompt} [{default}]: ") or default
    
    @classmethod
    def get_boolean_input(cls, prompt: str, default: bool = False) -> bool:
        """
        Get boolean input from user with Rich UI styling.
        
        Args:
            prompt (str): Input prompt
            default (bool): Default value
            
        Returns:
            bool: User input
        """
        if HAS_RICH:
            return Confirm.ask(prompt, default=default)
        else:
            default_str = "Y/n" if default else "y/N"
            response = input(f"{prompt} [{default_str}]: ").strip().lower()
            if not response:
                return default
            return response[0] == 'y'
    
    @classmethod
    def print_header(cls, text: str) -> None:
        """
        Print a header with Rich UI styling.
        
        Args:
            text (str): Header text
        """
        if HAS_RICH:
            console.print(f"\n[bold blue]{text}[/bold blue]")
        else:
            print(f"\n{ascii_art.section_header(text)}")
    
    @classmethod
    def print_message(cls, message: str, color: str = "green") -> None:
        """
        Print a message with Rich UI styling.
        
        Args:
            message (str): Message to print
            color (str): Message color
        """
        if HAS_RICH:
            console.print(f"[{color}]{message}[/{color}]")
        else:
            print(message)
    
    @classmethod
    def create_progress(cls) -> Any:
        """
        Create a progress bar with Rich UI styling.
        
        Returns:
            Any: Progress bar object
        """
        if HAS_RICH:
            return Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[bold]{task.percentage:>3.0f}%"),
                TimeElapsedColumn()
            )
        elif TQDM_AVAILABLE:
            return tqdm
        else:
            return None
