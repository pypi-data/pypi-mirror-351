"""Module providing the model for the splitting configuration and an enum to define the validation methods."""

# ────────────────────────────────── Imports ───────────────────────────────── #
# 3rd party
from typing import Optional, Dict, Any
from pydantic import BaseModel, Extra, Field, root_validator
from enum import Enum


# Private
# @mypy: cannot find stubs because of nuitka compilation
from evoml_api_models import MlTask  # type: ignore

# ──────────────────────────────────────────────────────────────────────────── #


class ValidationMethod(str, Enum):
    """Enumeration of the supported validation methods"""

    cross_validation = "cross-validation"
    holdout = "holdout"
    sliding_window = "sliding-window"
    expanding_window = "expanding-window"
    forecast_holdout = "forecast-holdout"

    def get_option_field(self) -> str:
        """Each enum member has a corresponding option field (where you expect
        to find the config for this method)
        """
        # Convert the current value from 'kebab-case' to 'camelCase'
        words = self.value.split("-")
        camelcase = words[0] + "".join(map(str.capitalize, words[1:]))
        return f"{camelcase}Options"


class CrossValidationOptions(BaseModel, extra=Extra.forbid):
    """Individual parameters for the 'cross-validation' method"""

    folds: int = Field(5, ge=2, le=10)
    keepOrder: bool = False


class HoldoutOptions(BaseModel, extra=Extra.forbid):
    """Individual parameters for the 'holdout' method"""

    size: float = Field(0.01, ge=0.01, le=0.5)
    keepOrder: bool = False


class SlidingWindowOptions(BaseModel, extra=Extra.forbid):
    """Individual parameters for the 'sliding-window' method"""

    horizon: Optional[int] = Field(None, ge=1)
    gap: int = Field(0, ge=0)
    trainWindowLength: Optional[int] = Field(None, ge=1)
    slideLength: Optional[int] = Field(None, ge=1)


class ExpandingWindowOptions(BaseModel, extra=Extra.forbid):
    """Individual parameters for the 'expanding-window' method"""

    horizon: Optional[int] = Field(None, ge=1)
    gap: int = Field(0, ge=0)
    initialTrainWindowLength: Optional[int] = Field(None, ge=1)
    expansionLength: Optional[int] = Field(None, ge=1)


class ForecastHoldoutOptions(BaseModel, extra=Extra.forbid):
    """Individual parameters for the 'forecasting-holdout' method"""

    size: float = Field(0.01, ge=0.01, le=0.5)
    gap: int = Field(0, ge=0)


class ValidationMethodOptions(BaseModel, extra=Extra.forbid):
    method: ValidationMethod = ValidationMethod.cross_validation
    crossValidationOptions: Optional[CrossValidationOptions] = None
    holdoutOptions: Optional[HoldoutOptions] = None
    slidingWindowOptions: Optional[SlidingWindowOptions] = None
    expandingWindowOptions: Optional[ExpandingWindowOptions] = None
    forecastHoldoutOptions: Optional[ForecastHoldoutOptions] = None

    @root_validator
    def check_method_options(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Checks that the option field associated with the current method has
        been provided
        """
        method: ValidationMethod = values["method"]
        options_field = method.get_option_field()
        if values.get(options_field) is None:
            raise ValueError(f"Method {method} requires {options_field} to be non-null")
        return values


class FitEvalSplitConfig(BaseModel, extra=Extra.forbid):
    """Config model containing the parameters used when generating a cross-validator."""

    ml_task: MlTask

    is_time_series: Optional[bool] = None
    len_train: Optional[int] = None
    len_test: Optional[int] = None
    validation: Optional[bool] = None

    validation_method_options: ValidationMethodOptions
