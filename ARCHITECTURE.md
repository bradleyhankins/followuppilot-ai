# Architecture

FollowUpPilot AI is a Streamlit-based public demonstration of a sales follow-up workflow assistant for home-service and local service businesses.

The near-term interface is Streamlit. The core logic is intentionally modular so the deterministic workflow can later move into a private multi-user application.

## Layers

```text
Streamlit UI
- form inputs
- validation messages
- recommendation and copy-center rendering
- PDF download

Domain models and validation
- LeadInput
- GeneratedCopy
- FollowupPlan
- user-friendly validation messages

Rules engine
- priority scoring
- lead temperature
- deal risk
- lead-stage behavior
- suggested follow-up date
- overdue/due-today/upcoming status
- channel-specific next action
- deterministic fallback copy

Optional AI enhancement
- prompt construction
- JSON-first response parsing
- safe diagnostic handling
- deterministic fallback when unavailable

Reporting
- report text builder
- PDF generation
```

## Data Flow

1. A user loads a sample scenario or enters lead details in Streamlit.
2. `core.models.LeadInput` normalizes current and legacy field names.
3. `core.validation.validate_lead_input` returns user-friendly messages before generation.
4. `core.followup_logic.run_followup_workflow` creates the deterministic follow-up plan.
5. `ai_helpers.enhance_text` optionally improves copy-center text if `OPENAI_API_KEY` or `OPENAI_TOKEN` is configured.
6. The app renders escaped outputs and offers a PDF export.

## Preserved Design Choices

- Rules-first deterministic behavior
- Optional AI copy polish
- Graceful no-AI fallback
- Public-safe fictional sample data
- Copy-center workflow
- PDF export
- Privacy-forward positioning

## Current Non-Goals

This phase does not add a production database, authentication, billing, scheduled jobs, direct CRM integration, or a private manager dashboard.

## Future Direction

The next practical architecture step is a persisted lead-list layer that can power manager visibility into open and overdue follow-up without changing the scoring and copy-generation core.
