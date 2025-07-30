import os
import logging
from services.sheets.sheets_manager import SheetsManager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_sheets_manager():
    """Test the SheetsManager class."""
    print("Initializing SheetsManager...")
    sheets_manager = SheetsManager()
    
    print(f"Is Google Sheets available: {sheets_manager.is_available()}")
    
    # Test logging a trip
    if sheets_manager.is_available():
        print("Logging a test trip...")
        trip_data = {
            'date': '2025-04-30',
            'distance': 5.0,
            'duration': 30,
            'calories': 150,
            'co2_saved': 1.2
        }
        result = sheets_manager.log_trip('test_user', trip_data)
        print(f"Trip logged successfully: {result}")
    else:
        print("Google Sheets is not available, skipping trip logging test")

if __name__ == "__main__":
    test_sheets_manager()