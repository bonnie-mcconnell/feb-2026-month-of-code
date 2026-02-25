from keyword_discovery.pipeline.ngrams import generate_ngrams


def test_generate_ngrams():
    tokens = ["deterministic", "corpus", "analysis"]

    ngrams = generate_ngrams(tokens, [1, 2])

    assert ngrams == [
        "deterministic",
        "corpus",
        "analysis",
        "deterministic corpus",
        "corpus analysis",
    ]