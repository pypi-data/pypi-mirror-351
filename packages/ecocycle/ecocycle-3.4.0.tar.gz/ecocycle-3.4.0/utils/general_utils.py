"""
EcoCycle - Utilities Module
Contains utility functions for calculations, formatting, and common operations.
"""
import math
import re
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, Union

logger = logging.getLogger(__name__)


def calculate_distance(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> float:
    """
    Calculate the distance between two points using the Haversine formula.

    Args:
        start_lat (float): Starting point latitude
        start_lon (float): Starting point longitude
        end_lat (float): Ending point latitude
        end_lon (float): Ending point longitude

    Returns:
        float: Distance in kilometers
    """
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    start_lat_rad = math.radians(start_lat)
    start_lon_rad = math.radians(start_lon)
    end_lat_rad = math.radians(end_lat)
    end_lon_rad = math.radians(end_lon)

    # Haversine formula
    dlon = end_lon_rad - start_lon_rad
    dlat = end_lat_rad - start_lat_rad

    a = math.sin(dlat / 2)**2 + math.cos(start_lat_rad) * math.cos(end_lat_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance
    distance = R * c

    return distance


def calculate_calories(distance_km: float, speed_kph: float, weight_kg: int) -> int:
    """
    Calculate calories burned during cycling based on distance, speed, and weight.

    Args:
        distance_km (float): Distance in kilometers
        speed_kph (float): Speed in kilometers per hour
        weight_kg (int): Weight in kilograms

    Returns:
        int: Calories burned
    """
    # Cycling MET (Metabolic Equivalent of Task) values for different speeds
    # MET values from the Compendium of Physical Activities
    if speed_kph < 16:  # Leisure cycling
        met = 4.0
    elif speed_kph < 20:  # Moderate cycling
        met = 6.0
    elif speed_kph < 25:  # Vigorous cycling
        met = 8.0
    elif speed_kph < 30:  # Fast cycling
        met = 10.0
    else:  # Racing
        met = 12.0

    # Calculate duration in hours
    if speed_kph > 0:
        duration_hours = distance_km / speed_kph
    else:
        duration_hours = 0

    # Calories = MET * weight (kg) * duration (hours) * 3.5 / 200
    calories = int(met * weight_kg * duration_hours * 3.5 / 200 * 1000)

    return calories


def calculate_co2_saved(distance_km: float) -> float:
    """
    Calculate CO2 emissions saved by cycling instead of driving.

    Args:
        distance_km (float): Distance in kilometers

    Returns:
        float: CO2 saved in kilograms
    """
    # Average CO2 emissions per kilometer for a passenger car (in kg)
    # Values from European Environment Agency
    car_co2_per_km = 0.130  # 130g/km = 0.130kg/km

    # Calculate CO2 saved (cycling produces negligible CO2)
    co2_saved = distance_km * car_co2_per_km

    return co2_saved


def format_distance(distance_km: float) -> str:
    """
    Format distance with appropriate units.

    Args:
        distance_km (float): Distance in kilometers

    Returns:
        str: Formatted distance string
    """
    if distance_km < 1:
        return f"{distance_km * 1000:.0f} m"
    else:
        return f"{distance_km:.1f} km"


def format_co2(co2_kg: float) -> str:
    """
    Format CO2 with appropriate units.

    Args:
        co2_kg (float): CO2 in kilograms

    Returns:
        str: Formatted CO2 string
    """
    if co2_kg < 1:
        return f"{co2_kg * 1000:.0f} g CO2"
    else:
        return f"{co2_kg:.2f} kg CO2"


def format_calories(calories: int) -> str:
    """
    Format calories.

    Args:
        calories (int): Calories burned

    Returns:
        str: Formatted calories string
    """
    return f"{calories} kcal"


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email (str): Email address to validate

    Returns:
        bool: True if email is valid, False otherwise
    """
    # Basic email validation pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def get_date_range(date_str: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a date range string and return start and end dates.
    Supports formats like 'YYYY-MM-DD', 'YYYY-MM-DD to YYYY-MM-DD', 'last week', 'this month', etc.

    Args:
        date_str (str): Date range string

    Returns:
        tuple: (start_date, end_date) in 'YYYY-MM-DD' format
    """
    if not date_str:
        return None, None

    today = datetime.now().date()

    # Check if it's a specific date
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str, date_str

    # Check if it's a date range with "to" separator
    range_match = re.match(r'^(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})$', date_str)
    if range_match:
        start_date, end_date = range_match.groups()
        return start_date, end_date

    # Handle relative date ranges
    date_str = date_str.lower()

    if date_str == 'today':
        return today.isoformat(), today.isoformat()

    if date_str == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday.isoformat(), yesterday.isoformat()

    if date_str == 'this week':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week.isoformat(), end_of_week.isoformat()

    if date_str == 'last week':
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        return start_of_last_week.isoformat(), end_of_last_week.isoformat()

    if date_str == 'this month':
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        return start_of_month.isoformat(), end_of_month.isoformat()

    if date_str == 'last month':
        if today.month == 1:
            start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            end_of_last_month = today.replace(year=today.year, month=1, day=1) - timedelta(days=1)
        else:
            start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(month=today.month, day=1) - timedelta(days=1)
        return start_of_last_month.isoformat(), end_of_last_month.isoformat()

    if date_str == 'this year':
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        return start_of_year.isoformat(), end_of_year.isoformat()

    if date_str == 'last year':
        start_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
        end_of_last_year = today.replace(year=today.year - 1, month=12, day=31)
        return start_of_last_year.isoformat(), end_of_last_year.isoformat()

    # None of the patterns matched
    logger.warning(f"Could not parse date range: {date_str}")
    return None, None


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit.

    Args:
        celsius (float): Temperature in Celsius

    Returns:
        float: Temperature in Fahrenheit
    """
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Convert Fahrenheit to Celsius.

    Args:
        fahrenheit (float): Temperature in Fahrenheit

    Returns:
        float: Temperature in Celsius
    """
    return (fahrenheit - 32) * 5/9


def meters_per_second_to_kmh(speed_mps: float) -> float:
    """
    Convert speed from meters per second to kilometers per hour.

    Args:
        speed_mps (float): Speed in meters per second

    Returns:
        float: Speed in kilometers per hour
    """
    return speed_mps * 3.6


def kmh_to_mph(speed_kmh: float) -> float:
    """
    Convert speed from kilometers per hour to miles per hour.

    Args:
        speed_kmh (float): Speed in kilometers per hour

    Returns:
        float: Speed in miles per hour
    """
    return speed_kmh * 0.621371


def mph_to_kmh(speed_mph: float) -> float:
    """
    Convert speed from miles per hour to kilometers per hour.

    Args:
        speed_mph (float): Speed in miles per hour

    Returns:
        float: Speed in kilometers per hour
    """
    return speed_mph * 1.60934


def km_to_miles(distance_km: float) -> float:
    """
    Convert distance from kilometers to miles.

    Args:
        distance_km (float): Distance in kilometers

    Returns:
        float: Distance in miles
    """
    return distance_km * 0.621371


def miles_to_km(distance_miles: float) -> float:
    """
    Convert distance from miles to kilometers.

    Args:
        distance_miles (float): Distance in miles

    Returns:
        float: Distance in kilometers
    """
    return distance_miles * 1.60934


def calculate_average_speed(distance_km: float, duration_minutes: float) -> float:
    """
    Calculate average speed from distance and duration.

    Args:
        distance_km (float): Distance in kilometers
        duration_minutes (float): Duration in minutes

    Returns:
        float: Speed in kilometers per hour
    """
    if duration_minutes <= 0:
        return 0.0

    # Convert duration to hours
    duration_hours = duration_minutes / 60.0

    # Calculate speed
    speed = distance_km / duration_hours

    return speed


def is_valid_phone_number(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone (str): Phone number to validate

    Returns:
        bool: True if phone number is valid, False otherwise
    """
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Check if we have a valid number of digits (8-15)
    return 8 <= len(digits) <= 15


def format_phone_number(phone: str) -> str:
    """
    Format a phone number to standard international format.

    Args:
        phone (str): Phone number to format

    Returns:
        str: Formatted phone number
    """
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', phone)

    # Handle international prefix
    if digits.startswith('00'):
        digits = '+' + digits[2:]
    elif not digits.startswith('+'):
        # Assume local number, add default country code (+1 for US)
        digits = '+1' + digits

    return digits


def truncate_string(text: str, max_length: int, ellipsis: str = '...') -> str:
    """
    Truncate a string to a maximum length with an ellipsis.

    Args:
        text (str): The string to truncate
        max_length (int): Maximum length
        ellipsis (str): Ellipsis to add if truncated

    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text

    # Calculate the actual truncation point, accounting for the ellipsis
    truncate_at = max_length - len(ellipsis)

    # Find the last space before the truncation point to avoid cutting words
    last_space = text[:truncate_at].rfind(' ')

    if last_space > 0:
        # Truncate at the last space
        return text[:last_space] + ellipsis
    else:
        # No space found, truncate at the exact point
        return text[:truncate_at] + ellipsis


def get_current_date_str() -> str:
    """
    Get the current date as a string in YYYY-MM-DD format.

    Returns:
        str: Current date in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse a date string in the format YYYY-MM-DD.

    Args:
        date_str (str): Date string in YYYY-MM-DD format

    Returns:
        Optional[datetime]: Datetime object if parsing is successful, None otherwise
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logger.warning(f"Could not parse date: {date_str}")
        return None


if __name__ == "__main__":
    # Test utility functions
    print("Distance calculation:")
    # New York to Los Angeles (approximate)
    distance = calculate_distance(40.7128, -74.0060, 34.0522, -118.2437)
    print(f"NY to LA: {distance:.1f} km")

    print("\nCalorie calculation:")
    calories = calculate_calories(25.0, 18.0, 70)
    print(f"25 km at 18 km/h for 70 kg person: {calories} kcal")

    print("\nCO2 saved calculation:")
    co2 = calculate_co2_saved(10.0)
    print(f"10 km cycling instead of driving: {co2:.2f} kg CO2 saved")

    print("\nFormatting examples:")
    print(f"Distance: {format_distance(12.5)}")
    print(f"Distance: {format_distance(0.75)}")
    print(f"CO2: {format_co2(2.45)}")
    print(f"CO2: {format_co2(0.045)}")
    print(f"Calories: {format_calories(350)}")

    print("\nDate range parsing:")
    date_ranges = [
        "2023-04-15",
        "2023-04-01 to 2023-04-15",
        "today",
        "yesterday",
        "this week",
        "last week",
        "this month",
        "last month"
    ]

    for date_range in date_ranges:
        start, end = get_date_range(date_range)
        print(f"{date_range}: {start} to {end}")

    print("\nConversion functions:")
    print(f"20°C = {celsius_to_fahrenheit(20):.1f}°F")
    print(f"68°F = {fahrenheit_to_celsius(68):.1f}°C")
    print(f"10 m/s = {meters_per_second_to_kmh(10):.1f} km/h")
    print(f"25 km/h = {kmh_to_mph(25):.1f} mph")
    print(f"30 mph = {mph_to_kmh(30):.1f} km/h")
    print(f"100 km = {km_to_miles(100):.1f} miles")
    print(f"100 miles = {miles_to_km(100):.1f} km")

    print("\nAverage speed calculation:")
    speed = calculate_average_speed(30.0, 90.0)
    print(f"30 km in 90 minutes: {speed:.1f} km/h")
