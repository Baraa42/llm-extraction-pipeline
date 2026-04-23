# Project Spec

## Problem
Build a production-oriented extraction pipeline that converts short unstructured business text into validated structured JSON.

## Target user
Small ops / sales / support teams that receive messy inbound text and want structured records for triage and follow-up.

## V1 input
Single plain-text input per record.

Included:
- emails
- support tickets
- meeting notes
- call summaries
- CRM lead notes

Excluded:
- OCR
- PDFs
- attachments
- scanned docs

## V1 output
Structured JSON with:
- company_name
- contact_name
- request_type
- priority
- budget_amount
- budget_currency
- deadline_iso
- action_items
- notes
- needs_human_review

## Success metrics
Primary:
- schema_validity_rate
- exact_match_rate_by_field
- normalized_match_rate_by_field
- full_record_match_rate
- human_review_rate

Secondary:
- average_latency_ms

## Human review policy
Set needs_human_review=true when:
- key values are ambiguous
- multiple valid interpretations exist
- budget or deadline is unclear
- request type is unclear
- important fields seem present but cannot be extracted confidently

## Non-goals for v1
- OCR
- PDF ingestion
- vector DB
- multi-provider orchestration
- advanced frontend
- cloud infra

## Deliverables for Day 1
- repo scaffold
- final schema
- success metrics
- initial tests