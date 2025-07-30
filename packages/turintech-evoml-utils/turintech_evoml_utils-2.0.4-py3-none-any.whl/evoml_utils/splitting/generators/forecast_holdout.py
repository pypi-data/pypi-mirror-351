from evoml_utils.splitting.splitters import HoldoutSplitter
from evoml_utils.splitting.config_model import FitEvalSplitConfig


def generate_forecast_holdout_splitter(config: FitEvalSplitConfig) -> HoldoutSplitter:
    """

    Args:
        config (FitEvalSplitConfig): config to specify options for splitting.

    Returns:
        HoldoutSplitter

    """
    forecast_holdout_options = config.validation_method_options.forecastHoldoutOptions
    if forecast_holdout_options is None:
        raise ValueError("The forecast holdout options must be set when generating a forecast holdout splitter.")
    return HoldoutSplitter(holdout_size=forecast_holdout_options.size, shuffle=False)
