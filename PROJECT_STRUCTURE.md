# Project Structure

```text
.
├── app.py                  # Streamlit application entrypoint
├── README.md               # Project overview, case study, and test flow
├── ARCHITECTURE.md         # Architecture and design decisions
├── PROJECT_STRUCTURE.md    # Repository structure reference
├── DEVELOPMENT_NOTES.md    # Implementation notes and future refactor plan
├── requirements.txt        # Python dependencies
└── screenshots/            # README screenshots
```

## Current File Responsibilities

### `app.py`

Contains the deployed Streamlit workflow app.

Responsibilities:

- Page configuration
- Sample scenarios
- Lead scoring logic
- Deal risk and lead temperature logic
- Communication generation
- Copy center output
- Timeline generation
- Markdown follow-up plan export
- Streamlit UI rendering

## Future Production Structure

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

The current structure prioritizes fast portfolio review and live deployment while documenting the path to a modular production build.
