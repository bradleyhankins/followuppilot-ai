from __future__ import annotations

import json
import re
from typing import Any

AI_COPY_KEYS = {
    "sms": "sms",
    "subject": "subject",
    "email": "email",
    "voicemail": "voicemail",
    "crm": "crm",
    "coaching": "coaching",
}


def ai_copy_prompt(inputs: dict[str, Any], outputs: dict[str, Any]) -> str:
    payload = {
        "inputs": inputs,
        "rules_based_outputs": {
            "sms": outputs["sms"],
            "subject": outputs["subject"],
            "email": outputs["email"],
            "voicemail": outputs["voicemail"],
            "crm": outputs["crm"],
            "coaching": outputs["coaching"],
        },
    }
    return f"""
You are a sales follow-up assistant for a small business.
Improve the copy center outputs using the provided customer context and rules-based draft.
Keep the content concise, practical, professional, and specific.
Do not add new facts, offer terms, time limits, approvals, or promises that were not provided.
Preserve the same business intent and next step.

Return only valid JSON with these string keys:
sms, subject, email, voicemail, crm, coaching

Input payload:
{json.dumps(payload, ensure_ascii=True)}
"""


def parse_ai_copy(raw: str, fallback: dict[str, Any]) -> dict[str, Any]:
    if not raw:
        return fallback.copy()

    parsed = fallback.copy()
    json_payload = _extract_json(raw)
    if json_payload:
        for key in AI_COPY_KEYS:
            value = json_payload.get(key)
            if isinstance(value, str) and value.strip():
                parsed[key] = value.strip()
        return parsed

    parsed.update(_parse_heading_format(raw, fallback))
    return parsed


def _extract_json(raw: str) -> dict[str, Any] | None:
    raw = raw.strip()
    candidates = [raw]
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if match:
        candidates.append(match.group(0))

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _parse_heading_format(raw: str, fallback: dict[str, Any]) -> dict[str, Any]:
    sections = {
        "TEXT": "sms",
        "EMAIL SUBJECT": "subject",
        "EMAIL BODY": "email",
        "VOICEMAIL": "voicemail",
        "CRM NOTE": "crm",
        "MANAGER COACHING NOTE": "coaching",
    }
    parsed = fallback.copy()
    heading_pattern = re.compile(
        r"^(TEXT|EMAIL SUBJECT|EMAIL BODY|VOICEMAIL|CRM NOTE|MANAGER COACHING NOTE):\s*$",
        flags=re.MULTILINE,
    )
    matches = list(heading_pattern.finditer(raw))
    for index, match in enumerate(matches):
        heading = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        value = raw[start:end].strip()
        if value:
            parsed[sections[heading]] = value
    return parsed
