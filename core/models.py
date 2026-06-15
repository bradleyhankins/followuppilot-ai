from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

LEGACY_STAGE_ALIASES = {
    "Inspection Scheduled": "Appointment Set",
    "Inspection Completed": "Contacted",
    "Estimate Presented": "Estimate Sent",
    "Proposal Sent": "Estimate Sent",
    "Needs Follow-Up": "Decision Pending",
    "Verbal Yes / Pending Signature": "Decision Pending",
}


@dataclass(slots=True)
class LeadInput:
    customer_name: str = ""
    company_name: str = ""
    customer_email: str = ""
    customer_phone: str = ""
    service_type: str = "Roof Replacement"
    lead_stage: str = "Estimate Sent"
    context_notes: str = ""
    objection: str = "None"
    urgency: str = "Medium"
    financing: str = "No"
    tone: str = "Professional"
    last_contact_date: date | None = None
    assigned_rep: str = ""
    estimate_amount: float | None = None
    preferred_channel: str = "All"
    followup_intensity: str = "Standard"
    days_since_last_contact: int = 0

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> LeadInput:
        stage = raw.get("lead_stage", raw.get("lead_status", "Estimate Sent"))
        service_type = raw.get("service_type", raw.get("project_type", "Roof Replacement"))
        last_contact = _parse_date(raw.get("last_contact_date"))
        days_since = raw.get("days_since_last_contact", raw.get("days_since", 0))

        try:
            days_since_int = max(0, int(days_since))
        except (TypeError, ValueError):
            days_since_int = 0

        if last_contact is None and days_since_int:
            last_contact = date.today() - timedelta(days=days_since_int)
        elif last_contact is not None:
            days_since_int = max(0, (date.today() - last_contact).days)

        return cls(
            customer_name=str(raw.get("customer_name", raw.get("customer", ""))).strip(),
            company_name=str(raw.get("company_name", raw.get("company", ""))).strip(),
            customer_email=str(raw.get("customer_email", "")).strip(),
            customer_phone=str(raw.get("customer_phone", "")).strip(),
            service_type=str(service_type).strip() or "Roof Replacement",
            lead_stage=normalize_stage(str(stage).strip()),
            context_notes=str(raw.get("context_notes", raw.get("context", ""))).strip(),
            objection=str(raw.get("objection", "None")).strip() or "None",
            urgency=str(raw.get("urgency", "Medium")).strip() or "Medium",
            financing=str(raw.get("financing", "No")).strip() or "No",
            tone=str(raw.get("tone", "Professional")).strip() or "Professional",
            last_contact_date=last_contact,
            assigned_rep=str(raw.get("assigned_rep", "")).strip(),
            estimate_amount=_parse_amount(raw.get("estimate_amount")),
            preferred_channel=str(raw.get("preferred_channel", raw.get("channel", "All"))).strip()
            or "All",
            followup_intensity=str(raw.get("followup_intensity", raw.get("intensity", "Standard"))).strip()
            or "Standard",
            days_since_last_contact=days_since_int,
        )

    def to_workflow_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.update(
            {
                "customer": self.customer_name,
                "company": self.company_name,
                "project_type": self.service_type,
                "lead_status": self.lead_stage,
                "context": self.context_notes,
                "days_since": self.days_since_last_contact,
                "channel": self.preferred_channel,
                "intensity": self.followup_intensity,
            }
        )
        if self.last_contact_date:
            data["last_contact_date"] = self.last_contact_date.isoformat()
        return data


@dataclass(slots=True)
class GeneratedCopy:
    sms: str = ""
    subject: str = ""
    email: str = ""
    voicemail: str = ""
    crm: str = ""
    coaching: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class FollowupPlan:
    priority: str
    timing: str
    score: int
    temperature: str
    deal_risk: str
    main_risk: str
    next_action: str
    why: str
    suggested_followup_date: date | None
    followup_status: str
    days_overdue: int = 0
    is_overdue: bool = False
    due_today: bool = False
    upcoming_followup: bool = False
    copy: GeneratedCopy = field(default_factory=GeneratedCopy)
    guidance: str = ""
    sequence: dict[str, str] = field(default_factory=dict)
    call: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.update(self.copy.to_dict())
        data.pop("copy", None)
        if self.suggested_followup_date:
            data["suggested_followup_date"] = self.suggested_followup_date.isoformat()
        return data


def normalize_stage(stage: str) -> str:
    return LEGACY_STAGE_ALIASES.get(stage, stage or "Estimate Sent")


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not value:
        return None
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _parse_amount(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except ValueError:
        return None
