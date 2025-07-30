from itertools import chain
from typing import Callable, Generic, Optional, Set

from evoml_api_models import MlTask

from evoml_utils.metrics.scorers.custom import (
    ScorerName,
    decoded_target_scorer,
    parse_source_code,
    timelimit_scorer,
)
from evoml_utils.metrics.scorers.templates import (
    BuildContext,
    CustomClassScorer,
    CustomForecastScorer,
    CustomRegScorer,
    ExplainabilityScorer,
    PredProbaScorer,
    PredScorer,
    Scorer,
    ScorerT,
    TimedContextScorer,
)
from evoml_utils.metrics.specifications import (
    Direction,
    ExplainabilityMetricSpec,
    MeasurementContext,
    MetricSpecBase,
    PredMetricSpec,
    PredProbaMetricSpec,
    TimedContextMetricSpec,
)


class Metric(Generic[ScorerT]):
    """Main interface to manipulate metrics"""

    # Instance Attributes
    scorer: ScorerT

    def __init__(
        self,
        slug: str,
        direction: Direction,
        scorer_builder: Callable[[BuildContext], ScorerT],
        context: Optional[BuildContext] = None,
    ):
        self.slug = slug
        self.direction = direction

        context = context or BuildContext()
        self.scorer = scorer_builder(context)

    def __eq__(self, __o: object) -> bool:
        """Equality method required for a metric to be put into a set. Currently
        equality is determined by comparing the slugs. We also error out if the
        directions don't match (since they should) as a sanity check.
        """
        if not isinstance(__o, Metric):
            return False
        if __o.slug == self.slug:
            assert __o.direction == self.direction  # sanity check, directions should be the same
            return True
        else:
            return False

    def __hash__(self) -> int:
        return hash(self.slug)

    @classmethod
    def from_spec(cls, spec: MetricSpecBase, context: Optional[BuildContext] = None):
        """Construct a Metric from a MetricSpecBase object."""
        if isinstance(spec, PredMetricSpec):
            # @mypy: cannot resolve this error without moving from Callable to protocols or callable classes
            return PredMetric(slug=str(spec), direction=spec.direction, scorer_builder=spec.builder, context=context)  # type: ignore
        elif isinstance(spec, PredProbaMetricSpec):
            return PredProbaMetric(
                slug=str(spec), direction=spec.direction, scorer_builder=spec.builder, context=context  # type: ignore
            )
        # @mypy: cannot resolve this error without moving from Callable to protocols or callable classes
        elif isinstance(spec, ExplainabilityMetricSpec):
            return ExplainabilityMetric(
                slug=str(spec), direction=spec.direction, scorer_builder=spec.builder, context=context  # type: ignore
            )
        # @mypy: cannot resolve this error without moving from Callable to protocols or callable classes
        elif isinstance(spec, TimedContextMetricSpec):
            if spec.time_context is None:
                raise ValueError("The time context must be specified when creating a TimeContextMetricSpec.")
            return TimedContextMetric(
                slug=str(spec),
                direction=spec.direction,
                scorer_builder=spec.builder,  # type: ignore
                context=context,
                time_context=spec.time_context,
            )
        raise Exception(f"Unsupported metric spec for the Metric.from_spec method: {spec}.")


class PredMetric(Metric[PredScorer]): ...


class PredProbaMetric(Metric[PredProbaScorer]): ...


class ExplainabilityMetric(Metric[ExplainabilityScorer]): ...


class TimedContextMetric(Metric[TimedContextScorer]):
    def __init__(
        self,
        slug: str,
        direction: Direction,
        scorer_builder: Callable[[BuildContext], TimedContextScorer],
        time_context: MeasurementContext,
        context: Optional[BuildContext] = None,
    ):
        self.time_context = time_context
        super().__init__(slug=slug, direction=direction, scorer_builder=scorer_builder, context=context)


class CustomClassificationMetric(Metric[CustomClassScorer]):
    @staticmethod
    def _create_custom_builder(code: str) -> Callable[[BuildContext], CustomClassScorer]:
        """create a custom scorer builder from its code"""

        def _custom_builder(context: BuildContext) -> CustomClassScorer:
            if context.ml_task != MlTask.classification:
                raise ValueError(f"Incorrect task type for a CustomClassificationMetric: {context.ml_task}.")
            custom_scorer = parse_source_code(code, ScorerName.CLASS_SCORER)
            custom_scorer_decoded_inputs = decoded_target_scorer(custom_scorer, context.label_mappings)  # type: ignore
            custom_scorer_template = custom_scorer_decoded_inputs

            if custom_scorer_template is None:
                raise ValueError("Scorer template not provided")
            if not callable(custom_scorer_template):
                raise TypeError("Scorer template is not a function.")

            return custom_scorer_template

        return _custom_builder


class CustomRegressionMetric(Metric[CustomRegScorer]):
    @staticmethod
    def _create_custom_builder(code: str) -> Callable[[BuildContext], CustomRegScorer]:
        """create a custom scorer builder from its code"""

        def _custom_builder(context: BuildContext) -> CustomRegScorer:
            if context.ml_task != MlTask.regression:
                raise ValueError(f"Incorrect task type for a CustomRegressionMetric: {context.ml_task}.")
            custom_scorer_template = parse_source_code(code, ScorerName.REG_SCORER)

            if custom_scorer_template is None:
                raise ValueError("Scorer template not provided")
            if not callable(custom_scorer_template):
                raise TypeError("Scorer template is not a function.")

            # @pyright: doesn't recognise the narrowing of types and we can't add an assertion until replacing the custom scorer type hints with protocols or callable classes
            return custom_scorer_template  # type: ignore

        return _custom_builder


class CustomForecastingMetric(Metric[CustomForecastScorer]):
    @staticmethod
    def _create_custom_builder(code: str) -> Callable[[BuildContext], CustomForecastScorer]:
        """create a custom scorer builder from its code"""

        def _custom_builder(context: BuildContext) -> CustomForecastScorer:
            if context.ml_task != MlTask.forecasting:
                raise ValueError(f"Incorrect task type for a CustomForecastingMetric: {context.ml_task}.")
            custom_scorer_template = parse_source_code(code, ScorerName.FORECAST_SCORER)

            if custom_scorer_template is None:
                raise ValueError("Scorer template not provided")
            if not callable(custom_scorer_template):
                raise TypeError("Scorer template is not a function.")

            # @pyright: doesn't recognise the narrowing of types and we can't add an assertion until replacing the custom scorer type hints with protocols or callable classes
            return custom_scorer_template  # type: ignore

        return _custom_builder


def build_metrics(ml_task: MlTask, build_context: Optional[BuildContext] = None) -> Set[Metric]:
    """Helper function to build all known metrics for a specific ML Task."""
    if build_context is None:
        build_context = BuildContext(ml_task=ml_task)
    pred_metrics = (m for m in PredMetricSpec if ml_task.value in m.value)
    pred_proba_metrics = (m for m in PredProbaMetricSpec if ml_task.value in m.value)

    explainability_metrics = (m for m in ExplainabilityMetricSpec if ml_task.value in m.value)

    time_based_metrics = (m for m in TimedContextMetricSpec if ml_task.value in m.value)

    return {
        Metric.from_spec(spec=m, context=build_context)
        for m in chain(pred_metrics, pred_proba_metrics, explainability_metrics, time_based_metrics)
    }


__all__ = [
    "Metric",
    "BuildContext",
    "PredMetric",
    "PredProbaMetric",
    "ExplainabilityMetric",
    "TimedContextMetric",
    "CustomClassificationMetric",
    "CustomRegressionMetric",
    "CustomForecastingMetric",
]
