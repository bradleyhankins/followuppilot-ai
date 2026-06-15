from __future__ import annotations

from datetime import date
from html import escape

from core.report_builder import build_report
from pdf_helpers import markdown_to_pdf


def test_report_generation_handles_missing_optional_values():
    report = build_report(
        {"company_name": "Summit Home Services", "service_type": "Roof Repair"},
        {
            "temperature": "Warm",
            "deal_risk": "Low",
            "main_risk": "No major risk identified",
            "priority": "Low Priority",
            "score": 4,
            "timing": "Follow up within 48-72 hours",
            "suggested_followup_date": date(2026, 6, 15).isoformat(),
            "followup_status": "Upcoming follow-up",
            "next_action": "Send a text.",
            "why": "Demo explanation.",
            "sms": "Text",
            "subject": "Subject",
            "email": "Email",
            "voicemail": "Voicemail",
            "crm": "CRM",
            "call": "Call",
            "guidance": "Guidance",
            "coaching": "Coaching",
            "sequence": {"Touch 1": "Message"},
        },
    )

    assert "Summit Home Services" in report
    assert "Upcoming follow-up" in report


def test_pdf_generation_returns_bytes_for_unusual_characters():
    pdf = markdown_to_pdf("# Report\n\n## Section\nCustomer said <maybe> & had unusual chars.")

    assert pdf.startswith(b"%PDF")


def test_html_escaping_sanitizes_user_content():
    value = '<script>alert("x")</script>'

    assert escape(value) == '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;'
