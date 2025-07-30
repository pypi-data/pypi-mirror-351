#!/usr/bin/env python3
"""
EcoCycle - Google Sheets Configuration Diagnostic Tool
This script checks your Google Sheets configuration and helps fix any issues.
"""
import os
import sys
import json
import logging
from pathlib import Path
import core.dependency.dependency_manager  # Import dependency_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def check_env_variables():
    """Check if required environment variables are set."""
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    spreadsheet_id = os.environ.get('ECOCYCLE_SPREADSHEET_ID')
    
    print("\n--- Checking Environment Variables ---")
    
    if creds_path:
        print(f"✓ GOOGLE_APPLICATION_CREDENTIALS is set to: {creds_path}")
        # Check if the file exists
        if os.path.exists(creds_path):
            print(f"✓ Credentials file exists at: {creds_path}")
        else:
            print(f"❌ ERROR: Credentials file not found at: {creds_path}")
            logger.error(f"Credentials file not found at: {creds_path}")
    else:
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
        logger.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
    
    if spreadsheet_id:
        print(f"✓ ECOCYCLE_SPREADSHEET_ID is set to: {spreadsheet_id}")
    else:
        print("❌ ERROR: ECOCYCLE_SPREADSHEET_ID environment variable is not set")
        logger.error("ECOCYCLE_SPREADSHEET_ID environment variable is not set")
    
    return creds_path, spreadsheet_id

def find_credentials_file():
    """Find possible credentials files in the workspace."""
    possible_files = []
    
    # Common names for Google API credentials files
    patterns = [
        "*.json",
        "*credentials*.json",
        "*secret*.json",
        "*auth*.json",
        "*google*.json",
    ]
    
    print("\n--- Searching for Credential Files ---")
    
    # Search in the current directory and parent directory
    search_dirs = [os.getcwd(), os.path.dirname(os.getcwd())]
    
    for directory in search_dirs:
        for pattern in patterns:
            path = Path(directory)
            for file in path.glob(pattern):
                if file.is_file():
                    try:
                        # Try to read the file as JSON
                        with open(file, 'r') as f:
                            data = json.load(f)
                        
                        # Check if it looks like a Google credentials file
                        if "type" in data and "project_id" in data and "private_key" in data:
                            possible_files.append(str(file))
                            print(f"✓ Found potential credentials file: {file}")
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Not a valid JSON file, skip
                        pass
                    except Exception as e:
                        print(f"Error reading file {file}: {e}")
                        logger.error(f"Error reading file {file}: {e}")
    
    if not possible_files:
        print("❌ No potential Google credential files found")
        logger.error("No potential Google credential files found")
    
    return possible_files

def test_google_sheets_connection(creds_path=None, spreadsheet_id=None):
    """Test the connection to Google Sheets API."""
    print("\n--- Testing Google Sheets Connection ---")
    
    if not creds_path or not os.path.exists(creds_path):
        print("❌ Cannot test connection: Credentials file not found")
        logger.error("Cannot test connection: Credentials file not found")
        return False
    
    if not spreadsheet_id:
        print("❌ Cannot test connection: Spreadsheet ID not set")
        logger.error("Cannot test connection: Spreadsheet ID not set")
        return False
    
    print("Attempting to connect to Google Sheets API...")
    
    try:
        # Ensure required packages are installed
        dependency_manager.ensure_packages([
            'google-api-python-client', 
            'google-auth', 
            'google-auth-oauthlib', 
            'google-auth-httplib2'
        ])
        
        # Import required packages
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Initialize credentials and service
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        
        # Try to access the spreadsheet
        result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        title = result.get('properties', {}).get('title', 'Unknown')
        
        print(f"✓ Successfully connected to spreadsheet: {title}")
        print(f"✓ The spreadsheet has {len(result.get('sheets', []))} sheets")
        
        # List the sheets
        sheet_names = [sheet.get('properties', {}).get('title') for sheet in result.get('sheets', [])]
        print(f"✓ Sheets: {', '.join(sheet_names)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets API: {e}")
        logger.error(f"Error connecting to Google Sheets API: {e}")
        return False

def create_or_update_env_file(creds_path, spreadsheet_id):
    """Create or update the .env file with the correct environment variables."""
    print("\n--- Updating .env File ---")
    
    env_path = os.path.join(os.getcwd(), '.env')
    env_vars = {}
    
    # Read existing .env file if it exists
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Update with new values
    if creds_path:
        env_vars['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
    if spreadsheet_id:
        env_vars['ECOCYCLE_SPREADSHEET_ID'] = spreadsheet_id
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.write("# EcoCycle environment variables\n")
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✓ Updated .env file with correct environment variables")
    return True

def main():
    """Main function to run the diagnostic tool."""
    print("======================================")
    print("EcoCycle - Google Sheets Configuration Diagnostic")
    print("======================================")
    
    # Check environment variables
    creds_path, spreadsheet_id = check_env_variables()
    
    # Find potential credentials files
    if not creds_path or not os.path.exists(creds_path):
        possible_files = find_credentials_file()
        
        if possible_files and not creds_path:
            # User the first found file
            creds_path = possible_files[0]
            print(f"\nUsing credential file: {creds_path}")
    
    # Test connection
    connection_success = False
    if creds_path and spreadsheet_id:
        connection_success = test_google_sheets_connection(creds_path, spreadsheet_id)
    
    # Provide summary and recommendations
    print("\n======================================")
    print("Diagnostic Summary & Recommendations")
    print("======================================")
    
    if not creds_path or not os.path.exists(creds_path):
        print("1. You need to set up a valid Google credentials file:")
        print("   - In your workspace, you have 'Google Auth Client Secret.json'")
        print("   - Set GOOGLE_APPLICATION_CREDENTIALS environment variable to this file path")
        print("   - Add to .env: GOOGLE_APPLICATION_CREDENTIALS=Google Auth Client Secret.json")
    
    if not spreadsheet_id:
        print("\n2. You need to set your Google Sheets spreadsheet ID:")
        print("   - Create a spreadsheet in Google Sheets")
        print("   - Get the ID from the URL: https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit")
        print("   - Add to .env: ECOCYCLE_SPREADSHEET_ID=your_spreadsheet_id")
    
    if creds_path and os.path.exists(creds_path) and spreadsheet_id and not connection_success:
        print("\n3. Connection failed despite having credentials and spreadsheet ID:")
        print("   - Ensure the service account has access to the spreadsheet")
        print("   - Share the spreadsheet with the service account email address")
        print("   - Check that the credentials file is valid")
        print("   - Ensure you have internet connectivity")
    
    if connection_success:
        print("\n✓ Success! Your Google Sheets configuration is working correctly.")
    else:
        print("\nWould you like to update your .env file with the correct paths? (y/n)")
        choice = input("> ").strip().lower()
        
        if choice == 'y':
            if not creds_path and len(possible_files) > 1:
                print("\nMultiple credential files found. Which one would you like to use?")
                for i, file in enumerate(possible_files):
                    print(f"{i+1}. {file}")
                file_choice = input("\nEnter number: ").strip()
                try:
                    file_index = int(file_choice) - 1
                    if 0 <= file_index < len(possible_files):
                        creds_path = possible_files[file_index]
                except ValueError:
                    print("Invalid choice. Using default.")
            
            if not spreadsheet_id:
                print("\nEnter your Google Sheets spreadsheet ID:")
                spreadsheet_id = input("> ").strip()
            
            create_or_update_env_file(creds_path, spreadsheet_id)
            print("\nPlease restart your application for the changes to take effect.")

if __name__ == "__main__":
    main()
