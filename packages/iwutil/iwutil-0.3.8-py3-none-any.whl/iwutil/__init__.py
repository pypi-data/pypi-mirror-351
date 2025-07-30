from . import save
from . import random
import matplotlib.pyplot as plt
import numpy as np
from functools import singledispatch
import pandas as pd
from pathlib import Path
import shutil
import sys
import json


def subplots_autolayout(
    n, *args, n_rows=None, figsize=None, layout="constrained", **kwargs
):
    """
    Create a subplot element with a
    """
    n_rows = n_rows or int(n // np.sqrt(n))
    n_cols = int(np.ceil(n / n_rows))

    figwidth_default = min(15, 4 * n_cols)
    figheight_default = min(8, 1 + 3 * n_rows)
    figsize = figsize or (figwidth_default, figheight_default)
    fig, axes = plt.subplots(
        n_rows, n_cols, *args, figsize=figsize, layout=layout, **kwargs
    )
    # if we just have a single axis, make sure we are returning an array instead
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    axes = axes.flatten()

    return fig, axes


class OptionSpec:
    """
    Specification for an option

    Parameters
    ----------
    default_value : any
        The default value for the option
    other_allowed_values : list, optional
        A list of allowed values for the option, by default None. If None, the value
        can be anything. If a list, the value must be in this list.
    """
    def __init__(self, default_value, other_allowed_values: list | None =None):
        self.default_value = default_value
        self.allowed_values = None
        self.any_value_allowed = True
        if other_allowed_values is not None:
            self.allowed_values = [self.default_value]+other_allowed_values
            self.any_value_allowed = False

def check_and_combine_options(default_options, custom_options=None):
    """
    Check that all required options are provided, and combine default and custom options

    Parameters
    ----------
    default_options : dict
        Dictionary of default options. Each key is an option name, and the value can be
        either:
        - The default value for that option
        - "[required]" if the option must be provided in custom_options
        - A list of allowed values for that option. If the option is not provided in
          custom_options, the first value in the list is used.
    custom_options : dict, optional
        Dictionary of custom options, by default None. If a key in custom_options is not
        in default_options, an error is raised.

    Returns
    -------
    dict
        Combined options

    Raises
    ------
    ValueError
        If a key in custom_options is not in default_options
        If a required option is not provided in custom_options
        If a list option is not one of the allowed values
    """

    if custom_options is None:
        custom_options = {}

    # Check that all custom option keys have a default
    for k in custom_options:
        if k not in default_options:
            raise ValueError(f"Option '{k}' not recognized")

    # If any default options are marked as "[required]", check that they are provided
    # If a default option is a list, check that the custom option value is in that list
    # If a default option is a list and no custom option is provided, use the first value
    combined_options = {}
    for k, v in default_options.items():
        if v == "[required]" and k not in custom_options:
            raise ValueError(f"Option '{k}' is required")
        elif isinstance(v, OptionSpec):
            if k in custom_options:
                if v.any_value_allowed is False and custom_options[k] not in v.allowed_values:
                    raise ValueError(f"Option '{k}' must be one of {v.allowed_values}")
                combined_options[k] = custom_options[k]
            else:
                combined_options[k] = v.default_value
        else:
            combined_options[k] = custom_options.get(k, v)

    return combined_options


@singledispatch
def read_df(file, **kwargs):
    """
    Read a dataframe from a file. Currently supports csv, xls, xlsx, json, and parquet.

    Parameters
    ----------
    file : str or Path
        File to read
    **kwargs : dict
        Additional keyword arguments to pass to the read function
    """
    raise NotImplementedError(f"Reading type {type(file)} not implemented")


@read_df.register
def _(file: str, **kwargs):
    return iwutil_file_path_helper(file, **kwargs)


@read_df.register
def _(file: Path, **kwargs):
    return iwutil_file_path_helper(file, **kwargs)


@read_df.register
def _(file: pd.DataFrame, **kwargs):
    return file


def iwutil_file_path_helper(file_name: str | Path, **kwargs):
    file_extension = Path(file_name).suffix[1:]

    if file_extension == "csv":
        return pd.read_csv(file_name, **kwargs)
    elif file_extension in ["xls", "xlsx"]:
        return pd.read_excel(file_name, **kwargs)
    elif file_extension == "json":
        return pd.read_json(file_name, **kwargs)
    elif file_extension == "parquet":
        return pd.read_parquet(file_name, **kwargs)
    elif file_extension == "txt":
        if "sep" not in kwargs:
            kwargs["sep"] = "\t"
        return pd.read_csv(file_name, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def read_json(file_name):
    """
    Read a json file and sanitize the input

    Parameters
    ----------
    file_name : str or Path
        File to read
    """
    with open(file_name, encoding='utf-8') as f:
        return json.load(f)


def copyfile(src, dst):
    """
    Copy a file from src to dst, creating the parent directory if it does not exist

    Parameters
    ----------
    src : str or Path
        Source file
    dst : str or Path
        Destination file
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def this_dir(file):
    """
    Get the directory of the file
    """
    return Path(file).parent

def append_path(path):
    """
    Append a path to the current path

    Parameters
    ----------
    path : str or Path
        Path to append
    """
    sys.path.append(str(path))
