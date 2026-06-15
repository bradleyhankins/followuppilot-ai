from __future__ import annotations

from datetime import date

from app import (
    ai_cache_context,
    build_workspace_plan,
    lead_id_from_selector_label,
    lead_selector_label,
    output_widget_keys,
    resolve_selected_lead,
)
from core.followup_logic import run_followup_workflow
from core.lead_store import refresh_lead_plan
from core.models import LeadRecord
from core.report_builder import build_report


def lead(**overrides) -> LeadRecord:
    data = {
        "lead_id": "FUP-ACTIVE",
        "customer_name": "Avery Johnson",
        "company_name": "Summit Home Services",
        "service_type": "Roof Replacement",
        "lead_stage": "Estimate Sent",
        "assigned_rep": "Mia Chen",
        "estimate_amount": 18000,
        "context_notes": "Customer reviewed the estimate and asked about financing.",
        "objection": "Price",
        "urgency": "High",
        "financing": "Yes",
        "tone": "Consultative",
        "preferred_channel": "All",
        "followup_intensity": "Standard",
        "last_contact_date": "2026-06-13",
    }
    data.update(overrides)
    return refresh_lead_plan(LeadRecord.from_mapping(data), today=date(2026, 6, 14))


def test_selector_label_round_trips_lead_id():
    item = lead(lead_id="FUP-1010", customer_name="Quinn Harper", service_type="HVAC Replacement")

    label = lead_selector_label(item)

    assert label == "FUP-1010 - Quinn Harper (HVAC Replacement)"
    assert lead_id_from_selector_label(label) == "FUP-1010"


def test_resolve_selected_lead_uses_new_selection():
    active = lead(lead_id="FUP-ACTIVE")
    won = lead(lead_id="FUP-1010", lead_stage="Won", customer_name="Quinn Harper")

    assert resolve_selected_lead([active, won], "FUP-1010").lead_id == "FUP-1010"


def test_generated_widget_keys_are_scoped_by_lead_and_builder_context():
    active_keys = output_widget_keys("workspace_FUP-ACTIVE")
    won_keys = output_widget_keys("workspace_FUP-1010")
    builder_keys = output_widget_keys("builder_price_objection")

    assert active_keys["sms"] != won_keys["sms"]
    assert active_keys["email"] != won_keys["email"]
    assert not set(active_keys.values()) & set(builder_keys.values())


def test_workspace_plan_uses_newly_selected_won_lead_after_active_lead():
    active = lead(lead_id="FUP-ACTIVE", lead_stage="Estimate Sent", customer_name="Avery Johnson")
    won = lead(lead_id="FUP-1010", lead_stage="Won", customer_name="Quinn Harper")

    _, active_plan = build_workspace_plan(active)
    won_inputs, won_plan = build_workspace_plan(won)

    assert "Avery" in active_plan["sms"]
    assert won_inputs["lead_stage"] == "Won"
    assert won_plan["followup_status"] == "No Active Sales Follow-Up"
    assert won_plan["suggested_followup_date"] is None
    assert "handoff" in won_plan["next_action"].lower() or "customer care" in won_plan["next_action"].lower()
    assert "Avery" not in won_plan["sms"]


def test_workspace_plan_does_not_block_on_ai_enhancement(monkeypatch):
    item = lead(lead_id="FUP-1004", customer_name="Taylor Brooks", service_type="Windows")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("workspace plans must render deterministic output before optional AI")

    monkeypatch.setattr("app.enhance_outputs", fail_if_called)

    inputs, plan = build_workspace_plan(item)

    assert inputs["customer_name"] == "Taylor Brooks"
    assert "Taylor" in plan["sms"]
    assert plan["subject"]
    assert "Taylor" in plan["email"]


def test_workspace_plan_uses_newly_selected_closed_lost_lead_after_active_lead():
    active = lead(lead_id="FUP-ACTIVE", lead_stage="Decision Pending", customer_name="Avery Johnson")
    closed = lead(lead_id="FUP-1011", lead_stage="Closed Lost", customer_name="Morgan Lee")

    _, active_plan = build_workspace_plan(active)
    closed_inputs, closed_plan = build_workspace_plan(closed)

    assert "Avery" in active_plan["sms"]
    assert closed_inputs["lead_stage"] == "Closed Lost"
    assert closed_plan["suggested_followup_date"] is None
    assert "active sales follow-up is paused" in closed_plan["why"]
    assert "Avery" not in closed_plan["sms"]


def test_pdf_report_inputs_match_current_selected_lead():
    won = lead(lead_id="FUP-1010", lead_stage="Won", customer_name="Quinn Harper")

    inputs, plan = build_workspace_plan(won)
    report = build_report(inputs, plan)

    assert "Quinn Harper" in report
    assert "No Active Sales Follow-Up" in report
    assert "Avery Johnson" not in report


def test_ai_cache_context_changes_for_materially_different_leads():
    active = lead(lead_id="FUP-ACTIVE", lead_stage="Estimate Sent", customer_name="Avery Johnson")
    won = lead(lead_id="FUP-1010", lead_stage="Won", customer_name="Quinn Harper")

    active_context = ai_cache_context(active.to_workflow_dict(), "workspace_FUP-ACTIVE")
    won_context = ai_cache_context(won.to_workflow_dict(), "workspace_FUP-1010")

    assert active_context != won_context
    assert active_context["context_key"] != won_context["context_key"]
    assert active_context["lead_stage"] != won_context["lead_stage"]


def test_pure_engine_won_and_closed_lost_do_not_reuse_active_plan_content():
    active = lead(lead_id="FUP-ACTIVE", lead_stage="Estimate Sent", customer_name="Avery Johnson")
    won = lead(lead_id="FUP-1010", lead_stage="Won", customer_name="Quinn Harper")
    closed = lead(lead_id="FUP-1011", lead_stage="Closed Lost", customer_name="Morgan Lee")

    active_plan = run_followup_workflow(active.to_workflow_dict(), today=date(2026, 6, 14))
    won_plan = run_followup_workflow(won.to_workflow_dict(), today=date(2026, 6, 14))
    closed_plan = run_followup_workflow(closed.to_workflow_dict(), today=date(2026, 6, 14))

    assert active_plan["customer_name"] if "customer_name" in active_plan else active.customer_name
    assert won_plan["followup_status"] == "No Active Sales Follow-Up"
    assert closed_plan["priority"] == "No Active Follow-Up"
    assert "Avery" not in won_plan["sms"]
    assert "Avery" not in closed_plan["sms"]
