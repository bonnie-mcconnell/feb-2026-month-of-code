from keyword_discovery.domain.document import Document
from keyword_discovery.domain.corpus import Corpus
from keyword_discovery.services.keyword_engine import KeywordEngine


def test_full_pipeline_determinism():
    doc1 = Document(
        id="doc_0001",
        path="a.txt",
        content="Deterministic corpus analysis",
        tokens=[]
    )

    doc2 = Document(
        id="doc_0002",
        path="b.txt",
        content="Corpus indexing deterministic parsing",
        tokens=[]
    )

    corpus = Corpus([doc1, doc2])

    engine1 = KeywordEngine(corpus, ngrams=[1, 2])
    scores1 = engine1.compute_tfidf()

    engine2 = KeywordEngine(corpus, ngrams=[1, 2])
    scores2 = engine2.compute_tfidf()

    assert scores1 == scores2