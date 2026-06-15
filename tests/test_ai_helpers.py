from __future__ import annotations

from ai_helpers import prepare_prompt, read_token
from core.prompts import parse_ai_copy


def test_read_token_prefers_openai_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "primary")
    monkeypatch.setenv("OPENAI_TOKEN", "legacy")

    assert read_token() == "primary"


def test_prepare_prompt_trims_long_input():
    prepared = prepare_prompt("x" * 13000)

    assert "[Input was trimmed" in prepared
    assert len(prepared) < 12500


def test_parse_ai_copy_prefers_json_payload():
    fallback = {
        "sms": "old text",
        "subject": "old subject",
        "email": "old email",
        "voicemail": "old voicemail",
        "crm": "old crm",
        "coaching": "old coaching",
    }
    raw = '{"sms":"new text","subject":"new subject","email":"new email","voicemail":"new voicemail","crm":"new crm","coaching":"new coaching"}'

    parsed = parse_ai_copy(raw, fallback)

    assert parsed["sms"] == "new text"
    assert parsed["subject"] == "new subject"


def test_parse_ai_copy_falls_back_to_heading_payload():
    fallback = {
        "sms": "old text",
        "subject": "old subject",
        "email": "old email",
        "voicemail": "old voicemail",
        "crm": "old crm",
        "coaching": "old coaching",
    }
    raw = "TEXT:\nnew text\n\nEMAIL SUBJECT:\nnew subject\n"

    parsed = parse_ai_copy(raw, fallback)

    assert parsed["sms"] == "new text"
    assert parsed["subject"] == "new subject"
    assert parsed["email"] == "old email"
