# Gold v2 Dataset Summary

## Overview

`gold_v2.jsonl` expands the original 40-example development dataset to 100 labeled examples.

- Total examples: 100
- Existing examples preserved from v1: 40
- New examples added: 60

## Difficulty Distribution

{'easy': 46, 'medium': 35, 'hard': 19}

## Source Type Distribution

{'email': 29, 'support_ticket': 21, 'meeting_note': 18, 'call_note': 19, 'chat_message': 8, 'crm_note': 5}

## Request Type Distribution

{'proposal_request': 19, 'support_issue': 25, 'demo_request': 4, 'implementation_request': 16, 'content_request': 12, 'pricing_inquiry': 4, 'data_request': 20}

## Priority Distribution

{'medium': 65, 'urgent': 10, 'low': 8, 'high': 17}

## Field Coverage

- Budget present: 22/100
- Deadline present: 28/100
- Needs human review: 41/100

## Added Coverage

The 60 new examples add more coverage for:

- emails
- support tickets
- meeting notes
- call notes
- Slack/chat-style messages
- CRM notes
- ambiguous budgets
- vague or invalid deadlines
- uncertain company/contact identity
- request type boundary cases
- human-review cases
- null-heavy examples

## Intended Use

Use this dataset as the stronger benchmark for the next stage:

1. run the current best `gpt-5-mini` pipeline on `gold_v2.jsonl`
2. add local inference support
3. compare local model output against the API baseline
