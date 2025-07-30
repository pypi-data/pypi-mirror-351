from evoml_utils.splitting.splitters import SlidingWindowSplitter
from evoml_utils.splitting.config_model import FitEvalSplitConfig


def generate_sliding_window_splitter(config: FitEvalSplitConfig) -> SlidingWindowSplitter:
    options = config.validation_method_options.slidingWindowOptions
    if options is None:
        raise ValueError("The splitting options must be specified when generating a sliding window splitter.")
    if options.horizon is None:
        raise ValueError("The horizon must be specified when generating a sliding window splitter.")
    if options.trainWindowLength is None:
        raise Exception("The train window length must be set when generating a sliding window splitter.")
    if options.slideLength is None:
        raise ValueError("The slide length must be set when generating a sliding window splitter.")
    if options.gap is None:
        raise ValueError("The gap must be set when generating a sliding window window splitter.")

    # During the tuning stage of a trial we allow the splitter to choose where to place the first test window.
    # During testing we place the first test window at the end of the training set.
    first_test_window_start = None if config.validation else config.len_train

    return SlidingWindowSplitter(
        horizon=options.horizon,
        train_window_length=options.trainWindowLength,
        slide_length=options.slideLength,
        gap=options.gap,
        first_test_window_start=first_test_window_start,
    )
