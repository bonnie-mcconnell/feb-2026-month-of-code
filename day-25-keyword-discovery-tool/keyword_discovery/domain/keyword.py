from dataclasses import dataclass


@dataclass(frozen=True)
class Keyword:
    term: str
    ngram_size: int
    doc_frequency: int
    score: float