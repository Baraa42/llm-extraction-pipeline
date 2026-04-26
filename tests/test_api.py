from fastapi.testclient import TestClient

from src import api
from src.extractor import ExtractionResult
from src.schemas import ExtractionRecord


client = TestClient(api.app)


def make_record() -> ExtractionRecord:
    return ExtractionRecord(
        company_name="Acme",
        contact_name="Sarah",
        request_type="implementation_request",
        priority="medium",
        budget_amount=12000,
        budget_currency="USD",
        deadline_iso="2026-05-15",
        action_items=["Migrate Zendesk"],
        notes=None,
        needs_human_review=False,
    )


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_endpoint_success(monkeypatch):
    result = ExtractionResult(
        record=make_record(),
        raw_response='{"company_name":"Acme"}',
        final_raw_response='{"company_name":"Acme"}',
        error=None,
        error_type=None,
        attempts=1,
        repaired=False,
    )
    monkeypatch.setattr(api, "extract_record_result", lambda text: result)

    response = client.post("/extract", json={"text": "Sarah from Acme needs Zendesk migration."})

    assert response.status_code == 200
    body = response.json()
    assert body["prediction"]["company_name"] == "Acme"
    assert body["prediction"]["request_type"] == "implementation_request"
    assert body["raw_response"] == '{"company_name":"Acme"}'
    assert body["final_raw_response"] == '{"company_name":"Acme"}'
    assert body["error"] is None
    assert body["error_type"] is None
    assert body["attempts"] == 1
    assert body["repaired"] is False


def test_extract_endpoint_extraction_failure_returns_200(monkeypatch):
    result = ExtractionResult(
        record=None,
        raw_response="bad output",
        final_raw_response="still bad",
        error="ValidationError: invalid request_type",
        error_type="schema_validation_error",
        attempts=2,
        repaired=False,
    )
    monkeypatch.setattr(api, "extract_record_result", lambda text: result)

    response = client.post("/extract", json={"text": "Sarah from Acme needs Zendesk migration."})

    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] is None
    assert body["raw_response"] == "bad output"
    assert body["final_raw_response"] == "still bad"
    assert body["error"] == "ValidationError: invalid request_type"
    assert body["error_type"] == "schema_validation_error"
    assert body["attempts"] == 2
    assert body["repaired"] is False


def test_extract_endpoint_missing_text_validation():
    response = client.post("/extract", json={})

    assert response.status_code == 422


def test_extract_endpoint_empty_text_validation():
    response = client.post("/extract", json={"text": "   "})

    assert response.status_code == 422
