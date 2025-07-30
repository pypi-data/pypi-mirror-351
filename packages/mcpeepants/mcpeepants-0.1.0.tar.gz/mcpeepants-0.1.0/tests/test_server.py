"""Tests for MCP server module."""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from mcpeepants.server import (
    create_server, _get_plugin_paths, server_lifespan, 
    ServerContext, main
)


class TestGetPluginPaths:
    def test_no_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False
                paths = _get_plugin_paths()
                assert paths == []
                
    def test_env_var_single_path(self):
        with patch.dict(os.environ, {"MCP_PLUGIN_PATHS": "/path1"}):
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False
                paths = _get_plugin_paths()
                assert "/path1" in paths
                
    def test_env_var_multiple_paths(self):
        with patch.dict(os.environ, {"MCP_PLUGIN_PATHS": "/path1:/path2:/path3"}):
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False
                paths = _get_plugin_paths()
                assert "/path1" in paths
                assert "/path2" in paths
                assert "/path3" in paths
                
    def test_env_var_empty_paths(self):
        with patch.dict(os.environ, {"MCP_PLUGIN_PATHS": ":/path1:::/path2:"}):
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False
                paths = _get_plugin_paths()
                assert paths == ["/path1", "/path2"]
                
    def test_default_plugin_dir_exists(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True
                paths = _get_plugin_paths()
                assert len(paths) == 1
                assert "plugins" in paths[0]
                

class TestServerLifespan:
    @pytest.mark.asyncio
    async def test_lifespan_context(self):
        mock_server = MagicMock()
        
        with patch.dict(os.environ, {"PYTEST_PATH": "/test/path"}):
            with patch("mcpeepants.server._get_plugin_paths") as mock_paths:
                mock_paths.return_value = ["/plugin1", "/plugin2"]
                
                async with server_lifespan(mock_server) as ctx:
                    assert isinstance(ctx, ServerContext)
                    assert ctx.pytest_path == "/test/path"
                    assert ctx.plugin_paths == ["/plugin1", "/plugin2"]
                    assert ctx.plugin_loader is not None
                    
    @pytest.mark.asyncio
    async def test_lifespan_default_pytest_path(self):
        mock_server = MagicMock()
        
        with patch.dict(os.environ, {}, clear=True):
            async with server_lifespan(mock_server) as ctx:
                assert ctx.pytest_path == "."
                

class TestCreateServer:
    def test_create_server_default_name(self):
        server = create_server()
        assert server.name == "mcpeepants"
        
    def test_create_server_custom_name(self):
        server = create_server("Custom Server")
        assert server.name == "Custom Server"
        
    def test_server_has_required_components(self):
        server = create_server()
        assert hasattr(server, 'tool')
        assert hasattr(server, 'resource')
        assert hasattr(server, 'prompt')
        assert hasattr(server, 'run')
        
    @pytest.mark.asyncio
    async def test_server_loads_plugins_in_lifespan(self):
        server = MagicMock()
        server.tool = MagicMock(return_value=lambda x: x)
        server.resource = MagicMock(return_value=lambda x: x)
        server.prompt = MagicMock(return_value=lambda x: x)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
from mcpeepants.plugin_loader import tool, resource, prompt

@tool
def plugin_tool():
    return "tool"
    
@resource("plugin://res")
def plugin_resource():
    return "resource"
    
@prompt
def plugin_prompt():
    return "prompt"
''')
            plugin_file = f.name
            
        try:
            with patch.dict(os.environ, {"MCP_PLUGIN_PATHS": plugin_file}):
                async with server_lifespan(server) as ctx:
                    assert server.tool.call_count >= 1
                    assert server.resource.call_count >= 1  
                    assert server.prompt.call_count >= 1
        finally:
            os.unlink(plugin_file)
                                

class TestMain:
    def test_main_default_args(self):
        test_args = ["server.py"]
        with patch.object(sys, "argv", test_args):
            with patch("mcpeepants.server.mcp") as mock_mcp:
                mock_mcp.run = MagicMock()
                
                main()
                
                mock_mcp.run.assert_called_once_with(transport="stdio")
                
    def test_main_custom_args(self):
        test_args = ["server.py", "--transport", "sse", "--name", "My Server"]
        with patch.object(sys, "argv", test_args):
            with patch("mcpeepants.server.create_server") as mock_create:
                mock_server = MagicMock()
                mock_create.return_value = mock_server
                
                main()
                
                mock_create.assert_called_once_with("My Server")
                mock_server.run.assert_called_once_with(transport="sse")
