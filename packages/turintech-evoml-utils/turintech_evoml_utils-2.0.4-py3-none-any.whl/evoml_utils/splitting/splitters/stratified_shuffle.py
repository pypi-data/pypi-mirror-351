import pandas as pd

# @mypy: cannot find stubs
from sklearn.model_selection import StratifiedShuffleSplit  # type: ignore
from typing import Optional, List, Any


from .base import BaseSplitter
from evoml_utils.splitting.data_split import FitEvalSplit


class StratifiedShuffleSplitter(BaseSplitter):
    def __init__(self, test_size: float, n_splits: int, random_state: int):
        """
        Splits the dataset into fitting and evaluation indices using the stratified shuffle split method.

        Args:
            test_size (float): fraction of the dataset to use for testing.
            n_splits (int): number of folds into which to divide the dataset.
            random_state (int): random seed.
        """
        self._splitter = StratifiedShuffleSplit(test_size=test_size, n_splits=n_splits, random_state=random_state)

    def split(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> List[FitEvalSplit]:
        """Generate indices to split data into training and test set.

        Args:
            X (pd.DataFrame): data to be split
            y: always ignored, exists for compatibility

        Returns:
            List[FitEvalSplit]

        """
        return [
            FitEvalSplit(fit_indices=fit_indices.tolist(), eval_indices=eval_indices.tolist(), index=idx + 1)
            for idx, (fit_indices, eval_indices) in enumerate(self._splitter.split(X=X, y=y))
        ]
