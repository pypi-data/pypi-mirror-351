#!/usr/bin/env python3
"""
EcoCycle - Fix Google Sheets Configuration
Sets the Google Sheets spreadsheet ID and verifies the connection.
"""
import logging
import sys
import os

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from services.sheets.sheets_manager import SheetsManager

def configure_spreadsheet_id(spreadsheet_id=None):
    """
    Configure the Google Sheets spreadsheet ID and test the connection.
    
    Args:
        spreadsheet_id (str): Google Sheets spreadsheet ID to set
    
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    if not spreadsheet_id:
        logger.error("No spreadsheet ID provided. Usage: python fix_sheets_config.py <spreadsheet_id>")
        return False
    
    # Create a new SheetsManager instance
    sheets_manager = SheetsManager()
    
    # Set the spreadsheet ID
    sheets_manager.spreadsheet_id = spreadsheet_id
    
    # Test the connection
    if sheets_manager.is_available():
        logger.info(f"Successfully connected to Google Sheets with spreadsheet ID: {spreadsheet_id}")
        
        # Try to read a sheet
        try:
            user_sheet = sheets_manager.get_or_create_sheet(sheets_manager.SHEET_USERS)
            logger.info(f"User sheet exists or was created: {user_sheet}")
            
            # Save the spreadsheet ID permanently
            logger.info("To make this configuration permanent, set this environment variable:")
            logger.info(f"export ECOCYCLE_SPREADSHEET_ID={spreadsheet_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error reading/creating sheet: {e}")
            return False
    else:
        logger.error("Failed to connect to Google Sheets. Check your credentials and spreadsheet ID.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("No spreadsheet ID provided. Usage: python fix_sheets_config.py <spreadsheet_id>")
        sys.exit(1)
    
    spreadsheet_id = sys.argv[1]
    success = configure_spreadsheet_id(spreadsheet_id)
    
    if success:
        logger.info("Google Sheets configuration completed successfully.")
    else:
        logger.error("Failed to configure Google Sheets integration.")
        sys.exit(1)
