from typing import Any, Optional


import numpy as np


SPECIAL_NAN_STRINGS = {
    "null",
    "na",
    "n/a",
    "#na",
    "#n/a",
    "#n/a n/a",
    "1.#ind",
    "-1.#ind",
    "nan",
    "-nan",
    "1.#qnan",
    "-1.#qnan",
    "?",
    ".",
    "inf",
    "-inf",
    "none",
    "<space>",
    "<blank>",
    "-",
    " ",
    "  ",
}


def special_nan_to_nan(value: Optional[str]) -> Any:
    """
    Converts a special string nan value to np.nan. If a value not in
    special nan strings is given, the output is equal to the input.

    Args:
        value (Optional[str]): It can be numeric or string.

    Returns:
        np.nan if value is a special nan string else value itself.
    """

    return np.nan if value in SPECIAL_NAN_STRINGS else value
