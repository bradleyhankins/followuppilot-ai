# Development Notes

## Build Philosophy

FollowUpPilot AI is designed as a practical workflow assistant for sales follow-up execution.

The app focuses on repeatable workflow support rather than opaque automation.

## Engineering Priorities

1. Clear user workflow
2. Transparent scoring and recommendation rules
3. Copy-ready communication outputs
4. CRM documentation support
5. Public-safe sample scenarios
6. Simple deployment on Streamlit Community Cloud

## Current Tradeoffs

The deployed portfolio version keeps the app in a single Streamlit entrypoint for simplicity. This makes it easy to run and review, while a future production version would split message generation and scoring into separate modules.

## Future Refactor Plan

A future production-oriented version should split the app into:

```text
src/config.py
src/scoring.py
src/message_generation.py
src/reports.py
src/components.py
src/styles.css
```

## Testing Opportunities

The most valuable future tests would cover:

- Priority score calculation
- Lead temperature classification
- Deal risk classification
- Next-best-action selection
- Follow-up sequence generation
- Markdown report generation

## Code Quality Roadmap

Potential future tooling:

- Ruff for linting and formatting
- Pytest for business logic tests
- Pre-commit hooks
- GitHub Actions smoke checks
