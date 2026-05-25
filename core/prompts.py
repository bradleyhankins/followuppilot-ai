def ai_copy_prompt(inputs: dict, outputs: dict) -> str:
    return f"""
You are a sales follow-up assistant for a small business.
Improve the copy center outputs using the provided customer context and rules-based draft.
Keep the content concise, practical, professional, and specific.
Do not add new facts, offer terms, time limits, approvals, or promises that were not provided.
Preserve the same business intent and next step.

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


def parse_ai_copy(raw: str, fallback: dict) -> dict:
    if not raw:
        return fallback

    sections = {
        "TEXT": "sms",
        "EMAIL SUBJECT": "subject",
        "EMAIL BODY": "email",
        "VOICEMAIL": "voicemail",
        "CRM NOTE": "crm",
        "MANAGER COACHING NOTE": "coaching",
    }
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
