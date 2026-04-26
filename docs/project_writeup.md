# LLM Extraction Pipeline: From Prompt Demo to Evaluated System

## 1. Problem

Business teams receive messy inbound text from emails, support tickets, meeting notes, and call notes. That text often needs to become structured records for triage, routing, analytics, follow-up, or reporting.

LLMs are useful for this kind of extraction, but raw prompting alone is not enough for production-oriented use. The goal is not just to generate JSON, but to build a measurable and reliable extraction pipeline.

## 2. Design Goals

The project was designed around a few practical ML engineering goals:

- strict schema
- validated outputs
- repeatable evaluation
- reliability metadata
- failure visibility
- simple API interface
- minimal dependencies
- production-oriented structure

This project treats the model as one component inside a system, not as the whole system.

## 3. System Architecture

```text
input text
   ↓
prompt builder
   ↓
LLM call
   ↓
JSON parser
   ↓
Pydantic validation
   ↓
repair retry if needed
   ↓
prediction JSONL / API response
   ↓
evaluation report
```

The prompt builder turns raw business text into extraction instructions. The extractor calls the model, captures raw output, parses JSON, and validates the result. The schema validator enforces the contract the rest of the system depends on. The reliability layer adds raw-response capture, error taxonomy, attempts metadata, and one repair retry for parse or schema failures. The evaluator compares prediction JSONL files against a gold dataset. The FastAPI layer exposes the same extraction path through a local API.

## 4. Schema and Validation

The extraction schema contains:

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

`request_type` and `priority` use enums. Optional fields are nullable because real inbound text often omits company details, budget, deadline, or contact information. The Pydantic model uses strict validation with `extra="forbid"` so unexpected fields are rejected.

Schema validation matters because the model output is never trusted blindly. A response has to parse as JSON and pass validation before it becomes a prediction.

## 5. Reliability Layer

The reliability layer captures:

- raw model response
- final raw response
- one repair retry
- error type
- attempts count
- repaired flag

Example metadata:

```json
{
  "raw_response": "...",
  "final_raw_response": "...",
  "error": null,
  "error_type": null,
  "attempts": 1,
  "repaired": false
}
```

This makes the pipeline easier to debug. If the model produces malformed JSON or a schema-invalid result, the system can attempt one repair pass and preserve both responses. If extraction fails, the caller still receives structured failure metadata rather than an opaque exception.

## 6. Evaluation Methodology

Evaluation uses a gold JSONL dataset and prediction JSONL files. The evaluator reports:

- prediction success rate
- error count
- invalid prediction count
- missing and extra prediction counts
- full-record exact match
- field-level exact match
- soft `action_items` metrics

Exact match is appropriate for structured fields such as:

```text
budget_amount
budget_currency
deadline_iso
request_type
priority
needs_human_review
```

Exact match is too strict for `action_items`, where equivalent tasks can be phrased differently. The evaluator therefore also reports token precision, token recall, token F1, and token Jaccard for action items.

## 7. Current Results

Current best baseline:

```text
Dataset: 40 labeled examples
Model: gpt-5-mini
Prediction success: 40/40
```

Latest reliability evaluation:

```text
company_name: 39/40 (97.50%)
contact_name: 40/40 (100.00%)
request_type: 34/40 (85.00%)
priority: 38/40 (95.00%)
budget_amount: 39/40 (97.50%)
budget_currency: 39/40 (97.50%)
deadline_iso: 40/40 (100.00%)
action_items exact: 2/40 (5.00%)
notes: 20/40 (50.00%)
needs_human_review: 34/40 (85.00%)
```

Soft `action_items` metrics:

```text
token_precision: 51.73%
token_recall: 78.39%
token_f1: 60.49%
token_jaccard: 47.65%
```

The dataset is small, so the results are directional rather than definitive.

## 8. Failure Analysis

The main observed failure patterns are:

- action item wording differs from gold labels
- notes are subjective
- ambiguous company/contact names
- request type boundary cases
- priority calibration issues
- vague deadlines
- conflicting budgets

Failure analysis guided prompt and labeling improvements. Prompt v3 tightened budget, deadline, human-review, and request-type behavior. Prompt v3.1 addressed priority over-classification where normal business requests with ordinary deadlines were being marked high. Soft action-item metrics showed that exact match was too harsh for free-text task phrasing.

## 9. Human Review Loop

The human review path is documented in [human_review_workflow.md](human_review_workflow.md).

The intended loop is:

```text
prediction → review → correction → future gold dataset
```

Review statuses are:

```text
accepted
corrected
rejected
needs_more_context
```

This matters because real extraction systems improve through reviewable errors, corrections, and promotion of representative examples into future gold datasets.

## 10. API and Deployment Readiness

The project exposes a FastAPI interface:

- `GET /health`
- `POST /extract`

The API returns prediction data plus reliability metadata. The project also includes Docker packaging and deployment readiness documentation in [deployment.md](deployment.md).

Production caveats remain:

- no authentication yet
- no rate limiting yet
- no request persistence yet
- no audit trail yet

The current state is a deployment-ready foundation, not a public production API.

## 11. Key Lessons

- Schema validation is essential.
- Evaluation design matters as much as prompting.
- Exact match can be misleading for free-text fields.
- Reliability metadata makes debugging easier.
- Prompt tuning should be guided by failure analysis.
- Small datasets are enough for iteration, not final benchmark claims.

## 12. Limitations

- small dataset
- no PDF/OCR support
- no frontend/UI
- no live deployment yet
- no large model comparison yet
- no cost/latency tracking yet
- no auth/rate limiting
- no human correction automation yet

## 13. Roadmap

- Expand dataset from 40 to 100+ examples
- Add model comparison with cost and latency tracking
- Add Cloud Run deployment
- Add request logging / audit trail
- Add human correction workflow automation
- Add optional review UI
- Explore PDF/OCR ingestion later
