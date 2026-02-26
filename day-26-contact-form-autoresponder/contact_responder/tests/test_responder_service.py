from contact_responder.services.responder_service import ResponderService
from contact_responder.domain.spam import SpamConfig
from contact_responder.infra.rate_limiter import RateLimiter


# --- Helpers --- #
def _config_test():
    """SpamConfig for tests, lower threshold for deterministic spam"""
    return SpamConfig(
        blacklisted_phrases=["buy now", "free money"],
        suspicious_phrases=["click here", "limited offer"],
        max_links=2,
        excessive_length=2000,
        spam_threshold=1,  # lower for testing
    )


def _valid_payload():
    return {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "This is a valid message.",
        "source_ip": "1.2.3.4",
    }


# --- Tests --- #
def test_valid_not_spam():
    service = ResponderService(spam_config=_config_test())

    result = service.process(_valid_payload())

    assert result["status"] == "ok"
    assert result["is_spam"] is False


def test_blacklisted_phrase_spam():
    service = ResponderService(spam_config=_config_test())

    payload = _valid_payload()
    payload["message"] = "Buy now this product"

    result = service.process(payload)

    assert result["is_spam"] is True


def test_rate_limited():
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    service = ResponderService(spam_config=_config_test(), rate_limiter=limiter)

    payload = _valid_payload()

    service.process(payload)
    result = service.process(payload)

    assert result["status"] == "rate_limited"


def test_service_rate_limited(mocker):
    mock_rate = mocker.Mock()
    mock_rate.allow.return_value = False

    # Use correct SpamConfig object instead of string path
    service = ResponderService(spam_config=_config_test(), rate_limiter=mock_rate)
    result = service.process({
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "Valid message",
        "source_ip": "1.2.3.4",
    })
    assert result["status"] == "rate_limited"