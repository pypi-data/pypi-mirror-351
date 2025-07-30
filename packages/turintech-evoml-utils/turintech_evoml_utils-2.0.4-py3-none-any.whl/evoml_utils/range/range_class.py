"""Module providing Range class."""

# ───────────────────────────────── Imports ────────────────────────────────── #
# Standard Libraries
from __future__ import annotations
from typing import Literal, Dict, Any, TypeVar, Optional, Union
from enum import Enum
from functools import total_ordering


# 3rd Party
import numpy as np
import pandas as pd
from pydantic import root_validator
from pydantic.dataclasses import dataclass

# ─────────────────────────────────── Code ─────────────────────────────────── #


class RangeType(str, Enum):
    POINT = "point"
    RAY = "ray"
    INTERVAL = "interval"


T = TypeVar("T")
S = TypeVar("S")


# @mypy: Argument 1 to "total_ordering" has incompatible type "Union[Type[Dataclass], DataclassProxy]"; expected "Type[Dataclass]"
@total_ordering  # type: ignore
@dataclass(frozen=True)
class Range:
    """Totally ordered frozen pydantic dataclass for intervals, rays, and numbers.

    The class to represent ranges of real numbers and perform operations
    on them.

    Attributes:
        num (Optional[float]): points.
            (None by default).
        start (Optional[float]): the starting point of an interval or a ray.
            (None by default).
        end (Optional[float]): the ending point of an interval or a ray.
            (None by default).
        start_inclusive (Optional[bool]): indicator whether the start of
            a ray/an interval includes the point.
            (None by default).
        end_inclusive (Optional[bool]): indicator whether the end of
            a ray/an interval includes the point.
            (None by default).
        type (RangeType): the type of instance. Is set automatically
            by `set_default_type` root validator.
            (None by default)

    Methods:
        `includes`: checks if one range includes another.
        `overlap`: checks if two ranges overlap.
        `centre`: returns the centre point of a range.
        `midpoint`: returns the midpoint between two ranges.
            Raises a ValueError if the ranges overlap.
        Please see the docstrings of the methods for more information.

    Examples:
        Range(num=5.0) indicates a point 5.0.

        Range(start=3.0, end=15.0) indicates the range [3, 15],
        where both edges are by default included.

        Range(start=-3.5, start_inclusive=True) indicates the
        ray [-3.5, inf). The edge point is included.

        Range(num=4.0, start=4.0) will raise:
        ValueError: An object can represent only either a point,
        a ray or an interval.

    Notes:
        For points only 'num' is not None.
        For rays either 'start' or 'end' is inf or -inf, respectively.
        For intervals both 'start' and 'end' are real numbers, or
            -inf and inf simultaneously, respectively.

        Five pydantic root validators were implemented in the class
        to ensure the validity of the instances:
            1) At least one of 'num', 'start', or 'end' has to be not None.
                Meaning that an instance must mean something.
            2) An instance must be either a point, a ray, or an interval.
            3) Inclusiveness attributes are not available for points.
            4) Start of an interval must be less than its end.
            5) If start and end of an interval are the same, a point
                is initialised instead.

        An additional three root validators were created to set the default
        values:
            1) The other end of a ray or an interval to inf or -inf.
            2) The default type of given Range using RangeType Enum class.
            3) The default inclusiveness attributes for rays and intervals.
                For rays edges are by default not included.
                For intervals edges are by default included.
                    Exceprion is the case when both edges are inf or -inf.
                    In that case the edges are not included.

        For example:

        >>> Range(start=3)
        Range(num=None, start=3.0, end=inf, start_inclusive=False, \
end_inclusive=False, type=<RangeType.RAY: 'ray'>)
        >>> Range(start=-4)
        Range(num=None, start=-4.0, end=inf, start_inclusive=False, \
end_inclusive=False, type=<RangeType.RAY: 'ray'>)
        >>> Range(start=-1, end=5.5)
        Range(num=None, start=-1.0, end=5.5, start_inclusive=True, \
end_inclusive=True, type=<RangeType.INTERVAL: 'interval'>)
        >>> Range(np.inf)
        Range(num=inf, start=None, end=None, start_inclusive=None, \
end_inclusive=None, type=<RangeType.POINT: 'point'>)
        >>> Range(end=np.inf)
        Range(num=None, start=-inf, end=inf, start_inclusive=False, \
end_inclusive=False, type=<RangeType.INTERVAL: 'interval'>)
        >>> Range(start=-np.inf, end=np.inf)
        Range(num=None, start=-inf, end=inf, start_inclusive=False, \
end_inclusive=False, type=<RangeType.INTERVAL: 'interval'>)

        The added `__str__` dunder method returns the string representation in
        a uniform format for any point, ray and interval. For example:

        >>> str(Range(num=5.0))
        '5.0'
        >>> str(Range(start=50.0))
        '(50.0, inf)'
        >>> str(Range(end=-1.0, end_inclusive=True))
        '(-inf, -1.0]'
        >>> str(Range(start=-20.0, end=50.0))
        '[-20.0, 50.0]'

        The added `__lt__` and `__eq__` dunder methods in combination with the
        @total_ordering functools decorator define a strict total order on a
        given set of Ranges. Thus, it is possible to compare any two instances
        of the class. Additionally, this allows for python's "sorted" method
        and pandas' "sort_values" to work on an array-like object of Ranges.
        When sorted, nans are put at the end of an array. For example:

        >>> column = pd.Series([
        ...     Range(num=5.5), Range(start=6.23, start_inclusive=False),
        ...     Range(end=1.0, end_inclusive=True), Range(num=1),
        ...     Range(num=10.0), np.nan, Range(num=3), Range(num=-3),
        ...     Range(start=2, end=3), np.nan, Range(num=2.5),
        ...     Range(start=2, end=4, start_inclusive=False),
        ... ])
        >>> column.sort_values()
        2     (-inf, 1.0]
        7            -3.0
        3             1.0
        8      [2.0, 3.0]
        11     (2.0, 4.0]
        10            2.5
        6             3.0
        0             5.5
        1     (6.23, inf)
        4            10.0
        5             NaN
        9             NaN
        dtype: object

        The added `__add__` dunder method allows to perform commutitative
        addition of the Range instances. The result of an addition is the
        smallest possible Range object that would include both terms.

        For example:

        >>> Range(1) + Range(2)
        Range(num=None, start=1.0, end=2.0, start_inclusive=True, \
end_inclusive=True, type=<RangeType.INTERVAL: 'interval'>)

        >>> Range(start=-3, end=4) + Range(2)
        Range(num=None, start=-3.0, end=4.0, start_inclusive=True, \
end_inclusive=True, type=<RangeType.INTERVAL: 'interval'>)

        >>> Range(4) + Range(start=1, end=2)
        Range(num=None, start=1.0, end=4.0, start_inclusive=True, \
end_inclusive=True, type=<RangeType.INTERVAL: 'interval'>)

        >>> Range(4) + Range(start=4)
        Range(num=None, start=4.0, end=inf, start_inclusive=True, \
end_inclusive=False, type=<RangeType.RAY: 'ray'>)

        >>> Range(5) + Range(end=4)
        Range(num=None, start=-inf, end=5.0, start_inclusive=False, \
end_inclusive=True, type=<RangeType.RAY: 'ray'>)

        >>> Range(start=3, end=6) + Range(start=5)
        Range(num=None, start=3.0, end=inf, start_inclusive=True, \
end_inclusive=False, type=<RangeType.RAY: 'ray'>)

        >>> Range(start=2) + Range(start=3, start_inclusive=True)
        Range(num=None, start=2.0, end=inf, start_inclusive=False, \
end_inclusive=False, type=<RangeType.RAY: 'ray'>)

        >>> Range(start=2) + Range(end=3)
        Range(num=None, start=-inf, end=inf, start_inclusive=False, \
end_inclusive=False, type=<RangeType.INTERVAL: 'interval'>)

        >>> Range(end=2) + Range(np.inf)
        Range(num=None, start=-inf, end=inf, start_inclusive=False, \
end_inclusive=True, type=<RangeType.INTERVAL: 'interval'>)

    """

    num: Optional[float] = None
    start: Optional[float] = None
    end: Optional[float] = None
    start_inclusive: Optional[bool] = None
    end_inclusive: Optional[bool] = None
    type: Optional[RangeType] = None

    @root_validator
    @classmethod
    def at_least_one_of_num_start_end_not_none(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if all([values["num"] is None, values["start"] is None, values["end"] is None]):
            raise ValueError("At least one of 'num', 'start', or 'end' must have a value.")
        return values

    @root_validator
    @classmethod
    def either_point_ray_range(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values["num"] is not None and any([values["start"] is not None, values["end"] is not None]):
            raise ValueError("An object can represent only either a point, a ray, or an interval.")
        return values

    @root_validator
    @classmethod
    def validate_ends_and_set_other_end_for_rays_and_intervals(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Root validator to set the other end for rays and intervals, e.g.
        Range(start=5) -> Range(start=5, end=np.inf)  # for ray
        Range(end=np.inf) -> Range(start=np.NINF, end=np.inf)  # for interval"""
        if values["num"] is None:
            if values["start"] is None:
                values["start"] = np.NINF
            if values["end"] is None:
                values["end"] = np.inf

        return values

    @root_validator
    @classmethod
    def set_default_type(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values["num"] is not None:
            values["type"] = RangeType.POINT
        elif (values["start"] == np.NINF) ^ (values["end"] == np.inf):
            values["type"] = RangeType.RAY
        else:
            values["type"] = RangeType.INTERVAL
        return values

    @root_validator
    @classmethod
    def set_default_inclusiveness_for_rays_and_intervals(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Rays are by default not inclusive;
        Intervals are by default inclusive on both sides.
        For intervals the exception is (-inf, inf)"""
        if values["type"] == RangeType.RAY:
            if values["start_inclusive"] is None:
                values["start_inclusive"] = False
            if values["end_inclusive"] is None:
                values["end_inclusive"] = False

        elif values["type"] == RangeType.INTERVAL:
            if values["start_inclusive"] is None:
                values["start_inclusive"] = values["start"] != np.NINF
            if values["end_inclusive"] is None:
                values["end_inclusive"] = values["end"] != np.inf

        return values

    @root_validator
    @classmethod
    def interval_start_must_be_less_or_equal_end(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate interval.start <= interval.end is True.

        If interval.start == interval.end,
            `validate_interval_same_start_and_end_is_a_point`
            will create a Point instead of an interval
        """
        if values["type"] == RangeType.INTERVAL and values["start"] > values["end"]:
            raise ValueError("Start of the interval must be less or equal to its end.")
        return values

    @root_validator
    @classmethod
    def validate_interval_same_start_and_end_is_a_point(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """If the interval start and end are the same and the inclusiveness
        attributes are both true, initialize a point instead.
        If the interval start and end are the same but the inclusiveness
        attributes are not both true, raise an error.
        """
        if values["type"] == RangeType.INTERVAL and values["start"] == values["end"]:
            if not values["start_inclusive"] or not values["end_inclusive"]:
                raise ValueError(
                    "The interval's inclusiveness attributes were set incorrectly. "
                    "If you wish to initialise an interval with same start and end, "
                    "initialise a Range as a point instead."
                )

            # enforce initialisation as a point instead
            values["num"] = values["start"]
            values["start"], values["end"] = None, None
            values["start_inclusive"], values["end_inclusive"] = None, None
            values["type"] = RangeType.POINT

        return values

    @root_validator
    @classmethod
    def points_cannot_be_inclusive(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values["type"] == RangeType.POINT and any(
            [values["start_inclusive"] is not None, values["end_inclusive"] is not None]
        ):
            raise ValueError("Points cannot be inclusive.")
        return values

    def __eq__(self, other: Any) -> bool:
        if type(other) not in [int, float, Range]:
            return False

        # to be able to compare with integers and floats
        if type(other) in [int, float]:
            other = Range(num=other)

        eq = self.__dict__.items() == other.__dict__.items()

        if not isinstance(eq, bool):
            raise TypeError(f"Range.__eq__ should return a boolean type. Got {eq}.")

        return eq

    def __lt__(self, other: Any) -> bool:
        if type(other) not in [int, float, Range]:
            return False

        # to be able to compare with integers and floats
        if type(other) in [int, float]:
            other = Range(num=other)

        # first, compare Ranges on the num for points and on the start for rays and intervals
        self_val = self.num if self.type == RangeType.POINT else self.start
        other_val = other.num if other.type == RangeType.POINT else other.start

        # different values and any 2 points
        if self_val != other_val or self.type == RangeType.POINT and other.type == RangeType.POINT:
            return self_val < other_val

        # same values
        # points are smaller than rays and interval
        if (self.type == RangeType.POINT) ^ (other.type == RangeType.POINT):
            return other.type in [RangeType.RAY, RangeType.INTERVAL]

        # compare rays and intervals on the end value; different end values
        if self.end != other.end:
            return self.end < other.end

        # same end values; compare on start inclusiveness
        if self.start_inclusive ^ other.start_inclusive:
            return self.start_inclusive_

        # same end values, same start inclusiveness; compare on end inclusiveness
        return not self.end_inclusive and other.end_inclusive

    def __add__(self, other: Range) -> Range:
        def check_inclusiveness(range1: Range, range2: Range, side: Literal["start", "end"]) -> bool:
            """This function checks whether the start or end should be inclusive after the addition."""

            # both Ranges are points
            if (range1.type == RangeType.POINT) and (range2.type == RangeType.POINT):
                return True

            # one of the Ranges is a point
            if (range1.type == RangeType.POINT) ^ (range2.type == RangeType.POINT):
                point, ray_or_int = (range1, range2) if range1.type == RangeType.POINT else (range2, range1)

                if side == "start":
                    return point.num_ <= ray_or_int.start_ or ray_or_int.start_inclusive_

                # side == "end"
                return ray_or_int.end_ <= point.num_ or ray_or_int.end_inclusive_

            # ray + ray; ray + interval; interval + interval
            if side == "start":
                return (
                    range1.start_inclusive_
                    if range1.start_ < range2.start_
                    else (
                        range2.start_inclusive_
                        if range2.start_ < range1.start_
                        else range1.start_inclusive_ or range2.start_inclusive_
                    )
                )

            # side == "end"
            return (
                range1.end_inclusive_
                if range2.end_ < range1.end_
                else (
                    range2.end_inclusive_
                    if range1.end_ < range2.end_
                    else range1.end_inclusive_ or range2.end_inclusive_
                )
            )

        return Range(
            start=min([x for x in [self.num, self.start, other.num, other.start] if x is not None], default=None),
            end=max([x for x in [self.num, self.end, other.num, other.end] if x is not None], default=None),
            start_inclusive=check_inclusiveness(self, other, "start"),
            end_inclusive=check_inclusiveness(self, other, "end"),
        )

    def centre(self) -> float:
        """Find the centre point of a Range.

        Examples:

        >>> Range(2).centre()
        2.0
        >>> Range(start=0, end=10).centre()
        5.0
        >>> Range(start=10).centre()
        inf

        """

        if self.type == RangeType.POINT:
            return self.num_

        return (self.start_ + self.end_) / 2

    def includes(self, other: Union[Range, int, float]) -> bool:
        """This function checks whether `self` fully includes `other` in itself.

        Examples:

        >>> Range(start=1, end=5).includes(Range(3))
        True
        >>> Range.includes(Range(start=5), Range(start=6, end=10))
        True
        >>> Range(start=0, end=3, start_inclusive=False).includes(0)
        False
        >>> Range(start=10).includes(Range(np.inf))
        True
        >>> Range(end=5).includes(Range(np.NINF))
        True

        """

        # to be able to compare with integers and floats
        if isinstance(other, float):
            other = Range(num=other)
        elif isinstance(other, int):
            other = Range(num=float(other))

        # self is a point
        if self.type == RangeType.POINT:
            return other.type == RangeType.POINT and self.num == other.num

        # self is a ray or an interval, other is a point
        if other.type == RangeType.POINT:

            # special case for rays and points at infinity
            if self.end == np.inf and other.num == np.inf or self.start == np.NINF and other.num == np.NINF:
                return True

            return (self.start_ <= other.num_ if self.start_inclusive_ else self.start_ < other.num_) and (
                self.end_ >= other.num_ if self.end_inclusive_ else self.end_ > other.num_
            )

        return (
            self.start_ < other.start_
            if self.start != other.start
            else self.start_inclusive or not other.start_inclusive
        ) and (self.end_ > other.end_ if self.end != other.end else self.end_inclusive or not other.end_inclusive)

    def overlap(self, other: Range) -> bool:
        """Check whether the two given Ranges overlap.

        Overlap means that there exists a point, which epsilon interval
        is a subset of both Ranges:

        .. math::
            \\exists x, \\epsilon > 0: (x-\\epsilon, x+\\epsilon) \\subset self \\cap other

        >>> Range.overlap(Range(5), Range(5))
        False
        >>> Range.overlap(Range(start=5), Range(5))
        False
        >>> Range.overlap(Range(start=5, end=10), Range(start=10, start_inclusive=True))
        False
        >>> Range.overlap(Range(start=5, end=10), Range(start=8))
        True

        """

        # both are points
        if self.type == RangeType.POINT and other.type == RangeType.POINT:
            return False

        # one of the Ranges is a point
        if (self.type == RangeType.POINT) ^ (other.type == RangeType.POINT):
            point, ray_or_int = (self, other) if self.type == RangeType.POINT else (other, self)
            assert point.num is not None
            assert ray_or_int.start is not None and ray_or_int.end is not None
            return ray_or_int.start < point.num < ray_or_int.end

        # both are ray or interval
        if self.start == other.start or self.end == other.end:
            return True

        assert self.start is not None and self.end is not None
        assert other.start is not None and other.end is not None

        return self.start < other.end and other.start < self.end

    @staticmethod
    def midpoint(range1: Range, range2: Range) -> Range:
        """This function finds the midpoint for two not intercepting ranges.

        Examples:

        >>> Range.midpoint(Range(2), Range(4))
        Range(num=3.0, start=None, end=None, start_inclusive=None, \
end_inclusive=None, type=<RangeType.POINT: 'point'>)

        >>> Range.midpoint(Range(start=3), Range(2))
        Range(num=2.5, start=None, end=None, start_inclusive=None, \
end_inclusive=None, type=<RangeType.POINT: 'point'>)

        >>> Range.midpoint(Range(start=3), Range(start=-1, end=0))
        Range(num=1.5, start=None, end=None, start_inclusive=None, \
end_inclusive=None, type=<RangeType.POINT: 'point'>)

        >>> Range.midpoint(Range(start=-1, end=0), Range(start=1, end=10))
        Range(num=0.5, start=None, end=None, start_inclusive=None, \
end_inclusive=None, type=<RangeType.POINT: 'point'>)

        """

        # both are points
        if range1.type == RangeType.POINT and range2.type == RangeType.POINT:
            return Range(num=(range1.num_ + range2.num_) / 2)

        # one of the Ranges is a point
        if (range1.type == RangeType.POINT) ^ (range2.type == RangeType.POINT):
            point, ray_or_int = (range1, range2) if range1.type == RangeType.POINT else (range2, range1)

            if ray_or_int.includes(point):
                raise ValueError("A Range and a point inside that Range do not have a midpoint.")

            return Range(
                num=(
                    (point.num_ + ray_or_int.start_) / 2
                    if point.num_ <= ray_or_int.start_
                    else (point.num_ + ray_or_int.end_) / 2 if ray_or_int.end_ <= point.num_ else None
                )  # None should never be returned as otherwise the point is included
            )

        # for rays and intervals
        if Range.overlap(range1, range2):
            raise ValueError("Overlapping Ranges do not have a midpoint.")

        return Range(num=(range1.end_ + range2.start_) / 2 if range1 < range2 else (range1.start_ + range2.end_) / 2)

    def __str__(self):
        # points
        if self.type == RangeType.POINT:
            return str(self.num)

        # rays and intervals
        left_bracket = "[" if self.start_inclusive else "("
        right_bracket = "]" if self.end_inclusive else ")"
        return "".join([left_bracket, str(self.start), ", ", str(self.end), right_bracket])

    # ---------------------------------------------------------------------------------------------------------------- #
    # Properties which guaranteeing a non-Null return or a clear error message for diagnosing the issue.
    # ---------------------------------------------------------------------------------------------------------------- #
    @property
    def start_(self) -> float:
        if self.start is None:
            raise ValueError(
                f"Start should be specified for ranges representing intervals and rays. This range represents a "
                f"{self.type}."
            )
        return self.start

    @property
    def start_inclusive_(self) -> bool:
        if self.start_inclusive is None:
            raise ValueError(
                f"The start inclusive attribute should be specified for ranges representing intervals and rays. This "
                f"range represents a {self.type}."
            )
        return self.start_inclusive

    @property
    def end_(self) -> float:
        if self.end is None:
            raise ValueError(
                f"End should be specified for ranges representing intervals and rays. This range represents a "
                f"{self.type}."
            )
        return self.end

    @property
    def end_inclusive_(self) -> bool:
        if self.end_inclusive is None:
            raise ValueError(
                f"The end inclusive attribute should be specified for ranges representing intervals and rays. This "
                f"range represents a {self.type}."
            )
        return self.end_inclusive

    @property
    def num_(self) -> float:
        if self.num is None:
            raise ValueError(
                f"Num should be specified for ranges representing a single point. This range represents a {self.type}."
            )
        return self.num
