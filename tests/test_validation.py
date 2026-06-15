from __future__ import annotations

from datetime import date, timedelta

from core.validation import validate_lead_input

VALID_INPUTS = {
    "customer_name": "Avery Johnson",
    "company_name": "Summit Home Services",
    "service_type": "Roof Replacement",
    "lead_stage": "Estimate Sent",
    "context_notes": "Customer liked the project plan and asked for help comparing options.",
    "objection": "Price",
    "urgency": "High",
    "financing": "Yes",
    "tone": "Consultative",
    "last_contact_date": date.today().isoformat(),
    "estimate_amount": 1000,
    "preferred_channel": "All",
    "followup_intensity": "Standard",
}


def test_validation_accepts_representative_demo_input():
    assert validate_lead_input(VALID_INPUTS) == []


def test_validation_flags_blank_required_business_fields():
    messages = validate_lead_input({**VALID_INPUTS, "company_name": "   ", "service_type": ""})

    assert any("business or team" in message for message in messages)
    assert any("service type" in message.lower() for message in messages)


def test_validation_flags_invalid_email_phone_and_amount():
    messages = validate_lead_input(
        {
            **VALID_INPUTS,
            "customer_email": "not-an-email",
            "customer_phone": "12",
            "estimate_amount": -1,
        }
    )

    assert any("email" in message for message in messages)
    assert any("phone" in message for message in messages)
    assert any("zero or greater" in message for message in messages)


def test_validation_flags_future_last_contact_date():
    messages = validate_lead_input(
        {**VALID_INPUTS, "last_contact_date": (date.today() + timedelta(days=1)).isoformat()}
    )

    assert any("future" in message for message in messages)


def test_validation_flags_insufficient_context_for_decision_stage():
    messages = validate_lead_input({**VALID_INPUTS, "lead_stage": "Decision Pending", "context_notes": "No"})

    assert any("context" in message for message in messages)


def test_validation_flags_closed_lost_active_followup_default():
    messages = validate_lead_input({**VALID_INPUTS, "lead_stage": "Closed Lost"})

    assert any("Closed Lost" in message for message in messages)
