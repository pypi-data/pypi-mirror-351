#!/usr/bin/env python3
"""
EcoCycle - Plugin Manager Module
Provides a plugin system for extending application functionality.
"""
import os
import sys
import importlib.util
import inspect
import logging
import json
import pkgutil
from typing import Dict, List, Any, Optional, Type, Callable, Set, Union, Tuple

# Import config module for paths
try:
    import config.config as config
    # Use config module for log directory
    LOG_DIR = config.LOG_DIR
    PLUGINS_DIR = os.path.join(config.PROJECT_ROOT, 'plugins')
except ImportError:
    # Fallback if config module is not available
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Logs')
    PLUGINS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'plugins')

# Ensure log and plugins directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PLUGINS_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'plugin_manager.log'))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Plugin metadata file name
PLUGIN_METADATA_FILE = 'plugin.json'

# Plugin interface class
class PluginInterface:
    """Base interface that all plugins must implement."""

    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        raise NotImplementedError("Plugin must implement 'name' property")

    @property
    def version(self) -> str:
        """Get the version of the plugin."""
        raise NotImplementedError("Plugin must implement 'version' property")

    @property
    def description(self) -> str:
        """Get the description of the plugin."""
        raise NotImplementedError("Plugin must implement 'description' property")

    @property
    def author(self) -> str:
        """Get the author of the plugin."""
        raise NotImplementedError("Plugin must implement 'author' property")

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise
        """
        raise NotImplementedError("Plugin must implement 'initialize' method")

    def shutdown(self) -> bool:
        """
        Shutdown the plugin.

        Returns:
            True if shutdown was successful, False otherwise
        """
        raise NotImplementedError("Plugin must implement 'shutdown' method")

    def get_hooks(self) -> Dict[str, Callable]:
        """
        Get the hooks provided by the plugin.

        Returns:
            Dictionary mapping hook names to hook functions
        """
        raise NotImplementedError("Plugin must implement 'get_hooks' method")


class PluginManager:
    """Manager for discovering, loading, and managing plugins."""

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of PluginManager exists."""
        if cls._instance is None:
            cls._instance = super(PluginManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the plugin manager."""
        if self._initialized:
            return

        self._plugins = {}  # name -> plugin instance
        self._plugin_modules = {}  # name -> module
        self._hooks = {}  # hook_name -> list of (plugin_name, hook_function)
        self._initialized = True

        # Add plugins directory to Python path
        if PLUGINS_DIR not in sys.path:
            sys.path.append(PLUGINS_DIR)

    def discover_plugins(self) -> List[Dict[str, Any]]:
        """
        Discover available plugins.

        Returns:
            List of plugin metadata dictionaries
        """
        plugins_metadata = []

        # Check if plugins directory exists
        if not os.path.exists(PLUGINS_DIR):
            logger.warning(f"Plugins directory not found: {PLUGINS_DIR}")
            return plugins_metadata

        # Iterate through plugin directories
        for item in os.listdir(PLUGINS_DIR):
            plugin_dir = os.path.join(PLUGINS_DIR, item)

            # Skip if not a directory
            if not os.path.isdir(plugin_dir):
                continue

            # Check for plugin metadata file
            metadata_file = os.path.join(plugin_dir, PLUGIN_METADATA_FILE)
            if not os.path.exists(metadata_file):
                logger.warning(f"Plugin metadata file not found: {metadata_file}")
                continue

            try:
                # Load plugin metadata
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Validate metadata
                required_fields = ['name', 'version', 'description', 'author', 'main']
                if not all(field in metadata for field in required_fields):
                    logger.warning(f"Plugin metadata missing required fields: {metadata_file}")
                    continue

                # Add plugin directory to metadata
                metadata['directory'] = plugin_dir

                # Add to list of discovered plugins
                plugins_metadata.append(metadata)
                logger.info(f"Discovered plugin: {metadata['name']} v{metadata['version']}")

            except Exception as e:
                logger.error(f"Error loading plugin metadata: {metadata_file} - {e}")

        return plugins_metadata

    def load_plugin(self, metadata: Dict[str, Any]) -> Optional[PluginInterface]:
        """
        Load a plugin from metadata.

        Args:
            metadata: Plugin metadata dictionary

        Returns:
            Plugin instance or None if loading failed
        """
        try:
            plugin_name = metadata['name']
            plugin_dir = metadata['directory']
            main_module = metadata['main']

            # Check if plugin is already loaded
            if plugin_name in self._plugins:
                logger.warning(f"Plugin already loaded: {plugin_name}")
                return self._plugins[plugin_name]

            # Import the plugin module
            module_path = os.path.join(plugin_dir, main_module)
            spec = importlib.util.spec_from_file_location(plugin_name, module_path)
            if spec is None:
                logger.error(f"Could not find module: {module_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class (subclass of PluginInterface)
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, PluginInterface) and
                    obj is not PluginInterface):
                    plugin_class = obj
                    break

            if plugin_class is None:
                logger.error(f"No plugin class found in module: {module_path}")
                return None

            # Create plugin instance
            plugin = plugin_class()

            # Validate plugin
            if plugin.name != plugin_name:
                logger.warning(f"Plugin name mismatch: {plugin.name} != {plugin_name}")

            # Initialize plugin
            if not plugin.initialize():
                logger.error(f"Failed to initialize plugin: {plugin_name}")
                return None

            # Register plugin
            self._plugins[plugin_name] = plugin
            self._plugin_modules[plugin_name] = module

            # Register hooks
            hooks = plugin.get_hooks()
            for hook_name, hook_func in hooks.items():
                if hook_name not in self._hooks:
                    self._hooks[hook_name] = []
                self._hooks[hook_name].append((plugin_name, hook_func))

            logger.info(f"Loaded plugin: {plugin_name} v{plugin.version}")
            return plugin

        except Exception as e:
            logger.error(f"Error loading plugin: {metadata.get('name', 'unknown')} - {e}")
            return None

    def load_all_plugins(self) -> Dict[str, PluginInterface]:
        """
        Discover and load all available plugins.

        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        plugins_metadata = self.discover_plugins()

        for metadata in plugins_metadata:
            self.load_plugin(metadata)

        return self._plugins

    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """
        Get a loaded plugin by name.

        Args:
            name: Name of the plugin

        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)

    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """
        Get all loaded plugins.

        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        return self._plugins.copy()

    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin by name.

        Args:
            name: Name of the plugin

        Returns:
            True if plugin was unloaded, False otherwise
        """
        if name not in self._plugins:
            logger.warning(f"Plugin not loaded: {name}")
            return False

        plugin = self._plugins[name]

        try:
            # Shutdown plugin
            if not plugin.shutdown():
                logger.warning(f"Plugin shutdown failed: {name}")

            # Remove hooks
            for hook_name, hooks in list(self._hooks.items()):
                self._hooks[hook_name] = [(p, h) for p, h in hooks if p != name]
                if not self._hooks[hook_name]:
                    del self._hooks[hook_name]

            # Remove plugin
            del self._plugins[name]
            del self._plugin_modules[name]

            logger.info(f"Unloaded plugin: {name}")
            return True

        except Exception as e:
            logger.error(f"Error unloading plugin: {name} - {e}")
            return False

    def unload_all_plugins(self) -> bool:
        """
        Unload all plugins.

        Returns:
            True if all plugins were unloaded, False if any failed
        """
        success = True

        for name in list(self._plugins.keys()):
            if not self.unload_plugin(name):
                success = False

        return success

    def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Call all hook functions for a given hook name.

        Args:
            hook_name: Name of the hook to call
            *args: Positional arguments to pass to hook functions
            **kwargs: Keyword arguments to pass to hook functions

        Returns:
            List of results from hook functions
        """
        if hook_name not in self._hooks:
            return []

        results = []

        for plugin_name, hook_func in self._hooks[hook_name]:
            try:
                result = hook_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error calling hook '{hook_name}' from plugin '{plugin_name}': {e}")

        return results

    def has_hook(self, hook_name: str) -> bool:
        """
        Check if any plugins provide a given hook.

        Args:
            hook_name: Name of the hook to check

        Returns:
            True if hook exists, False otherwise
        """
        return hook_name in self._hooks

    def get_hooks(self, hook_name: str) -> List[Callable]:
        """
        Get all hook functions for a given hook name.

        Args:
            hook_name: Name of the hook to get

        Returns:
            List of hook functions
        """
        if hook_name not in self._hooks:
            return []

        return [hook_func for _, hook_func in self._hooks[hook_name]]

    def get_all_hooks(self) -> Dict[str, List[Tuple[str, Callable]]]:
        """
        Get all hooks.

        Returns:
            Dictionary mapping hook names to lists of (plugin_name, hook_function) tuples
        """
        return self._hooks.copy()


# Create a singleton instance
plugin_manager = PluginManager()


# Helper functions
def create_plugin_template(plugin_name: str, output_dir: Optional[str] = None) -> str:
    """
    Create a template for a new plugin.

    Args:
        plugin_name: Name of the plugin
        output_dir: Directory to create the plugin in (default: plugins directory)

    Returns:
        Path to the created plugin directory
    """
    if output_dir is None:
        output_dir = PLUGINS_DIR

    # Create plugin directory
    plugin_dir = os.path.join(output_dir, plugin_name)
    os.makedirs(plugin_dir, exist_ok=True)

    # Create plugin metadata file
    metadata = {
        "name": plugin_name,
        "version": "0.1.0",
        "description": f"{plugin_name} plugin for EcoCycle",
        "author": "EcoCycle User",
        "main": "plugin.py",
        "dependencies": []
    }

    with open(os.path.join(plugin_dir, PLUGIN_METADATA_FILE), 'w') as f:
        json.dump(metadata, f, indent=4)

    # Create plugin module file
    plugin_code = f'''#!/usr/bin/env python3
"""
EcoCycle Plugin - {plugin_name}
"""
from core.plugin.plugin_manager import PluginInterface


class {plugin_name.capitalize()}Plugin(PluginInterface):
    """Implementation of the {plugin_name} plugin."""

    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        return "{plugin_name}"

    @property
    def version(self) -> str:
        """Get the version of the plugin."""
        return "0.1.0"

    @property
    def description(self) -> str:
        """Get the description of the plugin."""
        return "{plugin_name} plugin for EcoCycle"

    @property
    def author(self) -> str:
        """Get the author of the plugin."""
        return "EcoCycle User"

    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Returns:
            True if initialization was successful, False otherwise
        """
        print(f"Initializing {self.name} plugin...")
        return True

    def shutdown(self) -> bool:
        """
        Shutdown the plugin.

        Returns:
            True if shutdown was successful, False otherwise
        """
        print(f"Shutting down {self.name} plugin...")
        return True

    def get_hooks(self) -> dict:
        """
        Get the hooks provided by the plugin.

        Returns:
            Dictionary mapping hook names to hook functions
        """
        return {{
            "example_hook": self.example_hook
        }}

    def example_hook(self, *args, **kwargs):
        """Example hook function."""
        print(f"{self.name} plugin: example_hook called with args={{args}}, kwargs={{kwargs}}")
        return "Example hook result"
'''

    with open(os.path.join(plugin_dir, "plugin.py"), 'w') as f:
        f.write(plugin_code)

    # Create README file
    readme = f'''# {plugin_name} Plugin

A plugin for EcoCycle.

## Description

{plugin_name} plugin for EcoCycle.

## Installation

1. Copy this directory to the `plugins` directory in your EcoCycle installation.
2. Restart EcoCycle.

## Usage

TODO: Add usage instructions.

## License

TODO: Add license information.
'''

    with open(os.path.join(plugin_dir, "README.md"), 'w') as f:
        f.write(readme)

    logger.info(f"Created plugin template: {plugin_dir}")
    return plugin_dir
