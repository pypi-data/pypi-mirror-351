from typing import List, Optional, Type

import numpy as np

from .account import Account
from .broker import Broker
from .commission import Commission, CommissionType
from .data import CandlestickPhase, Data
from .market import Market
from .plotting import Plotting
from .spread import Spread, SpreadType
from .stats import Statistics
from .strategy import Strategy
from .trade import Trade


class Backtester:
    """Main class for the backtester.

    This class is responsible for running the backtest and collecting statistics.
    """

    def __init__(
        self,
        data: Data,
        strategy: Type[Strategy],
        money: float = 1000.0,
        spread: Optional[Spread] = None,
        commission: Optional[Commission] = None,
        benchmark: Optional[Data] = None,
    ):
        """Initializes a Backtester object.

        Args:
            data (Data): The data object containing market data.
                strategy (Type[Strategy]): The trading strategy to be tested.
            User should pass the type of the strategy class, not an instance.
            money (float): The initial amount of money for the account. Default is 1000.0.
            spread (Optional[Spread]): The spread object.
            commission (Optional[Commission]): The commission object.
            benchmark (Optional[Data]): Optional benchmark data for comparison (for example for beta, alpha indicators).
        """

        self.__data = data
        self.__account = Account(initial_money=money)
        if commission is None:
            commission = Commission(CommissionType.FIXED, 0.0)
        if spread is None:
            spread = Spread(SpreadType.FIXED, 0.0)
        self.__equity_log = np.zeros(len(self.__data) + 1, dtype=float)
        self.__equity_log[0] = money
        self.__trades_log: List[Trade] = []
        self.__statistics = Statistics(
            trades=self.__trades_log,
            equity_log=self.__equity_log,
            account=self.__account,
            benchmark=benchmark,
        )
        self.__broker = Broker(
            self.__data,
            self.__account,
            spread,
            commission,
            self.__trades_log,
            self.__statistics,
        )

        self.__is_bankruptcy = False

        self.__strategy = strategy()
        self.__strategy.set_account(self.__account)
        self.__strategy.set_positions(self.__broker.get_positions())
        self.__strategy.set_market(Market(self.__data))
        self.__strategy.prepare_indicators(self.__data)

    def run(self) -> None:
        """Runs the backtest.

        This method executes the trading strategy.
        """

        for i in range(self.__strategy.candletsticks_to_skip()):
            self.__equity_log[i + 1] = self.__equity_log[0]
            self.__data.increment_data_index()

        for i in range(self.__strategy.candletsticks_to_skip(), len(self.__data)):
            self.__process_candlestick_phase(CandlestickPhase.OPEN)

            if self.__is_bankruptcy:
                self.process_bankruptcy(i)
                break

            self.__process_candlestick_phase(CandlestickPhase.CLOSE)

            if self.__is_bankruptcy:
                self.process_bankruptcy(i)
                break

            self.__equity_log[i + 1] = (
                self.__account.current_money + self.__broker.get_assets_value()
            )

            self.__data.increment_data_index()

    def get_statistics(self) -> Statistics:
        """Returns the statistics of the backtest.

        Should be called after the backtest is run.

        Returns:
            Statistics: The statistics object containing the results of the backtest.
        """

        return self.__statistics

    def get_plotting(self) -> Plotting:
        """Returns the plotting object for visualization of the backtest results.

        Should be called after the backtest is run.

        Returns:
            Plotting: The plotting object for visualization.
        """

        return Plotting(self.__data, self.__trades_log, self.__equity_log)

    def __check_bankruptcy(self) -> bool:
        if (self.__account.current_money + self.__broker.get_assets_value()) <= 0.0:
            return True

        if self.__data.get_candlestick_phase() == CandlestickPhase.CLOSE:
            if (
                self.__account.current_money
                + self.__broker.get_assets_value_at_price(
                    self.__data.get_current_low_price()
                )
            ) <= 0.0:
                return True

            if (
                self.__account.current_money
                + self.__broker.get_assets_value_at_price(
                    self.__data.get_current_high_price()
                )
            ) <= 0.0:
                return True

        return False

    def process_bankruptcy(self, data_index: int) -> None:
        self.__equity_log[data_index + 1 :] = 0.0

    def __process_candlestick_phase(self, phase: CandlestickPhase) -> None:
        self.__data.set_candlestick_phase(phase)

        if self.__check_bankruptcy():
            self.__is_bankruptcy = True
            return

        self.__broker.process_stop_losses()
        self.__broker.process_take_profits()

        new_orders = self.__strategy.collect_orders(
            phase,
            self.__data.get_current_price(),
            self.__data.get_current_datatime(),
        )
        self.__broker.process_new_orders(new_orders=new_orders)
        self.__broker.process_limit_orders()
