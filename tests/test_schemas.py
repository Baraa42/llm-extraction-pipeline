from src.schemas import ExtractionRecord, Priority, RequestType
from pydantic import ValidationError


def test_request_type_taxonomy_is_small_and_general():
    assert [item.value for item in RequestType] == [
        "demo_request",
        "support_issue",
        "pricing_inquiry",
        "proposal_request",
        "implementation_request",
        "data_request",
        "content_request",
        "sales_lead",
        "other",
    ]


def test_extraction_record_valid():
    record = ExtractionRecord(
        company_name="Acme Labs",
        contact_name="Sarah Chen",
        request_type=RequestType.demo_request,
        priority=Priority.medium,
        budget_amount=15000,
        budget_currency="USD",
        deadline_iso="2026-05-15",
        action_items=["Schedule demo", "Send available time slots"],
        notes="Ops team interested in evaluation.",
        needs_human_review=False,
    )

    assert record.company_name == "Acme Labs"
    assert record.request_type == RequestType.demo_request
    assert record.priority == Priority.medium


def test_invalid_request_type_rejected():
    try:
        ExtractionRecord(
            request_type="bug_report",
            priority=Priority.medium,
            needs_human_review=False,
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("invalid request_type should be rejected")
