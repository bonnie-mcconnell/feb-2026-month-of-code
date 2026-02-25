import math
from typing import Dict, List

from keyword_discovery.domain.keyword import Keyword
from keyword_discovery.domain.scoring import TermScore
from keyword_discovery.pipeline.index_builder import CorpusIndex


class KeywordEngine:
    """
    Orchestrates IDF, TF-IDF aggregation, ranking,
    and long-tail filtering.
    """

    def __init__(self, index: CorpusIndex):
        self.index = index

    def compute_idf(self) -> Dict[str, float]:
        """
        IDF(term) = ln(total_docs / (1 + doc_frequency))
        """
        idf_values: Dict[str, float] = {}

        total_docs = self.index.total_documents

        for term, doc_ids in self.index.inverted_index.items():
            df = len(doc_ids)
            idf = math.log(total_docs / (1 + df))
            idf_values[term] = idf

        return idf_values

    def compute_tfidf(self) -> List[TermScore]:
        """
        Computes aggregated TF-IDF score per term.
        """
        idf_values = self.compute_idf()

        aggregated_scores: Dict[str, float] = {}

        for doc_id, tf_values in self.index.term_frequencies.items():
            for term, tf in tf_values.items():
                tfidf = tf * idf_values[term]
                aggregated_scores[term] = aggregated_scores.get(term, 0.0) + tfidf

        results: List[TermScore] = []

        for term, score in aggregated_scores.items():
            ngram_size = term.count(" ") + 1
            df = len(self.index.inverted_index[term])

            results.append(
                TermScore(
                    term=term,
                    ngram_size=ngram_size,
                    doc_frequency=df,
                    tfidf_score=score,
                )
            )

        return self._sort_terms(results)

    def extract_long_tail(
        self,
        scores: List[TermScore],
        min_doc_frequency: int,
        max_doc_frequency: int,
        min_score: float,
        require_multiword: bool = True,
    ) -> List[Keyword]:
        """
        Explicit long-tail filtering.
        """
        keywords: List[Keyword] = []

        for score in scores:
            if score.doc_frequency < min_doc_frequency:
                continue

            if score.doc_frequency > max_doc_frequency:
                continue

            if score.tfidf_score < min_score:
                continue

            if require_multiword and score.ngram_size < 2:
                continue

            keywords.append(
                Keyword(
                    term=score.term,
                    ngram_size=score.ngram_size,
                    doc_frequency=score.doc_frequency,
                    score=score.tfidf_score,
                )
            )

        return self._sort_keywords(keywords)

    @staticmethod
    def _sort_terms(terms: List[TermScore]) -> List[TermScore]:
        return sorted(
            terms,
            key=lambda t: (-t.tfidf_score, t.term),
        )

    @staticmethod
    def _sort_keywords(keywords: List[Keyword]) -> List[Keyword]:
        return sorted(
            keywords,
            key=lambda k: (-k.score, k.term),
        )