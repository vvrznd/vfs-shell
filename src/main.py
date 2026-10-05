"""Entry point for the shell emulator."""
import sys

from .shell import run


def main() -> int:
    """Start the interactive shell."""
    return run()


if __name__ == "__main__":
    sys.exit(main())