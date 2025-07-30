from typing import List, Tuple

from .account import Account
from .commission import Commission
from .data import Data
from .order import CloseOrder, Order, OrderAction
from .position import Position, PositionType
from .spread import Spread
from .stats import Statistics
from .trade import CloseTrade, OpenTrade, Trade


class Broker:
    """Represents the broker that handles orders and positions.

    This class is used to manage the trading operations, including opening and closing positions,
    processing orders, and managing the account balance.
    """

    def __init__(
        self,
        data: Data,
        accout: Account,
        spread: Spread,
        commission: Commission,
        trades_log: List[Trade],
        statistics: Statistics,
    ):
        """Initializes a Broker object.

        Args:
            data (Data): The data object containing market data.
            accout (Account): The account object representing the user's account.
            spread (float): The spread value for the broker.
            commission (Optional[Commission]): The commission object representing the broker's fees.
            trades_log (List[Trade]): The list of trades made during the backtest, that will be filled.
            statistics (Statistics): The statistics object.
        """

        self.__data = data
        self.__account = accout
        self.__spread = spread
        self.__commission = commission
        self.__positions: List[Position] = []
        self.__limit_orders: List[Order] = []
        self.__trades_log = trades_log
        self.__statistics = statistics

    def get_positions(self) -> List[Position]:
        """Returns the list of positions held by the user.

        Returns:
            List[Position]: The list of positions held by the user.
        """

        return self.__positions

    def get_assets_value(self) -> float:
        """Returns the total value of the assets held by the user.

        Returns:
            float: The total value of the assets held by the user.
        """

        assets_value = 0.0
        for position in self.__positions:
            assets_value += position.calc_value(self.__data.get_current_price())

        return assets_value

    def get_assets_value_at_price(self, price: float) -> float:
        """Returns the total value of the assets held by the user at a given price.

        Args:
            price (float): The price at which to calculate the value of the assets.

        Args:
            price (float): The price at which to calculate the value of the assets.
        """

        assets_value = 0.0
        for position in self.__positions:
            assets_value += position.calc_value(price)

        return assets_value

    def process_new_orders(self, new_orders: List[Order]) -> None:
        """Processes new orders and executes them if possible.

        Args:
            new_orders (List[Order]): The list of new orders to process.
        """

        if new_orders == []:
            return

        price = self.__data.get_current_price()

        for order in new_orders:
            if order.limit_price is not None:
                self.__limit_orders.append(order)
                continue

            if order.action == OrderAction.CLOSE:
                adjusted_price = self.__adjust_close_price_by_spread(
                    price, order.position_type
                )
                self.__process_close_order(order, adjusted_price)
            elif order.action == OrderAction.OPEN:
                adjusted_price = self.__adjust_open_price_by_spread(
                    price, order.position_type
                )
                self.__process_open_order(order, adjusted_price)

    def process_stop_losses(self) -> None:
        """Processes stop loss orders and closes positions if necessary."""

        low_price = self.__data.get_current_low_price()
        high_price = self.__data.get_current_high_price()

        close_orders: List[Tuple[CloseOrder, float]] = []

        for position in self.__positions:
            if position.stop_loss is None:
                continue

            if not self.__check_stop_loss_price(
                position.stop_loss, low_price, high_price, position.position_type
            ):
                continue

            price = self.__get_stop_loss_order_price(
                position.stop_loss, low_price, high_price, position.position_type
            )

            order = CloseOrder(
                size=position.size,
                position_to_close=position,
            )

            close_orders.append((order, price))

        for order, price in close_orders:
            self.__process_close_order(order, price)

    def process_take_profits(self) -> None:
        """Processes take profit orders and closes positions if necessary."""

        low_price = self.__data.get_current_low_price()
        high_price = self.__data.get_current_high_price()

        close_orders: List[Tuple[CloseOrder, float]] = []

        for position in self.__positions:
            if position.take_profit is None:
                continue

            if not self.__check_take_profit_price(
                position.take_profit, low_price, high_price, position.position_type
            ):
                continue

            price = self.__get_take_profit_order_price(
                position.take_profit, low_price, high_price, position.position_type
            )
            order = CloseOrder(
                size=position.size,
                position_to_close=position,
            )

            close_orders.append((order, price))

        for order, price in close_orders:
            self.__process_close_order(order, price)

    def process_limit_orders(self) -> None:
        """Processes limit orders and executes them if possible."""

        price = self.__data.get_current_price()
        low_price = self.__data.get_current_low_price()
        high_price = self.__data.get_current_high_price()

        orders_to_remove: List[Order] = []

        for order in self.__limit_orders:
            assert order.limit_price is not None
            if order.action == OrderAction.OPEN:
                if not self.__check_limit_price(
                    order.limit_price, price, order.position_type
                ):
                    continue

                order_price = self.__get_limit_order_price(
                    order.limit_price, low_price, high_price, order.position_type
                )
                self.__process_open_order(order, order_price)
                orders_to_remove.append(order)

        for order in orders_to_remove:
            self.__limit_orders.remove(order)

    def __process_open_order(self, order: Order, price: float) -> None:
        money = order.size * price
        commission = self.__commission.calc_commission_value(price) * order.size
        total_cost = money + commission

        if not self.__account.has_enough_money(total_cost):
            return

        self.__positions.append(
            Position(
                order.position_type,
                price,
                self.__data.get_current_numpy_datetime(),
                order.size,
                order.stop_loss,
                order.take_profit,
            )
        )
        self.__account.update_money(-total_cost)
        self.__statistics.add_commission(commission)

        self.__trades_log.append(
            OpenTrade(
                order.position_type,
                self.__data.get_current_numpy_datetime(),
                price,
                order.size,
                market_order=(order.limit_price is None),
            )
        )

    def __process_close_order(self, order: Order, price: float) -> None:
        if order.position_to_close is not None:
            self.__process_close_order_specified_position(order, price)
        else:
            self.__process_close_order_fifo_positions(order, price)

    def __process_close_order_fifo_positions(self, order: Order, price: float) -> None:
        size_to_reduce_left = order.size
        positions_to_close: List[Position] = []

        for i, position in enumerate(self.__positions):
            if position.position_type != order.position_type:
                continue

            reduce_size = min(size_to_reduce_left, position.size)

            if reduce_size < position.size:

                self.__positions[i] = position.replace(size=position.size - reduce_size)
            else:
                positions_to_close.append(position)

            self.__account.update_money(
                self.__calc_money_from_close(position, price, reduce_size)
            )
            commission = self.__commission.calc_commission_value(price) * reduce_size
            self.__statistics.add_commission(commission)
            self.__account.update_money(-commission)

            size_to_reduce_left -= reduce_size

            self.__trades_log.append(
                CloseTrade(
                    order.position_type,
                    position.open_datetime,
                    position.open_price,
                    self.__data.get_current_numpy_datetime(),
                    price,
                    reduce_size,
                    market_order=(order.limit_price is None),
                )
            )

            if size_to_reduce_left == 0:
                break

        for position in positions_to_close:
            self.__positions.remove(position)

    def __process_close_order_specified_position(
        self, order: Order, price: float
    ) -> None:
        assert order.position_to_close is not None

        if order.size > order.position_to_close.size:
            raise ValueError(
                "if order.position_to_close is specified, order.size must be less than or equal to order.position_to_close.size"
            )

        self.__account.update_money(
            self.__calc_money_from_close(order.position_to_close, price, order.size)
        )
        self.__account.update_money(
            -self.__commission.calc_commission_value(price) * order.size
        )

        if order.size == order.position_to_close.size:
            self.__positions.remove(order.position_to_close)
        else:
            position_index = self.__positions.index(order.position_to_close)
            self.__positions[position_index] = order.position_to_close.replace(
                size=order.position_to_close.size - order.size
            )

        self.__trades_log.append(
            CloseTrade(
                order.position_type,
                order.position_to_close.open_datetime,
                order.position_to_close.open_price,
                self.__data.get_current_numpy_datetime(),
                price,
                order.size,
                market_order=(order.limit_price is None),
            )
        )

    def __adjust_open_price_by_spread(
        self, price: float, position_type: PositionType
    ) -> float:
        spread = self.__spread.calc_spread_value(price)
        return price + spread if position_type == PositionType.LONG else price - spread

    def __adjust_close_price_by_spread(
        self, price: float, position_type: PositionType
    ) -> float:
        spread = self.__spread.calc_spread_value(price)
        return price - spread if position_type == PositionType.LONG else price + spread

    def __calc_money_from_close(
        self, position: Position, current_price: float, size: int
    ) -> float:
        return (
            size * current_price
            if position.position_type == PositionType.LONG
            else size * (2 * position.open_price - current_price)
        )

    def __check_limit_price(
        self, limit_price: float, price: float, position_type: PositionType
    ) -> bool:
        price = self.__adjust_open_price_by_spread(price, position_type)
        return (
            limit_price >= price
            if position_type == PositionType.LONG
            else limit_price <= price
        )

    def __get_limit_order_price(
        self,
        limit_price: float,
        low_price: float,
        high_price: float,
        position_type: PositionType,
    ) -> float:
        return (
            min(high_price, limit_price)
            if position_type == PositionType.LONG
            else max(low_price, limit_price)
        )

    def __check_stop_loss_price(
        self,
        stop_loss_price: float,
        low_price: float,
        high_price: float,
        position_type: PositionType,
    ) -> bool:
        adjusted_low_price = self.__adjust_close_price_by_spread(
            low_price, position_type
        )
        adjusted_high_price = self.__adjust_close_price_by_spread(
            high_price, position_type
        )

        return (
            stop_loss_price >= adjusted_low_price
            if position_type == PositionType.LONG
            else stop_loss_price <= adjusted_high_price
        )

    def __get_stop_loss_order_price(
        self,
        stop_loss_price: float,
        low_price: float,
        high_price: float,
        position_type: PositionType,
    ) -> float:
        return (
            min(high_price, stop_loss_price)
            if position_type == PositionType.LONG
            else max(low_price, stop_loss_price)
        )

    def __check_take_profit_price(
        self,
        take_profit_price: float,
        low_price: float,
        high_price: float,
        position_type: PositionType,
    ) -> bool:
        adjusted_low_price = self.__adjust_close_price_by_spread(
            low_price, position_type
        )
        adjusted_high_price = self.__adjust_close_price_by_spread(
            high_price, position_type
        )

        return (
            take_profit_price <= adjusted_high_price
            if position_type == PositionType.LONG
            else take_profit_price >= adjusted_low_price
        )

    def __get_take_profit_order_price(
        self,
        take_profit_price: float,
        low_price: float,
        high_price: float,
        position_type: PositionType,
    ) -> float:
        return (
            max(low_price, take_profit_price)
            if position_type == PositionType.LONG
            else min(high_price, take_profit_price)
        )
