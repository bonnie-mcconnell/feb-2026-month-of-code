import math
from typing import Dict, List, Optional

from keyword_discovery.domain.corpus import Corpus
from keyword_discovery.domain.document import Document
from keyword_discovery.domain.keyword import Keyword
from keyword_discovery.domain.scoring import TermScore
from keyword_discovery.pipeline.index_builder import build_index, CorpusIndex
from keyword_discovery.pipeline.tokenizer import tokenize
from keyword_discovery.pipeline.normalizer import normalize_tokens, load_stopwords
from keyword_discovery.pipeline.ngrams import generate_ngrams


class KeywordEngine:
    """
    Full pipeline orchestration:
    ingestion -> tokenization -> normalization -> n-grams
    -> indexing -> scoring -> long-tail extraction
    """

    def __init__(
        self,
        corpus: Corpus,
        ngrams: List[int],
        stopword_file: Optional[str] = None,
        remove_numeric: bool = True,
        scoring: str = "tfidf",
        suppress_subterms: bool = False,
    ):
        self.corpus = corpus
        self.ngrams = sorted(ngrams)
        self.stopwords = load_stopwords(stopword_file)
        self.remove_numeric = remove_numeric
        self.scoring = scoring
        self.suppress_subterms_flag = suppress_subterms

        self._prepare_documents()
        self.index = build_index(self.corpus)

    def _prepare_documents(self) -> None:
        """
        Mutates document tokens deterministically.
        This is the only controlled mutation point.
        """
        updated_docs: List[Document] = []

        for doc in self.corpus.documents:
            raw_tokens = tokenize(doc.content)

            normalized = normalize_tokens(
                raw_tokens,
                stopwords=self.stopwords,
                remove_numeric=self.remove_numeric,
            )

            ngram_tokens = generate_ngrams(normalized, self.ngrams)

            updated_docs.append(
                Document(
                    id=doc.id,
                    path=doc.path,
                    content=doc.content,
                    tokens=ngram_tokens,
                )
            )

        self.corpus = Corpus(updated_docs)


    def compute_document_keywords(self, doc_id: str) -> List[TermScore]:
        """
        Return TF-IDF ranked terms for a single document.
        """
        vectors = self._compute_document_tfidf_vectors()

        if doc_id not in vectors:
            raise ValueError("Invalid document ID provided.")

        doc_vector = vectors[doc_id]

        results: List[TermScore] = []

        for term, score in doc_vector.items():
            results.append(
                TermScore(
                    term=term,
                    ngram_size=term.count(" ") + 1,
                    doc_frequency=len(self.index.inverted_index[term]),
                    tfidf_score=score,
                )
            )

        return self._sort_terms(results)

    def _compute_document_tfidf_vectors(self) -> Dict[str, Dict[str, float]]:
        """
        Build per-document TF-IDF vectors:
        {doc_id: {term: tfidf_score}}
        """
        idf_values = self.compute_idf()
        vectors: Dict[str, Dict[str, float]] = {}

        for doc_id, tf_values in self.index.term_frequencies.items():
            vectors[doc_id] = {}
            for term, tf in tf_values.items():
                vectors[doc_id][term] = tf * idf_values[term]

        return vectors
    

    def compute_document_similarity(self, doc_id_a: str, doc_id_b: str) -> float:
        """
        Compute cosine similarity between two documents
        using TF-IDF vectors.
        """

        vectors = self._compute_document_tfidf_vectors()

        vec_a = vectors.get(doc_id_a)
        vec_b = vectors.get(doc_id_b)

        if vec_a is None or vec_b is None:
            raise ValueError("Invalid document ID provided.")

        all_terms = set(vec_a.keys()) | set(vec_b.keys())

        dot = sum(vec_a.get(t, 0.0) * vec_b.get(t, 0.0) for t in all_terms)

        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot / (norm_a * norm_b)


    def export_inverted_index(self) -> dict:
        """
        Export inverted index as serializable dictionary.
        """
        export = {}

        for term, postings in self.index.inverted_index.items():
            export[term] = sorted(postings)

        return export
    
    # ------------------------
    # Scoring Logic
    # ------------------------
    def compute_scores(self) -> List[TermScore]:
        if self.scoring == "bm25":
            scores = self.compute_bm25()
        else:
            scores = self.compute_tfidf()

        if self.suppress_subterms_flag:
            scores = self._suppress_subsumed(scores)

        return scores


    def suppress_subsumed(self, scores: List[TermScore]) -> List[TermScore]:
        """
        Public wrapper for subsumption suppression.
        Kept separate so it can be tested independently.
        """
        return self._suppress_subsumed(scores)

    
    def _suppress_subsumed(self, scores: List[TermScore]) -> List[TermScore]:
        selected: List[TermScore] = []
        selected_terms = set()

        for score in scores:
            term_tokens = score.term.split()

            # if any selected term fully contains this term, skip
            if any(
                set(term_tokens).issubset(set(existing.split()))
                for existing in selected_terms
            ):
                continue

            selected.append(score)
            selected_terms.add(score.term)

        return selected


    def compute_idf(self) -> Dict[str, float]:
        idf_values: Dict[str, float] = {}
        total_docs = self.index.total_documents

        for term, doc_ids in self.index.inverted_index.items():
            df = len(doc_ids)
            idf = math.log(total_docs / (1 + df))
            idf_values[term] = idf

        return idf_values

    def compute_tfidf(self) -> List[TermScore]:
        idf_values = self.compute_idf()
        aggregated_scores: Dict[str, float] = {}

        for doc_id, tf_values in self.index.term_frequencies.items():
            for term, tf in tf_values.items():
                tfidf = tf * idf_values[term]
                aggregated_scores[term] = aggregated_scores.get(term, 0.0) + tfidf

        results: List[TermScore] = []

        for term, score in aggregated_scores.items():
            results.append(
                TermScore(
                    term=term,
                    ngram_size=term.count(" ") + 1,
                    doc_frequency=len(self.index.inverted_index[term]),
                    tfidf_score=score,
                )
            )

        return self._sort_terms(results)


    def compute_bm25(self, k1: float = 1.5, b: float = 0.75) -> List[TermScore]:
        N = self.index.total_documents

        avg_doc_length = sum(
            sum(tf.values())
            for tf in self.index.term_frequencies.values()
        ) / N

        results: Dict[str, float] = {}

        for term, doc_ids in self.index.inverted_index.items():
            df = len(doc_ids)
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

            for doc_id in doc_ids:
                tf = self.index.term_frequencies[doc_id][term]
                doc_length = sum(self.index.term_frequencies[doc_id].values())

                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))

                score = idf * (numerator / denominator)

                results[term] = results.get(term, 0.0) + score

        output: List[TermScore] = []

        for term, score in results.items():
            output.append(
                TermScore(
                    term=term,
                    ngram_size=term.count(" ") + 1,
                    doc_frequency=len(self.index.inverted_index[term]),
                    tfidf_score=score,
                )
            )

        return self._sort_terms(output)

    def extract_long_tail(
        self,
        scores: List[TermScore],
        min_doc_frequency: int,
        max_doc_frequency: int,
        min_score: float,
        require_multiword: bool = True,
    ) -> List[Keyword]:

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
    