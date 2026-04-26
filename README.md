# LLM Extraction + Eval Pipeline

## Overview

This project converts messy business text into validated structured JSON using an LLM, Pydantic schema validation, reliability handling, and measurable evaluation.

It extracts fields such as company, contact, request type, priority, budget, deadline, action items, notes, and whether human review is needed.

## Why This Project Exists

The goal is to build a production-oriented LLM extraction pipeline, not just a prompt demo. The project emphasizes repeatable evaluation, schema validation, failure analysis, raw response capture, and reliability hooks that make model behavior inspectable.

## Features

- Strict extraction schema with Pydantic validation
- Prompted JSON extraction from messy business text
- Raw model response capture
- One repair retry for JSON parse or schema validation failures
- Attempts and repaired metadata for reliability tracking
- Prediction JSONL output for batch runs
- Exact field-level evaluation
- Soft token-level `action_items` evaluation
- Local FastAPI interface with `GET /health` and `POST /extract`

## Demo Examples

See [docs/demo_examples.md](docs/demo_examples.md) for representative extraction examples, including clean requests, support tickets, ambiguous call notes, API usage, and reliability behavior.

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

Evaluation separates strict structured-field metrics from softer `action_items` scoring. Exact match remains useful for fields such as dates, budgets, enums, and booleans, while token-level `action_items` metrics provide a more informative signal for naturally variable phrasing.

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
docs/             labeling policy and supporting docs
```

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
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5-mini
```

Do not commit real secrets.

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

The API requires `OPENAI_API_KEY`. It uses `OPENAI_MODEL` when set, otherwise the extractor defaults to `gpt-5-mini`.

`POST /extract` returns the validated prediction plus reliability metadata: `raw_response`, `final_raw_response`, `error`, `error_type`, `attempts`, and `repaired`.

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

## Current Baseline

- Current best prompt/baseline: `baseline_v3_1` / `reliability_v1`
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

## Reports

Selected reports live in `data/reports/`:

- `reliability_v1_report.md`
- `baseline_v2_eval.md`
- `baseline_v2_failure_review_detailed.md`
- `baseline_inspection_v1_v2.md`

## Known Limitations

- Dataset is small: 40 examples.
- `action_items` exact match is too strict for natural-language task phrasing.
- No deployment yet.
- No UI yet.
- No human-in-the-loop correction interface yet.
- No large-scale model comparison yet.
- No cost or latency tracking yet.

## Roadmap

- Expand dataset from 40 to 100+ examples.
- Add Cloud Run deployment docs.
- Deploy API to Cloud Run or a similar platform.
- Add model comparison with cost and latency tracking.
- Add human correction workflow.
- Add optional UI for reviewing extractions and errors.
