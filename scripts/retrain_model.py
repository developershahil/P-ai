"""Simple retraining pipeline entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from personal_ai.learning.trainer import train_and_compare


def main() -> None:
    parser = argparse.ArgumentParser(description="Run model retraining and promotion checks.")
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional path to write the full retraining result as JSON.",
    )
    args = parser.parse_args()

    result = train_and_compare()

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print("Retraining result:")
    for key, value in result.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
