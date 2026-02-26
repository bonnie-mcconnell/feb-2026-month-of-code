import pytest

from contact_responder.domain.message import ContactMessage
from contact_responder.domain.spam import (
    SpamConfig,
    score_message,
)


def _msg(message: str):
    return ContactMessage.create(
        name="Jane Doe",
        email="jane@example.com",
        subject="Hello",
        message=message,
        source_ip="1.2.3.4",
    )


BASE_CONFIG = SpamConfig(
    blacklisted_phrases=["bitcoin"],
    suspicious_phrases=["investment opportunity"],
    max_links=2,
    excessive_length=200,
    spam_threshold=3,
)


def test_blacklisted_phrase_detected():
    msg = _msg("This contains bitcoin promotion")

    result = score_message(msg, BASE_CONFIG)

    assert result.spam_score == 1
    assert "blacklisted_phrase" in result.flags
    assert result.is_spam is False


def test_suspicious_phrase_detected():
    msg = _msg("This is an investment opportunity")

    result = score_message(msg, BASE_CONFIG)

    assert result.spam_score == 1
    assert "suspicious_phrase" in result.flags


def test_too_many_links_detected():
    msg = _msg("http://a.com http://b.com http://c.com")

    result = score_message(msg, BASE_CONFIG)

    assert result.spam_score == 1
    assert "too_many_links" in result.flags


def test_excessive_length_detected():
    msg = _msg("A" * 201)

    result = score_message(msg, BASE_CONFIG)

    assert result.spam_score == 1
    assert "excessive_length" in result.flags


def test_repeated_characters_detected():
    msg = _msg("Helloooooooooooo")

    result = score_message(msg, BASE_CONFIG)

    assert result.spam_score == 1
    assert "repeated_characters" in result.flags


def test_duplicate_submission_detected():
    msg = _msg("Normal content")

    fingerprint = msg.fingerprint()

    result = score_message(
        msg,
        BASE_CONFIG,
        recent_fingerprints={fingerprint},
    )

    assert result.spam_score == 1
    assert "duplicate_submission" in result.flags


def test_threshold_boundary():
    msg = _msg("bitcoin investment opportunity http://a.com http://b.com http://c.com")

    result = score_message(msg, BASE_CONFIG)

    assert result.spam_score >= 3
    assert result.is_spam is True


def test_spam_scoring_deterministic():
    msg = _msg("bitcoin test message")

    result1 = score_message(msg, BASE_CONFIG)
    result2 = score_message(msg, BASE_CONFIG)

    assert result1 == result2