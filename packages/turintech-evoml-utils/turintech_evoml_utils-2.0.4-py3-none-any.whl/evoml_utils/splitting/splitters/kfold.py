import pandas as pd
from typing import Optional, List, Any

# @mypy: cannot find sktime types
from sklearn.model_selection import KFold  # type: ignore


from .base import BaseSplitter
from evoml_utils.splitting.data_split import FitEvalSplit


class KFoldSplitter(BaseSplitter):
    def __init__(self, n_splits: int, shuffle: bool, random_state: Optional[int]):
        """
        Splits the dataset into fitting and evaluation indices using the k-fold method.

        Args:
            n_splits (int): number of folds into which to divide the dataset.
            shuffle (bool): whether to shuffle the data.
            random_state (Optional[int]): random seed.
        """
        self._splitter = KFold(n_splits=n_splits, shuffle=shuffle, random_state=random_state)

    def split(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> List[FitEvalSplit]:
        """Generate indices to split data into training and test set.

        Args:
            X (pd.DataFrame): data to be split
            y (Optional[pd.Series]): always ignored, exists for compatibility

        Returns:
            List[FitEvalSplit]

        """
        return [
            FitEvalSplit(fit_indices=fit_indices.tolist(), eval_indices=eval_indices.tolist(), index=idx + 1)
            for idx, (fit_indices, eval_indices) in enumerate(self._splitter.split(X=X, y=y))
        ]
