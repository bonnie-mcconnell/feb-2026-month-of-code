import string
from typing import List


_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def tokenize(text: str) -> List[str]:
    """
    Deterministic whitespace tokenization.
    Strips leading/trailing punctuation.
    Does not normalize case.
    """
    raw_tokens = text.split()

    tokens = []
    for token in raw_tokens:
        cleaned = token.strip(string.punctuation)
        if cleaned:
            tokens.append(cleaned)

    return tokens