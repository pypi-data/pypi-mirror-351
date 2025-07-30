#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EcoCycle - Admin Panel Module
Provides admin functionality for managing users, viewing logs, and fixing data.
"""
import sys
import logging
from datetime import datetime
import core.dependency.dependency_manager  # Import dependency_manager

# Ensure required packages are installed
dependency_manager.ensure_packages(['tabulate', 'colorama'])

try:
    from tabulate import tabulate
    import colorama
    from colorama import Fore, Style
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

from utils.ascii_art import display_section_header, display_info_message, display_success_message, display_error_message
import core.database_manager

def show_admin_panel(sheets_manager, user_manager):
    """Display the admin panel with options for managing the EcoCycle system. """
    if not HAS_DEPENDENCIES:
        print("Required dependencies not available. Please install tabulate and colorama.")
        return

    admin_name = input("Enter your admin name for the logs: ").strip()
    if not admin_name:
        admin_name = "Admin"

    # Log the admin login
    try:
        sheets_manager.log_admin_action(admin_name, "LOGIN", "Admin logged into the system")
        logging.info(f"Admin '{admin_name}' logged in")
    except Exception as e:
        logging.error(f"Failed to log admin login: {e}", exc_info=True)
        print(f"{Fore.RED}Warning: Failed to log admin action. Some features may be limited.{Style.RESET_ALL}")

    # Log to the database
    conn = database_manager.create_connection()
    if conn:
        database_manager.add_user(conn, (admin_name, "Admin", "", "", "", "", 1, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.close()

    while True:
        display_section_header("Admin Panel")
        print(f"{Fore.YELLOW}0. Exit Program{Style.RESET_ALL}")
        print("1. View User Statistics")
        print("2. View Admin Action Logs")
        print("3. View Email Logs")
        print("4. Fix User Data")
        print("5. Generate System Report")
        print("6. Back to Main Menu")

        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == '0':
            # Exit program
            print("\nExiting program...")
            import sys
            sys.exit(0)
        elif choice == '1':
            view_user_statistics(sheets_manager, admin_name)
        elif choice == '2':
            view_admin_logs(sheets_manager, admin_name)
        elif choice == '3':
            view_email_logs(sheets_manager, admin_name)
        elif choice == '4':
            fix_user_data(sheets_manager, user_manager, admin_name)
        elif choice == '5':
            generate_system_report(sheets_manager, admin_name)
        elif choice == '6':
            try:
                sheets_manager.log_admin_action(admin_name, "LOGOUT", "Admin exited the admin panel")
                logging.info(f"Admin '{admin_name}' logged out")
            except Exception as e:
                logging.error(f"Failed to log admin logout: {e}", exc_info=True)

            display_info_message("Returning to main menu")
            return
        else:
            print(f"{Fore.YELLOW}Invalid choice. Please enter a number from 0 to 6.{Style.RESET_ALL}")

def view_user_statistics(sheets_manager, admin_name):
    """View statistics for all users in the system."""
    display_section_header("User Statistics")

    try:
        # Fetch all user data from Google Sheets
        user_data = sheets_manager.get_all_user_data()

        if len(user_data) <= 1:
            display_info_message("No user data available.")
            return

        # Format data for tabulate
        headers = user_data[0]
        data = user_data[1:]

        # Log the admin action
        sheets_manager.log_admin_action(admin_name, "VIEW_STATS", f"Viewed statistics for {len(data)} users")

        # Log to the database
        conn = database_manager.create_connection()
        if conn:
            database_manager.add_stat(conn, (admin_name, len(data), sum(float(row[5]) if len(row) > 5 and row[5] else 0 for row in data), sum(float(row[6]) if len(row) > 6 and row[6] else 0 for row in data), 0))
            conn.close()

        # Display data in a table
        print(tabulate(data, headers=headers, tablefmt="grid", numalign="right"))

        # Display summary statistics
        total_users = len(data)
        total_distance = sum(float(row[5]) if len(row) > 5 and row[5] else 0 for row in data)
        total_co2_saved = sum(float(row[6]) if len(row) > 6 and row[6] else 0 for row in data)

        print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
        print(f"Total Users: {total_users}")
        print(f"Total Distance Cycled: {total_distance:.2f} km")
        print(f"Total CO2 Saved: {total_co2_saved:.2f} kg")

        input("\nPress Enter to continue...")

    except Exception as e:
        logging.error(f"Error viewing user statistics: {e}", exc_info=True)
        display_error_message(f"Error viewing user statistics: {e}")
        input("\nPress Enter to continue...")

def view_admin_logs(sheets_manager, admin_name):
    """View the admin action logs."""
    display_section_header("Admin Action Logs")

    # Ask for filter options
    print("Filter options:")
    print("1. View all logs")
    print("2. Filter by admin name")
    print("3. Filter by action type")

    filter_choice = input("\nEnter your choice (1-3): ").strip()

    try:
        # Get all admin actions
        logs = sheets_manager.get_admin_actions(limit=100)

        if len(logs) <= 1:
            display_info_message("No admin logs available.")
            return

        # Apply filters if selected
        filtered_logs = logs[0:1]  # Keep the header row

        if filter_choice == '2':
            filter_admin = input("Enter admin name to filter by: ").strip()
            filtered_logs.extend([log for log in logs[1:] if log[1].lower() == filter_admin.lower()])
        elif filter_choice == '3':
            filter_action = input("Enter action type to filter by (LOGIN, LOGOUT, VIEW_STATS, etc.): ").strip().upper()
            filtered_logs.extend([log for log in logs[1:] if log[2].upper() == filter_action])
        else:
            # Default: show all logs
            filtered_logs = logs

        # Log the admin action
        sheets_manager.log_admin_action(admin_name, "VIEW_LOGS", f"Viewed admin action logs with filter option {filter_choice}")

        # Log to the database
        conn = database_manager.create_connection()
        if conn:
            database_manager.add_stat(conn, (admin_name, len(filtered_logs) - 1, 0, 0, 0))
            conn.close()

        # Display logs in a table
        if len(filtered_logs) > 1:
            print(tabulate(filtered_logs[1:], headers=filtered_logs[0], tablefmt="grid"))
        else:
            display_info_message("No logs match the filter criteria.")

        input("\nPress Enter to continue...")

    except Exception as e:
        logging.error(f"Error viewing admin logs: {e}", exc_info=True)
        display_error_message(f"Error viewing admin logs: {e}")
        input("\nPress Enter to continue...")

def view_email_logs(sheets_manager, admin_name):
    """View the email logs."""
    display_section_header("Email Logs")

    try:
        # Get all email logs
        logs = sheets_manager.get_email_logs(limit=100)

        if len(logs) <= 1:
            display_info_message("No email logs available.")
            return

        # Log the admin action
        sheets_manager.log_admin_action(admin_name, "VIEW_EMAIL_LOGS", f"Viewed email logs")

        # Log to the database
        conn = database_manager.create_connection()
        if conn:
            database_manager.add_stat(conn, (admin_name, len(logs) - 1, 0, 0, 0))
            conn.close()

        # Display logs in a table
        print(tabulate(logs[1:], headers=logs[0], tablefmt="grid"))

        input("\nPress Enter to continue...")

    except Exception as e:
        logging.error(f"Error viewing email logs: {e}", exc_info=True)
        display_error_message(f"Error viewing email logs: {e}")
        input("\nPress Enter to continue...")

def fix_user_data(sheets_manager, user_manager, admin_name):
    """Fix data for a specific user."""
    display_section_header("Fix User Data")

    # Ask for the username to fix
    username = input("Enter username to fix data for: ").strip()

    if not username:
        display_error_message("Username cannot be empty.")
        return

    try:
        # Get fresh data from Google Sheets for this user
        user_data, row_num = sheets_manager.get_user_data(username)

        if row_num < 0:
            display_error_message(f"User '{username}' not found in the database.")
            return

        # Display current data
        print(f"\n{Fore.CYAN}Current data for user '{username}':{Style.RESET_ALL}")
        headers = ["Field", "Value"]
        field_names = ["User Name", "Last Distance", "Last Price", "Cumulative Points", 
                       "Cumulative Price", "Cumulative Distance", "Cumulative CO2 Saved", "Cumulative Calories"]

        # Ensure user_data has enough elements
        while len(user_data) < len(field_names):
            user_data.append("")

        # Create a list of [field_name, value] pairs
        data = [[field_names[i], user_data[i]] for i in range(len(field_names))]

        print(tabulate(data, headers=headers, tablefmt="simple"))

        # Ask which field to fix
        print("\nWhich field would you like to fix?")
        for i, field in enumerate(field_names):
            print(f"{i+1}. {field}")

        field_choice = input("\nEnter field number (1-8), or 0 to cancel: ").strip()

        if field_choice == '0':
            display_info_message("Data fix cancelled.")
            return

        try:
            field_index = int(field_choice) - 1
            if field_index < 0 or field_index >= len(field_names):
                display_error_message("Invalid field number.")
                return

            field_name = field_names[field_index]
            current_value = user_data[field_index] if field_index < len(user_data) else ""

            new_value = input(f"Enter new value for {field_name} (current: {current_value}): ").strip()

            if new_value:
                # Update the user data
                user_data[field_index] = new_value

                # Save the updated data
                sheets_manager.update_user_data(username, user_data)

                # Log the admin action
                sheets_manager.log_admin_action(admin_name, "FIX_DATA", 
                                              f"Fixed {field_name} for user '{username}' from '{current_value}' to '{new_value}'")

                # Log to the database
                conn = database_manager.create_connection()
                if conn:
                    database_manager.update_user(conn, (username, "", "", "", "", "", 0, 0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    conn.close()

                display_success_message(f"Successfully updated {field_name} for user '{username}'.")
            else:
                display_info_message("No changes made.")

        except ValueError:
            display_error_message("Please enter a valid number.")

    except Exception as e:
        logging.error(f"Error fixing user data: {e}", exc_info=True)
        display_error_message(f"Error fixing user data: {e}")

    input("\nPress Enter to continue...")

def generate_system_report(sheets_manager, admin_name):
    """Generate a system report with key statistics."""
    display_section_header("System Report")

    try:
        # Get current date and time
        now = datetime.now()

        print(f"{Fore.CYAN}EcoCycle System Report{Style.RESET_ALL}")
        print(f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Generated by: {admin_name}")
        print("-" * 50)

        # Get user statistics
        user_data = sheets_manager.get_all_user_data()

        if len(user_data) <= 1:
            print("No user data available.")
        else:
            data = user_data[1:]
            total_users = len(data)
            total_distance = sum(float(row[5]) if len(row) > 5 and row[5] and row[5] != '' else 0 for row in data)
            total_co2_saved = sum(float(row[6]) if len(row) > 6 and row[6] and row[6] != '' else 0 for row in data)
            total_calories = sum(float(row[7]) if len(row) > 7 and row[7] and row[7] != '' else 0 for row in data)

            print(f"{Fore.GREEN}User Statistics:{Style.RESET_ALL}")
            print(f"Total Users: {total_users}")
            print(f"Total Distance Cycled: {total_distance:.2f} km")
            print(f"Total CO2 Saved: {total_co2_saved:.2f} kg")
            print(f"Total Calories Burned: {total_calories:.2f} kcal")

            # Calculate environmental impact equivalents
            trees_saved = total_co2_saved / 25  # Approx 25kg CO2 absorbed by a tree per year
            car_trips_avoided = total_distance / 10  # Assuming 10km per car trip

            print(f"\n{Fore.GREEN}Environmental Impact:{Style.RESET_ALL}")
            print(f"Equivalent to planting {trees_saved:.2f} trees")
            print(f"Equivalent to avoiding {car_trips_avoided:.0f} car trips")

            # User engagement statistics
            active_users = len([row for row in data if len(row) > 2 and row[2] and row[2] != ''])
            avg_distance_per_user = total_distance / total_users if total_users > 0 else 0

            print(f"\n{Fore.GREEN}User Engagement:{Style.RESET_ALL}")
            print(f"Active Users: {active_users} ({(active_users/total_users*100):.1f}% of total)")
            print(f"Average Distance per User: {avg_distance_per_user:.2f} km")

        # Log the admin action
        sheets_manager.log_admin_action(admin_name, "GENERATE_REPORT", "Generated system report")

        # Log to the database
        conn = database_manager.create_connection()
        if conn:
            database_manager.add_stat(conn, (admin_name, total_users, total_distance, total_co2_saved, total_calories))
            conn.close()

        # Ask if user wants to save the report
        save_report = input("\nWould you like to save this report to a file? (y/n): ").strip().lower()

        if save_report == 'y':
            report_filename = f"ecocycle_report_{now.strftime('%Y%m%d_%H%M%S')}.txt"

            with open(report_filename, 'w') as f:
                f.write("EcoCycle System Report\n")
                f.write(f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Generated by: {admin_name}\n")
                f.write("-" * 50 + "\n\n")

                if len(user_data) <= 1:
                    f.write("No user data available.\n")
                else:
                    f.write("User Statistics:\n")
                    f.write(f"Total Users: {total_users}\n")
                    f.write(f"Total Distance Cycled: {total_distance:.2f} km\n")
                    f.write(f"Total CO2 Saved: {total_co2_saved:.2f} kg\n")
                    f.write(f"Total Calories Burned: {total_calories:.2f} kcal\n\n")

                    f.write("Environmental Impact:\n")
                    f.write(f"Equivalent to planting {trees_saved:.2f} trees\n")
                    f.write(f"Equivalent to avoiding {car_trips_avoided:.0f} car trips\n\n")

                    f.write("User Engagement:\n")
                    f.write(f"Active Users: {active_users} ({(active_users/total_users*100):.1f}% of total)\n")
                    f.write(f"Average Distance per User: {avg_distance_per_user:.2f} km\n")

            display_success_message(f"Report saved to {report_filename}")

    except Exception as e:
        logging.error(f"Error generating system report: {e}", exc_info=True)
        display_error_message(f"Error generating system report: {e}")

    input("\nPress Enter to continue...")
