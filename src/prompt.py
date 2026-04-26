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

Reference date:
- The reference date for interpreting deadlines is 2026-04-26.
- If text gives month/day without year, infer the year from the reference date.
- Example: "by May 3" -> "2026-05-03".
- Relative deadlines like "next Friday", "tomorrow morning", "this week", "after the holidays", or "next month" -> null.
- If a relative or vague deadline appears important to execution, set needs_human_review to true.

Rules:
- Return exactly one JSON object and nothing else.
- Use null for missing, unknown, ambiguous, or unsupported values.
- budget_amount must be numeric or null.
- budget_currency must be a 3-letter currency code or null.
- deadline_iso must be a date string in YYYY-MM-DD format or null.
- If a deadline is unclear, relative, vague, invalid, or missing the exact date, set deadline_iso to null.
- If text gives a month/day deadline without a year, infer the year from the reference date when unambiguous.
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
- For action_items, prefer concise phrasing close to the requester's wording when possible.

Budget rules:
- Extract budget_amount only when the budget is explicit, fixed enough, approved or usable, and currency is known.
- Set both budget_amount and budget_currency to null for ranges, conditional budgets, conflicting budgets, unapproved budgets, caps with exclusions, unknown currency, and vague limits like "under 6k" without currency.
- If budget is ambiguous or conflicting, set budget_amount=null and budget_currency=null.
- If budget ambiguity affects actionability, mention it briefly in notes and set needs_human_review=true.
- "around $2k if needed" -> budget_amount=null and budget_currency=null.
- "€8-10k range but CFO hasn't approved" -> budget_amount=null and budget_currency=null.
- "cap is 25k all-in but hardware excluded" -> budget_amount=null and budget_currency=null.
- "under 6k" with no currency -> budget_amount=null and budget_currency=null.
- "spend whatever, ops says keep below $15k" -> budget_amount=null and budget_currency=null.

Human review rules:
- Set needs_human_review=true when ambiguity or conflict affects what should be done, priced, scheduled, or extracted.
- Use true for ambiguous, conditional, or conflicting budget; vague deadline that appears important; unclear scope; unclear request_type; uncertain company/contact; or multiple possible interpretations.
- Do not set true only because budget is missing.
- Do not set true only because deadline is missing.
- Do not set true for normal actionable requests with ordinary missing fields.
- Unclear scope between MVP and full rollout -> true.
- Budget conditional or not approved -> true.
- "maybe company X" -> true.
- Normal request with no budget -> false.

Priority rules:
- Priority measures operational urgency and business impact, not merely the presence of a deadline, budget, deliverable, or scoped project.
- A normal future deadline does not imply high priority.
- Budget, a concrete deliverable, or a scoped project does not imply high priority.
- low: informational, exploratory, or explicitly non-urgent.
- medium: normal business requests, proposals, quotes, demos, reports, content work, implementation plans, or project deliverables with ordinary future deadlines and no stated operational pressure.
- high: important time-sensitive requests with clear operational or business pressure, customer-facing degradation, important broken workflow, launch pressure, executive/customer pressure, or workaround needed soon.
- urgent: emergency, production-down, blocking all users/orders/payments, same-day critical fix, immediate action with serious operational impact, or ASAP tied to a critical executive/customer deadline.
- "urgent-ish", "today if possible", or "before weekend is ok" should usually be high, not urgent.
- "ASAP" is urgent only when paired with serious operational impact; otherwise high.

Priority calibration examples:
- "Please send proposal and timeline by 2026-05-15" -> medium.
- "Prepare demo for 2026-04-28" -> medium.
- "Deliver edited photos by 2026-04-29" -> medium.
- "Quarterly analytics report draft by 2026-04-30" -> medium.
- "Need migration plan by 2026-05-10" -> medium.
- "Dashboard export button broken after last release" -> medium unless customer/business impact is stated.
- "Tenant portal slow, especially invoices, need answer before Monday ops call" -> medium unless serious operational impact is stated.
- "Urgent-ish, tomorrow morning would save us" -> high.
- "Invoice has wrong tax rate, correct today if possible" -> high.
- "Checkout returns 500 and blocks all online orders, fix immediately" -> urgent.
- "Dashboard must be live for board/customer demo next week and asks ASAP" -> urgent.

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
- Do not overuse other.

Request type boundary examples:
- procurement options / quote for equipment -> proposal_request if scoped.
- general price sheet / package pricing / rate card -> pricing_inquiry.
- audit with final report -> data_request.
- diagnose conversion drop / tracking issue -> support_issue.
- CRM cleanup estimate -> proposal_request if asking for estimate.
- CRM cleanup/reporting work -> data_request if asking to perform cleanup/report.
- maintenance retainer terms -> proposal_request.
- executing ongoing maintenance -> implementation_request.
- badge printing / conference print materials -> content_request.
- dashboard live / wireframes / implementation plan -> implementation_request if build/setup is requested.

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


def build_repair_prompt(input_text: str, raw_response: str, error_message: str) -> str:
    """Build a short prompt to repair malformed extraction output."""
    return f"""You attempted to extract structured JSON from the input text, but the output failed parsing or schema validation.

Original input:
\"\"\"
{input_text}
\"\"\"

Bad output:
\"\"\"
{raw_response}
\"\"\"

Error:
\"\"\"
{error_message}
\"\"\"

Return a corrected JSON object only.
Do not include markdown.
Do not include explanations.
Follow this schema:
{{
  "company_name": string or null,
  "contact_name": string or null,
  "request_type": one of ["demo_request", "support_issue", "pricing_inquiry", "proposal_request", "implementation_request", "data_request", "content_request", "sales_lead", "other"],
  "priority": one of ["low", "medium", "high", "urgent"],
  "budget_amount": number or null,
  "budget_currency": string or null,
  "deadline_iso": string or null,
  "action_items": list of strings,
  "notes": string or null,
  "needs_human_review": boolean
}}

Use null for missing or ambiguous values.
action_items must always be a list.
budget_currency must be a 3-letter code or null.
deadline_iso must be YYYY-MM-DD or null."""
