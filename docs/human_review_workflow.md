# Human Review Workflow

## Overview

The extraction pipeline produces structured JSON from messy business text. Some records are clean and can be accepted automatically. Others are ambiguous, incomplete, conflicting, or failed during extraction and should be reviewed by a human.

The goal is to turn model errors and ambiguous cases into improved labels for future evaluation.

## Workflow

```text
input text
   ↓
LLM extraction
   ↓
schema validation
   ↓
prediction + reliability metadata
   ↓
human review if needed
   ↓
correction saved
   ↓
correction promoted into gold dataset
   ↓
future eval improves
```

## When to send a record to human review

Send a record to review when any of these apply:

- `needs_human_review = true`
- model output failed parsing or schema validation
- repair retry was used
- `error_type` is not null
- budget is ambiguous or conflicting
- deadline is invalid or vague but important
- request type is unclear
- company/contact identity is uncertain
- action items are incomplete or over-expanded

## What the reviewer checks

The reviewer checks every schema field:

```text
company_name
contact_name
request_type
priority
budget_amount
budget_currency
deadline_iso
action_items
notes
needs_human_review
```

The reviewer should prefer `null` over guessing.

## Correction format

Corrections are stored in:

```text
data/corrections/
```

Each correction should include:

```json
{
  "id": "review_001",
  "source_example_id": "ex_039",
  "input_text": "...",
  "prediction": {},
  "corrected_target": {},
  "reviewer_notes": "...",
  "review_status": "corrected"
}
```

## Review status values

- `accepted`: prediction is correct as-is
- `corrected`: prediction had errors and corrected target is provided
- `rejected`: input is not suitable for this schema
- `needs_more_context`: reviewer cannot determine correct output from available text

## Promotion to gold dataset

A correction can be promoted into the gold dataset when:

- `review_status = corrected` or `accepted`
- `corrected_target` validates against the schema
- the input is representative of real business text
- the correction adds useful coverage

Promotion path:

```text
data/corrections/example.json
   ↓
data/gold/gold_v2.jsonl
```

## Example review decisions

### Case 1 — Accepted

```json
{
  "review_status": "accepted",
  "reviewer_notes": "Prediction matches target."
}
```

### Case 2 — Corrected

```json
{
  "review_status": "corrected",
  "reviewer_notes": "Budget was conditional, so budget_amount and budget_currency should be null."
}
```

### Case 3 — Needs more context

```json
{
  "review_status": "needs_more_context",
  "reviewer_notes": "Company identity and deadline are ambiguous in the source text."
}
```

## Future improvements

- correction template generator
- reviewer CLI
- Streamlit review UI
- automatic promotion script
- correction audit log
