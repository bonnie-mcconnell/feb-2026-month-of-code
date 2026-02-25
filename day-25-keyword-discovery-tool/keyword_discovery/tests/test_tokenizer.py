from keyword_discovery.pipeline.tokenizer import tokenize


def test_tokenize_strips_punctuation():
    text = "Deterministic parsing, indexing."
    tokens = tokenize(text)

    assert tokens == ["Deterministic", "parsing", "indexing"]