from typing import Optional
import logging
import pandas as pd


from metaml.meta_models import MetaModel


from evoml_utils.metrics.metrics import (
    Metric,
    PredMetric,
    PredProbaMetric,
    ExplainabilityMetric,
    CustomRegressionMetric,
    CustomClassificationMetric,
    CustomForecastingMetric,
)


logger = logging.getLogger("evoml-utils")


class InsufficientInformationException(Exception):
    """Raised when we don't have sufficient information to evaluate a metric."""

    pass


def evaluate_metric(
    metric: Metric,
    y_true: Optional[pd.Series] = None,
    y_pred: Optional[pd.Series] = None,
    y_pred_proba: Optional[pd.DataFrame] = None,
    model: Optional[MetaModel] = None,
    num_features: Optional[int] = None,
    X: Optional[pd.DataFrame] = None,
) -> Optional[float]:
    """Called by evoml to evaluate a single metric.

    This function handles the logic of determining which inputs are expected
    for a given metric type.

    Args:
        metric:
            The class of the metric to be evaluated.
        y_true:
            Array of shape (n_samples,). True values for the target.
        y_pred:
            Array of shape (n_samples,). Predicted values for the target.
        y_pred_proba:
            Array of shape (n_samples, n_classes). Predicted probabilities for
            the target.
        model:
            The model to be evaluated.
        num_features:
            The number of features of the preprocessed dataset.
        X:
            Array of shape (n_samples, n_features). The original dataset.
            Used for custom loss functions where the user may want to use
            information from the original dataset e.g. the user wishes to use
            domain knowledge to create a custom loss function based on one or
            more of the features of the original dataset.

    Returns:
        The score of the metric, or None if the metric could not be evaluated.
    """
    # If we have a PredMetric then we check if we have y_true and y_pred before evaluation.
    if isinstance(metric, PredMetric):
        if (y_true is not None) and (y_pred is not None):
            return metric.scorer(y_true, y_pred)
        raise InsufficientInformationException("Insufficient information to evaluate a PredMetric.")

    # If we have a PredProbaMetric then we check if we have y_true and y_pred_proba before evaluation.
    if isinstance(metric, PredProbaMetric):
        if (y_true is not None) and (y_pred_proba is not None):
            return metric.scorer(y_true, y_pred_proba)
        raise InsufficientInformationException("Insufficient information to evaluate a PredProbaMetric.")

    # If we have an ExplainabilityMetric then we check if we have model and num_features before evaluation.
    if isinstance(metric, ExplainabilityMetric):
        if (model is not None) and (num_features is not None):
            return metric.scorer(model, num_features)
        raise InsufficientInformationException("Insufficient information to evaluate an ExplainabilityMetric.")

    # If we have an CustomRegressionMetric then we check if we have y_true, y_pred and X before evaluation.
    if isinstance(metric, CustomRegressionMetric):
        if (y_true is not None) and (y_pred is not None) and (X is not None):
            return metric.scorer(y_true, y_pred, X)
        raise InsufficientInformationException("Insufficient information to evaluate a CustomRegressionMetric.")

    # If we have an CustomClassificationMetric then we check if we have y_true, y_pred, y_pred_proba and X before
    # evaluation.
    if isinstance(metric, CustomClassificationMetric):
        if (y_true is not None) and (y_pred is not None) and (X is not None):
            return metric.scorer(y_true, y_pred, y_pred_proba, X)
        raise InsufficientInformationException("Insufficient information to evaluate a CustomClassificationMetric.")

    # If we have a CustomForecastingMetric then we check if we have y_true, y_pred and X before evaluation.
    if isinstance(metric, CustomForecastingMetric):
        if (y_true is not None) and (y_pred is not None) and (X is not None):
            return metric.scorer(y_true, y_pred, X)
        raise InsufficientInformationException("Insufficient information to evaluate a CustomForecastingMetric.")

    raise NotImplementedError(f"Unsupported metric: {metric}.")
