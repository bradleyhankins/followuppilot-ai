# Architecture

FollowUpPilot AI is a Streamlit sales follow-up workflow assistant for field-sales and home-service teams.

## Current Architecture

The current version is optimized for simple Streamlit Community Cloud deployment and easy GitHub review.

```text
app.py
README.md
requirements.txt
screenshots/
```

## Application Layers

The app is currently deployed from one Streamlit entrypoint, but the code is organized conceptually into clear layers:

```text
Configuration
- Project types
- Lead statuses
- Objection categories
- Tone options
- Sample scenarios

Business Logic
- Priority scoring
- Lead temperature logic
- Deal risk classification
- Next-best-action recommendation
- Objection guidance
- Follow-up sequence generation

Communication Generation
- Text message generation
- Email generation
- Voicemail script generation
- CRM note generation
- Call script generation
- Manager coaching note generation

Reporting
- Downloadable Markdown follow-up plan

Presentation
- Streamlit builder form
- Recommendation snapshot
- Copy center
- Timeline cards
- Tabs and output sections
```

## Design Choices

FollowUpPilot uses rules-based workflow logic so the output remains transparent, editable, and easy to understand.

Key design goals:

- Improve follow-up consistency
- Support sales reps with copy-ready communication
- Improve CRM note quality
- Provide manager coaching context
- Keep all sample data fictional and public-safe

## Why Single-File for This Version

The current single-file version keeps deployment simple for a portfolio app. A future production version would separate configuration, logic, components, and reports.

## Future Production Layout

```text
app.py
src/
  config.py
  scoring.py
  message_generation.py
  reports.py
  components.py
  styles.css
tests/
  test_scoring.py
  test_message_generation.py
```

## Future Refactor Plan

1. Move CSS into `styles.css`
2. Move lead scoring into `src/scoring.py`
3. Move message generation into `src/message_generation.py`
4. Move report generation into `src/reports.py`
5. Add unit tests for priority, temperature, and deal-risk logic
