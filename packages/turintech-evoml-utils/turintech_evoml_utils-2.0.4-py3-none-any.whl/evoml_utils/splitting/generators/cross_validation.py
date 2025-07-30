from typing import Union, Optional


# @mypy: doesn't recognise types evoml_api_models types because of nuitka compilation
from evoml_api_models import MlTask  # type: ignore


from evoml_utils.splitting.config_model import FitEvalSplitConfig
from evoml_utils.splitting.splitters import KFoldSplitter, StratifiedKFoldSplitter


def generate_cross_validation_splitter(
    config: FitEvalSplitConfig, random_state: Optional[int] = None
) -> Union[KFoldSplitter, StratifiedKFoldSplitter]:
    """

    Args:
        config (FitEvalSplitConfig): config to specify options for splitting.
        random_state (int): random seed.

    Returns:
        Union[KFoldSplitter, StratifiedKFoldSplitter]

    """
    cross_validation_options = config.validation_method_options.crossValidationOptions

    if cross_validation_options is None:
        raise Exception("The cross validation options should be set when generating a cross validation splitter.")

    # Whether to shuffle the data.
    shuffle = not cross_validation_options.keepOrder
    # Random seed.
    random_state = random_state if shuffle else None

    # Perform a stratified split for classification tasks.
    if config.ml_task == MlTask.classification:
        return StratifiedKFoldSplitter(
            n_splits=cross_validation_options.folds, shuffle=shuffle, random_state=random_state
        )

    return KFoldSplitter(
        n_splits=cross_validation_options.folds,
        shuffle=not cross_validation_options.keepOrder,
        random_state=random_state,
    )
