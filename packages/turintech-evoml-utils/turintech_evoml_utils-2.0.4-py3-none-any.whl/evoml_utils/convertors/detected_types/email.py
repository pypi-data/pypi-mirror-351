from typing import Optional


import pandas as pd
from email_validator import validate_email, ValidatedEmail


from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column


def to_email(value: Optional[str]) -> Optional[ValidatedEmail]:
    """
    Checks if value is a string in a valid email format and returns a ValidatedEmail object if this is true.
    Otherwise, it returns None.

    Args:
        value:
            Can be string or nan.
    Returns:
        Optional[ValidatedEmail]:
            A ValidatedEmail object as it is returned by the email-validator library.
    """

    if not isinstance(value, str):
        return None
    try:  # validate_email raises an exception for invalid strings
        email_obj = validate_email(value, check_deliverability=False)
        return email_obj
    except:
        return None


def to_email_objs_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of strings to a column of the corresponding ValidatedEmail objects. Any invalid
    value is converted to None.

    Args:
        column:
            The input column is pandas.Series format.
    Returns:
        pd.Series:
            The converted column consisting of ValidatedEmail objects and None values.
    """

    return validated_column_to_column(column, to_email)
