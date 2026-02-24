import logging
from arbitrage_notifier.infra import logging_config

def test_logger_setup():
    logger = logging.getLogger("arbitrage_notifier")
    assert logger is not None

def test_logging_config_json():
    logging_config.configure_logging(json_logs=True)

def test_logging_config_console():
    logging_config.configure_logging(json_logs=False)