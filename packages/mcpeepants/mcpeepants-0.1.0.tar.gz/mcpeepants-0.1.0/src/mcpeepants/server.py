"""Main MCP server implementation."""

import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv

from .plugin_loader import PluginLoader
from .async_tools import run_pytest_async

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dependencies = ["python-dotenv", "pytest"]


@dataclass
class ServerContext:
    plugin_loader: PluginLoader
    plugin_paths: List[str]
    pytest_path: str


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[ServerContext]:
    plugin_paths = _get_plugin_paths()
    pytest_path = os.environ.get("PYTEST_PATH", ".")
    
    logger.info(f"Starting MCP server with plugin paths: {plugin_paths}")
    logger.info(f"Pytest path: {pytest_path}")
    
    plugin_loader = PluginLoader(plugin_paths)
    plugins = plugin_loader.load_plugins()
    
    for tool_func in plugins["tools"]:
        server.tool()(tool_func)
        
    for resource_func in plugins["resources"]:
        uri = getattr(resource_func, '_mcp_resource_uri', 'plugin://resource')
        server.resource(uri)(resource_func)
        
    for prompt_func in plugins["prompts"]:
        server.prompt()(prompt_func)
        
    logger.info(f"Loaded {len(plugins['tools'])} tools, "
               f"{len(plugins['resources'])} resources, "
               f"{len(plugins['prompts'])} prompts from plugins")
    
    try:
        yield ServerContext(
            plugin_loader=plugin_loader,
            plugin_paths=plugin_paths,
            pytest_path=pytest_path
        )
    finally:
        logger.info("MCP server shutting down")


def _get_plugin_paths() -> List[str]:
    paths = []
    
    env_paths = os.environ.get("MCP_PLUGIN_PATHS", "")
    if env_paths:
        paths.extend([p.strip() for p in env_paths.split(":") if p.strip()])
        
    default_plugin_dir = Path(__file__).parent / "plugins"
    if default_plugin_dir.exists():
        paths.append(str(default_plugin_dir))
        
    return paths


def create_server(name: str = "mcpeepants") -> FastMCP:
    mcp = FastMCP(name, lifespan=server_lifespan, dependencies=dependencies)
    
    @mcp.tool()
    async def pytest_runner(
        ctx: Context,
        test_path: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run pytest on the specified path or configured test directory.
        
        Args:
            test_path: Path to test file or directory (optional, uses PYTEST_PATH env var if not provided)
            extra_args: Additional pytest arguments (e.g., ["-k", "test_name", "-x"])
            timeout: Maximum execution time in seconds (default: 30)
            
        Returns:
            Test execution results including output and summary
        """
        logger.info(f"pytest_runner called with test_path={test_path}, extra_args={extra_args}, timeout={timeout}")
        
        # Get server context to use configured pytest_path if not provided
        server_ctx = ctx.request_context.lifespan_context
        if test_path is None and hasattr(server_ctx, 'pytest_path'):
            test_path = server_ctx.pytest_path
            
        # Use default timeout if not specified
        if timeout is None:
            timeout = int(os.environ.get('PYTEST_TIMEOUT', '30'))
            
        result = await run_pytest_async(test_path, extra_args, timeout)
        logger.info(f"pytest_runner completed with success={result.get('success', False)}")
        return result
    
    @mcp.tool()
    def pytest_runner_debug(
        ctx: Context,
        test_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Debug version of pytest runner that returns mock results.
        
        Args:
            test_path: Path to test (for logging only)
            
        Returns:
            Mock test results
        """
        logger.info(f"pytest_runner_debug called with test_path={test_path}")
        
        return {
            "success": True,
            "exit_code": 0,
            "stdout": "Mock test output\n.....\n5 passed in 0.01s",
            "stderr": "",
            "summary": {
                "total": 5,
                "passed": 5,
                "failed": 0,
                "skipped": 0,
                "errors": 0
            },
            "test_path": str(test_path or "mock_path"),
            "debug_note": "This is a mock response to test if the tool itself works"
        }
    
    @mcp.tool()
    def subprocess_test(
        ctx: Context,
        command: str = "echo",
        args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Test subprocess execution with simple commands.
        
        Args:
            command: Command to run (default: echo)
            args: Arguments for the command
            
        Returns:
            Command execution results
        """
        import subprocess
        
        if args is None:
            args = ["Hello from subprocess"]
            
        cmd = [command] + args
        logger.info(f"subprocess_test: Running {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                shell=os.name == 'nt'  # Use shell on Windows for echo
            )
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": ' '.join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 5 seconds",
                "command": ' '.join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}",
                "command": ' '.join(cmd)
            }
        
    @mcp.resource("tests://results")
    def test_results_resource() -> Dict[str, str]:
        """Resource for accessing test results."""
        return {"message": "Use the pytest_runner tool to run tests and get results"}
        
    @mcp.prompt()
    def run_tests_prompt() -> str:
        """Prompt for running tests."""
        return """I can help you run tests using pytest.

Available commands:
- "Run all tests" - runs all tests in the configured test directory
- "Run tests in <path>" - runs tests in a specific file or directory  
- "Run test <test_name>" - runs a specific test by name
- "Run tests with coverage" - runs tests with coverage report

The test directory is configured via the PYTEST_PATH environment variable.

What tests would you like to run?"""
    
    
    return mcp


# Create a default server instance that can be imported
mcp = create_server()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="mcpeepants")
    parser.add_argument("--transport", choices=["stdio", "sse"], 
                       default="stdio", help="Transport protocol")
    parser.add_argument("--name", default="mcpeepants",
                       help="Server name")
    
    args = parser.parse_args()
    
    if args.name != "mcpeepants":
        server = create_server(args.name)
    else:
        server = mcp
    
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
