from datetime import datetime, timezone
from typing import TypedDict, Unpack

from contact_responder.domain.message import ContactMessage


class _MessageInput(TypedDict, total=False):
    name: str
    email: str
    subject: str
    message: str
    source_ip: str


def _create_message(**overrides: Unpack[_MessageInput]):
    base: _MessageInput = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Project Inquiry",
        "message": "Hello there.",
        "source_ip": "1.2.3.4",
    }

    base.update(overrides)
    return ContactMessage.create(**base)


def test_normalization_strips_and_collapses_spaces():
    msg = _create_message(
        name="  Jane   Doe  ",
        message="Hello    world   "
    )

    assert msg.name == "Jane Doe"
    assert msg.message == "Hello world"


def test_newline_normalization():
    msg = _create_message(
        message="Line1\r\nLine2\rLine3"
    )

    assert msg.message == "Line1\nLine2\nLine3"


def test_fingerprint_deterministic():
    msg1 = _create_message()
    msg2 = _create_message()

    assert msg1.fingerprint() == msg2.fingerprint()


def test_fingerprint_changes_on_content_change():
    msg1 = _create_message()
    msg2 = _create_message(message="Different content")

    assert msg1.fingerprint() != msg2.fingerprint()


def test_uuid_unique():
    msg1 = _create_message()
    msg2 = _create_message()

    assert msg1.message_id != msg2.message_id


def test_created_at_override():
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)

    msg = ContactMessage.create(
        name="Jane",
        email="jane@example.com",
        subject="Hello",
        message="Message content",
        source_ip="1.2.3.4",
        now=now,
    )

    assert msg.created_at == now


def test_email_context_returns_expected_dict():
    msg = _create_message()
    ctx = msg.email_context()

    assert ctx["name"] == msg.name
    assert ctx["email"] == msg.email
    assert ctx["subject"] == msg.subject
    assert ctx["message"] == msg.message