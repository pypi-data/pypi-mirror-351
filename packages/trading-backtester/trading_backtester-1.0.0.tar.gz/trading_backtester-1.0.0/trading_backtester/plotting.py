from typing import Any, Dict, List, Optional

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Annotation
from matplotlib.ticker import FuncFormatter, MaxNLocator

from .data import Data
from .position import PositionType
from .trade import Trade, TradeType


class Plotting:
    """Class for plotting the backtest results.

    Used to visualize the backtest results, including equity, closed traes, and candlestick charts.
    """

    __POSITIVE_BAR_COLOR = "green"
    __NEGATIVE_BAR_COLOR = "red"

    __CANDLESTICK_BAR_WIDTH = 0.75
    __VOLUME_BAR_WIDTH = 0.95
    __SPACE_BETWEEN_PLOTS = 0.2

    __EQUITY_PLOT_RATIO = 1
    __VOLUME_PLOT_RATIO = 1
    __PRICE_PLOT_RATIO = 3

    __EQUITY_DRAWDOWN_THRESHOLD = 0.02

    __LONG_TRADE_MARKER = "^"
    __SHORT_TRADE_MARKER = "v"

    def __init__(
        self,
        data: Data,
        trades: List[Trade],
        equity_log: np.ndarray[Any, np.dtype[Any]],
    ):
        """Initializes the Plotting object.

        Should be used after the backtest is completed.

        Args:
            data (Data): The data used for the backtest.
            trades (List[Trade]): List of trades made during the backtest.
            equity_log (np.ndarray): Array containing the equity log of the backtest.
        """

        self.__figure: Optional[Figure] = None

        self.__data = data
        self.__trades = trades
        self.__equity_log = equity_log

        self.__should_draw_candlesticks: bool
        self.__should_draw_volume: bool
        self.__should_draw_equity: bool
        self.__should_draw_trades: bool
        self.__should_draw_annotations: bool
        self.config_drawing()

    def config_drawing(
        self,
        draw_candlesticks: bool = True,
        draw_volume: bool = True,
        draw_equity: bool = True,
        draw_trades: bool = True,
        annotations: bool = True,
    ) -> None:
        """Configures the drawing options for the plots.

        Args:
            draw_candlesticks (bool): Whether to draw candlestick charts. Default is True.
            draw_volume (bool): Whether to draw volume charts. Default is True.
            draw_equity (bool): Whether to draw equity charts. Default is True.
            draw_trades (bool): Whether to draw closed trades. Default is True.
            annotations (bool): Whether to show annotations on the plots. Default is True.
        """

        self.__should_draw_candlesticks = draw_candlesticks
        self.__should_draw_volume = draw_volume
        self.__should_draw_equity = draw_equity
        self.__should_draw_trades = draw_trades
        self.__should_draw_annotations = annotations

        self.__figure = None

    def get_figure(self) -> Figure:
        """Returns the figure object.

        This method returns the figure object, which can be used for further customization or saving by the user.

        Returns:
            Figure: The generated figure object.
        """

        self.__prepare_figure()
        assert self.__figure is not None
        return self.__figure

    def show_plot(self) -> None:
        """Displays the plot."""

        self.__prepare_figure()
        assert self.__figure is not None
        plt.show()

    def save_plot(self, file_path: str, **kwargs) -> None:
        """Saves the plot to a file.

        Args:
            file_path (str): The path to save the plot.
            **kwargs: Additional arguments to pass to the matplotlib savefig function.
        """

        self.__prepare_figure()
        assert self.__figure is not None
        self.__figure.savefig(file_path, **kwargs)

    def __prepare_figure(self) -> None:
        if self.__figure is not None:
            return

        num_of_plots = 0
        height_ratios: List[int] = []
        ax_equity_index = -1
        ax_price_index = -1
        ax_volume_index = -1

        if self.__should_draw_equity:
            ax_equity_index = num_of_plots
            num_of_plots += 1
            height_ratios.append(self.__EQUITY_PLOT_RATIO)

        if self.__should_draw_candlesticks or self.__should_draw_trades:
            ax_price_index = num_of_plots
            num_of_plots += 1
            height_ratios.append(self.__PRICE_PLOT_RATIO)

        if self.__should_draw_volume:
            ax_volume_index = num_of_plots
            num_of_plots += 1
            height_ratios.append(self.__VOLUME_PLOT_RATIO)

        if num_of_plots == 0:
            raise ValueError("No plots to draw. Please enable at least one plot.")
        if num_of_plots == 1:
            height_ratios = [1]

        fig, ax = plt.subplots(
            num_of_plots,
            1,
            sharex=True,
            gridspec_kw={
                "hspace": self.__SPACE_BETWEEN_PLOTS,
                "height_ratios": height_ratios,
            },
        )

        if num_of_plots == 1:
            ax = [ax]

        if self.__should_draw_candlesticks or self.__should_draw_trades:
            self.__draw_price_plot(ax[ax_price_index])

        if self.__should_draw_volume:
            self.__draw_volume_plot(ax[ax_volume_index])

        if self.__should_draw_equity:
            self.__draw_equity_plot(ax[ax_equity_index])

        dateformat = self.__get_date_format()
        xticklabels = [
            np.datetime64(dt)
            .astype("datetime64[s]")
            .astype(object)
            .strftime(dateformat)
            for dt in self.__data.datetime
        ]
        x_axis_values = np.arange(len(self.__data))

        last_axis = ax[-1]
        last_axis.set_xticks(x_axis_values)
        last_axis.set_xticklabels(xticklabels)
        last_axis.set_xlabel("Time")
        last_axis.xaxis.set_major_locator(
            MaxNLocator(integer=True, prune="both", nbins=10)
        )
        fig.autofmt_xdate()

        fig.text(
            0.5,
            0.5,
            "Trading-Backtester\n@madamskip1",
            fontsize=50,
            color="black",
            ha="center",
            va="center",
            alpha=0.1,
            rotation=30,
        )

        self.__figure = fig

    def __draw_price_plot(self, ax: Axes) -> None:
        ax.set_ylabel("Price")
        ax.grid(True, axis="y"),

        if self.__should_draw_candlesticks:
            self.__draw_candlesticks(ax)

        if self.__should_draw_trades:
            self.__draw_closed_trades(ax)

    def __draw_volume_plot(self, ax: Axes) -> None:
        ax.set_ylabel("Volume")
        ax.grid(True, axis="y")

        for x, data in enumerate(self.__data):
            color = self.__get_bar_color(data["open"], data["close"])
            ax.bar(
                x,
                data["volume"],
                width=self.__VOLUME_BAR_WIDTH,
                color=color,
                zorder=2,
            )

    def __draw_equity_plot(self, ax: Axes) -> None:
        ax.set_ylabel("Equity")

        ax_right = ax.twinx()
        ax_right.set_ylabel("Equity %")
        ax.grid(True, axis="y")

        ax.plot(self.__equity_log, zorder=11, color="blue")
        scatter = ax.scatter(
            np.arange(len(self.__equity_log)), self.__equity_log, s=10, alpha=0
        )

        percent_equity = self.__equity_log / self.__equity_log[0] * 100
        ax_right.set_ylim(
            percent_equity.min() - percent_equity.min() * 0.05,
            percent_equity.max() + percent_equity.max() * 0.05,
        )
        formatter = FuncFormatter(lambda y, _: f"{y:.1f}%")
        ax_right.yaxis.set_major_formatter(formatter)

        peaks = np.maximum.accumulate(self.__equity_log)
        drawdowns = self.__equity_log - peaks
        drawdowns_percentages = np.abs(drawdowns / peaks)

        self.__draw_equity_drawdown(ax, drawdowns_percentages)

        if self.__should_draw_annotations:
            equity_annotation = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(20, 20),
                textcoords="offset points",
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    alpha=0.95,
                ),
                zorder=20,
                arrowprops=dict(arrowstyle="->"),
            )

            equity_annotation.set_visible(False)

            def on_mouse_move(event: MouseEvent):
                if event.inaxes not in (ax, ax_right):
                    self.__hide_annotation_and_redraw_if_necessary(
                        equity_annotation, event
                    )
                    return

                cond, ind = scatter.contains(event)
                if not cond:
                    self.__hide_annotation_and_redraw_if_necessary(
                        equity_annotation, event
                    )
                    return

                idx = int(ind["ind"][0])
                pos = scatter.get_offsets()[idx]
                if (
                    np.array_equal(equity_annotation.xy, pos)
                    and equity_annotation.get_visible()
                ):
                    return

                equity_annotation.xy = pos
                value = self.__equity_log[idx]
                drawdown = drawdowns[idx]
                drawdown_percentage = drawdowns_percentages[idx] * 100
                equity_annotation.set_text(
                    f"Equity: {value:.2f}\nDrawdown: {drawdown:.2f} ({abs(drawdown_percentage):.2f}%)"
                )
                equity_annotation.set_visible(True)
                event.canvas.draw_idle()

            ax.figure.canvas.mpl_connect("motion_notify_event", on_mouse_move)

    def __draw_equity_drawdown(
        self, ax: Axes, drawdowns_percentages: np.ndarray
    ) -> None:
        in_drawdown = False
        last_peak = 0
        max_drawdown = 0.0
        for i, drawdown in enumerate(drawdowns_percentages):
            if drawdown == 0.0:
                if in_drawdown:
                    if max_drawdown >= self.__EQUITY_DRAWDOWN_THRESHOLD:
                        ax.axvspan(last_peak, i - 1, color="red", alpha=0.2, zorder=1)
                    in_drawdown = False
                    max_drawdown = 0.0

                last_peak = i
            else:
                in_drawdown = True
                max_drawdown = max(max_drawdown, drawdown)

        if in_drawdown and max_drawdown >= self.__EQUITY_DRAWDOWN_THRESHOLD:
            ax.axvspan(
                last_peak,
                len(drawdowns_percentages) - 1,
                color="red",
                alpha=0.2,
                zorder=1,
            )

    def __draw_candlesticks(self, ax: Axes) -> None:
        for x, data in enumerate(self.__data):
            candlestick_color = self.__get_bar_color(data["open"], data["close"])

            # Draw the high and low lines
            ax.plot(
                [x, x], [data["low"], data["high"]], color=candlestick_color, zorder=2
            )

            body_low = min(data["open"], data["close"])
            body_height = abs(data["close"] - data["open"])
            body_bottom_left = (x - self.__CANDLESTICK_BAR_WIDTH / 2, body_low)

            # Draw the body of the candlestick
            ax.add_patch(
                Rectangle(
                    body_bottom_left,
                    self.__CANDLESTICK_BAR_WIDTH,
                    body_height,
                    facecolor=candlestick_color,
                    zorder=3,
                )
            )

    def __draw_closed_trades(self, ax: Axes) -> None:
        datetime_to_x_axis: Dict[np.datetime64, int] = {
            dt: x for x, dt in enumerate(self.__data.datetime)
        }
        closed_trades: List[Trade] = [
            trade
            for trade in reversed(self.__trades)
            if trade.trade_type == TradeType.CLOSE
        ]

        closed_trades_markers: List[Line2D] = []
        trade_lines_x_start: List[int] = []
        trade_lines_x_end: List[int] = []
        trade_lines_y_start: List[float] = []
        trade_lines_y_end: List[float] = []

        for trade in closed_trades:
            assert trade.close_datetime is not None
            assert trade.close_price is not None

            x_start = datetime_to_x_axis[trade.open_datetime]
            y_start = trade.open_price
            x_end = datetime_to_x_axis[trade.close_datetime]
            y_end = trade.close_price

            trade_lines_x_start.append(x_start)
            trade_lines_x_end.append(x_end)
            trade_lines_y_start.append(y_start)
            trade_lines_y_end.append(y_end)

            closed_trade_marker = self.__draw_closed_trade_marker(
                ax,
                x_end,
                y_end,
                trade.position_type,
                trade.open_price,
                trade.close_price,
            )
            closed_trades_markers.append(closed_trade_marker)

        ax.plot(
            [trade_lines_x_start, trade_lines_x_end],
            [trade_lines_y_start, trade_lines_y_end],
            color="black",
            linewidth=2,
            linestyle="--",
            zorder=4,
        )

        ax.legend(handles=self.__prepare_closed_trade_legend(closed_trades), loc="best")

        if self.__should_draw_annotations:
            closed_trade_annotation = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(20, 20),
                textcoords="offset points",
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    alpha=0.95,
                ),
                zorder=20,
                arrowprops=dict(arrowstyle="->"),
            )
            closed_trade_annotation.set_visible(False)

            def on_mouse_move(event: MouseEvent):
                if event.inaxes is not ax:
                    self.__hide_annotation_and_redraw_if_necessary(
                        closed_trade_annotation, event
                    )
                    return

                for i, marker in enumerate(closed_trades_markers):
                    contains, _ = marker.contains(event)
                    if not contains:
                        continue

                    pos = (marker.get_xdata(), marker.get_ydata())
                    if (
                        np.array_equal(closed_trade_annotation.xy, pos)
                        and closed_trade_annotation.get_visible()
                    ):
                        return

                    closed_trade_annotation.xy = pos
                    close_trade = closed_trades[i]
                    closed_trade_annotation.set_text(
                        f"{"Long" if close_trade.position_type == PositionType.LONG else "Short"} Trade\n"
                        f"Open: {close_trade.open_price:.2f}\n"
                        f"Close: {close_trade.close_price:.2f}\n"
                        f"Size: {close_trade.close_size:.2f}\n"
                        f"Profit/Loss: {close_trade.calc_profit_loss():.2f}"
                    )
                    closed_trade_annotation.set_visible(True)
                    event.canvas.draw_idle()
                    return

                self.__hide_annotation_and_redraw_if_necessary(
                    closed_trade_annotation, event
                )

            ax.figure.canvas.mpl_connect("motion_notify_event", on_mouse_move)

    def __draw_closed_trade_marker(
        self,
        ax: Axes,
        x_end: int,
        y_end: float,
        position_type: PositionType,
        open_price: float,
        close_price: float,
    ) -> Line2D:
        if position_type == PositionType.LONG:
            marker = self.__LONG_TRADE_MARKER
            color = (
                self.__POSITIVE_BAR_COLOR
                if open_price < close_price
                else self.__NEGATIVE_BAR_COLOR
            )
        else:
            marker = self.__SHORT_TRADE_MARKER
            color = (
                self.__POSITIVE_BAR_COLOR
                if open_price > close_price
                else self.__NEGATIVE_BAR_COLOR
            )

        close_marker = ax.plot(
            x_end,
            y_end,
            marker=marker,
            color=color,
            zorder=5,
            markeredgecolor="black",
            markersize=10,
        )[0]

        return close_marker

    def __prepare_closed_trade_legend(self, closed_trades: List[Trade]) -> List[Line2D]:
        had_profitable_long_trade = False
        had_profitable_short_trade = False
        had_losing_long_trade = False
        had_losing_short_trade = False

        for trade in closed_trades:
            assert trade.close_datetime is not None
            assert trade.close_price is not None

            if trade.position_type == PositionType.LONG:
                if trade.calc_profit_loss() > 0:
                    had_profitable_long_trade = True
                else:
                    had_losing_long_trade = True
            else:
                if trade.calc_profit_loss() > 0:
                    had_profitable_short_trade = True
                else:
                    had_losing_short_trade = True

        legend_elements: List[Line2D] = []
        if had_profitable_long_trade:
            legend_elements.append(
                self.__prepare_dummy_closed_trade_legend_marker(
                    self.__LONG_TRADE_MARKER,
                    "Profitable closed Long Trade",
                    self.__POSITIVE_BAR_COLOR,
                )
            )
        if had_losing_long_trade:
            legend_elements.append(
                self.__prepare_dummy_closed_trade_legend_marker(
                    self.__LONG_TRADE_MARKER,
                    "Losing closed Long Trade",
                    self.__NEGATIVE_BAR_COLOR,
                )
            )
        if had_profitable_short_trade:
            legend_elements.append(
                self.__prepare_dummy_closed_trade_legend_marker(
                    self.__SHORT_TRADE_MARKER,
                    "Profitable closed Short Trade",
                    self.__POSITIVE_BAR_COLOR,
                )
            )
        if had_losing_short_trade:
            legend_elements.append(
                self.__prepare_dummy_closed_trade_legend_marker(
                    self.__SHORT_TRADE_MARKER,
                    "Losing closed Short Trade",
                    self.__NEGATIVE_BAR_COLOR,
                )
            )

        return legend_elements

    def __prepare_dummy_closed_trade_legend_marker(
        self,
        marker: str,
        label: str,
        markerfacecolor: str,
    ) -> Line2D:
        return Line2D(
            [0],
            [0],
            marker=marker,
            linestyle="None",
            color="black",
            label=label,
            markerfacecolor=markerfacecolor,
            markersize=10,
        )

    def __get_bar_color(self, open_val: float, close_val: float) -> str:
        return (
            self.__POSITIVE_BAR_COLOR
            if close_val >= open_val
            else self.__NEGATIVE_BAR_COLOR
        )

    def __get_date_format(self) -> str:
        diffs = np.diff(self.__data.datetime)
        min_diff = np.min(diffs)

        if min_diff < np.timedelta64(1, "h"):
            return "%H:%M"
        elif min_diff < np.timedelta64(12, "h"):
            return "%m-%d %H:%M"
        elif min_diff < np.timedelta64(28, "D"):
            return "%Y-%m-%d"
        elif min_diff < np.timedelta64(365, "D"):
            return "%Y-%m"
        else:
            return "%Y"

    def __hide_annotation_and_redraw_if_necessary(
        self,
        annotation: Annotation,
        event: MouseEvent,
    ) -> None:
        if annotation.get_visible():
            annotation.set_visible(False)
            event.canvas.draw_idle()
