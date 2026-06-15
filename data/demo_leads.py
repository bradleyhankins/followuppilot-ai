from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta

from core.lead_store import refresh_lead_plan
from core.models import LeadRecord


def demo_leads(today: date | None = None) -> list[LeadRecord]:
    today = today or date.today()
    raw = [
        ("FUP-1001", "Avery Johnson", "Summit Home Services", "Roof Replacement", "Estimate Sent", "Mia Torres", 18400, "Price", "High", "Yes", "Consultative", "All", "Standard", 2, "Customer liked the roof plan but needs help understanding the price difference versus a smaller repair."),
        ("FUP-1002", "Morgan Ellis", "Summit Home Services", "Siding", "Decision Pending", "Eli Brooks", 12600, "Spouse / Decision Maker", "Medium", "No", "Reassuring", "Phone Call", "Persistent", 5, "Customer wants to review color, budget, and timing with their spouse before signing."),
        ("FUP-1003", "Jordan Miller", "Summit Home Services", "Gutters", "Estimate Sent", "Noor Patel", 3100, "Timing", "Medium", "No", "Direct", "Text", "Persistent", 4, "Estimate sent after heavy rain concerns. Customer has not responded since proposal review."),
        ("FUP-1004", "Taylor Brooks", "Summit Home Services", "Windows", "Estimate Sent", "Mia Torres", 9800, "Financing", "Medium", "Yes", "No-Pressure", "Email", "Light Touch", 1, "Customer likes the window package but wants clarity on monthly payment options."),
        ("FUP-1005", "Jamie Carter", "Summit Home Services", "HVAC", "New Lead", "Eli Brooks", 11200, "None", "High", "No", "Urgent", "Phone Call", "Standard", 0, "Customer requested a quote after the existing system stopped cooling reliably."),
        ("FUP-1006", "Riley Nguyen", "Summit Home Services", "Plumbing Repair", "Contacted", "Noor Patel", 1450, "Timing", "High", "No", "Professional", "Text", "Standard", 2, "Customer has an intermittent leak and needs help deciding whether to repair now."),
        ("FUP-1007", "Cameron Reed", "Summit Home Services", "Electrical Service", "Appointment Set", "Mia Torres", 2400, "None", "Medium", "No", "Professional", "Email", "Standard", 1, "Panel inspection is scheduled and customer asked what to expect during the visit."),
        ("FUP-1008", "Drew Morgan", "Summit Home Services", "Crawlspace Work", "Decision Pending", "Eli Brooks", 15200, "Need to Think About It", "Medium", "Yes", "Consultative", "All", "Persistent", 8, "Customer understands the moisture issue but is weighing budget and timeline."),
        ("FUP-1009", "Parker Sloan", "Summit Home Services", "Pest Control", "Contacted", "Noor Patel", 850, "Other", "Low", "No", "Friendly", "Voicemail", "Light Touch", 6, "Customer asked about recurring service after seeing activity near the garage."),
        ("FUP-1010", "Quinn Harper", "Summit Home Services", "Home Inspection", "Won", "Mia Torres", 625, "None", "Low", "No", "Professional", "CRM Note", "Standard", 3, "Customer approved the inspection and needs post-sale scheduling handoff."),
        ("FUP-1011", "Alex Monroe", "Summit Home Services", "Remodeling Consultation", "Closed Lost", "Eli Brooks", 22500, "Getting Other Quotes", "Low", "No", "No-Pressure", "CRM Note", "Standard", 14, "Customer selected another contractor after comparing remodeling scopes."),
        ("FUP-1012", "Skyler Chen", "Summit Home Services", "Roof Repair", "Estimate Sent", "Noor Patel", 4200, "Price", "High", "No", "Direct", "Text", "Persistent", 7, "Customer has an active leak and asked whether the repair can be staged."),
        ("FUP-1013", "Harper Lane", "Summit Home Services", "Gutters", "Decision Pending", "Mia Torres", 3600, "Getting Other Quotes", "Medium", "No", "Consultative", "Phone Call", "Standard", 5, "Customer is comparing gutter scope, guard options, and install timeline."),
        ("FUP-1014", "Reese Bennett", "Summit Home Services", "HVAC", "Estimate Sent", "Eli Brooks", 13400, "Financing", "High", "Yes", "Reassuring", "All", "Persistent", 6, "Customer needs replacement before peak heat and wants payment clarity."),
        ("FUP-1015", "Rowan Hayes", "Summit Home Services", "Siding", "New Lead", "Noor Patel", 0, "None", "Medium", "No", "Friendly", "Phone Call", "Standard", 0, "Customer submitted a request for siding options and wants an initial consultation."),
        ("FUP-1016", "Casey Rivera", "Summit Home Services", "Plumbing Repair", "Closed Lost", "Mia Torres", 900, "Timing", "Low", "No", "No-Pressure", "CRM Note", "Standard", 20, "Customer postponed the repair after a temporary fix held."),
        ("FUP-1017", "Emerson Gray", "Summit Home Services", "Electrical Service", "Contacted", "Eli Brooks", 6800, "Need to Think About It", "Medium", "No", "Professional", "Email", "Standard", 3, "Customer is reviewing a service-panel upgrade and asked for a written recap."),
        ("FUP-1018", "Finley Stone", "Summit Home Services", "Pest Control", "Won", "Noor Patel", 1200, "None", "Low", "No", "Friendly", "CRM Note", "Standard", 1, "Customer approved quarterly service and needs onboarding notes."),
    ]
    status_overrides = {
        "FUP-1001": (today, "Due Today"),
        "FUP-1002": (today - timedelta(days=2), "Overdue"),
        "FUP-1003": (today - timedelta(days=1), "Overdue"),
        "FUP-1005": (today, "Due Today"),
        "FUP-1008": (today - timedelta(days=3), "Overdue"),
        "FUP-1012": (today - timedelta(days=4), "Overdue"),
        "FUP-1014": (today - timedelta(days=1), "Overdue"),
        "FUP-1015": (today + timedelta(days=1), "Upcoming"),
    }
    leads: list[LeadRecord] = []
    for item in raw:
        (
            lead_id,
            customer,
            company,
            service_type,
            stage,
            rep,
            estimate,
            objection,
            urgency,
            financing,
            tone,
            channel,
            intensity,
            days_since,
            context,
        ) = item
        lead = LeadRecord.from_mapping(
            {
                "lead_id": lead_id,
                "customer_name": customer,
                "company_name": company,
                "service_type": service_type,
                "lead_stage": stage,
                "assigned_rep": rep,
                "estimate_amount": estimate,
                "context_notes": context,
                "objection": objection,
                "urgency": urgency,
                "financing": financing,
                "tone": tone,
                "preferred_channel": channel,
                "followup_intensity": intensity,
                "last_contact_date": (today - timedelta(days=days_since)).isoformat(),
                "created_date": (today - timedelta(days=days_since + 7)).isoformat(),
                "updated_date": (today - timedelta(days=max(days_since - 1, 0))).isoformat(),
            }
        )
        refreshed = refresh_lead_plan(lead, today=today)
        if lead_id in status_overrides and refreshed.lead_stage not in {"Won", "Closed Lost"}:
            suggested, status = status_overrides[lead_id]
            refreshed = replace(
                refreshed,
                suggested_followup_date=suggested,
                followup_status=status,
            )
        leads.append(refreshed)
    return leads
