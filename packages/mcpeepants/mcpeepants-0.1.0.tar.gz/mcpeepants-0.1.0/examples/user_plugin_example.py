"""Example plugin showing how to extend the MCP server with custom functionality."""

from mcpeepants.plugin_loader import tool, resource, prompt
from typing import Dict, Any, List, Optional
import json
import os
from pathlib import Path


@tool
def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON content or error message
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return {
            "success": True,
            "data": data,
            "file_path": str(path.absolute())
        }
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}


@tool
def list_files(directory: str, pattern: Optional[str] = None) -> Dict[str, Any]:
    """
    List files in a directory with optional pattern matching.
    
    Args:
        directory: Directory path to list
        pattern: Optional glob pattern (e.g., "*.py", "test_*")
        
    Returns:
        List of files or error message
    """
    try:
        path = Path(directory)
        if not path.exists():
            return {"error": f"Directory not found: {directory}"}
            
        if not path.is_dir():
            return {"error": f"Not a directory: {directory}"}
            
        if pattern:
            files = list(path.glob(pattern))
        else:
            files = list(path.iterdir())
            
        file_list = []
        for f in files:
            file_list.append({
                "name": f.name,
                "path": str(f),
                "is_file": f.is_file(),
                "is_dir": f.is_dir(),
                "size": f.stat().st_size if f.is_file() else None
            })
            
        return {
            "success": True,
            "directory": str(path.absolute()),
            "pattern": pattern,
            "count": len(file_list),
            "files": sorted(file_list, key=lambda x: (not x["is_dir"], x["name"]))
        }
    except Exception as e:
        return {"error": f"Failed to list files: {str(e)}"}


@tool
def calculate_statistics(numbers: List[float]) -> Dict[str, Any]:
    """
    Calculate basic statistics for a list of numbers.
    
    Args:
        numbers: List of numbers
        
    Returns:
        Statistics including mean, median, min, max, etc.
    """
    try:
        if not numbers:
            return {"error": "Empty list provided"}
            
        sorted_numbers = sorted(numbers)
        n = len(numbers)
        
        mean = sum(numbers) / n
        
        if n % 2 == 0:
            median = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
        else:
            median = sorted_numbers[n//2]
            
        variance = sum((x - mean) ** 2 for x in numbers) / n
        std_dev = variance ** 0.5
        
        return {
            "success": True,
            "count": n,
            "mean": mean,
            "median": median,
            "min": min(numbers),
            "max": max(numbers),
            "range": max(numbers) - min(numbers),
            "variance": variance,
            "std_dev": std_dev,
            "sum": sum(numbers)
        }
    except Exception as e:
        return {"error": f"Failed to calculate statistics: {str(e)}"}


@resource("files://json")
def json_files_resource() -> Dict[str, str]:
    """Resource for JSON file operations."""
    return {
        "description": "Tools for working with JSON files",
        "tools": ["read_json_file"],
        "example": "read_json_file(file_path='config.json')"
    }


@resource("files://directory")  
def directory_resource() -> Dict[str, str]:
    """Resource for directory operations."""
    return {
        "description": "Tools for listing and exploring directories",
        "tools": ["list_files"],
        "examples": [
            "list_files(directory='.')",
            "list_files(directory='./src', pattern='*.py')"
        ]
    }


@resource("math://statistics")
def statistics_resource() -> Dict[str, str]:
    """Resource for statistical calculations."""
    return {
        "description": "Calculate statistics on numerical data",
        "tools": ["calculate_statistics"],
        "example": "calculate_statistics(numbers=[1, 2, 3, 4, 5])"
    }


@prompt
def file_operations_prompt() -> str:
    """Prompt for file operations."""
    return """I can help you work with files and directories.

**File Operations:**
- Read JSON files: "Read the config.json file"
- List directory contents: "Show me all Python files in the src folder"
- Browse directories: "List all files in the current directory"

**Data Analysis:**
- Calculate statistics: "Calculate statistics for these numbers: 10, 20, 30, 40, 50"

What would you like to do?"""


@prompt
def data_analysis_prompt() -> str:
    """Prompt for data analysis tasks."""
    return """I can help you analyze data and calculate statistics.

Available operations:
1. **Basic Statistics**: Calculate mean, median, min, max, standard deviation
2. **File Analysis**: Read JSON data files and analyze their contents
3. **Directory Analysis**: Count files, find patterns, explore structure

Examples:
- "Calculate the average of 15, 23, 19, 31, 27"
- "Read data.json and calculate statistics on the 'values' field"
- "How many Python files are in the project?"

What data would you like to analyze?"""
