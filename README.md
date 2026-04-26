# LLM Extraction + Eval Pipeline

A production-oriented LLM extraction pipeline that converts messy business text into validated structured JSON, with schema validation, reliability handling, repeatable evaluation, a FastAPI interface, and Docker packaging.

The project is designed to be more than a prompt demo: model outputs are parsed, validated, evaluated, and made inspectable through raw response capture and failure metadata.

---

## What It Extracts

The pipeline extracts structured records from short unstructured business messages such as emails, support tickets, meeting notes, and call notes.

Target fields include:

- `company_name`
- `contact_name`
- `request_type`
- `priority`
- `budget_amount`
- `budget_currency`
- `deadline_iso`
- `action_items`
- `notes`
- `needs_human_review`

---

## Features

- Strict Pydantic extraction schema
- Prompted JSON extraction from messy business text
- Pydantic validation with forbidden extra fields
- Raw model response capture
- One repair retry for JSON parse or schema validation failures
- Attempts / repaired metadata for reliability tracking
- Prediction JSONL output for batch extraction
- Exact field-level evaluation
- Soft token-level `action_items` evaluation
- FastAPI interface with `GET /health` and `POST /extract`
- Dockerized API
- GitHub Actions test workflow

---

## Documentation

- [Demo examples](docs/demo_examples.md) — representative clean, ambiguous, and messy extraction examples
- [Project writeup](docs/project_writeup.md) — design, reliability layer, evaluation methodology, failure analysis, and roadmap
- [Human review workflow](docs/human_review_workflow.md) — correction format and promotion path into future gold datasets
- [Deployment readiness](docs/deployment.md) — local Docker usage, Cloud Run templates, secret handling, and production caveats

---

## Architecture

```text
input text
   |
   v
prompt builder
   |
   v
LLM call
   |
   v
JSON parser
   |
   v
Pydantic validation
   |
   v
repair retry if needed
   |
   v
prediction JSONL / API response
   |
   v
evaluation report
```

The model output is not trusted blindly. Each response is captured, parsed as JSON, and validated against the extraction schema. If parsing or schema validation fails, the reliability layer can make one repair attempt and preserve both the original and final raw responses.

Evaluation separates strict structured-field metrics from softer `action_items` scoring. Exact match remains useful for dates, budgets, enums, and booleans, while token-level `action_items` metrics provide a more informative signal for naturally variable task phrasing.

---

## Project Structure

```text
src/
  api.py          FastAPI app
  extractor.py    LLM call, parsing, validation, reliability layer
  prompt.py       extraction and repair prompt builders
  schemas.py      Pydantic extraction schema
  evaluate.py     gold loading, prediction loading, metrics

scripts/
  run_extract.py  single-text and dataset extraction CLI
  run_eval.py     dry-run validation and prediction evaluation CLI

data/
  gold/           labeled JSONL dataset
  reports/        selected eval and analysis reports

tests/            unit tests for schema, prompt, extractor, eval, API, CLIs
docs/             supporting documentation
```

---

## Setup

Install dependencies:

```bash
poetry install
```

Create a local environment file:

```bash
cp .env.example .env
```

Set the required variables in `.env`:

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

Do not commit real secrets.

---

## Run Extraction

Single text:

```bash
poetry run python scripts/run_extract.py \
  --text "Hi, Sarah from Acme needs help migrating Zendesk by May 15. Budget is $12k."
```

Dataset:

```bash
poetry run python scripts/run_extract.py \
  --gold data/gold/gold_v1.jsonl \
  --out data/predictions/baseline.jsonl
```

Small sample run:

```bash
poetry run python scripts/run_extract.py \
  --gold data/gold/gold_v1.jsonl \
  --out data/predictions/sample.jsonl \
  --limit 5
```

---

## Run Evaluation

Validate the gold dataset:

```bash
poetry run python scripts/run_eval.py \
  --gold data/gold/gold_v1.jsonl \
  --dry-run
```

Compare predictions against gold:

```bash
poetry run python scripts/run_eval.py \
  --gold data/gold/gold_v1.jsonl \
  --pred data/predictions/baseline.jsonl
```

---

## Run Local API

Start the FastAPI app:

```bash
poetry run uvicorn src.api:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Extraction:

```bash
curl -X POST http://127.0.0.1:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi, Sarah from Acme needs help migrating Zendesk by May 15. Budget is $12k."}'
```

`POST /extract` returns the validated prediction plus reliability metadata:

- `raw_response`
- `final_raw_response`
- `error`
- `error_type`
- `attempts`
- `repaired`

---

## Run with Docker

Build:

```bash
docker build -t llm-extraction-pipeline .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env llm-extraction-pipeline
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Your `.env` file must contain `OPENAI_API_KEY`.

---

## Current Baseline

Current best prompt / baseline:

```text
baseline_v3_1 / reliability_v1
```

Current benchmark:

- Dataset: 40 labeled examples
- Model: `gpt-5-mini`
- Prediction success: 40/40 (100.00%)
- Full record exact match: 2/40 (5.00%)

Latest reliability eval:

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

The dataset is intentionally small, so these numbers are directional rather than definitive. `action_items` exact match is intentionally strict and underestimates quality because equivalent tasks can be phrased many ways.

---

## Selected Reports

Selected reports live in `data/reports/`:

- `reliability_v1_report.md`
- `baseline_v2_eval.md`
- `baseline_v2_failure_review_detailed.md`
- `baseline_inspection_v1_v2.md`

---

## Known Limitations

- Dataset is small: 40 examples.
- `action_items` exact match is too strict for natural-language task phrasing.
- No live deployment yet.
- No UI yet.
- No human-in-the-loop correction interface yet.
- No large-scale model comparison yet.
- No cost or latency tracking yet.
- No authentication or rate limiting yet.

---

## Roadmap

- Expand dataset from 40 to 100+ examples.
- Deploy API to Cloud Run or a similar platform.
- Add model comparison with cost and latency tracking.
- Add automated human correction workflow.
- Add optional UI for reviewing extractions and errors.
- Add request logging, audit trail, authentication, and rate limiting before any public production use.

---

## Positioning

This project demonstrates a practical LLM systems workflow:

```text
schema design
→ extraction
→ validation
→ reliability handling
→ measurable evaluation
→ API serving
→ Docker packaging
→ documentation
```

The core focus is building an evaluated and inspectable extraction system, not just prompting a model.
