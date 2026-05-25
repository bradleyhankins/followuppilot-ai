def value_statement(project_type: str) -> str:
    return {
        "Roof Replacement": "protecting the home from leaks, storm damage, and long-term structural issues",
        "Roof Repair": "stopping the current issue before it turns into a larger problem",
        "Siding": "protecting the wall system, improving curb appeal, and reducing maintenance concerns",
        "Gutters": "moving water away from the home to protect fascia, foundation, and landscaping",
        "Windows": "improving comfort, energy efficiency, and curb appeal",
        "HVAC": "improving comfort, reliability, and energy performance",
        "Pest Control": "protecting the home and preventing the issue from spreading",
        "General Home Service": "protecting the home and creating a clear path forward",
        "Other": "making sure the project is handled correctly",
    }.get(project_type, "making sure the project is handled correctly")


def calculate_priority(lead_status, urgency, financing, objection, project_type, days_since, intensity):
    score = 0
    score += 3 if lead_status in ["Estimate Presented", "Proposal Sent", "Verbal Yes / Pending Signature"] else 2 if lead_status in ["Inspection Completed", "Needs Follow-Up"] else 1
    score += {"Low": 1, "Medium": 2, "High": 3}.get(urgency, 1)
    score += 1 if financing == "Yes" else 0
    score += 1 if objection != "None" else 0
    score += 1 if project_type in ["Roof Replacement", "Roof Repair", "Siding", "Gutters"] else 0
    score += 2 if days_since >= 7 else 1 if days_since >= 3 else 0
    score += 1 if intensity in ["Persistent", "Last Attempt"] else 0
    if score >= 9:
        return "High Priority", "Follow up today", score
    if score >= 6:
        return "Medium Priority", "Follow up within 24 hours", score
    return "Low Priority", "Follow up within 48-72 hours", score


def get_lead_temperature(priority, lead_status, days_since):
    if lead_status == "Verbal Yes / Pending Signature" or (priority == "High Priority" and days_since <= 3):
        return "Hot"
    if priority in ["High Priority", "Medium Priority"]:
        return "Warm"
    return "Cool"


def get_deal_risk(objection, days_since, lead_status):
    if lead_status == "Closed Lost":
        return "High", "Closed-lost status"
    if days_since >= 7:
        return "High", "No recent contact"
    if objection in ["Price", "Getting Other Quotes", "Financing"]:
        return "Medium", f"{objection} resistance"
    if objection in ["Spouse / Decision Maker", "Need to Think About It", "Timing"]:
        return "Medium", f"{objection} delay"
    return "Low", "No major risk identified"


def next_best_action(inputs, priority, deal_risk):
    if inputs["channel"] == "Phone Call" or priority == "High Priority":
        action = "Call first, then send a short recap text."
    elif inputs["channel"] == "Text":
        action = "Send a concise text that asks for a clear next step."
    elif inputs["channel"] == "Email":
        action = "Send a recap email with the decision points and next step."
    else:
        action = "Send a text and email, then call if there is no response."

    extras = {
        "Price": " Rebuild value before discussing any pricing change.",
        "Spouse / Decision Maker": " Offer to review the decision with both decision-makers.",
        "Financing": " Revisit payment options and clarify what part of financing is the concern.",
        "Getting Other Quotes": " Help the customer compare scope, warranty, timeline, and trust instead of price alone.",
    }
    action += extras.get(inputs["objection"], "")
    if inputs["days_since"] >= 7 or inputs["intensity"] == "Last Attempt":
        action += " Use a polite close-the-loop message so the opportunity does not stay open indefinitely."
    return action


def tone_opener(tone, greeting, company, project_type):
    options = {
        "Friendly": f"{greeting} this is a quick follow-up from {company}.",
        "Professional": f"{greeting} this is a follow-up from {company} regarding your {project_type.lower()} project.",
        "Urgent": f"{greeting} I wanted to follow up quickly so we can keep your {project_type.lower()} project moving.",
        "Direct": f"{greeting} checking in from {company}.",
        "Consultative": f"{greeting} I wanted to follow up and help you think through the best next step for your {project_type.lower()} project.",
        "Reassuring": f"{greeting} I wanted to check in and make sure you feel comfortable with the next step for your {project_type.lower()} project.",
        "High-Confidence": f"{greeting} I wanted to follow up because this is the right time to keep your {project_type.lower()} project moving forward.",
        "No-Pressure": f"{greeting} no pressure at all — I just wanted to follow up from {company} and see what questions you still have.",
    }
    return options.get(tone, options["Professional"])


def build_text_message(inputs):
    customer = inputs["customer"] or "there"
    company = inputs["company"] or "our team"
    project_type = inputs["project_type"]
    status_line = {
        "New Lead": "I wanted to help get the next step scheduled and learn more about what you are needing.",
        "Inspection Scheduled": "I wanted to confirm we are still good for the appointment and answer any questions before we come out.",
        "Inspection Completed": "I wanted to check in after the appointment and make sure the recommended next steps were clear.",
        "Estimate Presented": "I wanted to see if you had any questions about the estimate, scope, or options we reviewed.",
        "Proposal Sent": "I wanted to confirm you received the proposal and see if there is anything I can clarify.",
        "Needs Follow-Up": "I wanted to reconnect and see what questions came up since we last spoke.",
        "Verbal Yes / Pending Signature": "I wanted to help get the final step wrapped up so we can keep everything moving.",
        "Closed Lost": "I wanted to thank you again for the opportunity. If anything changes, I would be happy to help.",
    }.get(inputs["lead_status"], "I wanted to check in and help with the next step.")
    objection_line = f" I know {inputs['objection'].lower()} was one of the things you were thinking through, and I am happy to help make that clearer." if inputs["objection"] != "None" else ""
    close = "Should I keep this active for you, or would it be better for me to close out my follow-up for now?" if inputs["intensity"] == "Last Attempt" else "Can we set a quick time today to make a clear yes/no decision on the next step?" if inputs["intensity"] == "Persistent" else "Would you like me to help you review the next step?"
    return f"{tone_opener(inputs['tone'], f'Hi {customer},', company, project_type)} {status_line}{objection_line} The goal is really about {value_statement(project_type)}. {close}"


def build_email(inputs):
    customer = inputs["customer"] or "there"
    company = inputs["company"] or "our team"
    project_type = inputs["project_type"]
    subject = f"Following Up on Your {project_type} Project"
    body = f"Hi {customer},\n\nI wanted to follow up regarding your {project_type.lower()} project and see what questions you may have.\n\nThe main goal is {value_statement(project_type)}."
    if inputs["objection"] != "None":
        body += f"\n\nI know you mentioned {inputs['objection'].lower()}. That is understandable. My goal is not to pressure you, but to help make the decision clearer."
    if inputs["financing"] == "Yes":
        body += "\n\nWe can also revisit the payment options if that would make the project easier to plan around."
    body += f"\n\nWould it be helpful for me to walk you through the next step or answer any remaining questions?\n\nThanks again,\n{company}"
    return subject, body


def build_voicemail(inputs):
    return f"Hi {inputs['customer'] or 'there'}, this is {inputs['company'] or 'our team'}. I was calling to follow up on your {inputs['project_type'].lower()} project. I will send you a quick text as well, but I wanted to see if you had any questions or if you would like to review the next step. You can call or text me back whenever you get a chance. Thanks."


def objection_guidance(objection):
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


def manager_note(objection, priority):
    urgency = {
        "High Priority": "This lead should be treated as active pipeline and followed up today.",
        "Medium Priority": "This lead should be followed up within 24 hours before momentum drops.",
        "Low Priority": "This lead can be followed up within 48-72 hours, but should not be ignored.",
    }.get(priority, "Review and assign a clear next step.")
    return f"{urgency} Coach the rep to clarify the true concern, rebuild value, and secure a specific next step."


def followup_sequence(inputs):
    customer = inputs["customer"] or "there"
    project_type = inputs["project_type"].lower()
    if inputs["intensity"] == "Light Touch":
        return {
            "Touch 1: Today — Text": "Send a light check-in text.",
            "Touch 2: Day 3 — Email": "Send a helpful recap email.",
            "Touch 3: Day 7 — Text": "Close the loop gently if there is no response.",
        }
    if inputs["intensity"] == "Last Attempt":
        return {
            "Touch 1: Today — Call + Text": "Try one direct call and a close-the-loop text.",
            "Touch 2: Final Check-In": "Pause follow-up unless the customer re-engages.",
        }
    return {
        "Touch 1: Today — Text + Call": f"Text and call {customer} about the {project_type} project.",
        "Touch 2: Tomorrow — Email": "Send a recap email with value and next step.",
        "Touch 3: Day 3 — Value Reminder": "Reframe the project around the customer’s main goal.",
        "Touch 4: Day 7 — Final Check-In": "Ask whether to keep the project active or pause follow-up.",
    }


def build_crm_note(inputs, priority, timing, temperature, risk, main_risk, next_action):
    return f"Customer: {inputs['customer'] or 'N/A'}\nCompany: {inputs['company'] or 'N/A'}\nProject Type: {inputs['project_type']}\nCurrent Status: {inputs['lead_status']}\nLead Temperature: {temperature}\nDeal Risk: {risk}\nMain Risk: {main_risk}\nPriority: {priority}\nUrgency Level: {inputs['urgency']}\nDays Since Last Contact: {inputs['days_since']}\nLast Interaction: {inputs['context'] or 'Not provided'}\nPrimary Concern/Objection: {inputs['objection']}\nFinancing Discussed: {inputs['financing']}\nRecommended Next Step: {timing}\nNext Best Action: {next_action}\nCRM Action: Follow up using generated workflow and update disposition after customer response."


def build_call_script(inputs):
    return f"Opening:\nHi, is this {inputs['customer'] or 'the customer'}? This is following up about your {inputs['project_type'].lower()} project.\n\nReason for call:\nI wanted to reconnect and help with the next step.\n\nDiscovery question:\nWhat is the main thing you are still trying to decide or feel comfortable with?\n\nValue reminder:\nThe main goal is {value_statement(inputs['project_type'])}.\n\nClose:\nWould it make sense to review the next step together while I have you?"


def run_followup_workflow(inputs):
    priority, timing, score = calculate_priority(inputs["lead_status"], inputs["urgency"], inputs["financing"], inputs["objection"], inputs["project_type"], inputs["days_since"], inputs["intensity"])
    temperature = get_lead_temperature(priority, inputs["lead_status"], inputs["days_since"])
    deal_risk, main_risk = get_deal_risk(inputs["objection"], inputs["days_since"], inputs["lead_status"])
    next_action = next_best_action(inputs, priority, deal_risk)
    why = f"This lead is marked {priority} with a score of {score} because the status is {inputs['lead_status']}, urgency is {inputs['urgency'].lower()}, main concern is {inputs['objection'].lower()}, and it has been {inputs['days_since']} day(s) since last contact."
    sms = build_text_message(inputs)
    subject, email = build_email(inputs)
    voicemail = build_voicemail(inputs)
    crm = build_crm_note(inputs, priority, timing, temperature, deal_risk, main_risk, next_action)
    return {
        "priority": priority,
        "timing": timing,
        "score": score,
        "temperature": temperature,
        "deal_risk": deal_risk,
        "main_risk": main_risk,
        "next_action": next_action,
        "why": why,
        "sms": sms,
        "subject": subject,
        "email": email,
        "voicemail": voicemail,
        "guidance": objection_guidance(inputs["objection"]),
        "coaching": manager_note(inputs["objection"], priority),
        "sequence": followup_sequence(inputs),
        "crm": crm,
        "call": build_call_script(inputs),
    }
