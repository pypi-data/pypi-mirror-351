import re
from typing import Any, Optional, Dict, Tuple


import numpy as np
import pandas as pd


UNIT_NUM_PATTERN = re.compile(
    r"(?P<number>-? ?\d+(,\d{3})*(\.\d+)? ?)(?P<unit>(?i:(kilo|centi|milli)?meter(s)?|km"
    r"|cm|inch(es)?|miles?|mi\.?|foot|feet|ft|in|yards?|yd|lbs?|pounds?|ounces?|\x22|\'"
    r"|(kilo|milli)?grams?|kgs?|h(ours?)?|min(utes?)?|s(econds?)?|d(ays?)?|min.|sec(.|s)?|m|g|mm|mg))"
)

FEET_INCHES_PATTERN = re.compile(
    r"(?P<feet>-? ?\d+(,\d{3})*(\.\d+)? ?)(?i:foot|feet|ft|\')"
    r"(?P<inches> ?\d+(,\d{3})*(\.\d+)? ?)(?i:inches|inch|in|\x22)?"
)

MEMORY_PATTERN = re.compile(
    r"(?P<number>\d+(,\d{3})*(\.\d+)? ?)(?P<unit>(?i:(kilo|mega|giga|tera)?(bytes?|bits?)"
    r"|KB|MB|GB|TB|B|Kb|b|Mb|Gb|Tb|kb|mb|gb|tb))"
)

LENGTH_UNIT_PATTERN = re.compile(
    r"(?i)(kilo|centi|milli)?meter(s)?|km|m|cm|mm|inch(es)?|miles?|mi\.?|foot|feet|ft|in|yards?|\x22|\'|yd"
)

MASS_UNIT_PATTERN = re.compile(r"(?i)lbs?|pounds?|(kilo|milli)?grams?|kgs?|mg|g|ounces?")

DURATION_PATTERN = re.compile(r"(?i)h(ours?)?|min(utes?)?|s(econds?)?|d(ays?)?")

MEMORY_UNIT_PATTERN = re.compile(
    r"(?i)(kilo|mega|giga|terra)?(bytes?|bits?)" r"|KB|MB|GB|TB|B|Kb|b|Mb|Gb|Tb|kb|mb|gb|tb"
)

UNIT_CONVERSIONS = {
    "m": {
        "km": 1000,
        "cm": 0.01,
        "mm": 0.001,
        "Mm": 1000000,
        "kilometer": 1000,
        "kilometers": 1000,
        "m": 1,
        "meters": 1,
        "meter": 1,
        "centimeters": 0.01,
        "centimeter": 0.01,
        "millimeter": 0.001,
        "millimeters": 0.001,
        "inch": 0.0254,
        "inches": 0.0254,
        "\x22": 0.0254,
        "in": 0.0254,
        "miles": 1609.34,
        "mile": 1609.34,
        "mi.": 1609.34,
        "mi": 1609.34,
        "foot": 0.3048,
        "feet": 0.3048,
        "ft": 0.3048,
        "'": 0.3048,
        "yd": 0.9144,
        "yards": 0.9144,
        "yard": 0.9144,
    },  # conversion rates to m
    "kg": {
        "lb": 0.453592,
        "lbs": 0.453592,
        "pounds": 0.453592,
        "pound": 0.453592,
        "ounce": 0.0283495,
        "ounces": 0.0283495,
        "kilogram": 1,
        "kilograms": 1,
        "gram": 0.001,
        "grams": 0.001,
        "milligram": 10**-6,
        "milligrams": 10**-6,
        "kg": 1,
        "kgs": 1,
        "mg": 10**-6,
        "g": 0.001,
        "Mg": 1000,
    },  # conversion rates to kg
    "h": {
        "hours": 1,
        "h": 1,
        "hour": 1,
        "min": 1 / 60,
        "minute": 1 / 60,
        "minutes": 1 / 60,
        "s": 1 / 3600,
        "second": 1 / 3600,
        "seconds": 1 / 3600,
        "d": 24,
        "days": 24,
        "day": 24,
    },  # conversion rates to h
    "GB": {
        "byte": 1.0 / (1024 * 1024 * 1024),
        "bytes": 1.0 / (1024 * 1024 * 1024),
        "bits": 1.0 / (1024 * 1024 * 1024 * 8),
        "bit": 1.0 / (1024 * 1024 * 1024 * 8),
        "kilobyte": 1.0 / (1024 * 1024),
        "kilobytes": 1.0 / (1024 * 1024),
        "kilobit": 1.0 / (1024 * 1024 * 8),
        "kilobits": 1.0 / (1024 * 1024 * 8),
        "megabits": 1.0 / (1024 * 8),
        "megabit": 1.0 / (1024 * 8),
        "megabytes": 1.0 / 1024,
        "megabyte": 1.0 / 1024,
        "gigabyte": 1,
        "gigabytes": 1,
        "gigabits": 1.0 / 8,
        "gigabit": 1.0 / 8,
        "terabytes": 1024,
        "terabyte": 1024,
        "terabits": 1024.0 / 8,
        "terabit": 1024.0 / 8,
        "KB": 1 / (1024.0 * 1024.0),
        "MB": 1.0 / 1024,
        "GB": 1.0,
        "TB": 1024,
        "kB": 1.0 / (1024 * 1024),
        "mB": 1.0 / 1024,
        "gB": 1,
        "tB": 1024,
        "B": 1.0 / (1024 * 1024 * 1024),
        "b": 1.0 / (1024 * 1024 * 1024 * 8),
        "kb": 1.0 / (1024 * 1024 * 8),
        "mb": 1.0 / (1024 * 8),
        "gb": 1.0 / 8,
        "tb": 1024.0 / 8,
    },  # conversion rates to GB
}


def is_length_unit(unit: Any) -> bool:
    """
    Checks if the input is a string representing a length value.

    Args:
        unit:
            Input string.
    Returns:
        bool:
            True if value is a valid length value, False otherwise.
    """
    if not isinstance(unit, str):
        return False
    return LENGTH_UNIT_PATTERN.fullmatch(unit) is not None


def is_weight_unit(unit: Any) -> bool:
    """
    Checks if the input is a string representing a weight value.

    Args:
        unit:
            Input string.
    Returns:
        bool:
            True if value is a valid weight value, False otherwise.
    """
    if not isinstance(unit, str):
        return False
    return MASS_UNIT_PATTERN.fullmatch(unit) is not None


def is_duration_unit(unit: Any) -> bool:
    """
    Checks if the input is a string representing a duration unit.

    Args:
        unit:
            Input string.
    Returns:
        bool:
            True if value is a valid duration unit, False otherwise.
    """
    if not isinstance(unit, str):
        return False
    return DURATION_PATTERN.fullmatch(unit) is not None


def is_memory_unit(unit: Any) -> bool:
    """
    Checks if the input is a string representing a memory unit.

    Args:
        unit:
            Input string.
    Returns:
        bool:
            True if value is a valid memory unit, False otherwise.
    """

    if not isinstance(unit, str):
        return False
    return MEMORY_UNIT_PATTERN.fullmatch(unit) is not None


def find_unit(units: pd.Series) -> Optional[str]:
    """
    Given a column of units, the function returns a string that represents a unit that will be used for the major
    category of units found in the data.

    Args:
        units:
            A column in pandas.Series of strings representing units.
    Returns:
        Optional[str]:
            returns the unit string that corresponds to the major detected category in units. It can be one of the four
        : m, kg, GB, h.
    """

    length_units = units.apply(is_length_unit).sum()
    weight_units = units.apply(is_weight_unit).sum()
    memory_units = units.apply(is_memory_unit).sum()
    duration_units = units.apply(is_duration_unit).sum()
    categories_counts: Dict[str, int] = {
        "m": length_units,
        "kg": weight_units,
        "GB": memory_units,
        "h": duration_units,
    }
    if max(categories_counts.values()) == 0:  # no valid unit detected
        return None
    return max(categories_counts, key=lambda k: categories_counts[k])


def to_one_units_category(units: pd.Series, major_unit: str) -> pd.Series:
    """
    Replaces units that do not belong in the same category with major_unit (which takes the values m, h, kg, GB) with
    null.

    Args:
        units:
            A pandas.Series column with strings representing units.
        major_unit:
            A string a unit representing each of the four unit categories (weight, memory, length, duration). It takes
            one of the four values: m, h, kg, GB.
    Returns:
        pd.Series:
            A series with units in the same category with major_unit and nan values.
    """

    if major_unit not in ["m", "h", "kg", "GB"]:
        raise ValueError("Not valid unit value.")
    check_functions_dict = {
        "m": is_length_unit,
        "h": is_duration_unit,
        "kg": is_weight_unit,
        "GB": is_memory_unit,
    }
    check_unit_function = check_functions_dict[major_unit]
    units[~units.apply(check_unit_function)] = np.nan  # replacing values that do not belong in the same category
    return units


def unit_number_split(value: Optional[str]) -> Tuple[float, Optional[str]]:
    """
    Given a value the function tries to get the numeric part and the unit. If a valid unit&number value is given,the
    function returns a tuple consisting of the numeric part and the unit string. On all other inputs, the function
    returns a tuple of nan values.

    Args:
        value:
            It can be string or np.nan.
    Returns:
        Tuple[float, Optional[str]]:
            Returns a tuple of the numeric part and the unit string.
    """

    num = np.nan
    unit = None
    if isinstance(value, str):
        value = value.strip()

        if match := UNIT_NUM_PATTERN.fullmatch(value):
            xa1 = match.group("number").replace(" ", "").replace(",", "")
            num = float(xa1)
            unit = match.group("unit")

        elif match := FEET_INCHES_PATTERN.fullmatch(value):
            inches = match.group("inches").replace(" ", "").replace(",", "")
            feet = match.group("feet").replace(" ", "").replace(",", "")
            feet = float(feet)
            inches = float(inches)
            if feet < 0:
                inches *= -1
            num = feet * 12 + inches
            unit = "inches"

        elif match := MEMORY_PATTERN.fullmatch(value):
            xa1 = match.group("number").replace(" ", "").replace(",", "")
            num = float(xa1)
            unit = match.group("unit")

    return num, unit


def convert_to_common_unit(floats: pd.Series, units: pd.Series, unit: str) -> pd.Series:
    """
    Given a column of numbers, a column of the corresponding units, and a string with the target unit, it returns a
    column of numbers that correspond to all units converted to unit. If a value in units is not in the same category
    with unit, the corresponding value is set to none.

    Args:
        floats:
            A column of numbers in pandas.Series format.
        units:
            A column of strings (units) in pandas.Series format.
        unit:
            The target unit, as a string.
    Returns:
        pd.Series:
            A column with the converted numbers.
    """

    conversion_rates = UNIT_CONVERSIONS[unit]

    for i, value in units.items():
        if pd.isnull(value):
            floats[i] = None
        elif value in conversion_rates:
            floats[i] *= conversion_rates[value]
        elif value.lower() in conversion_rates:
            floats[i] *= conversion_rates[value.lower()]
        else:
            floats[i] = None
    return floats


def convert_unit_number_column(column: pd.Series, unit: str) -> pd.Series:
    """
    Converts a column with string unitNumber values to the corresponding float numbers for the input unit.
    Any invalid strings are converted to None.

    Args:
        column:
            Input column in pandas.Series format.
        unit:
            Represents the unit that all values will be converted to, as a string.
    Returns:
        pd.Series:
            The converted column with float values that correspond to the input unit.
    """

    converted = column.apply(unit_number_split)
    floats = converted.apply(lambda x: x[0] if not pd.isnull(x) else x)
    units = converted.apply(lambda x: x[1] if not pd.isnull(x) else x)
    if not isinstance(floats, pd.Series):
        raise ValueError(f"floats is expected to be a pandas series, received {type(floats)}.")
    if not isinstance(units, pd.Series):
        raise ValueError(f"units is expected to be a pandas series, received {type(units)}.")
    right_category_units = to_one_units_category(units, unit)
    converted_floats = convert_to_common_unit(floats, right_category_units, unit)
    return converted_floats
