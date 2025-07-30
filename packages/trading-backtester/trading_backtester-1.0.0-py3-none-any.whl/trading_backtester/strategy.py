from datetime import datetime
from typing import List, Sequence

from .account import Account
from .data import CandlestickPhase, Data
from .indicator import Indicator
from .market import Market
from .order import Order
from .position import Position


class Strategy:
    """Base class for trading strategies.

    Should be subclassed by the user to implement specific trading strategies.
    """

    def __init__(self):
        self.__positions: List[Position]
        self.__candlesticks_to_skip = 0
        self.__account: Account
        self.__market: Market

    def collect_orders(
        self, candlestick_phase: CandlestickPhase, price: float, date_time: datetime
    ) -> List[Order]:
        """Collects the user's orders for the current candlestick (and its phase).

        This method is intended to be implemented by the user to define their own strategy's order logic.
        It should be overridden in subclasses to provide specific order logic.

        Args:
            candlestick_phase (CandlestickPhase): The current candlestick phase (open or close).
            price (float): The current price of the asset.
            date_time (datetime): The datetime of the current candlestick.

        Returns:
            List[Order]: A list of orders to be executed.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")

    def prepare_indicators(self, data: Data) -> None:
        for member_name in dir(self):
            member = getattr(self, member_name)
            if isinstance(member, Indicator):
                member.prepare_indicator(data)
                self.__candlesticks_to_skip = max(
                    self.__candlesticks_to_skip, member.candlesticks_to_skip()
                )

    @property
    def _market(self) -> Market:
        """Returns the market object.

        Provides the user with a way to check the current market's data.
        This includes the current (and past) price, volume, and other market data.
        """

        return self.__market

    @property
    def _positions(self) -> Sequence[Position]:
        """Returns the current positions.

        Provides the user with a way to check the current positions in the account.
        This includes all open positions.
        """

        assert self.__positions is not None, "Positions have not been set."
        return tuple(self.__positions)

    @property
    def _current_money(self) -> float:
        """Returns the current money in the account.

        Provieds the user with a way to check the current money in the account.
        This is the money available for trading.
        """

        assert self.__account is not None, "Account has not been set."
        return self.__account.current_money

    def candletsticks_to_skip(self) -> int:
        """Returns the number of candlesticks to skip.

        This is used to determine how many candlesticks should be skipped
        before the strategy can start trading.
        Many indicators require a certain number of candlesticks
        to be calculated before they can be used.

        Returns:
            int: The number of candlesticks to skip.
        """

        return self.__candlesticks_to_skip

    def set_positions(self, positions: List[Position]) -> None:
        """Sets reference to the positions' list."""

        self.__positions = positions

    def set_account(self, account: Account) -> None:
        """Sets reference to the account object."""

        self.__account = account

    def set_market(self, market: Market) -> None:
        """Sets reference to the market object."""

        self.__market = market
