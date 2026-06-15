# Project Structure

```text
.
├── app.py
├── ai_helpers.py
├── pdf_helpers.py
├── README.md
├── ARCHITECTURE.md
├── CASE_STUDY.md
├── DEVELOPMENT_NOTES.md
├── PRIVACY_AND_AI_USE.md
├── PROJECT_STRUCTURE.md
├── requirements.txt
├── pyproject.toml
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── .streamlit/
│   └── config.toml
├── core/
│   ├── __init__.py
│   ├── models.py
│   ├── validation.py
│   ├── followup_logic.py
│   ├── prompts.py
│   └── report_builder.py
├── data/
│   ├── __init__.py
│   └── sample_data.py
├── screenshots/
└── tests/
    ├── test_ai_helpers.py
    ├── test_followup_logic.py
    ├── test_reports.py
    ├── test_sample_data.py
    └── test_validation.py
```

## File Responsibilities

- `app.py`: Streamlit app and orchestration.
- `core/models.py`: typed dataclasses for the workflow domain.
- `core/validation.py`: validation rules and user-facing messages.
- `core/followup_logic.py`: deterministic scoring, follow-up, stage, copy, and next-action rules.
- `core/prompts.py`: AI prompt and response parsing helpers.
- `core/report_builder.py`: report text builder for PDF export.
- `ai_helpers.py`: OpenAI key lookup, prompt trimming, diagnostics, and fallback.
- `pdf_helpers.py`: ReportLab PDF rendering.
- `data/sample_data.py`: dropdown options and fictional demo scenarios.
- `tests/`: deterministic unit and smoke coverage.
