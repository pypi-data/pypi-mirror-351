from typing import TypeVar, Optional
from functools import partial
from enum import Enum
from sklearn import metrics


from evoml_api_models import MlTask


from evoml_utils.metrics.scorers.templates import ScorerBuilder
import evoml_utils.metrics.scorers.implementations as scorer_implementations


class Direction(str, Enum):
    """Direction for optimization. Aliases `asc → MIN` & `desc → MAX`"""

    MIN = "min"
    MAX = "max"

    @classmethod
    def _missing_(cls, value: object):
        """Allow for aliasing of `asc → MIN` and `desc → MAX`"""
        if value == "asc":
            return cls.MIN
        if value == "desc":
            return cls.MAX
        return super()._missing_(value)


class MeasurementContext(str, Enum):
    """Context for a time-based metric. Gives a hint as when the context manager for the scorer should be used.

    FIT: scorer context should be used when fitting the model
    PREDICT: scorer context should be used making predictions
    """

    FIT = "fit"
    PREDICT = "predict"


class MetricSpecBase(str, Enum):
    """A metric specification (MetricSpec) is a class used to enumerate all
    known metrics. As such, a metric spec member has all the information
    required to constuct it's corresponding `Metric` instance (minus build
    context).

    Specifically, `MetricSpecBase` is the base class used for defining new
    metric specifications. It defines the boilerplate for converting an enum
    member defined with the dict

    {
      slug: str
      order: str ["min"/"max"]
      builder: ScorerBuilder
    }

    where

    slug: the unique identifier for the metric

    order: the direction for the metric

    builder: the function used to construct the scorer, which takes a valid
    `BuildContext` as it's sole argument. We opted for storing a builder rather
    than the actual scorer in the spec to defer any potential runtime cost of
    building the scorer to when we actually need to convert it into a `Metric`.
    """

    direction: Direction
    builder: ScorerBuilder
    ml_task: MlTask
    _value_: str
    time_context: Optional[MeasurementContext]

    def __new__(cls, metric_dict: dict):
        obj = str.__new__(cls, metric_dict["slug"])
        obj._value_ = metric_dict["slug"]
        obj.direction = metric_dict["order"]
        obj.builder = metric_dict["builder"]
        obj.ml_task = MlTask(metric_dict["slug"].split("-")[0])
        obj.time_context = metric_dict.get("time-context", None)
        return obj

    def __str__(self) -> str:
        return self._value_


class PredMetricSpec(MetricSpecBase):
    CLASSIFICATION_PRECISION = {
        "slug": "classification-precision",
        "order": "max",
        "builder": lambda c: (
            partial(metrics.precision_score, average="binary", pos_label=c.positive_y)
            if c.positive_y is not None
            else partial(metrics.precision_score, average="macro")
        ),
    }
    CLASSIFICATION_RECALL = {
        "slug": "classification-recall",
        "order": "max",
        "builder": lambda c: (
            partial(metrics.recall_score, average="binary", pos_label=c.positive_y)
            if c.positive_y is not None
            else partial(metrics.recall_score, average="macro")
        ),
    }
    CLASSIFICATION_F1 = {
        "slug": "classification-f1",
        "order": "max",
        "builder": lambda c: (
            partial(metrics.f1_score, average="binary", pos_label=c.positive_y)
            if c.positive_y is not None
            else partial(metrics.f1_score, average="macro")
        ),
    }
    CLASSIFICATION_ACCURACY = {
        "slug": "classification-accuracy",
        "order": "max",
        "builder": lambda c: metrics.accuracy_score,
    }
    CLASSIFICATION_MCC = {
        "slug": "classification-mcc",
        "order": "max",
        "builder": lambda c: metrics.matthews_corrcoef,
    }
    CLASSIFICATION_COHEN_KAPPA = {
        "slug": "classification-cohen-kappa",
        "order": "max",
        "builder": lambda c: metrics.cohen_kappa_score,
    }
    REGRESSION_MAE = {
        "slug": "regression-mae",
        "order": "min",
        "builder": lambda c: metrics.mean_absolute_error,
    }
    REGRESSION_MAPE = {
        "slug": "regression-mape",
        "order": "min",
        "builder": lambda c: scorer_implementations.mean_absolute_percentage_error,
    }
    REGRESSION_MSE = {
        "slug": "regression-mse",
        "order": "min",
        "builder": lambda c: partial(metrics.mean_squared_error, squared=False),
    }
    REGRESSION_R2 = {
        "slug": "regression-r2",
        "order": "max",
        "builder": lambda c: metrics.r2_score,
    }
    REGRESSION_PEARSON_COEF = {
        "slug": "regression-pearson-coef",
        "order": "max",
        "builder": lambda c: scorer_implementations.corr_coef_score,
    }
    REGRESSION_SPEARMAN_COEF = {
        "slug": "regression-spearman-coef",
        "order": "max",
        "builder": lambda c: scorer_implementations.spearmanr_score,
    }
    FORECASTING_MAE = {
        "slug": "forecasting-mae",
        "order": "min",
        "builder": lambda c: metrics.mean_absolute_error,
    }
    FORECASTING_MAPE = {
        "slug": "forecasting-mape",
        "order": "min",
        "builder": lambda c: scorer_implementations.mean_absolute_percentage_error,
    }
    FORECASTING_SMAPE = {
        "slug": "forecasting-smape",
        "order": "min",
        "builder": lambda c: scorer_implementations.symmetric_mean_absolute_percentage_error,
    }
    FORECASTING_WMAPE = {
        "slug": "forecasting-wmape",
        "order": "min",
        "builder": lambda c: scorer_implementations.weighted_mean_absolute_percentage_error,
    }
    FORECASTING_MSE = {
        "slug": "forecasting-mse",
        "order": "min",
        "builder": lambda c: partial(metrics.mean_squared_error, squared=False),
    }
    FORECASTING_R2 = {
        "slug": "forecasting-r2",
        "order": "max",
        "builder": lambda c: metrics.r2_score,
    }


class PredProbaMetricSpec(MetricSpecBase):
    CLASSIFICATION_LOG_LOSS = {
        "slug": "classification-log-loss",
        "order": "min",
        "builder": lambda c: partial(metrics.log_loss, labels=c.labels),
    }
    CLASSIFICATION_ROC = {
        "slug": "classification-roc",
        "order": "max",
        "builder": lambda c: partial(scorer_implementations.roc_auc_score, labels=c.labels),
    }


class ExplainabilityMetricSpec(MetricSpecBase):
    CLASSIFICATION_EXPLAINABILITY = {
        "slug": "classification-explainability",
        "order": "max",
        "builder": lambda c: partial(scorer_implementations.explainability_scorer, mltask=MlTask.classification),
    }
    REGRESSION_EXPLAINABILITY = {
        "slug": "regression-explainability",
        "order": "max",
        "builder": lambda c: partial(scorer_implementations.explainability_scorer, mltask=MlTask.regression),
    }
    FORECASTING_EXPLAINABILITY = {
        "slug": "forecasting-explainability",
        "order": "max",
        "builder": lambda c: partial(scorer_implementations.explainability_scorer, mltask=MlTask.forecasting),
    }


class TimedContextMetricSpec(MetricSpecBase):
    """Enum for all known metrics that measure time.

    Their scorers can be used as context managers in order to measure time of
    whatever is executed within said context, then the measurements can be
    obtained by calling the scorers after exiting said context.

    The scorers have signature:
    __call__(*args, **kwargs) -> Score

    where `Score` is normally a float.

    *args and **kwargs are ignored and are simply put there for convenience (so
     the scorer can be called in any scenario without having to worry about
     passing no arguments)

    An example usage of one such scorer would be:

    ```
    scorer = TimeBasedMetric.CLASSIFICATION_TRAINING_TIME.scorer

    with scorer:
       fit_some_model(...)

    training_time = scorer()
    ```

    """

    CLASSIFICATION_TRAINING_TIME = {
        "slug": "classification-training-time",
        "order": "min",
        "builder": lambda c: scorer_implementations.TimedContextScorer(normalisation_factor=c.normalisation_factor),
        "time-context": MeasurementContext.FIT,
    }

    REGRESSION_TRAINING_TIME = {
        "slug": "regression-training-time",
        "order": "min",
        "builder": lambda c: scorer_implementations.TimedContextScorer(normalisation_factor=c.normalisation_factor),
        "time-context": MeasurementContext.FIT,
    }

    FORECASTING_TRAINING_TIME = {
        "slug": "forecasting-training-time",
        "order": "min",
        "builder": lambda c: scorer_implementations.TimedContextScorer(normalisation_factor=c.normalisation_factor),
        "time-context": MeasurementContext.FIT,
    }

    CLASSIFICATION_PREDICTION_TIME = {
        "slug": "classification-prediction-time",
        "order": "min",
        "builder": lambda c: scorer_implementations.TimedContextScorer(normalisation_factor=c.normalisation_factor),
        "time-context": MeasurementContext.PREDICT,
    }

    REGRESSION_PREDICTION_TIME = {
        "slug": "regression-prediction-time",
        "order": "min",
        "builder": lambda c: scorer_implementations.TimedContextScorer(normalisation_factor=c.normalisation_factor),
        "time-context": MeasurementContext.PREDICT,
    }

    FORECASTING_PREDICTION_TIME = {
        "slug": "forecasting-prediction-time",
        "order": "min",
        "builder": lambda c: scorer_implementations.TimedContextScorer(normalisation_factor=c.normalisation_factor),
        "time-context": MeasurementContext.PREDICT,
    }


MetricSpecT = TypeVar("MetricSpecT", bound=MetricSpecBase)
