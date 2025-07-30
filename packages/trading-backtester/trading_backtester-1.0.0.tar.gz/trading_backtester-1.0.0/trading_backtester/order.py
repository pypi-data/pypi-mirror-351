from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from .position import Position, PositionType


class OrderAction(Enum):
    """Represents the action when processing an order will be taken."""

    OPEN = 1
    """Order to open a position."""
    CLOSE = 2
    """Order to close a position."""


class Order(ABC):
    """Base class for orders.

    Represents an order in the market.
    """

    @abstractmethod
    def __init__(
        self,
        size: int,
        action: OrderAction,
        position_type: PositionType,
        position_to_close: Optional[Position] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        limit_price: Optional[float] = None,
    ):
        """Initializes an Order object.
        Args:
            size (int): The size of the order.
            action (OrderAction): The action to be taken (open or close position).
            position_type (PositionType): The type of position (long or short).
            position_to_close (Optional[Position]): The position to close. Optional, if not provided, the position will be closed in FIFO order.
            stop_loss (Optional[float]): The stop loss price. Optional.
            take_profit (Optional[float]): The take profit price. Optional.
            limit_price (Optional[float]): The limit price for the order. Optional, if not provided, the order will be a market order.
        """

        self.__size = size
        self.__position_type = position_type
        self.__action = action
        self.__position_to_close = position_to_close
        self.__stop_loss = stop_loss
        self.__take_profit = take_profit
        self.__limit_price = limit_price

    @property
    def size(self) -> int:
        """Returns the size of the asset to be traded.

        Returns:
            int: The size of the order.
        """

        return self.__size

    @property
    def position_type(self) -> PositionType:
        """Returns the type of the asset to be traded.

        Returns:
            PositionType: The type of position (long or short).
        """

        return self.__position_type

    @property
    def action(self) -> OrderAction:
        """Returns the action to be taken (open or close position).

        Returns:
            OrderAction: The action to be taken (open or close position).
        """

        return self.__action

    @property
    def position_to_close(self) -> Optional[Position]:
        """Returns the position to close.

        Returns:
            Optional[Position]: The position to close. Optional.
        """
        return self.__position_to_close

    @property
    def stop_loss(self) -> Optional[float]:
        """Returns the stop loss price.

        Returns:
            Optional[float]: The stop loss price. Optional.
        """

        return self.__stop_loss

    @property
    def take_profit(self) -> Optional[float]:
        """Returns the take profit price.

        Returns:
            Optional[float]: The take profit price. Optional.
        """

        return self.__take_profit

    @property
    def limit_price(self) -> Optional[float]:
        """Returns the limit price for the order.

        Returns:
            Optional[float]: The limit price for the order. Optional.
        """

        return self.__limit_price


class OpenOrder(Order):
    def __init__(
        self,
        size: int,
        position_type: PositionType,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        limit_price: Optional[float] = None,
    ):
        """Initializes an OpenOrder object.

        Args:
            size (int): The size of the order.
            position_type (PositionType): The type of position (long or short).
            stop_loss (Optional[float]): The stop loss price. Optional.
            take_profit (Optional[float]): The take profit price. Optional.
            limit_price (Optional[float]): The limit price for the order. Optional, if not provided, the order will be a market order.
        """

        super().__init__(
            size=size,
            action=OrderAction.OPEN,
            position_type=position_type,
            stop_loss=stop_loss,
            take_profit=take_profit,
            limit_price=limit_price,
        )


class CloseOrder(Order):
    def __init__(
        self,
        size: int,
        position_type: Optional[PositionType] = None,
        position_to_close: Optional[Position] = None,
    ):
        """Initializes a CloseOrder object.

        Args:
            size (int): The size of the order.
            position_type (Optional[PositionType]): The type of position (long or short). Optional, if not provided, the position will be closed in FIFO order.
            position_to_close (Optional[Position]): The position to close. Optional, if not provided, the position will be closed in FIFO order.
        """

        if position_to_close is None and position_type is None:
            raise ValueError(
                "Either position_to_close or position_type must be provided."
            )

        if position_to_close is not None:
            position_type = position_to_close.position_type

        assert position_type is not None

        super().__init__(
            size=size,
            action=OrderAction.CLOSE,
            position_type=position_type,
            position_to_close=position_to_close,
        )
