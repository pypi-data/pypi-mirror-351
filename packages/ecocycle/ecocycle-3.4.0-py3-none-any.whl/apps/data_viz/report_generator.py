"""
EcoCycle - Report Generator Module
Provides functionality to generate comprehensive PDF reports with visualization data.
"""
import os
import time
import datetime
import logging
import tempfile
from typing import Dict, List, Any, Optional, Tuple

# Import utilities
import utils.ascii_art as ascii_art
from .ui_utilities import HAS_RICH, console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.layout import Layout
from rich.table import Table
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Check if FPDF is available for PDF generation
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"
REPORT_DIR = "reports"


class ReportGenerator:
    """Provides functionality for generating comprehensive PDF reports."""
    
    def __init__(self, user_manager=None, ui=None, activity_viz=None, carbon_viz=None, progress_viz=None):
        """Initialize the report generator module."""
        self.user_manager = user_manager
        self.ui = ui
        self.activity_viz = activity_viz
        self.carbon_viz = carbon_viz
        self.progress_viz = progress_viz
        
        # Create report directory if it doesn't exist
        os.makedirs(REPORT_DIR, exist_ok=True)
    
    def generate_pdf_report(self):
        """Generate a comprehensive PDF report with all visualizations."""
        ascii_art.clear_screen()
        ascii_art.display_header()
        
        # Use Rich UI if available
        if HAS_RICH:
            # Create a layout for the header
            layout = Layout()
            layout.split(
                Layout(name="header", size=3),
                Layout(name="main")
            )
            
            # Create a stylish header
            header_title = Text("Generate PDF Report", style="bold magenta")
            header_panel = Panel(
                Align.center(header_title),
                box=DOUBLE,
                border_style="magenta",
                padding=(1, 2)
            )
            layout["header"].update(header_panel)
            
            # Display the header
            console.print(layout["header"])
            
            # Add descriptive panel
            report_description = Panel(
                "Generate a comprehensive PDF report with all your cycling visualizations and statistics.",
                title="PDF Report Generator",
                border_style="magenta",
                box=ROUNDED,
                padding=(1, 2)
            )
            console.print(report_description)
        else:
            ascii_art.display_section_header("Generate PDF Report")
            print("Generate a comprehensive PDF report with all your cycling visualizations and statistics.")
        
        # Check if PDF generation is available
        if not PDF_AVAILABLE:
            # Try to install FPDF automatically
            from core.dependency import dependency_manager
            success, failed = dependency_manager.ensure_feature('pdf', silent=False)
            
            if not success:
                if HAS_RICH:
                    error_panel = Panel(
                        Text.assemble(
                            ("PDF generation requires the FPDF package.\n\n", "bold red"),
                            ("The package could not be installed automatically.\n", "yellow"),
                            ("Please install it manually with: ", "white"),
                            ("pip install fpdf", "bold cyan")
                        ),
                        title="[bold red]PDF Generation Not Available[/bold red]",
                        border_style="red",
                        box=HEAVY,
                        padding=(1, 2)
                    )
                    console.print(error_panel)
                    self.ui.prompt_continue()
                else:
                    print("\nPDF generation requires the FPDF package.")
                    print("Please install it manually with: pip install fpdf")
                    input("\nPress Enter to continue...")
                return
            else:
                # Import FPDF after installation
                from fpdf import FPDF
                # Set the module-level variable
                globals()['PDF_AVAILABLE'] = True
        
        # Get user data
        user = self.user_manager.get_current_user()
        username = user.get('username')
        
        # Get user stats
        stats = user.get('stats', {})
        trips = stats.get('trips', [])
        
        # Check if user has any trips
        if not trips:
            if HAS_RICH:
                no_data_panel = Panel(
                    Text.assemble(
                        ("No cycling data available for PDF report!\n\n", "bold red"),
                        ("You need to log some cycling trips before generating a report.\n", "yellow"),
                        ("Use the 'Log New Trip' feature from the main menu to get started.", "italic cyan")
                    ),
                    box=HEAVY,
                    border_style="yellow",
                    title="[bold red]No Report Data[/bold red]",
                    title_align="center",
                    padding=(1, 2)
                )
                console.print(Align.center(no_data_panel))
                
                # Prompt to return
                self.ui.prompt_continue("Press Enter to return to the visualization menu")
                return
            else:
                print("\nNo cycling data available for PDF report.")
                print("You need to log some cycling trips before generating a report.")
                input("\nPress Enter to continue...")
                return
        
        try:
            # Generate visualizations for the report
            if HAS_RICH:
                # Show progress with detailed steps
                with Progress(
                    SpinnerColumn(spinner_name="dots"),
                    TextColumn("[bold magenta]Generating PDF report...[/bold magenta]"),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    expand=True
                ) as progress:
                    # Setup main task and steps
                    main_task = progress.add_task("Generating report", total=100)
                    
                    # Step 1: Generate temp directory for visualizations
                    progress.update(main_task, advance=5, description="Creating temporary files")
                    temp_dir = tempfile.mkdtemp()
                    
                    # Step 2: Generate visualizations
                    progress.update(main_task, advance=5, description="Generating visualizations")
                    
                    # Generate activity summary visualization
                    progress.update(main_task, advance=15, description="Creating activity summary")
                    activity_path = os.path.join(temp_dir, "activity_summary.png")
                    activity_generated = self.activity_viz.generate_activity_summary(user, activity_path)
                    
                    # Generate carbon savings visualization
                    progress.update(main_task, advance=15, description="Creating carbon savings chart")
                    carbon_path = os.path.join(temp_dir, "carbon_savings.png")
                    carbon_generated = self.carbon_viz.generate_carbon_visualization(user, carbon_path)
                    
                    # Generate progress visualization
                    progress.update(main_task, advance=15, description="Creating progress chart")
                    progress_path = os.path.join(temp_dir, "progress.png")
                    progress_generated = self.progress_viz.generate_progress_visualization(user, progress_path)
                    
                    # Step 3: Create PDF document
                    progress.update(main_task, advance=10, description="Creating PDF document")
                    
                    # Create timestamp for the filename
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    pdf_filename = os.path.join(REPORT_DIR, f"cycling_report_{username}_{timestamp}.pdf")
                    
                    # Check if PDF generation is available
                    if not PDF_AVAILABLE:
                        progress.update(main_task, description="Error: Missing dependency")
                        error_msg = "The fpdf package is required for PDF generation. Please install it with 'pip install fpdf'."
                        logger.error(error_msg)
                        raise ImportError(error_msg)
                    
                    # Create PDF object - explicitly import FPDF to avoid variable scope issues
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    
                    # Step 4: Add content to PDF
                    progress.update(main_task, advance=5, description="Adding title page")
                    
                    # Add title page
                    pdf.set_font('Arial', 'B', 24)
                    pdf.cell(0, 20, 'EcoCycle Activity Report', ln=True, align='C')
                    pdf.ln(10)
                    
                    pdf.set_font('Arial', 'I', 14)
                    pdf.cell(0, 10, f"Generated for: {user.get('name', username)}", ln=True, align='C')
                    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
                    pdf.ln(10)
                    
                    # Add profile summary
                    progress.update(main_task, advance=5, description="Adding profile summary")
                    
                    pdf.set_font('Arial', 'B', 18)
                    pdf.cell(0, 15, 'Profile Summary', ln=True)
                    pdf.ln(5)
                    
                    # Create profile summary table
                    pdf.set_font('Arial', '', 12)
                    pdf.set_fill_color(240, 240, 240)
                    
                    # Calculate totals
                    total_trips = len(trips)
                    total_distance = sum(float(trip.get('distance', 0)) for trip in trips)
                    total_duration = sum(float(trip.get('duration', 0)) for trip in trips)
                    total_carbon = sum(float(trip.get('carbon_saved', 0)) for trip in trips)
                    total_calories = sum(float(trip.get('calories_burned', 0)) for trip in trips)
                    
                    # Add profile data
                    pdf.cell(60, 10, 'Total Trips:', 1, 0, 'L', 1)
                    pdf.cell(0, 10, f"{total_trips}", 1, 1, 'L')
                    
                    pdf.cell(60, 10, 'Total Distance:', 1, 0, 'L', 1)
                    pdf.cell(0, 10, f"{total_distance:.2f} km", 1, 1, 'L')
                    
                    pdf.cell(60, 10, 'Total Duration:', 1, 0, 'L', 1)
                    pdf.cell(0, 10, f"{total_duration:.0f} minutes", 1, 1, 'L')
                    
                    pdf.cell(60, 10, 'Total Carbon Saved:', 1, 0, 'L', 1)
                    pdf.cell(0, 10, f"{total_carbon:.2f} kg", 1, 1, 'L')
                    
                    pdf.cell(60, 10, 'Total Calories Burned:', 1, 0, 'L', 1)
                    pdf.cell(0, 10, f"{total_calories:.0f} calories", 1, 1, 'L')
                    
                    pdf.ln(10)
                    
                    # Add activity summary visualization
                    progress.update(main_task, advance=5, description="Adding activity visualization")
                    if activity_generated:
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 18)
                        pdf.cell(0, 15, 'Activity Summary', ln=True)
                        pdf.image(activity_path, x=10, y=30, w=190)
                    
                    # Add carbon savings visualization
                    progress.update(main_task, advance=5, description="Adding carbon visualization")
                    if carbon_generated:
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 18)
                        pdf.cell(0, 15, 'Carbon Savings', ln=True)
                        pdf.image(carbon_path, x=10, y=30, w=190)
                    
                    # Add progress visualization
                    progress.update(main_task, advance=5, description="Adding progress visualization")
                    if progress_generated:
                        pdf.add_page()
                        pdf.set_font('Arial', 'B', 18)
                        pdf.cell(0, 15, 'Progress Over Time', ln=True)
                        pdf.image(progress_path, x=10, y=30, w=190)
                    
                    # Add recent trips table
                    progress.update(main_task, advance=5, description="Adding trip history")
                    
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 18)
                    pdf.cell(0, 15, 'Recent Trips', ln=True)
                    pdf.ln(5)
                    
                    # Create table header
                    pdf.set_font('Arial', 'B', 12)
                    pdf.set_fill_color(200, 200, 200)
                    pdf.cell(30, 10, 'Date', 1, 0, 'C', 1)
                    pdf.cell(30, 10, 'Distance (km)', 1, 0, 'C', 1)
                    pdf.cell(35, 10, 'Duration (min)', 1, 0, 'C', 1)
                    pdf.cell(35, 10, 'Carbon (kg)', 1, 0, 'C', 1)
                    pdf.cell(0, 10, 'Calories', 1, 1, 'C', 1)
                    
                    # Add recent trips (up to 10)
                    pdf.set_font('Arial', '', 12)
                    sorted_trips = sorted(trips, key=lambda x: x.get('date', ''), reverse=True)
                    display_count = min(10, len(sorted_trips))
                    
                    for i in range(display_count):
                        trip = sorted_trips[i]
                        pdf.cell(30, 10, trip.get('date', ''), 1, 0, 'C')
                        pdf.cell(30, 10, f"{float(trip.get('distance', 0)):.1f}", 1, 0, 'C')
                        pdf.cell(35, 10, f"{float(trip.get('duration', 0)):.0f}", 1, 0, 'C')
                        pdf.cell(35, 10, f"{float(trip.get('carbon_saved', 0)):.2f}", 1, 0, 'C')
                        pdf.cell(0, 10, f"{float(trip.get('calories_burned', 0)):.0f}", 1, 1, 'C')
                    
                    # Save PDF file
                    progress.update(main_task, advance=5, description="Saving PDF report")
                    pdf.output(pdf_filename)
                    
                    # Clean up temporary files
                    progress.update(main_task, description="Cleaning up temporary files")
                    try:
                        if os.path.exists(activity_path):
                            os.remove(activity_path)
                        if os.path.exists(carbon_path):
                            os.remove(carbon_path)
                        if os.path.exists(progress_path):
                            os.remove(progress_path)
                        os.rmdir(temp_dir)
                    except Exception as e:
                        logger.warning(f"Error cleaning up temporary files: {e}")
                    
                    # Complete the progress bar
                    progress.update(main_task, completed=100, description="PDF report completed")
                
                # Show success message
                success_panel = Panel(
                    Text.assemble(
                        ("PDF report successfully generated!\n\n", "bold green"),
                        ("File saved as:\n", "white"),
                        (f"{pdf_filename}", "bold cyan")
                    ),
                    title="[bold green]Report Generation Complete[/bold green]",
                    border_style="green",
                    box=ROUNDED,
                    padding=(1, 2)
                )
                console.print(success_panel)
                
                
                pdf.set_font('Arial', 'I', 14)
                pdf.cell(0, 10, f"Generated for: {user.get('name', username)}", ln=True, align='C')
                pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
                pdf.ln(10)
                
                # Add profile summary
                pdf.set_font('Arial', 'B', 18)
                pdf.cell(0, 15, 'Profile Summary', ln=True)
                pdf.ln(5)
                
                # Create profile summary table
                pdf.set_font('Arial', '', 12)
                pdf.set_fill_color(240, 240, 240)
                
                # Calculate totals
                total_trips = len(trips)
                total_distance = sum(float(trip.get('distance', 0)) for trip in trips)
                total_duration = sum(float(trip.get('duration', 0)) for trip in trips)
                total_carbon = sum(float(trip.get('carbon_saved', 0)) for trip in trips)
                total_calories = sum(float(trip.get('calories_burned', 0)) for trip in trips)
                
                # Add profile data
                pdf.cell(60, 10, 'Total Trips:', 1, 0, 'L', 1)
                pdf.cell(0, 10, f"{total_trips}", 1, 1, 'L')
                
                pdf.cell(60, 10, 'Total Distance:', 1, 0, 'L', 1)
                pdf.cell(0, 10, f"{total_distance:.2f} km", 1, 1, 'L')
                
                pdf.cell(60, 10, 'Total Duration:', 1, 0, 'L', 1)
                pdf.cell(0, 10, f"{total_duration:.0f} minutes", 1, 1, 'L')
                
                pdf.cell(60, 10, 'Total Carbon Saved:', 1, 0, 'L', 1)
                pdf.cell(0, 10, f"{total_carbon:.2f} kg", 1, 1, 'L')
                
                pdf.cell(60, 10, 'Total Calories Burned:', 1, 0, 'L', 1)
                pdf.cell(0, 10, f"{total_calories:.0f} calories", 1, 1, 'L')
                
                pdf.ln(10)
                
                # Add activity summary visualization
                if activity_generated:
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 18)
                    pdf.cell(0, 15, 'Activity Summary', ln=True)
                    pdf.image(activity_path, x=10, y=30, w=190)
                
                # Add carbon savings visualization
                if carbon_generated:
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 18)
                    pdf.cell(0, 15, 'Carbon Savings', ln=True)
                    pdf.image(carbon_path, x=10, y=30, w=190)
                
                # Add progress visualization
                if progress_generated:
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 18)
                    pdf.cell(0, 15, 'Progress Over Time', ln=True)
                    pdf.image(progress_path, x=10, y=30, w=190)
                
                # Add recent trips table
                pdf.add_page()
                pdf.set_font('Arial', 'B', 18)
                pdf.cell(0, 15, 'Recent Trips', ln=True)
                pdf.ln(5)
                
                # Create table header
                pdf.set_font('Arial', 'B', 12)
                pdf.set_fill_color(200, 200, 200)
                pdf.cell(30, 10, 'Date', 1, 0, 'C', 1)
                pdf.cell(30, 10, 'Distance (km)', 1, 0, 'C', 1)
                pdf.cell(35, 10, 'Duration (min)', 1, 0, 'C', 1)
                pdf.cell(35, 10, 'Carbon (kg)', 1, 0, 'C', 1)
                pdf.cell(0, 10, 'Calories', 1, 1, 'C', 1)
                
                # Add recent trips (up to 10)
                pdf.set_font('Arial', '', 12)
                sorted_trips = sorted(trips, key=lambda x: x.get('date', ''), reverse=True)
                display_count = min(10, len(sorted_trips))
                
                for i in range(display_count):
                    trip = sorted_trips[i]
                    pdf.cell(30, 10, trip.get('date', ''), 1, 0, 'C')
                    pdf.cell(30, 10, f"{float(trip.get('distance', 0)):.1f}", 1, 0, 'C')
                    pdf.cell(35, 10, f"{float(trip.get('duration', 0)):.0f}", 1, 0, 'C')
                    pdf.cell(35, 10, f"{float(trip.get('carbon_saved', 0)):.2f}", 1, 0, 'C')
                    pdf.cell(0, 10, f"{float(trip.get('calories_burned', 0)):.0f}", 1, 1, 'C')
                
                # Save PDF file
                print("Saving PDF report...")
                pdf.output(pdf_filename)
                
                # Clean up temporary files
                try:
                    if os.path.exists(activity_path):
                        os.remove(activity_path)
                    if os.path.exists(carbon_path):
                        os.remove(carbon_path)
                    if os.path.exists(progress_path):
                        os.remove(progress_path)
                    os.rmdir(temp_dir)
                except Exception as e:
                    logger.warning(f"Error cleaning up temporary files: {e}")
                
                # Show success message
                print(f"\nPDF report successfully generated!")
                print(f"File saved as: {pdf_filename}")
                
                # Ask if user wants to open the PDF
                open_choice = input("\nOpen PDF report? (y/n): ")
                if open_choice.lower() == 'y':
                    self.ui.open_file_browser(pdf_filename)
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            self.ui.display_error(f"Error generating PDF report: {str(e)}")
        
        # Final prompt to return to menu
        self.ui.prompt_continue()
