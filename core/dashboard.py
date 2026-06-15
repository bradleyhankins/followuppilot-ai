from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date

from core.models import LeadRecord

ACTIVE_STAGES = {"New Lead", "Contacted", "Appointment Set", "Estimate Sent", "Decision Pending"}


@dataclass(slots=True)
class AttentionItem:
    lead_id: str
    title: str
    reason: str
    severity: str = "Medium"


def dashboard_metrics(leads: list[LeadRecord]) -> dict[str, float | int]:
    active = [lead for lead in leads if lead.lead_stage in ACTIVE_STAGES]
    return {
        "active_leads": len(active),
        "overdue_followups": sum(1 for lead in active if lead.followup_status == "Overdue"),
        "due_today": sum(1 for lead in active if lead.followup_status == "Due Today"),
        "high_priority": sum(1 for lead in active if lead.priority == "High Priority"),
        "active_pipeline_value": sum(lead.estimate_amount or 0 for lead in active),
        "won_value": sum(lead.estimate_amount or 0 for lead in leads if lead.lead_stage == "Won"),
    }


def count_by(leads: list[LeadRecord], field: str) -> dict[str, int]:
    return dict(Counter(str(getattr(lead, field) or "Unassigned") for lead in leads))


def value_by_stage(leads: list[LeadRecord]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for lead in leads:
        totals[lead.lead_stage] += lead.estimate_amount or 0
    return dict(totals)


def overdue_by_rep(leads: list[LeadRecord]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for lead in leads:
        if lead.followup_status == "Overdue" and lead.lead_stage in ACTIVE_STAGES:
            counts[lead.assigned_rep or "Unassigned"] += 1
    return dict(counts)


def manager_attention_flags(leads: list[LeadRecord], today: date | None = None) -> list[AttentionItem]:
    today = today or date.today()
    flags: list[AttentionItem] = []
    overdue_by_owner = overdue_by_rep(leads)
    for lead in leads:
        if lead.followup_status == "Overdue" and lead.priority == "High Priority":
            flags.append(
                AttentionItem(
                    lead.lead_id,
                    f"{lead.customer_name} is overdue and high priority",
                    "High-priority overdue follow-up needs same-day manager attention.",
                    "High",
                )
            )
        if (
            lead.lead_stage in ACTIVE_STAGES
            and (lead.estimate_amount or 0) >= 10000
            and lead.last_contact_date
            and (today - lead.last_contact_date).days >= 5
        ):
            flags.append(
                AttentionItem(
                    lead.lead_id,
                    f"{lead.customer_name} has a large estimate with stale contact",
                    "Large estimate has not had recent contact in five or more days.",
                    "High",
                )
            )
        if lead.lead_stage == "Decision Pending":
            flags.append(
                AttentionItem(
                    lead.lead_id,
                    f"{lead.customer_name} is decision pending",
                    "Decision-stage leads should have a clear next step and follow-up owner.",
                    "Medium",
                )
            )
        missing = []
        if not lead.customer_name:
            missing.append("customer")
        if not lead.assigned_rep:
            missing.append("rep")
        if not lead.context_notes:
            missing.append("context")
        if missing:
            flags.append(
                AttentionItem(
                    lead.lead_id,
                    f"{lead.lead_id} is missing required information",
                    f"Missing {', '.join(missing)} information may reduce follow-up quality.",
                    "Medium",
                )
            )
    for rep, count in overdue_by_owner.items():
        if count >= 2:
            flags.append(
                AttentionItem(
                    f"rep:{rep}",
                    f"{rep} has {count} overdue follow-ups",
                    "Multiple overdue follow-ups may indicate a coaching or workload issue.",
                    "High",
                )
            )
    return flags
