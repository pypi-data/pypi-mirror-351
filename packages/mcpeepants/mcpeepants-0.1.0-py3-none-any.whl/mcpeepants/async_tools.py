"""Async-safe pytest runner for MCP server."""

import asyncio
import os
import sys
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


async def run_pytest_async(
    test_path: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Run pytest asynchronously to avoid blocking the MCP server.
    
    Args:
        test_path: Path to test file or directory
        extra_args: Additional pytest arguments
        timeout: Maximum execution time in seconds
        
    Returns:
        Test execution results
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
    
    # First check if pytest is available
    check_cmd = [sys.executable, "-c", "import pytest; print(pytest.__version__)"]
    try:
        proc = await asyncio.create_subprocess_exec(
            *check_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
        if proc.returncode != 0:
            return {
                "success": False,
                "error": "pytest is not installed. Please install it with: pip install pytest",
                "exit_code": -1,
                "stderr": stderr.decode('utf-8', errors='replace') if stderr else ""
            }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Checking pytest availability timed out",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to check pytest availability: {str(e)}",
            "exit_code": -1
        }
    
    # Build minimal pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "-p", "no:cacheprovider",
        "-p", "no:warnings", 
        "-p", "no:cov",
        "--tb=short",
        "-v",
        "-s",
        "--no-header",
        str(test_path)
    ]
    
    if extra_args:
        cmd.extend(extra_args)
        
    # Set up clean environment
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PY_COLORS"] = "0"
    
    # Ensure proper Python path
    project_root = Path(__file__).parent.parent.parent
    env["PYTHONPATH"] = str(project_root)
    
    logger.info(f"Running async pytest: {' '.join(cmd)}")
    
    try:
        # Create subprocess
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=str(test_path.parent if test_path.is_file() else test_path)
        )
        
        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Pytest timed out after {timeout}s, attempting to terminate...")
            
            # Try graceful termination first
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                # Force kill if graceful termination fails
                logger.warning("Graceful termination failed, force killing pytest process...")
                proc.kill()
                await proc.wait()
            
            return {
                "success": False,
                "error": f"Test execution timed out after {timeout} seconds. This may indicate tests are hanging or taking too long.",
                "exit_code": -1,
                "timeout": timeout,
                "hint": "Try running with a longer timeout or check for hanging tests"
            }
        
        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
        
        # Extract summary
        summary = _extract_pytest_summary(stdout_text.split('\n'))
        
        return {
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "summary": summary,
            "test_path": str(test_path)
        }
        
    except Exception as e:
        logger.error(f"Failed to run pytest: {e}")
        return {
            "success": False,
            "error": str(e),
            "exit_code": -1
        }


def _extract_pytest_summary(output_lines: List[str]) -> Dict[str, Any]:
    """Extract test summary from pytest output."""
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0
    }
    
    for line in output_lines:
        line = line.strip()
        # Look for summary line like "5 passed in 0.12s"
        parts = line.split()
        for i, part in enumerate(parts):
            if part.isdigit() and i + 1 < len(parts):
                next_word = parts[i + 1].lower()
                count = int(part)
                if "passed" in next_word:
                    summary["passed"] = count
                elif "failed" in next_word:
                    summary["failed"] = count
                elif "skipped" in next_word:
                    summary["skipped"] = count
                elif "error" in next_word:
                    summary["errors"] = count
                    
    summary["total"] = sum([
        summary["passed"], 
        summary["failed"], 
        summary["skipped"], 
        summary["errors"]
    ])
    
    return summary


def run_pytest_sync(
    test_path: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Synchronous wrapper for run_pytest_async.
    """
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
            # We're already in an async context
            # Create a task and run it
            return asyncio.create_task(
                run_pytest_async(test_path, extra_args, timeout)
            )
        except RuntimeError:
            # No running loop, create one
            return asyncio.run(
                run_pytest_async(test_path, extra_args, timeout)
            )
    except Exception as e:
        logger.error(f"Failed to run pytest sync wrapper: {e}")
        return {
            "success": False,
            "error": f"Failed to execute pytest: {str(e)}",
            "exit_code": -1
        }
