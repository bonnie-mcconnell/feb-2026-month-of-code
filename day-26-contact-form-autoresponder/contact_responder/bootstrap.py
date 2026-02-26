from fastapi import FastAPI

from contact_responder.api.routes import router
from contact_responder.infra.config_loader import load_spam_config
from contact_responder.infra.logger import configure_logging
from contact_responder.infra.rate_limiter import RateLimiter
from contact_responder.services.responder_service import ResponderService


def create_service(config_path: str) -> ResponderService:
    configure_logging()

    spam_config = load_spam_config(config_path)

    rate_limiter = RateLimiter(
        max_requests=10,
        window_seconds=60,
    )

    return ResponderService(
        spam_config=spam_config,
        rate_limiter=rate_limiter,
    )


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app

app = create_app()