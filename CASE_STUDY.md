# FollowUpPilot AI Case Study

## Problem

Small home-service and local-service businesses often lose revenue after a lead or estimate because follow-up is inconsistent.

Common failure points:

- managers cannot quickly see which leads are overdue or high risk
- reps have to remember what to send, when to send it, and what to record
- CRM notes are often too thin for a manager to understand deal status
- Won and Closed Lost leads can be treated like normal active-sales leads
- AI-only workflows can produce persuasive copy without enough business guardrails

The result is a messy follow-up process where good leads quietly go cold.

## Solution

FollowUpPilot AI demonstrates a lightweight follow-up operating system:

```text
Manager sees overdue risk -> opens lead -> rep gets next action/copy -> outcome is recorded.
```

The product connects two experiences:

- **Manager Dashboard:** pipeline visibility, overdue work, due-today follow-up, rep workload, high-priority leads, manager attention flags, and CSV tools.
- **Lead Workspace:** selected-lead review, deterministic follow-up recommendation, customer-ready copy, CRM note, call script, sequence, PDF download, and outcome recording.

The demo is public-safe and uses fictional data only. It intentionally avoids production-only features such as authentication, billing, durable database storage, scheduled jobs, real CRM integrations, and live email/SMS sending.

## Product Loop

1. A manager opens the dashboard and sees follow-up risk.
2. The manager filters or searches the lead table.
3. The manager opens a selected lead in the Lead Workspace.
4. The rep reviews customer context, estimate details, lead stage, last contact date, and preferred channel.
5. FollowUpPilot produces:
   - next best action
   - priority
   - deal risk
   - follow-up status
   - suggested follow-up date
   - email draft
   - text-message draft
   - voicemail
   - CRM note
   - manager coaching note
   - call script
   - follow-up sequence
6. The rep records the outcome and note.
7. The app updates last action, last-contact date, lead stage where appropriate, and the next deterministic recommendation.

This loop gives managers visibility and gives reps a practical execution path without pretending the public demo is a full CRM.

## Responsible AI And Rules-First Approach

FollowUpPilot uses a rules-first architecture:

```text
Rules decide. AI polishes. Guardrails constrain. Fallback protects.
```

The deterministic engine owns business behavior:

- lead-stage rules
- Closed Lost and Won behavior
- overdue status
- due-today/upcoming status
- suggested follow-up date
- priority and deal risk
- next action
- manager attention flags
- report/PDF source data

Optional AI enhancement is limited to copy polish. It does not decide lead priority, risk, status, stage, dates, or business outcomes.

If no OpenAI key is configured, the app still works through deterministic fallback. This makes the demo reliable in public portfolio settings and safer for environments where AI services are unavailable.

## Screenshots

| View | Screenshot |
| --- | --- |
| Manager Dashboard | [docs/assets/screenshots/01-manager-dashboard.png](docs/assets/screenshots/01-manager-dashboard.png) |
| Lead Workspace Active Lead | [docs/assets/screenshots/02-lead-workspace-active.png](docs/assets/screenshots/02-lead-workspace-active.png) |
| Won Lead Handling | [docs/assets/screenshots/03-lead-workspace-won.png](docs/assets/screenshots/03-lead-workspace-won.png) |
| Closed Lost Handling | [docs/assets/screenshots/04-lead-workspace-closed-lost.png](docs/assets/screenshots/04-lead-workspace-closed-lost.png) |
| Follow-Up Builder | [docs/assets/screenshots/05-followup-builder.png](docs/assets/screenshots/05-followup-builder.png) |
| Mobile View | [docs/assets/screenshots/06-mobile-view.png](docs/assets/screenshots/06-mobile-view.png) |

## Tech Stack

- Python
- Streamlit
- Pandas
- deterministic domain logic in typed Python models
- optional OpenAI enhancement
- ReportLab/PDF helper utilities
- CSV import/export
- Pytest
- Ruff
- GitHub Actions
- Streamlit Community Cloud

## Production Verification Notes

The live app has been verified at:

https://followuppilot-ai.streamlit.app/

Verified production workflows:

- app startup on Streamlit Community Cloud
- Manager Dashboard default view
- sidebar navigation across all four top-level views
- dashboard metrics, manager flags, charts, search, filters, and sorting
- dashboard lead open flow into Lead Workspace
- active lead -> Won lead -> Closed Lost lead -> active lead switching
- Won status showing no active sales follow-up
- Closed Lost behavior avoiding aggressive active-sales follow-up
- PDF download
- CSV template download
- CSV export
- Follow-Up Builder deterministic generation
- desktop, tablet, and mobile smoke checks
- graceful behavior without requiring OpenAI

Known non-blocker:

- Browser console may show nonfatal Streamlit/Vega-Lite chart warnings. These do not block the product workflow.

## Current Limitations

FollowUpPilot AI is a portfolio demo, not a production CRM.

It does not include:

- authentication
- billing
- production database
- tenant separation
- scheduled reminders
- live email or SMS sending
- direct CRM integrations
- audit logs
- data-retention controls
- real customer data storage

These omissions are intentional so the public demo remains lightweight, inspectable, and safe to use with fictional data.

## Future Production Path

A production implementation would require:

- durable database storage
- authenticated users and role-based permissions
- team/tenant separation
- audit trail and compliance review
- monitored scheduled follow-up reminders
- CRM/email/SMS integration design
- delivery and consent safeguards for messaging
- operational monitoring
- data-retention and deletion policy

The current demo is best understood as a working product prototype and portfolio case study that demonstrates the product loop and engineering direction without overbuilding infrastructure.
