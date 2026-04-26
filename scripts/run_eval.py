from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluate import (
    build_dry_run_summary,
    build_prediction_eval_summary,
    evaluate_predictions,
    load_gold_examples,
    load_prediction_examples,
    validate_examples,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate gold extraction examples.")
    parser.add_argument("--gold", required=True, help="Path to a gold JSONL dataset.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print dataset summary.")
    parser.add_argument("--pred", help="Path to a prediction JSONL file.")
    args = parser.parse_args(argv)

    examples = load_gold_examples(args.gold)
    _, errors = validate_examples(examples)

    if args.dry_run:
        print(build_dry_run_summary(examples, errors))

    if errors:
        return 1

    if args.pred:
        if args.dry_run:
            print()
        prediction_examples = load_prediction_examples(args.pred)
        results = evaluate_predictions(examples, prediction_examples)
        print(build_prediction_eval_summary(results))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
