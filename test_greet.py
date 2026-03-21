"""Unit tests for the greet module."""

import pytest
from greet import greet


def test_greet_basic():
    """Test that greet returns a personalized greeting."""
    assert greet("Alice") == "Hello, Alice!"


def test_greet_different_name():
    """Test greet with a different name."""
    assert greet("Bob") == "Hello, Bob!"


def test_greet_returns_string():
    """Test that greet always returns a string."""
    result = greet("Charlie")
    assert isinstance(result, str)


def test_greet_contains_name():
    """Test that the greeting contains the provided name."""
    name = "Diana"
    result = greet(name)
    assert name in result


def test_greet_empty_string():
    """Test greet with an empty string."""
    result = greet("")
    assert result == "Hello, !"


def test_greet_with_spaces():
    """Test greet with a name containing spaces."""
    assert greet("John Doe") == "Hello, John Doe!"
