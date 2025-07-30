#!/usr/bin/env python3
# encoding: utf-8
from typing import Tuple, List, Optional, Dict
import csv
import os
import sys

from pathlib import Path

sys.path.insert(0, str(Path().parent))

import pandas as pd
import numpy as np


# ──────────────────────────────────────────────────────────────────────────── #
def load_dataset(config: Dict, data_file_path: str, need_label: bool = True) -> Tuple[pd.DataFrame, str]:
    """Loads a dataframe from a csv and makes sure that it's compatible with the
    config

    This function's purpose is mainly to perform sanity checks on the duo
    dataframe/config and make sure that they are compatible. It raises a bunch
    of specific errors if anything is wrong.

    We want to automatically detect the delimiter used.

    Args:
        config (dict):
            Config dictionnary containing informations about the data to load
        data_file_path (str):
            Path to a csv/parquet file, usually data.csv/data.parquet

    Returns:
        Tuple:
            data (pd.DataFrame):
                A dataframe loaded from the given csv
            label (str):
                The label provided in the config file

    Raises:
        ValueError:
            If the given path is not a csv/parquet
            If the file does not exist
            If the index column is provided but not present in the file
            If the label column is not specified in the config file
            If the label column is not present in the file
    """
    # ---------------------- Check that the file exists ---------------------- #
    if not (os.path.exists(data_file_path) and os.path.isfile(data_file_path)):
        raise ValueError(f"The provided path ({data_file_path}) does not exist or is not a file")

    # ──────────────────────────── csv behaviour ───────────────────────────── #
    path = Path(data_file_path)
    if path.suffix == ".csv":
        # Encoding and delimiter logic are specific to csv files
        encoding = config.get("encoding", "utf-8")
        delimiter = config.get("delimiter", None)

        if "delimiter" not in config:
            # Detect the separator using python csv sniff method
            with open(path, "r", encoding=encoding) as data_file:
                # Must use all lines to determine delimiter as for text columns they
                # can be over multiple lines so just looking at the first few may
                # truncate these text columns and cause errors.
                try:
                    dialect = csv.Sniffer().sniff(data_file.read())
                    delimiter = dialect.delimiter
                except BaseException:  # sniff() raises a generic exception
                    delimiter = None

        # An explicit None (from the config) means no delimiter
        if delimiter is None:
            data = pd.read_csv(path, encoding=encoding)
        else:
            data = pd.read_csv(path, sep=delimiter, encoding=encoding)
    elif path.suffix == ".parquet":
        data = pd.read_parquet(path)
        data = data.applymap(lambda x: np.nan if isinstance(x, (str, type(None))) and x in ["", None] else x)
    else:
        raise ValueError("{data_file_path.suffix} extensions are not supported")

    # --------------------------- Check for index ---------------------------- #
    index = config.get("indexColumn", None)
    if index is not None:
        if index not in data.columns:
            raise ValueError("The index provided by the config does not exist " "in the csv")

    if not need_label:
        return data, ""

    # --------------------------- Check for label ---------------------------- #
    if "labelColumn" not in config:
        raise ValueError("The labelColumn is not specified in the config")

    label = config["labelColumn"]
    return data, label


def first_valid_extension(path: Path, extensions: List[str]) -> Optional[Path]:
    for ext in extensions:
        if path.with_suffix(ext).is_file():
            return path.with_suffix(ext)
    return None
