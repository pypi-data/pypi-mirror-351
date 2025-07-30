"""Test the async pytest runner timeout functionality."""

import pytest
import asyncio
from pathlib import Path

from mcpeepants.async_tools import run_pytest_async


@pytest.mark.asyncio
async def test_pytest_timeout():
    """Test that pytest runner properly times out hanging tests."""
    test_file = Path(__file__).parent / "fixtures" / "test_hanging.py"
    
    # Run with a short timeout, specifically run the hanging test
    result = await run_pytest_async(
        test_path=str(test_file),
        extra_args=["-k", "test_hanging_test", "-m", "hanging"],
        timeout=5
    )
    
    assert not result["success"]
    assert "timed out" in result["error"]
    assert result["timeout"] == 5
    assert "hint" in result
    

@pytest.mark.asyncio
async def test_pytest_normal_completion():
    """Test that pytest runner completes normally for non-hanging tests."""
    test_file = Path(__file__).parent / "fixtures" / "test_hanging.py"
    
    # Run the slow test with adequate timeout
    result = await run_pytest_async(
        test_path=str(test_file),
        extra_args=["-k", "test_slow_test"],
        timeout=10
    )
    
    assert result["success"]
    assert result["exit_code"] == 0
    assert "1 passed" in result["stdout"]
