from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta

from core.dashboard import (
    dashboard_metrics,
    manager_attention_flags,
    overdue_by_rep,
    value_by_stage,
)
from data.demo_leads import demo_leads


def test_dashboard_metrics_cover_active_overdue_due_today_and_value():
    leads = demo_leads(today=date(2026, 6, 14))

    metrics = dashboard_metrics(leads)

    assert metrics["active_leads"] > 0
    assert metrics["overdue_followups"] > 0
    assert metrics["due_today"] > 0
    assert metrics["active_pipeline_value"] > 0
    assert metrics["won_value"] > 0


def test_dashboard_metrics_exclude_won_from_active_followup_counts():
    won = replace(
        demo_leads(today=date(2026, 6, 14))[0],
        lead_stage="Won",
        followup_status="No Active Sales Follow-Up",
        priority="Customer Won",
        suggested_followup_date=None,
        estimate_amount=50000,
    )

    metrics = dashboard_metrics([won])

    assert metrics["active_leads"] == 0
    assert metrics["overdue_followups"] == 0
    assert metrics["due_today"] == 0
    assert metrics["high_priority"] == 0
    assert metrics["active_pipeline_value"] == 0
    assert metrics["won_value"] == 50000


def test_dashboard_breakdowns_return_manager_useful_groups():
    leads = demo_leads(today=date(2026, 6, 14))

    assert "Estimate Sent" in value_by_stage(leads)
    assert any(count > 0 for count in overdue_by_rep(leads).values())


def test_manager_attention_flags_include_key_categories():
    leads = demo_leads(today=date(2026, 6, 14))
    flags = manager_attention_flags(leads, today=date(2026, 6, 14))
    reasons = " ".join(flag.reason for flag in flags)

    assert "High-priority overdue" in reasons
    assert "Large estimate" in reasons
    assert "Decision-stage" in reasons
    assert "Multiple overdue" in reasons


def test_manager_attention_flags_detect_missing_information():
    lead = replace(
        demo_leads(today=date(2026, 6, 14))[0],
        customer_name="",
        assigned_rep="",
        context_notes="",
        last_contact_date=date.today() - timedelta(days=1),
    )

    flags = manager_attention_flags([lead])

    assert any("missing required information" in flag.title for flag in flags)
