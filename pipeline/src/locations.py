"""
Centralized definition of weather locations used throughout the application.
"""

# Define weather locations with coordinates and human-readable names
WEATHER_LOCATIONS = {
    "40.7128 -74.0060": "new_york",
    "34.0522 -118.2437": "los_angeles",
    "41.8781 -87.6298": "chicago",
    "29.7604 -95.3698": "houston",
    "33.4484 -112.0740": "phoenix",
}


# Get list of location coordinates for partitioning
def get_location_keys():
    return list(WEATHER_LOCATIONS.keys())


# Get location name from coordinates
def get_location_name(coordinate_key, default="unknown_location"):
    return WEATHER_LOCATIONS.get(coordinate_key, default)
