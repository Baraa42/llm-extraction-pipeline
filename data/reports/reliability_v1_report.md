# Reliability v1 Report

## Summary

- Processed: 40
- Succeeded: 40
- Failed: 0
- Repaired: 0
- Parse errors: 0
- Schema validation errors: 0
- API errors: 0
- Other errors: 0

## Error Types Observed

- None

All rows completed successfully on the first attempt.

## Eval

```text
Prediction Eval Summary

Total examples: 40
Prediction success: 40/40 (100.00%)
Errors: 0
Invalid predictions: 0
Missing predictions: 0
Extra predictions: 0

Full record exact match: 2/40 (5.00%)

Field exact match:
  company_name: 39/40 (97.50%)
  contact_name: 40/40 (100.00%)
  request_type: 34/40 (85.00%)
  priority: 38/40 (95.00%)
  budget_amount: 39/40 (97.50%)
  budget_currency: 39/40 (97.50%)
  deadline_iso: 40/40 (100.00%)
  action_items: 2/40 (5.00%)
  notes: 20/40 (50.00%)
  needs_human_review: 34/40 (85.00%)

Soft action_items metrics:
  exact_match: 2/40 (5.00%)
  token_precision: 51.73%
  token_recall: 78.39%
  token_f1: 60.49%
  token_jaccard: 47.65%
```

## Notes

- `raw_response` is captured for each successful row.
- `final_raw_response` is captured for each successful row.
- `attempts` is `1` for each row.
- `repaired` is `false` for each row.
- Repair retry remains available for JSON parse and schema validation failures, but was not needed in this run.
- Eval compatibility is preserved: `scripts/run_eval.py` completed successfully against `data/predictions/reliability_v1.jsonl`.
