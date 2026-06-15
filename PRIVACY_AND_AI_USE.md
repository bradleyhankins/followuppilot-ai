# Privacy and AI Use

FollowUpPilot AI is a public demo. It is designed for fictional, sample, or generalized customer follow-up scenarios only.

## Do Not Enter

- real customer personal information
- payment details
- financing application details
- medical, legal, or regulated data
- internal company secrets
- proprietary contracts or confidential business records
- passwords, API keys, or credentials

## Session Persistence

Phase 2 stores imported and edited leads only in the current Streamlit session. Uploaded CSV files are parsed in memory and are not intentionally written to persistent storage by the application.

## AI Processing

When `OPENAI_API_KEY` or `OPENAI_TOKEN` is configured, selected inputs may be sent to the AI provider to improve copy-center wording. The deterministic rules engine remains the source of truth for priority, dates, risk, stage behavior, and next action.

The app works without an AI key.

## CSV Safety

CSV exports protect against spreadsheet formula injection by prefixing risky cell values that begin with `=`, `+`, `-`, or `@`.

## Production Requirements

A production version would need authentication, authorization, durable storage, audit controls, data-retention policy, integration governance, and operational monitoring.
