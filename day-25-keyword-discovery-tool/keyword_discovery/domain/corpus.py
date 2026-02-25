from dataclasses import dataclass
from typing import List

from .document import Document


@dataclass(frozen=True)
class Corpus:
    """
    Collection of documents forming the analysis corpus.
    """
    documents: List[Document]

    @property
    def size(self) -> int:
        return len(self.documents)