from keyword_discovery.domain.document import Document
from keyword_discovery.domain.corpus import Corpus
from keyword_discovery.services.keyword_engine import KeywordEngine


def test_idf_single_document():
    doc = Document(
        id="doc_0001",
        path="d.txt",
        content="alpha beta",
        tokens=[]
    )

    corpus = Corpus([doc])
    engine = KeywordEngine(corpus, ngrams=[1])

    idf = engine.compute_idf()

    assert idf["alpha"] < 0
    assert idf["beta"] < 0


def test_rare_term_has_higher_score():
    doc1 = Document(
        id="doc_0001",
        path="d1.txt",
        content="common common rare",
        tokens=[]
    )

    doc2 = Document(
        id="doc_0002",
        path="d2.txt",
        content="common",
        tokens=[]
    )

    corpus = Corpus([doc1, doc2])
    engine = KeywordEngine(corpus, ngrams=[1])

    scores = engine.compute_tfidf()

    rare_score = next(s for s in scores if s.term == "rare")
    common_score = next(s for s in scores if s.term == "common")

    assert rare_score.tfidf_score > common_score.tfidf_score


def test_deterministic_sorting_tie_break():
    doc = Document(
        id="doc_0001",
        path="d.txt",
        content="a b",
        tokens=[]
    )

    corpus = Corpus([doc])
    engine = KeywordEngine(corpus, ngrams=[1])

    scores = engine.compute_tfidf()

    assert scores[0].term < scores[1].term


def test_long_tail_filtering():
    doc = Document(
        id="doc_0001",
        path="d.txt",
        content="deep learning deep learning",
        tokens=[]
    )

    corpus = Corpus([doc])
    engine = KeywordEngine(corpus, ngrams=[2])

    scores = engine.compute_tfidf()

    long_tail = engine.extract_long_tail(
        scores,
        min_doc_frequency=1,
        max_doc_frequency=1,
        min_score=-10.0,
        require_multiword=True,
    )

    assert all(k.ngram_size >= 2 for k in long_tail)


def test_phrase_subsumption():
    doc = Document(
        id="1",
        path="x",
        content="machine learning machine learning",
        tokens=[],
    )

    corpus = Corpus([doc])
    engine = KeywordEngine(corpus, ngrams=[1, 2])

    scores = engine.compute_scores()
    filtered = engine.suppress_subsumed(scores)
    
    terms = [s.term for s in filtered]

    assert not ("learning" in terms and "machine learning" in terms)


def test_scoring_mode_switch():
    doc = Document(id="1", path="x", content="alpha beta beta", tokens=[])
    corpus = Corpus([doc])

    engine = KeywordEngine(corpus, ngrams=[1], scoring="bm25")
    scores = engine.compute_scores()

    assert len(scores) > 0


def test_suppression_flag_in_engine():
    doc = Document(
        id="1",
        path="x",
        content="machine learning machine learning",
        tokens=[]
    )

    corpus = Corpus([doc])
    engine = KeywordEngine(
        corpus,
        ngrams=[1, 2],
        suppress_subterms=True,
    )

    scores = engine.compute_scores()
    terms = [s.term for s in scores]

    assert not ("learning" in terms and "machine learning" in terms)


def test_compute_document_keywords():
    doc1 = Document(id="1", path="x", content="alpha beta", tokens=[])
    doc2 = Document(id="2", path="y", content="gamma delta", tokens=[])

    corpus = Corpus([doc1, doc2])
    engine = KeywordEngine(corpus, ngrams=[1])

    keywords = engine.compute_document_keywords("1")
    terms = [k.term for k in keywords]

    assert "alpha" in terms
    assert "gamma" not in terms