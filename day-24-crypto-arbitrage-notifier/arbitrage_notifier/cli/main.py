import argparse
from pathlib import Path

from arbitrage_notifier.main import main


def cli():
    parser = argparse.ArgumentParser(description="Crypto Arbitrage Notifier")

    parser.add_argument(
        "--config",
        type=str,
        help="Path to config file",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single iteration and exit",
    )

    parser.add_argument(
        "--json-logs",
        action="store_true",
        help="Enable JSON structured logging",
    )

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None

    main(
        config_path=config_path,
        once=args.once,
        json_logs=args.json_logs,
    )


if __name__ == "__main__":
    cli()