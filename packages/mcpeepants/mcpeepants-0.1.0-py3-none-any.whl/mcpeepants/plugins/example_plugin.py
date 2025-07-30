"""Example plugin demonstrating how to create custom tools, resources, and prompts."""

from mcpeepants.plugin_loader import tool, resource, prompt
from typing import Dict, Any
import datetime


@tool
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> Dict[str, Any]:
    """
    Get the current time in the specified format.
    
    Args:
        format: strftime format string
        
    Returns:
        Dictionary with current time
    """
    try:
        current_time = datetime.datetime.now().strftime(format)
        return {
            "success": True,
            "time": current_time,
            "format": format
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@resource("time://current")
def current_time_resource() -> Dict[str, str]:
    """Resource for current time information."""
    return {
        "message": "Use the get_current_time tool to get the current time",
        "example": "get_current_time(format='%Y-%m-%d')"
    }


@prompt
def time_prompt() -> str:
    """Prompt for time-related operations."""
    return """I can help you with time-related operations.

Available commands:
- "What time is it?" - Get the current time
- "Get time in ISO format" - Get time in ISO 8601 format
- "Get date only" - Get just the current date

You can also specify custom formats using strftime syntax."""
