import streamlit as st

from ai_helpers import enhance_text, stable_cache_key
from core.followup_logic import run_followup_workflow
from core.prompts import ai_copy_prompt, parse_ai_copy
from core.report_builder import build_report
from data.sample_data import (
    CHANNEL_OPTIONS,
    FINANCING_OPTIONS,
    FOLLOWUP_INTENSITIES,
    LEAD_STATUSES,
    OBJECTIONS,
    PROJECT_TYPES,
    SAMPLE_SCENARIOS,
    TONES,
    URGENCY_LEVELS,
)
from pdf_helpers import markdown_to_pdf

st.set_page_config(page_title="FollowUpPilot AI", page_icon="💬", layout="wide")

CSS = """
<style>
.block-container{max-width:1180px;padding-top:1.35rem;padding-bottom:3rem}[data-testid="stSidebar"]{background:#111827}[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] li,[data-testid="stSidebar"] ul,[data-testid="stSidebar"] ol{color:#f9fafb!important}[data-testid="stSidebar"] li::marker{color:#93c5fd!important}.hero{padding:1.9rem 2rem;border-radius:20px;background:linear-gradient(135deg,#111827 0%,#1f2937 52%,#334155 100%);color:#fff;box-shadow:0 18px 36px rgba(17,24,39,.18);margin-bottom:1rem;border:1px solid rgba(255,255,255,.08)}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.75rem;font-weight:800;color:#93c5fd;margin-bottom:.65rem}.hero-title{font-size:2.25rem;line-height:1.08;font-weight:850;margin-bottom:.65rem}.hero-subtitle{font-size:1.02rem;line-height:1.62;color:#e5e7eb;max-width:900px}.hero-pills span{display:inline-block;padding:.35rem .65rem;margin:.75rem .28rem 0 0;border-radius:999px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);font-weight:700;font-size:.78rem;color:#f8fafc}.section-title{margin-top:1.25rem;margin-bottom:.55rem;font-size:1.4rem;font-weight:850;color:#111827}.section-lede{color:#4b5563;line-height:1.6;margin-bottom:1rem;max-width:950px}.form-group-title{font-size:.9rem;font-weight:850;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin:.35rem 0 .15rem 0}.metric-card,.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 8px 20px rgba(15,23,42,.055)}.metric-card{height:138px;padding:1rem;margin-bottom:.75rem}.metric-label{color:#6b7280;font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}.metric-value{color:#111827;font-size:1.35rem;line-height:1.18;font-weight:900;overflow-wrap:break-word}.metric-note{color:#64748b;font-size:.85rem;margin-top:.55rem}.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card{padding:1.15rem;margin-bottom:.8rem}.output-card{border-left:5px solid #111827}.guidance-card,.workflow-card{border-left:5px solid #1d4ed8}.sequence-card{border-left:5px solid #059669}.nba-card{border-left:5px solid #111827;background:#f8fafc}.output-card h3,.guidance-card h3,.sequence-card h3,.workflow-card h3,.nba-card h3{font-size:1.05rem;font-weight:850;color:#111827;margin-bottom:.4rem}.output-card p,.guidance-card p,.sequence-card p,.workflow-card p,.nba-card p,.output-card li,.guidance-card li,.sequence-card li,.workflow-card li,.nba-card li{color:#4b5563;line-height:1.52;font-size:.93rem}.status-high{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}.status-medium{background:#fef3c7;color:#92400e;border:1px solid #fde68a}.status-low{background:#d1fae5;color:#065f46;border:1px solid #a7f3d0}.status-pill{display:inline-block;padding:.25rem .6rem;border-radius:999px;font-weight:850;font-size:.78rem;margin-bottom:.5rem}.note-box{padding:.9rem 1rem;border-radius:14px;background:#f8fafc;color:#334155;border:1px solid #e2e8f0;font-weight:650;margin:.9rem 0;font-size:.92rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PRIVACY_NOTE = "Privacy note: Use fictional/sample data for public demos. Do not enter sensitive, confidential, or regulated customer information. If AI is enabled, entered text may be processed by the configured AI provider for output enhancement."


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


def priority_class(priority: str) -> str:
    if priority == "High Priority":
        return "status-high"
    if priority == "Medium Priority":
        return "status-medium"
    return "status-low"


def render_sidebar() -> None:
    with st.sidebar:
        st.title("FollowUpPilot AI")
        st.caption("Version 2.6")
        st.markdown("Sales follow-up workflow automation for field-sales and home-service teams.")
        st.divider()
        st.markdown("### Outputs")
        st.markdown("- Lead temperature\n- Deal risk\n- Copy center\n- Timeline\n- CRM note / call script\n- Objection guidance\n- PDF follow-up plan")


def render_hero() -> None:
    st.markdown(
        '<div class="hero"><div class="eyebrow">Sales Follow-Up Workflow Tool</div><div class="hero-title">FollowUpPilot AI</div><div class="hero-subtitle">Turn customer context into next-best actions, follow-up messages, CRM notes, call scripts, objection guidance, manager coaching notes, and multi-touch sequences.</div><div class="hero-pills"><span>Sales Execution</span><span>CRM Discipline</span><span>Follow-Up</span><span>Next Best Action</span><span>Streamlit</span></div></div>',
        unsafe_allow_html=True,
    )


def build_inputs(scenario: dict) -> dict | None:
    with st.form("followup_form"):
        form_group("Customer and project details")
        a, b = st.columns(2)
        with a:
            customer = st.text_input("Customer Name", value=scenario.get("customer", ""), placeholder="Example: Avery Johnson")
        with b:
            company = st.text_input("Company Name", value=scenario.get("company", ""), placeholder="Example: Summit Home Services")
        c, d = st.columns(2)
        with c:
            project_type = st.selectbox("Project Type", PROJECT_TYPES, index=PROJECT_TYPES.index(scenario.get("project_type", "Roof Replacement")))
        with d:
            lead_status = st.selectbox("Lead Status", LEAD_STATUSES, index=LEAD_STATUSES.index(scenario.get("lead_status", "Estimate Presented")))

        form_group("Last interaction")
        context = st.text_area("Last Interaction / Context", value=scenario.get("context", ""), height=120, max_chars=4000)

        form_group("Follow-up strategy")
        e, f, g, h = st.columns(4)
        with e:
            objection = st.selectbox("Main Concern", OBJECTIONS, index=OBJECTIONS.index(scenario.get("objection", "Price")))
        with f:
            financing = st.selectbox("Financing?", FINANCING_OPTIONS, index=FINANCING_OPTIONS.index(scenario.get("financing", "No")))
        with g:
            urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=URGENCY_LEVELS.index(scenario.get("urgency", "Medium")))
        with h:
            tone = st.selectbox("Tone", TONES, index=TONES.index(scenario.get("tone", "Professional")))
        i, j, k = st.columns(3)
        with i:
            days_since = st.number_input("Days Since Last Contact", min_value=0, max_value=90, value=int(scenario.get("days_since", 1)), step=1)
        with j:
            intensity = st.selectbox("Follow-Up Intensity", FOLLOWUP_INTENSITIES, index=FOLLOWUP_INTENSITIES.index(scenario.get("intensity", "Standard")))
        with k:
            channel = st.selectbox("Preferred Channel", CHANNEL_OPTIONS, index=CHANNEL_OPTIONS.index(scenario.get("channel", "All")))
        submitted = st.form_submit_button("Generate Follow-Up Plan", use_container_width=True)

    if not submitted:
        return None

    return {
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


def enhance_outputs(inputs: dict, outputs: dict) -> dict:
    raw = enhance_text(
        ai_copy_prompt(inputs, outputs),
        "",
        stable_cache_key("followup_copy", inputs),
    )
    if not raw:
        return outputs
    enhanced = parse_ai_copy(raw, outputs)
    outputs.update(enhanced)
    return outputs


def render_results(outputs: dict) -> None:
    section_title("Follow-up recommendation")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Priority", outputs["priority"], f"Score: {outputs['score']}")
    with c2:
        metric_card("Lead Temperature", outputs["temperature"])
    with c3:
        metric_card("Deal Risk", outputs["deal_risk"], outputs["main_risk"])
    with c4:
        metric_card("Timing", outputs["timing"])

    html_card("Next Best Action", f'<span class="status-pill {priority_class(outputs["priority"])}">{outputs["priority"]}</span><p>{outputs["next_action"]}</p>', "nba-card")
    html_card("Why This Recommendation", f"<p>{outputs['why']}</p>", "guidance-card")

    section_title("Copy center", "Use this section when the rep needs the fastest copy-ready outputs.")
    copy_tabs = st.tabs(["Send this text", "Send this email", "Leave this voicemail", "Add this CRM note", "Manager coaching note"])
    with copy_tabs[0]:
        st.text_area("Text", outputs["sms"], height=145)
    with copy_tabs[1]:
        st.text_input("Email Subject", outputs["subject"])
        st.text_area("Email Body", outputs["email"], height=260)
    with copy_tabs[2]:
        st.text_area("Voicemail", outputs["voicemail"], height=145)
    with copy_tabs[3]:
        st.text_area("CRM Note", outputs["crm"], height=260)
    with copy_tabs[4]:
        st.text_area("Manager Coaching Note", outputs["coaching"], height=145)

    section_title("Follow-up timeline")
    cols = st.columns(2)
    for pos, (label, message) in enumerate(outputs["sequence"].items()):
        with cols[pos % 2]:
            html_card(label, f"<p>{message}</p>", "sequence-card")

    section_title("Call workflow and objection guidance")
    t1, t2 = st.columns(2)
    with t1:
        st.text_area("Call script", outputs["call"], height=300)
    with t2:
        html_card("Objection Guidance", f"<p>{outputs['guidance']}</p>", "guidance-card")


def main() -> None:
    render_sidebar()
    render_hero()

    section_title("Customer follow-up builder", "Load a sample scenario or enter your own customer context. The app will generate a complete follow-up workflow.")
    st.markdown(f'<div class="note-box">{PRIVACY_NOTE}</div>', unsafe_allow_html=True)

    scenario_name = st.selectbox("Load Sample Scenario", list(SAMPLE_SCENARIOS.keys()))
    scenario = SAMPLE_SCENARIOS.get(scenario_name, {})
    inputs = build_inputs(scenario)

    if inputs is None:
        st.markdown('<div class="note-box">Complete the form or load a sample scenario, then click Generate Follow-Up Plan.</div>', unsafe_allow_html=True)
        return

    outputs = enhance_outputs(inputs, run_followup_workflow(inputs))
    render_results(outputs)

    section_title("Download follow-up plan")
    report = build_report(inputs, outputs)
    pdf_report = markdown_to_pdf(report, title="FollowUpPilot AI Follow-Up Plan")
    st.download_button("Download Follow-Up Plan PDF", data=pdf_report, file_name="followuppilot-follow-up-plan.pdf", mime="application/pdf", use_container_width=True)

    section_title("What this app demonstrates")
    html_card(
        "Portfolio Skills Shown",
        "<ul><li>Modular Streamlit architecture</li><li>AI-enhanced communication with rules-based fallback</li><li>Workflow mapping</li><li>Rules-based next-best-action logic</li><li>Sales communication generation</li><li>User-friendly PDF reporting</li></ul>",
        "workflow-card",
    )

    with st.expander("How to use FollowUpPilot AI"):
        st.markdown("1. Load a sample scenario or enter your own customer/project context.\n2. Generate the follow-up plan.\n3. Use the Copy Center for text, email, voicemail, CRM note, and coaching note.\n4. Review the follow-up timeline.\n5. Download the PDF follow-up plan for CRM documentation or team coaching.")
    st.markdown(f'<div class="note-box">{PRIVACY_NOTE}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
