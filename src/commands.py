"""Shell command implementations.

On stage 1 all commands except exit are stubs: they just print
their own name and arguments. Real logic will be added later.
"""
from typing import Callable


class ExitShell(Exception):
    """Raised by the exit command to stop the REPL."""


def _print_stub(name: str, args: list[str]) -> None:
    """Print a stub message with the command name and args."""
    print(f"{name}: {args}")


def cmd_ls(args: list[str]) -> None:
    """Stub for the ls command.

    Args:
        args: Command arguments.
    """
    _print_stub("ls", args)


def cmd_cd(args: list[str]) -> None:
    """Stub for the cd command.

    Args:
        args: Command arguments.
    """
    _print_stub("cd", args)


def cmd_exit(args: list[str]) -> None:
    """Exit the shell.

    Args:
        args: Command arguments (ignored).
    """
    raise ExitShell()


CommandHandler = Callable[[list[str]], None]

COMMANDS: dict[str, CommandHandler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}