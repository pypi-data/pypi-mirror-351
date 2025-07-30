from typing import Optional, Any, Union


import re
import numpy as np
import pandas as pd


PERCENTAGE_PATTERN = re.compile(r"(?P<num>-? ?\d+(,\d{3})*(\.\d+)?) ?(?P<percentage>%)?")


def percentage_to_numeric(value: Optional[Union[int, float, str]]) -> float:
    """
    Converts a percentage value to the corresponding float. If value is not a percentage but can be converted to a
    float, the function returns the converted float. In all other cases, the output is np.nan.

    Args:
        value:
            It can be string or nan.
    Returns:
        float:
            The converted float value or np.nan.
    """

    num = np.nan
    try:
        num = float(value)
    except:
        if isinstance(value, str):
            value = value.strip()
            if match := PERCENTAGE_PATTERN.fullmatch(value):
                num = float(match.group("num").replace(",", "").replace(" ", ""))
                if match.group("percentage") is not None:
                    num /= 100
    return num


def convert_percentage_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of string percentage values to a column of the corresponding float numbers
    and nan values for any non valid string value by using the function percentage_to_numeric.

    Args:
        column:
            The input column is pandas Series format.
    Returns:
        pd.Series:
            The converted column in pd.Series format.
    """
    numeric_column = column.apply(percentage_to_numeric)
    if not isinstance(numeric_column, pd.Series):
        raise ValueError(f"The output is expected to be a pandas Series, received: {type(numeric_column)}.")
    return numeric_column


def is_percentage(value: Optional[str]) -> bool:
    """
    Checks if the input is a valid percentage string.

    Args:
        value:
            Input string.
    Returns:
        bool:
            True if value is valid percentage, False otherwise.
    """

    if pd.isnull(value):
        return False

    value_str = value

    try:
        value_str = str(value)
    except Exception:
        return False

    match = PERCENTAGE_PATTERN.fullmatch(value_str)
    return bool(match and match.group("percentage"))
