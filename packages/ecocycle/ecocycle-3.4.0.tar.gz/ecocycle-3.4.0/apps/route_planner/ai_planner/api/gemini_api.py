"""
EcoCycle - Gemini API Integration Module
Provides functionality for interacting with Google's Gemini API
"""
import os
import time
import logging
import random
import threading
from typing import Dict, Any, Optional, Tuple, Union, List

from ..utils.constants import MAX_RETRY_ATTEMPTS, BASE_RETRY_DELAY, MAX_RETRY_DELAY

# Configure logging
logger = logging.getLogger(__name__)

# Flag to track if Gemini is available
GEMINI_AVAILABLE = False

# Try to import the Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiAPI:
    """Handles interactions with Google's Gemini API"""

    def __init__(self):
        """Initialize the Gemini API client"""
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.gemini_available = False
        self.default_model = None
        self.gemini_error = None
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # Initialize Gemini if possible
        self._initialize_gemini()

    def _initialize_gemini(self) -> bool:
        """Initialize the Gemini API with proper error handling"""
        global GEMINI_AVAILABLE

        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)

                # First check if the API is accessible by getting model list
                try:
                    models = genai.list_models()
                    supported_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                    logger.info(f"Available Gemini models: {supported_models}")

                    # Use the latest recommended model that's available
                    preferred_models = [
                        "models/gemini-2.0-flash-lite",
                    ]

                    self.default_model = None
                    for model in preferred_models:
                        if model in supported_models:
                            self.default_model = model
                            break

                    if not self.default_model:
                        logger.warning("No suitable Gemini model found. Using fallback.")
                        self.gemini_available = False
                        self.gemini_error = "No suitable model found"
                    else:
                        self.gemini_available = True
                        logger.info(f"Gemini API initialized successfully using model {self.default_model}")
                        return True
                except Exception as e:
                    logger.error(f"Error checking Gemini API models: {e}")
                    self.gemini_available = False
                    self.gemini_error = str(e)
            except Exception as e:
                logger.error(f"Error initializing Gemini API: {e}")
                self.gemini_available = False
                self.gemini_error = str(e)
        else:
            # Store the specific reason for API unavailability for better error messages
            if not GEMINI_AVAILABLE:
                self.gemini_error = "Package not installed"
            elif not self.api_key:
                self.gemini_error = "API key not set"
            else:
                self.gemini_error = "Unknown error"

            self.gemini_available = False

        return False

    def is_available(self) -> bool:
        """Check if the Gemini API is available for use"""
        return self.gemini_available

    def get_error(self) -> str:
        """Get the current error message if Gemini is unavailable"""
        return self.gemini_error or "Unknown error"

    def call_gemini_api(self, prompt: str, attempt: int = 1, progress_message: str = "Generating AI response") -> Tuple[bool, Union[str, Dict[str, str]]]:
        """Call the Gemini API with retry logic and progress indication

        Args:
            prompt: The prompt to send to the API
            attempt: The current attempt number (for retries)
            progress_message: Message to display during API call

        Returns:
            Tuple of (success, response_text) where response_text is either a string or an error dict
        """
        # Check if Gemini is available
        if not self.gemini_available:
            return False, {"error": f"Gemini API not available: {self.gemini_error}"}

        # Import progress indicators
        try:
            from yaspin import yaspin
            from yaspin.spinners import Spinners
            YASPIN_AVAILABLE = True
        except ImportError:
            YASPIN_AVAILABLE = False

        try:
            from rich.console import Console
            from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
            RICH_AVAILABLE = True
            console = Console()
        except ImportError:
            RICH_AVAILABLE = False

        def make_api_call():
            """Internal function to make the actual API call"""
            # Set up the model
            model = genai.GenerativeModel(
                model_name=self.default_model,
                generation_config=self.generation_config
            )
            # Make API request
            return model.generate_content(prompt)

        try:
            # Show visual progress bar during API call
            if RICH_AVAILABLE:
                from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn

                with Progress(
                    TextColumn(f"[bold blue]{progress_message}[/bold blue]"),
                    BarColumn(bar_width=40),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    transient=True
                ) as progress:
                    # Create a task that simulates API call progress
                    task = progress.add_task("Processing", total=100)

                    # Simulate progress during API call
                    from typing import Any
                    import threading
                    import time

                    # Flag to indicate when API call is complete
                    api_complete = threading.Event()
                    api_result: List[Any] = [None]
                    api_error: List[Any] = [None]

                    def api_call_thread():
                        try:
                            api_result[0] = make_api_call()
                        except Exception as e:
                            api_error[0] = e
                        finally:
                            api_complete.set()

                    # Start API call in background thread
                    thread = threading.Thread(target=api_call_thread)
                    thread.start()

                    # Animate progress bar while waiting for API
                    progress_value = 0.0
                    while not api_complete.is_set():
                        # Simulate gradual progress
                        if progress_value < 90:
                            progress_value += random.uniform(1, 3)
                            progress.update(task, completed=min(progress_value, 90))
                        time.sleep(0.1)

                    # Complete the progress bar
                    progress.update(task, completed=100)
                    thread.join()

                    if api_error[0]:
                        raise api_error[0]

                    if api_result[0] and hasattr(api_result[0], 'text'):
                        return True, api_result[0].text
                    else:
                        return False, {"error": "Invalid API response"}

            elif YASPIN_AVAILABLE:
                with yaspin(Spinners.dots, text=f"{progress_message}...", color="cyan") as spinner:
                    response = make_api_call()
                    spinner.ok("✅")
                    return True, response.text
            else:
                # Fallback with simple text progress bar
                print(f"{progress_message}...")

                # Simple ASCII progress bar
                import threading
                import time
                from typing import Any

                api_complete = threading.Event()
                api_result: List[Any] = [None]
                api_error: List[Any] = [None]

                def api_call_thread():
                    try:
                        api_result[0] = make_api_call()
                    except Exception as e:
                        api_error[0] = e
                    finally:
                        api_complete.set()

                # Start API call in background thread
                thread = threading.Thread(target=api_call_thread)
                thread.start()

                # Show ASCII progress bar
                bar_length = 30
                progress_chars = 0

                while not api_complete.is_set():
                    if progress_chars < bar_length - 2:
                        progress_chars += 1

                    # Create progress bar
                    filled = "█" * progress_chars
                    empty = "░" * (bar_length - progress_chars)
                    percentage = int((progress_chars / bar_length) * 100)

                    print(f"\r[{filled}{empty}] {percentage}%", end="", flush=True)
                    time.sleep(0.2)

                # Complete the progress bar
                filled = "█" * bar_length
                print(f"\r[{filled}] 100% ✅", flush=True)
                thread.join()

                if api_error[0]:
                    raise api_error[0]

                if api_result[0] and hasattr(api_result[0], 'text'):
                    return True, api_result[0].text
                else:
                    return False, {"error": "Invalid API response"}

        except Exception as e:
            logger.error(f"Error generating content with Gemini (attempt {attempt}): {e}")

            # Check for API error and retry if needed
            if attempt < MAX_RETRY_ATTEMPTS:
                logger.warning(f"Gemini API error (attempt {attempt}/{MAX_RETRY_ATTEMPTS}): {e}")
                # Exponential backoff with jitter
                retry_delay = min(BASE_RETRY_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1), MAX_RETRY_DELAY)

                # Show retry message with progress
                retry_message = f"Retrying in {retry_delay:.1f}s (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS})"
                if RICH_AVAILABLE:
                    try:
                        from rich.console import Console
                        console = Console()
                        console.print(f"[yellow]{retry_message}[/yellow]")
                    except ImportError:
                        print(f"⚠️ {retry_message}")
                elif YASPIN_AVAILABLE:
                    print(f"⚠️ {retry_message}")
                else:
                    print(f"⚠️ {retry_message}")

                import time
                time.sleep(retry_delay)
                return self.call_gemini_api(prompt, attempt + 1, progress_message)
            else:
                logger.error(f"Max retry attempts reached for Gemini API: {e}")
                return False, {"error": f"API error after {MAX_RETRY_ATTEMPTS} attempts: {str(e)}"}

    def generate_route(self, location: str, preferences: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a route recommendation using Gemini

        Args:
            location: The location for the route
            preferences: Dictionary of user preferences for the route

        Returns:
            Tuple of (success, route_data)
        """
        # Prepare the prompt
        prompt = self._create_route_prompt(location, preferences)

        # Call the API with custom progress message
        success, response_text = self.call_gemini_api(prompt, progress_message="🧭 Generating route recommendation")

        if success:
            try:
                # Process the response to extract structured route data
                if isinstance(response_text, str):
                    route_data = self._parse_route_response(response_text, location, preferences)
                    return True, route_data
                else:
                    return False, {"error": "Invalid response format from API"}
            except Exception as e:
                logger.error(f"Error parsing Gemini route response: {e}")
                return False, {"error": f"Error parsing response: {e}"}
        else:
            # response_text is a dict with error information
            if isinstance(response_text, dict):
                return False, response_text
            else:
                return False, {"error": str(response_text)}

    def generate_alternative_routes(self, location: str, preferences: Dict[str, Any],
                                   priority_types: Optional[List[str]] = None) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, str]]]:
        """Generate multiple alternative route recommendations using Gemini

        Args:
            location: The location for the route
            preferences: Dictionary of user preferences for the route
            priority_types: List of priority types for alternative routes (e.g., ['scenic', 'quick', 'safe'])

        Returns:
            Tuple of (success, list_of_route_data_or_error_dict)
        """
        if priority_types is None:
            priority_types = ['scenic', 'quick', 'safe']

        alternative_routes = []
        success_count = 0
        errors = []

        # Create a separate prompt for each priority type
        for i, priority in enumerate(priority_types):
            # Prepare the prompt with the specific priority
            prompt = self._create_alternative_route_prompt(location, preferences, priority)

            # Call the API with custom progress message
            progress_msg = f"🔄 Generating {priority} route ({i+1}/{len(priority_types)})"
            success, response_text = self.call_gemini_api(prompt, progress_message=progress_msg)

            if success:
                try:
                    # Process the response to extract structured route data
                    if isinstance(response_text, str):
                        route_data = self._parse_route_response(response_text, location, preferences)
                        # Add the priority type and a more descriptive name
                        route_data['priority'] = priority
                        route_data['name'] = f"{priority.title()} Route: {route_data['name']}"
                        alternative_routes.append(route_data)
                        success_count += 1
                    else:
                        errors.append(f"Invalid response format for {priority} route")
                except Exception as e:
                    error_msg = f"Error parsing {priority} route response: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            else:
                if isinstance(response_text, dict):
                    errors.append(f"Failed to generate {priority} route: {response_text.get('error', 'Unknown error')}")
                else:
                    errors.append(f"Failed to generate {priority} route: {response_text}")

        # Return success if we generated at least one alternative route
        if success_count > 0:
            return True, alternative_routes
        else:
            # Return error dictionary
            error_message = "\n".join(errors) if errors else "Unknown error occurred"
            return False, {"error": error_message}

    def _create_route_prompt(self, location: str, preferences: Dict[str, Any]) -> str:
        """Create a prompt for generating a route recommendation"""
        # Extract preferences
        preferred_distance = preferences.get('preferred_distance', 10)
        preferred_difficulty = preferences.get('preferred_difficulty', 'intermediate')
        preferred_terrain = preferences.get('preferred_terrain', 'mixed')
        preferred_route_types = ", ".join(preferences.get('preferred_route_types', ['leisure', 'nature']))
        points_of_interest = ", ".join(preferences.get('points_of_interest', ['viewpoints', 'parks']))

        # Create the prompt
        prompt = f"""
        Generate a detailed cycling route recommendation for a cyclist in {location}.

        Cyclist preferences:
        - Preferred distance: around {preferred_distance} km
        - Difficulty level: {preferred_difficulty}
        - Terrain type: {preferred_terrain}
        - Route types of interest: {preferred_route_types}
        - Points of interest: {points_of_interest}

        Please provide:
        1. A name for the route
        2. A detailed description including starting point, key waypoints, and ending point
        3. Total distance in kilometers
        4. Estimated difficulty level (beginner, intermediate, advanced, expert)
        5. Terrain type description
        6. Key points of interest along the route
        7. Safety considerations and tips
        8. Best time of day/year to ride this route
        9. A turn-by-turn summary of directions

        Format your response in clear sections with descriptive headers.
        Include enough detail that someone unfamiliar with the area could follow the route.
        """

        return prompt

    def _create_alternative_route_prompt(self, location: str, preferences: Dict[str, Any], priority: str) -> str:
        """Create a prompt for generating an alternative route with specific priority

        Args:
            location: The location for the route
            preferences: Dictionary of user preferences for the route
            priority: The priority for this alternative route (scenic, quick, safe)

        Returns:
            Formatted prompt string
        """
        # Extract preferences
        preferred_distance = preferences.get('preferred_distance', 10)
        preferred_difficulty = preferences.get('preferred_difficulty', 'intermediate')
        preferred_terrain = preferences.get('preferred_terrain', 'mixed')
        preferred_route_types = ", ".join(preferences.get('preferred_route_types', ['leisure', 'nature']))
        points_of_interest = ", ".join(preferences.get('points_of_interest', ['viewpoints', 'parks']))

        # Adjust the prompt based on priority
        priority_descriptions = {
            'scenic': "Create a highly scenic route that maximizes beautiful views, natural landscapes, and photo opportunities.",
            'quick': "Create an efficient and direct route that minimizes travel time while still being safe for cycling.",
            'safe': "Create a route that prioritizes cyclist safety with dedicated bike lanes, low traffic areas, and good visibility.",
            'family': "Create a family-friendly route suitable for children with easy terrain, rest stops, and interesting points for kids.",
            'challenging': "Create a challenging route with more elevation gain, technical sections, and a higher difficulty level."
        }

        priority_description = priority_descriptions.get(priority, "Create a balanced route that considers various factors important to cyclists.")

        # Create the prompt
        prompt = f"""
        Generate a detailed cycling route recommendation for a cyclist in {location}.

        THIS IS A {priority.upper()} PRIORITY ROUTE. {priority_description}

        Cyclist preferences:
        - Preferred distance: around {preferred_distance} km
        - Base difficulty level: {preferred_difficulty}
        - Preferred terrain type: {preferred_terrain}
        - Route types of interest: {preferred_route_types}
        - Points of interest: {points_of_interest}

        Please provide:
        1. A descriptive name for the route that highlights its {priority} nature
        2. A detailed description including starting point, key waypoints, and ending point
        3. Total distance in kilometers
        4. Estimated difficulty level (beginner, intermediate, advanced, expert)
        5. Terrain type description
        6. Key points of interest along the route
        7. Safety considerations and tips
        8. Best time of day/year to ride this route
        9. A turn-by-turn summary of directions
        10. Elevation profile description (flat, moderate hills, challenging climbs)

        Make sure to emphasize the {priority} aspects of this route in your description.
        Format your response in clear sections with descriptive headers.
        """

        return prompt

    def _parse_route_response(self, response_text: str, location: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the API response into a structured route object"""
        # For now, return a simple dictionary with the raw response
        # In a production system, you would parse the response into a structured format
        return {
            "name": "AI Generated Route", # This would be extracted from the response
            "location": location,
            "description": response_text,
            "distance": preferences.get('preferred_distance', 10),  # Would extract from response
            "difficulty": preferences.get('preferred_difficulty', 'intermediate'),  # Would extract from response
            "terrain": preferences.get('preferred_terrain', 'mixed'),  # Would extract from response
            "route_types": preferences.get('preferred_route_types', []),
            "points_of_interest": preferences.get('points_of_interest', []),
            "raw_response": response_text,
            "generated_at": time.time()
        }