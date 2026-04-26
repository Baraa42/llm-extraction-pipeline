from src.prompt import build_extraction_prompt


def test_prompt_includes_input_text():
    input_text = "Maya from GreenLeaf Foods wants a quote."

    prompt = build_extraction_prompt(input_text)

    assert input_text in prompt


def test_prompt_includes_schema_fields():
    prompt = build_extraction_prompt("sample text")

    for field_name in [
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
    ]:
        assert field_name in prompt


def test_prompt_includes_allowed_enum_values():
    prompt = build_extraction_prompt("sample text")

    for request_type in [
        "demo_request",
        "support_issue",
        "pricing_inquiry",
        "proposal_request",
        "implementation_request",
        "data_request",
        "content_request",
        "sales_lead",
        "other",
    ]:
        assert request_type in prompt

    for priority in ["low", "medium", "high", "urgent"]:
        assert priority in prompt


def test_prompt_includes_critical_extraction_rules():
    prompt = build_extraction_prompt("sample text")

    assert "Return JSON only" in prompt
    assert "Do not hallucinate values" in prompt
    assert "deadline_iso must be a date string in YYYY-MM-DD format or null" in prompt
    assert "Extract only action_items explicitly requested or clearly implied" in prompt
    assert "Set notes to null by default" in prompt
    assert "Set needs_human_review to true only when ambiguity or conflict" in prompt


def test_prompt_clarifies_pricing_vs_proposal_request_distinction():
    prompt = build_extraction_prompt("sample")

    assert "pricing_inquiry: only for general pricing" in prompt
    assert "proposal_request: asks for a proposal, quote, estimate" in prompt
    assert "If both pricing and a scoped proposal are requested, prefer proposal_request" in prompt


def test_prompt_clarifies_deadline_alone_does_not_imply_high_priority():
    prompt = build_extraction_prompt("sample")

    assert "A deadline alone does not imply high priority" in prompt
    assert "medium: normal business requests with ordinary deadlines" in prompt
    assert "urgent: ASAP, emergency, blocking, production-down, same-day" in prompt


def test_prompt_clarifies_notes_should_not_summarize():
    prompt = build_extraction_prompt("sample")

    assert "Set notes to null by default" in prompt
    assert "Use notes only for ambiguity, conflict, missing critical context" in prompt
    assert "Do not use notes to summarize the request" in prompt
    assert "Do not duplicate company, contact, budget, deadline, priority" in prompt


def test_prompt_clarifies_action_items_should_be_specific_but_concise():
    prompt = build_extraction_prompt("sample")

    assert "Extract only action_items explicitly requested or clearly implied" in prompt
    assert "Do not invent internal implementation steps" in prompt
    assert "Prefer 1-3 action_items for normal messages" in prompt
    assert "Make action_items specific but concise" in prompt
    assert "Each action item should be an actionable task" in prompt
    assert 'Avoid overly generic action_items like "Send proposal"' in prompt
    assert '"Provide a quote for redesigning the wholesale order form"' in prompt


def test_prompt_clarifies_human_review_is_not_for_ordinary_missing_fields():
    prompt = build_extraction_prompt("sample")

    assert "Do not set needs_human_review to true just because deadline_iso is null" in prompt
    assert "Do not set needs_human_review to true just because budget is missing" in prompt
    assert "Missing budget is normal and should not automatically trigger human review" in prompt


def test_prompt_discourages_project_plan_action_items():
    prompt = build_extraction_prompt("sample")

    assert "Do not create project plans" in prompt
    assert "Do not add prep, testing, validation, documentation, scheduling" in prompt
    assert '"Document root cause and remediation in the ticket"' in prompt
    assert '"Set up and test demo environment"' in prompt
