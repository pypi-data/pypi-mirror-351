from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .account import Account
from .data import Data
from .position import PositionType
from .trade import Trade, TradeType


class Statistics:
    """Class for calculating and returning backtest statistics.

    This class calculates various statistics related to the backtest,
    including the number of trades, final money, final asset value, final total equity,
    and key indicators such as maximum drawdown, beta, alpha, and the strategy's return.
    """

    @dataclass
    class __TradesCounters:
        total_open_trades: int = 0
        total_close_trades: int = 0
        total_open_long_trades: int = 0
        total_close_long_trades: int = 0
        total_open_short_trades: int = 0
        total_close_short_trades: int = 0

    def __init__(
        self,
        trades: List[Trade],
        equity_log: np.ndarray[Any, np.dtype[Any]],
        account: Account,
        benchmark: Optional[Data] = None,
    ):
        """Initializes the Statistics object.

        Should be used after the backtest is completed.

        Args:
            trades (List[Trade]): List of trades made during the backtest.
            equity_log (np.ndarray): Array containing the equity log of the backtest.
            account (Account): The account used for the backtest.
            benchmark (Optional[Data]): Optional benchmark data for calculating beta and alpha.
        """

        self.__account = account
        self.__trades = trades
        self.__equity_log = equity_log
        self.__benchmark = benchmark

        self.__total_commission = 0.0

    def add_commission(self, commission: float) -> None:
        """Adds the paid commission to the total commission.

        Args:
            commission (float): The commission paid for the trade.
        """

        self.__total_commission += commission

    def get_stats(self) -> Dict[str, Any]:
        """Calculates and returns various statistics related to the backtest.

        Returns:
            Dict[str, Any]: A dictionary containing various statistics related to the backtest.
        """

        peaks = np.maximum.accumulate(self.__equity_log)
        max_drowdown, max_drawdown_percentage = self.__calc_max_drawndown(peaks)
        max_drawdown_duration = self.__calc_max_drawdown_duration(peaks)
        beta = self.__calc_beta()
        trades_counters = self.__get_trades_counters()
        return_value = self.__equity_log[-1] - self.__equity_log[0]
        return_value_percentage = return_value / self.__equity_log[0] * 100
        profitable_trades_num = self.__calc_profitable_trades_number()
        profitable_trades_percentage = (
            profitable_trades_num / trades_counters.total_close_trades * 100
            if trades_counters.total_close_trades > 0
            else 0.0
        )
        peak_equity = self.__equity_log.max()

        return {
            "total_trades": len(self.__trades),
            "total_open_trades": trades_counters.total_open_trades,
            "total_close_trades": trades_counters.total_close_trades,
            "total_open_long_trades": trades_counters.total_open_long_trades,
            "total_close_long_trades": trades_counters.total_close_long_trades,
            "total_open_short_trades": trades_counters.total_open_short_trades,
            "total_close_short_trades": trades_counters.total_close_short_trades,
            "final_money": self.__account.current_money,
            "final_assets_value": self.__equity_log[-1] - self.__account.current_money,
            "final_total_equity": self.__equity_log[-1],
            "peak_equity": peak_equity,
            "return": return_value,
            "return_percentage": return_value_percentage,
            "max_drawdown": max_drowdown,
            "max_drawdown_percentage": max_drawdown_percentage,
            "max_drawdown_duration": max_drawdown_duration,
            "profitable_trades_num": profitable_trades_num,
            "profitable_trades_percentage": profitable_trades_percentage,
            "best_trade_return_percentage": self.__get_best_trade_return_percentage(),
            "worst_trade_return_percentage": self.__get_worst_trade_return_percentage(),
            "beta": beta,
            "alpha": self.__calc_alpha(beta),
            "buy_and_hold_return_percentage": self.__get_buy_and_hold_return_percentage(),
            "total_commission": self.__total_commission,
        }

    def __str__(self) -> str:
        """Returns a string representation of the statistics in a human-readable format.

        Returns:
            str: A string representation of the statistics.
        """
        stats = self.get_stats()
        return "\n".join(
            [
                "=== Statistics ===",
                f"Total trades: {stats['total_trades']}",
                f"Total open trades: {stats['total_open_trades']}",
                f"Total close trades: {stats['total_close_trades']}",
                f"Total open long trades: {stats['total_open_long_trades']}",
                f"Total close long trades: {stats['total_close_long_trades']}",
                f"Total open short trades: {stats['total_open_short_trades']}",
                f"Total close short trades: {stats['total_close_short_trades']}",
                f"Final money: {stats['final_money']:.2f}",
                f"Final total equity: {stats['final_total_equity']:.2f}",
                f"Return: {stats['return']:.2f} ({(stats['return_percentage']):.2f}%)",
                f"Max drawdown: {stats['max_drawdown']:.2f} ({stats['max_drawdown_percentage']:.2f}%)",
                f"Max drawdown duration: {stats['max_drawdown_duration']}",
                f"Winning trades: {stats['profitable_trades_num']} ({stats['profitable_trades_percentage']:.2f}%)",
                f"Best trade return: {stats['best_trade_return_percentage']:.2f}%",
                f"Worst trade return: {stats['worst_trade_return_percentage']:.2f}%",
                f"Beta: {stats['beta']:.2f}",
                f"Alpha: {stats['alpha']:.2f}",
                f"Buy and hold return: {stats['buy_and_hold_return_percentage']:.2f}%",
                f"Total commission paid: {stats['total_commission']:.2f}",
            ]
        )

    def __calc_max_drawndown(
        self, peaks: np.ndarray[Any, np.dtype[Any]]
    ) -> Tuple[float, float]:
        drawdowns = peaks - self.__equity_log
        max_drawdown = np.max(drawdowns)
        max_drawdown_index = np.argmax(drawdowns)
        max_drawdown_percentage = (max_drawdown / peaks[max_drawdown_index]) * 100

        return max_drawdown, max_drawdown_percentage

    def __calc_max_drawdown_duration(
        self, peaks: np.ndarray[Any, np.dtype[Any]]
    ) -> int:
        drawdowns_occurred = self.__equity_log < peaks

        longest_drawdown_duration = 0
        current_drawdown_duration = 0
        for is_drawdown in drawdowns_occurred:
            if is_drawdown:
                current_drawdown_duration += 1
            else:
                longest_drawdown_duration = max(
                    longest_drawdown_duration, current_drawdown_duration
                )
                current_drawdown_duration = 0
        longest_drawdown_duration = max(
            longest_drawdown_duration, current_drawdown_duration
        )
        return longest_drawdown_duration

    def __calc_beta(self) -> Optional[float]:
        if self.__benchmark is None:
            return None

        benchmark_data = np.insert(
            self.__benchmark.close, 0, self.__benchmark.open[0], axis=0
        )
        benchmark_returns = np.diff(benchmark_data) / benchmark_data[:-1]

        equity_returns = np.diff(self.__equity_log) / self.__equity_log[:-1]

        if len(benchmark_returns) < 2 or len(equity_returns) < 2:
            return None

        covariance = np.cov(equity_returns, benchmark_returns)[0, 1]
        market_variance = np.var(benchmark_returns, ddof=1)

        if market_variance == 0:
            return None

        return covariance / market_variance

    def __calc_alpha(
        self, beta: Optional[float], risk_free_rate: float = 0.0
    ) -> Optional[float]:
        if beta is None or self.__benchmark is None:
            return None

        equity_return = (
            self.__equity_log[-1] - self.__equity_log[0]
        ) / self.__equity_log[0]
        benchmark_return = (
            self.__benchmark.close[-1] - self.__benchmark.open[0]
        ) / self.__benchmark.open[0]

        return (
            equity_return - risk_free_rate - beta * (benchmark_return - risk_free_rate)
        )

    def __get_trades_counters(self) -> __TradesCounters:
        counters = self.__TradesCounters()
        for trade in self.__trades:
            if trade.trade_type == TradeType.OPEN:
                counters.total_open_trades += 1
                if trade.position_type == PositionType.LONG:
                    counters.total_open_long_trades += 1
                else:
                    counters.total_open_short_trades += 1
            else:
                counters.total_close_trades += 1
                if trade.position_type == PositionType.LONG:
                    counters.total_close_long_trades += 1
                else:
                    counters.total_close_short_trades += 1

        return counters

    def __calc_profitable_trades_number(self) -> int:
        """Calculates the number of winning trades.

        Returns:
            int: The number of winning trades.
        """

        winning_trades = 0
        for trade in self.__trades:
            if trade.trade_type != TradeType.CLOSE:
                continue

            if trade.position_type == PositionType.LONG:
                assert trade.close_price is not None
                if trade.close_price > trade.open_price:
                    winning_trades += 1
            elif trade.position_type == PositionType.SHORT:
                assert trade.close_price is not None
                if trade.close_price < trade.open_price:
                    winning_trades += 1

        return winning_trades

    def __get_best_trade_return_percentage(self) -> float:
        best_winning_trade_return_percentage = 0.0
        for trade in self.__trades:
            if trade.trade_type != TradeType.CLOSE:
                continue

            trade_return_percentage = 0.0
            if trade.position_type == PositionType.LONG:
                assert trade.close_price is not None
                trade_return_percentage = (
                    (trade.close_price - trade.open_price) / trade.open_price * 100
                )
            elif trade.position_type == PositionType.SHORT:
                assert trade.close_price is not None
                trade_return_percentage = (
                    (trade.open_price - trade.close_price) / trade.open_price * 100
                )

            best_winning_trade_return_percentage = max(
                best_winning_trade_return_percentage, trade_return_percentage
            )

        return best_winning_trade_return_percentage

    def __get_worst_trade_return_percentage(self) -> float:
        worst_losing_trade_return_percentage = 0.0
        for trade in self.__trades:
            if trade.trade_type != TradeType.CLOSE:
                continue

            trade_return_percentage = 0.0
            if trade.position_type == PositionType.LONG:
                assert trade.close_price is not None
                trade_return_percentage = (
                    (trade.close_price - trade.open_price) / trade.open_price * 100
                )
            elif trade.position_type == PositionType.SHORT:
                assert trade.close_price is not None
                trade_return_percentage = (
                    (trade.open_price - trade.close_price) / trade.open_price * 100
                )

            worst_losing_trade_return_percentage = min(
                worst_losing_trade_return_percentage, trade_return_percentage
            )

        return worst_losing_trade_return_percentage

    def __get_buy_and_hold_return_percentage(self) -> Optional[float]:
        if self.__benchmark is None:
            return 0.0

        return (
            (self.__benchmark.close[-1] - self.__benchmark.open[0])
            / self.__benchmark.open[0]
            * 100
        )
