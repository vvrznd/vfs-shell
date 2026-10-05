"""Tests for the command line parser."""
import pytest

from src.parser import parse


def test_empty_string_returns_empty_list() -> None:
    """Empty input should produce an empty token list."""
    assert parse("") == []


def test_only_spaces_returns_empty_list() -> None:
    """Whitespace-only input should produce an empty token list."""
    assert parse("    ") == []


def test_simple_command_without_args() -> None:
    """A single word becomes a one-element list."""
    assert parse("ls") == ["ls"]


def test_command_with_args() -> None:
    """Words separated by spaces become separate tokens."""
    assert parse("ls -la /home") == ["ls", "-la", "/home"]


def test_double_quoted_argument_is_single_token() -> None:
    """Text inside double quotes stays as one token."""
    result = parse('ls "file with spaces"')
    assert result == ["ls", "file with spaces"]


def test_single_quoted_argument_is_single_token() -> None:
    """Text inside single quotes stays as one token."""
    result = parse("cd 'my dir'")
    assert result == ["cd", "my dir"]


def test_leading_and_trailing_spaces_are_ignored() -> None:
    """Surrounding whitespace should be stripped."""
    assert parse("   ls   ") == ["ls"]


def test_unbalanced_quote_raises_value_error() -> None:
    """An unterminated quote is a syntax error."""
    with pytest.raises(ValueError):
        parse('ls "unterminated')