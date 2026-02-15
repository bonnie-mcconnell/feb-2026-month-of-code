import argparse
import json
import sys
from typing import Dict
from pathlib import Path

from .engine import run_pipeline
from .models import DailyAggregate
from .repository import Repository
from .ingest import ingest


def _serialize(
    data: Dict[str, Dict[str, DailyAggregate]]
) -> Dict:
    output = {}

    for ticker, date_map in data.items():
        output[ticker] = {}

        for date_str, aggregate in date_map.items():
            output[ticker][date_str] = aggregate.to_dict()

    return output


def cmd_ingest(args):
    repo = Repository()
    ingest(Path(args.input), repo)
    print(f"ingested file: {args.input}")


def cmd_run(args):
    repo = Repository()
    results = run_pipeline(args.input, repo=repo)
    print(json.dumps(_serialize(results), indent=2))


def cmd_summary(args):
    repo = Repository()
    # Fetch all daily aggregates from DB
    aggregates = repo.fetch_daily_aggregates()
    summary = {}
    for row in aggregates:
        ticker = row["ticker"]
        if ticker not in summary:
            summary[ticker] = {"total_volume": 0, "total_score": 0.0}
        summary[ticker]["total_volume"] += row["volume"]
        summary[ticker]["total_score"] += row["avg_score"] * row["volume"]

    # Compute overall_avg_score
    for ticker, data in summary.items():
        if data["total_volume"] > 0:
            data["overall_avg_score"] = data["total_score"] / data["total_volume"]
        del data["total_score"]

    print(json.dumps(summary, indent=2))


def cmd_report(args):
    repo = Repository()
    ticker = args.ticker.upper()
    aggregates = repo.fetch_daily_aggregates(ticker=ticker)

    if not aggregates:
        print(f"ticker not found: {ticker}")
        sys.exit(1)

    report = {}
    for row in aggregates:
        date = row["date"]
        report[date] = {
            "ticker": row["ticker"],
            "date": date,
            "avg_score": row["avg_score"],
            "volume": row["volume"],
            "positive_ratio": row["positive_ratio"],
            "negative_ratio": row["negative_ratio"],
        }

    print(json.dumps({ticker: report}, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="sentiment",
        description="rule-based stock news sentiment tracker",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ingest
    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("input", help="JSON or CSV file to ingest")
    ingest_parser.set_defaults(func=cmd_ingest)

    # run
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("input", help="JSON or CSV file to process")
    run_parser.set_defaults(func=cmd_run)

    # summary
    summary_parser = subparsers.add_parser("summary")
    summary_parser.set_defaults(func=cmd_summary)

    # report
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--ticker", required=True)
    report_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()