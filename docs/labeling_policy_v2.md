# Labeling Policy v2

Gold labels should represent what a careful human annotator would extract from
the input text. Do not infer values that are not explicitly present or clearly
supported. Prefer `null` over guessing.

Reference date for this dataset: `2026-04-26`.

## company_name

Extract the company only when it is explicitly named and reasonably certain.
If the company is uncertain, hypothetical, or phrased as "maybe X", set
`company_name` to `null`.

Mention company uncertainty in `notes` only when useful for acting on the
request.

## contact_name

Extract a contact only when a person name is explicitly present and likely to be
the contact. If missing or uncertain, use `null`.

## request_type

Use only these values:

- `demo_request`: asks for a demo.
- `support_issue`: bug, outage, incident, billing problem, or something broken.
- `pricing_inquiry`: asks for general pricing, packages, rate cards, or cost
  guidance without scoped project work.
- `proposal_request`: asks for a proposal, quote, estimate, RFP response,
  scope, timeline, or cost estimate for a specific project.
- `implementation_request`: setup, migration, onboarding, configuration,
  rollout, training, renewal, or enablement.
- `data_request`: reports, audit, export, analytics, dashboard, data cleanup,
  or metrics review.
- `content_request`: website, copy, creative work, design assets, landing page,
  campaign, badge/print/content production.
- `sales_lead`: general interest without a specific action request.
- `other`: only when no listed type fits.

If both pricing and scoped proposal/quote/estimate are requested, prefer
`proposal_request`. Do not overuse `other`.

## priority

- `urgent`: ASAP, emergency, production-down, blocking, same-day, immediate
  action, or critical incident.
- `high`: launch pressure, short turnaround, customer/executive pressure, or
  clearly time-sensitive business impact.
- `medium`: normal business request with ordinary deadline.
- `low`: informational or non-urgent request.

A deadline alone does not imply `high`.

## budget_amount / budget_currency

Extract budget only when it is explicit, fixed enough, and usable.

Set both fields to `null` when budget is vague, a range, conditional,
conflicting, not approved, "if needed", "could stretch", or has unknown
currency.

If budget is ambiguous or conflicting, explain briefly in `notes`.

## deadline_iso

Use `YYYY-MM-DD`.

If an exact date with year is given, normalize to ISO. If month/day is given
without year, infer the year from the reference date when unambiguous. For
example, "by May 3" becomes `2026-05-03`.

If a deadline is relative or vague, use `null`. Examples include "next Friday",
"this week", and "sometime next month". If the vague deadline is critical or
creates ambiguity, set `needs_human_review=true`.

## action_items

Extract the requester's desired outcomes only.

Keep action items specific, concise, directly supported by text, and usually
1-3 items. Do not invent internal project-management steps.

Bad examples unless explicitly requested:

- `Create project plan`
- `Validate workflow`
- `Document root cause`
- `Prepare detailed scope`
- `Confirm attendees`

Good examples:

- `Fix the booking page`
- `Provide a quote for redesigning the wholesale order form`
- `Migrate Zendesk setup`
- `Review Q1 usage data`

Do not over-optimize phrasing for exact match. Labels should be human-readable
and stable.

## notes

Set `notes` to `null` by default.

Use `notes` only for ambiguity, conflict, missing critical context, uncertain
company/contact, ambiguous or conflicting budget, invalid/vague deadline when
important, or unclear scope.

Do not use notes to summarize the request, say "no budget provided", say
"no deadline provided", duplicate fields already captured elsewhere, or restate
simple context.

Examples that should become `null`:

- `No budget discussed.`
- `No deadline provided.`
- `Issue started after last release.`
- `Migration from old spreadsheets.`

Examples that should stay:

- `Budget is conditional and not approved.`
- `Deadline is vague and may be critical.`
- `Customer identity is uncertain.`
- `Scope is unclear between MVP and full rollout.`

## needs_human_review

Set `needs_human_review=true` only when ambiguity or conflict prevents confident
extraction or clarification is needed to act.

Use `true` for conflicting budget, invalid/vague critical deadline, unclear
company/contact, unclear scope, multiple materially different interpretations,
or requests that cannot be acted on without clarification.

Do not set `true` just because budget, deadline, or contact is missing, or
because a deadline is vague but not critical. Normal actionable requests should
not require human review.
