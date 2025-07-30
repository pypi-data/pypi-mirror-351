# Weather Extension Plugin

Extended weather information for EcoCycle.

## Description

This plugin provides extended weather information for EcoCycle, including:

- Detailed weather data
- Air quality information
- Weather alerts
- Detailed weather forecasts

## Installation

1. Copy this directory to the `plugins` directory in your EcoCycle installation.
2. Ensure the `requests` package is installed.
3. Restart EcoCycle.

## Usage

The plugin provides the following hooks:

- `get_extended_weather(location)`: Get extended weather information for a location
- `get_air_quality(location)`: Get air quality information for a location
- `get_weather_alerts(location)`: Get weather alerts for a location
- `get_weather_forecast_details(location, days=5)`: Get detailed weather forecast for a location

Example usage:

```python
from core.plugin.plugin_manager import plugin_manager

# Load all plugins
plugin_manager.load_all_plugins()

# Check if the plugin is loaded
if plugin_manager.get_plugin("weather_extension"):
    # Call a hook
    results = plugin_manager.call_hook("get_extended_weather", "New York")
    if results:
        extended_weather = results[0]
        print(f"Temperature: {extended_weather['temperature']}°C")
        print(f"Feels like: {extended_weather['feels_like']}°C")
        print(f"Humidity: {extended_weather['humidity']}%")
```

## License

Apache License
