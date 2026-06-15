from __future__ import annotations

from dataclasses import replace
from datetime import date

from core.lead_store import (
    SessionLeadStore,
    complete_followup,
    csv_template,
    export_leads_csv,
    filter_leads,
    import_leads_csv,
    latest_followup_activity,
    refresh_lead_plan,
)
from core.models import LeadRecord


def lead(**overrides):
    data = {
        "lead_id": "L-1",
        "customer_name": "Demo Customer",
        "company_name": "Demo Company",
        "service_type": "Roof Replacement",
        "lead_stage": "Estimate Sent",
        "assigned_rep": "Mia",
        "estimate_amount": 10000,
        "context_notes": "Customer reviewed the estimate and asked for next steps.",
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


def test_session_lead_store_seed_get_upsert():
    state = {}
    store = SessionLeadStore(state)
    store.seed([lead()])

    assert store.get("L-1") is not None

    updated = lead(customer_name="Updated")
    store.upsert(updated)

    assert store.get("L-1").customer_name == "Updated"
    assert len(store.list()) == 1


def test_filter_leads_by_rep_stage_priority_status_and_search():
    leads = [
        replace(lead(lead_id="L-1", assigned_rep="Mia"), priority="High Priority", followup_status="Overdue"),
        lead(lead_id="L-2", customer_name="Other", assigned_rep="Eli", lead_stage="Won"),
    ]

    filtered = filter_leads(
        leads,
        search="Demo",
        assigned_rep="Mia",
        stage="Estimate Sent",
        priority="High Priority",
        followup_status="Overdue",
        overdue_only=True,
    )

    assert [item.lead_id for item in filtered] == ["L-1"]


def test_complete_followup_updates_outcome_stage_dates_and_recalculates():
    updated = complete_followup(
        lead(),
        "Appointment Scheduled",
        "Customer booked an inspection.",
        today=date(2026, 6, 14),
    )

    assert updated.outcome == "Appointment Scheduled"
    assert updated.outcome_note == "Customer booked an inspection."
    assert updated.lead_stage == "Appointment Set"
    assert updated.last_contact_date == date(2026, 6, 14)
    assert updated.last_action == "Customer booked an inspection."
    assert updated.suggested_followup_date is not None

    activity = latest_followup_activity(updated)
    assert activity["Outcome"] == "Appointment Scheduled"
    assert activity["Saved Outcome Note"] == "Customer booked an inspection."
    assert activity["Last Action"] == "Customer booked an inspection."
    assert activity["Completion / Last Contact Date"] == "2026-06-14"
    assert activity["Resulting Lead Stage"] == "Appointment Set"
    assert activity["Resulting Follow-Up Status"] == updated.followup_status
    assert activity["Next Recommended Follow-Up Date"] == updated.suggested_followup_date.isoformat()
    assert activity["Assigned Rep"] == "Mia"


def test_complete_followup_won_and_closed_lost_are_not_aggressive():
    won = complete_followup(lead(), "Won", "Customer signed.", today=date(2026, 6, 14))
    lost = complete_followup(lead(), "Closed Lost", "Customer chose another provider.", today=date(2026, 6, 14))

    assert won.lead_stage == "Won"
    assert won.priority == "Customer Won"
    assert won.followup_status == "No Active Sales Follow-Up"
    assert won.suggested_followup_date is None
    assert lost.lead_stage == "Closed Lost"
    assert lost.priority == "No Active Follow-Up"


def test_csv_import_accepts_good_rows_and_rejects_bad_rows_and_duplicates():
    csv_text = """lead_id,customer_name,company_name,service_type,lead_stage,assigned_rep,estimate_amount,context_notes,objection,urgency,financing,tone,preferred_channel,followup_intensity,last_contact_date
L-1,Demo Customer,Demo Company,Roof Replacement,Estimate Sent,Mia,10000,Customer reviewed the estimate and asked for next steps.,Price,High,Yes,Consultative,All,Standard,2026-06-13
L-1,Duplicate,Demo Company,Roof Replacement,Estimate Sent,Mia,10000,Customer reviewed the estimate and asked for next steps.,Price,High,Yes,Consultative,All,Standard,2026-06-13
L-3,Bad,Demo Company,Roof Replacement,Unknown,Mia,not-money,Customer reviewed the estimate and asked for next steps.,Price,High,Yes,Consultative,Fax,Standard,not-a-date
"""

    accepted, rejected = import_leads_csv(csv_text)

    assert len(accepted) == 1
    assert accepted[0].lead_id == "L-1"
    assert {row["source_row"] for row in rejected} == {3, 4}
    assert all({"source_row", "lead_id", "field", "reason"}.issubset(row) for row in rejected)
    assert any(row["field"] == "lead_id" and "Duplicate lead_id" in row["reason"] for row in rejected)
    assert any(row["field"] == "estimate_amount" and "Invalid estimate_amount" in row["reason"] for row in rejected)


def test_csv_export_protects_spreadsheet_formula_injection():
    dangerous = lead(customer_name="=cmd", company_name="+company")

    csv_text = export_leads_csv([dangerous])

    assert "'=cmd" in csv_text
    assert "'+company" in csv_text


def test_csv_template_has_expected_header():
    template = csv_template()

    assert template.startswith("lead_id,customer_name,company_name")
