"""Windows-oriented smoke checks for direct script execution."""

from __future__ import annotations

import inspect
import sys
from importlib.util import find_spec
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from personal_ai.core.assistant import handle_input


def main() -> None:
    result = handle_input("time")
    print("Assistant smoke check passed:", result.get("reply", ""))

    if find_spec("joblib") is None:
        print("Retrain dry-run not available in this environment; skipping optional retrain smoke check.")
        return

    from personal_ai.learning.trainer import train_and_compare

    signature = inspect.signature(train_and_compare)
    if "dry_run" in signature.parameters:
        retrain_result = train_and_compare(dry_run=True)
        print("Retrain dry-run check passed:", retrain_result.get("action", "unknown"))
    else:
        print("Retrain dry-run not supported; skipping optional retrain smoke check.")


if __name__ == "__main__":
    main()
