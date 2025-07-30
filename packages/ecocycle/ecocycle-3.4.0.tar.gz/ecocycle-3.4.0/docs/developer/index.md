# EcoCycle Developer Documentation

Welcome to the EcoCycle developer documentation. This guide provides comprehensive information on extending and integrating with the EcoCycle application.

## Architecture Overview

EcoCycle follows a Model-View-Controller (MVC) architecture:

- **Models**: Data structures and business logic (`/models/`)
- **Views**: User interface components (`/views/`)
- **Controllers**: Application logic connecting models and views (`/controllers/`)

The application also includes cross-platform components:
- Web interface (`/web/`)
- Mobile applications (`/mobile/`)
- API endpoints for third-party integration

## Getting Started with Development

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/ecocycle/ecocycle.git
   cd ecocycle
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your development settings
   ```

4. Run tests to verify your setup:
   ```bash
   pytest
   ```

### Project Structure

```
ecocycle/
├── controllers/       # Application logic
├── models/            # Data models and business logic
├── views/             # Terminal UI components
├── web/               # Web application
│   ├── api/           # REST API endpoints
│   ├── static/        # Static assets
│   └── templates/     # HTML templates
├── mobile/            # Mobile app components
├── docs/              # Documentation
├── tests/             # Test suite
└── db/                # Database files and migrations
```

## API Documentation

EcoCycle provides a comprehensive REST API for integrating with external applications.

### Authentication

All API requests require authentication using OAuth 2.0 or API keys.

```python
import requests

# Example API request
response = requests.get(
    "https://api.ecocycle.org/v1/routes",
    headers={"Authorization": "Bearer YOUR_API_TOKEN"}
)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/routes` | GET | Get user's saved routes |
| `/api/v1/routes` | POST | Create a new route |
| `/api/v1/activities` | GET | Get user's activities |
| `/api/v1/activities` | POST | Log a new activity |
| `/api/v1/impact` | GET | Get environmental impact data |
| `/api/v1/profile` | GET | Get user profile |

For complete API documentation, see [API Reference](./api/reference.md).

## Extending EcoCycle

### Plugin Development

EcoCycle supports plugins for extending functionality. Plugins can add new features, integrate with external services, or modify existing behavior.

#### Plugin Structure

```python
from ecocycle.plugin import EcoCyclePlugin

class MyCustomPlugin(EcoCyclePlugin):
    """Example plugin that adds a custom feature."""
    
    def __init__(self):
        super().__init__(
            name="My Custom Plugin",
            version="1.0.0",
            description="Adds a custom feature to EcoCycle",
            author="Your Name"
        )
    
    def initialize(self):
        """Called when the plugin is loaded."""
        self.register_command("my_command", self.my_command_handler)
        self.register_hook("after_activity_save", self.process_activity)
    
    def my_command_handler(self, args):
        """Handle custom command."""
        # Implementation
        
    def process_activity(self, activity):
        """Process activity after it's saved."""
        # Implementation
```

See [Plugin Development Guide](./plugins/guide.md) for more details.

### Custom Data Visualizations

You can create custom visualizations by extending the `Visualization` base class:

```python
from ecocycle.visualizations import Visualization
import matplotlib.pyplot as plt

class CustomVisualization(Visualization):
    """Custom visualization example."""
    
    def __init__(self):
        super().__init__(
            name="My Custom Chart",
            description="Shows custom data in a unique way",
            required_data=["activities"]
        )
    
    def generate(self, data):
        """Generate the visualization."""
        fig, ax = plt.subplots()
        # Implementation
        return fig
```

### Contributing to EcoCycle

We welcome contributions to the core EcoCycle project. Please follow our [Contribution Guidelines](./contributing.md) when submitting pull requests.

## Integration Examples

### Strava Integration

```python
from ecocycle.integrations import OAuth2Integration

class StravaIntegration(OAuth2Integration):
    """Integration with Strava API."""
    
    def __init__(self):
        super().__init__(
            name="Strava",
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            authorize_url="https://www.strava.com/oauth/authorize",
            token_url="https://www.strava.com/oauth/token",
            scopes=["read", "activity:read"]
        )
    
    def import_activities(self, user_id):
        """Import activities from Strava."""
        token = self.get_user_token(user_id)
        # Implementation
```

### Weather Service Integration

```python
from ecocycle.integrations import APIIntegration

class WeatherIntegration(APIIntegration):
    """Integration with weather service."""
    
    def __init__(self):
        super().__init__(
            name="Weather Service",
            base_url="https://api.weatherservice.com",
            api_key=WEATHER_API_KEY
        )
    
    def get_forecast(self, latitude, longitude):
        """Get weather forecast for a location."""
        endpoint = f"/forecast?lat={latitude}&lon={longitude}&units=metric"
        return self.make_request("GET", endpoint)
```

## Troubleshooting Development Issues

For common development issues and solutions, see the [Development Troubleshooting Guide](./troubleshooting.md).

## Release Process

Information about the EcoCycle release process, versioning, and changelog management can be found in the [Release Guide](./releases.md).

## Need Help?

If you need assistance with development:

- Check the [Developer FAQ](./faq.md)
- Join our [Developer Forum](https://ecocycle.org/forum/technical)
- Contact the development team at developers@ecocycle.org
