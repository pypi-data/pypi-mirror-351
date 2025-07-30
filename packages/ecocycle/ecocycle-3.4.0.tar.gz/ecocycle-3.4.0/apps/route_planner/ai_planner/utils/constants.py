"""
EcoCycle - AI Route Planner Constants Module
Contains all constants and configuration values for the AI Route Planner
"""
# Route types and categories
ROUTE_TYPES = ["commute", "leisure", "fitness", "family", "nature", "heritage"]
DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced", "expert"]
TERRAIN_TYPES = ["flat", "hilly", "mixed", "mountain"]

# Sample points of interest categories
POI_CATEGORIES = [
    "historical_sites", "viewpoints", "parks", "cafes", "water_features",
    "nature_reserves", "cultural_sites", "rest_areas"
]

# API Retry Configuration
MAX_RETRY_ATTEMPTS = 3               # Maximum number of retry attempts for API calls
BASE_RETRY_DELAY = 2                 # Base delay in seconds between retries
MAX_RETRY_DELAY = 60                 # Maximum delay in seconds between retries

# Cache Configuration
ROUTE_CACHE_EXPIRY = 60 * 60 * 24    # Route cache expiry time in seconds (24 hours)
CACHE_FILE_PATH = "data/cache/ai_route_cache.json"  # Path to the route cache file