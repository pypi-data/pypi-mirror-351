from typing import Union, Optional


from evoml_utils.splitting.splitters import HoldoutSplitter, StratifiedShuffleSplitter
from evoml_utils.splitting.config_model import FitEvalSplitConfig

# @mypy: doesn't recognise types evoml_api_models types because of nuitka compilation
from evoml_api_models import MlTask  # type: ignore


def generate_holdout_splitter(
    config: FitEvalSplitConfig, random_state: Optional[int] = None
) -> Union[HoldoutSplitter, StratifiedShuffleSplitter]:
    """

    Args:
        config (FitEvalSplitConfig): config to specify options for splitting.
        random_state (int): random seed.

    Returns:
        Union[HoldoutSplitter, StratifiedShuffleSplit]

    """
    if random_state is None:
        random_state = 0

    holdout_options = config.validation_method_options.holdoutOptions

    if holdout_options is None:
        raise Exception("The holdout splitting options must be specified when generating a holdout splitter.")
    if holdout_options.size is None:
        raise Exception("The size of the holdout set should be specified when generating a holdout splitter.")

    # Choose whether to keep the order of the dataset.
    keep_order = holdout_options.keepOrder or config.is_time_series

    # Return a stratified split for classification tasks.
    if config.ml_task == MlTask.classification and not keep_order:
        return StratifiedShuffleSplitter(test_size=holdout_options.size, n_splits=1, random_state=random_state)

    return HoldoutSplitter(holdout_size=holdout_options.size, shuffle=not keep_order, random_state=random_state)
