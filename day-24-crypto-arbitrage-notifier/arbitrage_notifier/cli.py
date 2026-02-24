import argparse
from pathlib import Path
from arbitrage_notifier.main import main

def cli():
    parser = argparse.ArgumentParser(description="Crypto Arbitrage Notifier")

    parser.add_argument(
        "--config", type=str, help="Path to config file"
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run the arbitrage check only once (useful for testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calculate spread but do not send alerts",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default="BTCUSDT",
        help="Override default trading symbol",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set log level",
    )

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None

    main(
        config_path=config_path,
        run_once=args.run_once,
        dry_run=args.dry_run,
        symbol=args.symbol,
        log_level=args.log_level,
    )

if __name__ == "__main__":
    cli()