from __future__ import annotations

from datetime import date, timedelta

from core.followup_logic import (
    calculate_priority,
    followup_status,
    get_deal_risk,
    get_lead_temperature,
    next_best_action,
    run_followup_workflow,
    suggest_followup_date,
)
from core.models import LeadInput

BASE_INPUTS = {
    "customer_name": "Avery Johnson",
    "company_name": "Summit Home Services",
    "service_type": "Roof Replacement",
    "lead_stage": "Estimate Sent",
    "context_notes": "Customer liked the proposal but had pricing questions.",
    "objection": "Price",
    "financing": "Yes",
    "urgency": "High",
    "tone": "Consultative",
    "last_contact_date": "2026-06-13",
    "days_since_last_contact": 1,
    "followup_intensity": "Standard",
    "preferred_channel": "All",
}


def test_calculate_priority_returns_high_priority_for_urgent_estimate():
    priority, timing, score = calculate_priority(
        lead_status="Estimate Sent",
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


def test_get_lead_temperature_returns_hot_for_decision_pending():
    temperature = get_lead_temperature(
        priority="Medium Priority",
        lead_status="Decision Pending",
        days_since=2,
    )

    assert temperature == "Hot"


def test_get_deal_risk_flags_old_leads_as_high_risk():
    risk, main_risk = get_deal_risk(
        objection="Timing",
        days_since=8,
        lead_status="Estimate Sent",
    )

    assert risk == "High"
    assert main_risk == "No recent contact"


def test_run_followup_workflow_returns_expected_output_keys():
    outputs = run_followup_workflow(BASE_INPUTS, today=date(2026, 6, 14))

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
        "suggested_followup_date",
        "followup_status",
        "is_overdue",
        "due_today",
        "upcoming_followup",
    }

    assert expected_keys.issubset(outputs.keys())
    assert outputs["priority"] in {"High Priority", "Medium Priority", "Low Priority"}
    assert isinstance(outputs["sequence"], dict)
    assert outputs["sms"]


def test_closed_lost_does_not_receive_active_sales_followup():
    inputs = {
        **BASE_INPUTS,
        "lead_stage": "Closed Lost",
        "preferred_channel": "CRM Note",
        "followup_intensity": "Standard",
    }

    outputs = run_followup_workflow(inputs, today=date(2026, 6, 14))

    assert outputs["priority"] == "No Active Follow-Up"
    assert outputs["suggested_followup_date"] is None
    assert "No active sales follow-up" in outputs["next_action"]
    assert outputs["followup_status"] == "No active follow-up"


def test_won_moves_to_post_sale_handoff():
    outputs = run_followup_workflow(
        {**BASE_INPUTS, "lead_stage": "Won"}, today=date(2026, 6, 14)
    )

    assert outputs["priority"] == "Customer Won"
    assert outputs["followup_status"] == "No Active Sales Follow-Up"
    assert outputs["suggested_followup_date"] is None
    assert not outputs["is_overdue"]
    assert not outputs["due_today"]
    assert not outputs["upcoming_followup"]
    assert "active sales" in outputs["next_action"].lower()
    assert any(term in outputs["next_action"].lower() for term in ["onboarding", "handoff", "kickoff", "customer care"])


def test_legacy_input_names_are_supported():
    outputs = run_followup_workflow(
        {
            "customer": "Legacy Customer",
            "company": "Legacy Company",
            "project_type": "Gutters",
            "lead_status": "Proposal Sent",
            "context": "Customer received the proposal and is comparing options.",
            "objection": "Timing",
            "financing": "No",
            "urgency": "Medium",
            "tone": "Direct",
            "days_since": 4,
            "intensity": "Persistent",
            "channel": "Text",
        },
        today=date(2026, 6, 14),
    )

    assert outputs["priority"] in {"Medium Priority", "High Priority"}
    assert "text" in outputs["next_action"].lower()


def test_each_channel_has_channel_specific_next_action():
    expected_terms = {
        "Phone Call": "Call first",
        "Text": "text",
        "Email": "email",
        "Voicemail": "voicemail",
        "CRM Note": "CRM note",
    }

    for channel, term in expected_terms.items():
        action = next_best_action(
            {**BASE_INPUTS, "preferred_channel": channel, "urgency": "Low"},
            "Low Priority",
            "Low",
        )
        assert term.lower() in action.lower()


def test_suggest_followup_date_can_be_due_today():
    lead = LeadInput.from_mapping({**BASE_INPUTS, "urgency": "High"})

    suggested = suggest_followup_date(lead, "High Priority", today=date(2026, 6, 14))

    assert suggested == date(2026, 6, 14)


def test_followup_status_overdue_due_today_and_upcoming():
    today = date(2026, 6, 14)

    overdue = followup_status(today - timedelta(days=2), today=today)
    due = followup_status(today, today=today)
    upcoming = followup_status(today + timedelta(days=2), today=today)

    assert overdue == ("Overdue by 2 day(s)", True, False, False, 2)
    assert due == ("Due today", False, True, False, 0)
    assert upcoming == ("Upcoming follow-up", False, False, True, 0)
