from __future__ import annotations

import hashlib
import os

import streamlit as st

DEFAULT_MODEL = "gpt-4.1-mini"
PRIMARY_TOKEN_NAME = "OPENAI_API_KEY"
LEGACY_TOKEN_NAME = "OPENAI_TOKEN"
MAX_PROMPT_CHARS = 11500

AI_GUARDRAIL_PREFIX = """
You are an embedded AI enhancement layer inside a deterministic business workflow app.
The rules-based app output is the source of truth.
Your job is to improve clarity, structure, tone, and usefulness without changing the underlying facts.
Do not add facts, numbers, offer terms, time limits, promises, approvals, or business outcomes that were not supplied by the user or rules-based workflow.
Stay inside the supplied customer context, project context, selected follow-up strategy, and generated recommendation.
Do not override calculations, scores, statuses, recommendations, or rule-based outputs provided by the app.
For follow-up outputs, keep the message helpful, professional, and aligned with the selected tone.
If information is missing, say it is missing or keep the fallback framing.
Keep the output practical, professional, and aligned with the user's provided context.
""".strip()


def read_token() -> str | None:
    primary = _read_secret(PRIMARY_TOKEN_NAME)
    legacy = _read_secret(LEGACY_TOKEN_NAME)
    return primary or legacy


def stable_cache_key(prefix: str, value: object) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"{prefix}_{digest}"


def prepare_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    if len(prompt) > MAX_PROMPT_CHARS:
        prompt = prompt[:MAX_PROMPT_CHARS] + "\n\n[Input was trimmed for length before AI enhancement.]"
    return f"{AI_GUARDRAIL_PREFIX}\n\n---\n\n{prompt}"


def get_openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        _record_ai_diagnostic("OpenAI package is not installed.")
        return None

    token = read_token()
    if not token:
        _record_ai_diagnostic("No OpenAI API key configured.")
        return None

    return OpenAI(api_key=token)


def generate_ai_text(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    client = get_openai_client()
    if client is None:
        return None

    try:
        response = client.responses.create(model=model, input=prepare_prompt(prompt))
        _record_ai_diagnostic("AI enhancement succeeded.")
        return response.output_text
    except Exception as exc:
        _record_ai_diagnostic(f"AI enhancement failed: {exc.__class__.__name__}")
        return None


def enhance_text(prompt: str, fallback: str, cache_key: str) -> str:
    if cache_key not in st.session_state:
        generated = generate_ai_text(prompt)
        st.session_state[cache_key] = generated.strip() if generated else fallback
    return st.session_state[cache_key]


def get_ai_diagnostic() -> str:
    return st.session_state.get("ai_diagnostic", "")


def _read_secret(name: str) -> str | None:
    try:
        token = st.secrets.get(name, None)
    except Exception:
        token = None
    return token or os.getenv(name)


def _record_ai_diagnostic(message: str) -> None:
    if os.getenv("FOLLOWUPPILOT_DEBUG_AI") == "1":
        st.session_state["ai_diagnostic"] = message
