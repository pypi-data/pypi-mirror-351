from typing import Optional, Any, List


import pandas as pd
import numpy as np
import numpy.typing as npt

# @mypy: can't find sktime types
import sktime.forecasting.model_selection  # type: ignore
from sktime.split import ExpandingWindowSplitter as _ExpandingWindowSplitter


from evoml_utils.splitting.exceptions import InsufficientWindowsException
from evoml_utils.splitting.data_split import FitEvalSplit
from .base import BaseSplitter


class ExpandingWindowSplitter(BaseSplitter):
    """Splits a dataset into fitting and evaluation indices using the expanding window method.

    Args:
        horizon (int): the length of a forecast i.e. the length of each test window.
        initial_fitting_window_length (int): the length of the training data in the first split.
        expansion_length (Optional[int]): the length by which to expand the training window.
        gap (int): the length of the gap between the end of the training data and the start of the testing data.
        partial (bool): whether to truncate the last test window when it crosses the end of the data.
    """

    fh: List[int]
    window_length: int

    def __init__(
        self,
        horizon: int,
        initial_fitting_window_length: int,
        expansion_length: Optional[int] = None,
        gap: int = 0,
        partial: bool = False,
    ):
        self.fh: List[int] = list(range(gap + 1, gap + 1 + horizon))
        self.horizon = horizon
        self.partial = partial

        if expansion_length is None:
            expansion_length = horizon

        self._splitter = _ExpandingWindowSplitter(
            fh=self.fh, initial_window=initial_fitting_window_length, step_length=expansion_length
        )

    def split(self, X: pd.DataFrame, y: Optional[Any] = None) -> List[FitEvalSplit]:  # type: ignore
        """Generate indices to split data into training and test set.

        Args:
            X (pd.DataFrame): data to be split
            y: always ignored, exists for compatibility

        Returns:
            List[FitEvalSplit]

        """
        if self.partial:
            if self.window_length + self.fh[0] > len(X):
                raise InsufficientWindowsException()
        elif self.window_length + self.fh[-1] > len(X):
            raise InsufficientWindowsException()

        if self.partial:
            index = np.arange(len(X) + self.horizon - 1)
        else:
            index = np.arange(len(X))

        indices: List[npt.NDArray[int], npt.NDArray[int]] = list(self._splitter.split(index))  # type: ignore

        return [
            FitEvalSplit(fit_indices=train.tolist(), eval_indices=test[test < len(X)].tolist(), index=idx + 1)
            for idx, (train, test) in enumerate(indices)
        ]

    @property
    def step_length(self) -> int:
        return self._splitter.step_length

    @property
    def window_length(self) -> int:
        return self._splitter.window_length
