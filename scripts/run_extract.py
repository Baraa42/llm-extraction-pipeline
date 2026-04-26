from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluate import load_gold_examples
from src.extractor import extract_record


def _error_string(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run baseline LLM extraction.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--text", help="Single text input to extract from.")
    mode.add_argument("--gold", help="Path to a gold JSONL dataset.")
    parser.add_argument("--out", help="Path for prediction JSONL output.")
    parser.add_argument("--limit", type=int, help="Maximum number of examples to process.")
    return parser


def _run_single_text(input_text: str) -> int:
    try:
        record = extract_record(input_text)
    except Exception as exc:
        print(_error_string(exc), file=sys.stderr)
        return 1

    print(json.dumps(record.model_dump(mode="json"), indent=2))
    return 0


def _run_dataset(gold_path: str, out_path: str, limit: int | None) -> int:
    examples = load_gold_examples(gold_path)
    if limit is not None:
        examples = examples[:limit]

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    succeeded = 0
    failed = 0
    total = len(examples)

    with out.open("w", encoding="utf-8") as handle:
        for index, example in enumerate(examples, start=1):
            example_id = example.get("id", f"line_{index}")
            print(f"Processing {index}/{total}: {example_id}")

            try:
                record = extract_record(example["input_text"])
            except Exception as exc:
                failed += 1
                output = {
                    "id": example_id,
                    "prediction": None,
                    "raw_response": None,
                    "error": _error_string(exc),
                }
            else:
                succeeded += 1
                output = {
                    "id": example_id,
                    "prediction": record.model_dump(mode="json"),
                    "raw_response": None,
                    "error": None,
                }

            handle.write(json.dumps(output) + "\n")

    print(f"Processed: {total}")
    print(f"Succeeded: {succeeded}")
    print(f"Failed: {failed}")
    print(f"Saved to: {out_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.gold and not args.out:
        parser.error("--out is required when --gold is provided")

    try:
        if args.text is not None:
            return _run_single_text(args.text)
        return _run_dataset(args.gold, args.out, args.limit)
    except Exception as exc:
        print(_error_string(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
