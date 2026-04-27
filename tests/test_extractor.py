import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src import extractor
from src.extractor import extract_record, extract_record_result, parse_model_json
from src.schemas import ExtractionRecord


VALID_MODEL_JSON = {
    "company_name": "Acme Labs",
    "contact_name": "Sarah Chen",
    "request_type": "demo_request",
    "priority": "medium",
    "budget_amount": 15000,
    "budget_currency": "USD",
    "deadline_iso": "2026-05-15",
    "action_items": ["Schedule demo"],
    "notes": None,
    "needs_human_review": False,
}


class FakeLLM:
    def __init__(self, output_text):
        self.output_text = output_text
        self.calls = []

    def __call__(self, prompt):
        self.calls.append(prompt)
        if isinstance(self.output_text, list):
            return self.output_text.pop(0)
        return self.output_text


@pytest.mark.parametrize(
    "raw_text",
    [
        json.dumps(VALID_MODEL_JSON),
        f"```json\n{json.dumps(VALID_MODEL_JSON)}\n```",
        f"Here is the extraction:\n{json.dumps(VALID_MODEL_JSON)}\nDone.",
    ],
)
def test_parse_model_json_parses_valid_json(raw_text):
    assert parse_model_json(raw_text) == VALID_MODEL_JSON


def test_parse_model_json_invalid_json_raises_error():
    with pytest.raises(json.JSONDecodeError):
        parse_model_json("not json {broken")


def test_extract_record_returns_validated_extraction_record(monkeypatch):
    fake_llm = FakeLLM(json.dumps(VALID_MODEL_JSON))
    monkeypatch.setattr(extractor, "call_llm", fake_llm)

    record = extract_record("Sarah from Acme Labs wants a demo.")

    assert isinstance(record, ExtractionRecord)
    assert record.company_name == "Acme Labs"
    assert record.request_type == "demo_request"
    assert "Sarah from Acme Labs wants a demo." in fake_llm.calls[0]


def test_extract_record_result_schema_validation_errors_are_returned(monkeypatch):
    invalid_payload = {**VALID_MODEL_JSON, "request_type": "bug_report"}
    fake_llm = FakeLLM(json.dumps(invalid_payload))
    monkeypatch.setattr(extractor, "call_llm", fake_llm)

    result = extract_record_result("Acme has a bug.", max_attempts=1)

    assert result.record is None
    assert result.error_type == "schema_validation_error"
    assert result.attempts == 1


def test_extract_record_missing_api_key_raises_value_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setattr(
        extractor,
        "call_llm",
        lambda prompt: (_ for _ in ()).throw(
            extractor.LLMConfigError("OPENAI_API_KEY not set", "missing_openai_api_key")
        ),
    )

    with pytest.raises(ValueError, match="OPENAI_API_KEY not set"):
        extract_record("Sarah from Acme Labs wants a demo.")


def test_extract_record_result_successful_first_attempt(monkeypatch):
    raw_response = json.dumps(VALID_MODEL_JSON)
    fake_llm = FakeLLM(raw_response)
    monkeypatch.setattr(extractor, "call_llm", fake_llm)

    result = extract_record_result("Sarah from Acme Labs wants a demo.")

    assert result.record is not None
    assert result.record.company_name == "Acme Labs"
    assert result.attempts == 1
    assert result.repaired is False
    assert result.raw_response == raw_response
    assert result.final_raw_response == raw_response
    assert result.error is None
    assert result.error_type is None


def test_extract_record_result_parse_failure_then_repair_success(monkeypatch):
    bad_response = "not json {broken"
    repaired_response = json.dumps(VALID_MODEL_JSON)
    fake_llm = FakeLLM([bad_response, repaired_response])
    monkeypatch.setattr(extractor, "call_llm", fake_llm)

    result = extract_record_result("Sarah from Acme Labs wants a demo.")

    assert result.record is not None
    assert result.attempts == 2
    assert result.repaired is True
    assert result.raw_response == bad_response
    assert result.final_raw_response == repaired_response
    assert result.error is None
    assert result.error_type is None
    assert "Bad output" in fake_llm.calls[1]


def test_extract_record_result_schema_failure_then_repair_success(monkeypatch):
    invalid_payload = {**VALID_MODEL_JSON, "request_type": "bug_report"}
    bad_response = json.dumps(invalid_payload)
    repaired_response = json.dumps(VALID_MODEL_JSON)
    fake_llm = FakeLLM([bad_response, repaired_response])
    monkeypatch.setattr(extractor, "call_llm", fake_llm)

    result = extract_record_result("Sarah from Acme Labs wants a demo.")

    assert result.record is not None
    assert result.attempts == 2
    assert result.repaired is True
    assert result.raw_response == bad_response
    assert result.final_raw_response == repaired_response
    assert result.error is None
    assert result.error_type is None


def test_extract_record_result_both_attempts_fail(monkeypatch):
    fake_llm = FakeLLM(["not json {broken", "still not json {broken"])
    monkeypatch.setattr(extractor, "call_llm", fake_llm)

    result = extract_record_result("Sarah from Acme Labs wants a demo.")

    assert result.record is None
    assert result.attempts == 2
    assert result.repaired is False
    assert result.error is not None
    assert result.error_type in {"json_parse_error", "schema_validation_error"}


def test_extract_record_result_missing_api_key_does_not_retry(monkeypatch):
    calls = []

    def fail_config(prompt):
        calls.append(prompt)
        raise extractor.LLMConfigError("OPENAI_API_KEY not set", "missing_openai_api_key")

    monkeypatch.setattr(extractor, "call_llm", fail_config)

    result = extract_record_result("Sarah from Acme Labs wants a demo.")

    assert result.record is None
    assert result.error_type == "missing_openai_api_key"
    assert result.attempts == 0
    assert len(calls) == 1
