"""Module providing special categorical specific regexes and classes."""

# ───────────────────────────────── Imports ────────────────────────────────── #
# Standard Library
import re
from enum import Enum

# ─────────────────────────────────── Code ─────────────────────────────────── #


# \s{,4} means that we allow up to 4 whitespace characters (\s equivalent to [\r\n\t\f\v  ])
SPECIAL_CATEGORICAL_RIGHT = re.compile(
    r"^(?P<eq1>(?P<neq1>not\s?)?(?:including|inclusive(?:ly)?))?\s?,?"  # optional (in)equality indicator
    r"(?P<neq2>(?:excluding|exclusive(?:ly)?)\s?,?)?"  # optional inequality indicator
    r"(?P<eq2>(?P<neq3>not\s?)?equal\s?(?:to\s?or|to|or)?)?"  # optional equality indicator
    r"\s{,4}(?:(?P<pos>above|greater|more|from|bigger|after|gt|>)|"  # positive ray
    r"(?P<neg>below|smaller|less|before|lower|lt|fewer|(?:up\s?)?to|<))"  # negative ray
    r"\s{,4}(?P<eq3>=|or\s?equal\s?(?:to)?)?"  # optional "or equal" or "or equal to"
    r"(?:\s{,4}than)?"  # optional "than"
    r"\s{,4}(?P<num>[+-]?(?:[0-9]*[.])?[0-9]+)\s?%?"  # the number
    r"\s?,?\s?(?P<eq4>(?:and\s?)?(?P<neq4>not\s?)?(?:including|inclusive(?:ly)?))?"  # optional equality indicator
    r"\s?,?\s?(?P<neq5>(?:and)?\s?excluding|exclusive(?:ly)?)?$",  # optional inequality indicator
    flags=re.I | re.X,
)

SPECIAL_CATEGORICAL_LEFT = re.compile(
    r"^(?P<eq1>(?P<neq1>not\s?)?(?:including|inclusive(?:ly)?))?\s?,?"  # optional (in)equality indicator
    r"(?P<neq2>(?:excluding|exclusive(?:ly)?)\s?,?)?"  # optional inequality indicator
    r"(?P<eq2>(?P<neq3>not\s?)?equal\s?(?:to\s?or|to|or)?)?"  # optional equality indicator
    r"\s{,4}(?P<num>[+-]?(?:[0-9]*[.])?[0-9]+)\s?%?"  # the number
    r"(?P<eq3>\s{,4}and)?"  # optional "and" is an equality indicator
    r"\s{,4}(?:(?P<pos>above|more|greater|larger|higher|bigger|(?P<eq4>plus|\+))|"  # positive ray
    r"(?P<neg>lower|less|below|smaller|fewer|shorter|(?P<eq5>-)))"  # negative ray
    r"\s?,?\s?(?P<eq6>(?:and\s?)?(?P<neq4>not\s?)?(?:including|inclusive(?:ly)?))?"  # optional equality indicator
    r"\s?,?\s?(?P<neq5>(?:and)?\s?excluding|exclusive(?:ly)?)?$",  # optional inequality indicator
    flags=re.I | re.X,
)

SPECIAL_CATEGORICAL_INTERVAL = re.compile(
    r"^(?:from)?"  # optional "from"
    r"\s{,4}(?P<num1>[+-]?([0-9]*[.])?[0-9]+)\s?%?"  # first number
    r"\s{,4}(?:to|-|—|~)"  # mandatory "to" or "-" or "—" or "~"
    r"\s{,4}(?P<num2>[+-]?([0-9]*[.])?[0-9]+)\s?%?$",  # second number
    flags=re.I | re.X,
)

SPECIAL_CATEGORICAL_INTERVAL_BETWEEN = re.compile(
    r"^between"  # mandatory "between"
    r"\s{,4}(?P<num1>[+-]?([0-9]*[.])?[0-9]+)\s?%?"  # first number
    r"\s{,4}and"  # mandatory "and"
    r"\s{,4}(?P<num2>[+-]?([0-9]*[.])?[0-9]+)\s?%?$",  # second number
    flags=re.I | re.X,
)

SPECIAL_CATEGORICAL_SPECIAL_WORDS = re.compile(
    r"^never$",
    flags=re.I | re.X,
)

# Frequency is not currently implemented
# Can catch cases like "5/month", "7 times a year", "93.4 per hour"
FREQUENCY = re.compile(
    r"^(?P<num>[+-]?([0-9]*[.])?[0-9]+)"  # the number
    r"\s{,4}(?:times)?"  # optional "times"
    r"\s{,4}(?:an?|per|each|/)"  # mandatory "a" or "an" or "per" or "each" or "/". Indicator of frequency
    r"\s{,4}(?P<unit>s|sec|second|min|minute|h|hour|d|day|week|mon|month|y|year)$",  # the frequency unit
    flags=re.I | re.X,
)


class SpecialCatRegExp(Enum):
    """Enumerator class to iterate over regular expressions of special
    categorical cases.

    Right and Left indicate the position of a number within the expression
        with regard to the indicators of ray directions.
    Interval indicates an interval.
    Interval Between is a special case for Interval. Made to match
        "between 50 and 60" but not "50 and 60".
    Special Words is a special case for words that indicate a specific number.

    Examples:
        "above 50" - Right
        "50 and greater" - Left
        "from 21 to 50.4" - Interval
        "between 40 and 60" - Interval Between
        "never" - Special Words

    """

    RIGHT = SPECIAL_CATEGORICAL_RIGHT
    LEFT = SPECIAL_CATEGORICAL_LEFT
    INTERVAL = SPECIAL_CATEGORICAL_INTERVAL
    INTERVAL_BETWEEN = SPECIAL_CATEGORICAL_INTERVAL_BETWEEN
    SPECIAL_WORDS = SPECIAL_CATEGORICAL_SPECIAL_WORDS

    def __call__(self, *args, **kwargs):
        return self.value.match(*args, **kwargs)
