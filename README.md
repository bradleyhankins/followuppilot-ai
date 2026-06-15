# FollowUpPilot AI

FollowUpPilot AI is a public flagship portfolio demonstration for home-service and local service businesses. It now demonstrates a lightweight follow-up operating system with two connected workflows:

- **Manager Dashboard:** visibility into open pipeline, overdue follow-up, rep workload, and leads needing attention.
- **Lead Workspace:** a rep or manager can review one managed lead, refresh the deterministic follow-up plan, record an outcome, and download a PDF plan.

The original single-lead Follow-Up Builder remains available for one-off follow-up generation.

## Live Demo

[Launch FollowUpPilot AI](https://followuppilot-ai.streamlit.app/)

## Current Version

Phase 2: Lead Workspace and Manager Dashboard.

This remains a Streamlit Community Cloud demo using fictional data and session-only persistence. It does not include authentication, billing, scheduled jobs, a production database, live email/SMS sending, or direct CRM integration.

## Design Pattern

```text
Rules decide. AI polishes. Guardrails constrain. Fallback protects.
```

The deterministic rules engine remains the source of truth for scoring, risk, lead-stage behavior, suggested follow-up dates, overdue state, next action, CRM notes, follow-up sequences, and manager attention flags. Optional AI enhancement only improves copy-center wording when an OpenAI key is configured.

## Manager Dashboard

The dashboard opens first and shows:

- active leads
- overdue follow-ups
- due-today follow-ups
- high-priority leads
- active pipeline value
- won value
- leads by stage
- pipeline value by stage
- leads by assigned rep
- overdue leads by rep
- priority distribution
- manager-attention flags
- searchable/filterable lead table
- CSV import/export tools

## Lead Workspace

The workspace supports:

- selecting a managed lead
- reviewing customer, project, estimate, stage, rep, and follow-up details
- editing appropriate lead fields
- refreshing the deterministic follow-up plan
- viewing text, email, voicemail, CRM note, call script, objection guidance, manager note, and sequence
- marking follow-up complete
- recording an outcome
- updating stage and last contact date
- recalculating the next recommendation
- downloading a PDF follow-up plan

Changes persist during the current Streamlit session only.

## CSV Format

The app provides a downloadable CSV template and accepts fictional or approved non-sensitive demo data. Import validates rows independently so one bad row does not crash the import.

Important columns include:

```text
lead_id, customer_name, company_name, customer_email, customer_phone,
service_type, lead_stage, assigned_rep, estimate_amount, context_notes,
objection, urgency, financing, tone, preferred_channel, followup_intensity,
last_contact_date
```

Exports protect against spreadsheet formula injection by prefixing risky cell values that begin with `=`, `+`, `-`, or `@`.

## Local Development

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Test and Lint

```bash
py -m pip install pytest ruff
py -m pytest -q
py -m ruff check .
py -c "import app; import core.followup_logic; import core.validation"
```

## AI Configuration

AI enhancement is optional.

Preferred:

```bash
OPENAI_API_KEY=your_api_key_here
```

Legacy compatibility:

```bash
OPENAI_TOKEN=your_api_key_here
```

If both are present, `OPENAI_API_KEY` is used.

## Privacy

This public demo is for fictional or generalized business scenarios. Do not enter real customer information, payment information, financing details, credentials, regulated data, confidential business records, or secrets.

## Future Production Path

A production implementation would require durable storage, authentication, authorization, tenant separation, audit trails, data-retention policy, CRM/email/SMS integration review, monitoring, and operational support.
