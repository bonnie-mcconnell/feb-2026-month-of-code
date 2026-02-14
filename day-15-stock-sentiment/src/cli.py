import argparse
import json
import sys
from typing import Dict

from .engine import run_pipeline
from .models import DailyAggregate


def _serialize(
    data: Dict[str, Dict[str, DailyAggregate]]
) -> Dict:
    output = {}

    for ticker, date_map in data.items():
        output[ticker] = {}

        for date_str, aggregate in date_map.items():
            output[ticker][date_str] = aggregate.to_dict()

    return output


def cmd_run(args):
    results = run_pipeline(args.input)
    print(json.dumps(_serialize(results), indent=2))


def cmd_summary(args):
    results = run_pipeline(args.input)

    summary = {}

    for ticker, date_map in results.items():
        total_volume = 0
        total_score = 0.0

        for aggregate in date_map.values():
            total_volume += aggregate.volume
            total_score += aggregate.avg_score * aggregate.volume

        if total_volume == 0:
            continue

        summary[ticker] = {
            "total_volume": total_volume,
            "overall_avg_score": total_score / total_volume,
        }

    print(json.dumps(summary, indent=2))


def cmd_report(args):
    results = run_pipeline(args.input)

    ticker = args.ticker.upper()

    if ticker not in results:
        print(f"ticker not found: {ticker}")
        sys.exit(1)

    report = {
        ticker: {
            date: aggregate.to_dict()
            for date, aggregate in results[ticker].items()
        }
    }

    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="sentiment",
        description="rule-based stock news sentiment tracker",
    )

    subparsers = parser.add_subparsers(dest="command")

    # run
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("input")
    run_parser.set_defaults(func=cmd_run)

    # summary
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("input")
    summary_parser.set_defaults(func=cmd_summary)

    # report
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("input")
    report_parser.add_argument("--ticker", required=True)
    report_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
