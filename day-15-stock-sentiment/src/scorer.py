import json
from pathlib import Path
from typing import Dict

from .tokenizer import tokenize


WEIGHTS_PATH = Path("config/weights.json")


def load_weights() -> tuple[Dict[str, float], Dict[str, float]]:
    with open(WEIGHTS_PATH, "r") as f:
        data = json.load(f)

    positive = {k: float(v) for k, v in data["positive"].items()}
    negative = {k: float(v) for k, v in data["negative"].items()}

    return positive, negative


POSITIVE_WORDS, NEGATIVE_WORDS = load_weights()


def score_headline(headline: str) -> float:
    tokens = tokenize(headline)

    score = 0.0
    matched = 0

    for token in tokens:
        if token in POSITIVE_WORDS:
            score += POSITIVE_WORDS[token]
            matched += 1
        elif token in NEGATIVE_WORDS:
            score += NEGATIVE_WORDS[token]
            matched += 1

    # Optional normalization to prevent long headlines dominating
    if matched > 0:
        score = score / matched

    return score


def classify(score: float) -> str:
    if score > 0.25:
        return "positive"
    if score < -0.25:
        return "negative"
    return "neutral"
