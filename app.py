import streamlit as st

from ai_helpers import enhance_text
from pdf_helpers import markdown_to_pdf

st.set_page_config(page_title="FollowUpPilot AI", page_icon="💬", layout="wide")

PROJECT_TYPES = ["Roof Replacement", "Roof Repair", "Siding", "Gutters", "Windows", "HVAC", "Pest Control", "General Home Service", "Other"]
LEAD_STATUSES = ["New Lead", "Inspection Scheduled", "Inspection Completed", "Estimate Presented", "Proposal Sent", "Needs Follow-Up", "Verbal Yes / Pending Signature", "Closed Lost"]
OBJECTIONS = ["None", "Price", "Need to Think About It", "Getting Other Quotes", "Spouse / Decision Maker", "Timing", "Financing", "Other"]
TONES = ["Friendly", "Professional", "Urgent", "Direct", "Consultative", "Reassuring", "High-Confidence", "No-Pressure"]
URGENCY_LEVELS = ["Low", "Medium", "High"]
FINANCING_OPTIONS = ["No", "Yes"]
FOLLOWUP_INTENSITIES = ["Light Touch", "Standard", "Persistent", "Last Attempt"]
CHANNEL_OPTIONS = ["All", "Text", "Email", "Phone Call", "Voicemail", "CRM Note"]

SAMPLE_SCENARIOS = {
    "Blank / Custom": {},
    "Price Objection": {"customer": "Avery Johnson", "company": "Summit Home Services", "project_type": "Roof Replacement", "lead_status": "Estimate Presented", "context": "Customer liked the project plan but said the price was higher than expected and wanted to review options before making a decision.", "objection": "Price", "financing": "Yes", "urgency": "High", "tone": "Consultative", "days_since": 1, "intensity": "Standard", "channel": "All"},
    "Needs Spouse Approval": {"customer": "Morgan Ellis", "company": "Summit Home Services", "project_type": "Siding", "lead_status": "Proposal Sent", "context": "Customer liked the siding option but said they needed to review the color, budget, and timeline with their spouse before moving forward.", "objection": "Spouse / Decision Maker", "financing": "No", "urgency": "Medium", "tone": "Reassuring", "days_since": 2, "intensity": "Standard", "channel": "All"},
    "Proposal Sent / No Response": {"customer": "Jordan Miller", "company": "Summit Home Services", "project_type": "Gutters", "lead_status": "Proposal Sent", "context": "Proposal was sent four days ago. Customer has not responded yet. The project was originally described as important before the next heavy rain.", "objection": "Timing", "financing": "No", "urgency": "Medium", "tone": "Direct", "days_since": 4, "intensity": "Persistent", "channel": "All"},
    "Financing Concern": {"customer": "Taylor Brooks", "company": "Summit Home Services", "project_type": "Windows", "lead_status": "Estimate Presented", "context": "Customer wants the project completed but was unsure about monthly payment options and total project cost.", "objection": "Financing", "financing": "Yes", "urgency": "Medium", "tone": "No-Pressure", "days_since": 1, "intensity": "Light Touch", "channel": "All"},
}

CSS = """
<style>
.block-container{max-width:1180px;padding-top:1.35rem;padding-bottom:3rem}[data-testid="stSidebar"]{background:#111827}[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] li,[data-testid="stSidebar"] ul,[data-testid="stSidebar"] ol{color:#f9fafb!important}[data-testid="stSidebar"] li::marker{color:#93c5fd!important}.hero{padding:1.9rem 2rem;border-radius:20px;background:linear-gradient(135deg,#111827 0%,#1f2937 52%,#334155 100%);color:#fff;box-shadow:0 18px 36px rgba(17,24,39,.18);margin-bottom:1rem;border:1px solid rgba(255,255,255,.08)}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.75rem;font-weight:800;color:#93c5fd;margin-bottom:.65rem}.hero-title{font-size:2.25rem;line-height:1.08;font-weight:850;margin-bottom:.65rem}.hero-subtitle{font-size:1.02rem;line-height:1.62;color:#e5e7eb;max-width:900px}.hero-pills span{display:inline-block;padding:.35rem .65rem;margin:.75rem .28rem 0 0;border-radius:999px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);font-weight:700;font-size:.78rem;color:#f8fafc}.section-title{margin-top:1.25rem;margin-bottom:.55rem;font-size:1.4rem;font-weight:850;color:#111827}.section-lede{color:#4b5563;line-height:1.6;margin-bottom:1rem;max-width:950px}.form-group-title{font-size:.9rem;font-weight:850;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin:.35rem 0 .15rem 0}.metric-card,.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 8px 20px rgba(15,23,42,.055)}.metric-card{height:138px;padding:1rem;margin-bottom:.75rem}.metric-label{color:#6b7280;font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}.metric-value{color:#111827;font-size:1.35rem;line-height:1.18;font-weight:900;overflow-wrap:break-word}.metric-note{color:#64748b;font-size:.85rem;margin-top:.55rem}.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card{padding:1.15rem;margin-bottom:.8rem}.output-card{border-left:5px solid #111827}.guidance-card,.workflow-card{border-left:5px solid #1d4ed8}.sequence-card{border-left:5px solid #059669}.nba-card{border-left:5px solid #111827;background:#f8fafc}.output-card h3,.guidance-card h3,.sequence-card h3,.workflow-card h3,.nba-card h3{font-size:1.05rem;font-weight:850;color:#111827;margin-bottom:.4rem}.output-card p,.guidance-card p,.sequence-card p,.workflow-card p,.nba-card p,.output-card li,.guidance-card li,.sequence-card li,.workflow-card li,.nba-card li{color:#4b5563;line-height:1.52;font-size:.93rem}.status-high{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}.status-medium{background:#fef3c7;color:#92400e;border:1px solid #fde68a}.status-low{background:#d1fae5;color:#065f46;border:1px solid #a7f3d0}.status-pill{display:inline-block;padding:.25rem .6rem;border-radius:999px;font-weight:850;font-size:.78rem;margin-bottom:.5rem}.note-box{padding:.9rem 1rem;border-radius:14px;background:#f8fafc;color:#334155;border:1px solid #e2e8f0;font-weight:650;margin:.9rem 0;font-size:.92rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def section_title(title, lede=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<div class="section-lede">{lede}</div>', unsafe_allow_html=True)

def form_group(title):
    st.markdown(f'<div class="form-group-title">{title}</div>', unsafe_allow_html=True)

def metric_card(label, value, note=None):
    note_html = f'<div class="metric-note">{note}</div>' if note else ""
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div>{note_html}</div>', unsafe_allow_html=True)

def html_card(title, body, css_class="output-card"):
    st.markdown(f'<div class="{css_class}"><h3>{title}</h3>{body}</div>', unsafe_allow_html=True)

def value_statement(project_type):
    return {"Roof Replacement":"protecting the home from leaks, storm damage, and long-term structural issues","Roof Repair":"stopping the current issue before it turns into a larger problem","Siding":"protecting the wall system, improving curb appeal, and reducing maintenance concerns","Gutters":"moving water away from the home to protect fascia, foundation, and landscaping","Windows":"improving comfort, energy efficiency, and curb appeal","HVAC":"improving comfort, reliability, and energy performance","Pest Control":"protecting the home and preventing the issue from spreading","General Home Service":"protecting the home and creating a clear path forward","Other":"making sure the project is handled correctly"}.get(project_type, "making sure the project is handled correctly")

def calculate_priority(lead_status, urgency, financing, objection, project_type, days_since, intensity):
    score = 0
    score += 3 if lead_status in ["Estimate Presented", "Proposal Sent", "Verbal Yes / Pending Signature"] else 2 if lead_status in ["Inspection Completed", "Needs Follow-Up"] else 1
    score += {"Low":1,"Medium":2,"High":3}.get(urgency,1)
    score += 1 if financing == "Yes" else 0
    score += 1 if objection != "None" else 0
    score += 1 if project_type in ["Roof Replacement","Roof Repair","Siding","Gutters"] else 0
    score += 2 if days_since >= 7 else 1 if days_since >= 3 else 0
    score += 1 if intensity in ["Persistent","Last Attempt"] else 0
    if score >= 9: return "High Priority", "Follow up today", score
    if score >= 6: return "Medium Priority", "Follow up within 24 hours", score
    return "Low Priority", "Follow up within 48-72 hours", score

def priority_class(priority):
    return "status-high" if priority == "High Priority" else "status-medium" if priority == "Medium Priority" else "status-low"

def get_lead_temperature(priority, lead_status, days_since):
    if lead_status == "Verbal Yes / Pending Signature" or (priority == "High Priority" and days_since <= 3): return "Hot"
    if priority in ["High Priority","Medium Priority"]: return "Warm"
    return "Cool"

def get_deal_risk(objection, days_since, lead_status):
    if lead_status == "Closed Lost": return "High", "Closed-lost status"
    if days_since >= 7: return "High", "No recent contact"
    if objection in ["Price","Getting Other Quotes","Financing"]: return "Medium", f"{objection} resistance"
    if objection in ["Spouse / Decision Maker","Need to Think About It","Timing"]: return "Medium", f"{objection} delay"
    return "Low", "No major risk identified"

def next_best_action(inputs, priority, deal_risk):
    action = "Call first, then send a short recap text." if inputs["channel"] == "Phone Call" or priority == "High Priority" else "Send a concise text that asks for a clear next step." if inputs["channel"] == "Text" else "Send a recap email with the decision points and next step." if inputs["channel"] == "Email" else "Send a text and email, then call if there is no response."
    extras = {"Price":" Rebuild value before discussing any pricing change.","Spouse / Decision Maker":" Offer to review the decision with both decision-makers.","Financing":" Revisit payment options and clarify what part of financing is the concern.","Getting Other Quotes":" Help the customer compare scope, warranty, timeline, and trust instead of price alone."}
    action += extras.get(inputs["objection"], "")
    if inputs["days_since"] >= 7 or inputs["intensity"] == "Last Attempt": action += " Use a polite close-the-loop message so the opportunity does not stay open indefinitely."
    return action

def tone_opener(tone, greeting, company, project_type):
    options = {"Friendly":f"{greeting} this is a quick follow-up from {company}.","Professional":f"{greeting} this is a follow-up from {company} regarding your {project_type.lower()} project.","Urgent":f"{greeting} I wanted to follow up quickly so we can keep your {project_type.lower()} project moving.","Direct":f"{greeting} checking in from {company}.","Consultative":f"{greeting} I wanted to follow up and help you think through the best next step for your {project_type.lower()} project.","Reassuring":f"{greeting} I wanted to check in and make sure you feel comfortable with the next step for your {project_type.lower()} project.","High-Confidence":f"{greeting} I wanted to follow up because this is the right time to keep your {project_type.lower()} project moving forward.","No-Pressure":f"{greeting} no pressure at all — I just wanted to follow up from {company} and see what questions you still have."}
    return options.get(tone, options["Professional"])

def build_text_message(inputs):
    customer = inputs["customer"] or "there"; company = inputs["company"] or "our team"; project_type = inputs["project_type"]
    status_line = {"New Lead":"I wanted to help get the next step scheduled and learn more about what you are needing.","Inspection Scheduled":"I wanted to confirm we are still good for the appointment and answer any questions before we come out.","Inspection Completed":"I wanted to check in after the appointment and make sure the recommended next steps were clear.","Estimate Presented":"I wanted to see if you had any questions about the estimate, scope, or options we reviewed.","Proposal Sent":"I wanted to confirm you received the proposal and see if there is anything I can clarify.","Needs Follow-Up":"I wanted to reconnect and see what questions came up since we last spoke.","Verbal Yes / Pending Signature":"I wanted to help get the final step wrapped up so we can keep everything moving.","Closed Lost":"I wanted to thank you again for the opportunity. If anything changes, I would be happy to help."}.get(inputs["lead_status"], "I wanted to check in and help with the next step.")
    objection_line = f" I know {inputs['objection'].lower()} was one of the things you were thinking through, and I am happy to help make that clearer." if inputs["objection"] != "None" else ""
    close = "Should I keep this active for you, or would it be better for me to close out my follow-up for now?" if inputs["intensity"] == "Last Attempt" else "Can we set a quick time today to make a clear yes/no decision on the next step?" if inputs["intensity"] == "Persistent" else "Would you like me to help you review the next step?"
    return f"{tone_opener(inputs['tone'], f'Hi {customer},', company, project_type)} {status_line}{objection_line} The goal is really about {value_statement(project_type)}. {close}"

def build_email(inputs):
    customer = inputs["customer"] or "there"; company = inputs["company"] or "our team"; project_type = inputs["project_type"]
    subject = f"Following Up on Your {project_type} Project"
    body = f"Hi {customer},\n\nI wanted to follow up regarding your {project_type.lower()} project and see what questions you may have.\n\nThe main goal is {value_statement(project_type)}."
    if inputs["objection"] != "None": body += f"\n\nI know you mentioned {inputs['objection'].lower()}. That is understandable. My goal is not to pressure you, but to help make the decision clearer."
    if inputs["financing"] == "Yes": body += "\n\nWe can also revisit the payment options if that would make the project easier to plan around."
    body += f"\n\nWould it be helpful for me to walk you through the next step or answer any remaining questions?\n\nThanks again,\n{company}"
    return subject, body

def build_voicemail(inputs):
    return f"Hi {inputs['customer'] or 'there'}, this is {inputs['company'] or 'our team'}. I was calling to follow up on your {inputs['project_type'].lower()} project. I will send you a quick text as well, but I wanted to see if you had any questions or if you would like to review the next step. You can call or text me back whenever you get a chance. Thanks."

def objection_guidance(objection):
    return {"Price":"Rebuild value before discounting. Clarify scope, warranty, risk, financing, install quality, and cost of waiting.","Need to Think About It":"Ask what specifically they need to think through. Turn vague delay into a clear concern.","Getting Other Quotes":"Clarify what they are comparing: scope, warranty, install quality, timeline, payment options, and trust.","Spouse / Decision Maker":"Offer to recap the project for both decision-makers and schedule a short review conversation.","Timing":"Clarify whether timing means budget, schedule, urgency, or uncertainty. Offer a realistic next-step plan.","Financing":"Clarify whether the issue is approval, monthly payment, APR, term, or total project cost.","Other":"Ask a clarifying question to uncover the real concern, then guide the customer toward a clear next step.","None":"Keep the follow-up simple. Confirm questions, restate the next step, and ask for a clear decision."}.get(objection, "Ask a clarifying question to uncover the real concern.")

def manager_note(objection, priority):
    urgency = {"High Priority":"This lead should be treated as active pipeline and followed up today.","Medium Priority":"This lead should be followed up within 24 hours before momentum drops.","Low Priority":"This lead can be followed up within 48-72 hours, but should not be ignored."}.get(priority, "Review and assign a clear next step.")
    return f"{urgency} Coach the rep to clarify the true concern, rebuild value, and secure a specific next step."

def followup_sequence(inputs):
    customer = inputs["customer"] or "there"; project_type = inputs["project_type"].lower()
    if inputs["intensity"] == "Light Touch":
        return {"Touch 1: Today — Text":"Send a light check-in text.","Touch 2: Day 3 — Email":"Send a helpful recap email.","Touch 3: Day 7 — Text":"Close the loop gently if there is no response."}
    if inputs["intensity"] == "Last Attempt":
        return {"Touch 1: Today — Call + Text":"Try one direct call and a close-the-loop text.","Touch 2: Final Check-In":"Pause follow-up unless the customer re-engages."}
    return {"Touch 1: Today — Text + Call":f"Text and call {customer} about the {project_type} project.","Touch 2: Tomorrow — Email":"Send a recap email with value and next step.","Touch 3: Day 3 — Value Reminder":"Reframe the project around the customer’s main goal.","Touch 4: Day 7 — Final Check-In":"Ask whether to keep the project active or pause follow-up."}

def build_crm_note(inputs, priority, timing, temperature, risk, main_risk, next_action):
    return f"Customer: {inputs['customer'] or 'N/A'}\nCompany: {inputs['company'] or 'N/A'}\nProject Type: {inputs['project_type']}\nCurrent Status: {inputs['lead_status']}\nLead Temperature: {temperature}\nDeal Risk: {risk}\nMain Risk: {main_risk}\nPriority: {priority}\nUrgency Level: {inputs['urgency']}\nDays Since Last Contact: {inputs['days_since']}\nLast Interaction: {inputs['context'] or 'Not provided'}\nPrimary Concern/Objection: {inputs['objection']}\nFinancing Discussed: {inputs['financing']}\nRecommended Next Step: {timing}\nNext Best Action: {next_action}\nCRM Action: Follow up using generated workflow and update disposition after customer response."

def build_call_script(inputs):
    return f"Opening:\nHi, is this {inputs['customer'] or 'the customer'}? This is following up about your {inputs['project_type'].lower()} project.\n\nReason for call:\nI wanted to reconnect and help with the next step.\n\nDiscovery question:\nWhat is the main thing you are still trying to decide or feel comfortable with?\n\nValue reminder:\nThe main goal is {value_statement(inputs['project_type'])}.\n\nClose:\nWould it make sense to review the next step together while I have you?"

def ai_copy_prompt(inputs, outputs):
    return f"""
You are a sales follow-up assistant for a small business.
Improve the copy center outputs using the provided customer context and rules-based draft.
Keep the content concise, practical, professional, and specific.
Do not invent facts or discounts. Preserve the same business intent and next step.

Customer/deal context:
{inputs}

Rules-based outputs:
Text: {outputs['sms']}
Email subject: {outputs['subject']}
Email body: {outputs['email']}
Voicemail: {outputs['voicemail']}
CRM note: {outputs['crm']}
Manager coaching note: {outputs['coaching']}

Return exactly in this format:
TEXT:
...

EMAIL SUBJECT:
...

EMAIL BODY:
...

VOICEMAIL:
...

CRM NOTE:
...

MANAGER COACHING NOTE:
...
"""

def parse_ai_copy(raw, fallback):
    if not raw:
        return fallback
    sections = {"TEXT": "sms", "EMAIL SUBJECT": "subject", "EMAIL BODY": "email", "VOICEMAIL": "voicemail", "CRM NOTE": "crm", "MANAGER COACHING NOTE": "coaching"}
    parsed = fallback.copy()
    for heading, key in sections.items():
        start = raw.find(f"{heading}:")
        if start == -1:
            continue
        start += len(f"{heading}:")
        end_candidates = [raw.find(f"{next_heading}:", start) for next_heading in sections if next_heading != heading]
        end_candidates = [idx for idx in end_candidates if idx != -1]
        end = min(end_candidates) if end_candidates else len(raw)
        value = raw[start:end].strip()
        if value:
            parsed[key] = value
    return parsed

def enhance_outputs(inputs, outputs):
    cache_key = f"followup_copy_{hash(str(inputs))}"
    raw = enhance_text(ai_copy_prompt(inputs, outputs), "", cache_key)
    if not raw:
        return outputs
    enhanced = parse_ai_copy(raw, outputs)
    outputs.update(enhanced)
    return outputs

def build_report(inputs, outputs):
    sequence_lines = "\n\n".join(f"### {label}\n{message}" for label, message in outputs["sequence"].items())
    return f"# FollowUpPilot AI Follow-Up Plan\n\n## Customer\nCustomer: {inputs['customer'] or 'N/A'}\nCompany: {inputs['company'] or 'N/A'}\nProject Type: {inputs['project_type']}\nLead Status: {inputs['lead_status']}\nLead Temperature: {outputs['temperature']}\nDeal Risk: {outputs['deal_risk']}\nMain Risk: {outputs['main_risk']}\nPriority: {outputs['priority']}\nPriority Score: {outputs['score']}\nRecommended Timing: {outputs['timing']}\nNext Best Action: {outputs['next_action']}\n\n## Why This Recommendation\n{outputs['why']}\n\n## Text Message\n{outputs['sms']}\n\n## Email\nSubject: {outputs['subject']}\n\n{outputs['email']}\n\n## Voicemail Script\n{outputs['voicemail']}\n\n## CRM Note\n{outputs['crm']}\n\n## Call Script\n{outputs['call']}\n\n## Objection Guidance\n{outputs['guidance']}\n\n## Manager Coaching Note\n{outputs['coaching']}\n\n## Follow-Up Sequence\n\n{sequence_lines}\n\n---\n\nGenerated by FollowUpPilot AI."

with st.sidebar:
    st.title("FollowUpPilot AI"); st.caption("Version 2.5")
    st.markdown("Sales follow-up workflow automation for field-sales and home-service teams.")
    st.divider(); st.markdown("### Outputs")
    st.markdown("- Lead temperature\n- Deal risk\n- Copy center\n- Timeline\n- CRM note / call script\n- Objection guidance\n- PDF follow-up plan")

st.markdown('<div class="hero"><div class="eyebrow">Sales Follow-Up Workflow Tool</div><div class="hero-title">FollowUpPilot AI</div><div class="hero-subtitle">Turn customer context into next-best actions, follow-up messages, CRM notes, call scripts, objection guidance, manager coaching notes, and multi-touch sequences.</div><div class="hero-pills"><span>Sales Execution</span><span>CRM Discipline</span><span>Follow-Up</span><span>Next Best Action</span><span>Streamlit</span></div></div>', unsafe_allow_html=True)
section_title("Customer follow-up builder", "Load a sample scenario or enter your own customer context. The app will generate a complete follow-up workflow.")
scenario_name = st.selectbox("Load Sample Scenario", list(SAMPLE_SCENARIOS.keys()))
scenario = SAMPLE_SCENARIOS.get(scenario_name, {})

with st.form("followup_form"):
    form_group("Customer and project details")
    a,b = st.columns(2)
    with a: customer = st.text_input("Customer Name", value=scenario.get("customer", ""), placeholder="Example: Avery Johnson")
    with b: company = st.text_input("Company Name", value=scenario.get("company", ""), placeholder="Example: Summit Home Services")
    c,d = st.columns(2)
    with c: project_type = st.selectbox("Project Type", PROJECT_TYPES, index=PROJECT_TYPES.index(scenario.get("project_type", "Roof Replacement")))
    with d: lead_status = st.selectbox("Lead Status", LEAD_STATUSES, index=LEAD_STATUSES.index(scenario.get("lead_status", "Estimate Presented")))
    form_group("Last interaction")
    context = st.text_area("Last Interaction / Context", value=scenario.get("context", ""), height=120)
    form_group("Follow-up strategy")
    e,f,g,h = st.columns(4)
    with e: objection = st.selectbox("Main Concern", OBJECTIONS, index=OBJECTIONS.index(scenario.get("objection", "Price")))
    with f: financing = st.selectbox("Financing?", FINANCING_OPTIONS, index=FINANCING_OPTIONS.index(scenario.get("financing", "No")))
    with g: urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=URGENCY_LEVELS.index(scenario.get("urgency", "Medium")))
    with h: tone = st.selectbox("Tone", TONES, index=TONES.index(scenario.get("tone", "Professional")))
    i,j,k = st.columns(3)
    with i: days_since = st.number_input("Days Since Last Contact", min_value=0, max_value=90, value=int(scenario.get("days_since", 1)), step=1)
    with j: intensity = st.selectbox("Follow-Up Intensity", FOLLOWUP_INTENSITIES, index=FOLLOWUP_INTENSITIES.index(scenario.get("intensity", "Standard")))
    with k: channel = st.selectbox("Preferred Channel", CHANNEL_OPTIONS, index=CHANNEL_OPTIONS.index(scenario.get("channel", "All")))
    submitted = st.form_submit_button("Generate Follow-Up Plan", use_container_width=True)

if not submitted:
    st.markdown('<div class="note-box">Complete the form or load a sample scenario, then click Generate Follow-Up Plan.</div>', unsafe_allow_html=True)
    st.stop()

inputs = {"customer": customer, "company": company, "project_type": project_type, "lead_status": lead_status, "context": context, "objection": objection, "financing": financing, "urgency": urgency, "tone": tone, "days_since": int(days_since), "intensity": intensity, "channel": channel}
priority, timing, score = calculate_priority(lead_status, urgency, financing, objection, project_type, int(days_since), intensity)
temperature = get_lead_temperature(priority, lead_status, int(days_since))
deal_risk, main_risk = get_deal_risk(objection, int(days_since), lead_status)
next_action = next_best_action(inputs, priority, deal_risk)
why = f"This lead is marked {priority} with a score of {score} because the status is {lead_status}, urgency is {urgency.lower()}, main concern is {objection.lower()}, and it has been {days_since} day(s) since last contact."
sms = build_text_message(inputs); subject, email = build_email(inputs); voicemail = build_voicemail(inputs); crm = build_crm_note(inputs, priority, timing, temperature, deal_risk, main_risk, next_action); call = build_call_script(inputs); guidance = objection_guidance(objection); coaching = manager_note(objection, priority); sequence = followup_sequence(inputs)
outputs = {"priority":priority,"timing":timing,"score":score,"temperature":temperature,"deal_risk":deal_risk,"main_risk":main_risk,"next_action":next_action,"why":why,"sms":sms,"subject":subject,"email":email,"voicemail":voicemail,"guidance":guidance,"coaching":coaching,"sequence":sequence,"crm":crm,"call":call}
outputs = enhance_outputs(inputs, outputs)

section_title("Follow-up recommendation")
c1,c2,c3,c4 = st.columns(4)
with c1: metric_card("Priority", priority, f"Score: {score}")
with c2: metric_card("Lead Temperature", temperature)
with c3: metric_card("Deal Risk", deal_risk, main_risk)
with c4: metric_card("Timing", timing)
html_card("Next Best Action", f'<span class="status-pill {priority_class(priority)}">{priority}</span><p>{next_action}</p>', "nba-card")
html_card("Why This Recommendation", f"<p>{why}</p>", "guidance-card")

section_title("Copy center", "Use this section when the rep needs the fastest copy-ready outputs.")
copy_tabs = st.tabs(["Send this text", "Send this email", "Leave this voicemail", "Add this CRM note", "Manager coaching note"])
with copy_tabs[0]: st.text_area("Text", outputs["sms"], height=145)
with copy_tabs[1]:
    st.text_input("Email Subject", outputs["subject"])
    st.text_area("Email Body", outputs["email"], height=260)
with copy_tabs[2]: st.text_area("Voicemail", outputs["voicemail"], height=145)
with copy_tabs[3]: st.text_area("CRM Note", outputs["crm"], height=260)
with copy_tabs[4]: st.text_area("Manager Coaching Note", outputs["coaching"], height=145)

section_title("Follow-up timeline")
cols = st.columns(2)
for pos, (label, message) in enumerate(sequence.items()):
    with cols[pos % 2]: html_card(label, f"<p>{message}</p>", "sequence-card")

section_title("Call workflow and objection guidance")
t1,t2 = st.columns(2)
with t1: st.text_area("Call script", call, height=300)
with t2:
    html_card("Objection Guidance", f"<p>{guidance}</p>", "guidance-card")

section_title("Download follow-up plan")
report = build_report(inputs, outputs)
pdf_report = markdown_to_pdf(report, title="FollowUpPilot AI Follow-Up Plan")
st.download_button("Download Follow-Up Plan PDF", data=pdf_report, file_name="followuppilot-follow-up-plan.pdf", mime="application/pdf", use_container_width=True)

section_title("What this app demonstrates")
html_card("Portfolio Skills Shown", "<ul><li>AI-enhanced communication with rules-based fallback</li><li>Workflow mapping</li><li>Rules-based next-best-action logic</li><li>Sales communication generation</li><li>CRM documentation support</li><li>User-friendly PDF reporting</li></ul>", "workflow-card")

with st.expander("How to use FollowUpPilot AI"):
    st.markdown("1. Load a sample scenario or enter your own customer/project context.\n2. Generate the follow-up plan.\n3. Use the Copy Center for text, email, voicemail, CRM note, and coaching note.\n4. Review the follow-up timeline.\n5. Download the PDF follow-up plan for CRM documentation or team coaching.")
st.markdown('<div class="note-box">Privacy note: Information entered into this app is processed during the active session and is not saved by this app.</div>', unsafe_allow_html=True)
