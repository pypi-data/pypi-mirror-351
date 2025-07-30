import json
import re
from typing import Optional


import pandas as pd


def to_map(value: Optional[str]) -> Optional[dict]:
    """
    Converts value to a dictionary if value follows a valid json object format and returns the converted
    object. If value is not in a valid format, it returns None.

    Args:
        value:
            Can be string or np.nan or None
    Returns:
        Optional[dict]:
            The corresponding dictionary or None.
    """

    if not isinstance(value, str):
        return None
    try:
        input_double_quotation = re.sub("'([^']+)'", '"\\g<1>"', value)  # replace pairs of
        # single quotes with pairs of double quotes as they are required by json parser
        json_obj = json.loads(input_double_quotation)
        if isinstance(json_obj, dict):
            return json_obj
    except:
        return None
    return None


def to_map_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of strings to a column of the corresponding dictionary objects. All strings not in a valid JSON
    object format are converted to None.

    Args:
        column:
            A pandas.Series column.
    Returns:
        pd.Series:
            Corresponding dictionary object.
    """
    map_column = column.apply(to_map)
    if not isinstance(map_column, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(map_column)}")
    return map_column
