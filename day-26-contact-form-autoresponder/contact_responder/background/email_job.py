import logging

logger = logging.getLogger(__name__)


def send_autoresponse(context: dict[str, str]) -> None:
    logger.info("Sending autoresponse to %s", context["email"])