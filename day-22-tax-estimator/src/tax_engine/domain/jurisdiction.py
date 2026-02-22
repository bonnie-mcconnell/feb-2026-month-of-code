from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List
from functools import lru_cache

from .money import Money
from .brackets import TaxBracket, TaxSchedule


_REQUIRED_KEYS = {
    "name",
    "currency",
    "scale",
    "rounding",
    "tax_brackets",
    "round_per_bracket",
}


class Jurisdiction:
    """
    Validated jurisdiction configuration.
    """

    def __init__(
        self,
        *,
        name: str,
        currency: str,
        scale: int,
        rounding: str,
        tax_schedule: TaxSchedule,
        standard_deduction: Money | None,
        self_employment_rate: Decimal | None,
        round_per_bracket: bool,
    ) -> None:

        self.name = name
        self.currency = currency
        self.scale = scale
        self.rounding = rounding
        self.tax_schedule = tax_schedule
        self.standard_deduction = standard_deduction
        self.self_employment_rate = self_employment_rate
        self.round_per_bracket = round_per_bracket

    # ------------------------------------------------

    @classmethod
    @lru_cache(maxsize=16)
    def load_from_file(cls, path: Path) -> "Jurisdiction":
        if not path.exists():
            raise FileNotFoundError(f"Jurisdiction file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return cls._from_dict(data)

    # ------------------------------------------------

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Jurisdiction":
        missing = _REQUIRED_KEYS - data.keys()
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")

        name = str(data["name"])
        currency = str(data["currency"])
        scale = int(data["scale"])
        rounding = str(data["rounding"])
        round_per_bracket = bool(data["round_per_bracket"])

        brackets = cls._parse_brackets(data["tax_brackets"])
        schedule = TaxSchedule(brackets)

        standard_deduction = None
        if "standard_deduction" in data:
            standard_deduction = Money.from_str(
                str(data["standard_deduction"]),
                scale=scale,
                rounding=rounding,
            )

        self_employment_rate = None
        if "self_employment_tax" in data:
            self_employment_rate = cls._to_decimal(data["self_employment_tax"])

            if not (Decimal("0") <= self_employment_rate <= Decimal("1")):
                raise ValueError("self_employment_tax must be between 0 and 1")

        return cls(
            name=name,
            currency=currency,
            scale=scale,
            rounding=rounding,
            tax_schedule=schedule,
            standard_deduction=standard_deduction,
            self_employment_rate=self_employment_rate,
            round_per_bracket=round_per_bracket,
        )

    # ------------------------------------------------

    @staticmethod
    def _parse_brackets(raw: List[Dict[str, Any]]) -> List[TaxBracket]:
        brackets: List[TaxBracket] = []

        for entry in raw:
            minimum = Jurisdiction._to_decimal(entry["min"])
            maximum = (
                Jurisdiction._to_decimal(entry["max"])
                if entry.get("max") is not None
                else None
            )
            rate = Jurisdiction._to_decimal(entry["rate"])

            brackets.append(
                TaxBracket(
                    minimum=minimum,
                    maximum=maximum,
                    rate=rate,
                )
            )

        return brackets

    # ------------------------------------------------

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        if isinstance(value, float):
            raise ValueError("Float values not allowed in configuration")

        try:
            return Decimal(str(value))
        except InvalidOperation as exc:
            raise ValueError(f"Invalid decimal value: {value}") from exc
