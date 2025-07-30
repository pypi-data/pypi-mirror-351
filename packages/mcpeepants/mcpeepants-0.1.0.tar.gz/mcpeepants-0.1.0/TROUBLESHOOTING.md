# Known Issues and Solutions

## pytest_runner Timeout Issue

### Problem
When running `pytest_runner` on the mcpeepants test suite itself, you may encounter a timeout error. This is because the test suite includes an intentionally hanging test (`test_hanging_test`) designed to test the timeout functionality.

### Solution
The hanging test is now marked with `@pytest.mark.hanging` and excluded by default. If you still experience timeouts:

1. **Run tests excluding the hanging marker**:
   ```bash
   pytest -m "not hanging"
   ```

2. **Use pytest_runner with exclusions**:
   ```python
   result = await pytest_runner(extra_args=["-m", "not hanging"])
   ```

3. **Increase timeout for slow tests**:
   ```python
   result = await pytest_runner(timeout=120)  # 2 minutes
   ```

### Testing the Timeout Feature
To specifically test the timeout functionality:
```python
# This will timeout as expected
result = await pytest_runner(
    test_path="tests/fixtures/test_hanging.py",
    extra_args=["-k", "test_hanging_test", "-m", "hanging"],
    timeout=5
)
```

## Other Common Issues

### "pytest not installed" Error
- **Solution**: Install pytest in the target project: `pip install pytest`

### Import Errors
- **Solution**: Ensure PYTHONPATH includes the project root (automatically handled by mcpeepants)

### Windows-specific Issues
- **Solution**: Use forward slashes in paths or raw strings (r"C:\path\to\tests")
