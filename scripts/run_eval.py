from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluate import build_dry_run_summary, load_gold_examples, validate_examples


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate gold extraction examples.")
    parser.add_argument("--gold", required=True, help="Path to a gold JSONL dataset.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print dataset summary.")
    args = parser.parse_args()

    examples = load_gold_examples(args.gold)
    _, errors = validate_examples(examples)

    if args.dry_run:
        print(build_dry_run_summary(examples, errors))

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
