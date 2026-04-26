# Demo Examples

## Overview

These examples show the kinds of messy business text the pipeline is designed to handle and the structured JSON shape it produces. The examples are illustrative: exact `action_items` wording may vary, but the schema and reliability metadata remain stable.

## Example 1 — Clean implementation request

Input:

```text
Hi, Sarah from Acme needs help migrating Zendesk by May 15. Budget is $12k.
```

Example output shape:

```json
{
  "company_name": "Acme",
  "contact_name": "Sarah",
  "request_type": "implementation_request",
  "priority": "medium",
  "budget_amount": 12000,
  "budget_currency": "USD",
  "deadline_iso": "2026-05-15",
  "action_items": ["Migrate Zendesk"],
  "notes": null,
  "needs_human_review": false
}
```

Why:

- Company and contact are explicit.
- Budget is explicit and has a known currency.
- Deadline is clear and normal, so priority is `medium`.
- No ambiguity requires human review.

## Example 2 — Support ticket with operational urgency

Input:

```text
Support ticket: FloraMart checkout returns 500 error. Contact: Nina. This is blocking all online orders, fix immediately.
```

Example output shape:

```json
{
  "company_name": "FloraMart",
  "contact_name": "Nina",
  "request_type": "support_issue",
  "priority": "urgent",
  "budget_amount": null,
  "budget_currency": null,
  "deadline_iso": null,
  "action_items": ["Fix checkout 500 error"],
  "notes": null,
  "needs_human_review": false
}
```

Why:

- The checkout is broken, so this is a `support_issue`.
- Blocking all online orders plus immediate action language makes it `urgent`.
- Missing budget is normal for support tickets and does not require human review.

## Example 3 — Ambiguous budget and scope

Input:

```text
Meeting note: Frida at Oak & Stone Furniture wants inventory forecasting. No confirmed scope yet. She asked us to send two options: cheap MVP and full rollout.
```

Example output shape:

```json
{
  "company_name": "Oak & Stone Furniture",
  "contact_name": "Frida",
  "request_type": "proposal_request",
  "priority": "medium",
  "budget_amount": null,
  "budget_currency": null,
  "deadline_iso": null,
  "action_items": ["Send cheap MVP option", "Send full rollout option"],
  "notes": "Scope is not confirmed.",
  "needs_human_review": true
}
```

Why:

- Asking for MVP and full-rollout options is a scoped proposal request.
- Scope is not confirmed, so notes capture the ambiguity.
- Human review is useful because execution depends on clarifying scope.

## Example 4 — Messy call note with uncertain entities

Input:

```text
Call scribble: Blue Harbor? maybe Blue Harbour Capital. Contact sounded like 'Anne' or 'Anna'. Wants compliance archive search fixed. Said by Friday, but no timezone/date. Budget 'not more than fifty' maybe $50k? confirm.
```

Example output shape:

```json
{
  "company_name": null,
  "contact_name": null,
  "request_type": "support_issue",
  "priority": "high",
  "budget_amount": null,
  "budget_currency": null,
  "deadline_iso": null,
  "action_items": ["Fix compliance archive search"],
  "notes": "Company, contact, budget, and deadline are ambiguous.",
  "needs_human_review": true
}
```

Why:

- Company and contact are uncertain, so both are `null`.
- Budget is ambiguous and not usable.
- "Friday" has no exact date or timezone, so `deadline_iso` is `null`.
- Human review is needed before acting confidently.

## Example 5 — Local API usage

Run the API:

```bash
poetry run uvicorn src.api:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Extraction request:

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi, Sarah from Acme needs help migrating Zendesk by May 15. Budget is $12k."}'
```

Response shape:

```json
{
  "prediction": {
    "company_name": "Acme",
    "contact_name": "Sarah",
    "request_type": "implementation_request",
    "priority": "medium",
    "budget_amount": 12000,
    "budget_currency": "USD",
    "deadline_iso": "2026-05-15",
    "action_items": ["Migrate Zendesk"],
    "notes": null,
    "needs_human_review": false
  },
  "raw_response": "...",
  "final_raw_response": "...",
  "error": null,
  "error_type": null,
  "attempts": 1,
  "repaired": false
}
```

## Reliability behavior

The system captures raw model responses, parses them as JSON, and validates them against the Pydantic schema. If JSON parsing or schema validation fails, the pipeline can attempt one repair pass. Failures are returned with structured error metadata so clients can inspect what happened.

Successful repair response shape:

```json
{
  "prediction": {
    "...": "..."
  },
  "raw_response": "invalid first response",
  "final_raw_response": "corrected JSON response",
  "error": null,
  "error_type": null,
  "attempts": 2,
  "repaired": true
}
```

Failure response shape:

```json
{
  "prediction": null,
  "raw_response": "invalid first response",
  "final_raw_response": "invalid repaired response",
  "error": "ValidationError: ...",
  "error_type": "schema_validation_error",
  "attempts": 2,
  "repaired": false
}
```

## Notes

- Examples are illustrative.
- Exact `action_items` wording may vary.
- The evaluator includes both strict exact match and softer token-overlap metrics for `action_items`.
- The goal is a production-oriented extraction pipeline, not just a prompt demo.
