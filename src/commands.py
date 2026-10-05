"""Shell command implementations and dispatcher.

On stages 1-2 all commands except exit are stubs: they just print
their own name and arguments. Real logic is added later.
"""
from typing import Callable


class ExitShell(Exception):
    """Raised by the exit command to stop the REPL."""


class CommandError(Exception):
    """Raised when a command cannot be executed."""


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


def dispatch(tokens: list[str]) -> None:
    """Look up a command by name and run it.

    Args:
        tokens: Parsed tokens; tokens[0] is the command name,
            the rest are arguments.

    Raises:
        CommandError: If the command name is not known.
    """
    name, args = tokens[0], tokens[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        raise CommandError(f"unknown command: {name}")
    handler(args)