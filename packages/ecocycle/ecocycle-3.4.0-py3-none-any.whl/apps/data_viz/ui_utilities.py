"""
EcoCycle - Data Visualization UI Utilities
Provides UI utility functions for the data visualization modules with Rich UI support.
"""
import os
import time
import threading
import logging
import webbrowser
from typing import List, Dict, Any, Optional, Union, Tuple

# Check if Rich is available for enhanced UI
try:
    import rich
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.align import Align
    from rich.box import Box, DOUBLE, ROUNDED, HEAVY, SQUARE
    from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.tree import Tree
    from rich.columns import Columns
    from rich.style import Style
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.rule import Rule
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# Import utilities
import utils.ascii_art as ascii_art
from core.dependency import dependency_manager

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"
REPORT_DIR = "reports"


class UIUtilities:
    """Provides UI utility functions for the data visualization modules."""
    
    def __init__(self):
        """Initialize UI utilities."""
        # Auto-install visualization dependencies if needed
        success, failed = dependency_manager.ensure_feature('visualization', silent=False)
        self.visualization_available = success
        
        if not success and HAS_RICH:
            console.print(
                Panel(
                    f"[yellow]Some visualization packages failed to install: {', '.join(failed)}[/yellow]\n"
                    "[dim]Please install them manually with:[/dim] [blue]pip install " + " ".join(failed) + "[/blue]",
                    title="[yellow]Warning[/yellow]",
                    border_style="yellow",
                    box=ROUNDED,
                    padding=(1, 2)
                )
            )
    
    def viz_color(self, viz_type: str) -> str:
        """Return an appropriate color based on visualization type."""
        viz_type = viz_type.lower()
        if 'activity' in viz_type:
            return 'blue'
        elif 'carbon' in viz_type:
            return 'green'
        elif 'trip' in viz_type:
            return 'yellow'
        elif 'progress' in viz_type:
            return 'cyan'
        elif 'calorie' in viz_type:
            return 'red'
        else:
            return 'magenta'
    
    def display_viz_menu(self) -> None:
        """Display the visualization menu with Rich UI styling."""
        if HAS_RICH:
            # Create a layout for better visual organization
            layout = Layout()
            layout.split(
                Layout(name="header", size=3),
                Layout(name="main")
            )
            
            # Title header with styling
            header_title = Text("Data Visualization Dashboard", style="bold cyan")
            header_panel = Panel(
                Align.center(header_title),
                box=ROUNDED,
                border_style="blue",
                padding=(1, 2)
            )
            layout["header"].update(header_panel)
            console.print(layout["header"])
            
            # Create options table with colored categories
            options_table = Table(
                show_header=True,
                header_style="bold cyan",
                box=ROUNDED,
                border_style="blue",
                title="Select a Visualization Option",
                title_style="bold cyan"
            )
            
            options_table.add_column("#", style="dim", width=3)
            options_table.add_column("Visualization", style="bold cyan")
            options_table.add_column("Description", style="blue")
            
            # Add rows with visualization options and descriptions
            options_table.add_row("1", "[bold blue]🌟 Activity Summary[/bold blue]", 
                                "View key metrics and summary of your cycling activities")
            options_table.add_row("2", "[bold green]🚲 Trip History Analysis[/bold green]", 
                                "Analyze your cycling trips with detailed visualizations")
            options_table.add_row("3", "[bold green]🌱 Carbon Savings[/bold green]", 
                                "Visualize environmental impact and carbon savings")
            options_table.add_row("4", "[bold blue]📈 Progress Over Time[/bold blue]", 
                                "Track your cycling progress and improvements over time")
            options_table.add_row("5", "[bold purple]📊 Generate PDF Report[/bold purple]", 
                                "Create a comprehensive report with all visualizations")
            options_table.add_row("6", "[bold yellow]🖼️ Manage Visualizations[/bold yellow]", 
                                "View and manage saved visualizations and reports")
            options_table.add_row("7", "[bold cyan]📤 Export Data[/bold cyan]", 
                                "Export your cycling data to various formats")
            options_table.add_row("8", "[bold red]↩️ Return to Main Menu[/bold red]", 
                                "Exit data visualization and return to main menu")
            
            console.print(options_table)
        else:
            # ASCII art fallback
            ascii_art.display_section_header("Data Visualization Options")
            print("1. Activity Summary")
            print("2. Trip History Analysis")
            print("3. Carbon Savings Visualization")
            print("4. Progress Over Time")
            print("5. Generate PDF Report")
            print("6. Manage Visualizations")
            print("7. Export Data")
            print("8. Return to Main Menu")
    
    def get_menu_choice(self, prompt: str, options: List[str], default: str = "1") -> str:
        """Get a menu choice from the user with appropriate UI."""
        if HAS_RICH:
            return Prompt.ask(f"[bold]{prompt}[/bold]", choices=options, default=default)
        else:
            return input(f"\n{prompt} ({'/'.join(options)}): ") or default
    
    def display_error(self, message: str, title: str = "Error") -> None:
        """Display an error message with appropriate UI."""
        if HAS_RICH:
            error_panel = Panel(
                Text(message, style="bold red"),
                title=f"[bold red]{title}[/bold red]",
                border_style="red",
                box=HEAVY,
                padding=(1, 2)
            )
            console.print(error_panel)
        else:
            print(f"\n{title}: {message}")
    
    def display_success(self, message: str, title: str = "Success") -> None:
        """Display a success message with appropriate UI."""
        if HAS_RICH:
            success_panel = Panel(
                Text(message, style="bold green"),
                title=f"[bold green]{title}[/bold green]",
                border_style="green",
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(success_panel)
        else:
            print(f"\n{title}: {message}")
    
    def display_info(self, message: str, title: str = "Information", color: str = "blue") -> None:
        """Display an information message with appropriate UI."""
        if HAS_RICH:
            info_panel = Panel(
                Text(message),
                title=f"[bold {color}]{title}[/bold {color}]",
                border_style=color,
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(info_panel)
        else:
            print(f"\n{title}: {message}")
    
    def prompt_continue(self, message: str = "Press Enter to continue") -> None:
        """Display a continue prompt with appropriate UI."""
        if HAS_RICH:
            console.print(f"[bold cyan]{message}[/bold cyan]")
            input()
        else:
            input(f"\n{message}...")
    
    def show_progress(self, message: str, total: int = None) -> Union[Progress, None]:
        """Show a progress indicator with appropriate UI."""
        if HAS_RICH:
            progress = Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn(f"[bold blue]{message}[/bold blue]"),
                BarColumn(bar_width=40),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                expand=True
            )
            task_id = progress.add_task("Processing", total=total)
            return progress, task_id
        else:
            print(f"\n{message}...")
            return None, None
    
    def cleanup_temp_file(self, path: str, delay: int = 5) -> None:
        """Clean up a temporary file after a delay."""
        def delete_file():
            time.sleep(delay)
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.error(f"Error cleaning up temporary file: {e}")
        
        cleanup_thread = threading.Thread(target=delete_file)
        cleanup_thread.daemon = True
        cleanup_thread.start()
    
    def open_file_browser(self, filepath: str) -> bool:
        """Open a file in the default application."""
        try:
            if HAS_RICH:
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold blue]Opening file...[/bold blue]"),
                    expand=True
                ) as progress:
                    task = progress.add_task("Opening...", total=None)
                    webbrowser.open(f"file://{os.path.abspath(filepath)}")
                    time.sleep(1)  # Brief delay for visual effect
                console.print("[green]✓ File opened in default application[/green]")
            else:
                print("\nOpening file in default application...")
                webbrowser.open(f"file://{os.path.abspath(filepath)}")
                print("File opened.")
            return True
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            self.display_error(f"Could not open file: {str(e)}")
            return False
    
    def create_table(self, columns: List[Tuple[str, str]], title: str = "", 
                   box_style: str = "ROUNDED", border_style: str = "blue") -> Table:
        """Create a Rich table with specified columns and styling."""
        if not HAS_RICH:
            return None
            
        box_styles = {
            "ROUNDED": ROUNDED,
            "HEAVY": HEAVY,
            "DOUBLE": DOUBLE,
            "SQUARE": SQUARE
        }
        
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box_styles.get(box_style, ROUNDED),
            border_style=border_style,
            title=title,
            title_style=f"bold {border_style}" if border_style != "default" else "bold"
        )
        
        for col_name, col_style in columns:
            table.add_column(col_name, style=col_style)
            
        return table
