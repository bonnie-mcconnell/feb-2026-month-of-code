import string
from typing import List


# Small, explicit stopword list.
# We keep this conservative to avoid accidentally removing signal.
STOPWORDS = {
    "the",
    "and",
    "of",
    "to",
    "in",
    "for",
    "on",
    "at",
    "with",
    "a",
    "an",
}


def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    if not text:
        return []

    text = text.lower()

    # remove punctuation
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)

    tokens = text.split()

    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]

    return tokens
