import time
from src.engine import run_engine
from src.schema import validate_output_schema
import pytest

def test_engine_runtime(monkeypatch):
    """
    FAANG-level deterministic guardrail:
    The engine should finish within a reasonable time for small configs.
    """

    config = {
        "name": "perf_blog",
        "targets": [
            {
                "url": f"http://example.com/article{i}",
                "fields": {"title": {"selector": "h1", "required": True}}
            } for i in range(5)  # small batch of targets
        ]
    }

    # Fake fetch to simulate network delay
    def fake_fetch(url):
        return {
            "ok": True,
            "status_code": 200,
            "content": "<h1>Hello World</h1>",
            "error": None
        }

    monkeypatch.setattr("src.engine", "fetch_url", fake_fetch)

    # Measure runtime
    start = time.perf_counter()
    result = run_engine(config)
    end = time.perf_counter()
    duration = end - start

    # Assert schema correctness
    assert validate_output_schema(result)

    # FAANG-level guardrail: engine must finish < 2s for 5 targets
    assert duration < 2.0, f"Engine took too long: {duration:.2f}s"
