import pandas as pd
import numpy as np


from pydantic import BaseModel
from typing import List, Tuple


from evoml_utils.splitting.config_model import FitEvalSplitConfig, ValidationMethod
from evoml_utils.splitting import generate_cv
from evoml_utils.splitting.exceptions import DataSplittingException, TooManyWindowsException
from evoml_utils.splitting.data_split import FitEvalSplit


class FitEvalSplitWindow(BaseModel):
    """The information defining a window which splits the data into fitting and evaluation sets."""

    fit_start: int
    fit_length: int
    eval_length: int
    is_validation: bool


def get_fit_eval_window_splits(split_config: FitEvalSplitConfig) -> Tuple[List[FitEvalSplit], List[FitEvalSplit]]:
    """Obtain the indices of the windows which divide the data into fitting and evaluation sets.

    Args:
        split_config (FitEvalSplitConfig):
            The parameters defining how to perform the fitting and evaluation split.

    Returns:
        val_splits, test_splits (List[FitEvalSplit], List[FitEvalSplit]):
            Lists of FitEvalSplits for both validation and testing.

    """

    if split_config.validation_method_options.method not in [
        ValidationMethod.expanding_window,
        ValidationMethod.sliding_window,
        ValidationMethod.forecast_holdout,
    ]:
        raise DataSplittingException(f"Unsupported splitting method: {split_config.validation_method_options.method}.")

    if split_config.len_train is None:
        raise Exception(
            "FitEvalSplitConfig.len_train must be set when getting the fitting and evaluation window splits."
        )

    if split_config.len_test is None:
        raise Exception(
            "FitEvalSplitConfig.len_test must be set when getting the fitting and evaluation window splits."
        )

    # Obtain splits used for validation.
    split_config.validation = True
    cv_val = generate_cv(split_config)

    indices_train = np.arange(split_config.len_train)
    X_train = pd.DataFrame(indices_train[:, np.newaxis])
    y_train = pd.Series(indices_train)
    val_splits = cv_val.split(X_train, y_train)

    # Obtain splits used for testing.
    split_config.validation = False
    cv_test = generate_cv(split_config)

    indices_combined = np.arange(split_config.len_train + split_config.len_test)
    X_combined = pd.DataFrame(indices_combined[:, np.newaxis])
    y_combined = pd.Series(indices_combined)
    test_splits = cv_test.split(X_combined, y_combined)

    return val_splits, test_splits


def convert_fit_eval_split_to_window(split: FitEvalSplit, is_validation: bool) -> FitEvalSplitWindow:
    """Return a `FitEvalSplitWindow` based on the supplied FitEvalSplit."""

    if split.eval_indices[0] != split.fit_indices[-1] + 1:
        raise DataSplittingException("The evaluation window must follow immediately after the fitting window.")

    return FitEvalSplitWindow(
        fit_start=split.fit_indices[0],
        fit_length=split.fit_indices[-1] + 1 - split.fit_indices[0],
        eval_length=split.eval_indices[-1] + 1 - split.eval_indices[0],
        is_validation=is_validation,
    )


def get_fit_eval_windows(split_config: FitEvalSplitConfig) -> List[FitEvalSplitWindow]:
    """Obtain the windows which divide the data into fitting and evaluation sets."""

    if split_config.validation_method_options.method not in [
        ValidationMethod.expanding_window,
        ValidationMethod.sliding_window,
        ValidationMethod.forecast_holdout,
    ]:
        raise DataSplittingException(f"Unsupported splitting method: {split_config.validation_method_options.method}.")

    val_window_splits, test_window_splits = get_fit_eval_window_splits(split_config)

    # Obtain windows for validation.
    val_window_list = [convert_fit_eval_split_to_window(split=split, is_validation=True) for split in val_window_splits]

    # Obtain windows for testing.
    test_window_list = [
        convert_fit_eval_split_to_window(split=split, is_validation=False) for split in test_window_splits
    ]

    combined_window_list = val_window_list + test_window_list

    """If the number of requested windows crosses a threshold we raise an exception,
     since the trial would be too slow."""
    MAX_WINDOWS = 15
    if len(combined_window_list) > MAX_WINDOWS:
        raise TooManyWindowsException()

    return combined_window_list
