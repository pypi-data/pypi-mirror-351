from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Tuple

import numpy as np

# DATA_TYPE defines the structured dtype for OHLCV time series data.
# Fields:
#     datetime (datetime64[ns]): Timestamp of the data point.
#     open (float): Opening price.
#     high (float): Highest price during the interval.
#     low (float): Lowest price during the interval.
#     close (float): Closing price.
#     volume (float): Trade volume.
DATA_TYPE = np.dtype(
    [
        ("datetime", "datetime64[ns]"),
        ("open", "f8"),
        ("high", "f8"),
        ("low", "f8"),
        ("close", "f8"),
        ("volume", "f8"),
    ]
)


class CandlestickPhase(Enum):
    """Represents the phase of a candlestick."""

    OPEN = 1
    """Open phase of a candlestick."""
    CLOSE = 2
    """Close phase of a candlestick."""


class Data:
    """Represents the market data and provides methods to access it."""

    def __init__(self, data: np.ndarray[Any, np.dtype[Any]]):
        """Initializes a Data object.

        Args:
            data (np.ndarray[Any, np.dtype[Any]]): The data array containing market data.
        """

        self.__data = data
        self.__current_data_index = 0
        self.__candlestick_phase = CandlestickPhase.OPEN

    def __getitem__(self, index: int) -> Any:
        """Returns the data at the specified index.

        Args:
            index (int): The index of the data to retrieve.

        Returns:
            Any: The data at the specified index.
        """

        return self.__data[index]

    def __len__(self) -> int:
        """Returns the length of the data.

        Returns:
            int: The length of the data.
        """

        return len(self.__data)

    def __iter__(self):
        """Returns an iterator for the data.

        Returns:
            Iterator: An iterator for the data.
        """

        return iter(self.__data)

    def set_candlestick_phase(self, phase: CandlestickPhase) -> None:
        """Sets the candlestick phase.

        Candlestick may be in OPEN or CLOSE phase.

        Args:
            phase (CandlestickPhase): The candlestick phase to set.
        """

        self.__candlestick_phase = phase

    def get_candlestick_phase(self) -> CandlestickPhase:
        """Returns the current candlestick phase.

        Returns:
            CandlestickPhase: The current candlestick phase.
        """

        return self.__candlestick_phase

    def increment_data_index(self) -> None:
        """Increments the current data index.

        This method is used to move to the next data point in the dataset.
        """

        self.__current_data_index += 1

    def get_data(self, key: Optional[str] = None) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the data for the specified key or the entire dataset.

        Args:
            key (Optional[str]): The key to retrieve data for. If None, returns the entire dataset.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The data for the specified key or the entire dataset.
        """

        return self.__data[key] if key else self.__data

    def get_current_data_index(self) -> int:
        """Returns the current data index.

        Returns:
            int: The current data index.
        """

        return self.__current_data_index

    def get_current_data(self, key: str) -> float:
        """Returns the current data for the specified key.

        Args:
            key (str): The key to retrieve data for.

        Returns:
            float: The current data for the specified key.
        """

        return self.__data[self.__current_data_index][key]

    def get_current_price(self) -> float:
        """Returns the current price of the asset.

        If the candlestick is in OPEN phase, returns the open price,
        if in CLOSE phase, returns the close price.

        Returns:
            float: The current price of the asset.
        """

        return self.__data[self.__current_data_index][
            "open" if self.__candlestick_phase == CandlestickPhase.OPEN else "close"
        ]

    def get_current_low_price(self) -> float:
        """Returns the low price of the current candlestick of the asset.

        If the candlestick is in OPEN phase, returns the open price,
        if in CLOSE phase, returns the low price.

        Returns:
            float: The low price of the current candlestick.
        """

        return (
            self.__data[self.__current_data_index]["low"]
            if self.__candlestick_phase == CandlestickPhase.CLOSE
            else self.__data[self.__current_data_index]["open"]
        )

    def get_current_high_price(self) -> float:
        """Returns the high price of the current candlestick of the asset.

        If the candlestick is in OPEN phase, returns the open price,
        if in CLOSE phase, returns the high price.

        Returns:
            float: The high price of the current candlestick.
        """

        return (
            self.__data[self.__current_data_index]["high"]
            if self.__candlestick_phase == CandlestickPhase.CLOSE
            else self.__data[self.__current_data_index]["open"]
        )

    def get_current_numpy_datetime(self) -> np.datetime64:
        """Returns the datetime of the current candlestick of the asset.

        If the candlestick is in OPEN phase, returns the open datetime,
        if in CLOSE phase, returns the close datetime.

        Returns:
            np.datetime64: The datetime of the current candlestick.
        """

        return self.__data[self.__current_data_index]["datetime"]

    def get_current_datatime(self) -> datetime:
        """Returns the datetime of the current candlestick of the asset.

        If the candlestick is in OPEN phase, returns the open datetime,
        if in CLOSE phase, returns the close datetime.

        Returns:
            datetime: The datetime of the current candlestick.
        """

        return (
            self.__data[self.__current_data_index]["datetime"]
            .astype("M8[ms]")
            .astype(datetime)
        )

    @property
    def datetime(self) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the datetime data of the dataset.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The datetime data of the dataset.
        """

        return self.__data["datetime"]

    @property
    def open(self) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the open price data of the dataset.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The open price data of the dataset.
        """

        return self.__data["open"]

    @property
    def low(self) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the low price data of the dataset.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The low price data of the dataset.
        """

        return self.__data["low"]

    @property
    def high(self) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the high price data of the dataset.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The high price data of the dataset.
        """

        return self.__data["high"]

    @property
    def close(self) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the close price data of the dataset.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The close price data of the dataset.
        """

        return self.__data["close"]

    @property
    def volume(self) -> np.ndarray[Any, np.dtype[Any]]:
        """Returns the volume data of the dataset.

        Returns:
            np.ndarray[Any, np.dtype[Any]]: The volume data of the dataset.
        """

        return self.__data["volume"]

    @staticmethod
    def from_array(
        data: List[
            Tuple[
                Any,
                Optional[float],
                Optional[float],
                Optional[float],
                Optional[float],
                Optional[float],
            ]
        ],
    ) -> "Data":
        """Creates a Data object from a list of tuples.

        Each tuple contains the following fields:
            - datetime (Any): Timestamp of the data point.
            - open (Optional[float]): Opening price.
            - high (Optional[float]): Highest price during the interval.
            - low (Optional[float]): Lowest price during the interval.
            - close (Optional[float]): Closing price.
            - volume (Optional[float]): Trade volume.

        Args:
            data (List[Tuple[Any, Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]]): The data to create the Data object from.
        """

        data_array = np.array(
            data,
            dtype=DATA_TYPE,
        )
        return Data(data_array)

    @staticmethod
    def from_csv(
        file_path: str,
        delimiter: str = ",",
    ) -> "Data":
        """Creates a Data object from a CSV file.

        The CSV file should have the following columns:
            - datetime (datetime64[ns]): Timestamp of the data point.
            - open (float): Opening price.
            - high (float): Highest price during the interval.
            - low (float): Lowest price during the interval.
            - close (float): Closing price.
            - volume (float): Trade volume.
        The first row of the CSV file should contain the column names.

        Args:
            file_path (str): The path to the CSV file.
            delimiter (str): The delimiter used in the CSV file. Default is ','.
        """

        data_np = np.genfromtxt(
            file_path,
            delimiter=delimiter,
            skip_header=1,
            dtype=DATA_TYPE,
            usecols=(0, 1, 2, 3, 4, 5),
        )
        return Data(data_np)
