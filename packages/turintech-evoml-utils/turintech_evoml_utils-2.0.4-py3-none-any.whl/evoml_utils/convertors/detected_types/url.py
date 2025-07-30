import re
from typing import Any, Union


import numpy as np
import pandas as pd


URL_PATTERN = re.compile(
    r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]"
    r"+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
)


def to_url_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of strings to a column containing only strings representing urls by converting all strings not in
    a valid url format to np.nan.

    Args:
        column:
            A column of strings in pandas.Series format.
    Returns:
        pd.Series:
            A column containing strings representing urls and/or nan values.
    """

    def url_match(x: Any) -> Union[str, float]:
        """Returns a string if it matches the URL pattern, otherwise returns nan."""
        if not isinstance(x, str):
            return np.nan
        if not URL_PATTERN.fullmatch(x):
            return np.nan
        return x

    # @pyright: doesn't understand that applying url_match to a series results in another series
    return column.apply(url_match)  # type: ignore
