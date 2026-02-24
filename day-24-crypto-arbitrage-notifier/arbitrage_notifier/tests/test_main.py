from pathlib import Path
import json
import tempfile
from unittest.mock import patch, MagicMock

from arbitrage_notifier.main import run_once, run_forever, DEFAULT_CONFIG
from arbitrage_notifier.main import load_config


def test_load_config_success():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        json.dump({"foo": "bar"}, f)
        path = Path(f.name)

    config = load_config(path)

    assert config["foo"] == "bar"


def test_load_config_missing():
    path = Path("nonexistent.json")

    try:
        load_config(path)
    except FileNotFoundError:
        assert True
    else:
        assert False


def test_run_once_no_crash():
    config = DEFAULT_CONFIG.copy()

    with patch("arbitrage_notifier.main.build_clients") as mock_build:
        mock_binance = MagicMock()
        mock_coinbase = MagicMock()

        mock_binance.get_ticker.return_value = MagicMock()
        mock_coinbase.get_ticker.return_value = MagicMock()

        mock_build.return_value = (mock_binance, mock_coinbase)

        run_once(config)


def test_run_forever_single_iteration():
    config = DEFAULT_CONFIG.copy()
    config["poll_interval_seconds"] = 0

    with patch("arbitrage_notifier.main.run_once") as mock_run:
        with patch("time.sleep", side_effect=KeyboardInterrupt):
            run_forever(config)

        mock_run.assert_called()