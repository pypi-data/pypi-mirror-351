from evoml_utils.splitting.config_model import FitEvalSplitConfig
from evoml_utils.splitting.splitters import ExpandingWindowSplitter


def generate_expanding_window_splitter(config: FitEvalSplitConfig) -> ExpandingWindowSplitter:
    """

    Args:
        config (FitEvalSplitConfig): config to specify options for splitting.

    Returns:
        ExpandingWindowSplitter

    """

    expanding_window_options = config.validation_method_options.expandingWindowOptions

    if expanding_window_options is None:
        raise ValueError("The expanding window options should be set when generating an expanding window splitter.")
    if expanding_window_options.horizon is None:
        raise ValueError("The horizon should be set when generating an expanding window splitter.")
    if config.len_train is None:
        raise ValueError("The gap should be set when generating an expanding window splitter.")

    # During the tuning phase of a trial the initial fitting window length should be as specified by the user.
    # During testing we use the entire training set minus the gap for fitting.
    if config.validation:
        if expanding_window_options.initialTrainWindowLength is None:
            raise ValueError(
                "The initial window length should be set when generating an expanding window splitter for validation."
            )
        initial_fitting_window_length = expanding_window_options.initialTrainWindowLength
    else:
        initial_fitting_window_length = config.len_train - expanding_window_options.gap

    return ExpandingWindowSplitter(
        horizon=expanding_window_options.horizon,
        initial_fitting_window_length=initial_fitting_window_length,
        expansion_length=expanding_window_options.expansionLength,
        gap=expanding_window_options.gap,
    )
