from __future__ import annotations

from datetime import date

from core.followup_logic import run_followup_workflow
from core.validation import validate_lead_input
from data.sample_data import SAMPLE_SCENARIOS


def test_representative_sample_scenarios_generate_outputs():
    for name, scenario in SAMPLE_SCENARIOS.items():
        if name == "Blank / Custom":
            continue

        messages = validate_lead_input(scenario)
        if scenario.get("lead_stage") == "Closed Lost":
            assert any("Closed Lost" in message for message in messages)
        else:
            assert messages == []

        outputs = run_followup_workflow(scenario, today=date(2026, 6, 14))
        assert outputs["crm"]
        assert outputs["sequence"]
