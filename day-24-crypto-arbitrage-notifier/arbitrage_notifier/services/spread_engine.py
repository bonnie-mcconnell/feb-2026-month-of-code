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

    best_spread: Optional[Spread] = None

    for buy_ticker in tickers:
        for sell_ticker in tickers:

            if buy_ticker.exchange == sell_ticker.exchange:
                continue

            buy_fee = fees.get(buy_ticker.exchange, Decimal("0"))
            sell_fee = fees.get(sell_ticker.exchange, Decimal("0"))

            buy_multiplier = Decimal("1") + (buy_fee / Decimal("100"))
            sell_multiplier = Decimal("1") - (sell_fee / Decimal("100"))

            effective_buy = buy_ticker.ask * buy_multiplier
            effective_sell = sell_ticker.bid * sell_multiplier

            spread_absolute = effective_sell - effective_buy

            if spread_absolute.amount <= Decimal("0"):
                continue

            spread_percent = spread_absolute.amount / effective_buy.amount

            candidate = Spread(
                symbol=symbol,
                buy_exchange=buy_ticker.exchange,
                sell_exchange=sell_ticker.exchange,
                buy_price=effective_buy,
                sell_price=effective_sell,
                spread_absolute=spread_absolute,
                spread_percent=spread_percent,
            )

            if best_spread is None or candidate.spread_absolute > best_spread.spread_absolute:
                best_spread = candidate

    return best_spread