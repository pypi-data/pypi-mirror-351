"""
EcoCycle - Data Visualization Base Module
Provides the core DataVisualization class that integrates all visualization features.
"""
import os
import logging

# Import modules
from .activity_summary import ActivitySummaryViz
from .trip_history import TripHistoryViz
from .carbon_savings import CarbonSavingsViz
from .progress_tracker import ProgressViz
from .report_generator import ReportGenerator
from .visualization_manager import VisualizationManager
from .data_exporter import DataExporter
from .ui_utilities import UIUtilities

# Import utilities
import utils.ascii_art as ascii_art

logger = logging.getLogger(__name__)

# Constants
VISUALIZATION_DIR = "visualizations"
REPORT_DIR = "reports"


class DataVisualization:
    """Data visualization features for EcoCycle (Modular Implementation)."""

    def __init__(self, user_manager=None, sheets_manager=None):
        """Initialize the data visualization module."""
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager
        
        # Create directories if they don't exist
        os.makedirs(VISUALIZATION_DIR, exist_ok=True)
        os.makedirs(REPORT_DIR, exist_ok=True)
        
        # Initialize UI utilities
        self.ui = UIUtilities()
        
        # Initialize sub-modules
        self.activity_summary = ActivitySummaryViz(self.user_manager, self.ui)
        self.trip_history = TripHistoryViz(self.user_manager, self.ui)
        self.carbon_savings = CarbonSavingsViz(self.user_manager, self.ui)
        self.progress_tracker = ProgressViz(self.user_manager, self.ui)
        self.report_generator = ReportGenerator(self.user_manager, self.ui, 
                                               self.activity_summary, 
                                               self.carbon_savings, 
                                               self.progress_tracker)
        self.viz_manager = VisualizationManager(self.user_manager, self.ui)
        self.data_exporter = DataExporter(self.user_manager, self.ui)

    def run_visualization(self):
        """Run the data visualization interactive interface."""
        ascii_art.clear_screen()
        ascii_art.display_header()
        
        # Display menu with Rich UI styling 
        self.ui.display_viz_menu()
        
        while True:
            choice = self.ui.get_menu_choice(
                prompt="Select a visualization option",
                options=["1", "2", "3", "4", "5", "6", "7", "8"],
                default="1"
            )
            
            if choice == "1":
                # Activity Summary
                self.activity_summary.show_activity_summary()
            elif choice == "2":
                # Trip History Analysis
                self.trip_history.analyze_trip_history()
            elif choice == "3":
                # Carbon Savings
                self.carbon_savings.visualize_carbon_savings()
            elif choice == "4":
                # Progress Over Time
                self.progress_tracker.show_progress_over_time()
            elif choice == "5":
                # Generate PDF Report
                self.report_generator.generate_pdf_report()
            elif choice == "6":
                # Manage Visualizations
                self.viz_manager.manage_visualizations()
            elif choice == "7":
                # Export Data
                self.data_exporter.export_data()
            elif choice == "8":
                # Return to Main Menu
                break
            
            # Clear screen after each operation
            ascii_art.clear_screen()
            ascii_art.display_header()
            self.ui.display_viz_menu()
