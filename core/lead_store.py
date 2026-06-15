from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import replace
from datetime import date
from io import StringIO
from typing import Any

from core.followup_logic import run_followup_workflow
from core.models import LeadRecord
from core.validation import VALID_CHANNELS, VALID_INTENSITY, VALID_LEAD_STAGES, VALID_URGENCY

OUTCOMES = [
    "No Response",
    "Contacted",
    "Appointment Scheduled",
    "Estimate Reviewed",
    "Follow-Up Requested",
    "Won",
    "Closed Lost",
    "Long-Term Nurture",
]

CSV_COLUMNS = [
    "lead_id",
    "customer_name",
    "company_name",
    "customer_email",
    "customer_phone",
    "service_type",
    "lead_stage",
    "assigned_rep",
    "estimate_amount",
    "context_notes",
    "objection",
    "urgency",
    "financing",
    "tone",
    "preferred_channel",
    "followup_intensity",
    "last_contact_date",
    "suggested_followup_date",
    "followup_status",
    "priority",
    "deal_risk",
    "outcome",
    "last_action",
    "outcome_note",
    "created_date",
    "updated_date",
]


class SessionLeadStore:
    def __init__(self, state: dict[str, Any], key: str = "managed_leads") -> None:
        self.state = state
        self.key = key

    def seed(self, leads: Iterable[LeadRecord], force: bool = False) -> None:
        if force or self.key not in self.state:
            self.state[self.key] = list(leads)

    def list(self) -> list[LeadRecord]:
        return list(self.state.get(self.key, []))

    def replace_all(self, leads: Iterable[LeadRecord]) -> None:
        self.state[self.key] = list(leads)

    def get(self, lead_id: str) -> LeadRecord | None:
        return next((lead for lead in self.list() if lead.lead_id == lead_id), None)

    def upsert(self, lead: LeadRecord) -> None:
        leads = self.list()
        for index, existing in enumerate(leads):
            if existing.lead_id == lead.lead_id:
                leads[index] = lead
                self.replace_all(leads)
                return
        leads.append(lead)
        self.replace_all(leads)


def refresh_lead_plan(lead: LeadRecord, today: date | None = None) -> LeadRecord:
    plan = run_followup_workflow(lead.to_workflow_dict(), today=today)
    return lead.with_plan(plan)


def refresh_all_plans(leads: Iterable[LeadRecord], today: date | None = None) -> list[LeadRecord]:
    return [refresh_lead_plan(lead, today=today) for lead in leads]


def complete_followup(
    lead: LeadRecord,
    outcome: str,
    action_note: str,
    today: date | None = None,
) -> LeadRecord:
    today = today or date.today()
    next_stage = stage_for_outcome(lead.lead_stage, outcome)
    completed = replace(
        lead,
        outcome=outcome,
        outcome_note=action_note.strip(),
        last_action=action_note.strip() or f"Follow-up completed: {outcome}",
        last_contact_date=today,
        updated_date=today,
        lead_stage=next_stage,
        followup_status="Completed",
    )
    if next_stage in {"Won", "Closed Lost"}:
        return refresh_lead_plan(completed, today=today)
    return refresh_lead_plan(completed, today=today)


def latest_followup_activity(lead: LeadRecord) -> dict[str, str]:
    return {
        "Outcome": lead.outcome or "N/A",
        "Saved Outcome Note": lead.outcome_note or "N/A",
        "Last Action": lead.last_action or "N/A",
        "Completion / Last Contact Date": lead.last_contact_date.isoformat()
        if lead.last_contact_date
        else "N/A",
        "Resulting Lead Stage": lead.lead_stage,
        "Resulting Follow-Up Status": lead.followup_status,
        "Next Recommended Follow-Up Date": lead.suggested_followup_date.isoformat()
        if lead.suggested_followup_date
        else "N/A",
        "Assigned Rep": lead.assigned_rep or "Unassigned",
    }


def stage_for_outcome(current_stage: str, outcome: str) -> str:
    return {
        "Appointment Scheduled": "Appointment Set",
        "Estimate Reviewed": "Decision Pending",
        "Won": "Won",
        "Closed Lost": "Closed Lost",
        "Long-Term Nurture": "Closed Lost",
    }.get(outcome, current_stage)


def filter_leads(
    leads: Iterable[LeadRecord],
    search: str = "",
    assigned_rep: str = "All",
    stage: str = "All",
    priority: str = "All",
    followup_status: str = "All",
    overdue_only: bool = False,
    sort_by: str = "follow-up date",
) -> list[LeadRecord]:
    search_value = search.strip().lower()
    filtered = []
    for lead in leads:
        haystack = " ".join(
            [
                lead.lead_id,
                lead.customer_name,
                lead.company_name,
                lead.service_type,
                lead.assigned_rep,
                lead.lead_stage,
            ]
        ).lower()
        if search_value and search_value not in haystack:
            continue
        if assigned_rep != "All" and lead.assigned_rep != assigned_rep:
            continue
        if stage != "All" and lead.lead_stage != stage:
            continue
        if priority != "All" and lead.priority != priority:
            continue
        if followup_status != "All" and lead.followup_status != followup_status:
            continue
        if overdue_only and lead.followup_status != "Overdue":
            continue
        filtered.append(lead)
    return sorted(filtered, key=_sort_key(sort_by))


def import_leads_csv(csv_text: str, existing_ids: set[str] | None = None) -> tuple[list[LeadRecord], list[dict[str, Any]]]:
    existing_ids = existing_ids or set()
    accepted: list[LeadRecord] = []
    rejected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    reader = csv.DictReader(StringIO(csv_text))
    if not reader.fieldnames:
        return [], [{"row": 0, "lead_id": "", "messages": ["CSV file is empty or missing a header row."]}]

    for row_number, row in enumerate(reader, start=2):
        lead_id = (row.get("lead_id") or "").strip()
        messages = validate_import_row(row)
        if not lead_id:
            messages.append("lead_id is required.")
        if lead_id in existing_ids or lead_id in seen_ids:
            messages.append(f"Duplicate lead_id: {lead_id}.")
        if messages:
            rejected.extend(_rejection_rows(row_number, lead_id, messages))
            continue
        seen_ids.add(lead_id)
        accepted.append(refresh_lead_plan(LeadRecord.from_mapping(row)))
    return accepted, rejected


def export_leads_csv(leads: Iterable[LeadRecord]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for lead in leads:
        row = {key: _safe_csv_cell(value) for key, value in lead.to_dict().items() if key in CSV_COLUMNS}
        writer.writerow(row)
    return output.getvalue()


def csv_template() -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerow(
        {
            "lead_id": "DEMO-001",
            "customer_name": "Fictional Customer",
            "company_name": "Summit Home Services",
            "service_type": "Roof Replacement",
            "lead_stage": "Estimate Sent",
            "assigned_rep": "Demo Rep",
            "estimate_amount": "8500",
            "context_notes": "Customer is comparing roof options after an inspection.",
            "objection": "Price",
            "urgency": "High",
            "financing": "Yes",
            "tone": "Consultative",
            "preferred_channel": "All",
            "followup_intensity": "Standard",
            "last_contact_date": date.today().isoformat(),
        }
    )
    return output.getvalue()


def validate_import_row(row: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    if (row.get("lead_stage") or "").strip() not in VALID_LEAD_STAGES:
        messages.append(f"Unknown lead stage: {row.get('lead_stage', '')}.")
    if (row.get("preferred_channel") or "All").strip() not in VALID_CHANNELS:
        messages.append(f"Unknown preferred channel: {row.get('preferred_channel', '')}.")
    if (row.get("urgency") or "Medium").strip() not in VALID_URGENCY:
        messages.append(f"Unknown urgency: {row.get('urgency', '')}.")
    if (row.get("followup_intensity") or "Standard").strip() not in VALID_INTENSITY:
        messages.append(f"Unknown follow-up intensity: {row.get('followup_intensity', '')}.")
    if not (row.get("company_name") or "").strip():
        messages.append("company_name is required.")
    if not (row.get("service_type") or "").strip():
        messages.append("service_type is required.")
    amount = row.get("estimate_amount")
    if amount not in (None, ""):
        try:
            if float(str(amount).replace("$", "").replace(",", "")) < 0:
                messages.append("estimate_amount must be zero or greater.")
        except ValueError:
            messages.append(f"Invalid estimate_amount: {amount}.")
    for key in ("last_contact_date", "created_date", "updated_date", "suggested_followup_date"):
        value = (row.get(key) or "").strip()
        if value:
            try:
                date.fromisoformat(value)
            except ValueError:
                messages.append(f"Invalid date for {key}: {value}.")
    return messages


def _rejection_rows(row_number: int, lead_id: str, messages: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "source_row": row_number,
            "lead_id": lead_id or "N/A",
            "field": _field_from_message(message),
            "reason": message,
        }
        for message in messages
    ]


def _field_from_message(message: str) -> str:
    if "lead_id" in message:
        return "lead_id"
    if "lead stage" in message:
        return "lead_stage"
    if "preferred channel" in message:
        return "preferred_channel"
    if "urgency" in message:
        return "urgency"
    if "follow-up intensity" in message:
        return "followup_intensity"
    if "company_name" in message:
        return "company_name"
    if "service_type" in message:
        return "service_type"
    if "estimate_amount" in message:
        return "estimate_amount"
    if "date for" in message:
        return message.rsplit(" ", 1)[-1].rstrip(":")
    return "row"


def _safe_csv_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    if text.startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text


def _sort_key(sort_by: str):
    priority_rank = {"High Priority": 0, "Medium Priority": 1, "Low Priority": 2}

    def key(lead: LeadRecord):
        if sort_by == "priority":
            return (priority_rank.get(lead.priority, 9), lead.customer_name)
        if sort_by == "estimate amount":
            return (-(lead.estimate_amount or 0), lead.customer_name)
        if sort_by == "last contact":
            return (lead.last_contact_date or date.max, lead.customer_name)
        return (lead.suggested_followup_date or date.max, lead.customer_name)

    return key
