from typing import Sequence, Callable, Any, TypeVar, Union, Optional

import pandas as pd
import numpy as np
import numpy.typing as npt

from evoml_utils.metrics.scorers.implementations import TimedContextScorer
from evoml_utils.metrics.scorers.context import BuildContext


PredScorer = Callable[[pd.Series, pd.Series], float]
"""Scorer which requires predicted targets.

Args:

    y_true (Sequence): 
        array-like of shape (n_samples,) containing true target values.

    y_pred (Sequence):
        array-like of shape (n_samples,) containing predictions for each example.

Returns:

    score (float):
        the evaluated score.

"""


PredProbaScorer = Callable[[pd.Series, pd.DataFrame], float]
"""Scorer which requires predicted probabilities.

Args:

    y_true (Sequence[int]): 
        array-like of shape (n_samples,) containing true class labels

    y_pred_proba (Sequence[float]):
        array-like of shape (n_samples, n_classes) containing predicted probabilities for each class.

Returns:

    score (float):
        the evaluated score.

"""


ExplainabilityScorer = Callable[[Any, int], float]
"""Scorer which examines a model to determine its explainability score.

Args:

    model (MetaModel): the model to be examined.

    n_features (int): the number of features in the data.

Returns:

    score (float):
        the evaluated explainability score.


"""

CustomRegScorer = Callable[
    [
        pd.Series,
        pd.Series,
        Optional[pd.DataFrame],
    ],
    float,
]
"""Custom regression scorer.

Args:

    y_true (Sequence[float]):
        array-like of shape (n_samples,) containing true target values.

    y_pred (Sequence[float]):
        array-like of shape (n_samples,) containing predictions for each example.

    X (pd.DataFrame):
        original data, array of mixed types depending on the features

Returns:

    score (float):
        the evaluated score.

"""

CustomClassScorer = Callable[
    [
        pd.Series,
        pd.Series,
        Optional[pd.DataFrame],
        Optional[pd.DataFrame],
    ],
    float,
]
"""Custom classification scorer.

Args:

    y_true (Sequence[int]):
        array-like of shape (n_samples,) containing true target values.

    y_pred (Sequence[int]):
        array-like of shape (n_samples,) containing predictions for each example.

    y_pred_proba (Sequence[float]):
        array-like of shape (n_samples, n_classes) containing predicted probabilities for each class.

    X (pd.DataFrame):
        original data, array of mixed types depending on the features

Returns:

    score (float):
        the evaluated score.

"""

CustomForecastScorer = Callable[
    [
        pd.Series,
        pd.Series,
        pd.DataFrame,
    ],
    float,
]
"""Custom forecasting scorer.

Args:

    y_true (Sequence[float]):
        array-like of shape (n_samples,) containing true target values.

    y_pred (Sequence[float]):
        array-like of shape (n_samples,) containing predictions for each example.

    X (pd.DataFrame):
        original data, array of mixed types depending on the features

Returns:

    score (float):
        the evaluated score.

"""

Scorer = Union[
    PredScorer,
    PredProbaScorer,
    ExplainabilityScorer,
    TimedContextScorer,
    CustomClassScorer,
    CustomRegScorer,
    CustomForecastScorer,
]
ScorerT = TypeVar("ScorerT", bound=Scorer)
ScorerBuilder = Callable[[BuildContext], ScorerT]
