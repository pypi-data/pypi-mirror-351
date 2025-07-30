import re
from typing import Optional, Tuple


import numpy as np
import pandas as pd


from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column
from evoml_utils.convertors.utils.common_patterns import STRIP_PATTERN, MULTIPLIERS


CURRENCY_SYMBOLS = ["£", "$", "€", "¥"]
CURRENCY_NAMES = {"£": "GBP", "$": "USD", "€": "EUR", "¥": "CNY"}
CURRENCY_PATTERN_1 = re.compile(r"-?( ?[$£€¥]) ?\d+(,\d{3})*(\.\d+)?( ?[kmb])?")
CURRENCY_PATTERN_2 = re.compile(r"-? ?\d+(,\d{3})*(\.\d+)?( ?[kmb])?( ?[$£€¥])")


def currency_number_split(
    value: Optional[str],
) -> Tuple[float, Optional[str]]:
    """
    Given a value the function tries to get the numeric part and the currency symbol. If a valid currency value is
    given, the function returns a tuple consisting of the numeric part and the currency symbol. On all other inputs,
    the function returns a tuple of nan values.

    Args:
        value:
            It can be string or nan.
    Returns:
        Tuple[Optional[float], Optional[str]]:
            Returns a tuple of the numeric part and the currency symbol of a currency value.
    """

    num = np.nan
    currency_symbol = None
    if isinstance(value, str):
        x = value.strip().lower()
        for currency in CURRENCY_SYMBOLS:
            if currency in x:
                currency_symbol = currency
        if CURRENCY_PATTERN_1.fullmatch(x):
            xa1 = re.sub("|".join(STRIP_PATTERN), "", x)
            try:
                num = float(xa1)
            except:
                num = MULTIPLIERS[xa1[-1]] * float(xa1[:-1])
        elif CURRENCY_PATTERN_2.fullmatch(x):
            xb1 = re.sub("|".join(STRIP_PATTERN), "", x)
            try:
                num = float(xb1)
            except:
                num = MULTIPLIERS[xb1[-1]] * float(xb1[:-1])
    if pd.isnull(num):
        return np.nan, None
    return num, currency_symbol


def convert_currency_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of string currency values to a column consisting of the numeric parts of the currency values.
    Any invalid string value is converted to a None value.

    Args:
        column:
            The input column in pandas.Series format.
    Returns:
        pd.Series:
            The converted column consisting of floats and None values.
    """

    converted = validated_column_to_column(column, currency_number_split)
    return validated_column_to_column(converted, lambda x: x[0] if not pd.isnull(x) else x)
