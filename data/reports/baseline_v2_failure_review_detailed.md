# Baseline v2 Detailed Failure Review

## Overall Summary

- Total examples: 40
- Prediction success: 40/40 (100.00%)
- Full record exact match: 2/40 (5.00%)
- Average field match rate: 76.50%
- Error count: 0

## Field Accuracy

| field              |   correct |   total |   accuracy_pct |
|:-------------------|----------:|--------:|---------------:|
| action_items       |         2 |      40 |            5   |
| notes              |        20 |      40 |           50   |
| needs_human_review |        29 |      40 |           72.5 |
| request_type       |        33 |      40 |           82.5 |
| priority           |        33 |      40 |           82.5 |
| budget_amount      |        35 |      40 |           87.5 |
| budget_currency    |        35 |      40 |           87.5 |
| deadline_iso       |        39 |      40 |           97.5 |
| company_name       |        40 |      40 |          100   |
| contact_name       |        40 |      40 |          100   |

## Mismatch Counts

| field              |   mismatch_count |
|:-------------------|-----------------:|
| action_items       |               38 |
| notes              |               20 |
| needs_human_review |               11 |
| request_type       |                7 |
| priority           |                7 |
| budget_amount      |                5 |
| budget_currency    |                5 |
| deadline_iso       |                1 |

## Compact Failure List

- `ex_002`: `action_items` mismatch
- `ex_003`: `action_items` mismatch
- `ex_004`: `action_items` mismatch
- `ex_004`: `notes` mismatch
- `ex_005`: `action_items` mismatch
- `ex_006`: `action_items` mismatch
- `ex_008`: `action_items` mismatch
- `ex_009`: `action_items` mismatch
- `ex_010`: `request_type` gold=`implementation_request` pred=`proposal_request`
- `ex_010`: `action_items` mismatch
- `ex_011`: `priority` gold=`medium` pred=`high`
- `ex_011`: `action_items` mismatch
- `ex_012`: `action_items` mismatch
- `ex_013`: `action_items` mismatch
- `ex_014`: `action_items` mismatch
- `ex_015`: `action_items` mismatch
- `ex_016`: `action_items` mismatch
- `ex_017`: `request_type` gold=`data_request` pred=`proposal_request`
- `ex_017`: `action_items` mismatch
- `ex_018`: `action_items` mismatch
- `ex_019`: `action_items` mismatch
- `ex_020`: `action_items` mismatch
- `ex_021`: `request_type` gold=`data_request` pred=`support_issue`
- `ex_021`: `budget_amount` gold=`None` pred=`2000.0`
- `ex_021`: `budget_currency` gold=`None` pred=`USD`
- `ex_021`: `action_items` mismatch
- `ex_021`: `notes` mismatch
- `ex_021`: `needs_human_review` gold=`True` pred=`False`
- `ex_022`: `priority` gold=`medium` pred=`high`
- `ex_022`: `action_items` mismatch
- `ex_022`: `notes` mismatch
- `ex_022`: `needs_human_review` gold=`True` pred=`False`
- `ex_023`: `budget_currency` gold=`None` pred=`EUR`
- `ex_023`: `action_items` mismatch
- `ex_023`: `notes` mismatch
- `ex_023`: `needs_human_review` gold=`True` pred=`False`
- `ex_024`: `request_type` gold=`proposal_request` pred=`data_request`
- `ex_024`: `action_items` mismatch
- `ex_025`: `priority` gold=`medium` pred=`high`
- `ex_025`: `deadline_iso` gold=`2026-05-03` pred=`None`
- `ex_025`: `action_items` mismatch
- `ex_025`: `notes` mismatch
- `ex_025`: `needs_human_review` gold=`False` pred=`True`
- `ex_026`: `priority` gold=`high` pred=`urgent`
- `ex_026`: `action_items` mismatch
- `ex_026`: `notes` mismatch
- `ex_026`: `needs_human_review` gold=`True` pred=`False`
- `ex_027`: `action_items` mismatch
- `ex_027`: `notes` mismatch
- `ex_027`: `needs_human_review` gold=`True` pred=`False`
- `ex_028`: `action_items` mismatch
- `ex_028`: `notes` mismatch
- `ex_028`: `needs_human_review` gold=`True` pred=`False`
- `ex_029`: `action_items` mismatch
- `ex_029`: `notes` mismatch
- `ex_030`: `priority` gold=`high` pred=`urgent`
- `ex_030`: `action_items` mismatch
- `ex_030`: `notes` mismatch
- `ex_030`: `needs_human_review` gold=`True` pred=`False`
- `ex_031`: `action_items` mismatch
- `ex_031`: `notes` mismatch
- `ex_032`: `request_type` gold=`implementation_request` pred=`proposal_request`
- `ex_032`: `action_items` mismatch
- `ex_032`: `notes` mismatch
- `ex_032`: `needs_human_review` gold=`True` pred=`False`
- `ex_033`: `request_type` gold=`data_request` pred=`implementation_request`
- `ex_033`: `budget_amount` gold=`None` pred=`25000.0`
- `ex_033`: `action_items` mismatch
- `ex_033`: `notes` mismatch
- `ex_034`: `action_items` mismatch
- `ex_034`: `notes` mismatch
- `ex_035`: `priority` gold=`high` pred=`medium`
- `ex_035`: `budget_amount` gold=`None` pred=`9500.0`
- `ex_035`: `budget_currency` gold=`None` pred=`USD`
- `ex_035`: `action_items` mismatch
- `ex_035`: `notes` mismatch
- `ex_036`: `action_items` mismatch
- `ex_036`: `notes` mismatch
- `ex_036`: `needs_human_review` gold=`True` pred=`False`
- `ex_037`: `budget_currency` gold=`None` pred=`AED`


## Field: `action_items`

Total mismatches: 38

### Sample mismatches

| id     | difficulty   | source_type    | gold                                                                       | pred                                                                                                                                                                             | input_text                                                                                                                                                              |
|:-------|:-------------|:---------------|:---------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_002 | easy         | support_ticket | ['Fix booking page', 'Call Dr. Lewis after issue is resolved']             | ['Fix the booking page so patients can schedule', 'Call Dr. Lewis after the issue is resolved']                                                                                  | Support ticket: Acme Dental - Dr. Lewis says the booking page is down and patients can't schedule. ASAP fix needed. Call him after resolved.                            |
| ex_003 | easy         | meeting_note   | ['Schedule warehouse automation demo', 'Include scanner workflow in demo'] | ['Prepare a warehouse automation demo for 2026-04-28', 'Include scanner workflow in the demo']                                                                                   | Meeting note: Omar at BrightPath Logistics asked us to prepare a warehouse automation demo for next Tuesday, 2026-04-28. No budget discussed. Include scanner workflow. |
| ex_004 | easy         | call_note      | ['Prepare monthly SEO package proposal']                                   | ['Prepare a proposal for a monthly SEO package.', 'Start the proposal process and deliver a draft by 2026-05-01 ensuring the package does not exceed EUR 2,000 per month.']      | Call with Priya / Northstar Hotels: wants monthly SEO package, max budget EUR 2,000 per month. Start proposal by Friday 2026-05-01.                                     |
| ex_005 | easy         | email          | ['Renew maintenance contract for another year', 'Prepare paperwork']       | ['Renew maintenance contract for one year', 'Prepare and deliver renewal paperwork by 2026-06-30', 'Ensure renewal/PO does not exceed $18,000']                                  | Email from James at Rivet Manufacturing: please renew our maintenance contract for another year. PO limit is $18,000. Need paperwork by 2026-06-30.                     |
| ex_006 | medium       | support_ticket | ['Investigate app login errors', 'Update status page']                     | ['Investigate login errors affecting members', 'Update the status page with incident findings and current status']                                                               | Ticket: UrbanFit Gym app login errors for members. Contact: Elena. Please investigate and update status page. Not urgent but should be handled this week.               |
| ex_008 | easy         | meeting_note   | ['Prepare HIPAA training slides', 'Prepare attendance sheet']              | ['Schedule HIPAA training session for new staff on 2026-05-08', 'Provide HIPAA training slides', 'Provide attendance sheet for the training']                                    | Meeting notes - ClearWave Clinic. Sarah wants a HIPAA training session for new staff on 2026-05-08. No price mentioned. Need slides and attendance sheet.               |
| ex_009 | easy         | call_note      | ['Edit product photos for spring catalog']                                 | ['Edit product photos for the spring catalog', 'Deliver the edited photos by 2026-04-29']                                                                                        | Call note: Ben from Atlas Coffee Roasters needs product photos edited for the spring catalog. Budget $900. Deliver by 2026-04-29.                                       |
| ex_010 | easy         | email          | ['Configure 30 laptops', 'Send procurement options']                       | ['Send procurement options and quotes for 30 configured laptops within the USD 24,000 budget', 'Confirm configuration and delivery schedule to ensure completion by 2026-08-15'] | Email: Hi team, Lisa here from Beacon School. We need 30 laptops configured before 2026-08-15. Approved budget is USD 24,000. Please send procurement options.          |
| ex_011 | easy         | support_ticket | ['Patch dashboard export button', 'Confirm when deployed']                 | ['Patch the dashboard export button', 'Confirm to Malik when the patch is deployed']                                                                                             | Ticket from Malik at Harbor Insurance: dashboard export button broken after last release. Please patch and confirm when deployed.                                       |
| ex_012 | easy         | meeting_note   | ['Prepare foot-traffic analytics pilot', 'Schedule kickoff']               | ['Kick off a pilot of foot-traffic analytics on 2026-05-05', 'Run the pilot within a £12,000 budget']                                                                            | Meeting note: Nova Retail wants a pilot of foot-traffic analytics. Contact is Irene. Pilot budget: £12k. Kickoff target 2026-05-05.                                     |
| ex_013 | easy         | email          | ['Provide security review scope', 'Provide cost estimate']                 | ['Provide scope and cost estimate for a security review of the vendor portal']                                                                                                   | Email from Tom, BluePeak Energy: need security review for vendor portal. Deadline 2026-05-31. Please provide scope and cost estimate.                                   |
| ex_014 | easy         | support_ticket | ['Fix checkout 500 error']                                                 | ['Fix the checkout 500 error and restore online ordering immediately']                                                                                                           | Support ticket: FloraMart checkout returns 500 error. Contact: Nina. This is blocking all online orders, fix immediately.                                               |
| ex_015 | easy         | call_note      | ['Prepare CRM migration plan']                                             | ['Provide a CRM migration plan by 2026-05-10', 'Migrate CRM data from old spreadsheets']                                                                                         | Call with Diego at Summit Builders: wants CRM migration from old spreadsheets. Budget 15,000 USD. Need migration plan by 2026-05-10.                                    |
| ex_016 | easy         | email          | ['Send pricing sheet for 500 barcode scanners']                            | ['Provide a pricing sheet for 500 barcode scanners']                                                                                                                             | Email: Karen from MedSupply Direct asked for a pricing sheet for 500 barcode scanners. No deadline, just send when ready.                                               |
| ex_017 | easy         | meeting_note   | ['Audit fraud alert workflow', 'Prepare final report']                     | ['Conduct a fraud alert workflow audit', 'Deliver final audit report by 2026-07-01 within a $30,000 budget cap']                                                                 | Meeting note - Contact: Victor, Company: Eastline Bank. Request: fraud alert workflow audit. Budget cap is $30k. Final report due 2026-07-01.                           |

## Field: `notes`

Total mismatches: 20

### Sample mismatches

| id     | difficulty   | source_type    | gold                                                                                                    | pred                                                                                                                                                                              | input_text                                                                                                                                                                                                                                                    |
|:-------|:-------------|:---------------|:--------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_004 | easy         | call_note      | Budget is per month.                                                                                    |                                                                                                                                                                                   | Call with Priya / Northstar Hotels: wants monthly SEO package, max budget EUR 2,000 per month. Start proposal by Friday 2026-05-01.                                                                                                                           |
| ex_021 | medium       | email          | Budget is approximate and conditional if needed; issue may be copy or tracking.                         |                                                                                                                                                                                   | hey it's Nora from LoopPay. Can you guys look at the onboarding emails? conversions fell last week. Not sure if this is copy or tracking. We can spend around $2k if needed, but first just diagnose.                                                         |
| ex_022 | medium       | support_ticket | Deadline is vague because the date of the Monday ops call is not provided.                              |                                                                                                                                                                                   | Support: From Teo @ Bricklane Properties. The tenant portal is slow again, especially invoices. Please check DB and CDN. Need answer before our Monday ops call.                                                                                              |
| ex_023 | medium       | meeting_note   | Budget range of €8-10k was mentioned but not approved.                                                  |                                                                                                                                                                                   | Meeting notes: Zoya / Meridian Travel. They want a chatbot for refund questions. Mentioned maybe €8-10k range but CFO hasn't approved. Need sample flow and risks list.                                                                                       |
| ex_025 | medium       | email          |                                                                                                         | Confirm the exact year for the requested delivery date.                                                                                                                           | Email: Hi, Sofia here from Petal Beauty. We need influencer campaign reporting cleaned up. Our intern made a mess of the sheet. Can you turn around something by May 3? Budget $1.2k.                                                                         |
| ex_026 | medium       | support_ticket | Deadline phrase 'tomorrow morning' is relative and may be critical.                                     |                                                                                                                                                                                   | Ticket - Crown Labs. Contact unknown. Their API key rotation broke the nightly import. They wrote 'urgent-ish, tomorrow morning would save us'. Need fix or workaround.                                                                                       |
| ex_027 | medium       | meeting_note   | Scope is not confirmed.                                                                                 | Scope is not confirmed yet; requester explicitly asked for two options (cheap MVP and full rollout).                                                                              | Meeting note: Frida at Oak & Stone Furniture wants inventory forecasting. No confirmed scope yet. She asked us to send two options: cheap MVP and full rollout.                                                                                               |
| ex_028 | medium       | email          | Deadline 'after the holidays' is vague.                                                                 |                                                                                                                                                                                   | Email from Kai, Solace Therapy: need help moving patient intake forms to Typeform. Budget is CAD 3,500. Wants it 'done after the holidays' but did not give date.                                                                                             |
| ex_029 | medium       | call_note      | Landing page review is conditional if obvious issues are found.                                         |                                                                                                                                                                                   | Call note: Liam from Redline Auto. Asked for paid ads audit, maybe landing page too if we see obvious issues. Budget not discussed. Send quick findings deck.                                                                                                 |
| ex_030 | medium       | support_ticket | Deadline 'today if possible' is relative and may be time-sensitive.                                     |                                                                                                                                                                                   | Support ticket: Vale Foods says invoice #4432 has wrong tax rate. Contact: Marta. Please correct it today if possible and email revised PDF.                                                                                                                  |
| ex_031 | medium       | meeting_note   | Budget applies to first phase only.                                                                     |                                                                                                                                                                                   | Meeting notes: QuantumEd wants course recommendation engine. Raj said first phase can be $20k, later more. We need technical approach and data requirements by 2026-05-12.                                                                                    |
| ex_032 | medium       | email          | Budget is described only as a reasonable monthly retainer with no amount.                               |                                                                                                                                                                                   | Email: from Mina at Glasshouse Studio. Their old vendor disappeared, site updates stuck. Need someone to take over maintenance. She asked for 'reasonable monthly retainer', no number.                                                                       |
| ex_033 | hard         | meeting_note   | Deadline is vague. Demo type is unclear. Budget cap excludes hardware but exact treatment is ambiguous. | Ambiguity in the message: unsure whether the deadline is for a board demo or a customer demo, and hardware exclusion was mentioned which may affect scope and the stated 25k cap. | msg pasted from sales: 'Daniel / Apex Robotics says the dashboard needs to be live for board demo next wk, or maybe the customer demo? not sure. He said cap is 25k all-in but then mentioned hardware excluded. Need wireframes + implementation plan asap.' |
| ex_034 | hard         | call_note      | Company name, contact name, budget, currency, and Friday deadline are ambiguous.                        | Multiple key details (company identity, contact name, budget amount/currency, and exact deadline) are ambiguous and require confirmation.                                         | Call scribble: Blue Harbor? maybe Blue Harbour Capital. Contact sounded like 'Anne' or 'Anna'. Wants compliance archive search fixed. Said by Friday, but no timezone/date. Budget 'not more than fifty' maybe $50k? confirm.                                 |
| ex_035 | hard         | email          | Budget conflicts with prior $12k quote. Deadline 'first week of June' is vague.                         | Ambiguity whether the finance-approved amount includes a penetration test; clarify inclusion before finalizing scope and reply.                                                   | Email chain summary: We told Horizon Biotech $12k for the audit, but Emma replied 'finance approved 9,500 max unless this includes pen test too'. Also says launch is 'first week of June'. Need decide scope + reply.                                        |

## Field: `needs_human_review`

Total mismatches: 11

### Sample mismatches

| id     | difficulty   | source_type    | gold   | pred   | input_text                                                                                                                                                                                                      |
|:-------|:-------------|:---------------|:-------|:-------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_021 | medium       | email          | True   | False  | hey it's Nora from LoopPay. Can you guys look at the onboarding emails? conversions fell last week. Not sure if this is copy or tracking. We can spend around $2k if needed, but first just diagnose.           |
| ex_022 | medium       | support_ticket | True   | False  | Support: From Teo @ Bricklane Properties. The tenant portal is slow again, especially invoices. Please check DB and CDN. Need answer before our Monday ops call.                                                |
| ex_023 | medium       | meeting_note   | True   | False  | Meeting notes: Zoya / Meridian Travel. They want a chatbot for refund questions. Mentioned maybe €8-10k range but CFO hasn't approved. Need sample flow and risks list.                                         |
| ex_025 | medium       | email          | False  | True   | Email: Hi, Sofia here from Petal Beauty. We need influencer campaign reporting cleaned up. Our intern made a mess of the sheet. Can you turn around something by May 3? Budget $1.2k.                           |
| ex_026 | medium       | support_ticket | True   | False  | Ticket - Crown Labs. Contact unknown. Their API key rotation broke the nightly import. They wrote 'urgent-ish, tomorrow morning would save us'. Need fix or workaround.                                         |
| ex_027 | medium       | meeting_note   | True   | False  | Meeting note: Frida at Oak & Stone Furniture wants inventory forecasting. No confirmed scope yet. She asked us to send two options: cheap MVP and full rollout.                                                 |
| ex_028 | medium       | email          | True   | False  | Email from Kai, Solace Therapy: need help moving patient intake forms to Typeform. Budget is CAD 3,500. Wants it 'done after the holidays' but did not give date.                                               |
| ex_030 | medium       | support_ticket | True   | False  | Support ticket: Vale Foods says invoice #4432 has wrong tax rate. Contact: Marta. Please correct it today if possible and email revised PDF.                                                                    |
| ex_032 | medium       | email          | True   | False  | Email: from Mina at Glasshouse Studio. Their old vendor disappeared, site updates stuck. Need someone to take over maintenance. She asked for 'reasonable monthly retainer', no number.                         |
| ex_036 | hard         | support_ticket | True   | False  | Ticket: 'Everything broken since migration' - customer: Alpine Market. No named contact. Details mention POS sync, loyalty points, and receipts. They wrote ASAP but also 'before weekend is ok'.               |
| ex_037 | hard         | meeting_note   | True   | False  | Meeting note messy: GigaFleet wants route optimization or maybe just reporting first. Carla says pilot could be 30-40k AED, procurement asked for USD equivalent. Need send phased proposal 'next month maybe'. |

## Field: `request_type`

Total mismatches: 7

### Sample mismatches

| id     | difficulty   | source_type   | gold                   | pred                   | input_text                                                                                                                                                                                                                                                    |
|:-------|:-------------|:--------------|:-----------------------|:-----------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_010 | easy         | email         | implementation_request | proposal_request       | Email: Hi team, Lisa here from Beacon School. We need 30 laptops configured before 2026-08-15. Approved budget is USD 24,000. Please send procurement options.                                                                                                |
| ex_017 | easy         | meeting_note  | data_request           | proposal_request       | Meeting note - Contact: Victor, Company: Eastline Bank. Request: fraud alert workflow audit. Budget cap is $30k. Final report due 2026-07-01.                                                                                                                 |
| ex_021 | medium       | email         | data_request           | support_issue          | hey it's Nora from LoopPay. Can you guys look at the onboarding emails? conversions fell last week. Not sure if this is copy or tracking. We can spend around $2k if needed, but first just diagnose.                                                         |
| ex_024 | medium       | call_note     | proposal_request       | data_request           | Call: Alex from Stonebridge Capital asked whether we can clean their CRM duplicates. He said 'ideally before month end' but no hard date. No budget, wants estimate.                                                                                          |
| ex_032 | medium       | email         | implementation_request | proposal_request       | Email: from Mina at Glasshouse Studio. Their old vendor disappeared, site updates stuck. Need someone to take over maintenance. She asked for 'reasonable monthly retainer', no number.                                                                       |
| ex_033 | hard         | meeting_note  | data_request           | implementation_request | msg pasted from sales: 'Daniel / Apex Robotics says the dashboard needs to be live for board demo next wk, or maybe the customer demo? not sure. He said cap is 25k all-in but then mentioned hardware excluded. Need wireframes + implementation plan asap.' |
| ex_038 | hard         | call_note     | content_request        | implementation_request | Call note: Yusuf from Pearl Events. He wants emergency badge printing for conference, 800 badges, asks if we can do under 6k. Currency not said. Event opens tomorrow morning.                                                                                |

## Field: `priority`

Total mismatches: 7

### Sample mismatches

| id     | difficulty   | source_type    | gold   | pred   | input_text                                                                                                                                                                                                                                     |
|:-------|:-------------|:---------------|:-------|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_011 | easy         | support_ticket | medium | high   | Ticket from Malik at Harbor Insurance: dashboard export button broken after last release. Please patch and confirm when deployed.                                                                                                              |
| ex_022 | medium       | support_ticket | medium | high   | Support: From Teo @ Bricklane Properties. The tenant portal is slow again, especially invoices. Please check DB and CDN. Need answer before our Monday ops call.                                                                               |
| ex_025 | medium       | email          | medium | high   | Email: Hi, Sofia here from Petal Beauty. We need influencer campaign reporting cleaned up. Our intern made a mess of the sheet. Can you turn around something by May 3? Budget $1.2k.                                                          |
| ex_026 | medium       | support_ticket | high   | urgent | Ticket - Crown Labs. Contact unknown. Their API key rotation broke the nightly import. They wrote 'urgent-ish, tomorrow morning would save us'. Need fix or workaround.                                                                        |
| ex_030 | medium       | support_ticket | high   | urgent | Support ticket: Vale Foods says invoice #4432 has wrong tax rate. Contact: Marta. Please correct it today if possible and email revised PDF.                                                                                                   |
| ex_035 | hard         | email          | high   | medium | Email chain summary: We told Horizon Biotech $12k for the audit, but Emma replied 'finance approved 9,500 max unless this includes pen test too'. Also says launch is 'first week of June'. Need decide scope + reply.                         |
| ex_040 | hard         | call_note      | high   | medium | Support note from sales call: customer maybe 'OrbitCare' healthcare group. Person was Neil. Wants data export for auditors, says due 04/31/2026, which seems wrong. Budget was 'included in support plan?' unsure. Pull records + verify date. |

## Field: `budget_amount`

Total mismatches: 5

### Sample mismatches

| id     | difficulty   | source_type   | gold   |   pred | input_text                                                                                                                                                                                                                                                    |
|:-------|:-------------|:--------------|:-------|-------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_021 | medium       | email         |        |   2000 | hey it's Nora from LoopPay. Can you guys look at the onboarding emails? conversions fell last week. Not sure if this is copy or tracking. We can spend around $2k if needed, but first just diagnose.                                                         |
| ex_033 | hard         | meeting_note  |        |  25000 | msg pasted from sales: 'Daniel / Apex Robotics says the dashboard needs to be live for board demo next wk, or maybe the customer demo? not sure. He said cap is 25k all-in but then mentioned hardware excluded. Need wireframes + implementation plan asap.' |
| ex_035 | hard         | email         |        |   9500 | Email chain summary: We told Horizon Biotech $12k for the audit, but Emma replied 'finance approved 9,500 max unless this includes pen test too'. Also says launch is 'first week of June'. Need decide scope + reply.                                        |
| ex_038 | hard         | call_note     |        |   6000 | Call note: Yusuf from Pearl Events. He wants emergency badge printing for conference, 800 badges, asks if we can do under 6k. Currency not said. Event opens tomorrow morning.                                                                                |
| ex_039 | hard         | email         |        |  15000 | Email: 'Hi it's Chris from Vantage Solar. We need the installer app rebuilt, or at least patched. The CEO said spend whatever, ops says keep below $15k. Need something usable before the Texas rollout.'                                                     |

## Field: `budget_currency`

Total mismatches: 5

### Sample mismatches

| id     | difficulty   | source_type   | gold   | pred   | input_text                                                                                                                                                                                                             |
|:-------|:-------------|:--------------|:-------|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_021 | medium       | email         |        | USD    | hey it's Nora from LoopPay. Can you guys look at the onboarding emails? conversions fell last week. Not sure if this is copy or tracking. We can spend around $2k if needed, but first just diagnose.                  |
| ex_023 | medium       | meeting_note  |        | EUR    | Meeting notes: Zoya / Meridian Travel. They want a chatbot for refund questions. Mentioned maybe €8-10k range but CFO hasn't approved. Need sample flow and risks list.                                                |
| ex_035 | hard         | email         |        | USD    | Email chain summary: We told Horizon Biotech $12k for the audit, but Emma replied 'finance approved 9,500 max unless this includes pen test too'. Also says launch is 'first week of June'. Need decide scope + reply. |
| ex_037 | hard         | meeting_note  |        | AED    | Meeting note messy: GigaFleet wants route optimization or maybe just reporting first. Carla says pilot could be 30-40k AED, procurement asked for USD equivalent. Need send phased proposal 'next month maybe'.        |
| ex_039 | hard         | email         |        | USD    | Email: 'Hi it's Chris from Vantage Solar. We need the installer app rebuilt, or at least patched. The CEO said spend whatever, ops says keep below $15k. Need something usable before the Texas rollout.'              |

## Field: `deadline_iso`

Total mismatches: 1

### Sample mismatches

| id     | difficulty   | source_type   | gold       | pred   | input_text                                                                                                                                                                            |
|:-------|:-------------|:--------------|:-----------|:-------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ex_025 | medium       | email         | 2026-05-03 |        | Email: Hi, Sofia here from Petal Beauty. We need influencer campaign reporting cleaned up. Our intern made a mess of the sheet. Can you turn around something by May 3? Budget $1.2k. |


## Questions for Review

For each high-mismatch field, classify issues as:

- `gold_issue`
- `prompt_issue`
- `eval_too_strict`
- `real_model_error`

Main likely questions:
1. Are `action_items` mostly semantically correct but exact-match too strict?
2. Are `notes` gold labels too verbose / inconsistent with null-by-default policy?
3. Are `needs_human_review` gold labels too aggressive?
4. Are `request_type` mismatches due to ambiguous taxonomy or model error?
5. Does the prompt need reference-date handling for month/day deadlines?
