import pytest
from pathlib import Path
from keyword_discovery.pipeline.normalizer import (
    load_stopwords,
    normalize_tokens,
    DEFAULT_STOPWORDS,
)


def test_load_stopwords_default():
    assert load_stopwords(None) == DEFAULT_STOPWORDS


def test_load_stopwords_from_file(tmp_path):
    file = tmp_path / "stop.txt"
    file.write_text("Alpha\nBeta\n", encoding="utf-8")

    words = load_stopwords(str(file))

    assert "alpha" in words
    assert "beta" in words


def test_load_stopwords_missing_file():
    with pytest.raises(FileNotFoundError):
        load_stopwords("nonexistent.txt")


def test_normalize_remove_numeric_false():
    tokens = ["Alpha", "123"]
    result = normalize_tokens(tokens, stopwords=set(), remove_numeric=False)

    assert result == ["alpha", "123"]
    

def test_normalize_removes_stopwords_and_lowercases():
    tokens = ["The", "Deterministic", "Engine"]

    normalized = normalize_tokens(tokens, DEFAULT_STOPWORDS)

    assert normalized == ["deterministic", "engine"]


def test_normalize_removes_numeric_tokens():
    tokens = ["123", "model", "456"]

    normalized = normalize_tokens(tokens, set())

    assert normalized == ["model"]