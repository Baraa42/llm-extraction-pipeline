from __future__ import annotations


def build_extraction_prompt(input_text: str) -> str:
    """Build the structured extraction prompt for a single input text."""
    return f"""You are an information extraction system.
Extract structured data from the input text.
Return exactly one JSON object.
Return JSON only.
Do not include markdown.
Do not include explanations.
Do not hallucinate values. Use null when a value is missing or cannot be determined.

Schema:
{{
  "company_name": string or null,
  "contact_name": string or null,
  "request_type": one of [
    "demo_request",
    "support_issue",
    "pricing_inquiry",
    "proposal_request",
    "implementation_request",
    "data_request",
    "content_request",
    "sales_lead",
    "other"
  ],
  "priority": one of [
    "low",
    "medium",
    "high",
    "urgent"
  ],
  "budget_amount": number or null,
  "budget_currency": string or null,
  "deadline_iso": string or null,
  "action_items": list of strings,
  "notes": string or null,
  "needs_human_review": boolean
}}

Rules:
- Return exactly one JSON object and nothing else.
- Use null for missing, unknown, ambiguous, or unsupported values.
- budget_amount must be numeric or null.
- budget_currency must be a 3-letter currency code or null.
- deadline_iso must be a date string in YYYY-MM-DD format or null.
- If a deadline is unclear, relative, vague, invalid, or missing the exact date, set deadline_iso to null.
- action_items must always be a list, even when empty.
- Extract only action_items explicitly requested or clearly implied by the input text.
- Do not invent internal implementation steps.
- Do not create project plans.
- Do not add prep, testing, validation, documentation, scheduling, or follow-up tasks unless explicitly requested.
- Keep action_items concise.
- Prefer 1-3 action_items for normal messages.
- Each action item should describe the requester's desired outcome, not the assistant's internal next step.
- Do not include generic action_items like "document root cause", "validate workflow", "create checklist", "confirm attendees", unless explicitly present in the input.
- Set notes to null by default.
- Use notes only for ambiguity, conflict, missing critical context, or important context not captured by other fields.
- Do not use notes to summarize the request.
- Do not duplicate company, contact, budget, deadline, priority, or action_items in notes.
- Do not mention ordinary missing fields in notes, such as missing phone number, missing email, or no budget, unless the missing information creates ambiguity.
- ASAP or urgency alone does not require notes.
- Set needs_human_review to true only when ambiguity or conflict prevents confident extraction or the request requires clarification to act.
- Do not set needs_human_review to true just because deadline_iso is null.
- Do not set needs_human_review to true just because budget is missing.
- "ASAP" means urgent priority, not necessarily human review.
- "next Friday" is relative, so deadline_iso should be null, but needs_human_review should be true only if the exact date is critical to the request.
- Missing budget is normal and should not automatically trigger human review.
- Make action_items specific but concise.
- Each action item should be an actionable task.
- Do not include contact or company names in action_items unless needed for the task.
- Avoid overly generic action_items like "Send proposal" when the requested work can be made more specific.
- Avoid overly verbose full-sentence action_items.

Priority rules:
- A deadline alone does not imply high priority.
- urgent: ASAP, emergency, blocking, production-down, same-day, immediate action language, or critical production impact.
- high: language indicates urgency, launch pressure, blocking status, short turnaround, executive/customer pressure, or clearly time-sensitive business impact.
- medium: normal business requests with ordinary deadlines.
- low: informational or non-urgent requests.

Request type guidance:
- demo_request: asks for a demo.
- support_issue: bug, issue, outage, incident, billing problem, or something broken.
- pricing_inquiry: only for general pricing, rates, packages, cost questions, price sheets, or budget guidance.
- proposal_request: asks for a proposal, quote, estimate, RFP response, scoped project plan, timeline, or formal scope for a specific project.
- If both pricing and a scoped proposal are requested, prefer proposal_request.
- implementation_request: setup, migration, onboarding, configuration, rollout, training, renewal, or enablement work.
- data_request: reports, audit, export, analytics, dashboard, data cleanup, or review of metrics.
- content_request: website, copy, creative work, design assets, landing page, campaign, photos, or badge/content production.
- sales_lead: general interest without a clear request.
- other: fallback when no listed request_type fits.

Good action item examples:
- "Fix the booking page"
- "Call Dr. Lewis after the issue is resolved"
- "Schedule warehouse automation demo"
- "Include scanner workflow in demo"
- "Provide a quote for redesigning the wholesale order form"
- "Send a proposal and timeline"

Bad action item examples:
- "Validate end-to-end scheduling workflow after fix"
- "Document root cause and remediation in the ticket"
- "Create demo script and checklist"
- "Set up and test demo environment"
- "Confirm attendees"
- "Prepare detailed scope, deliverables, and cost breakdown"
- "Help them with their request"

Text:
\"\"\"
{input_text}
\"\"\""""
