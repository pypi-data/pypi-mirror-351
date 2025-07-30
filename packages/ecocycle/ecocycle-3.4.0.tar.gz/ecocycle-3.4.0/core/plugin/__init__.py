"""
EcoCycle - Plugin Package
Provides a plugin system for extending application functionality.
"""
from core.plugin.plugin_manager import PluginInterface, plugin_manager, create_plugin_template
from core.plugin.plugin_loader import (
    initialize_plugins, shutdown_plugins, get_plugin, get_all_plugins,
    call_hook, has_hook, get_hooks, get_plugin_info
)

__all__ = [
    'PluginInterface',
    'plugin_manager',
    'create_plugin_template',
    'initialize_plugins',
    'shutdown_plugins',
    'get_plugin',
    'get_all_plugins',
    'call_hook',
    'has_hook',
    'get_hooks',
    'get_plugin_info'
]
