from enum import Enum
from typing import Tuple, Union


class CommissionType(Enum):
    """Represents the type of commission for the broker."""

    RELATIVE = 1
    """Commission is a percentage of the price."""
    MINIMUM_RELATIVE = 2
    """Commission is a percentage of the price,
        but has a minimum value that will be charged
        if calculated commission is lower.
    """
    FIXED = 3
    """Commission is a fixed fee per trade."""


class Commission:
    """Represents the commission for the broker.

    This class is used to calculate the commission for each trade.
    Commission is charged when a trade is executed - both on opening and closing.
    """

    def __init__(
        self,
        commission_type: CommissionType,
        commission_rate: Union[float, Tuple[float, float]],
    ):
        """Initializes a Commission object.

        Args:
            commission_type (CommissionType): The type of commission to be used.
            commission_rate (Union[float, Tuple[float, float]]): The commission rate.
                * If a float is provided, it represents either a relative commission as a percentage of the price, or a fixed fee.
                * If a tuple of two floats is given, it should be in the form of Tuple(minimum, relative), where:
                    - `minimum` is the minimum absolute commission that will be charged,
                    - `relative` is the percentage-based commission.
                    The effective commission will be the higher of the two: the `minimum` or the price multiplied by the `relative` rate.
                * If the commission type is FIXED, the commission_rate should be a float representing the fixed fee (1.0 == 1.0 pip).
                * If the commission type is RELATIVE, the commission_rate should be a float representing the percentage (0.01 == 1%).
                * If the commission type is MINIMUM_RELATIVE, the commission_rate should be a tuple of two floats representing the minimum fee (e.g. 1.0 == 1.0 $) and the relative percentage (e.g. 0.01 == 1%).
        """

        self.__commission_type = commission_type
        self.__commission_rate = commission_rate

    def calc_commission_value(self, price: float) -> float:
        """Calculates the commission value based on the price and commission type.

        Args:
            price (float): The price of the trade.

        Returns:
            float: The commission value.
        """

        commission = 0.0
        if self.__commission_type == CommissionType.RELATIVE:
            assert isinstance(self.__commission_rate, float)
            commission = price * self.__commission_rate
        elif self.__commission_type == CommissionType.MINIMUM_RELATIVE:
            assert (
                isinstance(self.__commission_rate, tuple)
                and len(self.__commission_rate) == 2
            )
            commission = max(
                self.__commission_rate[0], price * self.__commission_rate[1]
            )
        elif self.__commission_type == CommissionType.FIXED:
            assert isinstance(self.__commission_rate, float)
            commission = self.__commission_rate

        return commission
