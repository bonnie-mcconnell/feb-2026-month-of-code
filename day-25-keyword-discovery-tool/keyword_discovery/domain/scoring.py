from dataclasses import dataclass


@dataclass(frozen=True)
class TermScore:
    """
    Aggregated corpus-level TF-IDF score.
    """
    term: str
    ngram_size: int
    doc_frequency: int
    tfidf_score: float