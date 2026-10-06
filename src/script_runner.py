"""Startup script runner.

Reads a script file line by line, executes each line through the
same dispatcher as the interactive shell, and stops at the first
error. Both input and output are shown, imitating a dialogue.
"""
import sys
from collections.abc import Callable

from .commands import CommandError, ExitShellError, dispatch
from .context import ShellContext
from .parser import parse

PromptBuilder = Callable[[ShellContext], str]


def _run_line(ctx: ShellContext, line: str, prompt: str) -> bool:
    """Run a single script line.

    Args:
        ctx: Shell context.
        line: Raw line from the script file.
        prompt: Prompt to print before the line.

    Returns:
        True to continue, False to stop.

    Raises:
        ExitShellError: If the line contains the exit command.

    """
    print(f"{prompt}{line}")
    ctx.last_input = line
    try:
        tokens = parse(line)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return False

    if not tokens:
        return True

    try:
        dispatch(ctx, tokens)
    except ExitShellError:
        raise
    except CommandError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return False
    return True


def run_script(
    ctx: ShellContext, path: str, prompt_builder: PromptBuilder
) -> int:
    """Execute commands from a script file.

    Args:
        ctx: Shell context.
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
        prompt = prompt_builder(ctx)
        try:
            ok = _run_line(ctx, line, prompt)
        except ExitShellError:
            return 0
        if not ok:
            return 1
    return 0
