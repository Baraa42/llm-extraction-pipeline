# Baseline Inspection Report

## Overall Summary

| name        |   total |   has_prediction |   prediction_rate |   full_match_count |   full_match_rate |   avg_field_match_rate |
|:------------|--------:|-----------------:|------------------:|-------------------:|------------------:|-----------------------:|
| baseline_v1 |      40 |               40 |                 1 |                  0 |             0     |                 0.6975 |
| baseline_v2 |      40 |               40 |                 1 |                  1 |             0.025 |                 0.7175 |

## Field Accuracy

| field              |   baseline_v1 |   baseline_v2 |   delta_v2_minus_v1 |
|:-------------------|--------------:|--------------:|--------------------:|
| action_items       |         0     |         0.025 |               0.025 |
| notes              |         0.1   |         0.2   |               0.1   |
| needs_human_review |         0.675 |         0.65  |              -0.025 |
| request_type       |         0.775 |         0.75  |              -0.025 |
| priority           |         0.75  |         0.85  |               0.1   |
| budget_amount      |         0.875 |         0.875 |               0     |
| budget_currency    |         0.85  |         0.875 |               0.025 |
| company_name       |         0.975 |         0.975 |               0     |
| deadline_iso       |         0.975 |         0.975 |               0     |
| contact_name       |         1     |         1     |               0     |

## Notes

- Review lowest-accuracy fields first.
- Inspect most improved/regressed examples.
- Use this to decide prompt_v3 changes.

