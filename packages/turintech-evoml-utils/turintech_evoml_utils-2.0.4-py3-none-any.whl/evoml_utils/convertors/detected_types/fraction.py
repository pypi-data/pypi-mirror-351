from typing import Optional, Any, Union
import re


import numpy as np
import pandas as pd


FRACTIONS_PATTERN = re.compile(r"(?P<num1>-? ?\d+) ?\/ ?(?P<num2>\d+)")
RATIOS_PATTERN = re.compile(r"(?P<num1>\d+(.\d+)?) ?: ?(?P<num2>\d+(.\d+)?)")


def fraction_to_numeric(value: Optional[Union[str, int, float]]) -> float:
    """
    Converts a fraction string value to the corresponding float. If value is not a fraction but can be converted to a
    float, the function returns the converted float. In all other cases, the output is np.nan.

    Args:
        value:
            It can be string or nan.
    Returns:
        float:
            The converted float value or np.nan.
    """

    if not isinstance(value, (str, int, float)):
        return np.nan

    num = np.nan
    try:
        if isinstance(value, str):
            value = value.replace(" ", "")
        num = float(value)
    except:
        if match := FRACTIONS_PATTERN.fullmatch(value):
            num1 = float(match.group("num1"))
            num2 = float(match.group("num2"))
            if num2 == 0:
                num = np.nan
            elif num1 == 0:  # to avoid returning -0.0 in cases of -0/num
                num = 0
            else:
                num = num1 / num2
        elif match := RATIOS_PATTERN.fullmatch(value):
            try:
                num1 = float(match.group("num1"))  # raises an exception e.g. in the case 00:00
                num2 = float(match.group("num2"))
                num = np.nan if num2 == 0 else num1 / num2
            except:
                return np.nan
    return num


def convert_fraction_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of string fraction/ratio values to a column of the corresponding float numbers
    and nan values for any non valid string value by using the function fraction_to_numeric.

    Args:
        column:
            The input column is pandas Series format.
    Returns:
        pd.Series:
            The converted column in pd.Series format.
    """

    numeric_column = column.apply(fraction_to_numeric)
    if not isinstance(numeric_column, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(numeric_column)}")
    return numeric_column


def is_fraction(value: Any) -> bool:
    """
    Checks if the input is a valid fraction or ratio string.

    Args:
        value:
            Input string.
    Returns:
        bool:
            True if value is valid fraction, False otherwise.
    """

    if not isinstance(value, str):
        return False
    return FRACTIONS_PATTERN.fullmatch(value) is not None or RATIOS_PATTERN.fullmatch(value) is not None
