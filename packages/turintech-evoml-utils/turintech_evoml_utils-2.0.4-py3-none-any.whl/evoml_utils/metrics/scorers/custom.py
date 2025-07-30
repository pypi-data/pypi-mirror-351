"""Module providing utils code for users to input custom score functions and create
scorers."""

# ───────────────────────────────── Imports ────────────────────────────────── #

# Standard Library
import threading
from functools import wraps
from enum import Enum
from typing import Dict, List, Callable, TypeVar, Optional, Union, Tuple

# 3rd Party
import numpy as np
import pandas as pd
import sklearn
import scipy

# Private
from evoml_utils.metrics.scorers.templates import CustomClassScorer, CustomRegScorer, CustomForecastScorer

# ───────────────────────────────── Code ────────────────────────────────── #

# Extra Types
T = TypeVar("T")
OList = Optional[List[T]]


ALLOWED_LOCAL_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "divmod": divmod,
    "float": float,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "object": object,
    "pow": pow,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
    "Tuple": Tuple,
    "Union": Union,
    "Optional": Optional,
    "Dict": Dict,
    "List": List,
    "None": None,
}

ALLOWED_LOCAL_MODULES = {"np": np, "pd": pd, "sklearn": sklearn, "scipy": scipy}


class ScorerName(str, Enum):
    """Enum class to store the names of the scorer functions."""

    CLASS_SCORER = "custom_class_scorer_template"
    REG_SCORER = "custom_reg_scorer_template"
    FORECAST_SCORER = "custom_forecast_scorer_template"


def parse_source_code(
    source_code: str, scorer_name: ScorerName
) -> Union[CustomClassScorer, CustomRegScorer, CustomForecastScorer]:
    """
    This functions gets code in string form and obtains the functions defined by components_to_extract.

    Args:
        source_code:
            Custom scorer (as a string).
        scorer_name:
            A list of strings that contain the name(s) of the scorer function.
    Returns:
        Union[CustomClassScorer, CustomRegScorer]:
            Dictionary of function name associated with custom scorer (as a function).
    """

    if not isinstance(source_code, str):
        raise TypeError("Custom scorer must be in string format.")
    if not isinstance(scorer_name, ScorerName):
        raise TypeError("Components to extract must be a choice in `ScorerName`")

    allowed_globals: dict = {
        **ALLOWED_LOCAL_BUILTINS,
        **ALLOWED_LOCAL_MODULES,
        scorer_name.value: None,
        "__builtins__": None,
    }

    # Run custom_scorer i.e. add to context map
    exec(source_code, allowed_globals)

    if allowed_globals[scorer_name.value] is None:
        raise ValueError(f"Custom scorer {scorer_name.value} not found in source code.")

    # Obtain required custom scorer as a function
    return allowed_globals[scorer_name.value]


def timelimit_scorer(function: Callable, time_limit: float):
    """
    This functions acts as a decorator - it adds a timeout to the input function.

    Args:
        function:
            Custom scorer (as a function).
        time_limit:
            Time limit of code execution.
    Returns:
        A function that will raise a TimeoutError if it runs longer than `time_limit` seconds.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        # mutable objects to store results and exceptions
        result = [None]
        exception = [None]

        def run_func():
            try:
                result[0] = function(*args, **kwargs)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=run_func)
        thread.start()
        thread.join(time_limit)

        if thread.is_alive():
            # If the thread is still alive, the function is taking too long
            raise TimeoutError(f"Timed out after {time_limit} seconds")
        if exception[0]:
            raise exception[0]

        return result[0]

    return wrapper


def decoded_target_scorer(custom_scorer_template: CustomClassScorer, label_mappings: List[str]) -> CustomClassScorer:
    """Wrapper function to decode target labels.

    Args:
        custom_scorer_template:
            Classification (assumed) custom scorer (as a function).
        label_mappings:
            List of label mappings.

    Returns:
        Callable[[pd.Series, pd.Series, pd.DataFrame, pd.DataFrame], float]:
            Decoded target scorer.
    """

    def decode_target(
        y_true: pd.Series, y_pred: pd.Series, y_pred_proba: Optional[pd.DataFrame], *args, **kwargs
    ) -> float:
        y_true = y_true.map(dict(enumerate(label_mappings)))
        y_pred = y_pred.map(dict(enumerate(label_mappings)))
        if y_pred_proba is not None:
            y_pred_proba.rename(dict(enumerate(label_mappings)))

        return custom_scorer_template(y_true, y_pred, y_pred_proba, *args, **kwargs)

    return decode_target
