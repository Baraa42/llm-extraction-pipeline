from pathlib import Path

from src.evaluate import build_dry_run_summary, load_gold_examples, validate_examples


GOLD_PATH = Path("data/gold/gold_v1.jsonl")


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
