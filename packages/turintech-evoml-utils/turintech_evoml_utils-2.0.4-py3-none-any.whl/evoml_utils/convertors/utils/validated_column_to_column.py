from typing import Callable, Any


import pandas as pd


def validated_column_to_column(column: pd.Series, element_conversion_function: Callable[[Any], Any]) -> pd.Series:
    converted_column = column.apply(element_conversion_function)
    if not isinstance(converted_column, pd.Series):
        raise TypeError(f"Expected a pandas.Series. Received: {type(converted_column)}.")
    return converted_column
