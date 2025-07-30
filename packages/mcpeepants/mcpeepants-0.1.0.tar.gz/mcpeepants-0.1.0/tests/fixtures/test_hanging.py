"""Test fixture that simulates a hanging test."""

import time
import pytest


def test_slow_test():
    """A test that runs slowly but completes."""
    time.sleep(2)
    assert True


@pytest.mark.hanging
def test_hanging_test():
    """A test that hangs indefinitely."""
    # This test is marked as 'hanging' and should be excluded by default
    # It's only used for testing timeout functionality
    while True:
        time.sleep(1)
