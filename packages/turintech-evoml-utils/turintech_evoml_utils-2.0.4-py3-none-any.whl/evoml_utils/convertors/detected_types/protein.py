import re
from typing import Any, Union


import numpy as np
import pandas as pd


# Amino acids + Sequence wild cards ("X","*",".") + Ambiguous aliases:
# B = D or N
# J = I or L
# Z = E or Q
PROTEIN_SEQUENCE_PATTERN = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYX*.BZJ]{2,}$")


def to_protein_sequence_column(column: pd.Series) -> pd.Series:
    """Converts a column of strings to a column containing only strings
    representing protein sequences by converting all strings not in a
    valid protein sequence format to np.nan.

    Notes:
        The protein sequence format is defined as a string of 20 possible
        characters. However, protein sequences can also contain non-standard
        characters like X * . B Z J. These characters are not currently
        supported by the regular expression but can be added in the future.

    References:
        https://web.mit.edu/meme_v4.11.4/share/doc/alphabets.html


    Args:
        column (pd.Series): A column of strings in pandas.Series format.

    Returns:
        pd.Series: A column containing strings representing protein
            sequences and/or nan values.

    """

    def protein_match(x: Any) -> Union[str, float]:
        """Returns a string if it matches the protein sequence pattern, otherwise returns nan."""
        if not isinstance(x, str):
            return np.nan
        if not PROTEIN_SEQUENCE_PATTERN.fullmatch(x):
            return np.nan
        return x

    # @pyright: doesn't recognise that applying protein_match to a series will give another series
    return column.apply(protein_match)  # type: ignore
