import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .engine import FinanceEngine


DEFAULT_CONFIG_PATH = Path("config/categories.json")


def _serialize(obj: Any) -> Any:
    """
    Convert Decimals to string for JSON serialization.
    """
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(v) for v in obj]
    if hasattr(obj, "quantize"):  # crude Decimal check
        return str(obj)
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

    print(json.dumps(_serialize(output), indent=2))


if __name__ == "__main__":
    main()
