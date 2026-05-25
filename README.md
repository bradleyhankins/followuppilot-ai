# FollowUpPilot AI

FollowUpPilot AI is an AI-enhanced sales follow-up workflow assistant for field-sales and home-service teams. It turns customer context into next-best actions, priority scoring, lead temperature, deal risk, text messages, emails, voicemail scripts, CRM notes, call scripts, objection guidance, manager coaching notes, and multi-touch follow-up sequences.

## Live Demo

[Launch FollowUpPilot AI](https://followuppilot-ai.streamlit.app/)

## Current Version: v2.6

FollowUpPilot AI combines a deterministic rules-based follow-up workflow engine with embedded AI-enhanced communication generation.

The app is designed to work in two layers:

1. **Rules-based core:** calculates priority, lead temperature, deal risk, next-best action, objection guidance, CRM notes, and follow-up sequences.
2. **Embedded AI layer:** when an OpenAI token is available, the app quietly improves the Copy Center outputs, including text, email, voicemail, CRM note, and manager coaching note.

If the AI call fails or an API key is unavailable, the app silently falls back to the rules-based communication outputs. The user experience stays the same.

## Architecture

FollowUpPilot has been refactored from a single-file Streamlit prototype into a modular application.

```text
followuppilot-ai/
├── app.py
├── ai_helpers.py
├── pdf_helpers.py
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── followup_logic.py
│   ├── prompts.py
│   └── report_builder.py
├── data/
│   ├── __init__.py
│   └── sample_data.py
└── tests/
    └── test_followup_logic.py
```

### Module Responsibilities

- `app.py` handles Streamlit layout, form inputs, rendering, and orchestration.
- `core/followup_logic.py` contains priority scoring, lead temperature, deal risk, next-best-action logic, message templates, CRM notes, call scripts, objection guidance, coaching notes, and follow-up sequence generation.
- `core/prompts.py` contains AI prompt construction and structured AI output parsing.
- `core/report_builder.py` builds the structured report content used for PDF export.
- `data/sample_data.py` stores sample scenarios, dropdown options, lead statuses, objections, tones, and follow-up settings.
- `ai_helpers.py` manages OpenAI access, guardrails, prompt length control, stable cache keys, and silent fallback behavior.
- `pdf_helpers.py` converts structured report text into a downloadable PDF.

## AI Design Pattern

The guiding principle is:

```text
Rules decide. AI polishes. Guardrails constrain. Fallback protects.
```

The rules-based workflow remains the source of truth for:

- Follow-up priority
- Priority score
- Lead temperature
- Deal risk
- Next-best action
- Follow-up timing
- CRM note structure
- Call script
- Objection guidance
- Follow-up sequence

The AI layer is used only to improve the clarity, tone, and usefulness of communication outputs. It should not invent discounts, deadlines, financing approvals, customer promises, warranty terms, or facts that were not provided.

## Privacy and Responsible Use

This public demo is designed for fictional or sample data.

Users should not enter sensitive, confidential, regulated, or unnecessary customer information. When AI enhancement is enabled, text entered into the app may be processed by the configured AI provider for output enhancement.

## Why this project exists

Small and mid-sized businesses often lose revenue because follow-up is inconsistent, CRM notes are incomplete, and reps do not always know the best next step after a customer interaction.

FollowUpPilot AI helps standardize the follow-up process and gives teams a faster way to create clear, professional, context-aware communication and documentation.

## What it analyzes

- Customer/project context
- Project type
- Lead status
- Main concern or objection
- Urgency level
- Financing discussion status
- Preferred communication tone
- Days since last contact
- Follow-up intensity
- Preferred communication channel
- Sales follow-up timing
- Manager coaching priority

## Workflow Outputs

- Follow-up priority level
- Priority score
- Lead temperature
- Deal risk
- Main risk
- Recommended follow-up timing
- Next best action
- AI-enhanced text message with rules-based fallback
- AI-enhanced email with rules-based fallback
- AI-enhanced voicemail script with rules-based fallback
- AI-enhanced CRM note with rules-based fallback
- AI-enhanced manager coaching note with rules-based fallback
- Call script
- Objection-handling guidance
- Follow-up timeline
- Downloadable PDF follow-up plan

## Export Strategy

Current user-facing export:

- PDF follow-up plan for a sales manager, rep, or CRM documentation workflow

The app no longer exposes Markdown as the primary user-facing download because non-technical users expect a polished PDF report.

## Suggested Test Flow

1. Launch the live demo.
2. Load the “Price Objection” sample scenario.
3. Generate the follow-up plan.
4. Review the follow-up priority, lead temperature, deal risk, and next best action.
5. Review the AI-enhanced Copy Center and follow-up timeline.
6. Review the objection guidance, manager coaching note, and follow-up sequence.
7. Download the PDF follow-up plan.

## Automated Tests

This repo includes unit tests for the deterministic follow-up workflow logic.

Run tests locally with:

```bash
py -m pip install -r requirements.txt
py -m pip install pytest
py -m pytest
```

GitHub Actions runs the test suite automatically on push and pull request events.

## Screenshots

Screenshots will be refreshed after the final UI and PDF polish pass.

## Tech Stack

- Python
- Streamlit
- OpenAI API integration
- Rules-based follow-up workflow logic
- Modular app architecture
- Silent AI fallback pattern
- AI guardrails
- PDF report export
- Pytest
- GitHub Actions
- GitHub
- Streamlit Community Cloud

## Run Locally

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Environment Variables

To enable embedded AI output:

```bash
OPENAI_TOKEN=your_api_key_here
```

The app still works without this token by using the rules-based fallback.

## Public Demo Note

All sample data, names, companies, and scenarios used in this project are fictional and created for public portfolio demonstration purposes.

## Case Study

### Problem

Field-sales and home-service teams often lose opportunities because follow-up is inconsistent, CRM notes are incomplete, and sales representatives do not always have a clear next step after a customer interaction.

### Solution

FollowUpPilot AI helps sales representatives and managers create stronger follow-up communication and cleaner CRM documentation. The embedded AI layer improves the Copy Center language when available while preserving a reliable rules-based fallback.

### Business Value

FollowUpPilot AI helps small and mid-sized businesses improve sales execution by creating a more consistent follow-up process, improving message quality, standardizing CRM notes, and reducing missed follow-up opportunities.

## Built By

Bradley Hankins  
Operations & Revenue Leader | AI Workflow Automation | RevOps & Process Improvement
