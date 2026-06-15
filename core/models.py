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


@dataclass(slots=True)
class LeadRecord:
    lead_id: str
    customer_name: str
    company_name: str
    customer_email: str = ""
    customer_phone: str = ""
    service_type: str = "Roof Replacement"
    lead_stage: str = "Estimate Sent"
    assigned_rep: str = ""
    estimate_amount: float | None = None
    context_notes: str = ""
    objection: str = "None"
    urgency: str = "Medium"
    financing: str = "No"
    tone: str = "Professional"
    preferred_channel: str = "All"
    followup_intensity: str = "Standard"
    last_contact_date: date | None = None
    suggested_followup_date: date | None = None
    followup_status: str = "Upcoming"
    priority: str = "Low Priority"
    deal_risk: str = "Low"
    outcome: str = ""
    last_action: str = ""
    outcome_note: str = ""
    created_date: date = field(default_factory=date.today)
    updated_date: date = field(default_factory=date.today)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> LeadRecord:
        lead_input = LeadInput.from_mapping(raw)
        return cls(
            lead_id=str(raw.get("lead_id", "")).strip(),
            customer_name=lead_input.customer_name,
            company_name=lead_input.company_name,
            customer_email=lead_input.customer_email,
            customer_phone=lead_input.customer_phone,
            service_type=lead_input.service_type,
            lead_stage=lead_input.lead_stage,
            assigned_rep=lead_input.assigned_rep,
            estimate_amount=lead_input.estimate_amount,
            context_notes=lead_input.context_notes,
            objection=lead_input.objection,
            urgency=lead_input.urgency,
            financing=lead_input.financing,
            tone=lead_input.tone,
            preferred_channel=lead_input.preferred_channel,
            followup_intensity=lead_input.followup_intensity,
            last_contact_date=lead_input.last_contact_date,
            suggested_followup_date=_parse_date(raw.get("suggested_followup_date")),
            followup_status=str(raw.get("followup_status", "")).strip() or "Upcoming",
            priority=str(raw.get("priority", "")).strip() or "Low Priority",
            deal_risk=str(raw.get("deal_risk", "")).strip() or "Low",
            outcome=str(raw.get("outcome", "")).strip(),
            last_action=str(raw.get("last_action", "")).strip(),
            outcome_note=str(raw.get("outcome_note", raw.get("completion_note", ""))).strip(),
            created_date=_parse_date(raw.get("created_date")) or date.today(),
            updated_date=_parse_date(raw.get("updated_date")) or date.today(),
        )

    def to_lead_input(self) -> LeadInput:
        days_since = 0
        if self.last_contact_date:
            days_since = max(0, (date.today() - self.last_contact_date).days)
        return LeadInput(
            customer_name=self.customer_name,
            company_name=self.company_name,
            customer_email=self.customer_email,
            customer_phone=self.customer_phone,
            service_type=self.service_type,
            lead_stage=self.lead_stage,
            context_notes=self.context_notes,
            objection=self.objection,
            urgency=self.urgency,
            financing=self.financing,
            tone=self.tone,
            last_contact_date=self.last_contact_date,
            assigned_rep=self.assigned_rep,
            estimate_amount=self.estimate_amount,
            preferred_channel=self.preferred_channel,
            followup_intensity=self.followup_intensity,
            days_since_last_contact=days_since,
        )

    def to_workflow_dict(self) -> dict[str, Any]:
        return self.to_lead_input().to_workflow_dict()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("last_contact_date", "suggested_followup_date", "created_date", "updated_date"):
            value = data[key]
            data[key] = value.isoformat() if value else ""
        data["estimate_amount"] = "" if self.estimate_amount is None else self.estimate_amount
        return data

    def with_plan(self, plan: dict[str, Any]) -> LeadRecord:
        return LeadRecord.from_mapping(
            {
                **self.to_dict(),
                "suggested_followup_date": plan.get("suggested_followup_date") or "",
                "followup_status": normalize_followup_status(plan.get("followup_status", "")),
                "priority": plan.get("priority", self.priority),
                "deal_risk": plan.get("deal_risk", self.deal_risk),
            }
        )


def normalize_stage(stage: str) -> str:
    return LEGACY_STAGE_ALIASES.get(stage, stage or "Estimate Sent")


def normalize_followup_status(status: str) -> str:
    value = (status or "").strip()
    if value.startswith("Overdue"):
        return "Overdue"
    if value == "Due today":
        return "Due Today"
    if value == "Upcoming follow-up":
        return "Upcoming"
    if value == "No active follow-up":
        return "No Active Follow-Up"
    if value == "No Active Sales Follow-Up":
        return "No Active Sales Follow-Up"
    return value or "Upcoming"


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
