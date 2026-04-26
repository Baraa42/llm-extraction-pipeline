# Baseline v2 / v3 / v3.1 Comparison

## Overall Summary

| name          |   total |   prediction_success |   prediction_success_rate |   full_match_count |   full_match_rate |   avg_field_match_rate |   error_count |
|:--------------|--------:|---------------------:|--------------------------:|-------------------:|------------------:|-----------------------:|--------------:|
| baseline_v2   |      40 |                   40 |                         1 |                  2 |             0.05  |                 0.765  |             0 |
| baseline_v3   |      40 |                   40 |                         1 |                  1 |             0.025 |                 0.795  |             0 |
| baseline_v3_1 |      40 |                   40 |                         1 |                  1 |             0.025 |                 0.8025 |             0 |

## Field Accuracy Comparison

| field              |   baseline_v2 |   baseline_v3 |   baseline_v3_1 |   delta_v3_minus_v2 |   delta_v3_1_minus_v3 |   delta_v3_1_minus_v2 |
|:-------------------|--------------:|--------------:|----------------:|--------------------:|----------------------:|----------------------:|
| company_name       |         1     |         0.975 |           0.95  |              -0.025 |                -0.025 |                -0.05  |
| contact_name       |         1     |         1     |           0.975 |               0     |                -0.025 |                -0.025 |
| request_type       |         0.825 |         0.9   |           0.85  |               0.075 |                -0.05  |                 0.025 |
| priority           |         0.825 |         0.625 |           0.85  |              -0.2   |                 0.225 |                 0.025 |
| budget_amount      |         0.875 |         1     |           1     |               0.125 |                 0     |                 0.125 |
| budget_currency    |         0.875 |         1     |           1     |               0.125 |                 0     |                 0.125 |
| deadline_iso       |         0.975 |         1     |           0.975 |               0.025 |                -0.025 |                 0     |
| action_items       |         0.05  |         0.025 |           0.025 |              -0.025 |                 0     |                -0.025 |
| notes              |         0.5   |         0.5   |           0.5   |               0     |                 0     |                 0     |
| needs_human_review |         0.725 |         0.925 |           0.9   |               0.2   |                -0.025 |                 0.175 |

## Soft Action Items Metrics

| name          |   action_items_exact_match_rate |   action_token_precision |   action_token_recall |   action_token_f1 |   action_token_jaccard |
|:--------------|--------------------------------:|-------------------------:|----------------------:|------------------:|-----------------------:|
| baseline_v2   |                           0.05  |                 0.46339  |              0.776199 |          0.55999  |               0.430527 |
| baseline_v3   |                           0.025 |                 0.482809 |              0.802436 |          0.583946 |               0.445223 |
| baseline_v3_1 |                           0.025 |                 0.48524  |              0.793689 |          0.578354 |               0.442477 |


## Conclusion

`baseline_v3_1` is selected as the current best prompt.

Reason:
- It recovers priority accuracy after the v3 regression.
- It preserves the main v3 gains on budget extraction, currency extraction, deadline handling, and human-review behavior.
- `action_items` exact match remains very low, but manual inspection shows many predictions are semantically acceptable, so exact match is not the right metric for that field.


## Next Step

Implement soft action-item metrics inside `src/evaluate.py`.

Recommended metrics:
- `action_items_exact_match`
- `action_items_token_precision`
- `action_items_token_recall`
- `action_items_token_f1`
- `action_items_token_jaccard`

Do not continue prompt tuning until action-item eval is more meaningful.
