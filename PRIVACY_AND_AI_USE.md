# Privacy and AI Use

FollowUpPilot AI is a public portfolio demo and sales workflow assistant. It is designed for fictional, sample, or generalized customer follow-up scenarios.

## User Data Guidance

Do not enter sensitive, confidential, regulated, or private information into the public demo.

Avoid entering:

- real customer personally identifiable information
- payment details
- financing application details
- medical, legal, or regulated data
- internal company secrets
- proprietary pricing, contracts, or confidential business records
- passwords, API keys, or credentials

Optional email and phone fields exist to model realistic workflows, but they are not required for public demo use.

## AI Processing

When `OPENAI_API_KEY` or `OPENAI_TOKEN` is configured, selected user inputs may be sent to the AI provider to improve copy-center wording.

The app is built so that:

- deterministic rules are the source of truth
- AI only improves wording, clarity, tone, and structure
- AI should not invent offers, deadlines, approvals, or promises
- AI failure falls back to rules-based output
- the app does not intentionally store user-submitted data

## Secrets

Use Streamlit secrets or environment variables for API keys. Do not commit `.streamlit/secrets.toml`; it is ignored by git.

Preferred:

```bash
OPENAI_API_KEY=your_api_key_here
```

Legacy compatibility:

```bash
OPENAI_TOKEN=your_api_key_here
```

## Diagnostics

AI diagnostics are only recorded when `FOLLOWUPPILOT_DEBUG_AI=1` is set. Diagnostics are intentionally high-level and do not expose secrets, stack traces, or sensitive input content.

## Public Demo Note

All built-in sample names, companies, and scenarios are fictional and created for portfolio demonstration purposes.
