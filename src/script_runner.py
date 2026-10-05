"""Startup script runner.

Reads a script file line by line, executes each line through the
same dispatcher as the interactive shell, and stops at the first
error. Both input and output are shown, imitating a dialogue.
"""
import sys
from typing import Callable

from .commands import CommandError, ExitShell, dispatch
from .parser import parse

PromptBuilder = Callable[[], str]


def _run_line(line: str, prompt: str) -> bool:
    """Run a single script line.

    Args:
        line: Raw line from the script file.
        prompt: Prompt to print before the line.

    Returns:
        True to continue, False to stop (error occurred).

    Raises:
        ExitShell: If the line contains the exit command.
    """
    print(f"{prompt}{line}")
    try:
        tokens = parse(line)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return False

    if not tokens:
        return True

    try:
        dispatch(tokens)
    except ExitShell:
        raise
    except CommandError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return False
    return True


def run_script(path: str, prompt_builder: PromptBuilder) -> int:
    """Execute commands from a script file.

    Args:
        path: Path to the script file.
        prompt_builder: Callable that returns the prompt string.

    Returns:
        0 on success, 1 if the script could not be read or an
        error occurred during execution.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as exc:
        print(f"error: cannot read script: {exc}", file=sys.stderr)
        return 1

    for line in lines:
        prompt = prompt_builder()
        try:
            ok = _run_line(line, prompt)
        except ExitShell:
            return 0
        if not ok:
            return 1
    return 0