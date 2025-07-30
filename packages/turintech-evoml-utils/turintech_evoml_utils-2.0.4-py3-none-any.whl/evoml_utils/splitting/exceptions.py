from typing import Optional


class DataSplittingException(Exception):
    """Data splitting error."""

    message: str = "Data splitting error."

    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg or self.message)


class InsufficientWindowsException(DataSplittingException):
    """Raised when no splitting windows can be produced."""

    message = "The supplied dataset cannot be split using the supplied options."


class TooManyWindowsException(DataSplittingException):
    """Raised when the number of windows is too large for a trial to proceed."""

    message = (
        "The supplied options divide the dataset into too many windows. "
        "This would cause trials to be prohibitively slow."
    )
