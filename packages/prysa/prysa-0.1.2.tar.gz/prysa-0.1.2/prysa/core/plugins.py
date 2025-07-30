"""
Plugin extension system for prysa.
Allows dynamic discovery and registration of external tools (managers, linters, testers, etc).
"""
import importlib
import pkgutil
from typing import Dict, Type, Any, List

class PrysaPlugin:
    """Base class for all prysa plugins."""
    name: str = "base"
    type: str = "generic"  # e.g., 'manager', 'linter', 'tester'

    def register(self) -> None:
        """Register the plugin with prysa's registries."""
        raise NotImplementedError

class PluginRegistry:
    """Registry for loaded plugins."""
    def __init__(self):
        self.plugins: Dict[str, PrysaPlugin] = {}

    def register(self, plugin: PrysaPlugin):
        self.plugins[plugin.name] = plugin

    def get(self, name: str) -> PrysaPlugin:
        return self.plugins[name]

    def all(self) -> List[PrysaPlugin]:
        return list(self.plugins.values())

plugin_registry = PluginRegistry()

def discover_plugins(namespace: str = "prysa_plugins"):
    """Discover and load plugins from the given namespace package (default: 'prysa_plugins')."""
    for finder, name, ispkg in pkgutil.iter_modules():
        if name.startswith(namespace):
            module = importlib.import_module(name)
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, PrysaPlugin) and obj is not PrysaPlugin:
                    plugin = obj()
                    plugin_registry.register(plugin)
                    plugin.register()
