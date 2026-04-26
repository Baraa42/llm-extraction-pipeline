## Current Baseline Status

- Dataset: 40 labeled examples in `data/gold/gold_v1.jsonl`
- Model: `gpt-5-mini`
- Current best prompt: `baseline_v3_1`
- Prediction success: 40/40
- Strong fields:
  - budget amount / currency
  - deadline extraction
  - company/contact extraction
  - priority after v3.1 calibration
  - human-review flag
- Known limitation:
  - `action_items` exact match is too strict and underestimates quality
- Next step:
  - add soft scoring for `action_items` in eval

## Local API

Run the FastAPI app locally:

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

`POST /extract` returns the validated prediction plus reliability metadata:
`raw_response`, `final_raw_response`, `error`, `error_type`, `attempts`, and `repaired`.
