from typing import Dict, List

from .tokenizer import tokenize


# Domain-focused, intentionally small lexicon.
POSITIVE_WORDS: Dict[str, int] = {
    "strong": 1,
    "growth": 1,
    "beat": 1,
    "surge": 1,
    "upgrade": 1,
    "profit": 1,
    "record": 1,
    "gain": 1,
    "positive": 1,
    "outperform": 1,
}

NEGATIVE_WORDS: Dict[str, int] = {
    "loss": -1,
    "decline": -1,
    "miss": -1,
    "lawsuit": -1,
    "probe": -1,
    "investigation": -1,
    "downgrade": -1,
    "weak": -1,
    "cut": -1,
    "drop": -1,
}


def score_headline(headline: str) -> int:
    tokens = tokenize(headline)

    score = 0

    for token in tokens:
        if token in POSITIVE_WORDS:
            score += POSITIVE_WORDS[token]
        elif token in NEGATIVE_WORDS:
            score += NEGATIVE_WORDS[token]

    return score


def classify(score: int) -> str:
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"
