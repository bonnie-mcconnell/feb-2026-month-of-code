import tempfile
from pathlib import Path

import pytest

from keyword_discovery.pipeline.ingestion import ingest_directory, IngestionError


def test_ingestion_orders_files_deterministically():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        (base / "b.txt").write_text("second", encoding="utf-8")
        (base / "a.txt").write_text("first", encoding="utf-8")

        corpus = ingest_directory(tmpdir)

        assert corpus.size == 2
        assert corpus.documents[0].id == "doc_0001"
        assert corpus.documents[1].id == "doc_0002"

        # alphabetical ordering enforced
        assert corpus.documents[0].path.endswith("a.txt")
        assert corpus.documents[1].path.endswith("b.txt")


def test_ingestion_rejects_non_directory():
    with pytest.raises(IngestionError):
        ingest_directory("non_existent_path")


def test_ingestion_rejects_empty_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / "a.txt").write_text("", encoding="utf-8")

        with pytest.raises(IngestionError):
            ingest_directory(tmpdir)