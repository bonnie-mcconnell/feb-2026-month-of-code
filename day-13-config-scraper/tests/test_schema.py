from src.schema import validate_output_schema, get_schema_errors

def test_valid_output():
    output = {
        "source": "example_blog",
        "results": [
            {
                "url": "http://example.com",
                "status": "SUCCESS",
                "data": {"title": "Hello"},
                "errors": [],
            }
        ],
    }
    assert validate_output_schema(output)

def test_invalid_output_missing_keys():
    output = {
        "source": "example_blog",
        "results": [{}],  # missing all keys
    }
    errors = get_schema_errors(output)
    assert len(errors) >= 4  # url, status, data, errors missing

def test_invalid_data_type():
    output = {
        "source": "example_blog",
        "results": [
            {
                "url": 123,
                "status": "SUCCESS",
                "data": "not a dict",
                "errors": "not a list",
            }
        ],
    }
    errors = get_schema_errors(output)
    assert any("'url' must be str" in e for e in errors)
    assert any("'data' must be dict or None" in e for e in errors)
    assert any("'errors' must be list" in e for e in errors)
