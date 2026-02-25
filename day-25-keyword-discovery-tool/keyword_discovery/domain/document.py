from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Document:
    id: str
    path: str
    content: str
    tokens: List[str]