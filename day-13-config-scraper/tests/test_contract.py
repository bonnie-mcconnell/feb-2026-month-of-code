from src.engine import run_engine
from src.schema import validate_output_schema, get_schema_errors

def test_engine_contract(monkeypatch):
    config = {
        "name": "test_blog",
        "targets": [
            {"url": "http://example.com", "fields": {"title": {"selector": "h1", "required": True, "non_empty": True}}}
        ]
    }

    # Monkeypatch fetch_url to avoid real HTTP
    def fake_fetch(url):
        return {"ok": True, "status_code": 200, "content": "<h1>Hello</h1>", "error": None}

    monkeypatch.setattr("src.engine.fetch_url", fake_fetch)

    result = run_engine(config)

    # Schema validation
    if not validate_output_schema(result):
        errors = get_schema_errors(result)
        raise AssertionError(f"Engine output violates JSON schema:\n" + "\n".join(errors))

    # Snapshot test
    expected = {
        "source": "test_blog",
        "results": [{"url": "http://example.com", "status": "SUCCESS", "data": {"title": "Hello"}, "errors": []}]
    }

    assert result == expected, "Engine output does not match expected snapshot"

def test_engine_success_with_optional_missing(monkeypatch):
    config = {
        "name": "test_blog",
        "targets": [
            {"url": "http://example.com", "fields": {
                "title": {"selector": "h1", "required": True},
                "author": {"selector": ".author", "required": False}
            }}
        ]
    }

    def fake_fetch(url):
        return {"ok": True, "status_code": 200, "content": "<h1>Hello</h1>", "error": None}

    monkeypatch.setattr("src.engine.fetch_url", fake_fetch)

    result = run_engine(config)

    # Ensure schema is valid
    if not validate_output_schema(result):
        raise AssertionError("\n".join(get_schema_errors(result)))

    # PARTIAL because required fields passed
    assert result["results"][0]["status"] == "PARTIAL"

    assert result["results"][0]["errors"] == []


def test_engine_failed(monkeypatch):
    config = {
        "name": "test_blog",
        "targets": [
            {"url": "http://example.com", "fields": {"title": {"selector": "h1", "required": True}}}
        ]
    }

    def fake_fetch(url):
        return {"ok": False, "status_code": 500, "content": "", "error": "Server error"}

    monkeypatch.setattr("src.engine.fetch_url", fake_fetch)

    result = run_engine(config)

    # Schema validation
    if not validate_output_schema(result):
        raise AssertionError("\n".join(get_schema_errors(result)))

    assert result["results"][0]["status"] == "FAILED"
    assert "Server error" in result["results"][0]["errors"][0]