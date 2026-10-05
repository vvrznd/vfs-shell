"""Entry point for the shell emulator."""
import argparse
import sys

from .config import Config, debug_dump
from .script_runner import run_script
from .shell import build_prompt, run


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        argv: List of arguments (without the program name).

    Returns:
        Parsed namespace with vfs_path and script_path.
    """
    parser = argparse.ArgumentParser(
        prog="vfs-shell",
        description="Shell emulator with a virtual file system.",
    )
    parser.add_argument(
        "--vfs-path",
        dest="vfs_path",
        default=None,
        help="Path to the physical VFS location.",
    )
    parser.add_argument(
        "--script-path",
        dest="script_path",
        default=None,
        help="Path to the startup script.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Start the shell or run a startup script.

    Args:
        argv: Arguments passed to the program. If None, uses
            sys.argv[1:].

    Returns:
        Exit code: 0 on success, non-zero on error.
    """
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    config = Config(vfs_path=args.vfs_path, script_path=args.script_path)
    debug_dump(config)

    if config.script_path:
        return run_script(config.script_path, build_prompt)
    return run()


if __name__ == "__main__":
    sys.exit(main())