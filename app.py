import streamlit as st

st.set_page_config(page_title="FollowUpPilot AI", page_icon="💬", layout="wide")

def value_statement(project_type):
    values = {
        "Roof Replacement": "protecting the home from leaks, storm damage, and long-term structural issues",
        "Roof Repair": "stopping the current issue before it turns into a larger problem",
        "Siding": "protecting the wall system, improving curb appeal, and reducing maintenance concerns",
        "Gutters": "moving water away from the home to protect fascia, foundation, and landscaping",
        "Windows": "improving comfort, energy efficiency, and curb appeal",
        "HVAC": "improving comfort, reliability, and energy performance",
        "Pest Control": "protecting the home and preventing the issue from spreading",
        "General Home Service": "protecting the home and creating a clear path forward",
        "Other": "making sure the project is handled correctly"
    }
    return values.get(project_type, "making sure the project is handled correctly")

def priority_logic(lead_status, urgency, financing, objection, project_type):
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

def text_message(customer, company, project_type, lead_status, objection, tone, context):
    greeting = f"Hi {customer}," if customer else "Hi,"
    company = company or "our team"
    value = value_statement(project_type)

    opener = {
        "Friendly": f"{greeting} this is a quick follow-up from {company}.",
        "Professional": f"{greeting} this is a follow-up from {company} regarding your {project_type.lower()} project.",
        "Urgent": f"{greeting} I wanted to follow up quickly so we can keep your {project_type.lower()} project moving.",
        "Direct": f"{greeting} checking in from {company}."
    }.get(tone, f"{greeting} checking in from {company}.")

    status = {
        "New Lead": "I wanted to help get the next step scheduled and learn more about what you are needing.",
        "Inspection Scheduled": "I wanted to confirm we are still good for the inspection and answer any questions before we come out.",
        "Inspection Completed": "I wanted to check in after the inspection and make sure the recommended next steps were clear.",
        "Estimate Presented": "I wanted to see if you had any questions about the estimate, scope, or options we reviewed.",
        "Proposal Sent": "I wanted to confirm you received the proposal and see if there is anything I can clarify.",
        "Needs Follow-Up": "I wanted to reconnect and see what questions came up since we last spoke.",
        "Verbal Yes / Pending Signature": "I wanted to help get the final step wrapped up so we can keep everything moving.",
        "Closed Lost": "I wanted to thank you again for the opportunity. If anything changes, I would be happy to help."
    }.get(lead_status, "I wanted to check in and help with the next step.")

    objection_line = ""
    if objection != "None":
        objection_line = f" I know {objection.lower()} was one of the things you were thinking through, and I am happy to help make that clearer."

    value_line = f" The goal is really about {value}." if context else ""

    return f"{opener} {status}{objection_line}{value_line} Would you like me to help you review the next step?"

def email_message(customer, company, project_type, lead_status, objection, financing, tone, context):
    greeting = f"Hi {customer}," if customer else "Hi,"
    company = company or "our team"
    subject = {
        "New Lead": f"Next Step for Your {project_type} Project",
        "Inspection Scheduled": f"Confirming Your {project_type} Inspection",
        "Inspection Completed": f"Following Up After Your {project_type} Inspection",
        "Estimate Presented": f"Following Up on Your {project_type} Estimate",
        "Proposal Sent": f"Checking In on Your {project_type} Proposal",
        "Needs Follow-Up": f"Quick Follow-Up on Your {project_type} Project",
        "Verbal Yes / Pending Signature": f"Final Step for Your {project_type} Project",
        "Closed Lost": "Thank You for Considering Us"
    }.get(lead_status, f"Following Up on Your {project_type} Project")

    intro = f"I wanted to follow up regarding your {project_type.lower()} project and see what questions you may have."
    if tone == "Urgent":
        intro = f"I wanted to follow up quickly regarding your {project_type.lower()} project so we can keep the next step from getting delayed."
    elif tone == "Direct":
        intro = f"I wanted to follow up on your {project_type.lower()} project and help determine the next step."

    value = value_statement(project_type)
    body = f"{greeting}\n\n{intro}\n\nThe main goal is {value}."

    if objection != "None":
        body += f"\n\nI know you mentioned {objection.lower()}. That is understandable. My goal is not to pressure you, but to help make the decision clearer."
    if financing == "Yes":
        body += "\n\nWe can also revisit the payment options if that would make the project easier to plan around."

    body += f"\n\nWould it be helpful for me to walk you through the next step or answer any remaining questions?\n\nThanks again,\n{company}"
    return subject, body

def objection_guidance(objection):
    guidance = {
        "Price": "Rebuild value before discounting. Clarify scope, warranty, risk, financing, install quality, and cost of waiting.",
        "Need to Think About It": "Ask what specifically they need to think through. Turn vague delay into a clear concern.",
        "Getting Other Quotes": "Clarify what they are comparing: scope, warranty, install quality, timeline, payment options, and trust.",
        "Spouse / Decision Maker": "Offer to recap the project for both decision-makers and schedule a short review conversation.",
        "Timing": "Clarify whether timing means budget, schedule, urgency, or uncertainty. Offer a realistic next-step plan.",
        "Financing": "Clarify whether the issue is approval, monthly payment, APR, term, or total project cost.",
        "Other": "Ask a clarifying question to uncover the real concern, then guide the customer toward a clear next step.",
        "None": "Keep the follow-up simple. Confirm questions, restate the next step, and ask for a clear decision."
    }
    return guidance.get(objection, guidance["Other"])

def manager_note(objection, priority):
    if priority == "High Priority":
        urgency = "This lead should be treated as active pipeline and followed up today."
    elif priority == "Medium Priority":
        urgency = "This lead should be followed up within 24 hours before momentum drops."
    else:
        urgency = "This lead can be followed up within 48-72 hours, but should not be ignored."

    coaching = {
        "Price": "Coach the rep to rebuild value, clarify scope, and revisit financing before discounting.",
        "Getting Other Quotes": "Coach the rep to compare scope, warranty, install quality, timeline, and trust instead of price alone.",
        "Need to Think About It": "Coach the rep to ask what specifically needs to be thought through.",
        "Spouse / Decision Maker": "Coach the rep to involve decision-makers earlier and offer a clear recap.",
        "Financing": "Coach the rep to clarify if the issue is payment, approval, APR, term, or total cost.",
    }.get(objection, "Coach the rep to ask better discovery questions and secure a clear next step.")
    return urgency + " " + coaching

def followup_sequence(customer, company, project_type, objection):
    name = customer or "there"
    company = company or "our team"
    day0 = f"Hi {name}, this is {company}. Just checking in on your {project_type.lower()} project to see if you had any questions or wanted help with the next step."
    day1 = f"Hi {name}, I wanted to follow up again and make sure nothing was left unclear from our last conversation about the {project_type.lower()} project."
    if objection != "None":
        day1 += f" I remember {objection.lower()} was one of the things you were considering, and I am happy to walk through that."
    day3 = f"Hi {name}, I know these projects can take some thought. Is there anything specific holding you back that I can help clarify?"
    day7 = f"Hi {name}, I did not want to let this fall through the cracks. Would you like to keep the {project_type.lower()} project active, or should I close out my follow-up for now?"
    return {"Same Day": day0, "Next Day": day1, "Day 3": day3, "Day 7": day7}

st.title("💬 FollowUpPilot AI")
st.subheader("AI-assisted follow-up workflow tool for field-sales and home-service teams")
st.markdown("FollowUpPilot AI turns customer context into follow-up texts, emails, CRM notes, call scripts, objection guidance, follow-up sequences, and next-step plans.")

st.sidebar.title("FollowUpPilot AI")
st.sidebar.caption("Version 1.1 MVP")
st.sidebar.markdown("**Built by Bradley Hankins**\n\nA practical AI workflow automation tool for sales follow-up, CRM discipline, and customer communication.")
st.sidebar.divider()

with st.sidebar.expander("What this app generates"):
    st.markdown("- Text message\n- Email\n- CRM note\n- Call script\n- Objection guidance\n- Manager coaching note\n- Follow-up sequence\n- Downloadable plan")

st.header("Customer Follow-Up Builder")

with st.form("followup_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("Customer Name", placeholder="Example: Heather")
        company = st.text_input("Company Name", placeholder="Example: Summit Home Services")
        project_type = st.selectbox("Project Type", ["Roof Replacement", "Roof Repair", "Siding", "Gutters", "Windows", "HVAC", "Pest Control", "General Home Service", "Other"])
        lead_status = st.selectbox("Lead Status", ["New Lead", "Inspection Scheduled", "Inspection Completed", "Estimate Presented", "Proposal Sent", "Needs Follow-Up", "Verbal Yes / Pending Signature", "Closed Lost"])
    with col2:
        context = st.text_area("Last Interaction / Context", placeholder="Example: Customer liked the siding option but wanted to think about color and monthly payment.")
        objection = st.selectbox("Main Concern / Objection", ["None", "Price", "Need to Think About It", "Getting Other Quotes", "Spouse / Decision Maker", "Timing", "Financing", "Other"])
        financing = st.selectbox("Financing Discussed?", ["No", "Yes"])
        urgency = st.selectbox("Urgency Level", ["Low", "Medium", "High"])
        tone = st.selectbox("Preferred Tone", ["Friendly", "Professional", "Urgent", "Direct"])
    submitted = st.form_submit_button("Generate Follow-Up Plan")

if submitted:
    priority, timing, score = priority_logic(lead_status, urgency, financing, objection, project_type)
    sms = text_message(customer, company, project_type, lead_status, objection, tone, context)
    subject, email = email_message(customer, company, project_type, lead_status, objection, financing, tone, context)
    guidance = objection_guidance(objection)
    coaching = manager_note(objection, priority)
    sequence = followup_sequence(customer, company, project_type, objection)

    crm = f"""Customer: {customer or "N/A"}
Project Type: {project_type}
Current Status: {lead_status}
Priority: {priority}
Urgency Level: {urgency}
Last Interaction: {context or "Not provided"}
Primary Concern/Objection: {objection}
Financing Discussed: {financing}
Recommended Next Step: {timing}
CRM Action: Follow up using generated text/email and update disposition after customer response.
"""

    call = f"""Opening:
Hi, is this {customer or "the homeowner"}? This is following up about your {project_type.lower()} project.

Reason for call:
I wanted to reconnect and help with the next step.

Discovery question:
What is the main thing you are still trying to decide or feel comfortable with?

Value reminder:
The main goal is {value_statement(project_type)}, and I want to make sure you have a clear path forward.

Close:
Would it make sense to review the next step together while I have you?
"""

    st.divider()
    st.header("Follow-Up Recommendation")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Priority", priority)
    c2.metric("Recommended Timing", timing)
    c3.metric("Lead Status", lead_status)
    c4.metric("Priority Score", score)

    st.subheader("Customer Text Message")
    st.text_area("Copy-ready text message", sms, height=140)

    st.subheader("Customer Email")
    st.text_input("Subject Line", subject)
    st.text_area("Copy-ready email", email, height=300)

    st.subheader("CRM Note")
    st.text_area("CRM-ready note", crm, height=240)

    st.subheader("Call Script")
    st.text_area("Call script", call, height=280)

    st.subheader("Objection Guidance")
    st.info(guidance)

    st.subheader("Manager Coaching Note")
    st.warning(coaching)

    st.subheader("Suggested Follow-Up Sequence")
    for timing_label, msg in sequence.items():
        st.markdown(f"**{timing_label}**")
        st.text_area(f"{timing_label} message", msg, height=100)

    report = f"""# FollowUpPilot AI Follow-Up Plan

## Customer
Customer: {customer or "N/A"}
Company: {company or "N/A"}
Project Type: {project_type}
Lead Status: {lead_status}
Priority: {priority}
Priority Score: {score}
Recommended Timing: {timing}

## Context
{context or "No context provided."}

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

### Same Day
{sequence["Same Day"]}

### Next Day
{sequence["Next Day"]}

### Day 3
{sequence["Day 3"]}

### Day 7
{sequence["Day 7"]}

---
Generated by FollowUpPilot AI.
"""
    st.download_button("Download Follow-Up Plan", data=report, file_name="followuppilot-follow-up-plan.md", mime="text/markdown")
else:
    st.info("Complete the form and click Generate Follow-Up Plan to create customer communication, CRM notes, and next-step recommendations.")

st.divider()
st.header("Built for Practical AI Workflow Automation")
st.markdown("FollowUpPilot AI is a portfolio project demonstrating how AI-assisted workflows can reduce repetitive sales admin work, standardize customer communication, improve CRM note quality, and help managers create better follow-up discipline.")
st.info("Privacy note: Information entered into this app is processed during the active session and is not saved by this app.")
