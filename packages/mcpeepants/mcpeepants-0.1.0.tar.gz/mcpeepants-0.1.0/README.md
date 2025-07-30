# mcpeepants

An extensible MCP (Model Context Protocol) server library with plugin support. This library allows you to easily create MCP servers and extend them with custom tools, resources, and prompts without modifying the core library code.

## Features

- **Plugin System**: Dynamically load custom tools, resources, and prompts from external Python files
- **Built-in Pytest Tool**: Run pytest suites directly through MCP
- **Environment-based Configuration**: Configure plugin paths and test directories via environment variables
- **Type-safe**: Full type hints throughout the codebase
- **100% Test Coverage**: Comprehensive test suite included

## Installation

### Option 1: Using pip
```bash
pip install -r requirements.txt
```

### Option 2: Development installation
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Quick Start

### Running the Server

```bash
# Run with stdio transport (default)
python -m mcpeepants.server

# Run with SSE transport
python -m mcpeepants.server --transport sse

# Run with custom name
python -m mcpeepants.server --name "My Custom Server"
```

### Environment Variables

- `MCP_PLUGIN_PATHS`: Colon-separated list of paths to load plugins from
- `PYTEST_PATH`: Default path for the pytest runner tool (defaults to current directory)
- `PYTEST_TIMEOUT`: Timeout for pytest execution in seconds (defaults to 30)

Example:
```bash
export MCP_PLUGIN_PATHS="/path/to/plugins:/another/plugin/dir"
export PYTEST_PATH="./tests"
export PYTEST_TIMEOUT="60"  # Increase timeout for slower tests
python -m mcpeepants.server
```

## Usage Examples

### Creating Plugins

Create a Python file with your custom tools, resources, and prompts:

```python
# my_plugin.py
from mcpeepants.plugin_loader import tool, resource, prompt
from typing import Dict, Any

@tool
def my_custom_tool(param: str) -> Dict[str, Any]:
    """Description of what the tool does."""
    return {"result": f"Processed: {param}"}

@resource("myapp://data")
def my_data_resource() -> Dict[str, Any]:
    """Provide data to the MCP client."""
    return {"data": "Some data"}

@prompt
def my_custom_prompt() -> str:
    """Custom prompt for user interaction."""
    return "How can I help you with my custom functionality?"
```

Then set the plugin path:
```bash
export MCP_PLUGIN_PATHS="/path/to/my_plugin.py"
python -m mcp_server_lib.server
```

### Creating a Custom Server

You can also create a standalone server:

```python
# my_server.py
from mcpeepants import create_server

# Create and configure your server
server = create_server("My Custom Server")

# Run it
if __name__ == "__main__":
    server.run()
```

See `examples/custom_server_example.py` for a complete example.

## Claude Desktop Configuration

Add this to your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\mcp_servers.json`  
**macOS**: `~/Library/Application Support/Claude/mcp_servers.json`

### Using uv (recommended):

```json
{
  "mcpServers": {
    "mcpeepants": {
      "command": "C:\\Users\\[YOUR_USERNAME]\\AppData\\Local\\Microsoft\\WinGet\\Links\\uv.EXE",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "fastmcp",
        "--with",
        "python-dotenv",
        "--with",
        "pytest",
        "mcp",
        "run",
        "F:\\Projects\\MCP\\src\\mcpeepants\\server.py"
      ],
      "env": {
        "PYTHONPATH": "F:\\Projects\\MCP\\src",
        "MCP_PLUGIN_PATHS": "F:\\Projects\\MCP\\examples\\user_plugin_example.py",
        "PYTEST_PATH": "F:\\Projects\\MCP\\tests",
        "PYTEST_TIMEOUT": "30"
      }
    }
  }
}
```

**Note**: Replace `[YOUR_USERNAME]` with your Windows username. To find your uv.exe location, run `where uv` in Command Prompt.

See `claude_desktop_config.json` for a ready-to-use configuration.

## Built-in Tools

### pytest_runner

Run pytest on specified paths or the configured test directory with proper timeout handling.

**Arguments:**
- `test_path` (optional): Path to test file or directory
- `extra_args` (optional): Additional pytest arguments
- `timeout` (optional): Maximum execution time in seconds (defaults to PYTEST_TIMEOUT env var or 30)

**Example:**
```python
# Run all tests
pytest_runner()

# Run specific test file
pytest_runner(test_path="tests/test_example.py")

# Run with extra arguments
pytest_runner(extra_args=["-k", "test_name", "-x"])

# Run with custom timeout
pytest_runner(test_path="tests/slow_tests.py", timeout=120)
```

**Note**: The pytest runner includes safeguards against hanging tests:
- Automatic timeout with graceful termination
- Force kill if graceful termination fails
- Clear error messages when timeouts occur

## Testing

### Run Tests

```bash
# With coverage
python run_self_test.py

# Without coverage
python run_tests.py
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=mcpeepants --cov-report=term-missing

# Run specific test
pytest tests/test_plugin_loader.py -v
```

### Project Structure

```
mcpeepants/
├── src/
│   └── mcpeepants/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── plugin_loader.py   # Plugin system
│       ├── tools.py          # Built-in tools
│       └── plugins/          # Default plugins directory
├── tests/                    # Test suite
├── examples/                 # Example plugins
├── pyproject.toml           # Project configuration
└── run_self_test.py         # Self-test script
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions to common issues, including:
- pytest_runner timeout errors
- The hanging test in the test suite
- Import and path issues

## License

MIT
