# EcoCycle User Guide

## Introduction

Welcome to EcoCycle, a command-line application designed to help cyclists track their cycling activities, calculate their positive environmental impact, and engage with a community of environmentally conscious cyclists.

This guide will help you understand the features of EcoCycle and how to use them effectively.

## Table of Contents

1. [Getting Started](#getting-started)
   - [Installation](#installation)
   - [First Run](#first-run)
   - [User Authentication](#user-authentication)
2. [Core Features](#core-features)
   - [Logging Cycling Trips](#logging-cycling-trips)
   - [Viewing Statistics](#viewing-statistics)
   - [Data Visualization](#data-visualization)
   - [Carbon Footprint Calculator](#carbon-footprint-calculator)
   - [Weather and Route Planner](#weather-and-route-planner)
   - [Social Sharing and Achievements](#social-sharing-and-achievements)
   - [Notification System](#notification-system)
3. [Command-Line Interface](#command-line-interface)
   - [Basic Commands](#basic-commands)
   - [Advanced Commands](#advanced-commands)
4. [Settings and Preferences](#settings-and-preferences)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

## Getting Started

### Installation

#### Using pip (recommended)

```bash
pip install ecocycle
```

#### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ecocycle.git
   cd ecocycle
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### First Run

After installation, you can start EcoCycle by running:

```bash
python main.py
```

On first run, the application will:
- Check for required dependencies and offer to install any missing ones
- Create necessary configuration files and directories
- Guide you through the initial setup process

### User Authentication

EcoCycle offers the following authentication options:

1. **Guest Mode**: Quick access with limited features
2. **Local Account**: Create a local user profile for full functionality
3. **Google Sign-In**: Use your Google account for enhanced features and cloud sync (requires additional setup)

To authenticate:
1. From the main menu, select "Login"
2. Choose your preferred authentication method
3. Follow the on-screen prompts

## Core Features

### Logging Cycling Trips

The core functionality of EcoCycle allows you to log your cycling trips:

1. From the main menu, select "Log a cycling trip"
2. Enter the trip details:
   - Date (defaults to today)
   - Distance in kilometers
   - Duration in minutes
   - Your weight (for calorie calculation, asked only once)
3. Review the trip summary, which includes:
   - Average speed
   - Calories burned
   - CO2 emissions saved
4. Confirm to save the trip

### Viewing Statistics

EcoCycle provides comprehensive statistics on your cycling activities:

1. From the main menu, select "View statistics"
2. View your overall statistics:
   - Total trips
   - Total distance
   - Total CO2 saved
   - Total calories burned
3. View averages per trip
4. Check your recent trips history
5. Access detailed data visualization (if available)

### Data Visualization

For deeper insights, EcoCycle offers advanced data visualization:

1. From the Statistics screen, select "View detailed charts and graphs"
2. Choose from various visualization options:
   - Activity Summary Dashboard
   - Trip History Analysis
   - Carbon Savings Visualization
   - Progress Over Time
   - Generate PDF Report
   - Export Data

### Carbon Footprint Calculator

Calculate your carbon footprint and see how cycling helps reduce it:

1. From the main menu, select "Calculate carbon footprint"
2. Choose whether to calculate for:
   - Transportation choices
   - Home energy usage
   - Food consumption
   - Other lifestyle factors
3. View your total carbon footprint
4. See how your cycling activities are offsetting your carbon emissions
5. Get personalized recommendations for reducing your carbon footprint

### Weather and Route Planner

Plan your cycling trips with weather and route information:

1. From the main menu, select "Weather and route planning"
2. Choose from the following options:
   - Check weather forecast for cycling
   - Plan a cycling route
   - View saved routes
   - Calculate cycling environmental impact

This feature requires internet connectivity and may use external APIs for weather data and mapping.

### Social Sharing and Achievements

Track your achievements and share your progress:

1. From the main menu, select "Social sharing and achievements"
2. View your earned achievements and progress toward new ones
3. Check the global leaderboard
4. View and join cycling challenges
5. Generate shareable images with your stats
6. View the community's collective environmental impact

### Notification System

Stay motivated with customizable notifications:

1. From the main menu, select "Manage notifications"
2. Configure your notification preferences:
   - Email notifications
   - SMS notifications
   - Achievement notifications
   - Weekly summary
   - Eco tips
   - Reminder frequency
3. Update your contact information
4. View your notification history
5. Test notifications to ensure they're working correctly

## Command-Line Interface

EcoCycle offers a powerful command-line interface for advanced users.

### Basic Commands

```bash
# Start the application with the interactive menu
python main.py

# View your statistics
python main.py stats

# Check weather for cycling
python main.py weather --location "New York"

# Export your data
python main.py export --format csv --output cycling_data.csv
```

### Advanced Commands

```bash
# Update the application
python main.py update

# Run system diagnostics
python main.py doctor

# Get help on available commands
python main.py help
```

### Menu Navigation

In the interactive menu:
- Use `0` to exit the application
- Enter the number corresponding to your desired option (1-9)
- Press Enter to confirm your selection

## Settings and Preferences

Customize EcoCycle to suit your needs:

1. From the main menu, select "Settings and preferences"
2. Configure:
   - Weight (for calorie calculations)
   - Default transport mode
   - Theme
   - Notification settings

Your settings are saved automatically and will be applied each time you run EcoCycle.

## Troubleshooting

### Common Issues

**Problem**: Missing dependencies  
**Solution**: Run `python main.py doctor` to diagnose and fix dependency issues

**Problem**: Authentication failures  
**Solution**: Check your internet connection and ensure you're using the correct credentials

**Problem**: Data not saving  
**Solution**: Check file permissions in your user directory

### Logging

EcoCycle maintains logs to help diagnose issues:

- `ecocycle.log`: General application logs
- `ecocycle_debug.log`: Detailed debug information
- `ecocycle_web.log`: Web communication logs (for API interactions)

## FAQ

**Q: Is my data private?**  
A: Yes, by default, all your data is stored locally on your computer. If you use Google Sign-In, some data may be synchronized to your Google account, but this is optional and configurable.

**Q: How accurate are the calorie and CO2 calculations?**  
A: The calculations are based on widely accepted formulas and research. Calorie calculations consider distance, speed, and weight. CO2 calculations are based on average emissions from comparable car travel.

**Q: Can I use EcoCycle offline?**  
A: Yes, most features work offline. Weather and route planning require internet connectivity, as do social features and cloud synchronization.

**Q: How do I back up my data?**  
A: Your data is stored in files in the application directory. You can back these up manually, or enable cloud synchronization for automatic backups.

**Q: Can I track other activities besides cycling?**  
A: Currently, EcoCycle is optimized for cycling. Support for other eco-friendly transportation modes may be added in future versions.

---

Thank you for using EcoCycle and contributing to a greener world, one bike ride at a time!