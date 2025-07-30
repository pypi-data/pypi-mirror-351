from enum import Enum


class SpreadType(Enum):
    """Represents the type of spread's calculation."""

    FIXED = 1
    """Fixed spread - the difference between the bid and ask prices is a fixed amount."""
    RELATIVE = 2
    """Relative spread - the difference between the bid and ask prices is a percentage of the price."""


class Spread:
    """Represents a spread between the bid and ask prices.

    Spread is applied twice - once at opening and once at closing the position.
    """

    def __init__(self, spread_type: SpreadType, spread_rate: float):
        """Initialize the Spread object.

        Args:
            spread_type (SpreadType): The type of spread's calculation.
            spread_rate (float): The spread rate - the amount of spread in case of FIXED (e.g. 1.0 == 1.0 pip) or the percentage in case of RELATIVE (e.g. 0.01 == 1%).
        """

        self.__spread_type = spread_type
        self.__spread_rate = spread_rate

    def calc_spread_value(self, price: float) -> float:
        """Calculate the spread value.

        Args:
            price (float): The price of the trade.

        Returns:
            float: The spread value.
        """

        spread = 0.0
        if self.__spread_type == SpreadType.FIXED:
            spread = self.__spread_rate
        elif self.__spread_type == SpreadType.RELATIVE:
            spread = self.__spread_rate * price

        return spread
