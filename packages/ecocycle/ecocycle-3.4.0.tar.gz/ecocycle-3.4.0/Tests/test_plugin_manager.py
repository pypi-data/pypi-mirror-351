#!/usr/bin/env python3
"""
Test script for the plugin manager module.
This script tests the functionality of the plugin manager.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import json

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from core.plugin.plugin_manager import PluginManager, PluginInterface, create_plugin_template


class TestPluginInterface(PluginInterface):
    """Test implementation of the plugin interface."""
    
    def __init__(self, name="test_plugin", version="0.1.0"):
        self._name = name
        self._version = version
        self._initialize_called = False
        self._shutdown_called = False
    
    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        return self._name
    
    @property
    def version(self) -> str:
        """Get the version of the plugin."""
        return self._version
    
    @property
    def description(self) -> str:
        """Get the description of the plugin."""
        return "Test plugin for unit tests"
    
    @property
    def author(self) -> str:
        """Get the author of the plugin."""
        return "Test Author"
    
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        self._initialize_called = True
        return True
    
    def shutdown(self) -> bool:
        """
        Shutdown the plugin.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        self._shutdown_called = True
        return True
    
    def get_hooks(self) -> dict:
        """
        Get the hooks provided by the plugin.
        
        Returns:
            Dictionary mapping hook names to hook functions
        """
        return {
            "test_hook": self.test_hook,
            "another_hook": self.another_hook
        }
    
    def test_hook(self, *args, **kwargs):
        """Test hook function."""
        return f"test_hook called with args={args}, kwargs={kwargs}"
    
    def another_hook(self, *args, **kwargs):
        """Another test hook function."""
        return f"another_hook called with args={args}, kwargs={kwargs}"


class TestPluginManager(unittest.TestCase):
    """Test cases for the plugin manager module."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test plugins
        self.test_dir = tempfile.mkdtemp()
        self.test_plugins_dir = os.path.join(self.test_dir, 'plugins')
        os.makedirs(self.test_plugins_dir, exist_ok=True)
        
        # Save original plugins directory
        self.original_plugins_dir = PluginManager.PLUGINS_DIR
        
        # Override plugins directory
        PluginManager.PLUGINS_DIR = self.test_plugins_dir
        
        # Create a test plugin manager
        self.plugin_mgr = PluginManager()
        
        # Reset the singleton instance to force reinitialization
        PluginManager._instance = None
        PluginManager._instance = self.plugin_mgr
        self.plugin_mgr._initialized = False
        self.plugin_mgr.__init__()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original plugins directory
        PluginManager.PLUGINS_DIR = self.original_plugins_dir
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_singleton(self):
        """Test that PluginManager is a singleton."""
        # Create two instances
        plugin_mgr1 = PluginManager()
        plugin_mgr2 = PluginManager()
        
        # Check that they are the same instance
        self.assertIs(plugin_mgr1, plugin_mgr2)

    def test_create_plugin_template(self):
        """Test creating a plugin template."""
        # Create a plugin template
        plugin_dir = create_plugin_template("test_plugin", self.test_plugins_dir)
        
        # Check that the plugin directory was created
        self.assertTrue(os.path.exists(plugin_dir))
        
        # Check that the plugin files were created
        self.assertTrue(os.path.exists(os.path.join(plugin_dir, "plugin.json")))
        self.assertTrue(os.path.exists(os.path.join(plugin_dir, "plugin.py")))
        self.assertTrue(os.path.exists(os.path.join(plugin_dir, "README.md")))
        
        # Check the plugin metadata
        with open(os.path.join(plugin_dir, "plugin.json"), 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata["name"], "test_plugin")
        self.assertEqual(metadata["version"], "0.1.0")
        self.assertEqual(metadata["main"], "plugin.py")

    def test_discover_plugins(self):
        """Test discovering plugins."""
        # Create a test plugin
        plugin_dir = os.path.join(self.test_plugins_dir, "test_plugin")
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Create plugin metadata
        metadata = {
            "name": "test_plugin",
            "version": "0.1.0",
            "description": "Test plugin",
            "author": "Test Author",
            "main": "plugin.py"
        }
        
        with open(os.path.join(plugin_dir, "plugin.json"), 'w') as f:
            json.dump(metadata, f)
        
        # Create plugin module
        with open(os.path.join(plugin_dir, "plugin.py"), 'w') as f:
            f.write("""
from core.plugin.plugin_manager import PluginInterface

class TestPlugin(PluginInterface):
    @property
    def name(self): return "test_plugin"
    @property
    def version(self): return "0.1.0"
    @property
    def description(self): return "Test plugin"
    @property
    def author(self): return "Test Author"
    def initialize(self): return True
    def shutdown(self): return True
    def get_hooks(self): return {}
""")
        
        # Discover plugins
        plugins_metadata = self.plugin_mgr.discover_plugins()
        
        # Check that the plugin was discovered
        self.assertEqual(len(plugins_metadata), 1)
        self.assertEqual(plugins_metadata[0]["name"], "test_plugin")
        self.assertEqual(plugins_metadata[0]["version"], "0.1.0")
        self.assertEqual(plugins_metadata[0]["description"], "Test plugin")
        self.assertEqual(plugins_metadata[0]["author"], "Test Author")
        self.assertEqual(plugins_metadata[0]["main"], "plugin.py")
        self.assertEqual(plugins_metadata[0]["directory"], plugin_dir)

    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_load_plugin(self, mock_module_from_spec, mock_spec_from_file_location):
        """Test loading a plugin."""
        # Create mock module and spec
        mock_module = MagicMock()
        mock_spec = MagicMock()
        mock_spec_from_file_location.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module
        
        # Create mock plugin class
        mock_plugin = TestPluginInterface()
        mock_module.TestPlugin = MagicMock(return_value=mock_plugin)
        
        # Create plugin metadata
        metadata = {
            "name": "test_plugin",
            "version": "0.1.0",
            "description": "Test plugin",
            "author": "Test Author",
            "main": "plugin.py",
            "directory": os.path.join(self.test_plugins_dir, "test_plugin")
        }
        
        # Load plugin
        plugin = self.plugin_mgr.load_plugin(metadata)
        
        # Check that the plugin was loaded
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin, mock_plugin)
        
        # Check that the plugin was initialized
        self.assertTrue(mock_plugin._initialize_called)
        
        # Check that the plugin was registered
        self.assertEqual(self.plugin_mgr._plugins["test_plugin"], mock_plugin)
        self.assertEqual(self.plugin_mgr._plugin_modules["test_plugin"], mock_module)
        
        # Check that the hooks were registered
        self.assertIn("test_hook", self.plugin_mgr._hooks)
        self.assertIn("another_hook", self.plugin_mgr._hooks)
        self.assertEqual(len(self.plugin_mgr._hooks["test_hook"]), 1)
        self.assertEqual(len(self.plugin_mgr._hooks["another_hook"]), 1)
        self.assertEqual(self.plugin_mgr._hooks["test_hook"][0][0], "test_plugin")
        self.assertEqual(self.plugin_mgr._hooks["another_hook"][0][0], "test_plugin")

    def test_unload_plugin(self):
        """Test unloading a plugin."""
        # Create a test plugin
        plugin = TestPluginInterface()
        
        # Register the plugin
        self.plugin_mgr._plugins["test_plugin"] = plugin
        self.plugin_mgr._plugin_modules["test_plugin"] = MagicMock()
        self.plugin_mgr._hooks["test_hook"] = [("test_plugin", plugin.test_hook)]
        self.plugin_mgr._hooks["another_hook"] = [("test_plugin", plugin.another_hook)]
        
        # Unload the plugin
        result = self.plugin_mgr.unload_plugin("test_plugin")
        
        # Check that the plugin was unloaded
        self.assertTrue(result)
        self.assertTrue(plugin._shutdown_called)
        self.assertNotIn("test_plugin", self.plugin_mgr._plugins)
        self.assertNotIn("test_plugin", self.plugin_mgr._plugin_modules)
        self.assertNotIn("test_hook", self.plugin_mgr._hooks)
        self.assertNotIn("another_hook", self.plugin_mgr._hooks)

    def test_call_hook(self):
        """Test calling a hook."""
        # Create a test plugin
        plugin = TestPluginInterface()
        
        # Register the plugin
        self.plugin_mgr._plugins["test_plugin"] = plugin
        self.plugin_mgr._hooks["test_hook"] = [("test_plugin", plugin.test_hook)]
        
        # Call the hook
        results = self.plugin_mgr.call_hook("test_hook", "arg1", "arg2", kwarg1="value1")
        
        # Check the results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "test_hook called with args=('arg1', 'arg2'), kwargs={'kwarg1': 'value1'}")

    def test_has_hook(self):
        """Test checking if a hook exists."""
        # Create a test plugin
        plugin = TestPluginInterface()
        
        # Register the plugin
        self.plugin_mgr._plugins["test_plugin"] = plugin
        self.plugin_mgr._hooks["test_hook"] = [("test_plugin", plugin.test_hook)]
        
        # Check if hooks exist
        self.assertTrue(self.plugin_mgr.has_hook("test_hook"))
        self.assertFalse(self.plugin_mgr.has_hook("nonexistent_hook"))

    def test_get_hooks(self):
        """Test getting hooks."""
        # Create a test plugin
        plugin = TestPluginInterface()
        
        # Register the plugin
        self.plugin_mgr._plugins["test_plugin"] = plugin
        self.plugin_mgr._hooks["test_hook"] = [("test_plugin", plugin.test_hook)]
        
        # Get hooks
        hooks = self.plugin_mgr.get_hooks("test_hook")
        
        # Check the hooks
        self.assertEqual(len(hooks), 1)
        self.assertEqual(hooks[0], plugin.test_hook)
        
        # Get nonexistent hooks
        hooks = self.plugin_mgr.get_hooks("nonexistent_hook")
        
        # Check the hooks
        self.assertEqual(len(hooks), 0)


if __name__ == '__main__':
    unittest.main()
