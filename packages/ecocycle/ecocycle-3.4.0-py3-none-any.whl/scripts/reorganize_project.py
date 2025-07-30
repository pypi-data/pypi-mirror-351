#!/usr/bin/env python3
"""
Script to reorganize the EcoCycle project structure.
This will move files to their new locations and update import statements.
"""
import os
import re
import shutil

# Define the file migration mapping
file_mapping = {
    # Core system files
    "dependency_manager.py": "core/dependency/dependency_manager.py",
    "config.py": "config/config.py",
    "utils.py": "utils/general_utils.py",
    
    # Authentication system
    "user_manager.py": "auth/user_management/user_manager.py",
    
    # Data management
    "database_manager.py": "core/database_manager.py",
    "sheets_manager.py": "services/sheets/sheets_manager.py",
    "sync_service.py": "services/sync/sync_service.py",
    "check_sheets_config.py": "services/sheets/check_sheets_config.py",
    "fix_sheets_config.py": "services/sheets/fix_sheets_config.py",
    
    # Application modules
    "admin_panel.py": "apps/admin/admin_panel.py",
    "dashboard.py": "apps/dashboard/dashboard.py",
    "eco_challenges.py": "apps/challenges/eco_challenges.py",
    "social_gamification.py": "apps/gamification/social_gamification.py",
    "ai_route_planner.py": "apps/route_planner/ai_route_planner.py",
    "weather_route_planner.py": "apps/route_planner/weather_route_planner.py",
    "carbon_footprint.py": "apps/carbon_footprint.py",
    "data_visualization.py": "apps/data_visualization.py",
    "notification_system.py": "services/notifications/notification_system.py",
    
    # CLI and main apps
    "menu.py": "apps/menu.py",
    
    # Utilities
    "ascii_art.py": "utils/ascii_art.py",
    "eco_tips.py": "apps/eco_tips.py",
    "app_functions.py": "utils/app_functions.py",
}

# Track the new module paths for import updating
module_path_map = {}
for old_path, new_path in file_mapping.items():
    module_name = os.path.splitext(os.path.basename(old_path))[0]
    new_module_path = new_path.replace('/', '.').replace('.py', '')
    module_path_map[module_name] = new_module_path

def move_files():
    """Move files to their new locations according to the mapping."""
    for old_path, new_path in file_mapping.items():
        # Ensure the source file exists
        if not os.path.exists(old_path):
            print(f"Warning: Source file {old_path} does not exist, skipping.")
            continue
        
        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        
        # Move the file
        try:
            shutil.copy2(old_path, new_path)
            print(f"Copied {old_path} to {new_path}")
        except Exception as e:
            print(f"Error copying {old_path} to {new_path}: {e}")

def update_imports(file_path):
    """Update import statements."""
    global content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for module_name, new_path in module_path_map.items():
            # Handle from X import ...
            pattern = rf'from\s+({module_name}(?:\.\w+)*)\s+import'
            repl = lambda m: f"from {new_path}{m.group(1)[len(module_name):]} import"
            content = re.sub(pattern, repl, content)

            # Handle import X...
            pattern = rf'import\s+({module_name}(?:\.\w+)*)(\b|$)'
            repl = lambda m: f"import {new_path}{m.group(1)[len(module_name):]}"
            content = re.sub(pattern, repl, content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error updating imports in `{file_path}`: {e}")

if __name__ == "__main__":
    # Create directories first
    for _, path in file_mapping.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Copy files to new locations
    move_files()
    
    # Update import statements in all files
    update_imports()
    
    print("\nProject reorganization completed!")
    print("Please review the changes and test the application.")
    print("Once everything is working correctly, you can delete the original files.")
