"""Module providing utils code for users to create scorers/metrics."""

# ───────────────────────────────── Imports ────────────────────────────────── #
# Standard Library
import time
from typing import Union, List, Sequence, Optional

# 3rd Party
import numpy as np
import numpy.typing as npt
import pandas as pd
import sklearn.metrics
import logging
from scipy import stats

# Private
# @pyright: cannot find MetaModel type because of nuitka compilation
from metaml.meta_models import MetaModel  # type: ignore
from evoml_api_models import MlTask
from evoml_utils.data import explainability_scoring


# ───────────────────────────────── Code ────────────────────────────────── #

logger = logging.getLogger("evoml-explain")


class ScorerContextError(Exception):
    pass


def explainability_scorer(estimator: MetaModel, num_features: int, mltask: MlTask) -> float:
    """
    This function calculates an explainability value on how easy it is to understand the estimator in use.
    Args:
        estimator (MetaML):
            Machine learning model
            Task, e.g. classification, regression, etc.
        num_features (int):
            Dataset to calculate explainability for
        mltask (MlTask):
            Type of mltask of the estimator
    Returns:
        explainability_score (float):
            An explainability co-efficient.
    """
    # TODO: 1. Change it to a 5 star rating system,
    #       2. Remove y from functions arguments,
    #       3. Change mltask argument to something meaningful without default value,
    #       4. Return explainability_dict["justification"] and use in the front end
    (
        interpretability,
        expressiveness,
        consistency,
        space_complexity,
        numerical_stability,
        justification,
    ) = explainability_scoring.explainability_score(model=estimator, num_features=num_features, mltask=mltask)
    score = interpretability + expressiveness + consistency + space_complexity + numerical_stability
    return float(score / 5.0)


def corr_coef_score(y_true: Union[List, np.ndarray], y_predict: Union[List, np.ndarray]) -> float:
    """This function calculates a Pearson correlation coefficient.

    Args:
        y_true (Union[List, np.ndarray]):
            Target variable.
        y_predict (Union[List, np.ndarray]):
            Predicted target variable.
    Returns:
        score (float):
            A Pearson correlation coefficient - a number between -1 and +1 that indicates how strongly two variables
            (continuous) are linearly related.
    """

    return stats.pearsonr(y_true, y_predict)[0]


def spearmanr_score(y_true: npt.NDArray[np.floating], y_predict: npt.NDArray[np.floating]) -> float:
    """This function calculates a Spearman correlation coefficient.

    Args:
        y_true (Union[List, np.ndarray]):
            Target variable.
        y_predict (Union[List, np.ndarray]):
            Predicted target variable.
    Returns:
        score (float):
            A Spearman correlation coefficient - a number between -1 and +1 that assesses monotonic relationships
            (whether linear or not).
    """
    # @pyright: cannot recognise input or return types of stats.spearmanr
    return stats.spearmanr(y_true, y_predict).correlation  # type: ignore


def mean_absolute_percentage_error(y_true: npt.NDArray[np.floating], y_predict: npt.NDArray[np.floating]) -> np.float64:
    """This function calculates the mean absolute percentage error. It is a measure of prediction accuracy.
    Args:
        y_true:
            Target variable (test).
        y_predict:
            Predicted target variable.
    Returns:
        score:
            Mean absolute percentage error.
    """
    y_true_array: npt.NDArray[np.float64] = np.array(y_true, dtype=np.float64)
    y_predict_array: npt.NDArray[np.float64] = np.array(y_predict, dtype=np.float64)
    # Prevent division by 0
    y_true_array[y_true_array == 0] = 10**-6
    return np.mean(np.abs((y_true_array - y_predict_array) / y_true_array))


def weighted_mean_absolute_percentage_error(
    y_true: npt.NDArray[np.floating], y_predict: npt.NDArray[np.floating]
) -> np.float64:
    """This function calculates the weighted mean absolute percentage error. Here, the errors are weighted by values of
    the actuals.
    Args:
        y_true:
            Target variable (test).
        y_predict:
            Predicted target variable.
    Returns:
        score:
            Mean absolute percentage error.
    """

    y_true_array: npt.NDArray[np.float64] = np.array(y_true, dtype=np.float64)
    y_predict_array: npt.NDArray[np.float64] = np.array(y_predict, dtype=np.float64)
    # Prevent division by 0
    y_true_array[y_true_array == 0] = 10**-6
    return np.mean(np.abs(y_true_array - y_predict_array)) / np.mean(np.abs(y_true_array)) * 100


def symmetric_mean_absolute_percentage_error(
    y_true: npt.NDArray[np.floating], y_predict: npt.NDArray[np.floating]
) -> np.float64:
    """This function calculates the symmetric mean absolute percentage error.
    Args:
        y_true:
            Target variable (test).
        y_predict:
            Predicted target variable.
    Returns:
        score:
            Mean absolute percentage error.
    """

    y_true_array: npt.NDArray[np.float64] = np.array(y_true, dtype=np.float64)
    y_predict_array: npt.NDArray[np.float64] = np.array(y_predict, dtype=np.float64)
    # Prevent division by 0
    y_true_array[y_true_array == 0] = 10**-6
    return 200 * np.mean(np.abs(y_true_array - y_predict_array) / (np.abs(y_true_array) + np.abs(y_predict_array)))


def mean_absolute_scaled_error(
    y_true: npt.NDArray[np.floating], y_predict: npt.NDArray[np.floating], y_train: npt.NDArray[np.floating], m: int
) -> Union[np.float64, float]:
    """This function calculates the mean absolute scaled error.
    Args:
        y_true:
            Target variable (test).
        y_predict:
            Predicted target variable.
        y_train:
            Target variable (train).
        m:
            Seasonal period.
    Returns:
        score:
            Mean absolute percentage error.
    """

    y_true_array: npt.NDArray[np.float64] = np.array(y_true, dtype=np.float64)
    y_predict_array: npt.NDArray[np.float64] = np.array(y_predict, dtype=np.float64)
    y_train_array: npt.NDArray[np.float64] = np.array(y_train, dtype=np.float64)
    # Mean absolute error of naive seasonal prediction
    y_pred_naive = y_train_array[:-m]
    mae_naive = np.mean(np.abs(y_train_array[m:] - y_pred_naive))
    # Mean absolute scaled error
    if mae_naive == 0:
        return np.nan
    else:
        return np.mean(np.abs(y_true_array - y_predict_array)) / mae_naive


def roc_auc_score(
    y_true: pd.Series,
    y_pred_proba: pd.DataFrame,
    labels: Optional[Sequence[int]] = None,
) -> float:
    """Wrapper around sklearn.metrics.roc_auc_score due to incompatibility with binary classification.

    Args:

        y_true (Union[np.ndarray, pd.Series]): array-like of shape (n_samples,) containing class labels.

        y_pred_proba (pd.DataFrame): array-like of shape (n_samples, n_classes).

        labels (Optional[Sequence[int]]): array-like of shape (n_classes,) containing a list of all class labels.

    Returns:

        ROC AUC score (float): the area under the receiver operator curve.

    """
    if y_pred_proba.shape[1] == 2:
        return float(sklearn.metrics.roc_auc_score(y_true, y_pred_proba.iloc[:, 1]))
    if y_pred_proba.shape[1] > 2:
        return float(
            sklearn.metrics.roc_auc_score(y_true, y_pred_proba, labels=labels, multi_class="ovo", average="macro")
        )
    raise ValueError(f"y_pred_proba should have at least two columns. Found: {y_pred_proba.shape[1]}.")


class TimedContextScorer:
    """Scorer used for measuring the execution time of a block of code via a
    context manager

    An example usage would be:

    ```
    scorer = TimeBasedScorer()

    with scorer:
        do_something()

    time_to_do_something = scorer()
    ```

    """

    _start_time: Optional[float]
    _finish_time: Optional[float]

    def __init__(self, normalisation_factor: Optional[float] = None) -> None:
        self._start_time = None
        self._finish_time = None
        self._normalisation_factor = normalisation_factor

    def __enter__(self):
        self._start_time = time.perf_counter()

    def __exit__(self, *exc_details):
        self._finish_time = time.perf_counter()

    def __call__(self):
        if self._start_time is None:
            raise ScorerContextError("scorer called before context initialised")
        if self._finish_time is None:
            raise ScorerContextError("scorer called before context exited")

        if self._normalisation_factor is None:
            return self._finish_time - self._start_time
        else:
            return (self._finish_time - self._start_time) * self._normalisation_factor
