"""Plugin loader for dynamically loading MCP tools, resources, and prompts."""

import importlib.util
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class PluginLoader:
    def __init__(self, plugin_paths: Optional[List[str]] = None):
        self.plugin_paths = plugin_paths or []
        self._loaded_modules: Dict[str, Any] = {}
        
    def add_plugin_path(self, path: str) -> None:
        if path not in self.plugin_paths:
            self.plugin_paths.append(path)
            
    def load_plugins(self) -> Dict[str, List[Callable]]:
        plugins = {
            "tools": [],
            "resources": [],
            "prompts": []
        }
        
        for plugin_path in self.plugin_paths:
            if not os.path.exists(plugin_path):
                logger.warning(f"Plugin path does not exist: {plugin_path}")
                continue
                
            if os.path.isfile(plugin_path) and plugin_path.endswith('.py'):
                self._load_plugin_file(plugin_path, plugins)
            elif os.path.isdir(plugin_path):
                self._load_plugin_directory(plugin_path, plugins)
                
        return plugins
        
    def _load_plugin_file(self, file_path: str, plugins: Dict[str, List[Callable]]) -> None:
        try:
            module_name = Path(file_path).stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                logger.error(f"Failed to load spec for {file_path}")
                return
                
            module = importlib.util.module_from_spec(spec)
            self._loaded_modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._extract_plugin_components(module, plugins)
            
        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {e}")
            
    def _load_plugin_directory(self, dir_path: str, plugins: Dict[str, List[Callable]]) -> None:
        for file_name in os.listdir(dir_path):
            if file_name.endswith('.py') and not file_name.startswith('_'):
                file_path = os.path.join(dir_path, file_name)
                self._load_plugin_file(file_path, plugins)
                
    def _extract_plugin_components(self, module: Any, plugins: Dict[str, List[Callable]]) -> None:
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(module, attr_name)
            
            if hasattr(attr, '_mcp_tool'):
                plugins["tools"].append(attr)
            elif hasattr(attr, '_mcp_resource'):
                plugins["resources"].append(attr)
            elif hasattr(attr, '_mcp_prompt'):
                plugins["prompts"].append(attr)


def tool(func: Callable) -> Callable:
    func._mcp_tool = True
    return func


def resource(uri: str):
    def decorator(func: Callable) -> Callable:
        func._mcp_resource = True
        func._mcp_resource_uri = uri
        return func
    return decorator


def prompt(func: Callable) -> Callable:
    func._mcp_prompt = True
    return func
