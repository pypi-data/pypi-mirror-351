from typing import Optional, Union


import pandas as pd
import ipaddress
from ipaddress import IPv4Address, IPv6Address


from evoml_utils.convertors.utils.validated_column_to_column import validated_column_to_column


def to_ip(value: Union[float, int, str]) -> Optional[Union[IPv4Address, IPv6Address]]:
    """
    Converts value to an IP object if value represents an IP address.

    Args:
        value:
            Can be numeric or string
    Returns:
        Optional[Union[IPv4Address, IPv6Address]]:
            The corresponding IP object for value if value represents a valid IP address or None otherwise.
    """

    try:
        # @pyright: raises the error Argument of type "float | int | str" cannot be assigned to parameter "address" of type "_RawIPAddress" in function "ip_address" (reportArgumentType)
        address = ipaddress.ip_address(value)  # type: ignore
    except ValueError:
        address = None
    return address


def to_ip_objs_column(column: pd.Series) -> pd.Series:
    """
    Converts a column of strings to a column of the corresponding IPv4Address or IPv6Address objects.
    Any invalid value is converted to None.

    Args:
        column:
            The input column is pandas.Series format.
    Returns:
        pd.Series:
            The converted column consisting of IPv4Address and Ipv6Address objects and None values.
    """

    return validated_column_to_column(column, to_ip)
