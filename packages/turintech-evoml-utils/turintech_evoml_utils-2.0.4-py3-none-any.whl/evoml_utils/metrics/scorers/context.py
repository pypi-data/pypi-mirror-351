from typing import Optional, List, Tuple


from evoml_api_models import MlTask


class BuildContext:
    """Extra parameters sometimes needed to build MetricSpec scorers"""

    # Encoded positive class. A number between 0 and N-1 corresponding to the
    # positive class of the encoded labels
    positive_y: Optional[int]

    # All encoded classes. must be a list of integers O...N-1 where N is the
    # number of classes. To current knowledge, the encoding algorithm involves
    # sorting the string labels in alphabetical order, then numbering each class
    # from 0 to N-1. This may come in useful should you wish to add the label
    # mappings to the build context in the case where they are not provided by
    # the config.
    labels: Optional[List[int]]
    label_mappings: List[str]
    ml_task: Optional[MlTask]

    # Constant by which all time-based metrics are multiplied. For example, if
    # training time is measured on the whole dataset, setting a
    # normalisation_factor of `1000 / len(X_train)`
    normalisation_factor: Optional[float]

    def __init__(
        self,
        labels: Optional[List[int]] = None,
        label_mappings: Optional[List[str]] = None,
        positive_y: Optional[int] = None,
        ml_task: Optional[MlTask] = None,
        normalisation_factor: Optional[float] = None,
    ):
        self.labels = labels
        self.label_mappings = label_mappings if label_mappings is not None else []
        self.positive_y = positive_y
        self.ml_task = ml_task
        self.normalisation_factor = normalisation_factor

    @staticmethod
    def encode_labels(labels: List[str], positive_y: Optional[str] = None) -> Tuple[List[int], Optional[int]]:
        """Helper function to encode string labels as integers"""
        encoded_labels = list(range(len(labels)))
        encoded_positive_y = encoded_labels[labels.index(positive_y)] if positive_y is not None else positive_y
        return (encoded_labels, encoded_positive_y)


def create_build_context(
    ml_task: MlTask,
    label_mappings: List[str],
    positive_class: Optional[str],
    normalisation_factor: Optional[float] = None,
) -> BuildContext:
    """Helper function to create a suitable build context given the ML Task, the
    string versions of the labels and the positive class and the normalisation
    factor.

    This function does the encoding of the labels into integers using the index
    of each label in the provided list as the integer it will be encoded into.

    """
    labels, positive_y = BuildContext.encode_labels(
        labels=label_mappings,
        positive_y=positive_class,
    )

    return BuildContext(
        labels=labels,
        label_mappings=label_mappings,
        positive_y=positive_y,
        ml_task=ml_task,
        normalisation_factor=normalisation_factor,
    )
