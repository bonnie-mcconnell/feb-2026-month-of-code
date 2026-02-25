from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Document:
    """
    Immutable representation of a corpus document.
    Tokens are populated after normalization stage.
    """
    id: str
    path: str
    content: str
    tokens: List[str]