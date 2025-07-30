"""
EcoCycle - Data Visualization Module
Provides data visualization capabilities for cycling data and statistics.
This is a wrapper module that imports and uses the modular implementation from the data_viz package.
"""
import logging
from apps.data_viz import DataVisualization

logger = logging.getLogger(__name__)

# This module is maintained for backward compatibility
# The actual implementation has been moved to the data_viz package in a modular structure
# See apps/data_viz/* for the new implementation

def get_error_message():
    """Return an error message if someone tries to use this module directly."""
    return "This module has been replaced with a modular implementation. Please import from apps.data_viz instead."

# If someone tries to run this module directly
if __name__ == "__main__":
    print(get_error_message())
    print("To use the data visualization features, import from apps.data_viz instead.")
    print("Example: from apps.data_viz import DataVisualization")