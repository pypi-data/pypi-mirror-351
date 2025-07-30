"""Built-in tools for the MCP server."""

import os
import sys
import subprocess
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def run_pytest(
    test_path: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    capture_output: bool = True,
    minimal_mode: bool = True
) -> Dict[str, Any]:
    """
    Run pytest on the specified path.
    
    Args:
        test_path: Path to test file or directory. If None, uses PYTEST_PATH env var or current directory.
        extra_args: Additional arguments to pass to pytest
        capture_output: Whether to capture pytest output
        minimal_mode: Use minimal pytest configuration to avoid hanging
        
    Returns:
        Dictionary containing test results and output
    """
    if test_path is None:
        test_path = os.environ.get("PYTEST_PATH", ".")
        
    test_path = Path(test_path).absolute()
    if not test_path.exists():
        return {
            "success": False,
            "error": f"Test path does not exist: {test_path}",
            "exit_code": 1
        }
        
    # Build command
    cmd = [sys.executable, "-m", "pytest"]
    
    if minimal_mode:
        # Minimal mode to avoid hanging - disable all plugins and config
        cmd.extend([
            "-p", "no:cacheprovider",
            "-p", "no:warnings",
            "-p", "no:doctest",
            "-p", "no:cov",  # Explicitly disable coverage
            "-c", "/dev/null" if os.name != 'nt' else "nul",
            "--override-ini=addopts=",
            "--override-ini=asyncio_mode=strict"
        ])
    
    if capture_output:
        cmd.extend(["-v", "--tb=short", "--no-header", "-s"])
        
    # Add the test path
    cmd.append(str(test_path))
        
    if extra_args:
        cmd.extend(extra_args)
        
    # Set up environment
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PY_COLORS"] = "0"  # Disable colored output
    
    # Ensure PYTHONPATH includes the project root
    project_root = Path(__file__).parent.parent.parent
    pythonpath = env.get("PYTHONPATH", "")
    if pythonpath:
        env["PYTHONPATH"] = f"{project_root}{os.pathsep}{pythonpath}"
    else:
        env["PYTHONPATH"] = str(project_root)
    
    # Determine working directory
    if test_path.is_file():
        cwd = test_path.parent
    else:
        cwd = test_path
        
    logger.info(f"Running pytest command: {' '.join(cmd)}")
    logger.info(f"Working directory: {cwd}")
    
    # First check if pytest is available
    check_cmd = [sys.executable, "-c", "import pytest; print(pytest.__version__)"]
    try:
        check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
        if check_result.returncode != 0:
            return {
                "success": False,
                "error": "pytest is not installed or cannot be imported",
                "exit_code": -1,
                "stderr": check_result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Checking pytest availability timed out",
            "exit_code": -1
        }
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            env=env,
            timeout=60  # 60 second timeout
        )
        
        output_lines = result.stdout.split('\n') if result.stdout else []
        error_lines = result.stderr.split('\n') if result.stderr else []
        
        summary = _extract_pytest_summary(output_lines)
        
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "summary": summary,
            "test_path": str(test_path)
        }
        
    except subprocess.TimeoutExpired as e:
        logger.error(f"Pytest execution timed out after 60 seconds")
        return {
            "success": False,
            "error": "Test execution timed out after 60 seconds",
            "exit_code": -1,
            "stdout": e.stdout or "",
            "stderr": e.stderr or ""
        }
    except Exception as e:
        logger.error(f"Failed to run pytest: {e}")
        return {
            "success": False,
            "error": str(e),
            "exit_code": -1
        }


def _extract_pytest_summary(output_lines: List[str]) -> Dict[str, Any]:
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0
    }
    
    for line in output_lines:
        line = line.strip()
        if "passed" in line and "failed" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part.isdigit():
                    if i + 1 < len(parts):
                        next_word = parts[i + 1].lower()
                        if "passed" in next_word:
                            summary["passed"] = int(part)
                        elif "failed" in next_word:
                            summary["failed"] = int(part)
                        elif "skipped" in next_word:
                            summary["skipped"] = int(part)
                        elif "error" in next_word:
                            summary["errors"] = int(part)
                            
    summary["total"] = sum([summary["passed"], summary["failed"], summary["skipped"], summary["errors"]])
    return summary
