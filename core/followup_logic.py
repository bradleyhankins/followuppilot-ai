from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from core.models import FollowupPlan, GeneratedCopy, LeadInput

ACTIVE_STAGES = {"New Lead", "Contacted", "Appointment Set", "Estimate Sent", "Decision Pending"}


def value_statement(service_type: str) -> str:
    return {
        "Roof Replacement": "protecting the home from leaks, storm damage, and long-term structural issues",
        "Roof Repair": "stopping the current issue before it turns into a larger problem",
        "Siding": "protecting the wall system, improving curb appeal, and reducing maintenance concerns",
        "Gutters": "moving water away from the home to protect fascia, foundation, and landscaping",
        "Windows": "improving comfort, energy efficiency, and curb appeal",
        "HVAC": "improving comfort, reliability, and energy performance",
        "Plumbing Repair": "protecting the property from water damage and restoring reliability",
        "Electrical Service": "improving safety, reliability, and code-ready electrical performance",
        "Crawlspace Work": "protecting the home from moisture, air-quality, and structural concerns",
        "Pest Control": "protecting the home and preventing the issue from spreading",
        "Home Inspection": "giving the customer a clear understanding of condition, risk, and next steps",
        "Remodeling Consultation": "helping the customer plan scope, budget, timeline, and confidence",
        "General Home Service": "protecting the home and creating a clear path forward",
        "Other": "making sure the project is handled correctly",
    }.get(service_type, "making sure the project is handled correctly")


def calculate_priority(
    lead_status: str,
    urgency: str,
    financing: str,
    objection: str,
    project_type: str,
    days_since: int,
    intensity: str,
) -> tuple[str, str, int]:
    stage = LeadInput.from_mapping({"lead_status": lead_status}).lead_stage
    if stage == "Closed Lost":
        return "No Active Follow-Up", "No active follow-up recommended", 0
    if stage == "Won":
        return "Customer Won", "No active sales follow-up", 0

    score = 0
    score += {
        "New Lead": 2,
        "Contacted": 2,
        "Appointment Set": 2,
        "Estimate Sent": 3,
        "Decision Pending": 3,
    }.get(stage, 1)
    score += {"Low": 1, "Medium": 2, "High": 3}.get(urgency, 1)
    score += 1 if financing == "Yes" else 0
    score += 1 if objection != "None" else 0
    score += 1 if project_type in {"Roof Replacement", "Roof Repair", "Siding", "Gutters"} else 0
    score += 2 if days_since >= 7 else 1 if days_since >= 3 else 0
    score += 1 if intensity in {"Persistent", "Last Attempt"} else 0

    if score >= 9:
        return "High Priority", "Follow up today", score
    if score >= 6:
        return "Medium Priority", "Follow up within 24 hours", score
    return "Low Priority", "Follow up within 48-72 hours", score


def get_lead_temperature(priority: str, lead_status: str, days_since: int) -> str:
    stage = LeadInput.from_mapping({"lead_status": lead_status}).lead_stage
    if stage == "Closed Lost":
        return "Inactive"
    if stage == "Won":
        return "Won"
    if stage == "Decision Pending" or (priority == "High Priority" and days_since <= 3):
        return "Hot"
    if priority in {"High Priority", "Medium Priority"}:
        return "Warm"
    return "Cool"


def get_deal_risk(objection: str, days_since: int, lead_status: str) -> tuple[str, str]:
    stage = LeadInput.from_mapping({"lead_status": lead_status}).lead_stage
    if stage == "Closed Lost":
        return "Inactive", "Closed-lost status"
    if stage == "Won":
        return "Low", "Won status"
    if days_since >= 7:
        return "High", "No recent contact"
    if objection in {"Price", "Getting Other Quotes", "Financing"}:
        return "Medium", f"{objection} resistance"
    if objection in {"Spouse / Decision Maker", "Need to Think About It", "Timing"}:
        return "Medium", f"{objection} delay"
    return "Low", "No major risk identified"


def suggest_followup_date(lead: LeadInput, priority: str, today: date | None = None) -> date | None:
    """Return the next suggested contact date using readable, deterministic rules."""
    today = today or date.today()
    if lead.lead_stage == "Closed Lost" and lead.followup_intensity != "Last Attempt":
        return None
    if lead.lead_stage == "Won":
        return None

    stage_days = {
        "New Lead": 0,
        "Contacted": 1,
        "Appointment Set": 1,
        "Estimate Sent": 1,
        "Decision Pending": 0,
    }.get(lead.lead_stage, 2)
    urgency_adjustment = {"High": -1, "Medium": 0, "Low": 1}.get(lead.urgency, 0)
    intensity_adjustment = {
        "Persistent": -1,
        "Last Attempt": 0,
        "Standard": 0,
        "Light Touch": 2,
    }.get(lead.followup_intensity, 0)
    priority_adjustment = -1 if priority == "High Priority" else 0

    wait_days = max(0, stage_days + urgency_adjustment + intensity_adjustment + priority_adjustment)
    return today + timedelta(days=wait_days)


def followup_status(
    suggested_date: date | None,
    today: date | None = None,
) -> tuple[str, bool, bool, bool, int]:
    today = today or date.today()
    if suggested_date is None:
        return "No active follow-up", False, False, False, 0
    if suggested_date < today:
        return f"Overdue by {(today - suggested_date).days} day(s)", True, False, False, (
            today - suggested_date
        ).days
    if suggested_date == today:
        return "Due today", False, True, False, 0
    return "Upcoming follow-up", False, False, True, 0


def next_best_action(inputs: dict[str, Any], priority: str, deal_risk: str | None = None) -> str:
    lead = LeadInput.from_mapping(inputs)
    if lead.lead_stage == "Closed Lost":
        if lead.followup_intensity == "Last Attempt":
            return "Send one respectful close-the-loop or reactivation message, then pause active sales follow-up."
        return "No active sales follow-up recommended. Keep the lead closed unless the customer re-engages or a nurture campaign is explicitly selected."
    if lead.lead_stage == "Won":
        return "Do not run active sales follow-up. Move to onboarding, production handoff, project kickoff, or customer care."

    channel_actions = {
        "Phone Call": "Call first and document the outcome in the CRM.",
        "Text": "Send a concise text that asks for one clear next step.",
        "Email": "Send a recap email with decision points and a clear next step.",
        "Voicemail": "Leave a short voicemail, then send a matching text recap.",
        "CRM Note": "Do not contact the customer from this action. Add a clear CRM note and assign the next owner.",
        "All": "Send a text and email, then call if there is no response.",
    }
    action = channel_actions.get(lead.preferred_channel, channel_actions["All"])
    if priority == "High Priority" and lead.preferred_channel not in {"Phone Call", "CRM Note"}:
        action += " Because this is high priority, add a same-day call attempt."
    if deal_risk == "High":
        action += " Address the risk directly before momentum drops further."

    extras = {
        "Price": " Rebuild value before discussing any pricing change.",
        "Spouse / Decision Maker": " Offer to review the decision with both decision-makers.",
        "Financing": " Revisit payment options and clarify what part of financing is the concern.",
        "Getting Other Quotes": " Help the customer compare scope, warranty, timeline, and trust instead of price alone.",
    }
    action += extras.get(lead.objection, "")
    if lead.days_since_last_contact >= 7 or lead.followup_intensity == "Last Attempt":
        action += " Use a polite close-the-loop frame so the opportunity does not stay open indefinitely."
    return action


def tone_opener(tone: str, greeting: str, company: str, service_type: str) -> str:
    options = {
        "Friendly": f"{greeting} this is a quick follow-up from {company}.",
        "Professional": f"{greeting} this is a follow-up from {company} regarding your {service_type.lower()} project.",
        "Urgent": f"{greeting} I wanted to follow up quickly so we can keep your {service_type.lower()} project moving.",
        "Direct": f"{greeting} checking in from {company}.",
        "Consultative": f"{greeting} I wanted to follow up and help you think through the best next step for your {service_type.lower()} project.",
        "Reassuring": f"{greeting} I wanted to check in and make sure you feel comfortable with the next step for your {service_type.lower()} project.",
        "High-Confidence": f"{greeting} I wanted to follow up because this is the right time to keep your {service_type.lower()} project moving forward.",
        "No-Pressure": f"{greeting} no pressure at all - I just wanted to follow up from {company} and see what questions you still have.",
    }
    return options.get(tone, options["Professional"])


def build_text_message(inputs: dict[str, Any]) -> str:
    lead = LeadInput.from_mapping(inputs)
    customer = lead.customer_name or "there"
    company = lead.company_name or "our team"
    if lead.lead_stage == "Closed Lost":
        return f"Hi {customer}, thank you again for considering {company}. I will pause active follow-up for now, but if anything changes with your {lead.service_type.lower()} project, I would be glad to help."
    if lead.lead_stage == "Won":
        return f"Hi {customer}, thank you for choosing {company}. I will make sure the next step for your {lead.service_type.lower()} project is clear."

    status_line = {
        "New Lead": "I wanted to help get the next step scheduled and learn more about what you are needing.",
        "Contacted": "I wanted to reconnect and make sure your questions were answered.",
        "Appointment Set": "I wanted to confirm we are still good for the appointment and answer any questions before we come out.",
        "Estimate Sent": "I wanted to confirm you received the estimate and see if there is anything I can clarify.",
        "Decision Pending": "I wanted to help get the final decision point clear so we can keep everything moving.",
    }.get(lead.lead_stage, "I wanted to check in and help with the next step.")
    objection_line = (
        f" I know {lead.objection.lower()} was one of the things you were thinking through, and I am happy to help make that clearer."
        if lead.objection != "None"
        else ""
    )
    close = {
        "Last Attempt": "Should I keep this active for you, or would it be better for me to close out my follow-up for now?",
        "Persistent": "Can we set a quick time today to make a clear yes/no decision on the next step?",
    }.get(lead.followup_intensity, "Would you like me to help you review the next step?")
    return f"{tone_opener(lead.tone, f'Hi {customer},', company, lead.service_type)} {status_line}{objection_line} The goal is really about {value_statement(lead.service_type)}. {close}"


def build_email(inputs: dict[str, Any]) -> tuple[str, str]:
    lead = LeadInput.from_mapping(inputs)
    customer = lead.customer_name or "there"
    company = lead.company_name or "our team"
    if lead.lead_stage == "Closed Lost":
        return (
            f"Closing the Loop on Your {lead.service_type} Project",
            f"Hi {customer},\n\nThank you again for considering {company}. I will pause active follow-up for now. If anything changes or you would like to revisit the project later, I would be glad to help.\n\nThanks again,\n{company}",
        )
    if lead.lead_stage == "Won":
        return (
            f"Next Step for Your {lead.service_type} Project",
            f"Hi {customer},\n\nThank you for choosing {company}. I wanted to make sure the next step for your {lead.service_type.lower()} project is clear and easy to track.\n\nThanks again,\n{company}",
        )

    subject = f"Following Up on Your {lead.service_type} Project"
    body = f"Hi {customer},\n\nI wanted to follow up regarding your {lead.service_type.lower()} project and see what questions you may have.\n\nThe main goal is {value_statement(lead.service_type)}."
    if lead.objection != "None":
        body += f"\n\nI know you mentioned {lead.objection.lower()}. That is understandable. My goal is not to pressure you, but to help make the decision clearer."
    if lead.financing == "Yes":
        body += "\n\nWe can also revisit the payment options if that would make the project easier to plan around."
    body += f"\n\nWould it be helpful for me to walk you through the next step or answer any remaining questions?\n\nThanks again,\n{company}"
    return subject, body


def build_voicemail(inputs: dict[str, Any]) -> str:
    lead = LeadInput.from_mapping(inputs)
    if lead.lead_stage == "Closed Lost":
        return "No active voicemail recommended for a closed-lost lead unless reactivation is intentionally selected."
    return f"Hi {lead.customer_name or 'there'}, this is {lead.company_name or 'our team'}. I was calling to follow up on your {lead.service_type.lower()} project. I will send you a quick text as well, but I wanted to see if you had any questions or if you would like to review the next step. You can call or text me back whenever you get a chance. Thanks."


def objection_guidance(objection: str) -> str:
    return {
        "Price": "Rebuild value before discounting. Clarify scope, warranty, risk, financing, install quality, and cost of waiting.",
        "Need to Think About It": "Ask what specifically they need to think through. Turn vague delay into a clear concern.",
        "Getting Other Quotes": "Clarify what they are comparing: scope, warranty, install quality, timeline, payment options, and trust.",
        "Spouse / Decision Maker": "Offer to recap the project for both decision-makers and schedule a short review conversation.",
        "Timing": "Clarify whether timing means budget, schedule, urgency, or uncertainty. Offer a realistic next-step plan.",
        "Financing": "Clarify whether the issue is approval, monthly payment, APR, term, or total project cost.",
        "Other": "Ask a clarifying question to uncover the real concern, then guide the customer toward a clear next step.",
        "None": "Keep the follow-up simple. Confirm questions, restate the next step, and ask for a clear decision.",
    }.get(objection, "Ask a clarifying question to uncover the real concern.")


def manager_note(objection: str, priority: str) -> str:
    urgency = {
        "High Priority": "This lead should be treated as active pipeline and followed up today.",
        "Medium Priority": "This lead should be followed up within 24 hours before momentum drops.",
        "Low Priority": "This lead can be followed up within 48-72 hours, but should not be ignored.",
        "No Active Follow-Up": "This lead is closed lost and should not receive active sales follow-up by default.",
        "Customer Won": "This customer should move to onboarding, production handoff, project kickoff, or customer care.",
    }.get(priority, "Review and assign a clear next step.")
    return f"{urgency} Coach the rep to clarify the true concern, rebuild value, and secure a specific next step when active follow-up is appropriate."


def followup_sequence(inputs: dict[str, Any]) -> dict[str, str]:
    lead = LeadInput.from_mapping(inputs)
    customer = lead.customer_name or "there"
    service_type = lead.service_type.lower()
    if lead.lead_stage == "Closed Lost":
        return {
            "Closed Lost": "Pause active sales follow-up. Reactivate only if the customer re-engages or a nurture path is intentionally selected."
        }
    if lead.lead_stage == "Won":
        return {
            "Non-Sales Handoff": "Confirm onboarding, production handoff, project kickoff, or customer care ownership."
        }
    if lead.followup_intensity == "Light Touch":
        return {
            "Touch 1: Today - Text": "Send a light check-in text.",
            "Touch 2: Day 3 - Email": "Send a helpful recap email.",
            "Touch 3: Day 7 - Text": "Close the loop gently if there is no response.",
        }
    if lead.followup_intensity == "Last Attempt":
        return {
            "Touch 1: Today - Call + Text": "Try one direct call and a close-the-loop text.",
            "Touch 2: Final Check-In": "Pause follow-up unless the customer re-engages.",
        }
    return {
        "Touch 1: Today - Text + Call": f"Text and call {customer} about the {service_type} project.",
        "Touch 2: Tomorrow - Email": "Send a recap email with value and next step.",
        "Touch 3: Day 3 - Value Reminder": "Reframe the project around the customer's main goal.",
        "Touch 4: Day 7 - Final Check-In": "Ask whether to keep the project active or pause follow-up.",
    }


def build_crm_note(
    inputs: dict[str, Any],
    priority: str,
    timing: str,
    temperature: str,
    risk: str,
    main_risk: str,
    next_action: str,
    suggested_date: date | None = None,
    status: str = "",
) -> str:
    lead = LeadInput.from_mapping(inputs)
    amount = f"${lead.estimate_amount:,.2f}" if lead.estimate_amount is not None else "N/A"
    return (
        f"Customer: {lead.customer_name or 'N/A'}\n"
        f"Company: {lead.company_name or 'N/A'}\n"
        f"Assigned Rep: {lead.assigned_rep or 'N/A'}\n"
        f"Service Type: {lead.service_type}\n"
        f"Current Stage: {lead.lead_stage}\n"
        f"Estimate Amount: {amount}\n"
        f"Lead Temperature: {temperature}\n"
        f"Deal Risk: {risk}\n"
        f"Main Risk: {main_risk}\n"
        f"Priority: {priority}\n"
        f"Urgency Level: {lead.urgency}\n"
        f"Last Contact Date: {lead.last_contact_date.isoformat() if lead.last_contact_date else 'N/A'}\n"
        f"Days Since Last Contact: {lead.days_since_last_contact}\n"
        f"Suggested Follow-Up Date: {suggested_date.isoformat() if suggested_date else 'N/A'}\n"
        f"Follow-Up Status: {status or 'N/A'}\n"
        f"Last Interaction: {lead.context_notes or 'Not provided'}\n"
        f"Primary Concern/Objection: {lead.objection}\n"
        f"Financing Discussed: {lead.financing}\n"
        f"Recommended Next Step: {timing}\n"
        f"Next Best Action: {next_action}\n"
        "CRM Action: Follow up using generated workflow and update disposition after customer response."
    )


def build_call_script(inputs: dict[str, Any]) -> str:
    lead = LeadInput.from_mapping(inputs)
    if lead.lead_stage == "Closed Lost":
        return "No active sales call script recommended for a closed-lost lead."
    return f"Opening:\nHi, is this {lead.customer_name or 'the customer'}? This is following up about your {lead.service_type.lower()} project.\n\nReason for call:\nI wanted to reconnect and help with the next step.\n\nDiscovery question:\nWhat is the main thing you are still trying to decide or feel comfortable with?\n\nValue reminder:\nThe main goal is {value_statement(lead.service_type)}.\n\nClose:\nWould it make sense to review the next step together while I have you?"


def run_followup_workflow(inputs: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    lead = LeadInput.from_mapping(inputs)
    workflow_inputs = lead.to_workflow_dict()
    priority, timing, score = calculate_priority(
        lead.lead_stage,
        lead.urgency,
        lead.financing,
        lead.objection,
        lead.service_type,
        lead.days_since_last_contact,
        lead.followup_intensity,
    )
    temperature = get_lead_temperature(priority, lead.lead_stage, lead.days_since_last_contact)
    deal_risk, main_risk = get_deal_risk(
        lead.objection, lead.days_since_last_contact, lead.lead_stage
    )
    suggested_date = suggest_followup_date(lead, priority, today=today)
    status, is_overdue, due_today, upcoming, days_overdue = followup_status(
        suggested_date, today=today
    )
    if lead.lead_stage == "Won":
        status = "No Active Sales Follow-Up"
        is_overdue = False
        due_today = False
        upcoming = False
        days_overdue = 0
    next_action = next_best_action(workflow_inputs, priority, deal_risk)
    if lead.lead_stage == "Closed Lost":
        why = "This lead is Closed Lost, so active sales follow-up is paused unless reactivation is explicitly selected."
    elif lead.lead_stage == "Won":
        why = "This lead is Won, so the recommended workflow shifts from sales follow-up to post-sale handoff."
    else:
        why = (
            f"This lead is marked {priority} with a score of {score} because the stage is "
            f"{lead.lead_stage}, urgency is {lead.urgency.lower()}, main concern is "
            f"{lead.objection.lower()}, and it has been {lead.days_since_last_contact} day(s) "
            "since last contact."
        )
    sms = build_text_message(workflow_inputs)
    subject, email = build_email(workflow_inputs)
    voicemail = build_voicemail(workflow_inputs)
    crm = build_crm_note(
        workflow_inputs,
        priority,
        timing,
        temperature,
        deal_risk,
        main_risk,
        next_action,
        suggested_date,
        status,
    )
    plan = FollowupPlan(
        priority=priority,
        timing=timing,
        score=score,
        temperature=temperature,
        deal_risk=deal_risk,
        main_risk=main_risk,
        next_action=next_action,
        why=why,
        suggested_followup_date=suggested_date,
        followup_status=status,
        days_overdue=days_overdue,
        is_overdue=is_overdue,
        due_today=due_today,
        upcoming_followup=upcoming,
        copy=GeneratedCopy(
            sms=sms,
            subject=subject,
            email=email,
            voicemail=voicemail,
            crm=crm,
            coaching=manager_note(lead.objection, priority),
        ),
        guidance=objection_guidance(lead.objection),
        sequence=followup_sequence(workflow_inputs),
        call=build_call_script(workflow_inputs),
    )
    return plan.to_dict()
