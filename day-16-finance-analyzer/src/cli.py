import argparse
import json
import sys
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .engine import FinanceEngine


DEFAULT_CONFIG_PATH = Path("config/categories.json")


def _serialize(obj: Any) -> Any:
    """
    Recursively serialize domain objects into JSON-safe primitives.
    """
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_serialize(v) for v in obj]

    if isinstance(obj, Decimal):
        return str(obj)

    if isinstance(obj, (date, datetime)):
        return obj.isoformat()

    return obj


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="finance",
        description="Deterministic personal finance analyzer",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("transactions")

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("transactions")

    anomalies_parser = subparsers.add_parser("anomalies")
    anomalies_parser.add_argument("transactions")

    args = parser.parse_args()

    engine = FinanceEngine(DEFAULT_CONFIG_PATH)
    result = engine.analyze(args.transactions)

    if args.command == "analyze":
        output = asdict(result)
    elif args.command == "report":
        output = asdict(result.report)
    elif args.command == "anomalies":
        output = [asdict(a) for a in result.anomalies]
    else:
        parser.error("Unknown command")

    print(json.dumps(_serialize(output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
