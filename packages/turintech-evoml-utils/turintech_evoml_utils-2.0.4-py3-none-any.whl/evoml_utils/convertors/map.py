"""Module providing utils code for users to convert data."""

# ───────────────────────────────── Imports ────────────────────────────────── #
# Standard Libraries
from typing import Dict, Callable, List

# Private
from evoml_utils.convertors.detected_types import (
    to_float_column,
    convert_percentage_column,
    to_datetime_column,
    convert_phone_number_column,
    convert_unit_number_column,
    convert_currency_column,
    to_bankcode_or_barcode_column,
    to_geo_location_column,
    to_address_column,
    to_map_column,
    to_list_column,
    to_protein_sequence_column,
    identity_convertor,
    to_url_column,
    to_ip_objs_column,
    to_email_objs_column,
    convert_fraction_column,
    to_int_column,
)


from evoml_api_models import DetectedType


TypeConvertor = Callable


type_functions_map: Dict[DetectedType, TypeConvertor] = {
    DetectedType.float: to_float_column,
    DetectedType.integer: to_int_column,
    DetectedType.ip: to_ip_objs_column,
    DetectedType.datetime: to_datetime_column,
    DetectedType.map: to_map_column,
    DetectedType.list: to_list_column,
    DetectedType.bank_code: to_bankcode_or_barcode_column,
    DetectedType.barcode: to_bankcode_or_barcode_column,
    DetectedType.address: to_address_column,
    DetectedType.geo_location: to_geo_location_column,
    DetectedType.unit_number: convert_unit_number_column,
    DetectedType.currency: convert_currency_column,
    DetectedType.percentage: convert_percentage_column,
    DetectedType.fraction: convert_fraction_column,
    DetectedType.email: to_email_objs_column,
    DetectedType.phone: convert_phone_number_column,
    DetectedType.url: to_url_column,
    DetectedType.protein_sequence: to_protein_sequence_column,
    DetectedType.binary: identity_convertor,
    DetectedType.categorical: identity_convertor,
    DetectedType.unknown: identity_convertor,
    DetectedType.unary: identity_convertor,
    DetectedType.text: identity_convertor,
    DetectedType.duplicate: identity_convertor,
    DetectedType.unsupported: identity_convertor,
    DetectedType.sample_id: identity_convertor,
}


# Collecting missing DetectedType values
missing_types: List[str] = [
    detected_type.name for detected_type in DetectedType if detected_type not in type_functions_map
]


# Assert that there are no missing DetectedType values, displaying any missing types
assert not missing_types, f"Missing DetectedType values in type_functions_map: {', '.join(missing_types)}"


def type_to_convert_function(detected_type: DetectedType) -> TypeConvertor:
    """
    Returns the function that should be used to convert a column of the given detected type.

    Args:
        detected_type:
            String that represents one of the detected types.
    Returns:
        Union[Callable[[pd.Series], pd.Series], Callable[[pd.Series, str], pd.Series]]:
            The function that should be used to convert a column with the given detected type.
    """
    if detected_type not in [type_.value for type_ in DetectedType]:
        raise TypeError(f"{detected_type} is not a member of {DetectedType.__name__}.")

    conversion_function = type_functions_map[detected_type]
    return conversion_function
