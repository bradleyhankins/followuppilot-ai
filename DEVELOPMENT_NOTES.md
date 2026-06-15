# Development Notes

## Build Philosophy

FollowUpPilot AI is designed as a practical workflow assistant, not an opaque automation system. The deterministic workflow should always be understandable, testable, and useful without AI.

## Engineering Priorities

1. Preserve rules-first behavior.
2. Keep AI optional and bounded.
3. Validate inputs with user-friendly messages.
4. Treat the public demo as non-confidential.
5. Keep the Streamlit UI thin over reusable core logic.
6. Add tests before broadening the product surface.

## Current Foundation

The app now has typed domain models, validation, deterministic follow-up date logic, overdue state, lead-stage-specific behavior, channel-specific next actions, safer HTML rendering, AI fallback diagnostics, JSON-first AI parsing, PDF error handling, and expanded tests.

## Local Checks

```bash
py -m pytest -q
py -m ruff check .
py -c "import app; import core.followup_logic; import core.validation"
```

## Future Refactor Opportunities

- Move Streamlit styling into a separate CSS asset.
- Split deterministic copy templates from scoring logic.
- Add a session or CSV-backed lead list for manager visibility.
- Add UI smoke tests when the interface becomes more complex.
- Add generated screenshot refresh steps for portfolio documentation.
