#!/usr/bin/env python3
"""
Script to rename original files in the EcoCycle project to .bak files.
This will prevent them from being imported while keeping them for reference.

Usage:
  python backup_originals.py backup   # Convert original files to .bak files
  python backup_originals.py restore  # Restore .bak files to original names
"""
import os
import shutil
import sys

# Use the same file mapping from reorganize_project.py
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

def backup_original_files():
    """Rename original files to .bak files to prevent importing."""
    count = 0
    for old_path in file_mapping.keys():
        # Only process if the original file exists
        if os.path.exists(old_path):
            backup_path = f"{old_path}.bak"
            try:
                # Rename the file
                os.rename(old_path, backup_path)
                print(f"Renamed: {old_path} -> {backup_path}")
                count += 1
            except Exception as e:
                print(f"Error renaming {old_path}: {e}")
    
    print(f"\nCompleted! {count} original files have been renamed to .bak files.")
    print("These files will no longer be imported by Python, but are preserved for reference.")
    print("To restore the files, run: python backup_originals.py restore")

def restore_backup_files():
    """Restore .bak files to their original names."""
    count = 0
    for old_path in file_mapping.keys():
        # Check if backup file exists
        backup_path = f"{old_path}.bak"
        if os.path.exists(backup_path):
            try:
                # If the original file exists, we need to handle the conflict
                if os.path.exists(old_path):
                    print(f"Warning: {old_path} already exists, can't restore {backup_path}")
                    continue

                # Rename the backup file back to original
                os.rename(backup_path, old_path)
                print(f"Restored: {backup_path} -> {old_path}")
                count += 1
            except Exception as e:
                print(f"Error restoring {backup_path}: {e}")
    
    print(f"\nCompleted! {count} .bak files have been restored to their original names.")
    print("Note that this may cause conflict with the reorganized project structure.")
    print("To disable the original files again, run: python backup_originals.py backup")

def move_bak_files():
    """Move all .bak files to a backups directory with organized structure."""
    # Create backups directory if it doesn't exist
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    # Create organized subdirectories
    subdirs = {
        'core': ['dependency_manager.py', 'config.py', 'utils.py', 'database_manager.py'],
        'auth': ['user_manager.py'],
        'services': ['sheets_manager.py', 'sync_service.py', 'check_sheets_config.py', 
                    'fix_sheets_config.py', 'notification_system.py'],
        'apps': ['admin_panel.py', 'dashboard.py', 'eco_challenges.py', 
                 'social_gamification.py', 'ai_route_planner.py', 
                 'weather_route_planner.py', 'carbon_footprint.py', 
                 'data_visualization.py', 'menu.py', 'eco_tips.py'],
        'utils': ['ascii_art.py', 'app_functions.py']
    }
    
    count = 0
    for old_path in file_mapping.keys():
        backup_path = f"{old_path}.bak"
        if os.path.exists(backup_path):
            try:
                # Determine which subdirectory this file belongs to
                for subdir, files in subdirs.items():
                    if os.path.basename(old_path) in files:
                        # Create subdirectory structure if needed
                        backup_dir = os.path.join('backups', subdir)
                        if not os.path.exists(backup_dir):
                            os.makedirs(backup_dir)
                        
                        # Move the file to the appropriate subdirectory
                        new_path = os.path.join(backup_dir, os.path.basename(backup_path))
                        shutil.move(backup_path, new_path)
                        print(f"Organized: {backup_path} -> {new_path}")
                        count += 1
                        break
                else:
                    # If file doesn't match any category, put it in a 'misc' directory
                    backup_dir = os.path.join('backups', 'misc')
                    if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                    new_path = os.path.join(backup_dir, os.path.basename(backup_path))
                    shutil.move(backup_path, new_path)
                    print(f"Organized: {backup_path} -> {new_path}")
                    count += 1
            except Exception as e:
                print(f"Error moving {backup_path}: {e}")
    
    print(f"\nCompleted! {count} .bak files have been organized into the following structure:")
    print("- core: Core system files")
    print("- auth: Authentication related files")
    print("- services: Service layer files")
    print("- apps: Application modules")
    print("- utils: Utility files")
    print("- misc: Files that don't fit into other categories")
    print("\nYou can now safely delete the original .bak files if needed.")

def print_usage():
    """Print usage instructions."""
    print("Usage:")
    print("  python backup_originals.py backup   # Convert original files to .bak files")
    print("  python backup_originals.py restore  # Restore .bak files to original names")
    print("  python backup_originals.py move     # Move .bak files to backups directory")

if __name__ == "__main__":
    # Get operation from command line arguments
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    operation = sys.argv[1].lower()
    
    # Handle each operation
    if operation == "backup":
        print("This script will rename all original files to .bak extensions to prevent imports.")
        print("The files will remain in place but won't be imported by Python.")
        print("\nAre you sure you want to proceed? [y/N]")
        if input().lower() == 'y':
            backup_original_files()
    elif operation == "restore":
        print("This script will restore all .bak files to their original names.")
        print("Warning: This may cause conflicts with the reorganized project structure.")
        print("\nAre you sure you want to proceed? [y/N]")
        if input().lower() == 'y':
            restore_backup_files()
    elif operation == "move":
        print("This script will move all .bak files to an organized backup directory.")
        print("The files will be organized into core, auth, services, apps, utils, and misc directories.")
        print("\nAre you sure you want to proceed? [y/N]")
        if input().lower() == 'y':
            move_bak_files()
    else:
        print(f"Error: Unknown operation '{operation}'")
        print_usage()
        sys.exit(1)
