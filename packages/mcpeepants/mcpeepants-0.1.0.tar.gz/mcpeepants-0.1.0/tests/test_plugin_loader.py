"""Tests for plugin loader module."""

import os
import tempfile
import pytest
from pathlib import Path
from mcpeepants.plugin_loader import PluginLoader, tool, resource, prompt


class TestPluginLoader:
    def test_init(self):
        loader = PluginLoader()
        assert loader.plugin_paths == []
        assert loader._loaded_modules == {}
        
        loader = PluginLoader(["/path1", "/path2"])
        assert loader.plugin_paths == ["/path1", "/path2"]
        
    def test_add_plugin_path(self):
        loader = PluginLoader()
        loader.add_plugin_path("/path1")
        assert "/path1" in loader.plugin_paths
        
        loader.add_plugin_path("/path1")
        assert loader.plugin_paths.count("/path1") == 1
        
    def test_load_plugins_empty(self):
        loader = PluginLoader()
        plugins = loader.load_plugins()
        assert plugins == {"tools": [], "resources": [], "prompts": []}
        
    def test_load_plugins_nonexistent_path(self):
        loader = PluginLoader(["/nonexistent/path"])
        plugins = loader.load_plugins()
        assert plugins == {"tools": [], "resources": [], "prompts": []}
        
    def test_load_plugin_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
from mcpeepants.plugin_loader import tool, resource, prompt

@tool
def test_tool():
    return "tool result"
    
@resource("test://resource")
def test_resource():
    return "resource result"
    
@prompt
def test_prompt():
    return "prompt result"
''')
            plugin_file = f.name
            
        try:
            loader = PluginLoader([plugin_file])
            plugins = loader.load_plugins()
            
            assert len(plugins["tools"]) == 1
            assert len(plugins["resources"]) == 1
            assert len(plugins["prompts"]) == 1
            
            assert hasattr(plugins["tools"][0], '_mcp_tool')
            assert hasattr(plugins["resources"][0], '_mcp_resource')
            assert hasattr(plugins["prompts"][0], '_mcp_prompt')
            
        finally:
            os.unlink(plugin_file)
            
    def test_load_plugin_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_file = Path(tmpdir) / "test_plugin.py"
            plugin_file.write_text('''
from mcpeepants.plugin_loader import tool

@tool
def dir_test_tool():
    return "dir tool"
''')
            
            loader = PluginLoader([tmpdir])
            plugins = loader.load_plugins()
            
            assert len(plugins["tools"]) == 1
            assert hasattr(plugins["tools"][0], '_mcp_tool')
            
    def test_load_plugin_with_error(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('import nonexistent_module')
            plugin_file = f.name
            
        try:
            loader = PluginLoader([plugin_file])
            plugins = loader.load_plugins()
            assert plugins == {"tools": [], "resources": [], "prompts": []}
        finally:
            os.unlink(plugin_file)
            
    def test_ignore_private_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            public_file = Path(tmpdir) / "public.py"
            public_file.write_text('''
from mcpeepants.plugin_loader import tool

@tool
def public_tool():
    return "public"
''')
            
            private_file = Path(tmpdir) / "_private.py"
            private_file.write_text('''
from mcpeepants.plugin_loader import tool

@tool  
def private_tool():
    return "private"
''')
            
            loader = PluginLoader([tmpdir])
            plugins = loader.load_plugins()
            
            assert len(plugins["tools"]) == 1
            
            
class TestDecorators:
    def test_tool_decorator(self):
        @tool
        def my_tool():
            return "result"
            
        assert hasattr(my_tool, '_mcp_tool')
        assert my_tool._mcp_tool is True
        assert my_tool() == "result"
        
    def test_resource_decorator(self):
        @resource("test://uri")
        def my_resource():
            return "result"
            
        assert hasattr(my_resource, '_mcp_resource')
        assert my_resource._mcp_resource is True
        assert hasattr(my_resource, '_mcp_resource_uri')
        assert my_resource._mcp_resource_uri == "test://uri"
        assert my_resource() == "result"
        
    def test_prompt_decorator(self):
        @prompt
        def my_prompt():
            return "result"
            
        assert hasattr(my_prompt, '_mcp_prompt')
        assert my_prompt._mcp_prompt is True
        assert my_prompt() == "result"
