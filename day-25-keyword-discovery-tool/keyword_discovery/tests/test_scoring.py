from keyword_discovery.domain.document import Document
from keyword_discovery.domain.corpus import Corpus
from keyword_discovery.pipeline.index_builder import build_index
from keyword_discovery.services.keyword_engine import KeywordEngine


def test_idf_single_document():
    doc = Document(
        id="doc_0001",
        path="d.txt",
        content="",
        tokens=["alpha", "beta"]
    )

    corpus = Corpus([doc])
    index = build_index(corpus)
    engine = KeywordEngine(index)

    idf = engine.compute_idf()

    assert idf["alpha"] < 0
    assert idf["beta"] < 0


def test_rare_term_has_higher_score():
    doc1 = Document(
        id="doc_0001",
        path="d1.txt",
        content="",
        tokens=["common", "common", "rare"]
    )

    doc2 = Document(
        id="doc_0002",
        path="d2.txt",
        content="",
        tokens=["common"]
    )

    corpus = Corpus([doc1, doc2])
    index = build_index(corpus)
    engine = KeywordEngine(index)

    scores = engine.compute_tfidf()

    rare_score = next(s for s in scores if s.term == "rare")
    common_score = next(s for s in scores if s.term == "common")

    assert rare_score.tfidf_score > common_score.tfidf_score


def test_deterministic_sorting_tie_break():
    doc = Document(
        id="doc_0001",
        path="d.txt",
        content="",
        tokens=["a", "b"]
    )

    corpus = Corpus([doc])
    index = build_index(corpus)
    engine = KeywordEngine(index)

    scores = engine.compute_tfidf()

    # If equal score, alphabetical ordering
    assert scores[0].term < scores[1].term


def test_long_tail_filtering():
    doc = Document(
        id="doc_0001",
        path="d.txt",
        content="",
        tokens=["deep", "learning", "deep learning"]
    )

    corpus = Corpus([doc])
    index = build_index(corpus)
    engine = KeywordEngine(index)

    scores = engine.compute_tfidf()

    long_tail = engine.extract_long_tail(
        scores,
        min_doc_frequency=1,
        max_doc_frequency=1,
        min_score=-10.0,
        require_multiword=True,
    )

    assert all(k.ngram_size >= 2 for k in long_tail)