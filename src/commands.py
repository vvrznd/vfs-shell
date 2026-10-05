"""Shell command implementations.

All commands operate on a VirtualFileSystem in memory. They
receive a ShellContext carrying the VFS and the current working
directory inside it.
"""
import calendar
import datetime
from collections.abc import Callable

from .context import ShellContext
from .vfs import DIR_TYPE, VfsError

LONG_FLAG = "-l"
DEFAULT_CWD = "."
HOME_CANDIDATES = ("/home/user", "/home", "/")
OWNER_WIDTH = 8
SIZE_WIDTH = 6


class ExitShellError(Exception):
    """Raised by the exit command to stop the REPL."""


class CommandError(Exception):
    """Raised when a command cannot be executed."""


def _join(base: str, name: str) -> str:
    """Join a directory path and a child name."""
    if base == "/":
        return "/" + name
    return base.rstrip("/") + "/" + name


def _require_dir(ctx: ShellContext, path: str) -> None:
    """Raise CommandError unless path is a directory."""
    if not ctx.vfs.is_dir(path):
        raise CommandError(f"not a directory: {path}")


def _require_file(ctx: ShellContext, path: str) -> None:
    """Raise CommandError unless path is a file."""
    if not ctx.vfs.is_file(path):
        raise CommandError(f"not a file: {path}")


def _print_long(node, name: str) -> None:
    """Print a single entry in long format."""
    marker = "d" if node.kind == DIR_TYPE else "-"
    size = len(node.content)
    owner = f"{node.owner:<{OWNER_WIDTH}}"
    print(f"{marker} {owner} {size:>{SIZE_WIDTH}} {name}")


def cmd_ls(ctx: ShellContext, args: list[str]) -> None:
    """List VFS directory contents."""
    long_format = LONG_FLAG in args
    operands = [a for a in args if a != LONG_FLAG]
    target = operands[0] if operands else DEFAULT_CWD
    path = ctx.vfs.resolve(ctx.cwd, target)
    _require_dir(ctx, path)
    for name in ctx.vfs.list_dir(path):
        if long_format:
            node = ctx.vfs.get(_join(path, name))
            _print_long(node, name)
        else:
            print(name)


def _pick_home(ctx: ShellContext) -> str:
    """Return the first home directory that exists in the VFS."""
    for candidate in HOME_CANDIDATES:
        if ctx.vfs.is_dir(candidate):
            return candidate
    return "/"


def cmd_cd(ctx: ShellContext, args: list[str]) -> None:
    """Change current directory inside the VFS."""
    if not args:
        target = _pick_home(ctx)
    elif len(args) == 1:
        target = args[0]
    else:
        raise CommandError("cd: too many arguments")
    new_path = ctx.vfs.resolve(ctx.cwd, target)
    _require_dir(ctx, new_path)
    ctx.cwd = new_path


def cmd_exit(ctx: ShellContext, args: list[str]) -> None:
    """Exit the shell."""
    raise ExitShellError()


def cmd_tac(ctx: ShellContext, args: list[str]) -> None:
    """Print a file with its lines in reverse order."""
    if len(args) != 1:
        raise CommandError("tac: exactly one file argument required")
    path = ctx.vfs.resolve(ctx.cwd, args[0])
    _require_file(ctx, path)
    text = ctx.vfs.read_file(path).decode("utf-8", errors="replace")
    for line in reversed(text.splitlines()):
        print(line)


def _read_rev_source(ctx: ShellContext, args: list[str]) -> str:
    """Return text to be reversed by rev."""
    if len(args) > 1:
        raise CommandError("rev: at most one argument allowed")
    if args:
        path = ctx.vfs.resolve(ctx.cwd, args[0])
        _require_file(ctx, path)
        data = ctx.vfs.read_file(path)
        return data.decode("utf-8", errors="replace")
    return ctx.last_input


def cmd_rev(ctx: ShellContext, args: list[str]) -> None:
    """Reverse each line of a file (or the last input line)."""
    text = _read_rev_source(ctx, args)
    for line in text.splitlines():
        print(line[::-1])


def cmd_cal(ctx: ShellContext, args: list[str]) -> None:
    """Print a calendar for the current month."""
    if args:
        raise CommandError("cal: no arguments supported yet")
    today = datetime.datetime.now(
        tz=datetime.timezone.utc,
    ).date()
    calendar.setfirstweekday(calendar.MONDAY)
    print(calendar.month(today.year, today.month))


def _require_exists(ctx: ShellContext, path: str) -> None:
    """Raise CommandError unless the path exists in the VFS."""
    if path not in ctx.vfs:
        raise CommandError(f"no such path: {path}")


def _is_root(path: str) -> bool:
    """Return True if path points to the VFS root."""
    return path == "/" or path == ""


def cmd_rm(ctx: ShellContext, args: list[str]) -> None:
    """Remove a file from the VFS (in memory only)."""
    if len(args) != 1:
        raise CommandError("rm: exactly one file argument required")
    path = ctx.vfs.resolve(ctx.cwd, args[0])
    _require_exists(ctx, path)
    node = ctx.vfs.get(path)
    if node.kind == DIR_TYPE:
        raise CommandError(f"rm: is a directory: {path}")
    ctx.vfs.remove(path)


def cmd_rmdir(ctx: ShellContext, args: list[str]) -> None:
    """Remove an empty directory from the VFS (in memory only)."""
    if len(args) != 1:
        raise CommandError("rmdir: exactly one argument required")
    path = ctx.vfs.resolve(ctx.cwd, args[0])
    if _is_root(path):
        raise CommandError("rmdir: cannot remove root directory")
    _require_exists(ctx, path)
    node = ctx.vfs.get(path)
    if node.kind != DIR_TYPE:
        raise CommandError(f"rmdir: not a directory: {path}")
    if ctx.vfs.has_children(path):
        raise CommandError(f"rmdir: directory not empty: {path}")
    ctx.vfs.remove(path)


CommandHandler = Callable[[ShellContext, list[str]], None]

COMMANDS: dict[str, CommandHandler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "tac": cmd_tac,
    "rev": cmd_rev,
    "cal": cmd_cal,
    "rm": cmd_rm,
    "rmdir": cmd_rmdir,
}


def dispatch(ctx: ShellContext, tokens: list[str]) -> None:
    """Look up a command by name and run it."""
    name, args = tokens[0], tokens[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        raise CommandError(f"unknown command: {name}")
    try:
        handler(ctx, args)
    except VfsError as exc:
        raise CommandError(str(exc)) from exc