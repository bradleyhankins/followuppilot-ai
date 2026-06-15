# FollowUpPilot AI

FollowUpPilot AI is a public flagship portfolio demonstration for home-service and local service businesses. It helps a rep or manager turn lead context into a practical follow-up plan: customer-ready email and text drafts, voicemail copy, a CRM-ready note, a recommended next action, suggested follow-up timing, overdue status, and a downloadable PDF plan.

## Live Demo

[Launch FollowUpPilot AI](https://followuppilot-ai.streamlit.app/)

## Current Version

Phase 1 foundation upgrade.

The app is still a Streamlit demonstration, but the core workflow is organized so it can later move toward a private multi-user product without rewriting the business logic.

## Design Pattern

```text
Rules decide. AI polishes. Guardrails constrain. Fallback protects.
```

The deterministic rules engine remains the source of truth for scoring, lead stage behavior, follow-up date suggestions, overdue status, next action, CRM note structure, call workflow, and follow-up sequence. The optional AI layer only improves copy-center wording when an OpenAI key is configured.

If AI is unavailable or fails, the app continues with rules-based outputs.

## What the App Does

Users can load a sample scenario or enter lead information such as:

- customer and business name
- optional customer email and phone
- service type
- lead stage
- last interaction notes
- objection or concern
- urgency
- financing status
- tone
- last contact date
- assigned rep
- estimate amount
- preferred channel
- follow-up intensity

The app produces:

- follow-up priority and score
- lead temperature
- deal risk and main risk
- suggested follow-up date
- overdue, due-today, or upcoming status
- recommended next action
- text-message draft
- email subject and body
- voicemail script
- CRM-ready note
- manager coaching note
- call script
- objection guidance
- follow-up sequence
- downloadable PDF follow-up plan

## Current Architecture

```text
followuppilot-ai/
├── app.py
├── ai_helpers.py
├── pdf_helpers.py
├── requirements.txt
├── pyproject.toml
├── core/
│   ├── models.py
│   ├── validation.py
│   ├── followup_logic.py
│   ├── prompts.py
│   └── report_builder.py
├── data/
│   └── sample_data.py
└── tests/
    ├── test_ai_helpers.py
    ├── test_followup_logic.py
    ├── test_reports.py
    ├── test_sample_data.py
    └── test_validation.py
```

## Module Responsibilities

- `app.py` handles the Streamlit interface, form inputs, rendering, validation display, and orchestration.
- `core/models.py` defines typed `LeadInput`, `GeneratedCopy`, and `FollowupPlan` dataclasses.
- `core/validation.py` returns user-friendly validation messages for incomplete or invalid lead inputs.
- `core/followup_logic.py` contains deterministic scoring, lead-stage behavior, follow-up date logic, overdue status, next-action logic, and generated fallback copy.
- `core/prompts.py` builds AI copy prompts and parses JSON-first AI responses with heading-format fallback.
- `ai_helpers.py` manages OpenAI access, prompt trimming, cache keys, safe diagnostics, and deterministic fallback.
- `core/report_builder.py` builds report text for export.
- `pdf_helpers.py` converts report text into a PDF with defensive escaping and error handling.
- `data/sample_data.py` stores public-safe fictional demo scenarios and dropdown options.

## Privacy and Responsible Use

This public demo is designed for fictional, sample, or generalized business scenarios. Do not enter sensitive, confidential, regulated, or unnecessary customer information.

When AI enhancement is enabled, selected inputs may be sent to the configured AI provider for copy improvement. The app does not intentionally store submitted data, but public demos should still be treated as non-confidential environments.

## AI Configuration

AI enhancement is optional.

Preferred secret name:

```bash
OPENAI_API_KEY=your_api_key_here
```

Legacy compatibility is also supported:

```bash
OPENAI_TOKEN=your_api_key_here
```

If both are present, `OPENAI_API_KEY` is used.

## Run Locally

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

GitHub Actions runs pytest, Ruff, and a basic import smoke test on pushes and pull requests targeting `main`.

## Public Demo Limitations

This phase does not include a production database, authentication, billing, scheduled jobs, reminders, or CRM integrations. Manager visibility is represented by single-lead outputs and CRM-ready notes, not by a persisted multi-user dashboard yet.

Future phases may add saved lead lists, CSV upload, manager dashboards, team views, reminders, and private deployment patterns.

## Built By

Bradley Hankins  
Operations & Revenue Leader | AI Workflow Automation | RevOps & Process Improvement
