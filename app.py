import streamlit as st

# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="FollowUpPilot AI",
    page_icon="💬",
    layout="wide",
)

# -----------------------------------------------------------------------------
# App options
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

TONES = ["Friendly", "Professional", "Urgent", "Direct"]
URGENCY_LEVELS = ["Low", "Medium", "High"]
FINANCING_OPTIONS = ["No", "Yes"]

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
.block-container {
    max-width: 1180px;
    padding-top: 1.35rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #111827;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] ul,
[data-testid="stSidebar"] ol {
    color: #f9fafb !important;
}

[data-testid="stSidebar"] li::marker {
    color: #93c5fd !important;
}

.hero {
    padding: 1.9rem 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #111827 0%, #1f2937 52%, #334155 100%);
    color: #ffffff;
    box-shadow: 0 18px 36px rgba(17, 24, 39, .18);
    margin-bottom: 1rem;
    border: 1px solid rgba(255, 255, 255, .08);
}

.eyebrow {
    text-transform: uppercase;
    letter-spacing: .13em;
    font-size: .75rem;
    font-weight: 800;
    color: #93c5fd;
    margin-bottom: .65rem;
}

.hero-title {
    font-size: 2.25rem;
    line-height: 1.08;
    font-weight: 850;
    margin-bottom: .65rem;
}

.hero-subtitle {
    font-size: 1.02rem;
    line-height: 1.62;
    color: #e5e7eb;
    max-width: 900px;
}

.hero-pills span {
    display: inline-block;
    padding: .35rem .65rem;
    margin: .75rem .28rem 0 0;
    border-radius: 999px;
    background: rgba(255, 255, 255, .10);
    border: 1px solid rgba(255, 255, 255, .16);
    font-weight: 700;
    font-size: .78rem;
    color: #f8fafc;
}

.section-title {
    margin-top: 1.25rem;
    margin-bottom: .55rem;
    font-size: 1.4rem;
    font-weight: 850;
    color: #111827;
}

.section-lede {
    color: #4b5563;
    line-height: 1.6;
    margin-bottom: 1rem;
    max-width: 950px;
}

.form-group-title {
    font-size: .9rem;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #64748b;
    margin: .35rem 0 .15rem 0;
}

.metric-card,
.output-card,
.guidance-card,
.sequence-card,
.workflow-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, .055);
}

.metric-card {
    height: 138px;
    padding: 1rem;
    margin-bottom: .75rem;
}

.metric-label {
    color: #6b7280;
    font-size: .78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .05em;
    margin-bottom: .5rem;
}

.metric-value {
    color: #111827;
    font-size: 1.42rem;
    line-height: 1.18;
    font-weight: 900;
    overflow-wrap: break-word;
}

.metric-note {
    color: #64748b;
    font-size: .85rem;
    margin-top: .55rem;
}

.output-card,
.guidance-card,
.sequence-card,
.workflow-card {
    padding: 1.15rem;
    margin-bottom: .8rem;
}

.output-card {
    border-left: 5px solid #111827;
}

.guidance-card {
    border-left: 5px solid #1d4ed8;
}

.sequence-card {
    border-left: 5px solid #059669;
}

.workflow-card {
    border-left: 5px solid #1d4ed8;
}

.output-card h3,
.guidance-card h3,
.sequence-card h3,
.workflow-card h3 {
    font-size: 1.05rem;
    font-weight: 850;
    color: #111827;
    margin-bottom: .4rem;
}

.output-card p,
.guidance-card p,
.sequence-card p,
.workflow-card p,
.output-card li,
.guidance-card li,
.sequence-card li,
.workflow-card li {
    color: #4b5563;
    line-height: 1.52;
    font-size: .93rem;
}

.status-high {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
}

.status-medium {
    background: #fef3c7;
    color: #92400e;
    border: 1px solid #fde68a;
}

.status-low {
    background: #d1fae5;
    color: #065f46;
    border: 1px solid #a7f3d0;
}

.status-pill {
    display: inline-block;
    padding: .25rem .6rem;
    border-radius: 999px;
    font-weight: 850;
    font-size: .78rem;
    margin-bottom: .5rem;
}

.note-box {
    padding: .9rem 1rem;
    border-radius: 14px;
    background: #f8fafc;
    color: #334155;
    border: 1px solid #e2e8f0;
    font-weight: 650;
    margin: .9rem 0;
    font-size: .92rem;
}
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
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def html_card(title: str, body: str, css_class: str = "output-card") -> None:
    st.markdown(
        f"""
        <div class="{css_class}">
            <h3>{title}</h3>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    return values.get(project_type, "making sure the project is handled correctly")


def calculate_priority(lead_status: str, urgency: str, financing: str, objection: str, project_type: str) -> tuple[str, str, int]:
    score = 0

    if lead_status in ["Estimate Presented", "Proposal Sent", "Verbal Yes / Pending Signature"]:
        score += 3
    elif lead_status in ["Inspection Completed", "Needs Follow-Up"]:
        score += 2
    else:
        score += 1

    score += {"Low": 1, "Medium": 2, "High": 3}.get(urgency, 1)

    if financing == "Yes":
        score += 1

    if objection != "None":
        score += 1

    if project_type in ["Roof Replacement", "Roof Repair", "Siding", "Gutters"]:
        score += 1

    if score >= 8:
        return "High Priority", "Follow up today", score
    if score >= 5:
        return "Medium Priority", "Follow up within 24 hours", score
    return "Low Priority", "Follow up within 48-72 hours", score


def priority_class(priority: str) -> str:
    if priority == "High Priority":
        return "status-high"
    if priority == "Medium Priority":
        return "status-medium"
    return "status-low"


def build_text_message(inputs: dict) -> str:
    customer = inputs["customer"] or "there"
    company = inputs["company"] or "our team"
    project_type = inputs["project_type"]
    lead_status = inputs["lead_status"]
    objection = inputs["objection"]
    tone = inputs["tone"]
    context = inputs["context"]

    greeting = f"Hi {customer},"
    opener_by_tone = {
        "Friendly": f"{greeting} this is a quick follow-up from {company}.",
        "Professional": f"{greeting} this is a follow-up from {company} regarding your {project_type.lower()} project.",
        "Urgent": f"{greeting} I wanted to follow up quickly so we can keep your {project_type.lower()} project moving.",
        "Direct": f"{greeting} checking in from {company}.",
    }

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

    objection_line = ""
    if objection != "None":
        objection_line = f" I know {objection.lower()} was one of the things you were thinking through, and I am happy to help make that clearer."

    value_line = f" The goal is really about {value_statement(project_type)}." if context else ""

    return f"{opener_by_tone.get(tone, opener_by_tone['Professional'])} {status_line}{objection_line}{value_line} Would you like me to help you review the next step?"


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

    body = f"Hi {customer},\n\n{intro}\n\nThe main goal is {value_statement(project_type)}."

    if objection != "None":
        body += f"\n\nI know you mentioned {objection.lower()}. That is understandable. My goal is not to pressure you, but to help make the decision clearer."

    if financing == "Yes":
        body += "\n\nWe can also revisit the payment options if that would make the project easier to plan around."

    body += f"\n\nWould it be helpful for me to walk you through the next step or answer any remaining questions?\n\nThanks again,\n{company}"
    return subject, body


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

    day_0 = f"Hi {customer}, this is {company}. Just checking in on your {project_type} project to see if you had any questions or wanted help with the next step."
    day_1 = f"Hi {customer}, I wanted to follow up again and make sure nothing was left unclear from our last conversation about the {project_type} project."

    if objection != "None":
        day_1 += f" I remember {objection.lower()} was one of the things you were considering, and I am happy to walk through that."

    day_3 = f"Hi {customer}, I know these projects can take some thought. Is there anything specific holding you back that I can help clarify?"
    day_7 = f"Hi {customer}, I did not want to let this fall through the cracks. Would you like to keep the {project_type} project active, or should I close out my follow-up for now?"

    return {
        "Same Day": day_0,
        "Next Day": day_1,
        "Day 3": day_3,
        "Day 7": day_7,
    }


def build_crm_note(inputs: dict, priority: str, timing: str) -> str:
    return f"""Customer: {inputs['customer'] or 'N/A'}
Company: {inputs['company'] or 'N/A'}
Project Type: {inputs['project_type']}
Current Status: {inputs['lead_status']}
Priority: {priority}
Urgency Level: {inputs['urgency']}
Last Interaction: {inputs['context'] or 'Not provided'}
Primary Concern/Objection: {inputs['objection']}
Financing Discussed: {inputs['financing']}
Recommended Next Step: {timing}
CRM Action: Follow up using generated text/email and update disposition after customer response.
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


def build_report(inputs: dict, priority: str, score: int, timing: str, sms: str, subject: str, email: str, crm: str, call: str, guidance: str, coaching: str, sequence: dict) -> str:
    sequence_lines = "\n\n".join(f"### {label}\n{message}" for label, message in sequence.items())
    return f"""# FollowUpPilot AI Follow-Up Plan

## Customer
Customer: {inputs['customer'] or 'N/A'}
Company: {inputs['company'] or 'N/A'}
Project Type: {inputs['project_type']}
Lead Status: {inputs['lead_status']}
Priority: {priority}
Priority Score: {score}
Recommended Timing: {timing}

## Context
{inputs['context'] or 'No context provided.'}

## Text Message
{sms}

## Email
Subject: {subject}

{email}

## CRM Note
{crm}

## Call Script
{call}

## Objection Guidance
{guidance}

## Manager Coaching Note
{coaching}

## Follow-Up Sequence

{sequence_lines}

---

Generated by FollowUpPilot AI.
"""

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:
    st.title("FollowUpPilot AI")
    st.caption("Version 2.1")
    st.markdown(
        """
        Sales follow-up workflow automation for field-sales and home-service teams.

        Build cleaner customer communication, CRM notes, call scripts, and manager coaching notes.
        """
    )
    st.divider()
    st.markdown("### Outputs")
    st.markdown(
        """
        - Follow-up priority
        - Text message
        - Email
        - CRM note
        - Call script
        - Objection guidance
        - Manager coaching note
        - Multi-touch sequence
        - Downloadable plan
        """
    )

# -----------------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Sales Follow-Up Workflow Tool</div>
        <div class="hero-title">FollowUpPilot AI</div>
        <div class="hero-subtitle">
            Turn customer context into follow-up messages, CRM notes, call scripts, objection guidance,
            manager coaching notes, and multi-touch follow-up sequences.
        </div>
        <div class="hero-pills">
            <span>Sales Execution</span><span>CRM Discipline</span><span>Follow-Up</span><span>Manager Coaching</span><span>Streamlit</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Input workflow
# -----------------------------------------------------------------------------

section_title(
    "Customer follow-up builder",
    "Enter a fictional sample scenario or real customer context. The app will generate a complete follow-up workflow from the information provided.",
)

with st.form("followup_form"):
    form_group("Customer and project details")
    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        customer = st.text_input("Customer Name", placeholder="Example: Avery Johnson")
    with detail_col2:
        company = st.text_input("Company Name", placeholder="Example: Summit Home Services")

    project_col1, project_col2 = st.columns(2)
    with project_col1:
        project_type = st.selectbox("Project Type", PROJECT_TYPES)
    with project_col2:
        lead_status = st.selectbox("Lead Status", LEAD_STATUSES, index=3)

    form_group("Last interaction")
    context = st.text_area(
        "Last Interaction / Context",
        placeholder="Example: Customer liked the proposal but wanted to compare payment options and review timing with their spouse.",
        height=120,
    )

    form_group("Follow-up strategy")
    strategy_col1, strategy_col2, strategy_col3, strategy_col4 = st.columns(4)
    with strategy_col1:
        objection = st.selectbox("Main Concern", OBJECTIONS, index=1)
    with strategy_col2:
        financing = st.selectbox("Financing?", FINANCING_OPTIONS)
    with strategy_col3:
        urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=1)
    with strategy_col4:
        tone = st.selectbox("Tone", TONES, index=1)

    submitted = st.form_submit_button("Generate Follow-Up Plan", use_container_width=True)

# -----------------------------------------------------------------------------
# Output workflow
# -----------------------------------------------------------------------------

if not submitted:
    st.markdown(
        '<div class="note-box">Complete the form and click Generate Follow-Up Plan to create customer communication, CRM notes, and next-step recommendations.</div>',
        unsafe_allow_html=True,
    )
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
}

priority, timing, score = calculate_priority(lead_status, urgency, financing, objection, project_type)
sms = build_text_message(inputs)
subject, email = build_email(inputs)
guidance = objection_guidance(objection)
coaching = manager_note(objection, priority)
sequence = followup_sequence(inputs)
crm = build_crm_note(inputs, priority, timing)
call = build_call_script(inputs)
status_class = priority_class(priority)

# -----------------------------------------------------------------------------
# Recommendation snapshot
# -----------------------------------------------------------------------------

section_title("Follow-up recommendation")
snapshot_col1, snapshot_col2, snapshot_col3, snapshot_col4 = st.columns(4)
with snapshot_col1:
    metric_card("Priority", priority, f"Score: {score}")
with snapshot_col2:
    metric_card("Timing", timing)
with snapshot_col3:
    metric_card("Lead Status", lead_status)
with snapshot_col4:
    metric_card("Main Concern", objection)

html_card(
    "Workflow Diagnosis",
    f"""
    <span class="status-pill {status_class}">{priority}</span>
    <p><strong>Recommended timing:</strong> {timing}</p>
    <p><strong>Manager view:</strong> {coaching}</p>
    """,
    "guidance-card",
)

# -----------------------------------------------------------------------------
# Customer communication
# -----------------------------------------------------------------------------

section_title("Customer communication")
comm_tab1, comm_tab2 = st.tabs(["Text Message", "Email"])

with comm_tab1:
    st.text_area("Copy-ready text message", sms, height=145)

with comm_tab2:
    st.text_input("Subject Line", subject)
    st.text_area("Copy-ready email", email, height=310)

# -----------------------------------------------------------------------------
# CRM and call workflow
# -----------------------------------------------------------------------------

section_title("CRM and call workflow")
workflow_tab1, workflow_tab2 = st.tabs(["CRM Note", "Call Script"])

with workflow_tab1:
    st.text_area("CRM-ready note", crm, height=260)

with workflow_tab2:
    st.text_area("Call script", call, height=300)

# -----------------------------------------------------------------------------
# Objection and manager coaching
# -----------------------------------------------------------------------------

section_title("Objection guidance and manager coaching")
coaching_col1, coaching_col2 = st.columns(2)
with coaching_col1:
    html_card("Objection Guidance", f"<p>{guidance}</p>", "guidance-card")
with coaching_col2:
    html_card("Manager Coaching Note", f"<p>{coaching}</p>", "guidance-card")

# -----------------------------------------------------------------------------
# Follow-up sequence
# -----------------------------------------------------------------------------

section_title("Suggested follow-up sequence")
sequence_cols = st.columns(2)
for position, (label, message) in enumerate(sequence.items()):
    with sequence_cols[position % 2]:
        html_card(label, f"<p>{message}</p>", "sequence-card")

# -----------------------------------------------------------------------------
# Downloadable plan
# -----------------------------------------------------------------------------

section_title("Download follow-up plan")
report = build_report(inputs, priority, score, timing, sms, subject, email, crm, call, guidance, coaching, sequence)
st.download_button(
    "Download Follow-Up Plan",
    data=report,
    file_name="followuppilot-follow-up-plan.md",
    mime="text/markdown",
    use_container_width=True,
)

with st.expander("How to use FollowUpPilot AI"):
    st.markdown(
        """
        1. Enter the customer/project context.
        2. Select the lead status, main concern, urgency, financing status, and tone.
        3. Generate the follow-up plan.
        4. Copy the customer text, email, CRM note, and call script.
        5. Review objection guidance and manager coaching notes.
        6. Download the follow-up plan for CRM documentation or team coaching.
        """
    )

st.markdown(
    '<div class="note-box">Privacy note: Information entered into this app is processed during the active session and is not saved by this app.</div>',
    unsafe_allow_html=True,
)
