from pydantic import BaseModel


class SpreadResponse(BaseModel):
    symbol: str
    buy_exchange: str
    sell_exchange: str
    spread_percent: float


class HealthResponse(BaseModel):
    status: str
    redis: str
    binance: str
    coinbase: str