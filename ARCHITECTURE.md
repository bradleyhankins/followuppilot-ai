# Architecture

FollowUpPilot AI is a Streamlit-based public demonstration of a follow-up operating system for home-service and local service businesses.

## Current Layers

```text
Streamlit UI
- Manager Dashboard
- Lead Workspace
- Follow-Up Builder
- About This Demo

Domain models
- LeadInput
- FollowupPlan
- GeneratedCopy
- LeadRecord

Rules engine
- scoring
- risk
- suggested follow-up date
- overdue/due-today/upcoming state
- stage behavior
- copy generation
- follow-up sequence

Lead workspace services
- session-state store
- demo data seed
- CSV import/export
- filters and sorting
- outcome handling
- follow-up completion

Dashboard services
- summary metrics
- manager attention flags
- chart-ready aggregations

Optional AI
- prompt building
- JSON-first parsing
- deterministic fallback
```

## Data Flow

1. Demo leads are loaded from `data/demo_leads.py` into Streamlit session state.
2. Each `LeadRecord` reuses `LeadInput` for deterministic planning.
3. `run_followup_workflow` calculates the follow-up plan.
4. The dashboard aggregates refreshed lead records.
5. The workspace edits a lead, records an outcome, and recalculates the next recommendation.
6. CSV import/export uses row-level validation and does not persist uploaded files.

## Persistence

Phase 2 uses Streamlit session-state persistence only. This keeps the public demo simple while isolating store operations in `core/lead_store.py` so SQLite or PostgreSQL can replace the session store later.

## Non-Goals

No authentication, production database, scheduled jobs, billing, live email/SMS sending, or direct CRM integration is included in this phase.
