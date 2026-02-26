from datetime import datetime, timezone

from contact_responder.domain.message import ContactMessage


def _create_message(**overrides):
    base = {
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