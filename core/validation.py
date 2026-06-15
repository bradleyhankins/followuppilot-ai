from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

from core.models import LeadInput

VALID_CHANNELS = {"All", "Text", "Email", "Phone Call", "Voicemail", "CRM Note"}
VALID_LEAD_STAGES = {
    "New Lead",
    "Contacted",
    "Appointment Set",
    "Estimate Sent",
    "Decision Pending",
    "Won",
    "Closed Lost",
}
VALID_URGENCY = {"Low", "Medium", "High"}
VALID_INTENSITY = {"Light Touch", "Standard", "Persistent", "Last Attempt"}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_lead_input(raw: dict[str, Any] | LeadInput) -> list[str]:
    raw_service_blank = False
    if isinstance(raw, dict) and ("service_type" in raw or "project_type" in raw):
        raw_service_blank = not str(raw.get("service_type", raw.get("project_type", ""))).strip()

    lead = raw if isinstance(raw, LeadInput) else LeadInput.from_mapping(raw)
    messages: list[str] = []

    if not lead.company_name:
        messages.append("Enter a business or team name so the generated copy has a sender.")
    if raw_service_blank or not lead.service_type:
        messages.append("Choose a service type.")
    if not lead.lead_stage:
        messages.append("Choose a lead stage.")
    if lead.lead_stage not in VALID_LEAD_STAGES:
        messages.append(f"Choose a valid lead stage. Current value: {lead.lead_stage}.")
    if lead.urgency not in VALID_URGENCY:
        messages.append("Choose a valid urgency level.")
    if lead.preferred_channel not in VALID_CHANNELS:
        messages.append("Choose a valid preferred communication channel.")
    if lead.followup_intensity not in VALID_INTENSITY:
        messages.append("Choose a valid follow-up intensity.")

    if lead.customer_email and not EMAIL_RE.match(lead.customer_email):
        messages.append("Enter a valid customer email address or leave it blank for the demo.")
    if lead.customer_phone and not _valid_phone(lead.customer_phone):
        messages.append("Enter a valid customer phone number or leave it blank for the demo.")
    if lead.estimate_amount is not None and lead.estimate_amount < 0:
        messages.append("Estimate amount must be zero or greater.")
    if lead.last_contact_date and lead.last_contact_date > date.today():
        messages.append("Last contact date cannot be in the future.")
    if lead.days_since_last_contact < 0:
        messages.append("Days since last contact must be zero or greater.")

    if lead.lead_stage in {"Estimate Sent", "Decision Pending"} and len(lead.context_notes) < 20:
        messages.append(
            "Add a little more last-interaction context so the follow-up copy can be useful."
        )
    if lead.lead_stage == "Appointment Set" and lead.preferred_channel == "CRM Note":
        messages.append(
            "For appointment-set leads, choose a customer-facing channel unless you only need an internal note."
        )
    if lead.lead_stage == "Closed Lost" and lead.followup_intensity != "Last Attempt":
        messages.append(
            "Closed Lost leads default to no active sales follow-up. Use Last Attempt only for a final close-the-loop or reactivation note."
        )

    return messages


def parse_user_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _valid_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return 7 <= len(digits) <= 15
