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
