"""Shared shell context passed to command handlers."""
from dataclasses import dataclass

from .vfs import VirtualFileSystem


@dataclass
class ShellContext:
    """State shared between commands during a shell session.

    Attributes:
        vfs: Virtual file system in use.
        cwd: Current working directory inside the VFS.
        last_input: Last raw input line (used by rev when no file).
    """
    vfs: VirtualFileSystem
    cwd: str = "/"
    last_input: str = ""