import pytest

from contact_responder.domain.validation import (
    validate_contact_payload,
    ValidationError,
    NAME_MIN,
    NAME_MAX,
    SUBJECT_MIN,
    SUBJECT_MAX,
    MESSAGE_MIN,
    MESSAGE_MAX,
)


VALID_PAYLOAD = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "subject": "Project Inquiry",
    "message": "I'd like to discuss a project opportunity.",
}


def test_valid_payload_passes():
    validate_contact_payload(VALID_PAYLOAD)


@pytest.mark.parametrize("field", ["name", "email", "subject", "message"])
def test_missing_field_raises(field):
    payload = VALID_PAYLOAD.copy()
    payload.pop(field)

    with pytest.raises(ValidationError) as exc:
        validate_contact_payload(payload)

    assert exc.value.code == "missing_field"
    assert exc.value.field == field


def test_invalid_email_format():
    payload = VALID_PAYLOAD.copy()
    payload["email"] = "not-an-email"

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)


def test_email_header_injection_rejected():
    payload = VALID_PAYLOAD.copy()
    payload["email"] = "jane@example.com\nbcc:evil@example.com"

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)


def test_subject_header_injection_rejected():
    payload = VALID_PAYLOAD.copy()
    payload["subject"] = "Hello\nInjected"

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)


def test_html_rejected():
    payload = VALID_PAYLOAD.copy()
    payload["message"] = "<script>alert('x')</script>"

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)


def test_control_character_rejected():
    payload = VALID_PAYLOAD.copy()
    payload["message"] = "Hello\x01World"

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)


def test_name_length_boundaries():
    payload = VALID_PAYLOAD.copy()
    payload["name"] = "A" * (NAME_MIN - 1)

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)

    payload["name"] = "A" * NAME_MAX
    validate_contact_payload(payload)


def test_subject_length_boundaries():
    payload = VALID_PAYLOAD.copy()
    payload["subject"] = "A" * (SUBJECT_MIN - 1)

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)

    payload["subject"] = "A" * SUBJECT_MAX
    validate_contact_payload(payload)


def test_message_length_boundaries():
    payload = VALID_PAYLOAD.copy()
    payload["message"] = "A" * (MESSAGE_MIN - 1)

    with pytest.raises(ValidationError):
        validate_contact_payload(payload)

    payload["message"] = "A" * MESSAGE_MAX
    validate_contact_payload(payload)