#!/usr/bin/env python3
"""
Unit tests for hello.py module.
"""

import pytest
from io import StringIO
import sys
from hello import say_hello, main


def test_say_hello():
    """Test that say_hello returns the correct message."""
    expected_message = "Hello from Aira AI Agent!"
    assert say_hello() == expected_message


def test_main_output(capsys):
    """Test that main() prints the correct message."""
    main()
    captured = capsys.readouterr()
    expected_output = "Hello from Aira AI Agent!\n"
    assert captured.out == expected_output


def test_say_hello_returns_string():
    """Test that say_hello returns a string type."""
    result = say_hello()
    assert isinstance(result, str)


def test_say_hello_not_empty():
    """Test that say_hello returns a non-empty string."""
    result = say_hello()
    assert len(result) > 0