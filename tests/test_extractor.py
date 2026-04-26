import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src import extractor
from src.extractor import extract_record, parse_model_json
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


class FakeResponses:
    def __init__(self, output_text):
        self.output_text = output_text
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class FakeOpenAI:
    responses = None

    def __init__(self, api_key):
        self.api_key = api_key
        self.responses = self.__class__.responses


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
    fake_responses = FakeResponses(json.dumps(VALID_MODEL_JSON))
    FakeOpenAI.responses = fake_responses
    monkeypatch.setattr(extractor, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    record = extract_record("Sarah from Acme Labs wants a demo.")

    assert isinstance(record, ExtractionRecord)
    assert record.company_name == "Acme Labs"
    assert record.request_type == "demo_request"
    assert fake_responses.calls[0]["model"] == "test-model"
    assert fake_responses.calls[0]["temperature"] == 0
    assert "Sarah from Acme Labs wants a demo." in fake_responses.calls[0]["input"]


def test_extract_record_schema_validation_errors_are_raised(monkeypatch):
    invalid_payload = {**VALID_MODEL_JSON, "request_type": "bug_report"}
    FakeOpenAI.responses = FakeResponses(json.dumps(invalid_payload))
    monkeypatch.setattr(extractor, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    with pytest.raises(ValidationError):
        extract_record("Acme has a bug.")


def test_extract_record_missing_api_key_raises_value_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setattr(extractor, "OpenAI", FakeOpenAI)

    with pytest.raises(ValueError, match="OPENAI_API_KEY not set"):
        extract_record("Sarah from Acme Labs wants a demo.")


def test_extract_record_defaults_model_when_not_set(monkeypatch):
    fake_responses = FakeResponses(json.dumps(VALID_MODEL_JSON))
    FakeOpenAI.responses = fake_responses
    monkeypatch.setattr(extractor, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    extract_record("Sarah from Acme Labs wants a demo.")

    assert fake_responses.calls[0]["model"] == "gpt-5-mini"
    assert "temperature" not in fake_responses.calls[0]


def test_extract_record_omits_temperature_for_gpt_5_models(monkeypatch):
    fake_responses = FakeResponses(json.dumps(VALID_MODEL_JSON))
    FakeOpenAI.responses = fake_responses
    monkeypatch.setattr(extractor, "OpenAI", FakeOpenAI)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")

    extract_record("Sarah from Acme Labs wants a demo.")

    assert "temperature" not in fake_responses.calls[0]
