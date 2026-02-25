from keyword_discovery.domain.document import Document
from keyword_discovery.domain.corpus import Corpus
from keyword_discovery.services.keyword_engine import KeywordEngine
from keyword_discovery.pipeline.ingestion import ingest_directory


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


def test_full_pipeline_deterministic(tmp_path):
    file = tmp_path / "doc.txt"
    file.write_text("alpha beta beta gamma", encoding="utf-8")

    corpus = ingest_directory(tmp_path)

    engine1 = KeywordEngine(corpus, ngrams=[1])
    engine2 = KeywordEngine(corpus, ngrams=[1])

    scores1 = engine1.compute_tfidf()
    scores2 = engine2.compute_tfidf()

    assert [(s.term, s.tfidf_score) for s in scores1] == [
        (s.term, s.tfidf_score) for s in scores2
    ]


def test_compute_document_keywords(tmp_path):
    file = tmp_path / "doc.txt"
    file.write_text("alpha beta beta", encoding="utf-8")

    corpus = ingest_directory(tmp_path)
    engine = KeywordEngine(corpus, ngrams=[1])

    doc_id = corpus.documents[0].id

    results = engine.compute_document_keywords(doc_id)

    assert len(results) > 0
    assert all(r.term in ["alpha", "beta"] for r in results)