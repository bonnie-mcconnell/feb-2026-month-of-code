import pytest
from arbitrage_notifier import main

def test_main_load_config():
    # just ensure main config loads without exceptions
    try:
        main.load_config()
    except Exception:
        pytest.fail("Config loading failed")