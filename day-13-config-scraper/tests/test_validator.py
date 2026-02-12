from src.validator import validate_extraction


def base_fields():
    return {
        "title": {"selector": "h1", "required": True, "non_empty": True},
        "author": {"selector": ".author", "required": False, "non_empty": True},
    }


def test_success_case():
    extraction = {
        "data": {"title": "Hello", "author": "Jane"},
        "missing_selectors": [],
    }

    result = validate_extraction(extraction, base_fields())

    assert result["status"] == "SUCCESS"
    assert result["errors"] == []


def test_missing_required_field():
    extraction = {
        "data": {"title": None, "author": "Jane"},
        "missing_selectors": ["title"],
    }

    result = validate_extraction(extraction, base_fields())

    assert result["status"] == "FAILED"
    assert "missing required field: title" in result["errors"]


def test_optional_missing_results_in_partial():
    extraction = {
        "data": {"title": "Hello", "author": None},
        "missing_selectors": ["author"],
    }

    result = validate_extraction(extraction, base_fields())

    assert result["status"] == "PARTIAL"


def test_required_empty_fails():
    extraction = {
        "data": {"title": "", "author": "Jane"},
        "missing_selectors": [],
    }

    result = validate_extraction(extraction, base_fields())

    assert result["status"] == "FAILED"
    assert "required field empty: title" in result["errors"]
