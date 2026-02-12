from src.extractor import extract_fields


HTML = """
<html>
  <body>
    <h1>   Example   Title   </h1>
    <div class="author">John Doe</div>
  </body>
</html>
"""


def test_extract_basic_fields():
    fields = {
        "title": {"selector": "h1", "required": True, "non_empty": True},
        "author": {"selector": ".author", "required": False, "non_empty": True},
    }

    result = extract_fields(HTML, fields)

    assert result["data"]["title"] == "Example Title"
    assert result["data"]["author"] == "John Doe"
    assert result["missing_selectors"] == []


def test_missing_selector():
    fields = {
        "title": {"selector": "h1", "required": True, "non_empty": True},
        "date": {"selector": ".date", "required": False, "non_empty": False},
    }

    result = extract_fields(HTML, fields)

    assert result["data"]["date"] is None
    assert "date" in result["missing_selectors"]
