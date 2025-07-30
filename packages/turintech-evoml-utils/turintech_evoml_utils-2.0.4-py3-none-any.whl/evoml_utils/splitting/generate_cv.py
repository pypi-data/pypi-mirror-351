# ────────────────────────────────── Imports ───────────────────────────────── #
# Private
# @mypy: doesn't recognise types evoml_api_models types because of nuitka compilation
from evoml_api_models import MlTask  # type: ignore
from evoml_utils.splitting.generators import (
    generate_expanding_window_splitter,
    generate_holdout_splitter,
    generate_cross_validation_splitter,
    generate_sliding_window_splitter,
    generate_forecast_holdout_splitter,
)
from evoml_utils.splitting.config_model import FitEvalSplitConfig, ValidationMethod
from evoml_utils.splitting.splitters.base import BaseSplitter

# ──────────────────────────────────────────────────────────────────────────── #


def generate_cv(config: FitEvalSplitConfig) -> BaseSplitter:
    """Generate a cross-validator (cv) from the parameters contained in a given FitEvalSplitConfig.
    Args:
        config (FitEvalSplitConfig): the parameters defining the method used to split the data.
    Returns:
        BaseSplitter: a splitter which can be used to divide the data into fitting and evaluation sets.
    """

    # Find out if we are dealing with a time series.
    is_time_series = config.is_time_series or config.ml_task == MlTask.forecasting

    # Check we have an expected MlTask.
    if config.ml_task not in [MlTask.regression, MlTask.classification, MlTask.forecasting]:
        raise NotImplementedError(f"Unsupported ML task: {config.ml_task}")

    # Check that we are only using sliding or expanding window validation for time series.
    if (
        config.validation_method_options.method in [ValidationMethod.sliding_window, ValidationMethod.expanding_window]
        and not is_time_series
    ):
        raise ValueError(
            f"Invalid validation method for non timeseries tasks: {config.validation_method_options.method}"
        )

    # Prevent usage of k-fold cross validation for time series tasks.
    if config.validation_method_options.method == ValidationMethod.cross_validation and is_time_series:
        raise ValueError(f"Invalid validation method for timeseries tasks: {config.validation_method_options.method}")

    # Generate splitters.
    if config.validation_method_options.method == ValidationMethod.sliding_window:
        return generate_sliding_window_splitter(config=config)
    if config.validation_method_options.method == ValidationMethod.expanding_window:
        return generate_expanding_window_splitter(config=config)
    if config.validation_method_options.method == ValidationMethod.holdout:
        return generate_holdout_splitter(config=config)
    if config.validation_method_options.method == ValidationMethod.cross_validation:
        return generate_cross_validation_splitter(config=config)
    if config.validation_method_options.method == ValidationMethod.forecast_holdout:
        return generate_forecast_holdout_splitter(config=config)

    raise NotImplementedError(f"Unsupported validation method: {config.validation_method_options.method}")
