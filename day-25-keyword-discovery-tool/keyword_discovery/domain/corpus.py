from dataclasses import dataclass
from typing import List

from .document import Document


@dataclass(frozen=True)
class Corpus:
    documents: List[Document]

    @property
    def size(self) -> int:
        return len(self.documents)