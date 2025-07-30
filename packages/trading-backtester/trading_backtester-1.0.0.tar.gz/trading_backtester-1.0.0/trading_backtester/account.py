class Account:
    """Represents the account of the user."""

    def __init__(self, initial_money: float):
        """Initializes an Account object.

        Args:
            initial_money (float): The initial amount of user's money.
        """

        self.__current_money = initial_money

    @property
    def current_money(self) -> float:
        """Returns the current amount of money in the account.

        Returns:
            float: The current amount of money in the account.
        """

        return self.__current_money

    def update_money(self, amount: float) -> None:
        """Updates the current amount of money in the account.

        Args:
            amount (float): The amount to add or subtract from the current money.
        """

        self.__current_money += amount

    def has_enough_money(self, amount: float) -> bool:
        """Checks if the account has enough money.

        Args:
            amount (float): The amount to check.

        Returns:
            bool: True if the account has enough money, False otherwise.
        """

        return self.__current_money >= amount
