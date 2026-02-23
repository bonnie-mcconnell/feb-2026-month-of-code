from decimal import Decimal
from typing import List, Optional, Dict
from domain.ticker import Ticker
from domain.money import Money
from domain.spread import Spread


def compute_best_spread(
    symbol: str,
    tickers: List[Ticker],
    fees: Dict[str, Decimal],
) -> Optional[Spread]:
    if len(tickers) < 2:
        return None

    lowest_ask_ticker = min(tickers, key=lambda t: t.ask.amount)
    highest_bid_ticker = max(tickers, key=lambda t: t.bid.amount)

    if lowest_ask_ticker.exchange == highest_bid_ticker.exchange:
        return None

    buy_fee = fees.get(lowest_ask_ticker.exchange, Decimal("0"))
    sell_fee = fees.get(highest_bid_ticker.exchange, Decimal("0"))

    buy_multiplier = Decimal("1") + (buy_fee / Decimal("100"))
    sell_multiplier = Decimal("1") - (sell_fee / Decimal("100"))

    effective_buy = lowest_ask_ticker.ask * buy_multiplier
    effective_sell = highest_bid_ticker.bid * sell_multiplier

    spread_absolute = effective_sell - effective_buy

    if spread_absolute.amount <= Decimal("0"):
        return None

    spread_percent = spread_absolute.amount / effective_buy.amount

    return Spread(
        symbol=symbol,
        buy_exchange=lowest_ask_ticker.exchange,
        sell_exchange=highest_bid_ticker.exchange,
        buy_price=effective_buy,
        sell_price=effective_sell,
        spread_absolute=spread_absolute,
        spread_percent=spread_percent,
    )