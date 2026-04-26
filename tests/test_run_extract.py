import json

import pytest

from scripts import run_extract
from src.schemas import ExtractionRecord


def make_record(company_name="Acme"):
    return ExtractionRecord(
        company_name=company_name,
        contact_name="Sarah",
        request_type="implementation_request",
        priority="medium",
        budget_amount=12000,
        budget_currency="USD",
        deadline_iso="2026-05-15",
        action_items=["Migrate Zendesk setup"],
        notes=None,
        needs_human_review=False,
    )


def test_single_text_mode_prints_pretty_json(monkeypatch, capsys):
    monkeypatch.setattr(run_extract, "extract_record", lambda input_text: make_record())

    exit_code = run_extract.main(["--text", "Sarah from Acme needs Zendesk migration."])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["company_name"] == "Acme"
    assert output["action_items"] == ["Migrate Zendesk setup"]


def test_dataset_mode_writes_jsonl(monkeypatch, tmp_path, capsys):
    gold_path = tmp_path / "gold.jsonl"
    out_path = tmp_path / "predictions" / "baseline.jsonl"
    gold_path.write_text(
        "\n".join(
            [
                json.dumps({"id": "ex_001", "input_text": "First"}),
                json.dumps({"id": "ex_002", "input_text": "Second"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        run_extract,
        "extract_record",
        lambda input_text: make_record(company_name=input_text),
    )

    exit_code = run_extract.main(["--gold", str(gold_path), "--out", str(out_path)])

    assert exit_code == 0
    lines = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2
    assert lines[0]["id"] == "ex_001"
    assert lines[0]["prediction"]["company_name"] == "First"
    assert lines[0]["raw_response"] is None
    assert lines[0]["error"] is None
    assert lines[1]["id"] == "ex_002"
    assert lines[1]["prediction"] is not None
    assert lines[1]["prediction"]["company_name"] == "Second"
    assert lines[1]["error"] is None
    assert "Processed: 2" in capsys.readouterr().out


def test_dataset_mode_writes_error_without_crashing(monkeypatch, tmp_path):
    gold_path = tmp_path / "gold.jsonl"
    out_path = tmp_path / "predictions" / "baseline.jsonl"
    gold_path.write_text(
        "\n".join(
            [
                json.dumps({"id": "ex_001", "input_text": "Good output"}),
                json.dumps({"id": "ex_002", "input_text": "Bad output"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    def fail_extract(input_text):
        if input_text == "Bad output":
            raise ValueError("bad model output")
        return make_record(company_name=input_text)

    monkeypatch.setattr(run_extract, "extract_record", fail_extract)

    exit_code = run_extract.main(["--gold", str(gold_path), "--out", str(out_path)])

    assert exit_code == 0
    lines = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2
    assert lines[0]["id"] == "ex_001"
    assert lines[0]["prediction"]["company_name"] == "Good output"
    assert lines[0]["error"] is None
    assert lines[1]["id"] == "ex_002"
    assert lines[1]["prediction"] is None
    assert lines[1]["raw_response"] is None
    assert lines[1]["error"] == "ValueError: bad model output"


def test_dataset_mode_limit_processes_first_n(monkeypatch, tmp_path):
    gold_path = tmp_path / "gold.jsonl"
    out_path = tmp_path / "predictions" / "baseline.jsonl"
    gold_path.write_text(
        "\n".join(
            [
                json.dumps({"id": "ex_001", "input_text": "First"}),
                json.dumps({"id": "ex_002", "input_text": "Second"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(run_extract, "extract_record", lambda input_text: make_record())

    exit_code = run_extract.main(
        ["--gold", str(gold_path), "--out", str(out_path), "--limit", "1"]
    )

    assert exit_code == 0
    lines = out_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["id"] == "ex_001"


def test_gold_without_out_fails_argument_parsing(capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_extract.main(["--gold", "data/gold/gold_v1.jsonl"])

    assert exc_info.value.code == 2
    assert "--out is required when --gold is provided" in capsys.readouterr().err
