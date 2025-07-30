"""This module implements a kmeans-based binning algorithm for integer arrays."""

# ───────────────────────────────── Imports ────────────────────────────────── #
# Standard Library
from typing import Optional

# 3rd Party
import numpy as np
from sklearn.cluster import KMeans

# Dependencies
from evoml_utils.binning.binning import Binning

# ─────────────────────────────────── Code ─────────────────────────────────── #


class KmeansIntegerArrayBinning(Binning):
    """This class implements a binning algorithm for integer arrays using
    KMeans clustering algorithm from `sklearn`.

    The binning that retains the largest amount of information about the original
    ranks of the data is the binning that results in the (discrete) uniform
    distribution, as the uniform distribution is the maximum entropy distribution
    for a variable on a finite domain.

    The class utilises the KMeans algorithm from `sklearn` to find the binning.
    The KMeans algorithm is a heuristic algorithm, and is not guaranteed to
    find the optimal binning. Thus, the binning is only an approximation
    of the optimal binning.

    Notes:
        `evoml-utils.binning` also proves a DynamicIntegerArrayBinning class,
        which uses a dynamic programming algorithm to find the optimal binning.
        However, the dynamic programming algorithm scales poorly with the number
        of unique values in the array, and is not recommended for arrays with
        more than 10_000 unique values.

        Thus, the KMeansIntegerArrayBinning class is recommended for arrays
        with more than 10_000 unique values. While DynamicIntegerArrayBinning
        is recommended for arrays with less than 10_000 unique values.

        KMeans binning method is affected by outliers, and is not recommended
        if the data differs in scale.
            For example, np.array([0, 2, 2, 4, 4, 5, 6, 8, 1000]).
        However, OridinalEncoder can be used to solve this problem.

        The methods of this class are deterministic, and the results are reproducible.
        This class is able to handle negative, non-consecutive,
        and non-sorted integer arrays.
            For example, np.array([4, -1, 0, 5, 2, 8, 6, -2, 4, 5, 5, 2, 6]).

    Examples:
        >>> from evoml_utils.binning import KmeansIntegerArrayBinning
        >>> X, n_bins = np.array([0, 0, 0, 2, 2, 4, 4, 5, 5, 5, 6, 6, 8]), 3
        >>> iab = KmeansIntegerArrayBinning(n_bins)
        >>> labels = iab.fit_transform(X)
        >>> expected = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2])
        >>> np.array_equal(labels, expected)
        True

    References:
        The KMeans algorithm:
        https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html

    """

    def __init__(self, n_bins: int = 5):
        # setup
        self.n_bins = n_bins

        # attributes to be set during fit
        self._kmeans: Optional[KMeans] = None  # store model for transform function
        self._label_mapping: Optional[np.ndarray] = None  # store mapping of labels

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit the model on an array of integers and return the labels.

        Args:
            X (np.ndarray): array of integers to be binned.

        Returns:
            labels (np.ndarray): array of binned integers.

        Raises:
            TypeError: If the array is not of integer type.

        """

        return self.fit(X).transform(X)

    def fit(self, X: np.ndarray):
        """Fit the model on an array of integers.

        This function saves the kmeans model and the mapping of labels
        of the kmeans model in ascending order of their mean.

        Args:
            X (np.ndarray): array of integers to be binned.

        Returns:
            self

        Raises:
            TypeError: If the array is not of integer type.

        """

        if not np.issubdtype(X.dtype, np.integer):
            raise TypeError("Array must be of integer type.")

        km = KMeans(n_clusters=self.n_bins, random_state=42)
        km.fit_transform(X.reshape(-1, 1))

        # relabel the bins in ascending order of their mean
        idx = np.argsort(km.cluster_centers_.sum(axis=1))
        label_mapping = np.zeros_like(idx)
        label_mapping[idx] = np.arange(self.n_bins)

        # remember for transform function
        self._kmeans = km
        self._label_mapping = label_mapping

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform an array of integers using information
        obtained during fit. Able to handle unseen data.

        Args:
            X (np.ndarray): array of integers to be binned.

        Returns:
            labels (np.ndarray): array of binned integers.

        Raises:
            ValueError: If the binning method is unknown.
            TypeError: If the array is not of integer type.

        """

        if not np.issubdtype(X.dtype, np.integer):
            raise TypeError("Array must be of integer type.")

        if self._kmeans is None:
            raise ValueError("Model not fitted.")

        if self._label_mapping is None:
            raise ValueError("Label mapping is not initialized.")

        labels = self._kmeans.predict(X.reshape(-1, 1))
        labels = self._label_mapping[labels]

        return labels
