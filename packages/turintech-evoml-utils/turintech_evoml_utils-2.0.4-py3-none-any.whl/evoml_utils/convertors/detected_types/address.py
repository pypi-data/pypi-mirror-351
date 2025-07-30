import re
from typing import Tuple, Optional


import pandas as pd

# @mypy: missing library stubs or py.typed marker
import pyap  # type: ignore
import pyap.address  # type: ignore

from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column


def check_country_postcode(value: str, country: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if both country and a valid postcode are contained in value and returns the result of the check. If this
    check is True, it also returns the postcode found in value and the country.

    Args:
        value:
            A string input.
        country:
            A string representing a country and can take 3 values GB/CA/US.
    Returns:
        Tuple[bool, Optional[str]]:
            Returns result of the check.
    """

    country_regex_dict = {
        "GB": r"\b(United Kingdom|U\.? ?K\.?|G\.? ?B\.?|Great Britain|England|Scotland|Wales|Ireland|CYMRU|N\.? ?"
        r"I\.?)\b",
        "CA": r"\bCanada\b",
        "US": r"\b(United States?|U\.?S\.?(\.?A)?)\b",
    }
    # https://stackoverflow.com/questions/164979/regex-for-matching-uk-postcodes
    # https://stackoverflow.com/questions/15774555/efficient-regex-for-canadian-postal-code-function
    postcode_regex_dict = {
        "GB": r"\b(([A-Z]{1,2}\d[A-Z\d]?|ASCN|STHL|TDCU|BBND|[BFS]IQQ|PCRN|TKCA) ?\d[A-Z]{2}|BFPO ?\d{1,4}|"
        r"(KY\d|MSR|VG|AI)[ -]?\d{4}|[A-Z]{2} ?\d{2}|GE ?CX|GIR ?0A{2}|SAN ?TA1)\b",
        "CA": r"\b([ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d)\b",
        "US": r"\b(\d{5}(\-\d{4})?)\b",
    }
    country_regex = country_regex_dict[country]
    post_regex = postcode_regex_dict[country]
    country_match = re.search(country_regex, value, re.IGNORECASE)
    if country_match:  # if country in value, check that postcode is also in value
        post_match = re.search(
            post_regex + "( *,? *{})".format(country_match.group()),
            value,
            re.IGNORECASE,
        )
        if post_match:
            return True, post_match.group(1).replace(" ", "").upper()
    return False, None


def to_address(value: Optional[str]) -> Optional[dict]:
    """
    Checks if value is a string representing an address in UK, CA or US and if this is true, returns a dict with the
    address details as it is returned by pyap. If this is not true, the function returns None.

    Args:
        value:
            Can be string or np.nan
    Returns:
        Optional[dict]:
            Address in dict format, if value represents an address in UK/CA/US. Otherwise, None.
    """
    if not isinstance(value, str):
        return None
    country_names = {"GB": "United Kingdom", "US": "United States", "CA": "Canada"}
    for country in ["GB", "US", "CA"]:
        # @pyright: thinks pyap.parse can return booleans
        addresses: List[pyap.address.Address] = pyap.parse(value, country=country)  # type: ignore
        if addresses:
            check, postcode = check_country_postcode(value, country)
            if check:
                address_dict = addresses[0].as_dict()
                address_dict["country"] = country_names[country]
                address_dict["postal_code"] = postcode
                return address_dict
    return None


def to_address_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of string values to a column of the corresponding address dictionaries as they are returned by
    the pyap library. All invalid values are converted to None.

    Args:
        column:
            Input column in pandas.Series format.
    Returns:
        pd.Series:
            The converted column consisting of address dictionaries.
    """
    return validated_column_to_column(column, to_address)
