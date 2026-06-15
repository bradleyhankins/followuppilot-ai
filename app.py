from __future__ import annotations

from collections.abc import MutableMapping
from datetime import date, timedelta
from html import escape

import pandas as pd
import streamlit as st

from ai_helpers import enhance_text, stable_cache_key
from core.dashboard import (
    count_by,
    dashboard_metrics,
    manager_attention_flags,
    overdue_by_rep,
    value_by_stage,
)
from core.followup_logic import run_followup_workflow
from core.lead_store import (
    OUTCOMES,
    SessionLeadStore,
    complete_followup,
    csv_template,
    export_leads_csv,
    filter_leads,
    import_leads_csv,
    latest_followup_activity,
    refresh_lead_plan,
)
from core.models import LeadInput, LeadRecord
from core.prompts import ai_copy_prompt, parse_ai_copy
from core.report_builder import build_report
from core.validation import validate_lead_input
from data.demo_leads import demo_leads
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
.block-container{max-width:1220px;padding-top:1.1rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#111827}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label,[data-testid="stSidebar"] li{color:#f9fafb!important}
.app-hero{padding:1.55rem 1.7rem;border-radius:14px;background:linear-gradient(135deg,#111827 0%,#1f2937 52%,#334155 100%);color:#fff;margin-bottom:1rem;border:1px solid rgba(255,255,255,.08)}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;font-weight:800;color:#93c5fd;margin-bottom:.45rem}
.hero-title{font-size:2rem;line-height:1.08;font-weight:850;margin-bottom:.45rem}
.hero-subtitle{font-size:1rem;line-height:1.55;color:#e5e7eb;max-width:940px}
.section-title{margin-top:1.15rem;margin-bottom:.45rem;font-size:1.32rem;font-weight:850;color:#111827}
.section-lede{color:#4b5563;line-height:1.55;margin-bottom:.8rem;max-width:960px}
.form-group-title{font-size:.86rem;font-weight:850;text-transform:uppercase;letter-spacing:.06em;color:#64748b;margin:.35rem 0 .15rem 0}
.metric-card,.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card,.attention-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;box-shadow:0 6px 16px rgba(15,23,42,.045)}
.metric-card{padding:.9rem;margin-bottom:.65rem;min-height:118px}
.metric-label{color:#6b7280;font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.45rem}
.metric-value{color:#111827;font-size:1.28rem;line-height:1.18;font-weight:900;overflow-wrap:break-word}
.metric-note{color:#64748b;font-size:.82rem;margin-top:.45rem}
.output-card,.guidance-card,.sequence-card,.workflow-card,.nba-card,.attention-card{padding:1rem;margin-bottom:.72rem}
.output-card{border-left:5px solid #111827}.guidance-card,.workflow-card{border-left:5px solid #1d4ed8}.sequence-card{border-left:5px solid #059669}.nba-card{border-left:5px solid #111827;background:#f8fafc}.attention-card{border-left:5px solid #dc2626;background:#fffafa}
.output-card h3,.guidance-card h3,.sequence-card h3,.workflow-card h3,.nba-card h3,.attention-card h3{font-size:1rem;font-weight:850;color:#111827;margin-bottom:.35rem}
.output-card p,.guidance-card p,.sequence-card p,.workflow-card p,.nba-card p,.attention-card p,.output-card li,.guidance-card li,.sequence-card li,.workflow-card li,.nba-card li{color:#4b5563;line-height:1.5;font-size:.92rem}
.status-high{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}.status-medium{background:#fef3c7;color:#92400e;border:1px solid #fde68a}.status-low{background:#d1fae5;color:#065f46;border:1px solid #a7f3d0}.status-neutral{background:#e5e7eb;color:#374151;border:1px solid #d1d5db}
.status-pill{display:inline-block;padding:.25rem .6rem;border-radius:999px;font-weight:850;font-size:.78rem;margin-bottom:.5rem}
.note-box{padding:.85rem 1rem;border-radius:12px;background:#f8fafc;color:#334155;border:1px solid #e2e8f0;font-weight:650;margin:.85rem 0;font-size:.9rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PRIVACY_NOTE = (
    "Demo note: FollowUpPilot uses fictional sample data. Do not enter sensitive, confidential, "
    "regulated, or real customer information into the public demo."
)


def store() -> SessionLeadStore:
    lead_store = SessionLeadStore(st.session_state)
    lead_store.seed(demo_leads())
    return lead_store


def section_title(title: str, lede: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)
    if lede:
        st.markdown(f'<div class="section-lede">{escape(lede)}</div>', unsafe_allow_html=True)


def form_group(title: str) -> None:
    st.markdown(f'<div class="form-group-title">{escape(title)}</div>', unsafe_allow_html=True)


def metric_card(label: str, value: str | int | float, note: str | None = None) -> None:
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


NAVIGATION_OPTIONS = ["Manager Dashboard", "Lead Workspace", "Follow-Up Builder", "About This Demo"]
DEFAULT_VIEW = "Manager Dashboard"
NAVIGATION_KEY = "navigation_view"


def normalize_view(view_name: object) -> str:
    view = str(view_name or "").strip()
    return view if view in NAVIGATION_OPTIONS else DEFAULT_VIEW


def set_view_state(
    state: MutableMapping[str, object],
    view_name: str,
    *,
    sync_navigation_widget: bool = True,
) -> str:
    view = normalize_view(view_name)
    state["view"] = view
    if sync_navigation_widget:
        state[NAVIGATION_KEY] = view
    return view


def set_view(view_name: str, *, sync_navigation_widget: bool = True) -> str:
    return set_view_state(
        st.session_state,
        view_name,
        sync_navigation_widget=sync_navigation_widget,
    )


def sync_view_from_navigation() -> None:
    st.session_state["view"] = normalize_view(st.session_state.get(NAVIGATION_KEY))


def route_for_view(view_name: object) -> str:
    return normalize_view(view_name)


def render_sidebar() -> str:
    desired_view = normalize_view(st.session_state.get("view", DEFAULT_VIEW))
    if st.session_state.get(NAVIGATION_KEY) != desired_view:
        st.session_state[NAVIGATION_KEY] = desired_view
    st.session_state["view"] = desired_view
    with st.sidebar:
        st.title("FollowUpPilot AI")
        st.caption("Version 4.0 workspace")
        st.markdown("Fictional-data follow-up operating system demo.")
        st.divider()
        view = st.radio(
            "Navigation",
            NAVIGATION_OPTIONS,
            key=NAVIGATION_KEY,
            on_change=sync_view_from_navigation,
        )
        st.session_state["view"] = normalize_view(view)
        st.divider()
        st.markdown(PRIVACY_NOTE)
    return st.session_state["view"]


def render_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="app-hero"><div class="eyebrow">Follow-Up Operating System Demo</div>'
        f'<div class="hero-title">{escape(title)}</div><div class="hero-subtitle">{escape(subtitle)}</div></div>',
        unsafe_allow_html=True,
    )


WORKSPACE_SELECTOR_KEY = "workspace_lead_selector"


def lead_selector_label(lead: LeadRecord) -> str:
    return f"{lead.lead_id} - {lead.customer_name} ({lead.service_type})"


def lead_id_from_selector_label(label: str) -> str:
    return label.split(" - ", 1)[0].strip()


def open_lead_in_workspace(
    state: MutableMapping[str, object],
    selected_label: str,
    *,
    sync_navigation_widget: bool = True,
) -> str:
    lead_id = lead_id_from_selector_label(selected_label)
    state["selected_lead_id"] = lead_id
    set_view_state(
        state,
        "Lead Workspace",
        sync_navigation_widget=sync_navigation_widget,
    )
    return lead_id


def output_widget_keys(prefix: str) -> dict[str, str]:
    safe_prefix = prefix.strip() or "followup"
    return {
        "sms": f"{safe_prefix}_sms",
        "subject": f"{safe_prefix}_email_subject",
        "email": f"{safe_prefix}_email_body",
        "voicemail": f"{safe_prefix}_voicemail",
        "crm": f"{safe_prefix}_crm",
        "coaching": f"{safe_prefix}_coaching",
        "call": f"{safe_prefix}_call",
    }


def ai_cache_context(inputs: dict, context_key: str) -> dict:
    return {
        "context_key": context_key,
        "customer_name": inputs.get("customer_name", ""),
        "company_name": inputs.get("company_name", ""),
        "service_type": inputs.get("service_type", ""),
        "lead_stage": inputs.get("lead_stage", ""),
        "context_notes": inputs.get("context_notes", ""),
        "objection": inputs.get("objection", ""),
        "urgency": inputs.get("urgency", ""),
        "financing": inputs.get("financing", ""),
        "tone": inputs.get("tone", ""),
        "preferred_channel": inputs.get("preferred_channel", ""),
        "followup_intensity": inputs.get("followup_intensity", ""),
        "last_contact_date": inputs.get("last_contact_date", ""),
        "estimate_amount": inputs.get("estimate_amount", ""),
    }


def resolve_selected_lead(leads: list[LeadRecord], selected_id: str | None) -> LeadRecord:
    return next((lead for lead in leads if lead.lead_id == selected_id), leads[0])


def sync_selected_lead_id_from_selector() -> None:
    st.session_state["selected_lead_id"] = lead_id_from_selector_label(
        st.session_state.get(WORKSPACE_SELECTOR_KEY, "")
    )


def prepare_workspace_selector(leads: list[LeadRecord]) -> list[str]:
    labels = [lead_selector_label(lead) for lead in leads]
    selected = resolve_selected_lead(leads, st.session_state.get("selected_lead_id"))
    selected_label = lead_selector_label(selected)
    current_label = st.session_state.get(WORKSPACE_SELECTOR_KEY)
    if current_label not in labels or lead_id_from_selector_label(current_label) != selected.lead_id:
        st.session_state[WORKSPACE_SELECTOR_KEY] = selected_label
    st.session_state["selected_lead_id"] = selected.lead_id
    return labels


def build_workspace_plan(lead: LeadRecord) -> tuple[dict, dict]:
    inputs = lead.to_workflow_dict()
    return inputs, run_followup_workflow(inputs)


def enhance_outputs(inputs: dict, outputs: dict, context_key: str = "builder") -> dict:
    raw = enhance_text(
        ai_copy_prompt(inputs, outputs),
        "",
        stable_cache_key("followup_copy", ai_cache_context(inputs, context_key)),
    )
    if not raw:
        return outputs
    outputs.update(parse_ai_copy(raw, outputs))
    return outputs


def render_results(outputs: dict, key_prefix: str = "followup") -> None:
    keys = output_widget_keys(key_prefix)
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

    section_title("Copy center", "Copy-ready outputs for customer communication and CRM documentation.")
    tabs = st.tabs(["Text", "Email", "Voicemail", "CRM Note", "Manager Coaching Note"])
    with tabs[0]:
        st.text_area("Text", outputs["sms"], height=145, key=keys["sms"])
    with tabs[1]:
        st.text_input("Email Subject", outputs["subject"], key=keys["subject"])
        st.text_area("Email Body", outputs["email"], height=250, key=keys["email"])
    with tabs[2]:
        st.text_area("Voicemail", outputs["voicemail"], height=145, key=keys["voicemail"])
    with tabs[3]:
        st.text_area("CRM Note", outputs["crm"], height=250, key=keys["crm"])
    with tabs[4]:
        st.text_area("Manager Coaching Note", outputs["coaching"], height=145, key=keys["coaching"])

    section_title("Follow-up timeline")
    cols = st.columns(2)
    for pos, (label, message) in enumerate(outputs["sequence"].items()):
        with cols[pos % 2]:
            html_card(label, message, "sequence-card")

    section_title("Call workflow and objection guidance")
    left, right = st.columns(2)
    with left:
        st.text_area("Call script", outputs["call"], height=285, key=keys["call"])
    with right:
        html_card("Objection Guidance", outputs["guidance"], "guidance-card")


def render_download(inputs: dict, outputs: dict, key: str = "download_pdf") -> None:
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
        key=key,
    )


def render_manager_dashboard(lead_store: SessionLeadStore) -> None:
    render_hero(
        "Manager Dashboard",
        "See open follow-up risk, overdue activity, rep workload, and the leads that need manager attention.",
    )
    leads = lead_store.list()
    metrics = dashboard_metrics(leads)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        metric_card("Active Leads", metrics["active_leads"])
    with c2:
        metric_card("Overdue", metrics["overdue_followups"])
    with c3:
        metric_card("Due Today", metrics["due_today"])
    with c4:
        metric_card("High Priority", metrics["high_priority"])
    with c5:
        metric_card("Active Pipeline", money(metrics["active_pipeline_value"]))
    with c6:
        metric_card("Won Value", money(metrics["won_value"]))

    section_title("Manager attention", "Deterministic flags that explain where a manager should look first.")
    flags = manager_attention_flags(leads)
    if not flags:
        st.success("No manager attention flags for the current lead list.")
    else:
        for item in flags[:8]:
            html_card(item.title, item.reason, "attention-card")

    section_title("Pipeline views", "Each chart is intended to help spot follow-up bottlenecks.")
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.caption("Leads by stage")
        render_bar_chart(count_by(leads, "lead_stage"), "Stage", "Leads")
        st.caption("Leads by assigned rep")
        render_bar_chart(count_by(leads, "assigned_rep"), "Rep", "Leads")
    with chart_cols[1]:
        st.caption("Pipeline value by stage")
        render_bar_chart(value_by_stage(leads), "Stage", "Value")
        st.caption("Overdue leads by rep")
        render_bar_chart(overdue_by_rep(leads), "Rep", "Overdue")
    st.caption("Priority distribution")
    render_bar_chart(count_by(leads, "priority"), "Priority", "Leads")

    render_lead_table(lead_store)
    render_csv_tools(lead_store)


def render_lead_table(lead_store: SessionLeadStore) -> None:
    leads = lead_store.list()
    section_title("Lead table", "Filter, sort, and open a lead in the workspace.")
    reps = ["All"] + sorted({lead.assigned_rep for lead in leads if lead.assigned_rep})
    stages = ["All"] + sorted({lead.lead_stage for lead in leads})
    priorities = ["All"] + sorted({lead.priority for lead in leads})
    statuses = ["All"] + sorted({lead.followup_status for lead in leads})
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        search = st.text_input("Search leads", placeholder="Customer, service, rep...")
    with f2:
        rep = st.selectbox("Assigned rep", reps)
    with f3:
        stage = st.selectbox("Stage", stages)
    with f4:
        priority = st.selectbox("Priority", priorities)
    f5, f6, f7 = st.columns(3)
    with f5:
        status = st.selectbox("Follow-up status", statuses)
    with f6:
        sort_by = st.selectbox("Sort by", ["follow-up date", "priority", "estimate amount", "last contact"])
    with f7:
        overdue_only = st.checkbox("Overdue only")

    filtered = filter_leads(leads, search, rep, stage, priority, status, overdue_only, sort_by)
    rows = [
        {
            "lead_id": lead.lead_id,
            "customer": lead.customer_name,
            "service": lead.service_type,
            "rep": lead.assigned_rep,
            "stage": lead.lead_stage,
            "estimate": money(lead.estimate_amount or 0),
            "priority": lead.priority,
            "risk": lead.deal_risk,
            "follow-up date": lead.suggested_followup_date.isoformat()
            if lead.suggested_followup_date
            else "N/A",
            "follow-up status": lead.followup_status,
        }
        for lead in filtered
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    if not filtered:
        st.info("No leads match the current filters.")
        return
    selected_label = st.selectbox(
        "Open lead in workspace",
        [f"{lead.lead_id} - {lead.customer_name} ({lead.service_type})" for lead in filtered],
    )
    if st.button("Open selected lead", use_container_width=True):
        open_lead_in_workspace(
            st.session_state,
            selected_label,
            sync_navigation_widget=False,
        )
        st.rerun()


def render_csv_tools(lead_store: SessionLeadStore) -> None:
    with st.expander("CSV import and export"):
        st.download_button(
            "Download CSV Template",
            data=csv_template(),
            file_name="followuppilot-lead-template.csv",
            mime="text/csv",
            use_container_width=True,
        )
        uploaded = st.file_uploader("Upload fictional lead CSV", type=["csv"])
        if uploaded is not None:
            text = uploaded.getvalue().decode("utf-8-sig")
            accepted, rejected = import_leads_csv(text, {lead.lead_id for lead in lead_store.list()})
            if accepted:
                lead_store.replace_all([*lead_store.list(), *accepted])
                st.success(f"Imported {len(accepted)} lead(s).")
            if rejected:
                rejected_rows = len({item["source_row"] for item in rejected})
                st.warning(f"Rejected {rejected_rows} row(s).")
                st.caption("Rejected row details")
                st.table(rejected)
        st.download_button(
            "Export Current Lead List",
            data=export_leads_csv(lead_store.list()),
            file_name="followuppilot-leads.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_lead_workspace(lead_store: SessionLeadStore) -> None:
    render_hero(
        "Lead Workspace",
        "Review one managed lead, update its state, generate follow-up copy, and record the outcome.",
    )
    leads = lead_store.list()
    if not leads:
        st.info("No leads are loaded. Import a CSV or reset the demo data from the dashboard.")
        return
    labels = prepare_workspace_selector(leads)
    st.selectbox(
        "Choose lead",
        labels,
        key=WORKSPACE_SELECTOR_KEY,
        on_change=sync_selected_lead_id_from_selector,
    )
    selected_id = st.session_state.get("selected_lead_id")
    lead = lead_store.get(selected_id) if selected_id else None
    if lead is None:
        st.warning("Selected lead could not be found.")
        return

    edited = render_lead_edit_form(lead)
    if edited:
        messages = workspace_validation_messages(edited)
        if messages:
            st.warning("Please adjust the lead before saving.")
            for message in messages:
                st.write(f"- {message}")
        else:
            refreshed = refresh_lead_plan(edited)
            lead_store.upsert(refreshed)
            st.session_state["selected_lead_id"] = refreshed.lead_id
            st.success("Lead saved and follow-up plan refreshed.")
            lead = refreshed

    lead = lead_store.get(lead.lead_id) or lead
    inputs, plan = build_workspace_plan(lead)
    render_latest_activity(lead)
    render_results(plan, key_prefix=f"workspace_{lead.lead_id}")
    render_download(inputs, plan, key=f"download_{lead.lead_id}")
    render_completion_controls(lead_store, lead)


def render_lead_edit_form(lead: LeadRecord) -> LeadRecord | None:
    with st.form(f"edit_{lead.lead_id}"):
        form_group("Lead details")
        a, b, c = st.columns(3)
        with a:
            customer = st.text_input("Customer Name", value=lead.customer_name)
        with b:
            company = st.text_input("Business / Team Name", value=lead.company_name)
        with c:
            rep = st.text_input("Assigned Rep", value=lead.assigned_rep)
        d, e, f = st.columns(3)
        with d:
            email = st.text_input("Customer Email (optional)", value=lead.customer_email)
        with e:
            phone = st.text_input("Customer Phone (optional)", value=lead.customer_phone)
        with f:
            estimate = st.number_input(
                "Estimate Amount",
                min_value=0.0,
                value=float(lead.estimate_amount or 0),
                step=100.0,
            )
        g, h, i = st.columns(3)
        with g:
            service = st.selectbox("Service Type", PROJECT_TYPES, index=safe_index(PROJECT_TYPES, lead.service_type))
        with h:
            stage = st.selectbox("Lead Stage", LEAD_STATUSES, index=safe_index(LEAD_STATUSES, lead.lead_stage))
        with i:
            last_contact = st.date_input(
                "Last Contact Date",
                value=lead.last_contact_date or date.today(),
                max_value=date.today(),
            )
        context = st.text_area("Last Interaction / Context", value=lead.context_notes, height=110)
        left, middle_left, middle_right, right = st.columns(4)
        with left:
            objection = st.selectbox("Main Concern", OBJECTIONS, index=safe_index(OBJECTIONS, lead.objection))
        with middle_left:
            urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=safe_index(URGENCY_LEVELS, lead.urgency))
        with middle_right:
            financing = st.selectbox("Financing?", FINANCING_OPTIONS, index=safe_index(FINANCING_OPTIONS, lead.financing))
        with right:
            tone = st.selectbox("Tone", TONES, index=safe_index(TONES, lead.tone))
        n, o = st.columns(2)
        with n:
            channel = st.selectbox("Preferred Channel", CHANNEL_OPTIONS, index=safe_index(CHANNEL_OPTIONS, lead.preferred_channel))
        with o:
            intensity = st.selectbox("Follow-Up Intensity", FOLLOWUP_INTENSITIES, index=safe_index(FOLLOWUP_INTENSITIES, lead.followup_intensity))
        submitted = st.form_submit_button("Save and refresh lead", use_container_width=True)
    if not submitted:
        return None
    return LeadRecord.from_mapping(
        {
            **lead.to_dict(),
            "customer_name": customer,
            "company_name": company,
            "customer_email": email,
            "customer_phone": phone,
            "service_type": service,
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
            "last_contact_date": last_contact.isoformat(),
            "updated_date": date.today().isoformat(),
        }
    )


def render_completion_controls(lead_store: SessionLeadStore, lead: LeadRecord) -> None:
    section_title("Record follow-up outcome")
    with st.form(f"complete_{lead.lead_id}"):
        a, b = st.columns(2)
        with a:
            outcome = st.selectbox("Outcome", OUTCOMES)
        with b:
            stage = st.selectbox("Update stage", LEAD_STATUSES, index=safe_index(LEAD_STATUSES, lead.lead_stage))
        note = st.text_area("Last action note", value=f"Follow-up completed for {lead.customer_name}.")
        submitted = st.form_submit_button("Mark follow-up complete", use_container_width=True)
    if submitted:
        adjusted = LeadRecord.from_mapping({**lead.to_dict(), "lead_stage": stage})
        updated = complete_followup(adjusted, outcome, note)
        lead_store.upsert(updated)
        st.session_state["selected_lead_id"] = updated.lead_id
        st.success("Follow-up marked complete and next recommendation recalculated.")
        st.rerun()


def render_latest_activity(lead: LeadRecord) -> None:
    if not any([lead.outcome, lead.last_action, lead.outcome_note]):
        return

    section_title("Latest Follow-Up Activity")
    activity = latest_followup_activity(lead)
    for field, value in activity.items():
        st.write(f"**{field}:** {value}")


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
            customer = st.text_input("Customer Name", value=scenario.get("customer_name", scenario.get("customer", "")))
        with b:
            company = st.text_input("Business / Team Name", value=scenario.get("company_name", scenario.get("company", "")))
        c, d = st.columns(2)
        with c:
            project_type = st.selectbox(
                "Service Type",
                PROJECT_TYPES,
                index=safe_index(PROJECT_TYPES, scenario.get("service_type", scenario.get("project_type", "Roof Replacement"))),
            )
        with d:
            lead_status = st.selectbox("Lead Stage", LEAD_STATUSES, index=safe_index(LEAD_STATUSES, scenario.get("lead_stage", scenario.get("lead_status", "Estimate Sent"))))
        context = st.text_area("Last Interaction / Context", value=scenario.get("context_notes", scenario.get("context", "")), height=120, max_chars=4000)
        e, f, g, h = st.columns(4)
        with e:
            objection = st.selectbox("Main Concern", OBJECTIONS, index=safe_index(OBJECTIONS, scenario.get("objection", "Price")))
        with f:
            financing = st.selectbox("Financing?", FINANCING_OPTIONS, index=safe_index(FINANCING_OPTIONS, scenario.get("financing", "No")))
        with g:
            urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=safe_index(URGENCY_LEVELS, scenario.get("urgency", "Medium")))
        with h:
            tone = st.selectbox("Tone", TONES, index=safe_index(TONES, scenario.get("tone", "Professional")))
        i, j, k = st.columns(3)
        with i:
            last_contact_date = st.date_input("Last Contact Date", value=scenario_date(scenario), max_value=date.today())
        with j:
            intensity = st.selectbox("Follow-Up Intensity", FOLLOWUP_INTENSITIES, index=safe_index(FOLLOWUP_INTENSITIES, scenario.get("followup_intensity", scenario.get("intensity", "Standard"))))
        with k:
            channel = st.selectbox("Preferred Channel", CHANNEL_OPTIONS, index=safe_index(CHANNEL_OPTIONS, scenario.get("preferred_channel", scenario.get("channel", "All"))))
        submitted = st.form_submit_button("Generate Follow-Up Plan", use_container_width=True)
    if not submitted:
        return None
    return {
        "customer_name": customer,
        "company_name": company,
        "service_type": project_type,
        "lead_stage": lead_status,
        "context_notes": context,
        "objection": objection,
        "financing": financing,
        "urgency": urgency,
        "tone": tone,
        "last_contact_date": last_contact_date.isoformat(),
        "days_since_last_contact": max(0, (date.today() - last_contact_date).days),
        "followup_intensity": intensity,
        "preferred_channel": channel,
    }


def render_followup_builder() -> None:
    render_hero(
        "Follow-Up Builder",
        "The original single-lead generator remains available for quick one-off follow-up planning.",
    )
    st.markdown(f'<div class="note-box">{escape(PRIVACY_NOTE)}</div>', unsafe_allow_html=True)
    scenario_name = st.selectbox("Load Sample Scenario", list(SAMPLE_SCENARIOS.keys()))
    inputs = build_inputs(SAMPLE_SCENARIOS.get(scenario_name, {}))
    if inputs is None:
        st.info("Complete the form or load a sample scenario, then click Generate Follow-Up Plan.")
        return
    messages = validate_lead_input(inputs)
    if messages:
        st.warning("Please adjust the follow-up details before generating the plan.")
        for message in messages:
            st.write(f"- {message}")
        return
    outputs = enhance_outputs(inputs, run_followup_workflow(inputs), context_key=f"builder_{scenario_name}")
    render_results(outputs, key_prefix=f"builder_{scenario_name}")
    render_download(inputs, outputs, key="builder_download")


def render_about() -> None:
    render_hero(
        "About This Demo",
        "A fictional-data demonstration of follow-up discipline for local service teams.",
    )
    st.markdown(
        """
### Business problem
Small service businesses often lose revenue because follow-up is inconsistent, CRM notes are thin, and managers cannot easily see which open leads are overdue.

### What the rules engine does
The deterministic workflow calculates priority, risk, next action, follow-up date, overdue state, communication drafts, CRM notes, and manager guidance from visible lead inputs.

### Where optional AI is used
When an OpenAI key is configured, AI can polish copy-center wording. It does not decide priority, risk, dates, or business outcomes. Without a key, deterministic fallback remains active.

### Human review
All outputs are drafts for human review. The app does not send email, send SMS, update a CRM, or schedule reminders.

### Privacy
This public demo is for fictional or approved non-sensitive data only. A production implementation would require authentication, tenant separation, durable storage, audit controls, CRM/email/SMS integration review, data-retention policy, and operational monitoring.
"""
    )


def workspace_validation_messages(lead: LeadRecord) -> list[str]:
    messages = validate_lead_input(lead.to_workflow_dict())
    if lead.lead_stage == "Closed Lost":
        messages = [message for message in messages if "Closed Lost leads default" not in message]
    return messages


def chart_data(values: dict[str, int | float], label: str, value_name: str) -> pd.DataFrame:
    return pd.DataFrame([{label: key, value_name: value} for key, value in values.items()])


def render_bar_chart(values: dict[str, int | float], label: str, value_name: str) -> None:
    data = chart_data(values, label, value_name)
    if data.empty:
        st.info("No data available for this chart.")
        return
    try:
        st.bar_chart(data, x=label, y=value_name)
    except Exception:
        st.table(data)


def money(value: int | float) -> str:
    return f"${value:,.0f}"


def safe_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


def main() -> None:
    lead_store = store()
    view = route_for_view(render_sidebar())
    if view == "Manager Dashboard":
        render_manager_dashboard(lead_store)
    elif view == "Lead Workspace":
        render_lead_workspace(lead_store)
    elif view == "Follow-Up Builder":
        render_followup_builder()
    else:
        render_about()


if __name__ == "__main__":
    main()
