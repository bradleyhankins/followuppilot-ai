from __future__ import annotations

from datetime import date, timedelta
from html import escape

import streamlit as st

from ai_helpers import enhance_text, stable_cache_key
from core.followup_logic import run_followup_workflow
from core.models import LeadInput
from core.prompts import ai_copy_prompt, parse_ai_copy
from core.report_builder import build_report
from core.validation import validate_lead_input
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

st.set_page_config(page_title="FollowUpPilot AI", page_icon="FP", layout="wide")

CSS = """
<style>
.block-container{max-width:1180px;padding-top:1.35rem;padding-bottom:3rem}[data-testid="stSidebar"]{background:#111827}[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] li,[data-testid="stSidebar"] ul,[data-testid="stSidebar"] ol{color:#f9fafb!important}[data-testid="stSidebar"] li::marker{color:#93c5fd!important}.hero{padding:1.9rem 2rem;border-radius:20px;background:linear-gradient(135deg,#111827 0%,#1f2937 52%,#334155 100%);color:#fff;box-shadow:0 18px 36px rgba(17,24,39,.18);margin-bottom:1rem;border:1px solid rgba(255,255,255,.08)}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.75rem;font-weight:800;color:#93c5fd;margin-bottom:.65rem}.hero-title{font-size:2.25rem;line-height:1.08;font-weight:850;margin-bottom:.65rem}.hero-subtitle{font-size:1.02rem;line-height:1.62;color:#e5e7eb;max-width:900px}.hero-pills span{display:inline-block;padding:.35rem .65rem;margin:.75rem .28rem 0 0;border-radius:999px;background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);font-weight:700;font-size:.78rem;color:#f8fafc}.section-title{margin-top:1.25rem;margin-bottom:.55rem;font-size:1.4rem;font-weight:850;color:#111827}.section-lede{color:#4b5563;line-height:1.6;margin-bottom:1rem;max-width:950px}.form-group-title{font-size:.9rem;font-weight:850;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin:.35rem 0 .15rem 0}.metric-card,.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card{background:#fff;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 8px 20px rgba(15,23,42,.055)}.metric-card{height:150px;padding:1rem;margin-bottom:.75rem}.metric-label{color:#6b7280;font-size:.78rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.5rem}.metric-value{color:#111827;font-size:1.22rem;line-height:1.18;font-weight:900;overflow-wrap:break-word}.metric-note{color:#64748b;font-size:.85rem;margin-top:.55rem}.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card{padding:1.15rem;margin-bottom:.8rem}.output-card{border-left:5px solid #111827}.guidance-card,.workflow-card{border-left:5px solid #1d4ed8}.sequence-card{border-left:5px solid #059669}.nba-card{border-left:5px solid #111827;background:#f8fafc}.output-card h3,.guidance-card h3,.sequence-card h3,.workflow-card h3,.nba-card h3{font-size:1.05rem;font-weight:850;color:#111827;margin-bottom:.4rem}.output-card p,.guidance-card p,.sequence-card p,.workflow-card p,.nba-card p,.output-card li,.guidance-card li,.sequence-card li,.workflow-card li,.nba-card li{color:#4b5563;line-height:1.52;font-size:.93rem}.status-high{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}.status-medium{background:#fef3c7;color:#92400e;border:1px solid #fde68a}.status-low{background:#d1fae5;color:#065f46;border:1px solid #a7f3d0}.status-neutral{background:#e5e7eb;color:#374151;border:1px solid #d1d5db}.status-pill{display:inline-block;padding:.25rem .6rem;border-radius:999px;font-weight:850;font-size:.78rem;margin-bottom:.5rem}.note-box{padding:.9rem 1rem;border-radius:14px;background:#f8fafc;color:#334155;border:1px solid #e2e8f0;font-weight:650;margin:.9rem 0;font-size:.92rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PRIVACY_NOTE = "Privacy note: Use fictional/sample data for public demos. Do not enter sensitive, confidential, or regulated customer information. If AI is enabled, entered text may be processed by the configured AI provider for output enhancement."


def section_title(title: str, lede: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<div class="section-lede">{escape(lede)}</div>', unsafe_allow_html=True)


def form_group(title: str) -> None:
    st.markdown(f'<div class="form-group-title">{escape(title)}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, note: str | None = None) -> None:
    note_html = f'<div class="metric-note">{escape(note)}</div>' if note else ""
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{escape(label)}</div>'
        f'<div class="metric-value">{escape(str(value))}</div>{note_html}</div>',
        unsafe_allow_html=True,
    )


def html_card(title: str, body: str, css_class: str = "output-card", body_is_html: bool = False) -> None:
    safe_body = body if body_is_html else f"<p>{escape(body)}</p>"
    st.markdown(
        f'<div class="{escape(css_class)}"><h3>{escape(title)}</h3>{safe_body}</div>',
        unsafe_allow_html=True,
    )


def priority_class(priority: str) -> str:
    if priority == "High Priority":
        return "status-high"
    if priority == "Medium Priority":
        return "status-medium"
    if priority == "Low Priority":
        return "status-low"
    return "status-neutral"


def render_sidebar() -> None:
    with st.sidebar:
        st.title("FollowUpPilot AI")
        st.caption("Version 3.0 foundation")
        st.markdown("Sales follow-up workflow automation for field-sales and home-service teams.")
        st.divider()
        st.markdown("### Outputs")
        st.markdown(
            "- Lead temperature\n- Deal risk\n- Follow-up date\n- Overdue status\n- Copy center\n- Timeline\n- CRM note / call script\n- PDF follow-up plan"
        )


def render_hero() -> None:
    st.markdown(
        '<div class="hero"><div class="eyebrow">Sales Follow-Up Workflow Tool</div><div class="hero-title">FollowUpPilot AI</div><div class="hero-subtitle">Turn customer context into next-best actions, follow-up messages, CRM notes, call scripts, objection guidance, manager coaching notes, and multi-touch sequences.</div><div class="hero-pills"><span>Sales Execution</span><span>CRM Discipline</span><span>Follow-Up</span><span>Next Best Action</span><span>Streamlit</span></div></div>',
        unsafe_allow_html=True,
    )


def scenario_date(scenario: dict) -> date:
    if scenario.get("last_contact_date"):
        parsed = LeadInput.from_mapping(scenario).last_contact_date
        if parsed:
            return parsed
    return date.today() - timedelta(days=int(scenario.get("days_since", 1)))


def build_inputs(scenario: dict) -> dict | None:
    with st.form("followup_form"):
        form_group("Customer and project details")
        a, b = st.columns(2)
        with a:
            customer = st.text_input(
                "Customer Name",
                value=scenario.get("customer_name", scenario.get("customer", "")),
                placeholder="Example: Avery Johnson",
            )
        with b:
            company = st.text_input(
                "Business / Team Name",
                value=scenario.get("company_name", scenario.get("company", "")),
                placeholder="Example: Summit Home Services",
            )
        c, d = st.columns(2)
        with c:
            project_type = st.selectbox(
                "Service Type",
                PROJECT_TYPES,
                index=PROJECT_TYPES.index(
                    scenario.get("service_type", scenario.get("project_type", "Roof Replacement"))
                ),
            )
        with d:
            default_stage = scenario.get("lead_stage", scenario.get("lead_status", "Estimate Sent"))
            lead_status = st.selectbox(
                "Lead Stage",
                LEAD_STATUSES,
                index=LEAD_STATUSES.index(default_stage)
                if default_stage in LEAD_STATUSES
                else LEAD_STATUSES.index("Estimate Sent"),
            )

        e, f, g = st.columns(3)
        with e:
            customer_email = st.text_input(
                "Customer Email (optional)", value=scenario.get("customer_email", "")
            )
        with f:
            customer_phone = st.text_input(
                "Customer Phone (optional)", value=scenario.get("customer_phone", "")
            )
        with g:
            assigned_rep = st.text_input("Assigned Rep (optional)", value=scenario.get("assigned_rep", ""))

        form_group("Last interaction")
        context = st.text_area(
            "Last Interaction / Context",
            value=scenario.get("context_notes", scenario.get("context", "")),
            height=120,
            max_chars=4000,
        )

        form_group("Follow-up strategy")
        h, i, j, k = st.columns(4)
        with h:
            objection = st.selectbox(
                "Main Concern",
                OBJECTIONS,
                index=OBJECTIONS.index(scenario.get("objection", "Price")),
            )
        with i:
            financing = st.selectbox(
                "Financing?",
                FINANCING_OPTIONS,
                index=FINANCING_OPTIONS.index(scenario.get("financing", "No")),
            )
        with j:
            urgency = st.selectbox(
                "Urgency",
                URGENCY_LEVELS,
                index=URGENCY_LEVELS.index(scenario.get("urgency", "Medium")),
            )
        with k:
            tone = st.selectbox("Tone", TONES, index=TONES.index(scenario.get("tone", "Professional")))

        left, middle_left, middle_right, right = st.columns(4)
        with left:
            last_contact_date = st.date_input(
                "Last Contact Date",
                value=scenario_date(scenario),
                max_value=date.today(),
            )
        with middle_left:
            estimate_amount = st.number_input(
                "Estimate Amount (optional)",
                min_value=0.0,
                value=float(scenario.get("estimate_amount", 0.0) or 0.0),
                step=100.0,
            )
        with middle_right:
            intensity = st.selectbox(
                "Follow-Up Intensity",
                FOLLOWUP_INTENSITIES,
                index=FOLLOWUP_INTENSITIES.index(scenario.get("followup_intensity", scenario.get("intensity", "Standard"))),
            )
        with right:
            channel = st.selectbox(
                "Preferred Channel",
                CHANNEL_OPTIONS,
                index=CHANNEL_OPTIONS.index(scenario.get("preferred_channel", scenario.get("channel", "All"))),
            )
        submitted = st.form_submit_button("Generate Follow-Up Plan", use_container_width=True)

    if not submitted:
        return None

    days_since = max(0, (date.today() - last_contact_date).days)
    return {
        "customer_name": customer,
        "company_name": company,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "service_type": project_type,
        "lead_stage": lead_status,
        "context_notes": context,
        "objection": objection,
        "financing": financing,
        "urgency": urgency,
        "tone": tone,
        "last_contact_date": last_contact_date.isoformat(),
        "days_since_last_contact": days_since,
        "assigned_rep": assigned_rep,
        "estimate_amount": estimate_amount if estimate_amount else None,
        "followup_intensity": intensity,
        "preferred_channel": channel,
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
        metric_card("Follow-Up Status", outputs["followup_status"], outputs["timing"])

    c5, c6 = st.columns(2)
    with c5:
        metric_card("Suggested Follow-Up Date", outputs.get("suggested_followup_date") or "N/A")
    with c6:
        overdue_note = (
            f"{outputs['days_overdue']} day(s) overdue"
            if outputs.get("is_overdue")
            else "Not overdue"
        )
        metric_card("Overdue", "Yes" if outputs.get("is_overdue") else "No", overdue_note)

    status_html = (
        f'<span class="status-pill {priority_class(outputs["priority"])}">'
        f'{escape(outputs["priority"])}</span><p>{escape(outputs["next_action"])}</p>'
    )
    html_card("Next Best Action", status_html, "nba-card", body_is_html=True)
    html_card("Why This Recommendation", outputs["why"], "guidance-card")

    section_title("Copy center", "Use this section when the rep needs the fastest copy-ready outputs.")
    copy_tabs = st.tabs(
        ["Send this text", "Send this email", "Leave this voicemail", "Add this CRM note", "Manager coaching note"]
    )
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
            html_card(label, message, "sequence-card")

    section_title("Call workflow and objection guidance")
    t1, t2 = st.columns(2)
    with t1:
        st.text_area("Call script", outputs["call"], height=300)
    with t2:
        html_card("Objection Guidance", outputs["guidance"], "guidance-card")


def render_download(inputs: dict, outputs: dict) -> None:
    section_title("Download follow-up plan")
    try:
        report = build_report(inputs, outputs)
        pdf_report = markdown_to_pdf(report, title="FollowUpPilot AI Follow-Up Plan")
    except ValueError as exc:
        st.warning(f"The report could not be generated yet: {exc}")
        return
    except Exception:
        st.warning("The PDF could not be generated. The on-screen follow-up plan is still available.")
        return
    st.download_button(
        "Download Follow-Up Plan PDF",
        data=pdf_report,
        file_name="followuppilot-follow-up-plan.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def main() -> None:
    render_sidebar()
    render_hero()

    section_title(
        "Customer follow-up builder",
        "Load a sample scenario or enter your own customer context. The app will generate a complete follow-up workflow.",
    )
    st.markdown(f'<div class="note-box">{escape(PRIVACY_NOTE)}</div>', unsafe_allow_html=True)

    scenario_name = st.selectbox("Load Sample Scenario", list(SAMPLE_SCENARIOS.keys()))
    scenario = SAMPLE_SCENARIOS.get(scenario_name, {})
    inputs = build_inputs(scenario)

    if inputs is None:
        st.markdown(
            '<div class="note-box">Complete the form or load a sample scenario, then click Generate Follow-Up Plan.</div>',
            unsafe_allow_html=True,
        )
        return

    validation_messages = validate_lead_input(inputs)
    if validation_messages:
        st.warning("Please adjust the follow-up details before generating the plan.")
        for message in validation_messages:
            st.write(f"- {message}")
        return

    outputs = enhance_outputs(inputs, run_followup_workflow(inputs))
    render_results(outputs)
    render_download(inputs, outputs)

    section_title("What this app demonstrates")
    portfolio_items = (
        "<ul><li>Modular Streamlit architecture</li>"
        "<li>AI-enhanced communication with rules-based fallback</li>"
        "<li>Workflow mapping</li>"
        "<li>Rules-based next-best-action logic</li>"
        "<li>Sales communication generation</li>"
        "<li>User-friendly PDF reporting</li></ul>"
    )
    html_card("Portfolio Skills Shown", portfolio_items, "workflow-card", body_is_html=True)

    with st.expander("How to use FollowUpPilot AI"):
        st.markdown(
            "1. Load a sample scenario or enter your own customer/project context.\n"
            "2. Generate the follow-up plan.\n"
            "3. Use the Copy Center for text, email, voicemail, CRM note, and coaching note.\n"
            "4. Review the follow-up date, overdue status, and timeline.\n"
            "5. Download the PDF follow-up plan for CRM documentation or team coaching."
        )
    st.markdown(f'<div class="note-box">{escape(PRIVACY_NOTE)}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
