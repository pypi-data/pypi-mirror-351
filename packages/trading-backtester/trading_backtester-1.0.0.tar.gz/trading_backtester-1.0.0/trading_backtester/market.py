from typing import Optional

from .data import CandlestickPhase, Data


class Market:
    """Represents the market data and provides methods to access it.

    This class is used to access the current market data and historical data by user.
    Acts as "proxy" for the Data class.
    """

    def __init__(self, data: Data):
        """Initializes a Market object.

        Args:
            data (Data): The data object containing market data.
        """

        self.__data = data

    def get_current_price(self) -> float:
        """Returns the current price of the asset.

        Returns:
            float: The current price of the asset.
        """
        return self.__data.get_current_price()

    def get_current_open_price(self) -> float:
        """Returns the open price of the current candlestick of the asset.

        Returns:
            float: The open price of the current candlestick.
        """
        return self.__data.get_current_data("open")

    def get_current_close_price(self) -> float:
        """Returns the close price of the current candlestick of the asset.

        Returns:
            float: The close price of the current candlestick.
        """

        if self.__data.get_candlestick_phase() != CandlestickPhase.CLOSE:
            raise ValueError(
                "Candlestick is not closed yet. Can't look into the future."
            )
        return self.__data.get_current_data("close")

    def get_current_low_price(self) -> float:
        if self.__data.get_candlestick_phase() == CandlestickPhase.OPEN:
            raise ValueError(
                "Candlestick is at open phase. Can't look into the future."
            )
        return self.__data.get_current_data("low")

    def get_current_high_price(self) -> float:
        """Returns the high price of the current candlestick of the asset.

        Returns:
            float: The high price of the current candlestick.
        """

        if self.__data.get_candlestick_phase() == CandlestickPhase.OPEN:
            raise ValueError(
                "Candlestick is at open phase. Can't look into the future."
            )
        return self.__data.get_current_data("high")

    def get_open_price_on_nth_ago(self, n: int) -> Optional[float]:
        """Returns the open price of the nth candlestick in the past.

        Args:
            n (int): The number of candlesticks in the past to look back.

        Returns:
            Optional[float]: The open price of the nth candlestick in the past.
                Returns None if n is greater than the current data index.

        Raises:
            ValueError: If n is less than 1.
        """

        if n < 1:
            raise ValueError("To look into the past, n must be greater than 0.")

        if self.__data.get_current_data_index() - n < 0:
            return None

        return self.__data[self.__data.get_current_data_index() - n]["open"]

    def get_close_price_on_nth_ago(self, n: int) -> Optional[float]:
        """Returns the close price of the nth candlestick in the past.

        Args:
            n (int): The number of candlesticks in the past to look back.

        Returns:
            Optional[float]: The close price of the nth candlestick in the past.
                Returns None if n is greater than the current data index.

        Raises:
            ValueError: If n is less than 1.
        """

        if n < 1:
            raise ValueError("To look into the past, n must be greater than 0.")

        if self.__data.get_current_data_index() - n < 0:
            return None

        return self.__data[self.__data.get_current_data_index() - n]["close"]

    def get_low_price_on_nth_ago(self, n: int) -> Optional[float]:
        """Returns the low price of the nth candlestick in the past.

        Args:
            n (int): The number of candlesticks in the past to look back.

        Returns:
            Optional[float]: The low price of the nth candlestick in the past.
                Returns None if n is greater than the current data index.

        Raises:
            ValueError: If n is less than 1.
        """

        if n < 1:
            raise ValueError("To look into the past, n must be greater than 0.")

        if self.__data.get_current_data_index() - n < 0:
            return None

        return self.__data[self.__data.get_current_data_index() - n]["low"]

    def get_high_price_on_nth_ago(self, n: int) -> Optional[float]:
        """Returns the high price of the nth candlestick in the past.

        Args:
            n (int): The number of candlesticks in the past to look back.

        Returns:
            Optional[float]: The high price of the nth candlestick in the past.
                Returns None if n is greater than the current data index.

        Raises:
            ValueError: If n is less than 1.
        """

        if n < 1:
            raise ValueError("To look into the past, n must be greater than 0.")

        if self.__data.get_current_data_index() - n < 0:
            return None

        return self.__data[self.__data.get_current_data_index() - n]["high"]
