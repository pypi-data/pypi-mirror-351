import pandas as pd
from abc import ABC, abstractmethod
from typing import List, Any


from evoml_utils.splitting.data_split import FitEvalSplit


class BaseSplitter(ABC):
    """Interface for splitters."""

    @abstractmethod
    def split(self, X: pd.DataFrame, y: pd.Series) -> List[FitEvalSplit]:
        """
        Get lists of train and test indices.

        Args:
            X (pd.DataFrame): array of features of shape (n_samples, n_features).
            y (pd.Series): array of target values with shape (n_samples,)

        Returns:
            List[FitEvalSplit]: stores fitting and evaluation indices produced by the splitter.

        """
        ...
