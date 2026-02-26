from __future__ import annotations

import re
import string
from email.utils import parseaddr


NAME_MIN = 2
NAME_MAX = 100

SUBJECT_MIN = 3
SUBJECT_MAX = 150

MESSAGE_MIN = 10
MESSAGE_MAX = 5000

EMAIL_MAX = 254


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<\s*(script|iframe|img|a)\b", re.IGNORECASE)


class ValidationError(Exception):
    def __init__(self, code: str, field: str | None = None):
        self.code = code
        self.field = field
        super().__init__(code)


def _ensure_printable(value: str, field: str) -> None:
    for ch in value:
        if ch == "\n":
            continue
        if ch not in string.printable or ord(ch) < 32:
            raise ValidationError("unsafe_content", field)


def _validate_email(email: str) -> None:
    if "\n" in email or "\r" in email:
        raise ValidationError("unsafe_content", "email")

    if len(email) > EMAIL_MAX:
        raise ValidationError("too_long", "email")

    parsed_name, parsed_email = parseaddr(email)

    if parsed_email != email:
        raise ValidationError("invalid_format", "email")

    if email.count("@") != 1:
        raise ValidationError("invalid_format", "email")


def validate_contact_payload(payload: dict) -> None:

    required = ["name", "email", "subject", "message"]

    for field in required:
        if field not in payload:
            raise ValidationError("missing_field", field)

        if not isinstance(payload[field], str):
            raise ValidationError("invalid_format", field)

    name = payload["name"]
    email = payload["email"]
    subject = payload["subject"]
    message = payload["message"]

    # Length checks
    if not (NAME_MIN <= len(name) <= NAME_MAX):
        raise ValidationError("invalid_length", "name")

    if not (SUBJECT_MIN <= len(subject) <= SUBJECT_MAX):
        raise ValidationError("invalid_length", "subject")

    if not (MESSAGE_MIN <= len(message) <= MESSAGE_MAX):
        raise ValidationError("invalid_length", "message")

    # Control chars
    _ensure_printable(name, "name")
    _ensure_printable(email, "email")
    _ensure_printable(subject, "subject")
    _ensure_printable(message, "message")

    # Email validation
    _validate_email(email)

    # Header injection protection
    if "\n" in subject or "\r" in subject:
        raise ValidationError("unsafe_content", "subject")

    # HTML/script rejection
    if _HTML_TAG_RE.search(message) or _SCRIPT_RE.search(message):
        raise ValidationError("unsafe_content", "message")