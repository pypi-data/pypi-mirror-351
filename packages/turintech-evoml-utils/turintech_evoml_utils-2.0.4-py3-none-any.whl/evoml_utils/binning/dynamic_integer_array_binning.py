"""This module implements a dynamic programming-based binning algorithm for integer arrays."""

# ───────────────────────────────── Imports ────────────────────────────────── #
# Standard Library
from typing import Optional

# 3rd Party
import numpy as np
import numpy.typing as npt

# Dependencies
from evoml_utils.binning.binning import Binning

# ─────────────────────────────────── Code ─────────────────────────────────── #


class DynamicIntegerArrayBinning(Binning):
    """This class implements a binning algorithm for integer arrays using
    a dynamic programming algorithm.

    The binning that retains the largest amount of information about the original
    ranks of the data is the binning that results in the (discrete) uniform
    distribution, as the uniform distribution is the maximum entropy distribution
    for a variable on a finite domain.

    The class utilises the dynamic programming algorithm to find the binning.
    The algorithm is guaranteed to find the optimal binning.

    Notes:
        `evoml-utils.binning also proves a KmeansIntegerArrayBinning class,
        which uses a KMeans algorithm to find the binning. Since the dynamic
        programming algorithm scales poorly with the number of unique values
        in the array, it is not recommended for arrays with more than
        10_000 unique values.

        Thus, the KMeansIntegerArrayBinning class is recommended for arrays
        with more than 10_000 unique values. While DynamicIntegerArrayBinning
        is recommended for arrays with less than 10_000 unique values.

        This class requires the array to be sorted.

        The methods of this class are deterministic, and the results are reproducible.
        This class is able to handle negative and non-consecutive.
            For example, np.array([-2, -1, 0, 2  2, 4, 4, 5, 5, 5, 6, 6, 8]).

    Examples:
        >>> from evoml_utils.binning import DynamicIntegerArrayBinning
        >>> X, n_bins = np.array([0, 0, 0, 2, 2, 4, 4, 5, 5, 5, 6, 6, 8]), 3
        >>> iab = DynamicIntegerArrayBinning(n_bins)
        >>> labels = iab.fit_transform(X)
        >>> expected = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2])
        >>> np.array_equal(labels, expected)
        True

    References:
        The dynamic programming solution is based on the following article:
        Shortest path with exactly k edges in a directed and weighted graph
        URL: https://www.geeksforgeeks.org/shortest-path-with-exactly-k-edges-
            in-a-directed-and-weighted-graph-set-2/?ref=rp

    """

    def __init__(self, n_bins: int = 5):
        # setup
        self.n_bins = n_bins

        # attributes to be set during fit
        self._label_mapping: Optional[dict] = None  # store mapping of labels
        self._fit_bins_counts: Optional[tuple] = None  # store counts of bins to significantly speed up fit_transform

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit the model on an array of integers and return the labels.

        Args:
            X (np.ndarray): array of integers to be binned. Must be sorted.

        Returns:
            labels (np.ndarray): array of binned integers.

        Raises:
            TypeError: if the array is not of integer type.

        """

        self.fit(X)
        if self._fit_bins_counts is None:
            raise ValueError("Model has not been fitted properly.")
        return np.repeat(np.arange(self.n_bins), self._fit_bins_counts)

    def fit(self, X: np.ndarray):
        """Fit the model on an array of integers.

        This function saves the information for the transform and
        fit_transform functions. Specifically, it saves the mapping of
        labels for the transform function. It also saves the counts of
        bins for the fit_transform function to significantly speed up
        fit_transform.

        Requires the array to be sorted.

        Args:
            X (np.ndarray): array of integers to be binned. Must be sorted.

        Raises:
            TypeError: if the array is not of integer type.

        """

        if not np.issubdtype(X.dtype, np.integer):
            raise TypeError("Array must be of integer type.")

        _, counts = np.unique(X, return_counts=True)
        res_counts = self._dynamic_programming_search(counts, self.n_bins)
        labels = np.repeat(np.arange(self.n_bins), res_counts)

        # remember for transform function
        self._label_mapping = dict(zip(X, labels))

        # remember for fit_transform function to significantly speed up fit_transform
        self._fit_bins_counts = res_counts

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform an array of integers using information
        obtained during fit. Able to handle unseen data.

        Does not require the array to be sorted.

        Args:
            X (np.ndarray): array of integers to be binned.

        Returns:
            labels (np.ndarray): array of binned integers.

        Raises:
            ValueError: if the model was not fitted prior.
            TypeError: if the array is not of integer type.

        """

        if not np.issubdtype(X.dtype, np.integer):
            raise TypeError("Array must be of integer type.")

        if self._label_mapping is None:
            raise ValueError("Model not fitted.")

        labels: npt.NDArray[np.integer] = np.empty(X.shape, dtype=int)  # initialise empty array of labels

        # get the indices of the values that are not in the fit dictionary
        dict_keys_as_array = np.fromiter(self._label_mapping.keys(), dtype=X.dtype)
        idx = np.where(np.isin(X, dict_keys_as_array, invert=True))

        # create a mask of the values that are not in the fit dictionary
        mask: npt.NDArray[np.bool_] = np.ones(X.size, dtype=bool)
        mask[idx] = False
        # replace values seen in fit with the corresponding label
        labels[mask] = self._vectorised_mapping(X[mask], self._label_mapping)

        # replace values not seen in fit with the closest values seen in fit
        closest_values = self._get_closest(X[idx], dict_keys_as_array)
        labels[idx] = self._vectorised_mapping(closest_values, self._label_mapping)

        return labels

    @staticmethod
    def _vectorised_mapping(arr_, my_dict):
        """Vectorised mapping of values in arr_ to values in my_dict."""
        return np.vectorize(my_dict.__getitem__, otypes=[int])(arr_)

    @staticmethod
    def _get_closest(values, arr_):
        """Get the closest value in arr_ for each value in values."""
        idxs = np.searchsorted(arr_, values, side="left")  # get insert positions

        # find indexes where previous index is closer
        prev_idx_is_less = (idxs == arr_.shape[0]) | (
            np.fabs(values - arr_[np.maximum(idxs - 1, 0)])
            < np.fabs(values - arr_[np.minimum(idxs, arr_.shape[0] - 1)])
        )

        idxs[prev_idx_is_less] -= 1

        return arr_[idxs]

    @staticmethod
    def _entropy(x):
        return x * np.log2(x)

    def _dynamic_programming_search(self, counts: np.ndarray, n_bins: int):
        """Dynamic programming solution for the search of optimal binning
        for a given array, maximising entropy.

        Notes:
            The maximisation function used is the following:
                sum_i m_k log (m_k) as it is equivalent to maximising the entropy,

        Args:
            counts (np.ndarray): An array of value counts.
            n_bins (int): The number of bins to return.

        Returns:
            (tuple): A tuple of numbers of elements in each bin.

        Raises:
            ValueError: if n_bins is greater than the number of values in the array.

        """

        # edge cases
        if n_bins == 1 and len(counts) >= 1:
            return [(len(counts),)], self._entropy(counts.sum())

        if n_bins > len(counts):
            raise ValueError("n_bins must be less than or equal to the number of values in the array.")

        N = len(counts)
        # If T(n, b) is the optimally binning the first n values into b bins, we need to compute T(N, n_bins)
        # we will use the recurrence:
        # T(n, b) = \min_{k>0} \{ f( cumsum[n] - cumsum[n-k] ) + T(n-k, b-1) }, and k_min determines the optimal split
        # we keep an array for the values T(b, b), ..., T(b, N - n_bins + b) in each iteration
        # initialise with the values for b = 1
        cum_sums = np.cumsum(counts)
        opt_vals = self._entropy(cum_sums[: -n_bins + 1])
        opt_splits = [(cum_sums[i],) for i in range(N - n_bins + 1)]  # number of elements in each bin

        # iteratively update the optimal values and splits for higher number of bins b = 2, ..., n_bins
        for b in range(2, n_bins + 1):
            new_vals = np.zeros(N - n_bins + 1)
            new_splits = []

            for n in range(b, N - n_bins + b + 1):  # binning the first n values into b bins
                # candidates for the optimal value
                candidates = self._entropy(cum_sums[n - 1] - cum_sums[b - 2 : n - 1]) + opt_vals[: n - b + 1]
                # candidates += z
                # get max and argmax
                i_opt = np.argmin(candidates)
                new_vals[n - b] = candidates[i_opt]
                # store the optimal split
                new_splits.append(opt_splits[i_opt] + (cum_sums[n - 1] - cum_sums[b - 2 + i_opt],))
            # update metrics
            # @mypy: Expression has type "List[Tuple[Any, Any]]", variable has type "List[Tuple[Any]]")
            opt_splits = new_splits  # type: ignore
            opt_vals = new_vals

        return opt_splits[-1]
