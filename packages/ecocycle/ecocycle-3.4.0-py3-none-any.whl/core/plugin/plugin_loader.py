#!/usr/bin/env python3
"""
EcoCycle - Plugin Loader Module
Provides functions for loading and using plugins in the application.
"""
import os
import sys
import logging
from typing import Dict, List, Any, Optional, Callable

# Import plugin manager
from core.plugin.plugin_manager import plugin_manager, PluginInterface

# Import config module for paths
try:
    import config.config as config
    # Use config module for log directory
    LOG_DIR = config.LOG_DIR
except ImportError:
    # Fallback if config module is not available
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Logs')

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'plugin_loader.log'))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def initialize_plugins() -> Dict[str, PluginInterface]:
    """
    Initialize all available plugins.
    
    Returns:
        Dictionary mapping plugin names to plugin instances
    """
    logger.info("Initializing plugins...")
    
    # Discover and load all plugins
    plugins = plugin_manager.load_all_plugins()
    
    logger.info(f"Initialized {len(plugins)} plugins")
    
    return plugins


def shutdown_plugins() -> bool:
    """
    Shutdown all loaded plugins.
    
    Returns:
        True if all plugins were unloaded successfully, False otherwise
    """
    logger.info("Shutting down plugins...")
    
    # Unload all plugins
    result = plugin_manager.unload_all_plugins()
    
    logger.info("Plugins shut down")
    
    return result


def get_plugin(name: str) -> Optional[PluginInterface]:
    """
    Get a plugin by name.
    
    Args:
        name: Name of the plugin
        
    Returns:
        Plugin instance or None if not found
    """
    return plugin_manager.get_plugin(name)


def get_all_plugins() -> Dict[str, PluginInterface]:
    """
    Get all loaded plugins.
    
    Returns:
        Dictionary mapping plugin names to plugin instances
    """
    return plugin_manager.get_all_plugins()


def call_hook(hook_name: str, *args, **kwargs) -> List[Any]:
    """
    Call a hook in all plugins that provide it.
    
    Args:
        hook_name: Name of the hook to call
        *args: Positional arguments to pass to the hook
        **kwargs: Keyword arguments to pass to the hook
        
    Returns:
        List of results from all hook calls
    """
    return plugin_manager.call_hook(hook_name, *args, **kwargs)


def has_hook(hook_name: str) -> bool:
    """
    Check if any plugins provide a hook.
    
    Args:
        hook_name: Name of the hook to check
        
    Returns:
        True if the hook is provided by at least one plugin, False otherwise
    """
    return plugin_manager.has_hook(hook_name)


def get_hooks(hook_name: str) -> List[Callable]:
    """
    Get all hook functions for a hook name.
    
    Args:
        hook_name: Name of the hook to get
        
    Returns:
        List of hook functions
    """
    return plugin_manager.get_hooks(hook_name)


def get_plugin_info() -> List[Dict[str, Any]]:
    """
    Get information about all loaded plugins.
    
    Returns:
        List of dictionaries with plugin information
    """
    plugins = plugin_manager.get_all_plugins()
    
    plugin_info = []
    
    for name, plugin in plugins.items():
        hooks = plugin.get_hooks()
        
        info = {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "author": plugin.author,
            "hooks": list(hooks.keys())
        }
        
        plugin_info.append(info)
    
    return plugin_info


# Initialize plugins when the module is imported
if __name__ != "__main__":
    try:
        initialize_plugins()
    except Exception as e:
        logger.error(f"Error initializing plugins: {e}")
