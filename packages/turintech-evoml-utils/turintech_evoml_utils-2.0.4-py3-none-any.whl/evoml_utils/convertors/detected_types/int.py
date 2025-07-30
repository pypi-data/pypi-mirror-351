import pandas as pd


from evoml_utils.convertors.detected_types.float import to_float_column


def to_int_column(column: pd.Series) -> pd.Series:
    """Confusingly named wrapper around to_float_column.
    TODO: rename this function.

    Args:
        column:
            The input column in pandas.Series format.
    Returns:
        pd.Series:
            The converted column with numeric values.
    """
    # If the column is of integer dtype then no conversion is needed
    if pd.api.types.is_integer_dtype(column):
        return column

    return to_float_column(column)
