"""Test the pytest runner tool integration."""

def test_simple_pass():
    """A simple test that passes."""
    assert 1 + 1 == 2
    
def test_simple_list():
    """Test list operations."""
    items = [1, 2, 3]
    assert len(items) == 3
    assert sum(items) == 6
    
def test_string_operations():
    """Test string operations."""
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert text.split() == ["hello", "world"]
