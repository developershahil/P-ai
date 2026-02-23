"""Build standalone executable using PyInstaller."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENTRY = PROJECT_ROOT / "personal_ai" / "main.py"


def main() -> None:
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        "personal-ai",
        str(ENTRY),
    ]
    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    main()
