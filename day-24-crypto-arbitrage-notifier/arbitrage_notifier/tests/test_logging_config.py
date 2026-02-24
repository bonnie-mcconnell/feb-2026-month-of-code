import logging
from arbitrage_notifier.infra import logging_config

def test_logger_setup():
    logger = logging.getLogger("arbitrage_notifier")
    assert logger is not None