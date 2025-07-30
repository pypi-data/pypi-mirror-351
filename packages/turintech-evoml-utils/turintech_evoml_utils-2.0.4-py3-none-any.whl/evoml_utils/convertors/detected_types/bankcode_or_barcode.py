from typing import Optional, Union, Any


import pandas as pd
from stdnum import iban, bic, ean, isbn  # type: ignore
from pycountry import countries


from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column


def to_barcode_or_bankcode(value: Optional[Union[float, int, str]], code_type: str) -> Optional[Any]:
    """
    Checks if value is a valid input for the given format, which can be ISBN, IBAN, EAN, and BIC.
    If it is true, returns a compact format of value as it is returned by stdnum. If
    the input is not valid, it returns None.

    Args:
        value:
            Can be string or numeric.
        code_type:
            Can be ISBN/ IBAN/ EAN/ BIC.
    Returns:
            A string representing a valid string for the given format formatted by stdnum library or None.
    """

    if not isinstance(value, (float, int, str)):
        return None

    convert_functions = {
        "BIC": bic.validate,
        "IBAN": iban.validate,
        "ISBN": isbn.validate,
        "EAN": ean.validate,
    }

    try:
        if isinstance(value, float):
            value = int(value)
        string_value = str(value)  # convert value to string
        if code_type == "ISBN":
            string_value = string_value.lstrip("ISBN")
        convert_function = convert_functions[code_type]
        validated_string = convert_function(string_value)
        # check that we have a valid country code in cases of IBAN and BIC
        if code_type in ["IBAN", "BIC"]:
            if code_type == "IBAN":
                country_code = validated_string[:2]
            else:
                country_code = validated_string[4:6]
            country_info = countries.get(alpha_2=country_code)
            if country_info is None:  # not valid country code
                return None
        return validated_string
    except:
        return None


def to_bankcode_or_barcode_column(column: pd.Series, code_type: str) -> pd.Series:
    """
    Converts all valid values of column for the given format to the corresponding string values and all non-valid
    values of column to None.

    Args:
        column:
            Input column in pandas.Series format.
        code_type:
            String representing a bankcode or barcode format. It can be EAN, ISBN, IBAN, BIC.
    Returns:
        (pd.Series): The converted column of bankcode or barcode values
    """
    return validated_column_to_column(column, lambda x: to_barcode_or_bankcode(x, code_type))
