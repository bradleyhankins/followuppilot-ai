from __future__ import annotations

from pathlib import Path

from app import chart_data

ROOT = Path(__file__).resolve().parents[1]


def test_app_does_not_import_altair_directly():
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")

    assert "import altair" not in app_source
    assert "alt.Chart" not in app_source
    assert "st.altair_chart" not in app_source


def test_requirements_do_not_pin_direct_altair_dependency():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "altair" not in requirements.lower()


def test_chart_data_returns_native_chart_ready_dataframe():
    data = chart_data({"Estimate Sent": 3, "Won": 1}, "Stage", "Leads")

    assert list(data.columns) == ["Stage", "Leads"]
    assert data.to_dict("records") == [
        {"Stage": "Estimate Sent", "Leads": 3},
        {"Stage": "Won", "Leads": 1},
    ]
