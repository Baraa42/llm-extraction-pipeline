from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.schemas import ExtractionRecord


def load_gold_examples(path: str | Path) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return examples


def validate_examples(examples: list[dict[str, Any]]) -> tuple[list[ExtractionRecord], list[str]]:
    valid: list[ExtractionRecord] = []
    errors: list[str] = []

    for index, example in enumerate(examples, start=1):
        example_id = example.get("id", f"line {index}")
        try:
            valid.append(ExtractionRecord.model_validate(example["target"]))
        except KeyError:
            errors.append(f"{example_id}: missing target")
        except ValidationError as exc:
            errors.append(f"{example_id}: {exc.errors()[0]['msg']}")

    return valid, errors


def build_dry_run_summary(examples: list[dict[str, Any]], errors: list[str]) -> str:
    difficulty = Counter(example.get("meta", {}).get("difficulty") for example in examples)
    source_type = Counter(example.get("meta", {}).get("source_type") for example in examples)
    valid_count = len(examples) - len(errors)

    lines = [
        f"Loaded {len(examples)} examples",
        f"Valid examples: {valid_count}",
        f"Invalid examples: {len(errors)}",
        "",
        "Difficulty:",
    ]
    lines.extend(f"  {name}: {difficulty.get(name, 0)}" for name in ("easy", "medium", "hard"))
    lines.extend(["", "Source type:"])
    lines.extend(
        f"  {name}: {source_type.get(name, 0)}"
        for name in ("email", "support_ticket", "meeting_note", "call_note")
    )

    budget_present = sum(1 for example in examples if example["target"].get("budget_amount") is not None)
    deadline_present = sum(1 for example in examples if example["target"].get("deadline_iso") is not None)
    human_review = sum(1 for example in examples if example["target"].get("needs_human_review"))
    lines.extend(
        [
            "",
            f"Budget present: {budget_present}",
            f"Deadline present: {deadline_present}",
            f"Needs human review: {human_review}",
        ]
    )

    if errors:
        lines.extend(["", "Errors:"])
        lines.extend(f"  {error}" for error in errors)

    return "\n".join(lines)
