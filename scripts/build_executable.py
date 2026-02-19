"""Build standalone executable using PyInstaller."""

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENTRY = PROJECT_ROOT / "personal_ai" / "main.py"


if __name__ == "__main__":
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
