"""Runtime configuration for the shell emulator."""
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration collected from CLI arguments.

    Attributes:
        vfs_path: Path to the physical VFS location, or None.
        script_path: Path to the startup script, or None.

    """

    vfs_path: str | None = None
    script_path: str | None = None


def debug_dump(config: Config) -> None:
    """Print the configuration in a debug-friendly format.

    Args:
        config: Configuration to print.

    """
    print("[debug] configuration:")
    print(f"[debug]   vfs_path    = {config.vfs_path!r}")
    print(f"[debug]   script_path = {config.script_path!r}")