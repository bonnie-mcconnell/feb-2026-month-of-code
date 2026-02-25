from pathlib import Path
from typing import List

from keyword_discovery.domain.document import Document
from keyword_discovery.domain.corpus import Corpus


class IngestionError(Exception):
    pass


def ingest_directory(input_path: str) -> Corpus:
    """
    Recursively ingest .txt files from directory.
    Files are processed in deterministic alphabetical order.
    """
    base_path = Path(input_path)

    if not base_path.exists():
        raise IngestionError(f"Input path does not exist: {input_path}")

    if not base_path.is_dir():
        raise IngestionError(f"Input path is not a directory: {input_path}")

    text_files = sorted(
        p for p in base_path.rglob("*.txt") if p.is_file()
    )

    if not text_files:
        raise IngestionError("No .txt files found in directory")

    documents: List[Document] = []

    for idx, file_path in enumerate(text_files, start=1):
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise IngestionError(f"Failed to decode file: {file_path}") from exc

        if not content.strip():
            raise IngestionError(f"Empty file detected: {file_path}")

        doc_id = f"doc_{idx:04d}"

        documents.append(
            Document(
                id=doc_id,
                path=str(file_path),
                content=content,
                tokens=[],
            )
        )

    return Corpus(documents=documents)