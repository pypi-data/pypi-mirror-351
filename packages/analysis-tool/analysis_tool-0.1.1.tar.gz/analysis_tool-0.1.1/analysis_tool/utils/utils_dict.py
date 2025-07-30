'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-06-19 15:31:32 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-04-29 13:49:40 +0200
FilePath     : utils_dict.py
Description  :

Copyright (c) 2024 by everyone, All Rights Reserved.
'''

import contextlib
import os, sys
import random
import re
import inspect
import textwrap
from itertools import chain
from collections.abc import Mapping
import string
from copy import deepcopy
from pathlib import Path

import numpy as np

from typing import TypedDict, Literal, Optional, Sequence, Union, TypeVar, NamedTuple, Dict, List


import colorama
import warnings
from rich import print as rprint


# ----- Dicitinary part -----
def dict_expand_env_vars(data: dict) -> dict:
    """Recursively expand environment variables."""
    if isinstance(data, dict):
        return {k: dict_expand_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [dict_expand_env_vars(v) for v in data]
    elif isinstance(data, str):
        return os.path.expandvars(data)
    else:
        return data


def compare_dicts(
    dict1: dict,
    dict2: dict,
    flag_dict1='Baseline',
    flag_dict2='Overwriting',
) -> dict:
    """compare two dictionaries iteratively

    Args:
        dict1 (dict): One of the dictionary for camparison
        dict2 (dict): The second dictionary to be compared
        flag_dict1 (str, optional): The description or key for the difference to be stored for the first dictionary. Defaults to 'Baseline'.
        flag_dict2 (str, optional): The description or key for the difference to be stored for the second dictionary. Defaults to 'Overwriting'.

    Returns:
        dict: The dictionary which stores the difference between two input dictionaries.
    """
    dict_diff = {
        flag_dict1: {},
        flag_dict2: {},
    }

    # def _compare_dicts(dict1, dict2, dict_diff_template1, dict_diff_template2):
    #     for key in dict1.keys() & dict2.keys():
    #         if isinstance(dict1.get(key), dict) and isinstance(dict2.get(key), dict):
    #             _compare_dicts(dict1.get(key), dict2.get(key), dict_diff_template1, dict_diff_template2)
    #         elif dict1.get(key) != dict2.get(key):
    #             rprint(f"{key} in baseline dictionary:    {dict1.get(key)}")
    #             rprint(f"{key} in overwriting dictionary: {dict2.get(key)}\n")
    #             if key not in dict_diff_template1:
    #                 dict_diff_template1[key] = dict1.get(key)
    #                 dict_diff_template2[key] = dict2.get(key)
    #             else:
    #                 # add a number to the suffix if the key word is duplicated, start from 1
    #                 for i in range(1, 999):
    #                     _key = f'{key}_{i}'
    #                     if _key not in dict_diff_template1:
    #                         dict_diff_template1[_key] = dict1.get(key)
    #                         dict_diff_template2[_key] = dict2.get(key)
    #                         break

    # _compare_dicts(dict1, dict2, dict_diff[flag_dict1], dict_diff[flag_dict2])

    def _compare_dicts(dict1, dict2, dict_diff_template1, dict_diff_template2, key_previous=None):
        for key in dict1.keys() & dict2.keys():
            if isinstance(dict1.get(key), dict) and isinstance(dict2.get(key), dict):
                _compare_dicts(dict1.get(key), dict2.get(key), dict_diff_template1, dict_diff_template2, key_previous=key)
            elif dict1.get(key) != dict2.get(key):
                if key_previous is None:
                    rprint(f"{key} in baseline dictionary:    {dict1.get(key)}")
                    rprint(f"{key} in overwriting dictionary: {dict2.get(key)}\n")
                    if key not in dict_diff_template1:
                        dict_diff_template1[key] = dict1.get(key)
                        dict_diff_template2[key] = dict2.get(key)
                    else:
                        # add a number to the suffix if the key word is duplicated, start from 1
                        for i in range(1, 999):
                            _key = f'{key}_{i}'
                            if _key not in dict_diff_template1:
                                dict_diff_template1[_key] = dict1.get(key)
                                dict_diff_template2[_key] = dict2.get(key)
                                break

                else:
                    rprint(f"{key_previous} -> {key} in baseline dictionary:    {dict1.get(key)}")
                    rprint(f"{key_previous} -> {key} in overwriting dictionary: {dict2.get(key)}\n")

                    if key_previous not in dict_diff_template1:
                        dict_diff_template1[key_previous] = {key: dict1.get(key)}
                        dict_diff_template2[key_previous] = {key: dict2.get(key)}
                    else:
                        if key not in dict_diff_template1[key_previous]:
                            dict_diff_template1[key_previous][key] = dict1.get(key)
                            dict_diff_template2[key_previous][key] = dict2.get(key)
                        else:
                            # add a number to the suffix if the key word is duplicated, start from 1
                            for i in range(1, 999):
                                _key = f'{key}_{i}'
                                if _key not in dict_diff_template1[key_previous]:
                                    dict_diff_template1[key_previous][_key] = dict1.get(key)
                                    dict_diff_template2[key_previous][_key] = dict2.get(key)
                                    break

    _compare_dicts(dict1, dict2, dict_diff[flag_dict1], dict_diff[flag_dict2])

    return dict_diff


# def update_config(config, overwrite_config) -> dict:
#     """Recursively update dictionary config with overwrite_config.

#     See
#     http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
#     for details.

#     Args:
#       config (dict): dictionary to update
#       overwrite_config (dict): dictionary whose items will overwrite those in config

#     """
#     configNew = deepcopy(config)

#     def _update(d, u):
#         for key, value in u.items():
#             if isinstance(value, Mapping):
#                 d[key] = _update(d.get(key, {}), value)
#             else:
#                 d[key] = value
#         return d

#     _update(configNew, overwrite_config)

#     return configNew

# #####################


def update_config(base_config: dict, overwrite_dict: dict) -> dict:
    """
    Recursively update the base configuration dictionary with values from the overwrite dictionary.

    See
    http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    for details.

    Args:
        base_config (dict): The original configuration dictionary to be updated.
        overwrite_dict (dict): Dictionary whose items will overwrite or update those in the base_config.

    Returns:
        dict: A new dictionary with the merged configuration.

    Note:
        The function will recursively traverse nested dictionaries and update values accordingly.
        If a key in `overwrite_dict` does not exist in `base_config`, it will be added.
        If a key in `overwrite_dict` corresponds to a dictionary, the merge will continue recursively.
        Otherwise, the value in `base_config` will be replaced with the one in `overwrite_dict`.
    """
    # Create a deep copy of the base configuration to avoid modifying the original input
    merged_config = deepcopy(base_config)

    def _recursive_update(orig_dict, new_dict):
        """
        Helper function to recursively update a dictionary with another dictionary's values.

        Args:
            orig_dict (dict): The original dictionary to be updated.
            new_dict (dict): The new dictionary whose values will overwrite those in `orig_dict`.

        Returns:
            dict: The updated dictionary with merged values.

        Note:
            The function will iterate through all keys in `new_dict`. If the key exists in `orig_dict`
            and both values are dictionaries, it will recursively merge the values. Otherwise, the key
            in `orig_dict` will be updated or added with the value from `new_dict`.
        """
        for key, value in new_dict.items():
            # If the key exists in both dictionaries and the value type differs, issue a warning
            if key in orig_dict and not isinstance(value, type(orig_dict.get(key))):
                warnings.warn(
                    f"{colorama.Fore.YELLOW}Type mismatch for key '{key}': original type {type(orig_dict.get(key))} but new type {type(value)}. Overwriting with new value.{colorama.Style.RESET_ALL}"
                )

            # If both values are dictionaries, recursively update them
            if isinstance(value, Mapping) and isinstance(orig_dict.get(key), Mapping):
                orig_dict[key] = _recursive_update(orig_dict.get(key, {}), value)
            else:
                # If the value is not a dictionary or the key does not exist, update the value
                orig_dict[key] = value

        return orig_dict

    # Update the merged configuration with the values from the overwrite dictionary
    _recursive_update(merged_config, overwrite_dict)

    return merged_config


########################


def remove_keys(d: dict, rkeys: list) -> dict:
    """Remove the keys from the dictionary recursively

    Args:
        d (dict): The dictionary to remove the keys from
        rkeys (list): The list of keys to remove

    Returns:
        dict: The dictionary with the keys removed
    """
    # Check input arguments
    rkeys: List = rkeys if isinstance(rkeys, list) else [rkeys]
    _d = deepcopy(d)

    # Remove the keys from the dictionary recursively
    def _remove_keys(d, rkeys):
        if isinstance(d, dict):
            return {k: _remove_keys(v, rkeys) for k, v in d.items() if k not in rkeys}
        else:
            return d

    return _remove_keys(_d, rkeys)


# Basic file operations
