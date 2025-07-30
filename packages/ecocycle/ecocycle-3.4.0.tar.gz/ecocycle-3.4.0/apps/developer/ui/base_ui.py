"""
EcoCycle - Base UI Component
Common functionality shared across all developer UI components.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.layout import Layout
    from rich.live import Live
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None
    # Create dummy classes for when Rich is not available
    class Panel:
        @staticmethod
        def fit(*args, **kwargs):
            return None

    class Table:
        def __init__(self, *args, **kwargs):
            pass
        def add_column(self, *args, **kwargs):
            pass
        def add_row(self, *args, **kwargs):
            pass

    class Tree:
        def __init__(self, *args, **kwargs):
            pass
        def add(self, *args, **kwargs):
            return self

    class Prompt:
        @staticmethod
        def ask(*args, **kwargs):
            return kwargs.get('default', '')

    class Confirm:
        @staticmethod
        def ask(*args, **kwargs):
            return False

# Export the classes so they can be imported by other modules
__all__ = ['BaseUI', 'HAS_RICH', 'console', 'Panel', 'Table', 'Tree', 'Prompt', 'Confirm']

logger = logging.getLogger(__name__)


class BaseUI:
    """Base class for all developer UI components."""

    def __init__(self, developer_auth, developer_tools):
        """Initialize the base UI component."""
        self.developer_auth = developer_auth
        self.developer_tools = developer_tools

    def wait_for_user(self):
        """Wait for user input to continue."""
        if HAS_RICH and console:
            Prompt.ask("\nPress Enter to continue", default="")
        else:
            input("\nPress Enter to continue...")

    def confirm_action(self, message: str) -> bool:
        """Get user confirmation for potentially dangerous actions."""
        if HAS_RICH and console:
            return Confirm.ask(f"[yellow]{message}[/yellow]")
        else:
            response = input(f"{message} (y/N): ").strip().lower()
            return response == 'y'

    def display_operation_result(self, result: Dict[str, Any], operation: str):
        """Display the result of an operation."""
        if 'error' in result:
            if HAS_RICH and console:
                console.print(f"[red]❌ {operation} failed: {result['error']}[/red]")
            else:
                print(f"❌ {operation} failed: {result['error']}")
        elif result.get('success'):
            if HAS_RICH and console:
                console.print(f"[green]✅ {operation} completed successfully[/green]")
            else:
                print(f"✅ {operation} completed successfully")
        else:
            if HAS_RICH and console:
                console.print(f"[yellow]⚠️ {operation} completed with warnings[/yellow]")
            else:
                print(f"⚠️ {operation} completed with warnings")

    def display_error(self, error_message: str):
        """Display an error message."""
        if HAS_RICH and console:
            console.print(f"[red]Error: {error_message}[/red]")
        else:
            print(f"Error: {error_message}")

    def display_success(self, success_message: str):
        """Display a success message."""
        if HAS_RICH and console:
            console.print(f"[green]{success_message}[/green]")
        else:
            print(success_message)

    def display_warning(self, warning_message: str):
        """Display a warning message."""
        if HAS_RICH and console:
            console.print(f"[yellow]{warning_message}[/yellow]")
        else:
            print(warning_message)

    def display_info(self, info_message: str):
        """Display an info message."""
        if HAS_RICH and console:
            console.print(f"[cyan]{info_message}[/cyan]")
        else:
            print(info_message)

    def create_table(self, title: str, columns: list) -> Optional[Table]:
        """Create a Rich table with given title and columns."""
        if HAS_RICH:
            table = Table(title=title)
            for col_name, col_style in columns:
                table.add_column(col_name, style=col_style)
            return table
        return None

    def create_panel(self, content: str, title: str = "", border_style: str = "blue") -> Optional[Panel]:
        """Create a Rich panel with given content and title."""
        if HAS_RICH:
            if title:
                return Panel.fit(content, title=title, border_style=border_style)
            else:
                return Panel.fit(content, border_style=border_style)
        return None

    def show_status(self, message: str):
        """Show a status message with spinner if Rich is available."""
        if HAS_RICH and console:
            return console.status(f"[bold green]{message}")
        else:
            print(message)
            return None

    def get_user_choice(self, prompt: str, choices: list, default: str = "0") -> str:
        """Get user choice from a list of options."""
        if HAS_RICH and console:
            return Prompt.ask(prompt, choices=choices, default=default)
        else:
            choice = input(f"{prompt} ({'/'.join(choices)}) [{default}]: ").strip()
            return choice if choice in choices else default

    def get_user_input(self, prompt: str, default: str = "") -> str:
        """Get user input with optional default."""
        if HAS_RICH and console:
            return Prompt.ask(prompt, default=default)
        else:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default

    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp

    def truncate_text(self, text: str, max_length: int = 50) -> str:
        """Truncate text to maximum length with ellipsis."""
        # Handle None values
        if text is None:
            text = 'N/A'
        # Convert to string if not already
        text = str(text)

        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
