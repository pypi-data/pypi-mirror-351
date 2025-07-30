from typing import Tuple, Union, List, NamedTuple, Dict, Set
from itertools import groupby


import numpy as np
import pandas as pd


from evoml_utils.range import Range, RangeType
from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column
from evoml_utils.convertors.utils.special_nan_to_nan import special_nan_to_nan
from evoml_utils.convertors.special_categorical.patterns import SpecialCatRegExp


class RayGroup(NamedTuple):
    boundary: float
    group: List[Range]


def convert_special_categorical_column(column: pd.Series, threshold: Union[int, float] = 1) -> Tuple[bool, pd.Series]:
    """The function to convert a special categorical column into a Series of
    Range objects.

    These objects can represent either a number, a ray or an interval.
    To do that the function uses the regular expressions for special
    categorical cases, specifically those that can be found in the
    SpecialCatRegExp Enumerator class.

    Notes:
        We consider cases like "above 50" to indicate (50, inf). We catch
        cases like "inclusively, above 50", "above 50 including",
        and ">=50" indicating [50, inf).

        String values that the regular expressions were not able to parse
        are converted to np.nan.

        To speed up the function and save up memory, identical inputs
        yield identical Range objects, that is, having the same ids.

        For example:

        >>> column_ = pd.Series(["above 40", "above 40"])
        >>> _, column_ = convert_special_categorical_column(column_)
        >>> isinstance(column_.iloc[0], Range) and isinstance(column_.iloc[1], Range)
        True
        >>> column_.iloc[0] is column_.iloc[1]
        True

        Threshold is a non-negative float or int:

        - If 0 <= threshold < 1, the threshold is a ratio of ray and intervals
            required for the function to return True.
        - if threshold > 1, the threshold is a number of rays and
            intervals required for the function to return True.

        Additional processing block slices rays. Specifically, it slices
        same-directional rays into non-overlapping intervals and rays.
        For example:

        >>> column_ = pd.Series([">=4", ">5"])
        >>> expected = pd.Series([Range(start=4, end=5), Range(start=5)])
        >>> _, ranges_ = convert_special_categorical_column(column_)
        >>> ranges_.equals(expected)
        True

        It also slices rays, if there exists a point in the direction
        they are facing. For example:

        >>> column_ = pd.Series([">=4", 5])
        >>> expected = pd.Series([Range(start=4, end=5, end_inclusive=False), Range(5)])
        >>> _, ranges_ = convert_special_categorical_column(column_)
        >>> ranges_.equals(expected)
        True

    Examples:
        >>> column_ = pd.Series([
        ...     "above 50", -1, 0, "hi", 2.5, np.nan, "2 to 3.5", "<=-1", "never",
        ... ])
        >>> expected = pd.Series([
        ...     Range(start=50.0), Range(num=-1.0), Range(num=0),
        ...     np.nan, Range(num=2.5), np.nan, Range(start=2.0, end=3.5),
        ...     Range(end=-1, end_inclusive=True), Range(num=0),
        ... ])
        >>> contains_special, ranges_ = convert_special_categorical_column(column_)
        >>> contains_special, ranges_.equals(expected)
        (True, True)

    Args:
        column (pd.Series): special categorical column to convert.
        threshold (Union[int, float]): the threshold for the number
            or the ratio of Range objects or number of rays and intervals for
            the function to compare against.
            Set to 1 by default.

    Returns:
        contains_special (bool): Whether the data passed the
            corresponding threshold.
        ranges (pd.Series[Range]): Series of Range onjects.

    Raises:
        ValueError: if threshold was set incorrectly.

    """

    # if the column is empty
    if (column_length := column.shape[0]) == 0:
        return False, column

    # -------------------------------------- Prepare data -------------------------------------- #

    # save original index and reset index
    orig_index = column.index
    column = column.reset_index(drop=True)

    # prepare data
    column = validated_column_to_column(column, special_nan_to_nan)  # convert special nan strings to nan values
    null_map = column.isnull()
    data_numeric = pd.to_numeric(column, errors="coerce")
    if not isinstance(data_numeric, pd.Series):
        raise TypeError(f"Expected a pandas series. Received: {type(data_numeric)}.")
    numeric_null_map: pd.Series = data_numeric.isnull()
    # @pyright: doesn't understand that filtering using these boolean masks returns pandas Series
    data_strings: pd.Series = column[numeric_null_map & ~null_map]  # type: ignore
    data_numeric: pd.Series = data_numeric[~numeric_null_map]  # type: ignore
    # If there are too many unique values, it is not likely to be a special categorical column,
    # so that we don't have to spend too much time matching the regexes.
    if data_strings.nunique() >= 100:
        return False, column

    # -------------------------------------- Convert data -------------------------------------- #

    ranges = np.empty(column_length, dtype=object)  # create empty array for Range objects

    # parse numerics
    for value, indexes in data_numeric.groupby(data_numeric).groups.items():
        ranges[indexes] = Range(num=float(value))

    def get_range(value):
        stripped = value.strip()

        if match := SpecialCatRegExp.RIGHT(stripped) or SpecialCatRegExp.LEFT(stripped):
            parsed_groups = [group for group, value in match.groupdict().items() if value is not None]

            return Range(
                start=float(match.group("num")) if "pos" in parsed_groups else None,
                end=float(match.group("num")) if "neg" in parsed_groups else None,
                start_inclusive=(
                    None
                    if "neg" in parsed_groups
                    else (
                        False
                        if any("neq" in group for group in parsed_groups)
                        else any("eq" in group for group in parsed_groups)
                    )
                ),
                end_inclusive=(
                    None
                    if "pos" in parsed_groups
                    else (
                        False
                        if any("neq" in group for group in parsed_groups)
                        else any("eq" in group for group in parsed_groups)
                    )
                ),
            )

        # regex search for intervals, e.g. "from 30 to 50", "between 30 and 50"
        elif match := SpecialCatRegExp.INTERVAL(stripped) or SpecialCatRegExp.INTERVAL_BETWEEN(stripped):
            num1, num2 = float(match.group("num1")), float(match.group("num2"))
            return Range(start=min(num1, num2), end=max(num1, num2))

        elif SpecialCatRegExp.SPECIAL_WORDS(stripped):
            return Range(num=0)

        return np.nan

    # parse strings
    for value, indexes in data_strings.groupby(data_strings).groups.items():
        ranges[indexes] = get_range(value)

    # ---------------------------------- Additional processing ---------------------------------- #

    rays: Set[Range] = {ray for ray in ranges if isinstance(ray, Range) and ray.type == RangeType.RAY}
    positive_rays = sorted([ray for ray in rays if ray.end == np.inf])
    negative_rays = sorted([ray for ray in rays if ray.start == np.NINF], reverse=True)
    points: Set[Range] = {point for point in ranges if isinstance(point, Range) and point.type == RangeType.POINT}

    # positive
    pos_ray_groups = [
        RayGroup(start, list(group)) for start, group in groupby(positive_rays, key=lambda ray: ray.start_)
    ]
    replace_rays: Dict[Range, Range] = {
        ray: Range(
            start=ray.start,
            end=pos_ray_groups[i + 1][0],
            start_inclusive=ray.start_inclusive,
            end_inclusive=not any(next_group_ray.start_inclusive for next_group_ray in pos_ray_groups[i + 1][1]),
        )
        for i in range(len(pos_ray_groups) - 1)
        for ray in pos_ray_groups[i][1]
    }

    if pos_ray_groups:
        if slice_pos_ray := min(
            {point for point in points if point.num_ > pos_ray_groups[-1].boundary},
            default=None,
        ):
            replace_rays.update(
                {
                    ray: Range(
                        start=ray.start,
                        end=slice_pos_ray.num_,
                        start_inclusive=ray.start_inclusive,
                        end_inclusive=False,
                    )
                    for ray in pos_ray_groups[-1][1]
                }
            )

    # negative
    neg_ray_groups = [RayGroup(end, list(group)) for end, group in groupby(negative_rays, key=lambda ray: ray.end_)]
    replace_rays.update(
        {
            ray: Range(
                start=neg_ray_groups[i + 1].boundary,
                end=ray.end,
                start_inclusive=not any(
                    next_group_ray.end_inclusive_ for next_group_ray in neg_ray_groups[i + 1].group
                ),
                end_inclusive=ray.end_inclusive_,
            )
            for i in range(len(neg_ray_groups) - 1)
            for ray in neg_ray_groups[i].group
        }
    )

    if neg_ray_groups:
        filtered_points: Set[Range] = {point for point in points if point.num_ < neg_ray_groups[-1].boundary}
        if filtered_points:
            slice_neg_ray = max(filtered_points)
            replace_rays.update(
                {
                    ray: Range(
                        start=slice_neg_ray.num_,
                        end=ray.end,
                        start_inclusive=False,
                        end_inclusive=ray.end_inclusive_,
                    )
                    for ray in neg_ray_groups[-1].group
                }
            )

    # update rays
    for key, value in replace_rays.items():
        ranges[ranges == key] = value

    # --------------------------------------- Return data --------------------------------------- #

    # count the number of rays and intervals
    condition_vectorised = np.vectorize(lambda x: isinstance(x, Range) and x.type != RangeType.POINT)
    number_of_rays_and_intervals = np.sum(condition_vectorised(ranges))

    # convert to pd.Series
    ranges = pd.Series(ranges, index=orig_index, name=column.name)

    # if there are no rays or intervals, return False
    if number_of_rays_and_intervals == 0:
        return False, ranges

    # treat as a total number
    if threshold >= 1:
        return (True, ranges) if number_of_rays_and_intervals >= threshold else (False, ranges)

    # treat as a ratio
    if 0 <= threshold < 1:
        return (True, ranges) if number_of_rays_and_intervals / column_length >= threshold else (False, ranges)

    raise ValueError("Threshold was set incorrectly")
