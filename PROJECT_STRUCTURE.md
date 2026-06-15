# Project Structure

```text
.
├── app.py
├── ai_helpers.py
├── pdf_helpers.py
├── core/
│   ├── dashboard.py
│   ├── followup_logic.py
│   ├── lead_store.py
│   ├── models.py
│   ├── prompts.py
│   ├── report_builder.py
│   └── validation.py
├── data/
│   ├── demo_leads.py
│   └── sample_data.py
├── tests/
│   ├── test_ai_helpers.py
│   ├── test_dashboard.py
│   ├── test_demo_leads.py
│   ├── test_followup_logic.py
│   ├── test_lead_store.py
│   ├── test_reports.py
│   ├── test_sample_data.py
│   └── test_validation.py
└── docs and screenshots
```

## Key Responsibilities

- `app.py`: Streamlit navigation and UI.
- `core/models.py`: typed lead and follow-up domain objects.
- `core/lead_store.py`: session store, CSV import/export, filtering, completion, and outcomes.
- `core/dashboard.py`: metrics, aggregations, and manager attention flags.
- `core/followup_logic.py`: deterministic rules-first follow-up engine.
- `data/demo_leads.py`: fictional managed lead dataset.
- `data/sample_data.py`: single-lead builder scenarios and dropdown options.
