"""This module implements the BaseBinning class for all custom binning algorithms."""

# ───────────────────────────────── Imports ────────────────────────────────── #
# Standard Library
from abc import ABC, abstractmethod

# 3rd Party
import numpy as np

# ─────────────────────────────────── Code ─────────────────────────────────── #


class Binning(ABC):
    """Abstract class for all custom binning algorithms.

    Requires the following methods to be implemented :
        - fit
        - transform
        - fit_transform

    """

    @abstractmethod
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """fit_transform function. Bin an array of integers.

        Args:
            X (np.ndarray): array of integers to be binned.

        Returns:
            (np.ndarray): array of binned integers.

        Raises:
            TypeError: If the array is not of integer type.

        """
        raise NotImplementedError()

    @abstractmethod
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform an array of integers using information
        obtained during fit. Able to handle unseen data.

        Args:
            X (np.ndarray): array of integers to be binned.

        Returns:
            (np.ndarray): array of binned integers.

        Raises:
            TypeError: If the array is not of integer type.

        """
        raise NotImplementedError()

    @abstractmethod
    def fit(self, X: np.ndarray):
        """Fit the binning algorithm to the data.

        Args:
            X (np.ndarray): array of integers to be binned.

        Raises:
            TypeError: If the array is not of integer type.

        """
        raise NotImplementedError()
