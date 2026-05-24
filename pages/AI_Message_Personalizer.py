import streamlit as st

from ai_helpers import generate_ai_text

st.set_page_config(page_title="FollowUpPilot AI - AI Message Personalizer", page_icon="💬", layout="wide")

st.title("AI Message Personalizer")
st.caption("Optional AI enhancement for rewriting follow-up messages from customer context.")

st.info(
    "This page is optional. The main FollowUpPilot workflow still works without AI. "
    "Set OPENAI_TOKEN in the deployment environment to enable AI output."
)

customer_context = st.text_area(
    "Customer / deal context",
    height=180,
    placeholder="Example: Customer liked the proposal but said price was higher than expected and needs to talk to spouse.",
)
message_goal = st.selectbox(
    "Message goal",
    ["Text message", "Email", "Voicemail script", "CRM note", "Final follow-up", "Objection response"],
)
tone = st.selectbox(
    "Tone",
    ["Friendly", "Professional", "Consultative", "Direct", "High-confidence", "No-pressure", "Reassuring"],
)
notes = st.text_area(
    "Rules-based output or draft to improve",
    height=160,
    placeholder="Paste the draft message from FollowUpPilot or write a rough draft here.",
)

if st.button("Generate AI Personalized Message", use_container_width=True):
    prompt = f"""
You are a sales follow-up assistant for a small business.
Rewrite the message using the customer context, goal, and tone.
Keep it professional, concise, specific, and action-oriented.
Do not invent facts that are not provided.

Customer context:
{customer_context}

Message goal:
{message_goal}

Tone:
{tone}

Draft or rules-based output:
{notes}

Return:
1. Recommended message
2. Why this wording works
3. Suggested next action
"""
    with st.spinner("Generating AI message..."):
        st.markdown(generate_ai_text(prompt))

st.divider()
st.markdown(
    "**AI positioning:** This page adds a natural-language personalization layer on top of the rules-based FollowUpPilot workflow."
)
