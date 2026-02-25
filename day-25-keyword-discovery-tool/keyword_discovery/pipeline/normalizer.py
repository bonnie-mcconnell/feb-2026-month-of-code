from pathlib import Path
from typing import Iterable, List, Set


DEFAULT_STOPWORDS: Set[str] = {
    "the", "and", "is", "in", "to", "of", "for", "on",
    "with", "as", "by", "at", "an", "be", "this", "that"
}


def load_stopwords(file_path: str | None) -> Set[str]:
    """
    Load stopwords from file if provided.
    Otherwise return embedded default set.
    """
    if file_path is None:
        return DEFAULT_STOPWORDS

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Stopword file not found: {file_path}")

    words = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        word = line.strip().lower()
        if word:
            words.add(word)

    return words


def normalize_tokens(
    tokens: Iterable[str],
    stopwords: Set[str],
    remove_numeric: bool = True,
) -> List[str]:
    """
    Lowercases and filters tokens deterministically.
    """
    normalized: List[str] = []

    for token in tokens:
        token_lower = token.lower()

        if remove_numeric and token_lower.isdigit():
            continue

        if token_lower in stopwords:
            continue

        normalized.append(token_lower)

    return normalized