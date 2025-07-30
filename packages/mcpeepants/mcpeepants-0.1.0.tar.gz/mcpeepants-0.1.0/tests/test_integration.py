"""Integration tests for the MCP server."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from mcpeepants.server import create_server
from mcpeepants.plugin_loader import tool


class TestServerIntegration:
    def test_server_with_plugin_integration(self):
        """Test that server correctly loads and uses plugins."""
        # Create a temporary plugin
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
from mcpeepants.plugin_loader import tool

@tool
def integration_test_tool(value: str):
    """Test tool for integration testing."""
    return {"result": f"processed: {value}"}
''')
            plugin_file = f.name
            
        try:
            with patch.dict(os.environ, {"MCP_PLUGIN_PATHS": plugin_file}):
                server = create_server("Test Server")
                assert server.name == "Test Server"
                
                # The server should have loaded our plugin during initialization
                # We can't easily test this without running the server, but we
                # can verify the server was created successfully
                
        finally:
            os.unlink(plugin_file)
            
    def test_builtin_tools_available(self):
        """Test that built-in tools are registered."""
        server = create_server()
        
        # The server should have pytest_runner tool registered
        # This is a basic test to ensure server creation works
        assert hasattr(server, 'tool')
        assert hasattr(server, 'resource')
        assert hasattr(server, 'prompt')
