"""Interactive shell (REPL)."""
import getpass
import socket
import sys

from .commands import CommandError, ExitShellError, dispatch
from .context import ShellContext
from .parser import parse


def _username() -> str:
    """Return the current OS username."""
    return getpass.getuser()


def _hostname() -> str:
    """Return the current OS hostname."""
    return socket.gethostname()


def build_prompt(ctx: ShellContext) -> str:
    """Form the prompt: user@host:vfs_cwd$ ."""
    user = _username()
    host = _hostname()
    return f"{user}@{host}:{ctx.cwd}$ "


def _execute(ctx: ShellContext, tokens: list[str]) -> bool:
    """Run tokens through the dispatcher."""
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


def run(ctx: ShellContext) -> int:
    """Run the REPL loop until exit or EOF."""
    while True:
        try:
            line = input(build_prompt(ctx))
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            continue

        ctx.last_input = line
        try:
            tokens = parse(line)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            continue

        if not tokens:
            continue

        try:
            _execute(ctx, tokens)
        except ExitShellError:
            return 0
