import argparse
import json
import sys
from typing import Dict
from pathlib import Path

from .engine import run_pipeline
from .models import DailyAggregate
from .repository import Repository
from .ingest import ingest
from .aggregator import Aggregator


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
    aggregates = repo.fetch_daily_aggregates()

    summary = {}

    for agg in aggregates:
        ticker = agg.ticker
        if ticker not in summary:
            summary[ticker] = {"total_volume": 0, "total_score": 0.0}

        summary[ticker]["total_volume"] += agg.volume
        summary[ticker]["total_score"] += agg.avg_score * agg.volume

    for ticker, data in summary.items():
        if data["total_volume"] > 0:
            data["overall_avg_score"] = (
                data["total_score"] / data["total_volume"]
            )
        del data["total_score"]

    print(json.dumps(summary, indent=2))


def cmd_report(args):
    repo = Repository()
    ticker = args.ticker.upper()

    aggregates = repo.fetch_daily_aggregates(ticker=ticker)

    if not aggregates:
        print(f"ticker not found: {ticker}")
        sys.exit(1)

    # Ensure chronological order
    aggregates.sort(key=lambda x: x.date)

    # Apply minimum volume filter
    min_volume = args.min_volume
    if min_volume > 0:
        aggregates = [a for a in aggregates if a.volume >= min_volume]

    if not aggregates:
        print(f"No data after applying min_volume={min_volume}")
        sys.exit(1)

    # Rolling average (3-day)
    rolling = Aggregator.compute_rolling_average(aggregates, window=3)

    # -------------------------------
    # Volume-weighted volatility
    # -------------------------------
    total_volume = sum(a.volume for a in aggregates)

    if total_volume > 0:
        mean = sum(a.avg_score * a.volume for a in aggregates) / total_volume

        variance = sum(
            a.volume * (a.avg_score - mean) ** 2
            for a in aggregates
        ) / total_volume

        volatility = variance ** 0.5
    else:
        mean = 0.0
        volatility = 0.0

    # -------------------------------
    # Sentiment momentum (raw signal)
    # -------------------------------
    momentum = 0.0
    if len(aggregates) > 1:
        momentum = aggregates[-1].avg_score - aggregates[-2].avg_score

    # -------------------------------
    # Z-score (last day vs weighted mean)
    # -------------------------------
    z_score = 0.0
    if volatility > 0:
        z_score = (aggregates[-1].avg_score - mean) / volatility

    # -------------------------------
    # Trend classification
    # -------------------------------
    if momentum > 0:
        trend = "improving"
    elif momentum < 0:
        trend = "deteriorating"
    else:
        trend = "flat"

    # -------------------------------
    # Volume spike detection
    # -------------------------------
    avg_volume = total_volume / len(aggregates)
    volume_spike = aggregates[-1].volume > 1.5 * avg_volume

    # -------------------------------
    # Build final report
    # -------------------------------
    report = {
        "ticker": ticker,
        "volatility": round(volatility, 4),
        "momentum": round(momentum, 4),
        "z_score": round(z_score, 4),
        "trend": trend,
        "volume_spike": volume_spike,
        "days": []
    }

    for agg, roll in zip(aggregates, rolling):
        report["days"].append({
            "date": agg.date,
            "avg_score": round(agg.avg_score, 4),
            "rolling_3": round(roll, 4),
            "volume": agg.volume,
            "positive_ratio": round(agg.positive_ratio, 4),
            "negative_ratio": round(agg.negative_ratio, 4),
        })

    print(json.dumps(report, indent=2))


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
    report_parser.add_argument(
        "--min-volume",
        type=int,
        default=0,
        help="minimum daily news volume filter"
    )
    report_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()