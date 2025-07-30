from pydantic import BaseModel
from typing import Optional
from enum import Enum


from evoml_utils.splitting.exceptions import DataSplittingException


class TrainTestSplitMethod(str, Enum):
    """The allowed methods for dividing the data into train and test sets."""

    percentage = "percentage"
    # @pyright: doesn't like the usage of index as a member name
    index = "index"  # type: ignore


class TrainTestSplitWindow(BaseModel):
    """The information defining the window which splits the data into training and test sets."""

    trainRangeFrom: int
    trainLength: int
    testLength: int


class TrainTestSplitConfig(BaseModel):
    """The options selected on the frontend which govern how the data will be divided into train and test sets."""

    method: TrainTestSplitMethod

    trainPercentage: float = 0.8
    lenData: Optional[int] = None

    trainRangeFrom: Optional[int] = None
    trainRangeTo: Optional[int] = None
    testRangeFrom: Optional[int] = None
    testRangeTo: Optional[int] = None


def get_train_test_split_window(split_config: TrainTestSplitConfig) -> TrainTestSplitWindow:
    """Obtain the window which splits the dataset into train and test sets.

    Args:
        split_config (TrainTestSplitConfig): The parameters defining how to perform the train/test split.

    Returns:
        TrainTestSplitWindow: The information defining the window which splits the data into train and test sets.

    """

    if split_config.method == TrainTestSplitMethod.percentage:
        if split_config.lenData is None:
            raise Exception("TrainTestSplitMethod.lenData must be set for train/test split by percentage.")

        train_length = int(split_config.trainPercentage * split_config.lenData)
        test_length = split_config.lenData - train_length
        return TrainTestSplitWindow(trainRangeFrom=0, trainLength=train_length, testLength=test_length)

    if split_config.method == TrainTestSplitMethod.index:
        if split_config.trainRangeTo is None:
            raise Exception("TrainTestSplitConfig.trainRangeTo must be set for train/test split by index.")
        if split_config.trainRangeFrom is None:
            raise Exception("TrainTestSplitConfig.trainRangeFrom must be set for train/test split by index.")
        if split_config.testRangeFrom is None:
            raise Exception("TrainTestSplitConfig.testRangeFrom must be set for train/test split by index.")
        if split_config.testRangeTo is None:
            raise Exception("TrainTestSplitConfig.testRangeTo must be set for train/test split by index.")
        if split_config.testRangeFrom != split_config.trainRangeTo + 1:
            raise DataSplittingException(
                "The testing range must follow immediately after the training range. Found:"
                f"Found: (trainRangeTo, testRangeFrom) = "
                f"({split_config.trainRangeTo},{split_config.testRangeFrom})."
            )
        return TrainTestSplitWindow(
            trainRangeFrom=split_config.trainRangeFrom,
            trainLength=split_config.trainRangeTo + 1 - split_config.trainRangeFrom,
            testLength=split_config.testRangeTo + 1 - split_config.testRangeFrom,
        )

    raise DataSplittingException(f"Unsupported splitting method: {split_config.method}")
