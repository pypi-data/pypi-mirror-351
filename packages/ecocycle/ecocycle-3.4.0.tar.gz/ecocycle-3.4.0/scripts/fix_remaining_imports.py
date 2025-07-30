#!/usr/bin/env python3
"""
Script to fix remaining import issues after project restructuring.
This addresses missed references and edge cases.
"""
import os
import re

# Files that need special handling
special_fixes = {
    # Fix root __init__.py file
    "__init__.py": [
        (r"from main import main as main_program", r"from .main import main as main_program"),
        (r"from .main import main as main_program", r"from .main import main as main_program"),  # Keep this line as is
    ],
    
    # Fix Demo Modules - handle special import cases
    "Demo Modules/demo_animations.py": [
        (r"import enhanced_ascii_art as ascii_art", r"import utils.ascii_art as ascii_art"),
    ],
    "Demo Modules/demo_enhanced_ui.py": [
        (r"import enhanced_ascii_art as ascii_art", r"import utils.ascii_art as ascii_art"),
    ],
    "Demo Modules/error_handler_example.py": [
        (r"from error_handler import", r"# TODO: Update error_handler import path\n# from error_handler import"),
        (r"import error_handler", r"# TODO: Update error_handler import path\n# import error_handler"),
    ],
    
    # Fix test files to use the new module structure
    "Tests/test_carbon_footprint.py": [
        (r"import apps.carbon_footprint", r"import apps.carbon_footprint"),  # Keep this line as is
    ],
    "Tests/test_cli.py": [
        (r"import cli", r"import cli"),  # Keep this line as is
    ],
    "Tests/test_enhanced_ui.py": [
        (r"import enhanced_ascii_art as ascii_art", r"import utils.ascii_art as ascii_art"),
    ],
    
    # Fix main.py config reference
    "main.py": [
        (r"LOG_DIR = config.LOG_DIR", r"LOG_DIR = config.config.LOG_DIR"),
    ],
}

def fix_file(file_path, fixes):
    """Apply specific fixes to a file."""
    try:
        print(f"Checking {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"  - File does not exist: {file_path}")
            return
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        modified = False
        for pattern, replacement in fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                print(f"  - Applied fix: {pattern} -> {replacement}")
                
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  - Updated file: {file_path}")
        else:
            print(f"  - No changes needed for: {file_path}")
    except Exception as e:
        print(f"  - Error processing {file_path}: {e}")

def main():
    """Main function to apply fixes."""
    os.chdir("/Users/shirishpothi/PycharmProjects/eco")
    print("Applying specific fixes to files...")
    
    for file_name, fixes in special_fixes.items():
        fix_file(file_name, fixes)
    
    print("\nAddressing remaining references to old module paths...")
    # Find and fix any missed old-style imports in new location files
    for root, _, files in os.walk('.'):
        # Skip venv and git directories
        if '.venv' in root or '.git' in root:
            continue
            
        # Only check in new directories to avoid messing with original files
        if not any(d in root for d in ['apps/', 'services/', 'utils/', 'auth/', 'core/', 'config/']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # Add specific checks for new location files
                fixes = [
                    # Fix any remaining references to old module paths
                    (r"import database_manager", r"import core.database_manager"),
                    (r"import admin_panel", r"import apps.admin.admin_panel"),
                    (r"import user_manager", r"import auth.user_management.user_manager"),
                    (r"import utils(\W)", r"import utils.general_utils\1"),
                    (r"import app_functions", r"import utils.app_functions"),
                    (r"import sheets_manager", r"import services.sheets.sheets_manager"),
                    (r"import notification_system", r"import services.notifications.notification_system"),
                    (r"import eco_tips", r"import apps.eco_tips"),
                    (r"import sync_service", r"import services.sync.sync_service"),
                    (r"import ai_route_planner", r"import apps.route_planner.ai_route_planner"),
                    (r"import weather_route_planner", r"import apps.route_planner.weather_route_planner"),
                    (r"import data_visualization", r"import apps.data_visualization"),
                    (r"import eco_challenges", r"import apps.challenges.eco_challenges"),
                    (r"import social_gamification", r"import apps.gamification.social_gamification"),
                    (r"import carbon_footprint", r"import apps.carbon_footprint"),
                    (r"import dashboard", r"import apps.dashboard.dashboard"),
                    (r"import ascii_art", r"import utils.ascii_art"),
                    (r"import dependency_manager", r"import core.dependency.dependency_manager"),
                    (r"import menu", r"import apps.menu"),
                    (r"from config import", r"from config.config import"),
                ]
                fix_file(file_path, fixes)
    
    print("\nFixing completed!")

if __name__ == "__main__":
    main()
