import pytest

from keyword_discovery.domain.document import Document
from keyword_discovery.domain.corpus import Corpus
from keyword_discovery.pipeline.index_builder import build_index


def test_tf_computation():
    doc = Document(
        id="doc_0001",
        path="test.txt",
        content="",
        tokens=["a", "b", "a"]
    )

    corpus = Corpus(documents=[doc])
    index = build_index(corpus)

    tf = index.term_frequencies["doc_0001"]

    assert tf["a"] == 2 / 3
    assert tf["b"] == 1 / 3


def test_inverted_index():
    doc1 = Document(
        id="doc_0001",
        path="d1.txt",
        content="",
        tokens=["alpha", "beta"]
    )

    doc2 = Document(
        id="doc_0002",
        path="d2.txt",
        content="",
        tokens=["beta", "gamma"]
    )

    corpus = Corpus(documents=[doc1, doc2])
    index = build_index(corpus)

    assert index.inverted_index["beta"] == {"doc_0001", "doc_0002"}
    assert index.inverted_index["alpha"] == {"doc_0001"}


def test_reject_document_without_tokens():
    doc = Document(
        id="doc_0001",
        path="empty.txt",
        content="",
        tokens=[]
    )

    corpus = Corpus(documents=[doc])

    with pytest.raises(ValueError):
        build_index(corpus)


