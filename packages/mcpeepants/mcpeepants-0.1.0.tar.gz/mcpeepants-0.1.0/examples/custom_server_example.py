"""Example of how to use MCP Server Library in your own project."""

from mcpeepants import create_server
from mcpeepants.plugin_loader import tool, resource, prompt
from typing import Dict, Any


# Create custom tools for your project
@tool
def hello_world(name: str = "World") -> Dict[str, Any]:
    """
    Say hello to someone.
    
    Args:
        name: The name to greet
        
    Returns:
        Greeting message
    """
    return {
        "message": f"Hello, {name}!",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@tool
def calculate_sum(numbers: list[float]) -> Dict[str, Any]:
    """
    Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of numbers to sum
        
    Returns:
        The sum and count
    """
    return {
        "sum": sum(numbers),
        "count": len(numbers),
        "average": sum(numbers) / len(numbers) if numbers else 0
    }


# Create resources
@resource("myapp://info")
def app_info_resource() -> Dict[str, str]:
    """Information about this application."""
    return {
        "name": "My Custom MCP Server",
        "version": "1.0.0",
        "description": "Example of using MCP Server Library"
    }


# Create prompts
@prompt
def greeting_prompt() -> str:
    """Greeting prompt for users."""
    return """Welcome to My Custom MCP Server!

I can help you with:
- Greetings: "Say hello to Alice"
- Math: "Calculate the sum of [1, 2, 3, 4, 5]"
- App info: "Tell me about this application"

What would you like to do?"""


def main():
    """Run the custom MCP server."""
    # Create server with custom name
    server = create_server("My Custom MCP Server")
    
    # The plugin loader will automatically find and register
    # the decorated functions above if this file is in the plugin path
    
    # You can also manually register tools if needed:
    # server.tool()(hello_world)
    # server.resource("myapp://info")(app_info_resource)
    # server.prompt()(greeting_prompt)
    
    # Run the server
    server.run()


if __name__ == "__main__":
    # To use this:
    # 1. Save this file (e.g., my_mcp_server.py)
    # 2. Set MCP_PLUGIN_PATHS to include this file
    # 3. Run: python my_mcp_server.py
    # Or configure in Claude Desktop to run this file directly
    main()
