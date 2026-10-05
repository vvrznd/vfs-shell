"""Command line parser.

Splits a raw input line into tokens, correctly handling quoted
arguments. Uses shlex under the hood.
"""
import shlex


def parse(line: str) -> list[str]:
    """Split a line into tokens, respecting quotes.

    Args:
        line: Raw input string from the user.

    Returns:
        List of tokens. Empty list if the line is blank.

    Raises:
        ValueError: If the line contains unbalanced quotes.
    """
    stripped = line.strip()
    if not stripped:
        return []
    return shlex.split(stripped)