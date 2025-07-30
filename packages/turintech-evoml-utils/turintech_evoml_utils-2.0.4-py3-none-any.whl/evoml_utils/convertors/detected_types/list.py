import re
import json
from typing import Optional


import pandas as pd


def to_list(input: Optional[str]) -> Optional[list]:
    """
    Converts input to a list if input follows a valid json list format and returns the converted object. If input
    is not in a valid format, it returns None.

    Args:
        input:
            Can be string or np.nan or None.
    Returns:
        Optional[list]:
            The converted list or None.
    """

    if not isinstance(input, str):
        return None
    try:
        input_double_quotation = re.sub("'([^']+)'", '"\\g<1>"', input)  # replace pairs of
        # single quotes with pairs of double quotes as they are required by json parser
        json_obj = json.loads(input_double_quotation)
        if isinstance(json_obj, list):
            return json_obj
    except:
        return None
    return None


def to_list_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of strings to a column of the corresponding list objects. All strings not in valid JSON list
    format are converted to None.

    Args:
        column:
            pandas.Series column.
    Returns:
        pd.Series:
            pandas.Series column of list objects.
    """

    list_column = column.apply(to_list)
    if not isinstance(list_column, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(list_column)}.")
    return list_column
