from enum import Enum
from typing import Optional

import numpy as np

from .position import PositionType


class TradeType(Enum):
    """Represents the type of trade."""

    OPEN = 1
    """Open trade."""
    CLOSE = 2
    """Close trade."""


class Trade:
    """Represents a completed trade.

    This class is used to store the information of a completed trade.
    It is used mainly for statistics and plotting.
    It is not  directly involved in the backtesting process.

    Attributes:
        trade_type (TradeType): The type of trade (open or close).
        position_type (PositionType): The type of position (long or short).
        open_datetime (np.datetime64): The datetime when the trade was opened.
        open_price (float): The price at which the trade was opened.
        open_size (Optional[float]): The size of the trade when opened. Optional for close trades..
        close_datetime (Optional[np.datetime64]): The datetime when the trade was closed. Optional for open trades.
        close_price (Optional[float]): The price at which the trade was closed. Optional for open trades.
        close_size (Optional[float]): The size of the trade when closed. Optional for open trades.
        market_order (bool): Indicates whether the trade was a market order or a limit order.
    """

    def __init__(
        self,
        trade_type: TradeType,
        position_type: PositionType,
        open_datetime: np.datetime64,
        open_price: float,
        open_size: Optional[float] = None,
        close_datetime: Optional[np.datetime64] = None,
        close_price: Optional[float] = None,
        close_size: Optional[float] = None,
        market_order: bool = False,
    ):
        """Initializes a Trade object.

        Args:
            trade_type (TradeType): The type of trade (open or close).
            position_type (PositionType): The type of position (long or short).
            open_datetime (np.datetime64): The datetime when the trade was opened.
            open_price (float): The price at which the trade was opened.
            open_size (Optional[float]): The size of the trade when opened. Optional for close trades.
            close_datetime (Optional[np.datetime64]): The datetime when the trade was closed. Optional for open trades.
            close_price (Optional[float]): The price at which the trade was closed. Optional for open trades.
            close_size (Optional[float]): The size of the trade when closed. Optional for open trades.
            market_order (bool): Indicates whether the trade was a market order or a limit order.
        """

        assert not (
            trade_type == TradeType.CLOSE
            and (close_price is None or close_size is None or close_datetime is None)
        ), "Close trades must have a close price and size and datetime."
        assert not (
            trade_type == TradeType.OPEN and open_size is None
        ), "Open trades must have an open size."

        self.trade_type = trade_type
        self.position_type = position_type
        self.open_datetime = open_datetime
        self.open_price = open_price
        self.open_size = open_size
        self.close_datetime = close_datetime
        self.close_price = close_price
        self.close_size = close_size
        self.market_order = market_order

    def calc_profit_loss(self) -> float:
        """Calculates the profit/loss of the completed trade.

        Returns:
            float: The profit/loss of the trade.
        """

        assert (
            self.trade_type == TradeType.CLOSE
        ), "Profit/loss can only be calculated for closed trades."
        assert (
            self.close_price is not None
        ), "Close price must be set for closed trades."
        assert self.close_size is not None, "Close size must be set for closed trades."

        profit_loss_per_unit = (
            (self.close_price - self.open_price)
            if self.position_type == PositionType.LONG
            else (self.open_price - self.close_price)
        )
        profit_loss = profit_loss_per_unit * self.close_size

        return profit_loss


class OpenTrade(Trade):
    def __init__(
        self,
        position_type: PositionType,
        open_datetime: np.datetime64,
        price: float,
        size: float,
        market_order: bool,
    ):
        """Initializes an OpenTrade object.
        Args:
            position_type (PositionType): The type of position (long or short).
            open_datetime (np.datetime64): The datetime when the trade was opened.
            price (float): The price at which the trade was opened.
            size (float): The size of the trade when opened.
            market_order (bool): Indicates whether the trade was a market order or a limit order.
        """

        super().__init__(
            trade_type=TradeType.OPEN,
            position_type=position_type,
            open_datetime=open_datetime,
            open_price=price,
            open_size=size,
            market_order=market_order,
        )


class CloseTrade(Trade):
    """Represents a closed trade.

    Provides a convenient way for users to create a close trade.
    """

    def __init__(
        self,
        position_type: PositionType,
        open_datetime: np.datetime64,
        open_price: float,
        close_datetime: np.datetime64,
        close_price: float,
        close_size: float,
        market_order: bool,
    ):
        """Initializes a CloseTrade object.

        Args:
            position_type (PositionType): The type of position (long or short).
            open_datetime (np.datetime64): The datetime when the trade was opened.
            open_price (float): The price at which the trade was opened.
            close_datetime (np.datetime64): The datetime when the trade was closed.
            close_price (float): The price at which the trade was closed.
            close_size (float): The size of the trade when closed.
            market_order (bool): Indicates whether the trade was a market order or a limit order.
        """
        super().__init__(
            trade_type=TradeType.CLOSE,
            position_type=position_type,
            open_datetime=open_datetime,
            open_price=open_price,
            close_datetime=close_datetime,
            close_price=close_price,
            close_size=close_size,
            market_order=market_order,
        )
