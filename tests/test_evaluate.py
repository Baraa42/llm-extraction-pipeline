from pathlib import Path
import json

from src.evaluate import (
    FIELDS,
    build_dry_run_summary,
    build_prediction_eval_summary,
    evaluate_predictions,
    load_gold_examples,
    load_prediction_examples,
    score_action_items,
    tokenize_text,
    validate_examples,
)
from scripts import run_eval


GOLD_PATH = Path("data/gold/gold_v1.jsonl")


def make_target(**overrides):
    target = {
        "company_name": "Acme",
        "contact_name": "Sarah",
        "request_type": "implementation_request",
        "priority": "medium",
        "budget_amount": 12000,
        "budget_currency": "USD",
        "deadline_iso": "2026-05-15",
        "action_items": ["Migrate Zendesk setup"],
        "notes": None,
        "needs_human_review": False,
    }
    target.update(overrides)
    return target


def test_gold_dataset_loads_and_validates():
    examples = load_gold_examples(GOLD_PATH)
    records, errors = validate_examples(examples)

    assert len(examples) == 40
    assert len(records) == 40
    assert errors == []


def test_dry_run_summary_output():
    examples = load_gold_examples(GOLD_PATH)
    _, errors = validate_examples(examples)

    output = build_dry_run_summary(examples, errors)

    assert "Loaded 40 examples" in output
    assert "Valid examples: 40" in output
    assert "Invalid examples: 0" in output
    assert "Difficulty:" in output
    assert "Source type:" in output
    assert "Budget present:" in output
    assert "Deadline present:" in output
    assert "Needs human review:" in output


def test_load_prediction_examples_loads_valid_jsonl(tmp_path):
    pred_path = tmp_path / "pred.jsonl"
    prediction = make_target()
    pred_path.write_text(
        json.dumps(
            {
                "id": "ex_001",
                "prediction": prediction,
                "raw_response": None,
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    examples = load_prediction_examples(pred_path)

    assert examples == [
        {
            "id": "ex_001",
            "prediction": prediction,
            "raw_response": None,
            "error": None,
        }
    ]


def test_tokenize_text_lowercases_strips_punctuation_and_stopwords():
    assert tokenize_text(" Fix the booking page! ") == {"fix", "booking", "page"}


def test_score_action_items_handles_casing_and_punctuation_overlap():
    score = score_action_items(["Fix booking page"], ["fix the booking page!"])

    assert score["precision"] == 1.0
    assert score["recall"] == 1.0
    assert score["f1"] > 0
    assert score["jaccard"] == 1.0


def test_score_action_items_exact_same_items_scores_one():
    score = score_action_items(["Fix booking page"], ["Fix booking page"])

    assert score == {
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0,
        "jaccard": 1.0,
    }


def test_score_action_items_unrelated_items_scores_zero():
    score = score_action_items(["Fix booking page"], ["Prepare finance report"])

    assert score == {
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "jaccard": 0.0,
    }


def test_score_action_items_both_empty_scores_one():
    score = score_action_items([], [])

    assert score == {
        "precision": 1.0,
        "recall": 1.0,
        "f1": 1.0,
        "jaccard": 1.0,
    }


def test_score_action_items_one_empty_scores_zero():
    score = score_action_items(["Fix booking page"], [])

    assert score == {
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "jaccard": 0.0,
    }


def test_evaluate_predictions_computes_exact_match_metrics():
    target = make_target(company_name=" Acme ")
    prediction = make_target(company_name="acme")
    gold_examples = [{"id": "ex_001", "target": target}]
    pred_examples = [{"id": "ex_001", "prediction": prediction, "error": None}]

    results = evaluate_predictions(gold_examples, pred_examples)

    assert results["total_examples"] == 1
    assert results["prediction_success_count"] == 1
    assert results["prediction_success_rate"] == 1
    assert results["error_count"] == 0
    assert results["invalid_prediction_count"] == 0
    assert results["missing_prediction_count"] == 0
    assert results["extra_prediction_count"] == 0
    assert results["full_record_exact_match_count"] == 1
    assert results["full_record_exact_match_rate"] == 1
    assert results["field_exact_match_counts"] == dict.fromkeys(FIELDS, 1)
    assert results["action_items_exact_match_rate"] == 1
    assert results["action_items_token_precision"] == 1
    assert results["action_items_token_recall"] == 1
    assert results["action_items_token_f1"] == 1
    assert results["action_items_token_jaccard"] == 1


def test_evaluate_predictions_counts_mismatched_fields():
    target = make_target(priority="medium", action_items=["Migrate Zendesk setup"])
    prediction = make_target(priority="high", action_items=["Prepare project plan"])
    gold_examples = [{"id": "ex_001", "target": target}]
    pred_examples = [{"id": "ex_001", "prediction": prediction, "error": None}]

    results = evaluate_predictions(gold_examples, pred_examples)

    assert results["full_record_exact_match_count"] == 0
    assert results["field_exact_match_counts"]["priority"] == 0
    assert results["field_exact_match_counts"]["action_items"] == 0
    assert results["field_exact_match_counts"]["company_name"] == 1
    assert results["action_items_token_precision"] == 0
    assert results["action_items_token_recall"] == 0
    assert results["action_items_token_f1"] == 0
    assert results["action_items_token_jaccard"] == 0


def test_evaluate_predictions_counts_missing_predictions_as_incorrect():
    gold_examples = [
        {"id": "ex_001", "target": make_target(company_name="Acme")},
        {"id": "ex_002", "target": make_target(company_name="Beta")},
    ]
    pred_examples = [{"id": "ex_001", "prediction": make_target(company_name="Acme"), "error": None}]

    results = evaluate_predictions(gold_examples, pred_examples)

    assert results["total_examples"] == 2
    assert results["prediction_success_count"] == 1
    assert results["missing_prediction_count"] == 1
    assert results["field_exact_match_counts"]["company_name"] == 1
    assert results["full_record_exact_match_count"] == 1


def test_evaluate_predictions_counts_extra_predictions_but_ignores_field_metrics():
    gold_examples = [{"id": "ex_001", "target": make_target()}]
    pred_examples = [
        {"id": "ex_001", "prediction": make_target(), "error": None},
        {"id": "ex_extra", "prediction": make_target(company_name="Extra"), "error": None},
    ]

    results = evaluate_predictions(gold_examples, pred_examples)

    assert results["extra_prediction_count"] == 1
    assert results["prediction_success_count"] == 1
    assert results["field_exact_match_counts"] == dict.fromkeys(FIELDS, 1)


def test_evaluate_predictions_counts_invalid_predictions():
    gold_examples = [{"id": "ex_001", "target": make_target()}]
    pred_examples = [
        {
            "id": "ex_001",
            "prediction": make_target(request_type="bug_report"),
            "error": None,
        }
    ]

    results = evaluate_predictions(gold_examples, pred_examples)

    assert results["prediction_success_count"] == 0
    assert results["invalid_prediction_count"] == 1
    assert results["field_exact_match_counts"] == dict.fromkeys(FIELDS, 0)


def test_build_prediction_eval_summary_contains_expected_sections():
    results = evaluate_predictions(
        [{"id": "ex_001", "target": make_target()}],
        [{"id": "ex_001", "prediction": make_target(), "error": None}],
    )

    output = build_prediction_eval_summary(results)

    assert "Prediction Eval Summary" in output
    assert "Total examples:" in output
    assert "Prediction success:" in output
    assert "Full record exact match:" in output
    assert "Field exact match:" in output
    assert "Soft action_items metrics:" in output
    assert "token_precision" in output
    assert "token_recall" in output
    assert "token_f1" in output
    assert "token_jaccard" in output
    for field in FIELDS:
        assert field in output


def test_run_eval_prediction_mode_compares_predictions(tmp_path, capsys):
    gold_path = tmp_path / "gold.jsonl"
    pred_path = tmp_path / "pred.jsonl"
    target = make_target()
    gold_path.write_text(
        json.dumps({"id": "ex_001", "input_text": "sample", "target": target}) + "\n",
        encoding="utf-8",
    )
    pred_path.write_text(
        json.dumps(
            {
                "id": "ex_001",
                "prediction": target,
                "raw_response": None,
                "error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = run_eval.main(["--gold", str(gold_path), "--pred", str(pred_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Prediction Eval Summary" in output
    assert "Total examples: 1" in output
    assert "Prediction success: 1/1 (100.00%)" in output
    assert "Errors: 0" in output
    assert "Full record exact match: 1/1 (100.00%)" in output
    assert "Field exact match:" in output


def test_run_eval_prediction_mode_reports_prediction_errors(tmp_path, capsys):
    gold_path = tmp_path / "gold.jsonl"
    pred_path = tmp_path / "pred.jsonl"
    target = make_target()
    gold_path.write_text(
        json.dumps({"id": "ex_001", "input_text": "sample", "target": target}) + "\n",
        encoding="utf-8",
    )
    pred_path.write_text(
        json.dumps(
            {
                "id": "ex_001",
                "prediction": None,
                "raw_response": None,
                "error": "ValueError: bad model output",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = run_eval.main(["--gold", str(gold_path), "--pred", str(pred_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Prediction success: 0/1 (0.00%)" in output
    assert "Errors: 1" in output
    assert "Full record exact match: 0/1 (0.00%)" in output
