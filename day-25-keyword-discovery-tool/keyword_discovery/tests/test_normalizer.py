from keyword_discovery.pipeline.normalizer import normalize_tokens, DEFAULT_STOPWORDS


def test_normalize_removes_stopwords_and_lowercases():
    tokens = ["The", "Deterministic", "Engine"]

    normalized = normalize_tokens(tokens, DEFAULT_STOPWORDS)

    assert normalized == ["deterministic", "engine"]


def test_normalize_removes_numeric_tokens():
    tokens = ["123", "model", "456"]

    normalized = normalize_tokens(tokens, set())

    assert normalized == ["model"]