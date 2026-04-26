from __future__ import annotations

import json
import string
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.schemas import ExtractionRecord


FIELDS = [
    "company_name",
    "contact_name",
    "request_type",
    "priority",
    "budget_amount",
    "budget_currency",
    "deadline_iso",
    "action_items",
    "notes",
    "needs_human_review",
]

STOPWORDS = {
    "a",
    "an",
    "the",
    "to",
    "for",
    "of",
    "and",
    "or",
    "in",
    "on",
    "by",
    "with",
    "from",
    "their",
    "our",
    "us",
    "we",
    "you",
    "please",
    "need",
    "needs",
}


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


def load_prediction_examples(path: str | Path) -> list[dict[str, Any]]:
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


def _normalize_for_exact_match(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, list):
        return [_normalize_for_exact_match(item) for item in value]
    return value


def _values_match(gold_value: Any, prediction_value: Any) -> bool:
    return _normalize_for_exact_match(gold_value) == _normalize_for_exact_match(prediction_value)


def tokenize_text(text: str) -> set[str]:
    translation = str.maketrans("", "", string.punctuation)
    normalized = text.lower().translate(translation)
    return {token for token in normalized.split() if token and token not in STOPWORDS}


def action_items_to_tokens(items: Any) -> set[str]:
    if not isinstance(items, list):
        return set()

    tokens: set[str] = set()
    for item in items:
        if isinstance(item, str):
            tokens.update(tokenize_text(item))
    return tokens


def score_action_items(gold_items: Any, pred_items: Any) -> dict[str, float]:
    gold_tokens = action_items_to_tokens(gold_items)
    pred_tokens = action_items_to_tokens(pred_items)

    if not gold_tokens and not pred_tokens:
        return {
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "jaccard": 1.0,
        }

    if not gold_tokens or not pred_tokens:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "jaccard": 0.0,
        }

    intersection = gold_tokens & pred_tokens
    precision = len(intersection) / len(pred_tokens)
    recall = len(intersection) / len(gold_tokens)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    jaccard = len(intersection) / len(gold_tokens | pred_tokens)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "jaccard": jaccard,
    }


def evaluate_predictions(
    gold_examples: list[dict[str, Any]],
    pred_examples: list[dict[str, Any]],
) -> dict[str, Any]:
    gold_ids = {example["id"] for example in gold_examples}
    predictions_by_id = {example.get("id"): example for example in pred_examples}

    total_examples = len(gold_examples)
    prediction_success_count = 0
    error_count = sum(1 for example in pred_examples if example.get("error") is not None)
    invalid_prediction_count = 0
    valid_predictions_by_id: dict[str, dict[str, Any]] = {}
    for example in pred_examples:
        prediction_payload = example.get("prediction")
        if prediction_payload is None:
            continue
        try:
            valid_predictions_by_id[example.get("id")] = ExtractionRecord.model_validate(
                prediction_payload
            ).model_dump(mode="json")
        except ValidationError:
            invalid_prediction_count += 1

    missing_prediction_count = sum(1 for example in gold_examples if example["id"] not in predictions_by_id)
    extra_prediction_count = sum(1 for example in pred_examples if example.get("id") not in gold_ids)
    full_record_exact_match_count = 0
    field_exact_match_counts = dict.fromkeys(FIELDS, 0)
    action_items_token_precision_total = 0.0
    action_items_token_recall_total = 0.0
    action_items_token_f1_total = 0.0
    action_items_token_jaccard_total = 0.0

    for gold_example in gold_examples:
        row = predictions_by_id.get(gold_example["id"])
        target = ExtractionRecord.model_validate(gold_example["target"]).model_dump(mode="json")
        if row is None or row.get("error") is not None or row.get("prediction") is None:
            continue

        prediction = valid_predictions_by_id.get(gold_example["id"])
        if prediction is None:
            continue

        prediction_success_count += 1
        all_fields_match = True
        action_item_scores = score_action_items(target["action_items"], prediction["action_items"])
        action_items_token_precision_total += action_item_scores["precision"]
        action_items_token_recall_total += action_item_scores["recall"]
        action_items_token_f1_total += action_item_scores["f1"]
        action_items_token_jaccard_total += action_item_scores["jaccard"]

        for field in FIELDS:
            if _values_match(target[field], prediction[field]):
                field_exact_match_counts[field] += 1
            else:
                all_fields_match = False

        if all_fields_match:
            full_record_exact_match_count += 1

    field_exact_match_rates = {
        field: field_exact_match_counts[field] / total_examples if total_examples else 0
        for field in FIELDS
    }
    action_items_exact_match_rate = field_exact_match_rates["action_items"]

    return {
        "total_examples": total_examples,
        "prediction_success_count": prediction_success_count,
        "prediction_success_rate": prediction_success_count / total_examples if total_examples else 0,
        "error_count": error_count,
        "invalid_prediction_count": invalid_prediction_count,
        "missing_prediction_count": missing_prediction_count,
        "extra_prediction_count": extra_prediction_count,
        "full_record_exact_match_count": full_record_exact_match_count,
        "full_record_exact_match_rate": (
            full_record_exact_match_count / total_examples if total_examples else 0
        ),
        "field_exact_match_counts": field_exact_match_counts,
        "field_exact_match_rates": field_exact_match_rates,
        "action_items_exact_match_rate": action_items_exact_match_rate,
        "action_items_token_precision": (
            action_items_token_precision_total / total_examples if total_examples else 0
        ),
        "action_items_token_recall": (
            action_items_token_recall_total / total_examples if total_examples else 0
        ),
        "action_items_token_f1": action_items_token_f1_total / total_examples if total_examples else 0,
        "action_items_token_jaccard": (
            action_items_token_jaccard_total / total_examples if total_examples else 0
        ),
    }


def _format_rate(rate: float) -> str:
    return f"{rate * 100:.2f}%"


def build_prediction_eval_summary(results: dict[str, Any]) -> str:
    total = results["total_examples"]
    success_count = results["prediction_success_count"]
    full_match_count = results["full_record_exact_match_count"]
    field_counts = results["field_exact_match_counts"]
    field_rates = results["field_exact_match_rates"]

    lines = [
        "Prediction Eval Summary",
        "",
        f"Total examples: {total}",
        (
            f"Prediction success: {success_count}/{total} "
            f"({_format_rate(results['prediction_success_rate'])})"
        ),
        f"Errors: {results['error_count']}",
        f"Invalid predictions: {results['invalid_prediction_count']}",
        f"Missing predictions: {results['missing_prediction_count']}",
        f"Extra predictions: {results['extra_prediction_count']}",
        "",
        (
            f"Full record exact match: {full_match_count}/{total} "
            f"({_format_rate(results['full_record_exact_match_rate'])})"
        ),
        "",
        "Field exact match:",
    ]
    lines.extend(
        f"  {field}: {field_counts[field]}/{total} ({_format_rate(field_rates[field])})"
        for field in FIELDS
    )
    lines.extend(
        [
            "",
            "Soft action_items metrics:",
            (
                f"  exact_match: {field_counts['action_items']}/{total} "
                f"({_format_rate(results['action_items_exact_match_rate'])})"
            ),
            f"  token_precision: {_format_rate(results['action_items_token_precision'])}",
            f"  token_recall: {_format_rate(results['action_items_token_recall'])}",
            f"  token_f1: {_format_rate(results['action_items_token_f1'])}",
            f"  token_jaccard: {_format_rate(results['action_items_token_jaccard'])}",
        ]
    )
    return "\n".join(lines)


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
