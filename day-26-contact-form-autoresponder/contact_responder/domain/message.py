from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


_WHITESPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\r\n|\r")


def _normalize_text(value: str) -> str:
    # Normalize newlines
    value = _MULTI_NEWLINE_RE.sub("\n", value)

    # Strip surrounding whitespace
    value = value.strip()

    # Remove trailing spaces per line
    lines = [line.rstrip() for line in value.split("\n")]
    value = "\n".join(lines)

    # Collapse internal excessive spaces (not newlines)
    value = _WHITESPACE_RE.sub(" ", value)

    return value


def _fingerprint_normalize(value: str) -> str:
    value = _normalize_text(value)
    value = value.lower()
    return value


@dataclass(frozen=True)
class ContactMessage:
    message_id: str
    name: str
    email: str
    subject: str
    message: str
    created_at: datetime
    source_ip: str

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        subject: str,
        message: str,
        source_ip: str,
        now: datetime | None = None,
    ) -> "ContactMessage":

        now = now or datetime.now(timezone.utc)

        normalized_name = _normalize_text(name)
        normalized_email = _normalize_text(email)
        normalized_subject = _normalize_text(subject)
        normalized_message = _normalize_text(message)

        return cls(
            message_id=str(uuid.uuid4()),
            name=normalized_name,
            email=normalized_email,
            subject=normalized_subject,
            message=normalized_message,
            created_at=now,
            source_ip=source_ip,
        )

    def fingerprint(self) -> str:
        base = (
            _fingerprint_normalize(self.name)
            + "|"
            + _fingerprint_normalize(self.email)
            + "|"
            + _fingerprint_normalize(self.subject)
            + "|"
            + _fingerprint_normalize(self.message)
        )

        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def email_context(self) -> dict[str, str]:
        # Explicit safe representation for email template use
        return {
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
        }