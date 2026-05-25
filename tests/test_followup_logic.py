from core.followup_logic import (
    calculate_priority,
    get_deal_risk,
    get_lead_temperature,
    run_followup_workflow,
)


def test_calculate_priority_returns_high_priority_for_urgent_estimate():
    priority, timing, score = calculate_priority(
        lead_status="Estimate Presented",
        urgency="High",
        financing="Yes",
        objection="Price",
        project_type="Roof Replacement",
        days_since=3,
        intensity="Persistent",
    )

    assert priority == "High Priority"
    assert timing == "Follow up today"
    assert score >= 9


def test_get_lead_temperature_returns_hot_for_pending_signature():
    temperature = get_lead_temperature(
        priority="Medium Priority",
        lead_status="Verbal Yes / Pending Signature",
        days_since=2,
    )

    assert temperature == "Hot"


def test_get_deal_risk_flags_old_leads_as_high_risk():
    risk, main_risk = get_deal_risk(
        objection="Timing",
        days_since=8,
        lead_status="Proposal Sent",
    )

    assert risk == "High"
    assert main_risk == "No recent contact"


def test_run_followup_workflow_returns_expected_output_keys():
    inputs = {
        "customer": "Avery Johnson",
        "company": "Summit Home Services",
        "project_type": "Roof Replacement",
        "lead_status": "Estimate Presented",
        "context": "Customer liked the proposal but had pricing questions.",
        "objection": "Price",
        "financing": "Yes",
        "urgency": "High",
        "tone": "Consultative",
        "days_since": 1,
        "intensity": "Standard",
        "channel": "All",
    }

    outputs = run_followup_workflow(inputs)

    expected_keys = {
        "priority",
        "timing",
        "score",
        "temperature",
        "deal_risk",
        "main_risk",
        "next_action",
        "why",
        "sms",
        "subject",
        "email",
        "voicemail",
        "guidance",
        "coaching",
        "sequence",
        "crm",
        "call",
    }

    assert expected_keys.issubset(outputs.keys())
    assert outputs["priority"] in {"High Priority", "Medium Priority", "Low Priority"}
    assert isinstance(outputs["sequence"], dict)
    assert outputs["sms"]
