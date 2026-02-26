from contact_responder.domain.message import ContactMessage
from contact_responder.domain.validation import (
    validate_contact_payload,
    ValidationError,
)
from contact_responder.domain.spam import (
    score_message,
    SpamConfig,
)
from contact_responder.infra.rate_limiter import RateLimiter


class ResponderService:
    def __init__(
        self,
        spam_config: SpamConfig,
        rate_limiter: RateLimiter | None = None,
    ):
        self.spam_config = spam_config
        self.rate_limiter = rate_limiter

    def process(self, payload: dict) -> dict:

        try:
            validate_contact_payload(payload)
        except ValidationError as exc:
            return {
                "status": "invalid",
                "error": exc.code,
                "field": exc.field,
            }

        source_ip = payload.get("source_ip", "0.0.0.0")

        if self.rate_limiter and not self.rate_limiter.allow(source_ip):
            return {
                "status": "rate_limited"
            }

        message = ContactMessage.create(
            name=payload["name"],
            email=payload["email"],
            subject=payload["subject"],
            message=payload["message"],
            source_ip=source_ip,
        )

        spam_result = score_message(message, self.spam_config)

        return {
            "status": "ok",
            "message_id": message.message_id,
            "spam_score": spam_result.spam_score,
            "is_spam": spam_result.is_spam,
            "flags": spam_result.flags,
            "fingerprint": message.fingerprint(),
            "email_context": message.email_context(),
        }
    
# TODO: add logging and audit creation