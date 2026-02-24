import os
from arbitrage_notifier.main import load_config


def test_env_override(monkeypatch):
    monkeypatch.setenv("ARBITRAGE_THRESHOLD", "0.01")
    config = load_config(None)
    assert config["alert_threshold_percent"] == 0.01