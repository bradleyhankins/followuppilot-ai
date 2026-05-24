from __future__ import annotations

import os

import streamlit as st

DEFAULT_MODEL = "gpt-4.1-mini"


def _read_token() -> str | None:
    token = None
    try:
        token = st.secrets.get("OPENAI_TOKEN", None)
    except Exception:
        token = None
    return token or os.getenv("OPENAI_TOKEN")


def get_openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        return None

    token = _read_token()
    if not token:
        return None

    return OpenAI(api_key=token)


def generate_ai_text(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    client = get_openai_client()
    if client is None:
        return None

    try:
        response = client.responses.create(model=model, input=prompt)
        return response.output_text
    except Exception:
        return None


def enhance_text(prompt: str, fallback: str, cache_key: str) -> str:
    if cache_key not in st.session_state:
        st.session_state[cache_key] = generate_ai_text(prompt) or fallback
    return st.session_state[cache_key]
