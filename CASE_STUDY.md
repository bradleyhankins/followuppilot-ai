# FollowUpPilot AI Case Study

## Overview

FollowUpPilot AI is a portfolio demonstration of a follow-up workflow assistant for home-service and local service businesses. It helps teams standardize what happens after a lead, appointment, estimate, or decision-stage conversation.

## Problem

Small service businesses often lose revenue because follow-up is inconsistent:

- reps delay follow-up after estimates
- message quality varies by rep
- CRM notes miss key context
- objections are not handled consistently
- managers lack visibility into next steps
- open leads can become overdue without a clear signal

## Solution

FollowUpPilot AI turns lead context into a structured follow-up plan. The app combines deterministic rules with optional AI-enhanced wording.

The user enters lead details, stage, notes, urgency, objection, last-contact date, and preferred channel. The app returns a recommended next action, suggested follow-up date, overdue status, customer-ready copy, CRM note, coaching note, and PDF report.

## Current Features

- typed lead input model
- user-friendly validation
- lead-stage handling for New Lead, Contacted, Appointment Set, Estimate Sent, Decision Pending, Won, and Closed Lost
- priority score and timing
- follow-up date suggestion
- overdue, due-today, and upcoming status
- channel-specific next action
- text, email, voicemail, CRM note, and manager coaching note
- call script and objection guidance
- public-safe sample scenarios
- PDF follow-up plan
- optional OpenAI enhancement with deterministic fallback
- pytest, Ruff, and CI smoke checks

## Business Value

The project demonstrates how lightweight workflow automation can improve follow-up consistency, CRM discipline, customer communication, and manager coaching without requiring an enterprise CRM build.

## Current Limitations

This is still a public Streamlit demo. It does not include authentication, saved lead lists, team dashboards, reminders, CRM sync, or a production database.

## Future Roadmap

Likely next improvements include CSV lead upload, a session-based manager table, open/overdue lead summaries, better demo screenshots, and eventually a private deployment path.
