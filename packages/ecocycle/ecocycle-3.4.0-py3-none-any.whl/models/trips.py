"""
EcoCycle - Trip Management Module
Handles trip data management and operations.
"""
import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import config.config as config

logger = logging.getLogger(__name__)


class Trip:
    """Represents a cycling trip."""

    def __init__(self, trip_id: str, user_id: str, name: str, distance: float,
                 duration: float, start_time: float, end_time: float,
                 co2_saved: float, calories: int, start_location: Optional[Dict] = None,
                 end_location: Optional[Dict] = None, tracking_id: Optional[str] = None):
        """
        Initialize a Trip object.

        Args:
            trip_id (str): Unique trip identifier
            user_id (str): User who took the trip
            name (str): Trip name
            distance (float): Distance in kilometers
            duration (float): Duration in seconds
            start_time (float): Start timestamp
            end_time (float): End timestamp
            co2_saved (float): CO2 saved in kg
            calories (int): Calories burned
            start_location (Dict): Starting location coordinates
            end_location (Dict): Ending location coordinates
            tracking_id (str): Associated tracking session ID
        """
        self.trip_id = trip_id
        self.user_id = user_id
        self.name = name
        self.distance = distance
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time
        self.co2_saved = co2_saved
        self.calories = calories
        self.start_location = start_location or {}
        self.end_location = end_location or {}
        self.tracking_id = tracking_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert trip to dictionary."""
        return {
            'id': self.trip_id,
            'user_id': self.user_id,
            'name': self.name,
            'distance': self.distance,
            'duration': self.duration,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'co2_saved': self.co2_saved,
            'calories': self.calories,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'tracking_id': self.tracking_id,
            'date': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trip':
        """Create Trip from dictionary."""
        return cls(
            trip_id=data.get('id', ''),
            user_id=data.get('user_id', ''),
            name=data.get('name', ''),
            distance=float(data.get('distance', 0)),
            duration=float(data.get('duration', 0)),
            start_time=float(data.get('start_time', 0)),
            end_time=float(data.get('end_time', 0)),
            co2_saved=float(data.get('co2_saved', 0)),
            calories=int(data.get('calories', 0)),
            start_location=data.get('start_location', {}),
            end_location=data.get('end_location', {}),
            tracking_id=data.get('tracking_id')
        )


class TripManager:
    """Manages trip data and operations."""

    def __init__(self):
        """Initialize the TripManager."""
        self.trips_file = os.path.join(config.DATA_DIR, 'trips.json')
        self.trips = self._load_trips()

    def _load_trips(self) -> Dict[str, List[Dict]]:
        """Load trips from file."""
        try:
            if os.path.exists(self.trips_file):
                with open(self.trips_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading trips: {e}")
            return {}

    def _save_trips(self) -> bool:
        """Save trips to file."""
        try:
            os.makedirs(os.path.dirname(self.trips_file), exist_ok=True)
            with open(self.trips_file, 'w') as f:
                json.dump(self.trips, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving trips: {e}")
            return False

    def create_trip(self, user_id: str, trip_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new trip.

        Args:
            user_id (str): User ID
            trip_data (Dict): Trip data

        Returns:
            Optional[str]: Trip ID if successful, None otherwise
        """
        try:
            # Generate unique trip ID
            trip_id = f"trip_{user_id}_{int(time.time())}"

            # Create trip object
            trip = Trip(
                trip_id=trip_id,
                user_id=user_id,
                name=trip_data.get('name', f'Trip {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
                distance=float(trip_data.get('distance', 0)),
                duration=float(trip_data.get('duration', 0)),
                start_time=float(trip_data.get('start_time', time.time())),
                end_time=float(trip_data.get('end_time', time.time())),
                co2_saved=float(trip_data.get('co2_saved', 0)),
                calories=int(trip_data.get('calories', 0)),
                start_location=trip_data.get('start_location', {}),
                end_location=trip_data.get('end_location', {}),
                tracking_id=trip_data.get('tracking_id')
            )

            # Add to trips
            if user_id not in self.trips:
                self.trips[user_id] = []

            self.trips[user_id].append(trip.to_dict())

            # Save to file
            if self._save_trips():
                logger.info(f"Trip {trip_id} created for user {user_id}")
                return trip_id
            else:
                logger.error(f"Failed to save trip {trip_id}")
                return None

        except Exception as e:
            logger.error(f"Error creating trip: {e}")
            return None

    def get_user_trips(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all trips for a user.

        Args:
            user_id (str): User ID

        Returns:
            List[Dict]: List of trip dictionaries
        """
        try:
            user_trips = self.trips.get(user_id, [])
            # Sort by start_time descending (newest first)
            return sorted(user_trips, key=lambda x: x.get('start_time', 0), reverse=True)
        except Exception as e:
            logger.error(f"Error getting trips for user {user_id}: {e}")
            return []

    def get_trip(self, user_id: str, trip_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific trip.

        Args:
            user_id (str): User ID
            trip_id (str): Trip ID

        Returns:
            Dict: Trip data if found, None otherwise
        """
        try:
            user_trips = self.trips.get(user_id, [])
            for trip in user_trips:
                if trip.get('id') == trip_id:
                    return trip
            return None
        except Exception as e:
            logger.error(f"Error getting trip {trip_id} for user {user_id}: {e}")
            return None

    def update_trip(self, user_id: str, trip_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a trip.

        Args:
            user_id (str): User ID
            trip_id (str): Trip ID
            update_data (Dict): Data to update

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_trips = self.trips.get(user_id, [])
            for i, trip in enumerate(user_trips):
                if trip.get('id') == trip_id:
                    # Update trip data
                    trip.update(update_data)
                    self.trips[user_id][i] = trip

                    # Save to file
                    if self._save_trips():
                        logger.info(f"Trip {trip_id} updated for user {user_id}")
                        return True
                    else:
                        logger.error(f"Failed to save updated trip {trip_id}")
                        return False

            logger.warning(f"Trip {trip_id} not found for user {user_id}")
            return False

        except Exception as e:
            logger.error(f"Error updating trip {trip_id} for user {user_id}: {e}")
            return False

    def delete_trip(self, user_id: str, trip_id: str) -> bool:
        """
        Delete a trip.

        Args:
            user_id (str): User ID
            trip_id (str): Trip ID

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_trips = self.trips.get(user_id, [])
            for i, trip in enumerate(user_trips):
                if trip.get('id') == trip_id:
                    # Remove trip
                    del self.trips[user_id][i]

                    # Save to file
                    if self._save_trips():
                        logger.info(f"Trip {trip_id} deleted for user {user_id}")
                        return True
                    else:
                        logger.error(f"Failed to save after deleting trip {trip_id}")
                        return False

            logger.warning(f"Trip {trip_id} not found for user {user_id}")
            return False

        except Exception as e:
            logger.error(f"Error deleting trip {trip_id} for user {user_id}: {e}")
            return False
