from src.preprocess import preprocess_text


def test_trailing_whitespace_removed():
    raw = "Hello world   \nThis is a test\t\t\n"
    processed = preprocess_text(raw)

    assert processed == "Hello world\nThis is a test\n"


def test_excessive_blank_lines_collapsed():
    raw = "Para one\n\n\n\nPara two"
    processed = preprocess_text(raw)

    assert processed == "Para one\n\nPara two"


def test_unicode_normalization_preserves_visible_text():
    raw = "Cafe\u0301"
    processed = preprocess_text(raw)

    # Should normalize to a single composed character
    assert processed == "Café"


def test_multiple_spaces_collapsed():
    raw = "This   has    too many   spaces"
    processed = preprocess_text(raw)

    assert processed == "This has too many spaces"


def test_idempotent_behavior():
    raw = "Line one  \n\n\nLine two"
    once = preprocess_text(raw)
    twice = preprocess_text(once)

    assert once == twice
