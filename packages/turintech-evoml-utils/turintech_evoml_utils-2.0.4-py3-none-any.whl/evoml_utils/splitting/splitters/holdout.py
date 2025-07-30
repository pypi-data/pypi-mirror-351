import numpy as np
import pandas as pd
from typing import Optional, List, Any

# @mpy: cannot find stubs
from sklearn.model_selection import train_test_split  # type: ignore


from evoml_utils.splitting.exceptions import DataSplittingException
from .base import BaseSplitter
from evoml_utils.splitting.data_split import FitEvalSplit


class HoldoutSplitter(BaseSplitter):
    """Cross-validator to produce a holdout split.

    Args:
        shuffle (bool): whether to shuffle the data
        random_state (int): seed for shuffling the data
        holdout_size (float): fraction of data to be used for testing
        stratify (bool): whether to perform a stratified split which ensures classes are equally represented in
            training and testing splits
    """

    def __init__(self, shuffle: bool = True, random_state: int = 0, holdout_size: float = 0.2, stratify: bool = False):
        self.shuffle = shuffle
        self.random_state = random_state
        self.holdout_size = holdout_size
        self.stratify = stratify

    def split(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> List[FitEvalSplit]:
        """Generate indices to split data into training and test set.

        Args:
            X (pd.DataFrame): data to be split
            y (Optional[pd.Series]): class labels used to perform a stratified split
        """
        stratification_labels = None
        if self.stratify:
            if y is None:
                raise DataSplittingException("y must be supplied in order to provide a stratified split.")

            stratification_labels = y
        input_indices = np.arange(len(X))
        train, test = train_test_split(
            input_indices,
            test_size=self.holdout_size,
            shuffle=self.shuffle,
            random_state=self.random_state,
            stratify=stratification_labels,
        )

        if not isinstance(train, np.ndarray) or not isinstance(test, np.ndarray):
            raise TypeError("The returned train and test indexes must be numpy arrays.")

        return [FitEvalSplit(fit_indices=train.tolist(), eval_indices=test.tolist(), index=1)]
