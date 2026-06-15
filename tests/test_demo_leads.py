from __future__ import annotations

from datetime import date

from data.demo_leads import demo_leads


def test_demo_dataset_has_representative_fictional_workspace():
    leads = demo_leads(today=date(2026, 6, 14))
    stages = {lead.lead_stage for lead in leads}
    services = {lead.service_type for lead in leads}
    reps = {lead.assigned_rep for lead in leads}
    statuses = {lead.followup_status for lead in leads}

    assert 15 <= len(leads) <= 20
    assert {"Won", "Closed Lost"}.issubset(stages)
    assert {"Overdue", "Due Today", "Upcoming"}.issubset(statuses)
    assert len(reps) >= 3
    assert {"Roof Replacement", "HVAC", "Plumbing Repair", "Electrical Service"}.issubset(services)


def test_demo_dataset_has_unique_lead_ids():
    leads = demo_leads(today=date(2026, 6, 14))
    ids = [lead.lead_id for lead in leads]

    assert len(ids) == len(set(ids))
