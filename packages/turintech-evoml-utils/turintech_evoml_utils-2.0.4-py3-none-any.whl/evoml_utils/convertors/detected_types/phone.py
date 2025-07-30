from typing import Optional, Union


import numpy as np
import pandas as pd


import phonenumbers as phone
from phonenumbers import NumberParseException


from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column
from evoml_utils.convertors.utils.special_nan_to_nan import special_nan_to_nan


def get_phone_strings(column: pd.Series) -> pd.Series:
    """Helper function to prepare column for phone number conversion.

    This function takes a column with values of types str, int, float, and
    returns a Series of string values.

    Removes trailing zeros in float values, e.g. 1234.0 -> 1234.
    Float values that are not integers are not allowed.
    Checks whether string values only contain allowed characters:
        0123456789()-.+ and whitespace.

    Only returns values that have passed all the checks.

    Args:
        column (pd.Series): column of potential phone numbers
            in string or numerical form.

    Returns:
        (pd.Series): processed Series of values for phone number conversion.

    """

    not_null_map = column.notna()
    data_numeric = pd.to_numeric(column, errors="coerce").astype(np.float64)  # convert to numeric
    if not isinstance(data_numeric, pd.Series):
        raise TypeError(f"Expected pandas.Series. Received: {type(data_numeric)}.")
    data_numeric = data_numeric.astype(float)

    int_map = pd.Series(False, index=column.index, dtype=bool)  # create empty mapping for integers
    allowed_chars_map = int_map.copy()  # create empty mapping for allowed characters

    int_map[not_null_map] = data_numeric.loc[not_null_map.index].apply(float.is_integer)
    not_numeric_not_null = data_numeric.isnull() & not_null_map
    allowed_chars_map[not_numeric_not_null] = validated_column_to_column(
        column[not_numeric_not_null], lambda x: set(x).issubset(set("0123456789()-. +"))
    )

    # phones with + sign or leading zero get them removed during pd.to_numeric, e.g. +4912345678 -> 4912345678,
    # so we need to add the original string back to the data
    leading_zero_map = column.astype(str).str.startswith(("0", "+")).astype("boolean").fillna(False)
    int_no_leading_zero_map = int_map & ~leading_zero_map

    data_strings = column.copy()
    # get rid of trailing .0
    data_strings[int_no_leading_zero_map] = data_numeric[int_no_leading_zero_map].astype(np.int64).astype(str)

    # select strings that are not floats and not null and have only allowed characters
    mask: pd.Series = (int_map | allowed_chars_map) & not_null_map
    data_strings = data_strings[mask].astype(str)
    if not isinstance(data_strings, pd.Series):
        raise TypeError(f"Expected a pandas.Series. Received: {type(data_strings)}.")

    return data_strings


def convert_string_to_phone(value: str, country: Optional[str]) -> Union[phone.PhoneNumber, float]:
    """The function to convert a string into a `phonenumbers.PhoneNumber` object.

    Use country = None to convert phone numbers represented in an international
    format. Use country = "US", "GB", "CA", etc. to convert phone numbers
    represented in a national format.

    Args:
        value (str): a string to convert.
        country (Optional[str]): represents the country that the value
            will be converted from.

    Returns:
        (Union[phone.PhoneNumber, float]): a `phonenumbers.PhoneNumber` object
            if the value is a valid phone number, otherwise np.nan.

    """

    try:
        parsed = phone.parse(value, country)
        return parsed if phone.is_valid_number(parsed) else np.nan
    except NumberParseException:  # phonenumbers library parse exception
        return np.nan


def convert_phone_number_column(column: pd.Series, country: Optional[str] = None) -> pd.Series:
    """The function to convert a phone number column into a Series of
    `phonenumbers.PhoneNumber` objects.

    Converts all phone numbers represented in an international format.
    Converts phone numbers represented in a national format only for the
        given country, e.g. "US", "GB", "CA", etc.
    All other values are converted to `np.nan`.

    Args:
        column (pd.Series): a column of phone numbers.
        country (Optional[str]): represents the country that all values in
            a national format will be converted from. If None, all values in
            any national format will be converted to np.nan.
            Default is None.

    Returns:
        (pd.Series): The converted column with the converted `PhoneNumber` objects.

    """

    # if the column is empty
    if (column_shape := column.shape)[0] == 0:
        return column

    # -------------------------------------- Prepare data -------------------------------------- #

    # save original index and reset index
    orig_index = column.index
    column = column.reset_index(drop=True)

    column = validated_column_to_column(column, special_nan_to_nan)  # convert special nan strings to np.nan
    data_strings = get_phone_strings(column)  # get strings to parse

    # -------------------------------------- Convert data -------------------------------------- #

    phones = np.empty(column_shape, dtype=object)  # create empty array for phone.PhoneNumbers
    phones.fill(np.nan)  # fill with nan values

    # convert phone numbers from international format
    not_converted_indexes: list = []  # remember indexes of not converted values to convert from national format
    for value, indexes in data_strings.groupby(data_strings).groups.items():
        converted_value = convert_string_to_phone(str(value), None)

        if isinstance(converted_value, phone.PhoneNumber):
            phones[indexes] = converted_value  # update the array of converted values
        else:
            not_converted_indexes.extend(indexes)  # update indexes of not converted values

    # early return if country is None
    if country is None:
        return pd.Series(phones, index=orig_index, name=column.name)

    # convert phone numbers from national format only for the given country
    data_strings = data_strings.loc[not_converted_indexes]

    for value, indexes in data_strings.groupby(data_strings).groups.items():
        converted_value = convert_string_to_phone(value, country)
        if isinstance(converted_value, phone.PhoneNumber):
            phones[indexes] = converted_value  # update the array of converted values

    # --------------------------------------- Return data --------------------------------------- #

    return pd.Series(phones, index=orig_index, name=column.name)
