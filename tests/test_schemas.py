from src.schemas import ExtractionRecord, Priority, RequestType


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