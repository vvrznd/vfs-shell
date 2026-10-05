"""Interactive shell (REPL)."""
import getpass
import os
import socket
import sys

from .commands import CommandError, ExitShell, dispatch
from .parser import parse


def _shorten_cwd(cwd: str, home: str) -> str:
    """Replace the home prefix with ~ and normalize separators."""
    normalized = cwd.replace("\\", "/")
    home_norm = home.replace("\\", "/")
    if normalized == home_norm:
        return "~"
    if normalized.startswith(home_norm + "/"):
        return "~" + normalized[len(home_norm):]
    return normalized


def build_prompt() -> str:
    """Form the prompt from real OS data: user@host:cwd$ ."""
    user = getpass.getuser()
    host = socket.gethostname()
    cwd = _shorten_cwd(os.getcwd(), os.path.expanduser("~"))
    return f"{user}@{host}:{cwd}$ "


def _execute(tokens: list[str]) -> bool:
    """Run tokens through the dispatcher.

    Args:
        tokens: Parsed command line tokens.

    Returns:
        True if the command succeeded, False on error.
    """
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


def run() -> int:
    """Run the REPL loop until exit or EOF."""
    while True:
        try:
            line = input(build_prompt())
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            continue

        try:
            tokens = parse(line)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            continue

        if not tokens:
            continue

        try:
            _execute(tokens)
        except ExitShell:
            return 0