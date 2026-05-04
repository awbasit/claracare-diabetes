"""Root launcher for ClaraCare CLI without PYTHONPATH setup."""

import sys
from pathlib import Path


def main() -> None:
    """Add src to path and run claracare CLI."""
    root = Path(__file__).resolve().parent
    src = root / "src"
    assert src.exists(), f"Missing src directory: {src}"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from claracare.cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
