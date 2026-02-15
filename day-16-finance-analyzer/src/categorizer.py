import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .models import Transaction


@dataclass
class CategoryRule:
    category: str
    keywords: List[str]


class Categorizer:
    def __init__(self, rules: List[CategoryRule], default_category: str):
        self.rules = rules
        self.default_category = default_category

    @classmethod
    def from_json(cls, path: str | Path) -> "Categorizer":
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Rules file not found: {path}")

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        default_category = data.get("default_category", "Uncategorized")

        rules_data = data.get("rules", [])
        rules: List[CategoryRule] = []

        for entry in rules_data:
            category = entry.get("category")
            keywords = entry.get("keywords", [])

            if not category or not isinstance(keywords, list):
                raise ValueError("Invalid rule entry in categories config")

            rules.append(
                CategoryRule(
                    category=category,
                    keywords=[k.lower() for k in keywords],
                )
            )

        return cls(rules=rules, default_category=default_category)

    def categorize(self, transactions: List[Transaction]) -> None:
        for tx in transactions:
            # Only categorize expenses
            if not tx.is_expense:
                continue

            description = tx.description.lower()

            matched = False

            for rule in self.rules:
                for keyword in rule.keywords:
                    if keyword in description:
                        tx.category = rule.category
                        matched = True
                        break

                if matched:
                    break

            if not matched:
                tx.category = self.default_category
