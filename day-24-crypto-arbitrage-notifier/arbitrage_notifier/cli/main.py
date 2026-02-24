import argparse
from pathlib import Path

from arbitrage_notifier.main import main


def cli():
    parser = argparse.ArgumentParser(
        description="Crypto Arbitrage Notifier"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to config file",
    )

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None

    main(config_path=config_path)


if __name__ == "__main__":
    cli()