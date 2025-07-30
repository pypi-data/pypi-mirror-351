from typing import Optional, Any, List


import numpy as np
import pandas as pd


from sktime.split import SlidingWindowSplitter as _SlidingWindowSplitter


from evoml_utils.splitting.exceptions import InsufficientWindowsException, DataSplittingException
from evoml_utils.splitting.data_split import FitEvalSplit
from .base import BaseSplitter


class SlidingWindowSplitter(BaseSplitter):  # type: ignore
    """Splits a dataset into fitting and evaluation indices using the sliding window method.

    Args:
        horizon (int): the length of a forecast i.e. the length of each test window
        train_window_length (int): the length of the training data in each split
        slide_length (Optional[int]): the length by which to shift the sliding window
        gap (int): the length of the gap between the end of the training data and the start of the testing data
        first_test_window_start (Optional[int]): the index at which to place the test window in the first split
        partial (bool): whether to truncate the last test window when it crosses the end of the data
    """

    fh: List[int]
    first_window_train_start: int
    window_length: int

    def __init__(
        self,
        horizon: int,
        train_window_length: int,
        slide_length: Optional[int] = None,
        gap: int = 0,
        first_test_window_start: Optional[int] = None,
        partial: bool = False,
    ):
        self.horizon = horizon
        self.partial = partial

        if slide_length is None:
            slide_length = horizon

        if first_test_window_start is None:
            self.first_train_window_start = 0
        else:
            self.first_train_window_start = first_test_window_start - gap - train_window_length

        if self.first_train_window_start < 0:
            raise DataSplittingException(
                f"The first training window must start at an index greater than zero. "
                f"Instead found: {self.first_train_window_start}."
            )

        self.fh: List[int] = list(range(gap + 1, gap + 1 + horizon))

        self._splitter = _SlidingWindowSplitter(fh=self.fh, window_length=train_window_length, step_length=slide_length)

    # @pyright: this method overrides `split` from `BasePlitter` in an incompatible manner. In future composition is better than inheritance.
    def split(self, X: pd.DataFrame, y: Optional[Any] = None) -> List[FitEvalSplit]:  # type: ignore
        """Generate indices to split data into training and test set.

        Args:
            X (pd.DataFrame): data to be split
            y: always ignored, exists for compatibility
        """
        if self.partial:
            if self.first_train_window_start + self.window_length + self.fh[0] > len(X):
                raise InsufficientWindowsException()
        elif self.first_train_window_start + self.window_length + self.fh[-1] > len(X):
            raise InsufficientWindowsException()
        if self.partial:
            index = np.arange(len(X) + self.horizon - 1 - self.first_train_window_start)
        else:
            index = np.arange(len(X) - self.first_train_window_start)

        indices: List[Tuple[npt.NDArray[int], npt.NDArray[int]]] = list(self._splitter.split(index))
        shifted_indices = [
            (train + self.first_train_window_start, test + self.first_train_window_start) for train, test in indices
        ]

        return [
            FitEvalSplit(fit_indices=train.tolist(), eval_indices=test[test < len(X)].tolist(), index=idx + 1)
            for idx, (train, test) in enumerate(shifted_indices)
        ]

    @property
    def window_length(self) -> int:
        return self._splitter.window_length
