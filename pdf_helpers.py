from __future__ import annotations

import re
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            spaceAfter=16,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.HexColor("#111827"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontSize=10,
            leading=14,
            spaceAfter=6,
            textColor=colors.HexColor("#374151"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#6b7280"),
        )
    )
    return styles


def _flush_bullets(story, bullets, style) -> None:
    if not bullets:
        return
    story.append(
        ListFlowable(
            [ListItem(Paragraph(_clean(item), style)) for item in bullets],
            bulletType="bullet",
            leftIndent=18,
        )
    )
    story.append(Spacer(1, 4))
    bullets.clear()


def markdown_to_pdf(markdown_text: str, title: str = "Report") -> bytes:
    if not str(markdown_text).strip():
        raise ValueError("Report content is empty.")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )
    styles = _styles()
    story = [Paragraph(_clean(title), styles["ReportTitle"])]
    bullets: list[str] = []

    for raw_line in str(markdown_text).splitlines():
        line = raw_line.strip()
        if not line:
            _flush_bullets(story, bullets, styles["Body"])
            story.append(Spacer(1, 4))
            continue
        if line.startswith("# "):
            _flush_bullets(story, bullets, styles["Body"])
            story.append(Paragraph(_clean(line[2:].strip()), styles["ReportTitle"]))
        elif line.startswith("## "):
            _flush_bullets(story, bullets, styles["Body"])
            story.append(Paragraph(_clean(line[3:].strip()), styles["SectionHeading"]))
        elif line.startswith("### "):
            _flush_bullets(story, bullets, styles["Body"])
            story.append(Paragraph(f"<b>{_clean(line[4:].strip())}</b>", styles["Body"]))
        elif line.startswith("- "):
            bullets.append(line[2:].strip())
        elif re.match(r"^\d+[.)]\s+", line):
            bullets.append(re.sub(r"^\d+[.)]\s+", "", line).strip())
        elif line == "---":
            _flush_bullets(story, bullets, styles["Body"])
            story.append(Spacer(1, 8))
        else:
            _flush_bullets(story, bullets, styles["Body"])
            story.append(Paragraph(_clean(line).replace("**", ""), styles["Body"]))

    _flush_bullets(story, bullets, styles["Body"])
    story.append(Spacer(1, 12))
    story.append(Paragraph("Generated from the live app workflow.", styles["Small"]))
    try:
        doc.build(story)
    except Exception as exc:
        raise ValueError("PDF rendering failed.") from exc
    return buffer.getvalue()


def _clean(value: str) -> str:
    return escape(str(value).replace("\x00", ""), quote=False)
