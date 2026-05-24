import streamlit as st

# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------

st.set_page_config(page_title="FollowUpPilot AI", page_icon="💬", layout="wide")

# -----------------------------------------------------------------------------
# App options and sample scenarios
# -----------------------------------------------------------------------------

PROJECT_TYPES = [
    "Roof Replacement",
    "Roof Repair",
    "Siding",
    "Gutters",
    "Windows",
    "HVAC",
    "Pest Control",
    "General Home Service",
    "Other",
]

LEAD_STATUSES = [
    "New Lead",
    "Inspection Scheduled",
    "Inspection Completed",
    "Estimate Presented",
    "Proposal Sent",
    "Needs Follow-Up",
    "Verbal Yes / Pending Signature",
    "Closed Lost",
]

OBJECTIONS = [
    "None",
    "Price",
    "Need to Think About It",
    "Getting Other Quotes",
    "Spouse / Decision Maker",
    "Timing",
    "Financing",
    "Other",
]

TONES = [
    "Friendly",
    "Professional",
    "Urgent",
    "Direct",
    "Consultative",
    "Reassuring",
    "High-Confidence",
    "No-Pressure",
]

URGENCY_LEVELS = ["Low", "Medium", "High"]
FINANCING_OPTIONS = ["No", "Yes"]
FOLLOWUP_INTENSITIES = ["Light Touch", "Standard", "Persistent", "Last Attempt"]
CHANNEL_OPTIONS = ["All", "Text", "Email", "Phone Call", "Voicemail", "CRM Note"]

SAMPLE_SCENARIOS = {
    "Blank / Custom": {},
    "Price Objection": {
        "customer": "Avery Johnson",
        "company": "Summit Home Services",
        "project_type": "Roof Replacement",
        "lead_status": "Estimate Presented",
        "context": "Customer liked the project plan but said the price was higher than expected and wanted to review options before making a decision.",
        "objection": "Price",
        "financing": "Yes",
        "urgency": "High",
        "tone": "Consultative",
        "days_since": 1,
        "intensity": "Standard",
        "channel": "All",
    },
    "Needs Spouse Approval": {
        "customer": "Morgan Ellis",
        "company": "Summit Home Services",
        "project_type": "Siding",
        "lead_status": "Proposal Sent",
        "context": "Customer liked the siding option but said they needed to review the color, budget, and timeline with their spouse before moving forward.",
        "objection": "Spouse / Decision Maker",
        "financing": "No",
        "urgency": "Medium",
        "tone": "Reassuring",
        "days_since": 2,
        "intensity": "Standard",
        "channel": "All",
    },
    "Proposal Sent / No Response": {
        "customer": "Jordan Miller",
        "company": "Summit Home Services",
        "project_type": "Gutters",
        "lead_status": "Proposal Sent",
        "context": "Proposal was sent four days ago. Customer has not responded yet. The project was originally described as important before the next heavy rain.",
        "objection": "Timing",
        "financing": "No",
        "urgency": "Medium",
        "tone": "Direct",
        "days_since": 4,
        "intensity": "Persistent",
        "channel": "All",
    },
    "Financing Concern": {
        "customer": "Taylor Brooks",
        "company": "Summit Home Services",
        "project_type": "Windows",
        "lead_status": "Estimate Presented",
        "context": "Customer wants the project completed but was unsure about monthly payment options and total project cost.",
        "objection": "Financing",
        "financing": "Yes",
        "urgency": "Medium",
        "tone": "No-Pressure",
        "days_since": 1,
        "intensity": "Light Touch",
        "channel": "All",
    },
}

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
.block-container { max-width: 1180px; padding-top: 1.35rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #111827; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] li,[data-testid="stSidebar"] ul,[data-testid="stSidebar"] ol { color: #f9fafb !important; }
[data-testid="stSidebar"] li::marker { color: #93c5fd !important; }
.hero { padding: 1.9rem 2rem; border-radius: 20px; background: linear-gradient(135deg, #111827 0%, #1f2937 52%, #334155 100%); color: #ffffff; box-shadow: 0 18px 36px rgba(17, 24, 39, .18); margin-bottom: 1rem; border: 1px solid rgba(255, 255, 255, .08); }
.eyebrow { text-transform: uppercase; letter-spacing: .13em; font-size: .75rem; font-weight: 800; color: #93c5fd; margin-bottom: .65rem; }
.hero-title { font-size: 2.25rem; line-height: 1.08; font-weight: 850; margin-bottom: .65rem; }
.hero-subtitle { font-size: 1.02rem; line-height: 1.62; color: #e5e7eb; max-width: 900px; }
.hero-pills span { display: inline-block; padding: .35rem .65rem; margin: .75rem .28rem 0 0; border-radius: 999px; background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.16); font-weight: 700; font-size: .78rem; color: #f8fafc; }
.section-title { margin-top: 1.25rem; margin-bottom: .55rem; font-size: 1.4rem; font-weight: 850; color: #111827; }
.section-lede { color: #4b5563; line-height: 1.6; margin-bottom: 1rem; max-width: 950px; }
.form-group-title { font-size: .9rem; font-weight: 850; text-transform: uppercase; letter-spacing: .06em; color: #64748b; margin: .35rem 0 .15rem 0; }
.metric-card,.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 18px; box-shadow: 0 8px 20px rgba(15, 23, 42, .055); }
.metric-card { height: 138px; padding: 1rem; margin-bottom: .75rem; }
.metric-label { color: #6b7280; font-size: .78rem; font-weight: 800; text-transform: uppercase; letter-spacing: .05em; margin-bottom: .5rem; }
.metric-value { color: #111827; font-size: 1.35rem; line-height: 1.18; font-weight: 900; overflow-wrap: break-word; }
.metric-note { color: #64748b; font-size: .85rem; margin-top: .55rem; }
.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card { padding: 1.15rem; margin-bottom: .8rem; }
.output-card { border-left: 5px solid #111827; }
.guidance-card { border-left: 5px solid #1d4ed8; }
.sequence-card { border-left: 5px solid #059669; }
.workflow-card { border-left: 5px solid #1d4ed8; }
.nba-card { border-left: 5px solid #111827; background: #f8fafc; }
.output-card h3,.guidance-card h3,.sequence-card h3,.workflow-card h3,.nba-card h3 { font-size: 1.05rem; font-weight: 850; color: #111827; margin-bottom: .4rem; }
.output-card p,.guidance-card p,.sequence-card p,.workflow-card p,.nba-card p,.output-card li,.guidance-card li,.sequence-card li,.workflow-card li,.nba-card li { color: #4b5563; line-height: 1.52; font-size: .93rem; }
.status-high { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.status-medium { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.status-low { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
.status-pill { display: inline-block; padding: .25rem .6rem; border-radius: 999px; font-weight: 850; font-size: .78rem; margin-bottom: .5rem; }
.note-box { padding: .9rem 1rem; border-radius: 14px; background: #f8fafc; color: #334155; border: 1px solid #e2e8f0; font-weight: 650; margin: .9rem 0; font-size: .92rem; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# UI helpers
# -----------------------------------------------------------------------------


def section_title(title: str, lede: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<div class="section-lede">{lede}</div>', unsafe_allow_html=True)


def form_group(title: str) -> None:
    st.markdown(f'<div class="form-group-title">{title}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, note: str | None = None) -> None:
    note_html = f'<div class="metric-note">{note}</div>' if note else ""
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{note_html}</div>', unsafe_allow_html=True)


def html_card(title: str, body: str, css_class: str = "output-card") -> None:
    st.markdown(f'<div class="{css_class}"><h3>{title}</h3>{body}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Business logic
# -----------------------------------------------------------------------------


def value_statement(project_type: str) -> str:
    values = {
        "Roof Replacement": "protecting the home from leaks, storm damage, and long-term structural issues",
        "Roof Repair": "stopping the current issue before it turns into a larger problem",
        "Siding": "protecting the wall system, improving curb appeal, and reducing maintenance concerns",
        "Gutters": "moving water away from the home to protect fascia, foundation, and landscaping",
        "Windows": "improving comfort, energy efficiency, and curb appeal",
        "HVAC": "improving comfort, reliability, and energy performance",
        "Pest Control": "protecting the home and preventing the issue from spreading",
        "General Home Service": "protecting the home and creating a clear path forward",
        "Other": "making sure the project is handled correctly",
    }
    return values.get(project_type, values["Other"])


def calculate_priority(lead_status: str, urgency: str, financing: str, objection: str, project_type: str, days_since: int, intensity: str) -> tuple[str, str, int]:
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


def priority_class(priority: str) -> str:
    if priority == "High Priority":
        return "status-high"
    if priority == "Medium Priority":
        return "status-medium"
    return "status-low"


def get_lead_temperature(priority: str, lead_status: str, days_since: int) -> str:
    if lead_status == "Verbal Yes / Pending Signature":
        return "Hot"
    if priority == "High Priority" and days_since <= 3:
        return "Hot"
    if priority in ["High Priority", "Medium Priority"]:
        return "Warm"
    return "Cool"


def get_deal_risk(objection: str, days_since: int, lead_status: str) -> tuple[str, str]:
    if lead_status == "Closed Lost":
        return "High", "Closed-lost status"
    if days_since >= 7:
        return "High", "No recent contact"
    if objection in ["Price", "Getting Other Quotes", "Financing"]:
        return "Medium", f"{objection} resistance"
    if objection in ["Spouse / Decision Maker", "Need to Think About It", "Timing"]:
        return "Medium", f"{objection} delay"
    return "Low", "No major risk identified"


def next_best_action(inputs: dict, priority: str, deal_risk: str) -> str:
    channel = inputs["channel"]
    objection = inputs["objection"]
    days_since = inputs["days_since"]
    intensity = inputs["intensity"]

    if channel == "Phone Call" or priority == "High Priority":
        action = "Call first, then send a short recap text."
    elif channel == "Text":
        action = "Send a concise text that asks for a clear next step."
    elif channel == "Email":
        action = "Send a recap email with the decision points and next step."
    else:
        action = "Send a text and email, then call if there is no response."

    if objection == "Price":
        action += " Rebuild value before discussing any pricing change."
    elif objection == "Spouse / Decision Maker":
        action += " Offer to review the decision with both decision-makers."
    elif objection == "Financing":
        action += " Revisit payment options and clarify what part of financing is the concern."
    elif objection == "Getting Other Quotes":
        action += " Help the customer compare scope, warranty, timeline, and trust instead of price alone."

    if days_since >= 7 or intensity == "Last Attempt":
        action += " Use a polite close-the-loop message so the opportunity does not stay open indefinitely."

    return action


def why_recommendation(inputs: dict, priority: str, score: int, deal_risk: str, main_risk: str) -> str:
    return (
        f"This lead is marked {priority} with a score of {score} because the status is {inputs['lead_status']}, "
        f"urgency is {inputs['urgency'].lower()}, the main concern is {inputs['objection'].lower()}, "
        f"and it has been {inputs['days_since']} day(s) since last contact. Deal risk is {deal_risk.lower()} due to {main_risk.lower()}."
    )


def tone_opener(tone: str, greeting: str, company: str, project_type: str) -> str:
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


def build_text_message(inputs: dict) -> str:
    customer = inputs["customer"] or "there"
    company = inputs["company"] or "our team"
    project_type = inputs["project_type"]
    lead_status = inputs["lead_status"]
    objection = inputs["objection"]
    tone = inputs["tone"]
    intensity = inputs["intensity"]

    greeting = f"Hi {customer},"
    opener = tone_opener(tone, greeting, company, project_type)

    status_line = {
        "New Lead": "I wanted to help get the next step scheduled and learn more about what you are needing.",
        "Inspection Scheduled": "I wanted to confirm we are still good for the appointment and answer any questions before we come out.",
        "Inspection Completed": "I wanted to check in after the appointment and make sure the recommended next steps were clear.",
        "Estimate Presented": "I wanted to see if you had any questions about the estimate, scope, or options we reviewed.",
        "Proposal Sent": "I wanted to confirm you received the proposal and see if there is anything I can clarify.",
        "Needs Follow-Up": "I wanted to reconnect and see what questions came up since we last spoke.",
        "Verbal Yes / Pending Signature": "I wanted to help get the final step wrapped up so we can keep everything moving.",
        "Closed Lost": "I wanted to thank you again for the opportunity. If anything changes, I would be happy to help.",
    }.get(lead_status, "I wanted to check in and help with the next step.")

    objection_line = f" I know {objection.lower()} was one of the things you were thinking through, and I am happy to help make that clearer." if objection != "None" else ""
    value_line = f" The goal is really about {value_statement(project_type)}."

    close = "Would you like me to help you review the next step?"
    if intensity == "Last Attempt":
        close = "Should I keep this active for you, or would it be better for me to close out my follow-up for now?"
    elif intensity == "Persistent":
        close = "Can we set a quick time today to make a clear yes/no decision on the next step?"

    return f"{opener} {status_line}{objection_line}{value_line} {close}"


def build_email(inputs: dict) -> tuple[str, str]:
    customer = inputs["customer"] or "there"
    company = inputs["company"] or "our team"
    project_type = inputs["project_type"]
    lead_status = inputs["lead_status"]
    objection = inputs["objection"]
    financing = inputs["financing"]
    tone = inputs["tone"]

    subject = {
        "New Lead": f"Next Step for Your {project_type} Project",
        "Inspection Scheduled": f"Confirming Your {project_type} Appointment",
        "Inspection Completed": f"Following Up After Your {project_type} Appointment",
        "Estimate Presented": f"Following Up on Your {project_type} Estimate",
        "Proposal Sent": f"Checking In on Your {project_type} Proposal",
        "Needs Follow-Up": f"Quick Follow-Up on Your {project_type} Project",
        "Verbal Yes / Pending Signature": f"Final Step for Your {project_type} Project",
        "Closed Lost": "Thank You for Considering Us",
    }.get(lead_status, f"Following Up on Your {project_type} Project")

    intro = f"I wanted to follow up regarding your {project_type.lower()} project and see what questions you may have."
    if tone == "Urgent":
        intro = f"I wanted to follow up quickly regarding your {project_type.lower()} project so we can keep the next step from getting delayed."
    elif tone == "Direct":
        intro = f"I wanted to follow up on your {project_type.lower()} project and help determine the next step."
    elif tone == "No-Pressure":
        intro = f"No pressure — I just wanted to follow up on your {project_type.lower()} project and see what questions you still have."
    elif tone == "Consultative":
        intro = f"I wanted to help you think through the best next step for your {project_type.lower()} project."

    body = f"Hi {customer},\n\n{intro}\n\nThe main goal is {value_statement(project_type)}."

    if objection != "None":
        body += f"\n\nI know you mentioned {objection.lower()}. That is understandable. My goal is not to pressure you, but to help make the decision clearer."
    if financing == "Yes":
        body += "\n\nWe can also revisit the payment options if that would make the project easier to plan around."

    body += f"\n\nWould it be helpful for me to walk you through the next step or answer any remaining questions?\n\nThanks again,\n{company}"
    return subject, body


def build_voicemail(inputs: dict) -> str:
    customer = inputs["customer"] or "there"
    company = inputs["company"] or "our team"
    project_type = inputs["project_type"].lower()
    return f"Hi {customer}, this is {company}. I was calling to follow up on your {project_type} project. I will send you a quick text as well, but I wanted to see if you had any questions or if you would like to review the next step. You can call or text me back whenever you get a chance. Thanks."


def objection_guidance(objection: str) -> str:
    guidance = {
        "Price": "Rebuild value before discounting. Clarify scope, warranty, risk, financing, install quality, and cost of waiting.",
        "Need to Think About It": "Ask what specifically they need to think through. Turn vague delay into a clear concern.",
        "Getting Other Quotes": "Clarify what they are comparing: scope, warranty, install quality, timeline, payment options, and trust.",
        "Spouse / Decision Maker": "Offer to recap the project for both decision-makers and schedule a short review conversation.",
        "Timing": "Clarify whether timing means budget, schedule, urgency, or uncertainty. Offer a realistic next-step plan.",
        "Financing": "Clarify whether the issue is approval, monthly payment, APR, term, or total project cost.",
        "Other": "Ask a clarifying question to uncover the real concern, then guide the customer toward a clear next step.",
        "None": "Keep the follow-up simple. Confirm questions, restate the next step, and ask for a clear decision.",
    }
    return guidance.get(objection, guidance["Other"])


def manager_note(objection: str, priority: str) -> str:
    urgency = {
        "High Priority": "This lead should be treated as active pipeline and followed up today.",
        "Medium Priority": "This lead should be followed up within 24 hours before momentum drops.",
        "Low Priority": "This lead can be followed up within 48-72 hours, but should not be ignored.",
    }.get(priority, "This lead should be reviewed and assigned a clear next step.")
    coaching = {
        "Price": "Coach the rep to rebuild value, clarify scope, and revisit financing before discounting.",
        "Getting Other Quotes": "Coach the rep to compare scope, warranty, install quality, timeline, and trust instead of price alone.",
        "Need to Think About It": "Coach the rep to ask what specifically needs to be thought through.",
        "Spouse / Decision Maker": "Coach the rep to involve decision-makers earlier and offer a clear recap.",
        "Financing": "Coach the rep to clarify if the issue is payment, approval, APR, term, or total cost.",
    }.get(objection, "Coach the rep to ask better discovery questions and secure a clear next step.")
    return f"{urgency} {coaching}"


def followup_sequence(inputs: dict) -> dict:
    customer = inputs["customer"] or "there"
    company = inputs["company"] or "our team"
    project_type = inputs["project_type"].lower()
    objection = inputs["objection"]
    intensity = inputs["intensity"]

    if intensity == "Light Touch":
        return {
            "Same Day": f"Hi {customer}, this is {company}. Just checking in on your {project_type} project to see if you had any questions.",
            "Day 3": f"Hi {customer}, I wanted to make sure you had everything you needed from us. Happy to help if questions came up.",
            "Day 7": f"Hi {customer}, I did not want to let this fall through the cracks. Let me know if you would like to revisit it.",
        }
    if intensity == "Last Attempt":
        return {
            "Today": f"Hi {customer}, I wanted to close the loop on your {project_type} project. Should I keep this active for you, or pause my follow-up for now?",
            "Final Check-In": f"Hi {customer}, I have not been able to reconnect, so I will close out my follow-up for now. If you need anything later, I would be happy to help.",
        }

    day_0 = f"Hi {customer}, this is {company}. Just checking in on your {project_type} project to see if you had any questions or wanted help with the next step."
    day_1 = f"Hi {customer}, I wanted to follow up again and make sure nothing was left unclear from our last conversation about the {project_type} project."
    if objection != "None":
        day_1 += f" I remember {objection.lower()} was one of the things you were considering, and I am happy to walk through that."
    day_3 = f"Hi {customer}, I know these projects can take some thought. Is there anything specific holding you back that I can help clarify?"
    day_7 = f"Hi {customer}, I did not want to let this fall through the cracks. Would you like to keep the {project_type} project active, or should I close out my follow-up for now?"
    return {"Same Day": day_0, "Next Day": day_1, "Day 3": day_3, "Day 7": day_7}


def build_crm_note(inputs: dict, priority: str, timing: str, temperature: str, risk: str, main_risk: str, next_action: str) -> str:
    return f"""Customer: {inputs['customer'] or 'N/A'}
Company: {inputs['company'] or 'N/A'}
Project Type: {inputs['project_type']}
Current Status: {inputs['lead_status']}
Lead Temperature: {temperature}
Deal Risk: {risk}
Main Risk: {main_risk}
Priority: {priority}
Urgency Level: {inputs['urgency']}
Days Since Last Contact: {inputs['days_since']}
Last Interaction: {inputs['context'] or 'Not provided'}
Primary Concern/Objection: {inputs['objection']}
Financing Discussed: {inputs['financing']}
Recommended Next Step: {timing}
Next Best Action: {next_action}
CRM Action: Follow up using generated text/email/call workflow and update disposition after customer response.
"""


def build_call_script(inputs: dict) -> str:
    customer = inputs["customer"] or "the customer"
    project_type = inputs["project_type"].lower()
    return f"""Opening:
Hi, is this {customer}? This is following up about your {project_type} project.

Reason for call:
I wanted to reconnect and help with the next step.

Discovery question:
What is the main thing you are still trying to decide or feel comfortable with?

Value reminder:
The main goal is {value_statement(inputs['project_type'])}, and I want to make sure you have a clear path forward.

Close:
Would it make sense to review the next step together while I have you?
"""


def build_report(inputs: dict, outputs: dict) -> str:
    sequence_lines = "\n\n".join(f"### {label}\n{message}" for label, message in outputs["sequence"].items())
    return f"""# FollowUpPilot AI Follow-Up Plan

## Customer
Customer: {inputs['customer'] or 'N/A'}
Company: {inputs['company'] or 'N/A'}
Project Type: {inputs['project_type']}
Lead Status: {inputs['lead_status']}
Lead Temperature: {outputs['temperature']}
Deal Risk: {outputs['deal_risk']}
Main Risk: {outputs['main_risk']}
Priority: {outputs['priority']}
Priority Score: {outputs['score']}
Recommended Timing: {outputs['timing']}
Next Best Action: {outputs['next_action']}

## Why This Recommendation
{outputs['why']}

## Context
{inputs['context'] or 'No context provided.'}

## Text Message
{outputs['sms']}

## Email
Subject: {outputs['subject']}

{outputs['email']}

## Voicemail Script
{outputs['voicemail']}

## CRM Note
{outputs['crm']}

## Call Script
{outputs['call']}

## Objection Guidance
{outputs['guidance']}

## Manager Coaching Note
{outputs['coaching']}

## Follow-Up Sequence

{sequence_lines}

---

Generated by FollowUpPilot AI.
"""

# -----------------------------------------------------------------------------
# Sidebar and hero
# -----------------------------------------------------------------------------

with st.sidebar:
    st.title("FollowUpPilot AI")
    st.caption("Version 2.2")
    st.markdown("Sales follow-up workflow automation for field-sales and home-service teams.")
    st.divider()
    st.markdown("### Outputs")
    st.markdown("""
    - Lead temperature
    - Deal risk
    - Next best action
    - Text / email / voicemail
    - CRM note / call script
    - Objection guidance
    - Follow-up sequence
    - Downloadable plan
    """)

st.markdown("""
<div class="hero">
    <div class="eyebrow">Sales Follow-Up Workflow Tool</div>
    <div class="hero-title">FollowUpPilot AI</div>
    <div class="hero-subtitle">Turn customer context into next-best actions, follow-up messages, CRM notes, call scripts, objection guidance, manager coaching notes, and multi-touch sequences.</div>
    <div class="hero-pills"><span>Sales Execution</span><span>CRM Discipline</span><span>Follow-Up</span><span>Next Best Action</span><span>Streamlit</span></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Input workflow
# -----------------------------------------------------------------------------

section_title("Customer follow-up builder", "Load a sample scenario or enter your own customer context. The app will generate a complete follow-up workflow.")

scenario_name = st.selectbox("Load Sample Scenario", list(SAMPLE_SCENARIOS.keys()))
scenario = SAMPLE_SCENARIOS.get(scenario_name, {})

with st.form("followup_form"):
    form_group("Customer and project details")
    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        customer = st.text_input("Customer Name", value=scenario.get("customer", ""), placeholder="Example: Avery Johnson")
    with detail_col2:
        company = st.text_input("Company Name", value=scenario.get("company", ""), placeholder="Example: Summit Home Services")

    project_col1, project_col2 = st.columns(2)
    with project_col1:
        project_type = st.selectbox("Project Type", PROJECT_TYPES, index=PROJECT_TYPES.index(scenario.get("project_type", "Roof Replacement")))
    with project_col2:
        lead_status = st.selectbox("Lead Status", LEAD_STATUSES, index=LEAD_STATUSES.index(scenario.get("lead_status", "Estimate Presented")))

    form_group("Last interaction")
    context = st.text_area("Last Interaction / Context", value=scenario.get("context", ""), placeholder="Example: Customer liked the proposal but wanted to compare payment options and review timing with their spouse.", height=120)

    form_group("Follow-up strategy")
    strategy_col1, strategy_col2, strategy_col3, strategy_col4 = st.columns(4)
    with strategy_col1:
        objection = st.selectbox("Main Concern", OBJECTIONS, index=OBJECTIONS.index(scenario.get("objection", "Price")))
    with strategy_col2:
        financing = st.selectbox("Financing?", FINANCING_OPTIONS, index=FINANCING_OPTIONS.index(scenario.get("financing", "No")))
    with strategy_col3:
        urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=URGENCY_LEVELS.index(scenario.get("urgency", "Medium")))
    with strategy_col4:
        tone = st.selectbox("Tone", TONES, index=TONES.index(scenario.get("tone", "Professional")))

    strategy_col5, strategy_col6, strategy_col7 = st.columns(3)
    with strategy_col5:
        days_since = st.number_input("Days Since Last Contact", min_value=0, max_value=90, value=int(scenario.get("days_since", 1)), step=1)
    with strategy_col6:
        intensity = st.selectbox("Follow-Up Intensity", FOLLOWUP_INTENSITIES, index=FOLLOWUP_INTENSITIES.index(scenario.get("intensity", "Standard")))
    with strategy_col7:
        channel = st.selectbox("Preferred Channel", CHANNEL_OPTIONS, index=CHANNEL_OPTIONS.index(scenario.get("channel", "All")))

    submitted = st.form_submit_button("Generate Follow-Up Plan", use_container_width=True)

if not submitted:
    st.markdown('<div class="note-box">Complete the form or load a sample scenario, then click Generate Follow-Up Plan.</div>', unsafe_allow_html=True)
    st.stop()

inputs = {
    "customer": customer,
    "company": company,
    "project_type": project_type,
    "lead_status": lead_status,
    "context": context,
    "objection": objection,
    "financing": financing,
    "urgency": urgency,
    "tone": tone,
    "days_since": int(days_since),
    "intensity": intensity,
    "channel": channel,
}

priority, timing, score = calculate_priority(lead_status, urgency, financing, objection, project_type, int(days_since), intensity)
temperature = get_lead_temperature(priority, lead_status, int(days_since))
deal_risk, main_risk = get_deal_risk(objection, int(days_since), lead_status)
next_action = next_best_action(inputs, priority, deal_risk)
why = why_recommendation(inputs, priority, score, deal_risk, main_risk)
sms = build_text_message(inputs)
subject, email = build_email(inputs)
voicemail = build_voicemail(inputs)
guidance = objection_guidance(objection)
coaching = manager_note(objection, priority)
sequence = followup_sequence(inputs)
call = build_call_script(inputs)
crm = build_crm_note(inputs, priority, timing, temperature, deal_risk, main_risk, next_action)
status_class = priority_class(priority)

outputs = {
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
    "guidance": guidance,
    "coaching": coaching,
    "sequence": sequence,
    "crm": crm,
    "call": call,
}

# -----------------------------------------------------------------------------
# Output workflow
# -----------------------------------------------------------------------------

section_title("Follow-up recommendation")
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Priority", priority, f"Score: {score}")
with col2:
    metric_card("Lead Temperature", temperature)
with col3:
    metric_card("Deal Risk", deal_risk, main_risk)
with col4:
    metric_card("Timing", timing)

html_card("Next Best Action", f'<span class="status-pill {status_class}">{priority}</span><p>{next_action}</p>', "nba-card")
html_card("Why This Recommendation", f"<p>{why}</p>", "guidance-card")

section_title("Customer communication")
comm_tabs = st.tabs(["Text Message", "Email", "Voicemail"])
with comm_tabs[0]:
    st.text_area("Copy-ready text message", sms, height=150)
with comm_tabs[1]:
    st.text_input("Subject Line", subject)
    st.text_area("Copy-ready email", email, height=315)
with comm_tabs[2]:
    st.text_area("Voicemail script", voicemail, height=175)

section_title("CRM and call workflow")
workflow_tabs = st.tabs(["CRM Note", "Call Script"])
with workflow_tabs[0]:
    st.text_area("CRM-ready note", crm, height=330)
with workflow_tabs[1]:
    st.text_area("Call script", call, height=300)

section_title("Objection guidance and manager coaching")
coach_col1, coach_col2 = st.columns(2)
with coach_col1:
    html_card("Objection Guidance", f"<p>{guidance}</p>", "guidance-card")
with coach_col2:
    html_card("Manager Coaching Note", f"<p>{coaching}</p>", "guidance-card")

section_title("Suggested follow-up sequence")
sequence_cols = st.columns(2)
for position, (label, message) in enumerate(sequence.items()):
    with sequence_cols[position % 2]:
        html_card(label, f"<p>{message}</p>", "sequence-card")

section_title("Download follow-up plan")
report = build_report(inputs, outputs)
st.download_button("Download Follow-Up Plan", data=report, file_name="followuppilot-follow-up-plan.md", mime="text/markdown", use_container_width=True)

with st.expander("How to use FollowUpPilot AI"):
    st.markdown("""
    1. Load a sample scenario or enter your own customer/project context.
    2. Select lead status, concern, urgency, tone, days since contact, intensity, and preferred channel.
    3. Generate the follow-up plan.
    4. Copy the customer text, email, voicemail, CRM note, and call script.
    5. Review next best action, deal risk, objection guidance, and manager coaching note.
    6. Download the follow-up plan for CRM documentation or team coaching.
    """)

st.markdown('<div class="note-box">Privacy note: Information entered into this app is processed during the active session and is not saved by this app.</div>', unsafe_allow_html=True)
