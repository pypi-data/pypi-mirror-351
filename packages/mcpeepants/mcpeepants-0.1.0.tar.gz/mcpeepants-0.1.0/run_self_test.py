"""Self-test script for the MCP Server Library."""

import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pytest_cov
        return True
    except ImportError:
        return False


def clean_coverage_data(project_root):
    """Clean up any existing coverage data to avoid conflicts."""
    coverage_files = [
        project_root / ".coverage",
        project_root / "htmlcov",
    ]
    
    for file_path in coverage_files:
        if file_path.exists():
            if file_path.is_file():
                file_path.unlink()
                print(f"Cleaned up: {file_path}")
            elif file_path.is_dir():
                import shutil
                shutil.rmtree(file_path)
                print(f"Cleaned up: {file_path}")


def run_self_test():
    """Run the test suite for this project."""
    project_root = Path(__file__).parent
    
    print("Running self-tests for mcpeepants...")
    print(f"Project root: {project_root}")
    
    # Check if pytest-cov is installed
    if not check_dependencies():
        print("\n⚠️  pytest-cov not installed. Installing development dependencies...")
        install_cmd = [sys.executable, "-m", "pip", "install", "-e", ".[dev]"]
        print(f"Running: {' '.join(install_cmd)}")
        result = subprocess.run(install_cmd, cwd=project_root)
        if result.returncode != 0:
            print("❌ Failed to install development dependencies")
            return 1
    
    # Clean up old coverage data to avoid conflicts
    print("\nCleaning up old coverage data...")
    clean_coverage_data(project_root)
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")
    
    # Run with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v", "--tb=short",
        "--cov=mcpeepants",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-m", "not hanging",  # Exclude hanging tests
        str(project_root / "tests")
    ]
    
    print(f"\nRunning command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, env=env)
    
    # If coverage fails for any reason, try without it
    if result.returncode != 0:
        print("\n⚠️  Coverage run failed. Running tests without coverage...")
        cmd = [
            sys.executable, "-m", "pytest",
            "-v", "--tb=short",
            "-m", "not hanging",  # Exclude hanging tests
            str(project_root / "tests")
        ]
        result = subprocess.run(cmd, env=env)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_self_test())
