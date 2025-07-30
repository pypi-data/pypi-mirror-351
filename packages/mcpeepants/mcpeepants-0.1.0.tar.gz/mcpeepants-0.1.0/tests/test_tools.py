"""Tests for built-in tools."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from mcpeepants.tools import run_pytest, _extract_pytest_summary


class TestRunPytest:
    def test_run_pytest_default_path(self):
        with patch.dict(os.environ, {"PYTEST_PATH": "."}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="test output",
                    stderr=""
                )
                
                result = run_pytest()
                
                assert result["success"] is True
                assert result["exit_code"] == 0
                assert result["test_path"] == "."
                
    def test_run_pytest_custom_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_example.py"
            test_file.write_text("def test_pass(): pass")
            
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="1 passed",
                    stderr=""
                )
                
                result = run_pytest(str(tmpdir))
                
                assert result["success"] is True
                assert result["test_path"] == str(tmpdir)
                
    def test_run_pytest_nonexistent_path(self):
        result = run_pytest("/nonexistent/path")
        
        assert result["success"] is False
        assert "does not exist" in result["error"]
        assert result["exit_code"] == 1
        
    def test_run_pytest_with_extra_args(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="",
                stderr=""
            )
            
            run_pytest(extra_args=["-k", "test_name", "-x"])
            
            call_args = mock_run.call_args[0][0]
            assert "-k" in call_args
            assert "test_name" in call_args
            assert "-x" in call_args
            
    def test_run_pytest_failure(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="1 failed",
                stderr="error output"
            )
            
            result = run_pytest()
            
            assert result["success"] is False
            assert result["exit_code"] == 1
            assert result["stderr"] == "error output"
            
    def test_run_pytest_exception(self):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test exception")
            
            result = run_pytest()
            
            assert result["success"] is False
            assert result["error"] == "Test exception"
            assert result["exit_code"] == -1
            
    def test_capture_output_flag(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="",
                stderr=""
            )
            
            run_pytest(capture_output=True)
            
            call_args = mock_run.call_args[0][0]
            assert "-v" in call_args
            assert "--tb=short" in call_args
            assert "--no-header" in call_args
            
            
class TestExtractPytestSummary:
    def test_extract_summary_basic(self):
        output_lines = [
            "collected 5 items",
            "",
            "test_file.py::test_one PASSED",
            "test_file.py::test_two FAILED",
            "",
            "3 passed, 1 failed, 1 skipped in 0.5s"
        ]
        
        summary = _extract_pytest_summary(output_lines)
        
        assert summary["passed"] == 3
        assert summary["failed"] == 1
        assert summary["skipped"] == 1
        assert summary["total"] == 5
        
    def test_extract_summary_with_errors(self):
        output_lines = [
            "2 passed, 1 failed, 2 errors in 1.0s"
        ]
        
        summary = _extract_pytest_summary(output_lines)
        
        assert summary["passed"] == 2
        assert summary["failed"] == 1
        assert summary["errors"] == 2
        assert summary["total"] == 5
        
    def test_extract_summary_no_results(self):
        output_lines = ["no tests ran"]
        
        summary = _extract_pytest_summary(output_lines)
        
        assert summary["total"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0
        
    def test_extract_summary_empty_output(self):
        summary = _extract_pytest_summary([])
        
        assert summary["total"] == 0
        assert all(v == 0 for k, v in summary.items() if k != "total")
