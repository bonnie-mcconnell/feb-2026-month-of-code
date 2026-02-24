from abc import ABC, abstractmethod
from domain.ticker import Ticker


class BaseExchangeClient(ABC):

    @abstractmethod
    def get_ticker(self, symbol: str) -> Ticker:
        """Fetch current ticker for a trading pair."""
        pass