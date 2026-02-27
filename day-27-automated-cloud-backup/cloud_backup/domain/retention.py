from dataclasses import dataclass


@dataclass(frozen=True)
class RetentionPolicy:
    retain_last: int
    retain_days: int

    def validate(self) -> None:
        if self.retain_last < 0:
            raise ValueError("retain_last must be >= 0")
        if self.retain_days < 0:
            raise ValueError("retain_days must be >= 0")