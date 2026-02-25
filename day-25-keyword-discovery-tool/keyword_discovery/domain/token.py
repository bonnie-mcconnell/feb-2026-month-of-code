from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    value: str
    ngram_size: int

# TODO: unused for now