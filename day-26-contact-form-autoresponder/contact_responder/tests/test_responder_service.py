from contact_responder.services.responder_service import ResponderService
from contact_responder.domain.spam import SpamConfig
from contact_responder.infra.rate_limiter import RateLimiter


def _config():
    return SpamConfig(
        blacklisted_phrases=["buy now"],
        suspicious_phrases=[],
        max_links=2,
        excessive_length=500,
        spam_threshold=1,
    )


def _valid_payload():
    return {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "This is a valid message.",
        "source_ip": "1.2.3.4",
    }


def test_valid_not_spam():
    service = ResponderService(_config())

    result = service.process(_valid_payload())

    assert result["status"] == "ok"
    assert result["is_spam"] is False


def test_blacklisted_phrase_spam():
    service = ResponderService(_config())

    payload = _valid_payload()
    payload["message"] = "Buy now this product"

    result = service.process(payload)

    assert result["is_spam"] is True


def test_rate_limited():
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    service = ResponderService(_config(), rate_limiter=limiter)

    payload = _valid_payload()

    service.process(payload)
    result = service.process(payload)

    assert result["status"] == "rate_limited"