#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EcoCycle - Dashboard Module
Provides functionality for displaying user statistics and sustainability metrics.
"""
import time
import logging
import random
from datetime import datetime
import core.dependency.dependency_manager  # Import dependency_manager

# Ensure required packages are installed
dependency_manager.ensure_packages(['tqdm', 'colorama', 'tabulate'])

try:
    from tqdm import tqdm
    import colorama
    from colorama import Fore, Style
    from tabulate import tabulate
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

from utils.ascii_art import display_section_header, display_success_message, display_error_message, display_info_message
import core.database_manager
from core.error_handler import EcoCycleError, DatabaseError, handle_error, retry, with_fallback

class Dashboard:
    """Dashboard class for managing cycling trip data and displaying statistics."""
    
    def __init__(self, user_manager, sheets_manager):
        """Initialize the dashboard with required managers."""
        self.user_manager = user_manager
        self.sheets_manager = sheets_manager
        
        # Constants for calculations
        self.CO2_PER_KM = 0.192  # kg of CO2 saved per km (compared to driving)
        self.CALORIES_PER_KM = 50  # calories burned per km (average)
        self.POINTS_PER_KM = 10  # eco points earned per km
        
        # Cache for current user
        self.current_user = None
    
    @retry(max_attempts=3, delay=1.0, exceptions=(DatabaseError,))
    def log_cycling_trip(self):
        """Log a new cycling trip for a user."""
        if not HAS_DEPENDENCIES:
            print("Required dependencies not available. Please install tqdm, colorama and tabulate.")
            return
        
        display_section_header("Log Cycling Trip")
        
        # Get username
        username = input("Enter your username: ").strip()
        if not username:
            display_error_message("Username cannot be empty.")
            return
        
        # Check if Google Sheets is available
        if not self.sheets_manager:
            display_error_message("Google Sheets connection is not available. Cannot log trip.")
            return
        
        try:
            # Try to get existing user data
            display_info_message(f"Looking up user data for {username}...")
            
            # Use loading indicator for user lookup
            with tqdm(total=100, desc="Searching user database", unit="%", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour='green') as pbar:
                user_data, row_num = self.sheets_manager.get_user_data(username)
                # Simulate a bit of processing time for better UX
                for i in range(10):
                    time.sleep(0.05)
                    pbar.update(10)
            
            # Check if user exists
            if row_num < 0:
                display_info_message(f"First time user '{username}'! Creating new user record.")
                user_data = [username, "0", "0", "0", "0", "0", "0", "0"]
            else:
                display_success_message(f"Found user '{username}' in the database.")
            
            # Get trip details with validation
            valid_input = False
            while not valid_input:
                try:
                    distance_str = input("Enter cycling distance in kilometers: ").strip()
                    distance = float(distance_str)
                    if distance <= 0:
                        display_error_message("Distance must be greater than zero.")
                    else:
                        valid_input = True
                except ValueError:
                    display_error_message("Please enter a valid number for distance.")
            
            # Calculate impact
            co2_saved = distance * self.CO2_PER_KM
            calories_burned = distance * self.CALORIES_PER_KM
            points_earned = distance * self.POINTS_PER_KM
            fuel_price = 1.50  # Assumed average fuel price per liter
            fuel_saved = distance * 0.08  # Assumed 8 liters per 100 km = 0.08 l/km
            money_saved = fuel_saved * fuel_price
            
            # Show calculation in progress with loading bar
            display_info_message("Calculating environmental impact...")
            with tqdm(total=100, desc="Processing", unit="%", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour='green') as pbar:
                for i in range(10):
                    time.sleep(0.1)
                    pbar.update(10)
            
            # Update user data
            last_distance = distance
            last_price = money_saved
            cum_points = float(user_data[3]) + points_earned if user_data[3] else points_earned
            cum_price = float(user_data[4]) + money_saved if user_data[4] else money_saved
            cum_distance = float(user_data[5]) + distance if user_data[5] else distance
            cum_co2 = float(user_data[6]) + co2_saved if user_data[6] else co2_saved
            cum_calories = float(user_data[7]) + calories_burned if user_data[7] else calories_burned
            
            new_user_data = [
                username,
                str(last_distance),
                str(last_price),
                str(cum_points),
                str(cum_price),
                str(cum_distance),
                str(cum_co2),
                str(cum_calories)
            ]
            
            # Save to Google Sheets
            display_info_message("Saving trip data...")
            with tqdm(total=100, desc="Saving to database", unit="%", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour='green') as pbar:
                self.sheets_manager.update_user_data(username, new_user_data)
                for i in range(5):
                    time.sleep(0.1)
                    pbar.update(20)
            
            # Log to the database
            conn = database_manager.create_connection()
            if conn:
                database_manager.add_trip(conn, (username, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), distance, 0, co2_saved, calories_burned))
                conn.close()
            
            # Display success and trip summary
            display_success_message("Trip logged successfully!")
            
            print(f"\n{Fore.CYAN}Trip Summary:{Style.RESET_ALL}")
            summary_data = [
                ["Distance", f"{distance:.2f} km"],
                ["CO2 Saved", f"{co2_saved:.2f} kg"],
                ["Calories Burned", f"{calories_burned:.0f} kcal"],
                ["Eco Points Earned", f"{points_earned:.0f} points"],
                ["Money Saved", f"${money_saved:.2f}"]
            ]
            print(tabulate(summary_data, tablefmt="simple"))
            
            print(f"\n{Fore.CYAN}Your Totals:{Style.RESET_ALL}")
            totals_data = [
                ["Total Distance", f"{cum_distance:.2f} km"],
                ["Total CO2 Saved", f"{cum_co2:.2f} kg"],
                ["Total Calories Burned", f"{cum_calories:.0f} kcal"],
                ["Total Eco Points", f"{cum_points:.0f} points"],
                ["Total Money Saved", f"${cum_price:.2f}"]
            ]
            print(tabulate(totals_data, tablefmt="simple"))
            
            # Update current user
            self.current_user = username
            
            # Add a random achievement or encouragement
            self._show_random_achievement(cum_distance, cum_co2, cum_calories)
        
        except DatabaseError as e:
            handle_error(e, display_error_message)
        except EcoCycleError as e:
            handle_error(e, display_error_message)
        except Exception as e:
            handle_error(EcoCycleError(f"Unexpected error: {str(e)}"), display_error_message)
        
        input("\nPress Enter to continue...")
    
    @retry(max_attempts=3, delay=1.0, exceptions=(DatabaseError,))
    def view_user_statistics(self):
        """View statistics for a user."""
        if not HAS_DEPENDENCIES:
            print("Required dependencies not available. Please install colorama and tabulate.")
            return
        
        display_section_header("User Statistics")
        
        # Get username (default to last used)
        default_username = self.current_user if self.current_user else ""
        if default_username:
            username = input(f"Enter username [{default_username}]: ").strip()
            if not username:
                username = default_username
        else:
            username = input("Enter username: ").strip()
        
        if not username:
            display_error_message("Username cannot be empty.")
            return
        
        # Check if Google Sheets is available
        if not self.sheets_manager:
            display_error_message("Google Sheets connection is not available. Cannot view statistics.")
            return
        
        try:
            # Get user data
            display_info_message(f"Looking up statistics for {username}...")
            
            # Use loading indicator for user lookup
            with tqdm(total=100, desc="Fetching user data", unit="%", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour='green') as pbar:
                user_data, row_num = self.sheets_manager.get_user_data(username)
                # Simulate a bit of processing time for better UX
                for i in range(10):
                    time.sleep(0.05)
                    pbar.update(10)
            
            if row_num < 0:
                display_error_message(f"User '{username}' not found.")
                return
            
            # Ensure all data fields are available
            while len(user_data) < 8:
                user_data.append("0")
            
            # Display user statistics
            print(f"\n{Fore.CYAN}Statistics for {username}:{Style.RESET_ALL}")
            
            # Format the data nicely
            stats_data = [
                ["Last Trip Distance", f"{float(user_data[1] or 0):.2f} km"],
                ["Last Trip Money Saved", f"${float(user_data[2] or 0):.2f}"],
                ["Total Eco Points", f"{float(user_data[3] or 0):.0f} points"],
                ["Total Money Saved", f"${float(user_data[4] or 0):.2f}"],
                ["Total Distance", f"{float(user_data[5] or 0):.2f} km"],
                ["Total CO2 Saved", f"{float(user_data[6] or 0):.2f} kg"],
                ["Total Calories Burned", f"{float(user_data[7] or 0):.0f} kcal"]
            ]
            
            print(tabulate(stats_data, tablefmt="grid"))
            
            # Add environmental impact equivalents
            co2_saved = float(user_data[6] or 0)
            trees_equivalent = co2_saved / 25  # Approx. 25kg CO2 absorbed by a tree per year
            car_trips_avoided = float(user_data[5] or 0) / 10  # Assuming 10km per car trip
            
            print(f"\n{Fore.GREEN}Environmental Impact:{Style.RESET_ALL}")
            print(f"🌳 Equivalent to planting {trees_equivalent:.1f} trees")
            print(f"🚗 Equivalent to avoiding {car_trips_avoided:.0f} car trips")
            
            # Log to the database
            conn = database_manager.create_connection()
            if conn:
                database_manager.add_stat(conn, (username, 0, float(user_data[5] or 0), co2_saved, float(user_data[7] or 0)))
                conn.close()
            
            # Update current user
            self.current_user = username
        
        except DatabaseError as e:
            handle_error(e, display_error_message)
        except EcoCycleError as e:
            handle_error(e, display_error_message)
        except Exception as e:
            handle_error(EcoCycleError(f"Unexpected error: {str(e)}"), display_error_message)
        
        input("\nPress Enter to continue...")
    
    def view_sustainability_dashboard(self):
        """View the sustainability dashboard with global statistics."""
        if not HAS_DEPENDENCIES:
            print("Required dependencies not available. Please install colorama and tabulate.")
            return
        
        display_section_header("Sustainability Dashboard")
        
        # Check if Google Sheets is available
        if not self.sheets_manager:
            display_error_message("Google Sheets connection is not available. Cannot view dashboard.")
            return
        
        try:
            # Get all user data
            display_info_message("Loading sustainability metrics...")
            
            # Use loading indicator
            with tqdm(total=100, desc="Analyzing global data", unit="%", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour='green') as pbar:
                all_user_data = self.sheets_manager.get_all_user_data()
                for i in range(5):
                    time.sleep(0.1)
                    pbar.update(20)
            
            if len(all_user_data) <= 1:
                display_info_message("No user data available yet.")
                return
            
            # Skip header row
            data = all_user_data[1:]
            
            # Calculate global statistics
            total_users = len(data)
            total_distance = sum(float(row[5]) if len(row) > 5 and row[5] and row[5] != '' else 0 for row in data)
            total_co2_saved = sum(float(row[6]) if len(row) > 6 and row[6] and row[6] != '' else 0 for row in data)
            total_calories = sum(float(row[7]) if len(row) > 7 and row[7] and row[7] != '' else 0 for row in data)
            
            # Calculate environmental impact equivalents
            trees_saved = total_co2_saved / 25  # Approx 25kg CO2 absorbed by a tree per year
            car_trips_avoided = total_distance / 10  # Assuming 10km per car trip
            gasoline_saved = total_distance * 0.08  # Assuming 8 liters per 100 km = 0.08 l/km
            
            # Display the dashboard
            print(f"\n{Fore.CYAN}Global Sustainability Metrics:{Style.RESET_ALL}")
            
            # Format the data nicely
            global_data = [
                ["Total Users", f"{total_users}"],
                ["Total Distance Cycled", f"{total_distance:.2f} km"],
                ["Total CO2 Saved", f"{total_co2_saved:.2f} kg"],
                ["Total Calories Burned", f"{total_calories:.0f} kcal"]
            ]
            
            print(tabulate(global_data, tablefmt="grid"))
            
            print(f"\n{Fore.GREEN}Environmental Impact:{Style.RESET_ALL}")
            impact_data = [
                ["🌳 Trees Equivalent", f"{trees_saved:.1f} trees"],
                ["🚗 Car Trips Avoided", f"{car_trips_avoided:.0f} trips"],
                ["⛽ Gasoline Saved", f"{gasoline_saved:.2f} liters"]
            ]
            
            print(tabulate(impact_data, tablefmt="simple"))
            
            # Display leaderboard
            print(f"\n{Fore.YELLOW}Top Cyclists Leaderboard:{Style.RESET_ALL}")
            
            # Sort users by total distance
            leaderboard_data = []
            for row in data:
                if len(row) > 5 and row[5] and row[5] != '':
                    leaderboard_data.append([row[0], float(row[5]), float(row[6]) if len(row) > 6 and row[6] and row[6] != '' else 0])
            
            # Sort by distance (descending)
            leaderboard_data.sort(key=lambda x: x[1], reverse=True)
            
            # Display top 5 users
            top_users = leaderboard_data[:5]
            if top_users:
                leaderboard_table = []
                for i, user in enumerate(top_users):
                    leaderboard_table.append([i+1, user[0], f"{user[1]:.2f} km", f"{user[2]:.2f} kg CO2"])
                
                print(tabulate(leaderboard_table, headers=["Rank", "User", "Distance", "CO2 Saved"], tablefmt="simple"))
            else:
                print("No users with recorded distances yet.")
            
            # Log to the database
            conn = database_manager.create_connection()
            if conn:
                database_manager.add_stat(conn, ("global", total_users, total_distance, total_co2_saved, total_calories))
                conn.close()
        
        except Exception as e:
            logging.error(f"Error viewing sustainability dashboard: {e}", exc_info=True)
            display_error_message(f"Error viewing sustainability dashboard: {e}")
        
        input("\nPress Enter to continue...")
    
    def _show_random_achievement(self, distance, co2, calories):
        """Show a random achievement or encouragement based on user stats."""
        achievements = [
            f"🏆 Amazing job! You've cycled {distance:.2f} km in total!",
            f"🌍 You've saved {co2:.2f} kg of CO2 emissions! That's making a difference!",
            f"🔥 You've burned {calories:.0f} calories through cycling! Keep it up!",
            "🚴 You're becoming a cycling champion! The planet thanks you!",
            "🌱 Your sustainable choices are helping create a greener future!",
            "⭐ You're a sustainability star! Keep pedaling for the planet!",
            f"💪 Impressive cycling stats! You're {(distance/100):.0f}% of the way to your next 100km milestone!"
        ]
        
        # Add special achievements based on milestones
        if distance >= 100:
            achievements.append("🏅 Century Rider: You've cycled more than 100km in total!")
        if distance >= 500:
            achievements.append("🥇 Road Warrior: You've cycled more than 500km! That's impressive!")
        if co2 >= 50:
            achievements.append("🌳 Climate Guardian: You've saved more than 50kg of CO2 emissions!")
        if calories >= 10000:
            achievements.append("🔥 Calorie Crusher: You've burned more than 10,000 calories cycling!")
        
        achievement = random.choice(achievements)
        print(f"\n{Fore.YELLOW}{achievement}{Style.RESET_ALL}")
