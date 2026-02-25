from dataclasses import dataclass


@dataclass(frozen=True)
class Keyword:
    """
    Long-tail keyword candidate.
    """
    term: str
    ngram_size: int
    doc_frequency: int
    score: float