# Trading-Backtester

A Python library for backtesting trading strategies. It allows users to simulate historical trades, evaluate strategy performance, and analyze key metrics such as returns, drawdowns, and risk. The library supports custom indicators, making it suitable for both simple and advanced strategies.

## Requirements

- numpy - for data and numeric manipulation
- matplotlib - for plotting results

### Why numpy?

Of course I could handle most mathematical operation using regular floats number, but NumPy is widely used for such tasks and help make code more structured. What's more, NumPy is supported by many trading indicators libraries - for example, I wanted to use my backtesting engine with `TA-Lib`, library that takes NumPy arrays as input. 

## Why another "Backtesting" library

There are many backtesting libraries and platforms available - that's right. However, when I was looking for Python backtesting library that could handle some specific requirements for my strategies - such as placing different orders at market open and closes, detecting price gaps, etc. - I found that the features set of popular libraries were not sufficient.

Additionally, building my own backtesting engine served as a great side project for learing and improving my development skills.

## Installation

Library is available on `PyPI`.

```bash
python3 -m pip install trading-backtester
```

## Usage example

### Declare RSI Indicator

We use [TA-Lib](https://github.com/TA-Lib/ta-lib-python) to calculate Relative Strength Indicator values. 

```python
class RsiIndicator(Indicator):
    def __init__(self, period: int):
        super().__init__()
        self.__period = period

    def _calc_indicator_values(self, data: Data) -> np.ndarray[Any, np.dtype[Any]]:
        rsi = talib.RSI(data.close, timeperiod=self.__period)
        return rsi
```

### Declare trading strategy

Our example trading strategy is based on the RSI Indicator:
- When RSI Indicator value crosses above 30 from below:
  - Open a long position
  - Close any existing short position
- When RSI indicator values crosses below 70 from above:
  - Open short position
  - Close any existing long position


```python
class RsiStrategy(Strategy):
    def __init__(
        self,
    ):
        super().__init__()
        self.__rsi_indicator = RsiIndicator(period=14)

    def collect_orders(
        self, candlestick_phase: CandlestickPhase, price: float, date_time: datetime
    ) -> List[Order]:
        orders: List[Order] = []

        if self.__rsi_indicator[-1] < 30 and self.__rsi_indicator[0] >= 30:
            # Open a long position when RSI crosses above 30
            # and close short position if exists

            if (
                len(self._positions) != 0
                and self._positions[0].position_type == PositionType.SHORT
            ):
                # Close short position if exists
                orders.append(
                    CloseOrder(
                        size=self._positions[0].size,
                        position_type=PositionType.SHORT,
                    )
                )

            if (
                len(self._positions) == 0
                or self._positions[0].position_type != PositionType.LONG
            ):
                orders.append(
                    OpenOrder(
                        size=1,
                        position_type=PositionType.LONG,
                    )
                )

        elif self.__rsi_indicator[-1] > 70 and self.__rsi_indicator[0] <= 70:
            # Open a short position when RSI crosses below 70
            # and close long position if exists

            if (
                len(self._positions) != 0
                and self._positions[0].position_type == PositionType.LONG
            ):
                # Close long position if exists
                orders.append(
                    CloseOrder(
                        size=self._positions[0].size,
                        position_type=PositionType.LONG,
                    )
                )

            if (
                len(self._positions) == 0
                or self._positions[0].position_type != PositionType.SHORT
            ):
                orders.append(
                    OpenOrder(
                        size=1,
                        position_type=PositionType.SHORT,
                    )
                )

        return orders
```

### Declare Backtester

For example purposes, we assume `1%` broker's commission and no spread.

```python
commission = Commission(CommissionType.RELATIVE, 0.001)
backtest = Backtester(
    data, RsiStrategy, money=10000, benchmark=data, commission=commission
)
backtest.run()
```

### Print statistics and draw plot

```python
stats = backtest.get_statistics()
print(stats)

plotting = backtest.get_plotting()
plotting.show_plot()
```


```
=== Statistics ===
Total trades: 41
Total open trades: 21
Total close trades: 20
Total open long trades: 11
Total close long trades: 10
Total open short trades: 10
Total close short trades: 10
Final money: 5069.67
Final total equity: 10638.73
Return: 638.73 (6.39%)
Max drawdown: 2012.18 (17.66%)
Max drawdown duration: 763
Winning trades: 15 (75.00%)
Best trade return: 20.38%
Worst trade return: -34.94%
Beta: 0.10
Alpha: -0.11
Buy and hold return: 166.80%
Total commission paid: 134.66
```

![RSI Indicator example result Plot](example/rsi_indicator_example_result_plot.png "RSI Indicator example result Plot")
