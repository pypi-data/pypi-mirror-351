import re
from typing import Optional, Tuple, Any


import numpy as np
import pandas as pd


from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column


LAT_DMS_PATTERN = re.compile(r'(([1-8]?\d)\u00b0([1-5]?\d)\'([1-5]?\d(\.\d+)?)|90\u00b00\'0(\.0+)?)"[NSns]?')
LONG_DMS_PATTERN = re.compile(r'(([1-9]?\d|1[0-7]\d)\u00b0([1-5]?\d)\'([1-5]?\d(\.\d+)?)|180\u00b00\'0(\.0+)?)"[EWew]?')


def to_long_lat(value: Optional[str]) -> Optional[Tuple[float, float]]:
    """
    If value is a string latLong tuple (brackets are optional, numbers separated by comma),
    the function returns a tuple of the corresponding float numbers. On all other
    inputs, the function returns None.

    Args:
        value:
            String or np.nan.
    Returns:
        Optional[Tuple[float, float]]
            A tuple of floats that can represent latitude and longitude coordinates or None.
    """

    if isinstance(value, str):
        start = value.startswith("(")
        end = value.endswith(")")
        if start != end:
            return None
        if start:
            value = value[1:-1]  # remove brackets
        values = value.split(",")
        if len(values) != 2:  # number of commas different than one
            return None
        try:
            lat_long = (float(values[0]), float(values[1]))
            if lat_long[0] > 90 or lat_long[0] < -90:
                return None
            if lat_long[1] > 180 or lat_long[1] < -180:
                return None
            return lat_long
        except:
            # check for dms pattern
            if LAT_DMS_PATTERN.fullmatch(values[0]) is None or LONG_DMS_PATTERN.fullmatch(values[1]) is None:
                return None
            # convert dms to decimal values
            lat = convert_dms_to_dd(values[0])
            long = convert_dms_to_dd(values[1])
            return lat, long
    return None


def convert_dms_to_dd(value: str) -> float:
    """
    Converts a string value in valid DMS format to a float number that represents the corresponding degrees number.

    Args:
        value:
            String value in valid DMS format
    Returns:
        float:
            Degrees number.
    """

    if is_dms_value(value) is False:
        raise TypeError("Input string is not in valid DMS format.")

    deg_index = value.find("\u00b0")
    degrees = float(value[:deg_index])
    min_index = value.find("'")
    minutes = float(value[deg_index + 1 : min_index])
    sec_index = value.find('"')
    seconds = float(value[min_index + 1 : sec_index])
    direction = value[-1]
    degrees = degrees + minutes / 60 + seconds / 3600
    if direction in ["S", "s", "W", "w"]:
        degrees *= -1
    return degrees


def to_lat(value: str) -> float:
    """
    Converts a string value to a float value or a dms latitude string value to the corresponding value.
    If value cannot be converted to float in latitude range or not in valid dms latitude format, the function returns
    nan.

    Args:
        value:
            String input.
    Returns:
        float:
            A float latitude value or nan if cannot be converted.
    """

    num = np.nan
    try:
        num = float(value)
        if num < -90 or num > 90:
            num = np.nan
    except:
        if isinstance(value, str) and LAT_DMS_PATTERN.fullmatch(value):
            num = convert_dms_to_dd(value)
    return num


def to_long(value: str) -> float:
    """
    Converts a string value to a float value or a dms longitude string value to the corresponding value.
    If value cannot be converted to float in longitude range or not in valid dms longitude format, the function returns
    nan.

    Args:
        value:
            String input.
    Returns:
        float:
            A float longitude value or nan if cannot be converted.
    """

    num = np.nan
    try:
        num = float(value)
        if num < -180 or num > 180:
            num = np.nan
    except:
        if isinstance(value, str) and LONG_DMS_PATTERN.fullmatch(value):
            num = convert_dms_to_dd(value)
    return num


def to_geo_location_column(column: pd.Series, geo_type: str) -> pd.Series:
    """
    Converts a column of string values to a column of the given geo_type. If geo_type is equal to
    latLong,the column is converted to a column of tuples of float numbers representing latitude and longitude.
    If geo_type is equal to latitude, the column is converted to a column of float numbers representing
    latitude, and if geo_type is equal to longitude, the column is converted to a column of float numbers representing
    longitude. In all cases, all invalid values are converted to None.

    Args:
        column:
            Input column in pandas.Series format.
        geo_type:
            String representing the geolocation format. It can be latLong, latitude, longitude.
    Returns:
        pd.Series:
            Converted column of string values to given geo_type.
    """
    column = validated_column_to_column(column, lambda x: x.replace(" ", "") if isinstance(x, str) else x)
    if geo_type == "latLong":
        return validated_column_to_column(column, to_long_lat)
    if geo_type == "latitude":
        return validated_column_to_column(column, to_lat)
    if geo_type == "longitude":
        return validated_column_to_column(column, to_long)
    raise ValueError("Not valid value for geoLocation subtype.")


def is_dms_value(value: Any) -> bool:
    """
    Checks if the input is a valid latitude or longitude value in dms format.

    Args:
        value:
            Input string.
    Returns:
        bool:
            True if value is a valid dms value, False otherwise.
    """
    if not isinstance(value, str):
        return False
    return LAT_DMS_PATTERN.fullmatch(value) is not None or LONG_DMS_PATTERN.fullmatch(value) is not None
