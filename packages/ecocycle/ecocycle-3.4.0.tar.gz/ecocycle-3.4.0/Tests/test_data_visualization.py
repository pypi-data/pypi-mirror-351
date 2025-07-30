"""
Test module for data_visualization.py
"""
import os
import sys
import unittest
from unittest import mock
import tempfile
import json

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import apps.data_visualization

class TestDataVisualization(unittest.TestCase):
    """Test cases for data_visualization module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock user_manager and sheets_manager
        self.mock_user_manager = mock.MagicMock()
        self.mock_sheets_manager = mock.MagicMock()
        
        # Create a DataVisualization instance for testing
        self.data_viz = data_visualization.DataVisualization(
            user_manager=self.mock_user_manager,
            sheets_manager=self.mock_sheets_manager
        )
        
        # Sample user data for testing
        self.sample_user = {
            'username': 'test_user',
            'trips': [
                {
                    'date': '2023-01-01',
                    'distance': 10.5,
                    'duration': 45,
                    'carbon_saved': 2.0,
                    'route_type': 'commute'
                },
                {
                    'date': '2023-01-02',
                    'distance': 15.2,
                    'duration': 60,
                    'carbon_saved': 2.9,
                    'route_type': 'leisure'
                },
                {
                    'date': '2023-01-03',
                    'distance': 8.7,
                    'duration': 35,
                    'carbon_saved': 1.7,
                    'route_type': 'errand'
                }
            ],
            'stats': {
                'total_distance': 34.4,
                'total_duration': 140,
                'total_carbon_saved': 6.6,
                'total_trips': 3
            }
        }
        
        # Set up mock for get_current_user
        self.mock_user_manager.get_current_user.return_value = self.sample_user
        
        # Create a temporary directory for test outputs
        self.test_output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for filename in os.listdir(self.test_output_dir):
            os.remove(os.path.join(self.test_output_dir, filename))
        os.rmdir(self.test_output_dir)
    
    def test_initialization(self):
        """Test initialization of DataVisualization class."""
        # Verify the instance is created correctly
        self.assertIsInstance(self.data_viz, data_visualization.DataVisualization)
        
        # Verify the user_manager and sheets_manager are set
        self.assertEqual(self.data_viz.user_manager, self.mock_user_manager)
        self.assertEqual(self.data_viz.sheets_manager, self.mock_sheets_manager)
    
    @mock.patch('data_visualization.input', return_value='1')
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', True)
    @mock.patch('data_visualization.plt')
    def test_show_activity_summary(self, mock_plt, mock_input):
        """Test activity summary visualization."""
        # Mock the plt.savefig to avoid actual file creation
        mock_plt.savefig = mock.MagicMock()
        
        # Call the method
        self.data_viz.show_activity_summary()
        
        # Verify plt.savefig was called (indicating a visualization was created)
        mock_plt.savefig.assert_called()
        
        # Verify user_manager.get_current_user was called
        self.mock_user_manager.get_current_user.assert_called()
    
    @mock.patch('data_visualization.input', return_value='1')
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', False)
    def test_show_activity_summary_no_visualization(self, mock_input):
        """Test activity summary when visualization is not available."""
        # Capture stdout to verify error message
        with mock.patch('sys.stdout', new=mock.StringIO()) as fake_stdout:
            self.data_viz.show_activity_summary()
            output = fake_stdout.getvalue()
            
            # Verify error message about visualization not being available
            self.assertIn("visualization dependencies", output.lower())
    
    @mock.patch('data_visualization.input', side_effect=['invalid', '1'])
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', True)
    @mock.patch('data_visualization.plt')
    def test_show_activity_summary_invalid_input(self, mock_plt, mock_input):
        """Test activity summary with invalid input."""
        # Mock the plt.savefig to avoid actual file creation
        mock_plt.savefig = mock.MagicMock()
        
        # Call the method
        self.data_viz.show_activity_summary()
        
        # Verify plt.savefig was called (indicating a visualization was created)
        mock_plt.savefig.assert_called()
        
        # Verify input was called twice (once for invalid input, once for valid)
        self.assertEqual(mock_input.call_count, 2)
    
    @mock.patch('data_visualization.input', return_value='1')
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', True)
    @mock.patch('data_visualization.plt')
    def test_analyze_trip_history(self, mock_plt, mock_input):
        """Test trip history analysis visualization."""
        # Mock the plt.savefig to avoid actual file creation
        mock_plt.savefig = mock.MagicMock()
        
        # Call the method
        self.data_viz.analyze_trip_history()
        
        # Verify plt.savefig was called (indicating a visualization was created)
        mock_plt.savefig.assert_called()
    
    @mock.patch('data_visualization.input', return_value='1')
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', True)
    @mock.patch('data_visualization.plt')
    def test_visualize_carbon_savings(self, mock_plt, mock_input):
        """Test carbon savings visualization."""
        # Mock the plt.savefig to avoid actual file creation
        mock_plt.savefig = mock.MagicMock()
        
        # Call the method
        self.data_viz.visualize_carbon_savings()
        
        # Verify plt.savefig was called (indicating a visualization was created)
        mock_plt.savefig.assert_called()
    
    @mock.patch('data_visualization.input', return_value='1')
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', True)
    @mock.patch('data_visualization.plt')
    def test_show_progress_over_time(self, mock_plt, mock_input):
        """Test progress over time visualization."""
        # Mock the plt.savefig to avoid actual file creation
        mock_plt.savefig = mock.MagicMock()
        
        # Call the method
        self.data_viz.show_progress_over_time()
        
        # Verify plt.savefig was called (indicating a visualization was created)
        mock_plt.savefig.assert_called()
    
    @mock.patch('data_visualization.input', return_value='')
    @mock.patch('data_visualization.PDF_AVAILABLE', True)
    @mock.patch('data_visualization.FPDF')
    def test_generate_pdf_report(self, mock_fpdf, mock_input):
        """Test PDF report generation."""
        # Mock FPDF instance
        mock_pdf_instance = mock.MagicMock()
        mock_fpdf.return_value = mock_pdf_instance
        
        # Call the method
        self.data_viz.generate_pdf_report()
        
        # Verify FPDF was instantiated
        mock_fpdf.assert_called()
        
        # Verify output method was called (indicating PDF was created)
        mock_pdf_instance.output.assert_called()
    
    @mock.patch('data_visualization.input', return_value='')
    @mock.patch('data_visualization.PDF_AVAILABLE', False)
    def test_generate_pdf_report_no_pdf(self, mock_input):
        """Test PDF report generation when PDF is not available."""
        # Capture stdout to verify error message
        with mock.patch('sys.stdout', new=mock.StringIO()) as fake_stdout:
            self.data_viz.generate_pdf_report()
            output = fake_stdout.getvalue()
            
            # Verify error message about PDF not being available
            self.assertIn("pdf generation", output.lower())
    
    @mock.patch('data_visualization.input', side_effect=['1', 'test_export.json'])
    def test_export_data(self, mock_input):
        """Test data export functionality."""
        # Create a temporary file path for the export
        export_path = os.path.join(self.test_output_dir, 'test_export.json')
        
        # Mock os.path.join to return our test path
        with mock.patch('os.path.join', return_value=export_path):
            # Call the method
            self.data_viz.export_data()
            
            # Verify the file was created
            self.assertTrue(os.path.exists(export_path))
            
            # Verify the file contains the expected data
            with open(export_path, 'r') as f:
                exported_data = json.load(f)
                self.assertEqual(exported_data['username'], self.sample_user['username'])
                self.assertEqual(len(exported_data['trips']), len(self.sample_user['trips']))
    
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', True)
    @mock.patch('data_visualization.plt')
    def test_generate_activity_summary(self, mock_plt):
        """Test _generate_activity_summary helper method."""
        # Mock the plt.savefig to avoid actual file creation
        mock_plt.savefig = mock.MagicMock()
        
        # Create a test output path
        output_path = os.path.join(self.test_output_dir, 'test_activity.png')
        
        # Call the method
        result = self.data_viz._generate_activity_summary(self.sample_user, output_path)
        
        # Verify plt.savefig was called with the correct path
        mock_plt.savefig.assert_called_with(output_path, dpi=100, bbox_inches='tight')
        
        # Verify the method returned True (success)
        self.assertTrue(result)
    
    @mock.patch('data_visualization.VISUALIZATION_AVAILABLE', False)
    def test_generate_activity_summary_no_visualization(self):
        """Test _generate_activity_summary when visualization is not available."""
        # Create a test output path
        output_path = os.path.join(self.test_output_dir, 'test_activity.png')
        
        # Call the method
        result = self.data_viz._generate_activity_summary(self.sample_user, output_path)
        
        # Verify the method returned False (failure)
        self.assertFalse(result)
    
    def test_run_visualization_function(self):
        """Test the run_visualization convenience function."""
        # Mock the DataVisualization class
        with mock.patch('data_visualization.DataVisualization') as mock_data_viz_class:
            # Mock the instance
            mock_data_viz_instance = mock.MagicMock()
            mock_data_viz_class.return_value = mock_data_viz_instance
            
            # Call the function
            data_visualization.run_visualization()
            
            # Verify DataVisualization was instantiated
            mock_data_viz_class.assert_called_once()
            
            # Verify run_visualization was called on the instance
            mock_data_viz_instance.run_visualization.assert_called_once()

if __name__ == '__main__':
    unittest.main()