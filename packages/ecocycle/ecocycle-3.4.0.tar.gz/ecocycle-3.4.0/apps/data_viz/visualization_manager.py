"""
EcoCycle - Visualization Manager Module
Provides functionality to manage visualizations and media files.
"""
import os
import datetime
import time
import logging
import tempfile
import qrcode
from io import BytesIO
from typing import List, Dict, Any, Optional, Tuple

# Import utilities
import utils.ascii_art as ascii_art
from .ui_utilities import HAS_RICH, console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, HEAVY
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.rule import Rule
from rich.columns import Columns
from rich.console import Group

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"
REPORT_DIR = "reports"


class VisualizationManager:
    """Provides functionality to manage visualizations and media files."""
    
    def __init__(self, user_manager=None, ui=None):
        """Initialize the visualization manager."""
        self.user_manager = user_manager
        self.ui = ui
    
    def manage_visualizations(self):
        """List and manage user visualizations with option to delete."""
        ascii_art.clear_screen()
        ascii_art.display_header()
        
        # Use Rich UI if available, otherwise fallback to ASCII art
        if HAS_RICH:
            console.print(Panel.fit(
                "[bold yellow]🖼 Manage Visualizations[/bold yellow]", 
                border_style="yellow", 
                padding=(1, 2)
            ))
        else:
            ascii_art.display_section_header("🖼 Manage Visualizations")

        # Get user data
        user = self.user_manager.get_current_user()
        username = user.get('username')

        # Check if visualizations directory exists
        if not os.path.exists(VISUALIZATION_DIR):
            if HAS_RICH:
                error_panel = Panel(
                    "[bold red]No visualizations directory found.[/bold red]\n\n[dim]The directory will be created when you generate your first visualization.[/dim]",
                    title="[red]Error[/red]",
                    border_style="red",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(error_panel)
                console.print("[cyan]Press Enter to return to Data Visualization Menu[/cyan]")
                input()
            else:
                print("No visualizations directory found.")
                print("The directory will be created when you generate your first visualization.")
                input("\nPress Enter to continue...")
            return

        # Get all visualization files and PDF reports for the current user
        user_files = []
        user_file_types = {}  # Store file types (visualization or report)
        
        for file in os.listdir(VISUALIZATION_DIR):
            # Check for both PNG visualizations and PDF reports
            if (file.endswith(".png") or file.endswith(".pdf")) and username in file:
                user_files.append(file)
                # Mark file type for later reference
                if file.endswith(".png"):
                    user_file_types[file] = "visualization"
                else:
                    user_file_types[file] = "report"

        # Check if user has any files to manage
        if not user_files:
            if HAS_RICH:
                info_panel = Panel(
                    "[yellow]No visualizations or PDF reports found for your account.[/yellow]\n\n[dim]Generate visualizations or PDF reports using the various options in the Data Visualization menu.[/dim]",
                    title="[yellow]Info[/yellow]",
                    border_style="yellow",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(info_panel)
                console.print("[cyan]Press Enter to return to Data Visualization Menu[/cyan]")
                input()
            else:
                print("No visualizations or PDF reports found for your account.")
                print("Generate these using the various options in the Data Visualization menu.")
                input("\nPress Enter to continue...")
            return

        # Sort files by creation time (newest first)
        user_files.sort(reverse=True)

        while True:
            # Clear screen and display header
            ascii_art.clear_screen()
            ascii_art.display_header()
            
            # Check if files exist again (in case they were all deleted)
            if not user_files:
                if HAS_RICH:
                    info_panel = Panel(
                        "[yellow]No visualizations or PDF reports found for your account.[/yellow]\n\n[dim]Generate visualizations or PDF reports using the various options in the Data Visualization menu.[/dim]",
                        title="[yellow]Info[/yellow]",
                        border_style="yellow",
                        box=ROUNDED,
                        padding=(1, 2)
                    )
                    console.print(info_panel)
                    console.print("[cyan]Press Enter to return to Data Visualization Menu[/cyan]")
                    input()
                else:
                    print("No visualizations or PDF reports found for your account.")
                    print("Generate these using the various options in the Data Visualization menu.")
                    input("\nPress Enter to continue...")
                return

            # Sort files by creation time (newest first)
            user_files.sort(reverse=True)

            # Display gallery header
            if HAS_RICH:
                # Count file types for the subtitle
                viz_count = sum(1 for ft in user_file_types.values() if ft == "visualization")
                report_count = sum(1 for ft in user_file_types.values() if ft == "report")
                
                # Create a stylish gallery header
                title = Text()
                title.append("✨ ", style="bright_white")
                title.append("Your Media Gallery", style="bold yellow")
                title.append(" ✨", style="bright_white")
                
                header_panel = Panel(
                    Align.center(title),
                    box=ROUNDED,
                    border_style="yellow",
                    subtitle=f"[italic]{viz_count} visualizations and {report_count} PDF reports[/italic]"
                )
                console.print(header_panel)

                # Create a menu with file options
                console.print(Rule("Gallery Options", style="yellow"))
                console.print()
                
                # Generate file list with icons and type indicators
                file_panels = []
                for idx, file in enumerate(user_files, 1):
                    file_type = user_file_types.get(file, "unknown")
                    icon = "📊" if file_type == "visualization" else "📄"
                    color = "green" if file_type == "visualization" else "blue"
                    
                    # Get file creation date
                    try:
                        file_date = datetime.datetime.fromtimestamp(
                            os.path.getctime(os.path.join(VISUALIZATION_DIR, file))
                        ).strftime('%Y-%m-%d %H:%M')
                    except:
                        file_date = "Unknown date"
                    
                    file_panel = Panel(
                        Group(
                            Text(f"{icon} {file}", style=f"bold {color}"),
                            Text(f"Created: {file_date}", style="dim"),
                            Text(f"Type: {file_type.capitalize()}", style="dim")
                        ),
                        border_style=color,
                        box=ROUNDED,
                        padding=(1, 2),
                        title=f"[{color}]#{idx}[/{color}]"
                    )
                    file_panels.append(file_panel)
                
                # Display files in columns
                console.print(Columns(file_panels, equal=True, expand=True))
                
                # Options menu
                console.print(Rule("Actions", style="yellow"))
                console.print("[bold]Select an option:[/bold]")
                console.print("1. [green]View/Open[/green] a visualization or report")
                console.print("2. [red]Delete[/red] a visualization or report")
                console.print("3. [cyan]Share[/cyan] a visualization or report (QR code)")
                console.print("4. [red bold]Delete ALL[/red bold] visualizations and reports")
                console.print("5. [yellow]Return[/yellow] to Data Visualization Menu")
                
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"], default="1")
            else:
                # ASCII art for systems without Rich
                ascii_art.display_section_header("Your Media Gallery")
                
                # Display files with numbers
                for idx, file in enumerate(user_files, 1):
                    file_type = user_file_types.get(file, "unknown")
                    print(f"{idx}. {file} - {file_type.capitalize()}")
                
                print("\nOptions:")
                print("1. View/Open a visualization or report")
                print("2. Delete a visualization or report")
                print("3. Share a visualization or report (QR code)")
                print("4. Delete ALL visualizations and reports")
                print("5. Return to Data Visualization Menu")
                
                choice = input("\nSelect an option (1-5): ")
            
            # Handle user choice
            if choice == "1":  # View/Open
                if HAS_RICH:
                    file_num = IntPrompt.ask(
                        "Enter the number of the file to view/open",
                        default=1,
                        show_default=True
                    )
                    
                    if file_num < 1 or file_num > len(user_files):
                        console.print("[bold red]Invalid file number![/bold red]")
                        time.sleep(1)
                        continue
                else:
                    file_num = input("\nEnter the number of the file to view/open: ")
                    try:
                        file_num = int(file_num)
                        if file_num < 1 or file_num > len(user_files):
                            raise ValueError
                    except ValueError:
                        print("Invalid file number!")
                        time.sleep(1)
                        continue
                
                # Open the selected file
                selected_file = user_files[file_num - 1]
                file_path = os.path.join(VISUALIZATION_DIR, selected_file)
                
                try:
                    self.ui.open_file_browser(file_path)
                except Exception as e:
                    logger.error(f"Error opening file: {e}")
                    self.ui.display_error(f"Error opening file: {str(e)}")
                
                # Small delay to show success message
                time.sleep(1)
                
            elif choice == "2":  # Delete
                if HAS_RICH:
                    file_num = int(Prompt.ask(
                        "Enter the number of the file to delete",
                        default="1",
                        show_default=True
                    ))
                    
                    if file_num < 1 or file_num > len(user_files):
                        console.print("[bold red]Invalid file number![/bold red]")
                        time.sleep(1)
                        continue
                        
                    selected_file = user_files[file_num - 1]
                    
                    # Confirm deletion
                    if Confirm.ask(f"[bold red]Are you sure you want to delete[/bold red] [bold yellow]{selected_file}[/bold yellow]?"):
                        try:
                            file_path = os.path.join(VISUALIZATION_DIR, selected_file)
                            os.remove(file_path)
                            
                            # Remove from lists
                            del user_file_types[selected_file]
                            user_files.remove(selected_file)
                            
                            console.print(f"[bold green]✓ Successfully deleted:[/bold green] {selected_file}")
                            time.sleep(1)
                        except Exception as e:
                            logger.error(f"Error deleting file: {e}")
                            console.print(f"[bold red]Error deleting file:[/bold red] {str(e)}")
                            time.sleep(2)
                else:
                    file_num = input("\nEnter the number of the file to delete: ")
                    try:
                        file_num = int(file_num)
                        if file_num < 1 or file_num > len(user_files):
                            raise ValueError
                    except ValueError:
                        print("Invalid file number!")
                        time.sleep(1)
                        continue
                    
                    selected_file = user_files[file_num - 1]
                    
                    # Confirm deletion
                    confirm = input(f"\nAre you sure you want to delete {selected_file}? (y/n): ")
                    if confirm.lower() == 'y':
                        try:
                            file_path = os.path.join(VISUALIZATION_DIR, selected_file)
                            os.remove(file_path)
                            
                            # Remove from lists
                            del user_file_types[selected_file]
                            user_files.remove(selected_file)
                            
                            print(f"\nSuccessfully deleted: {selected_file}")
                            time.sleep(1)
                        except Exception as e:
                            logger.error(f"Error deleting file: {e}")
                            print(f"Error deleting file: {str(e)}")
                            time.sleep(2)
            
            elif choice == "3":  # Share (QR code)
                if HAS_RICH:
                    file_num = IntPrompt.ask(
                        "Enter the number of the file to share",
                        default=1,
                        show_default=True
                    )
                    
                    if file_num < 1 or file_num > len(user_files):
                        console.print("[bold red]Invalid file number![/bold red]")
                        time.sleep(1)
                        continue
                else:
                    file_num = input("\nEnter the number of the file to share: ")
                    try:
                        file_num = int(file_num)
                        if file_num < 1 or file_num > len(user_files):
                            raise ValueError
                    except ValueError:
                        print("Invalid file number!")
                        time.sleep(1)
                        continue
                
                selected_file = user_files[file_num - 1]
                file_path = os.path.join(VISUALIZATION_DIR, selected_file)
                
                # Generate a temporary QR code for the file
                try:
                    # Create a temporary file for the QR code
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.close()
                    qr_path = temp_file.name
                    
                    # Get absolute path for the file
                    abs_path = os.path.abspath(file_path)
                    
                    # Generate QR code
                    if HAS_RICH:
                        with Progress(
                            SpinnerColumn(spinner_name="dots"),
                            TextColumn("[bold blue]Generating QR code...[/bold blue]"),
                            expand=True
                        ) as progress:
                            task = progress.add_task("Generating", total=None)
                            
                            # Create QR code with the file:// URL
                            qr = qrcode.QRCode(
                                version=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L,
                                box_size=10,
                                border=4,
                            )
                            qr.add_data(f"file://{abs_path}")
                            qr.make(fit=True)
                            
                            img = qr.make_image(fill_color="black", back_color="white")
                            img.save(qr_path)
                        
                        # Display success message
                        console.print("[bold green]✓ QR code generated successfully![/bold green]")
                        
                        # Open the QR code
                        if Confirm.ask("[bold]View the QR code?[/bold]", default=True):
                            self.ui.open_file_browser(qr_path)
                    else:
                        print("\nGenerating QR code...")
                        
                        # Create QR code with the file:// URL
                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr.add_data(f"file://{abs_path}")
                        qr.make(fit=True)
                        
                        img = qr.make_image(fill_color="black", back_color="white")
                        img.save(qr_path)
                        
                        # Display success message
                        print("\nQR code generated successfully!")
                        
                        # Ask to open the QR code
                        view = input("\nView the QR code? (y/n): ")
                        if view.lower() == 'y':
                            try:
                                self.ui.open_file_browser(qr_path)
                            except Exception as e:
                                logger.error(f"Error opening QR code: {e}")
                                print(f"Error opening QR code: {str(e)}")
                    
                    # Delete QR code file after delay (cleanup)
                    self.ui.cleanup_temp_file(qr_path)
                    
                except Exception as e:
                    logger.error(f"Error generating QR code: {e}")
                    if HAS_RICH:
                        console.print(f"[bold red]Error generating QR code:[/bold red] {str(e)}")
                    else:
                        print(f"Error generating QR code: {str(e)}")
                    time.sleep(2)
            
            elif choice == "4":  # Delete ALL
                # Confirm deletion of all files
                if HAS_RICH:
                    # Count the files that will be deleted
                    confirm_message = f"[bold red]Are you sure you want to delete ALL[/bold red] [bold yellow]{len(user_files)} visualizations and reports[/bold yellow]? This cannot be undone."
                    
                    if Confirm.ask(confirm_message):
                        try:
                            deleted_count = 0
                            
                            # Show progress
                            with Progress(
                                SpinnerColumn(spinner_name="dots"),
                                TextColumn("[bold red]Deleting files...[/bold red]"),
                                BarColumn(),
                                TextColumn("{task.percentage:.0f}%"),
                                expand=True
                            ) as progress:
                                delete_task = progress.add_task("Deleting", total=len(user_files))
                                
                                # Delete all user files
                                for file in user_files.copy():
                                    file_path = os.path.join(VISUALIZATION_DIR, file)
                                    os.remove(file_path)
                                    
                                    # Remove from data structures
                                    deleted_count += 1
                                    progress.update(delete_task, advance=1)
                                    
                                # Clear the lists
                                user_files.clear()
                                user_file_types.clear()
                            
                            # Show success message
                            success_panel = Panel(
                                f"[bold green]✓ Successfully deleted {deleted_count} files[/bold green]",
                                border_style="green",
                                box=ROUNDED,
                                padding=(1, 2)
                            )
                            console.print(success_panel)
                            time.sleep(2)
                            
                        except Exception as e:
                            logger.error(f"Error deleting all files: {e}")
                            console.print(f"[bold red]Error deleting files:[/bold red] {str(e)}")
                            time.sleep(2)
                else:
                    # ASCII art version
                    confirm = input(f"\nAre you sure you want to delete ALL {len(user_files)} visualizations and reports? This cannot be undone. (y/n): ")
                    if confirm.lower() == 'y':
                        try:
                            deleted_count = 0
                            print("\nDeleting files...")
                            
                            # Delete all user files
                            for file in user_files.copy():
                                file_path = os.path.join(VISUALIZATION_DIR, file)
                                os.remove(file_path)
                                deleted_count += 1
                            
                            # Clear the lists
                            user_files.clear()
                            user_file_types.clear()
                            
                            # Show success message
                            print(f"\nSuccessfully deleted {deleted_count} files")
                            time.sleep(2)
                            
                        except Exception as e:
                            logger.error(f"Error deleting all files: {e}")
                            print(f"Error deleting files: {str(e)}")
                            time.sleep(2)
                            
            elif choice == "5":  # Return to menu
                break
            
            # Small delay before refreshing
            time.sleep(0.5)
