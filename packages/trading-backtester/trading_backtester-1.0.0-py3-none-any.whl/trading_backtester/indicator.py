from abc import ABC, abstractmethod
from typing import Any, List

import numpy as np

from .data import Data


class Indicator(ABC):
    """Base class for indicators.

    Should be subclassed by the user to implement specific trading strategies.
    """

    def __init__(self):
        """Initializes an Indicator object."""

        self.__data: Data
        self.__indicator_values: np.ndarray[Any, np.dtype[Any]]

    def __getitem__(self, index: int) -> float | List[float] | Any:
        """Returns the indicator value at the specified index.

        Index is 0 for the current value, negative for past values.

        Args:
            index (int): The index of the indicator value to retrieve.

        Returns:
            float | List[float] | Any: The indicator value at the specified index.
        """

        if index > 0:
            raise IndexError(
                "Index must be 0 or negative (if you want to access past values)"
            )

        if index < 0:
            return self.__indicator_values[self.__data.get_current_data_index() + index]

        return self.get_current_indicator_value()

    def prepare_indicator(self, data: Data) -> None:
        """Prepares the indicator with the provided data.

        Args:
            data (Data): The data object containing market data.
        """

        self.__data = data
        self.__indicator_values = self._calc_indicator_values(self.__data)

    def get_indicator_values(self) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the indicator values.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The indicator values.
        """

        return self.__indicator_values

    def get_current_indicator_value(self) -> float | List[float] | Any:
        """Returns the current indicator value.

        Returns:
            float | List[float] | Any: The current indicator value.
        """

        return self.__indicator_values[self.__data.get_current_data_index()]

    def candlesticks_to_skip(self) -> int:
        """Returns the number of candlesticks to skip.

        Some indicators may require a certain number of candlesticks to be available before they can be calculated.

        Returns:
            int: The number of candlesticks to skip.
        """

        for index, indicator in enumerate(self.__indicator_values):
            if not np.isnan(indicator).any():
                return index
        return 0

    @abstractmethod
    def _calc_indicator_values(self, data: Data) -> np.ndarray[Any, np.dtype[Any]]:
        """Calculates the indicator values based on the provided data.

        Should be implemented by subclasses.

        Args:
            data (Data): The data object containing market data.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The calculated indicator values.
        """

        pass
