# contact_responder/domain/spam.py

from __future__ import annotations

import re
from dataclasses import dataclass

from .message import ContactMessage


_REPEAT_RE = re.compile(r"(.)\1{6,}")


@dataclass(frozen=True)
class SpamConfig:
    blacklisted_phrases: list[str]
    suspicious_phrases: list[str]
    max_links: int
    excessive_length: int
    spam_threshold: int


@dataclass(frozen=True)
class SpamResult:
    spam_score: int
    flags: list[str]
    is_spam: bool


def _count_links(text: str) -> int:
    return (
        text.count("http://")
        + text.count("https://")
        + text.count("www.")
    )


def score_message(
    message: ContactMessage,
    config: SpamConfig,
    recent_fingerprints: set[str] | None = None,
) -> SpamResult:

    score = 0
    flags: list[str] = []

    content = message.message.lower()

    # Blacklisted phrases
    for phrase in config.blacklisted_phrases:
        if phrase.lower() in content:
            score += 1
            flags.append("blacklisted_phrase")
            break

    # Suspicious phrases
    for phrase in config.suspicious_phrases:
        if phrase.lower() in content:
            score += 1
            flags.append("suspicious_phrase")
            break

    # URL threshold
    if _count_links(content) > config.max_links:
        score += 1
        flags.append("too_many_links")

    # Excessive length
    if len(message.message) > config.excessive_length:
        score += 1
        flags.append("excessive_length")

    # Repeated characters
    if _REPEAT_RE.search(message.message):
        score += 1
        flags.append("repeated_characters")

    # Duplicate submission
    if recent_fingerprints and message.fingerprint() in recent_fingerprints:
        score += 1
        flags.append("duplicate_submission")

    return SpamResult(
        spam_score=score,
        flags=flags,
        is_spam=score >= config.spam_threshold,
    )