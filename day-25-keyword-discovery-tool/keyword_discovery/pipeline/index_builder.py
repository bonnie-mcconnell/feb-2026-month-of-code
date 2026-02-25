from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Set

from keyword_discovery.domain.corpus import Corpus


@dataclass(frozen=True)
class CorpusIndex:
    term_frequencies: Dict[str, Dict[str, float]]
    inverted_index: Dict[str, Set[str]]
    total_documents: int


def build_index(corpus: Corpus) -> CorpusIndex:
    """
    Builds TF values per document and inverted index.
    """
    term_counts: Dict[str, Dict[str, int]] = {}
    inverted_index: Dict[str, Set[str]] = defaultdict(set)

    for doc in corpus.documents:
        if not doc.tokens:
            raise ValueError(f"Document has no tokens: {doc.id}")

        counts: Dict[str, int] = defaultdict(int)

        for token in doc.tokens:
            counts[token] += 1

        term_counts[doc.id] = dict(counts)

        for term in counts.keys():
            inverted_index[term].add(doc.id)

    term_frequencies: Dict[str, Dict[str, float]] = {}

    for doc_id, counts in term_counts.items():
        total_terms = sum(counts.values())

        tf_values: Dict[str, float] = {}

        for term, count in counts.items():
            tf = count / total_terms
            tf_values[term] = tf

        term_frequencies[doc_id] = tf_values

    return CorpusIndex(
        term_frequencies=term_frequencies,
        inverted_index=dict(inverted_index),
        total_documents=corpus.size,
    )