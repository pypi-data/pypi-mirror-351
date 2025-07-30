import re
import numpy as np
import pandas as pd
from typing import Union, Any


# Regex pattern to match numbers, even if commas are used to separate thousands
# E.g. "1,000", "1000" "1,000.1", "1000.1, "1", and "1.1"
FLOAT_PATTERN = re.compile(r"-? ?\d+(,\d{3})*(\.\d+)?")


def to_float(value: Union[bool, float, int, str, None]) -> float:
    """Converts a value of type bool, float, int, str, or None to float. This custom conversion function is necessary
     to support conversion of string representations of numbers with commas as thousands separators.

    Args:
        value (Union[float, int, str, bool, None]): The input value to be converted.

    Returns:
        (float): Converted float or np.nan.
    """
    if isinstance(value, float):
        return value
    if value is None:
        return np.nan
    num = np.nan
    try:
        num = float(value)
    except:
        if not isinstance(value, str):
            return num
        if FLOAT_PATTERN.fullmatch(value.strip()):
            return float(value.replace(",", "").replace(" ", ""))
    return num


def to_float_column(column: pd.Series, *args: Any, **kwargs: Any) -> pd.Series:
    """Converts any pandas series to a series with float dtype.

    Args:
        column (pd.Series): The input column in pandas.Series format.

    Returns:
        pd.Series: The converted column with float dtype.
    """
    # No conversion necessary if the column is already a float column
    if pd.api.types.is_float_dtype(column):
        return column

    # For some usages it may not be necessary to convert integers to floats, and this operation is expensive on large
    # datasets. But this function guarantees that the output is always a float column so this conversion is necessary.
    if pd.api.types.is_integer_dtype(column) or pd.api.types.is_bool_dtype(column):
        return column.astype(np.float64)

    # We deal with all other types, including strings and mixtures of types, here. Pandas can convert some strings to
    # floats, but it cannot parse numbers which contain commas
    numeric_column = pd.to_numeric(column, errors="coerce")  # errors='coerce' replaces invalid values with NaN
    if not isinstance(numeric_column, pd.Series):
        raise TypeError(f"pandas.to_numeric is expected to return a Series, got {type(numeric_column)}")

    # We do a second pass over elements which could not be converted to float by pandas.to_numeric, and try to convert
    # them using our custom converter. This is mainly to support strings with commas as thousands separators.
    null_map: pd.Series = numeric_column.isnull()
    numeric_column[null_map] = column.loc[null_map].apply(to_float)

    return numeric_column
