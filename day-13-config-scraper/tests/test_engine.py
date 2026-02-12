from src.engine import run_engine


def test_engine_success(monkeypatch):
    config = {
        "name": "test_source",
        "targets": [
            {
                "url": "http://example.com",
                "fields": {
                    "title": {"selector": "h1", "required": True, "non_empty": True}
                },
            }
        ],
    }

    def fake_fetch(url):
        return {
            "ok": True,
            "status_code": 200,
            "content": "<h1>Hello</h1>",
            "error": None,
        }

    monkeypatch.setattr("src.engine.fetch_url", fake_fetch)

    result = run_engine(config)

    assert result["results"][0]["status"] == "SUCCESS"


def test_engine_fetch_failure(monkeypatch):
    config = {
        "name": "test_source",
        "targets": [
            {
                "url": "http://bad-url.com",
                "fields": {
                    "title": {"selector": "h1", "required": True, "non_empty": True}
                },
            }
        ],
    }

    def fake_fetch(url):
        return {
            "ok": False,
            "status_code": None,
            "content": None,
            "error": "timeout",
        }

    monkeypatch.setattr("src.engine.fetch_url", fake_fetch)

    result = run_engine(config)

    assert result["results"][0]["status"] == "FAILED"
    assert "timeout" in result["results"][0]["errors"]
