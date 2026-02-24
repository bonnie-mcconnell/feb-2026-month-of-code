from pathlib import Path
import json
import tempfile

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