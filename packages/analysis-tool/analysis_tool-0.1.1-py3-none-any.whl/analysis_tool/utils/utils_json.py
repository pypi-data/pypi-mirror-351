'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-06-20 03:10:35 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-04-08 03:33:27 +0200
FilePath     : utils_json.py
Description  :

Copyright (c) 2024 by everyone, All Rights Reserved.
'''

import os, sys
from pathlib import Path
import json
from copy import deepcopy

from .utils_dict import update_config


# Use rich backend for logging
import logging
from rich.logging import RichHandler

# Configure rich logging globally
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%x %X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)  # or "DEBUG"/"WARNING" as needed
logger = logging.getLogger(__name__)


# ----- Json part -----
def read_json(input_file_name: str, mode: list = None, verbose=False) -> dict:
    # read json file
    with open(input_file_name, "r") as f:
        js = json.load(f)

    logger.info(f'Json file read from: {input_file_name}') if verbose else None

    # parse json file into the desired layer
    mode = mode.split(',') if (isinstance(mode, str) and ',' in mode) else mode
    mode = mode if isinstance(mode, list) else [mode]
    js_unfolded = deepcopy(js)

    for m in mode:
        js_unfolded = js_unfolded[m] if m else js_unfolded

    return js_unfolded


def save_json(js: dict, output_file_name: str):
    # Get the absolute path
    output_file_name = str(Path(output_file_name).resolve())
    # Create the directory if not existed
    Path(output_file_name).parent.mkdir(parents=True, exist_ok=True)
    # Save the json file
    with open(output_file_name, 'w') as f:
        json.dump(js, f, indent=4)
    logger.info(f'Json file saved to: {output_file_name}')


def merge_jsonfiles(
    input_jsonfiles: list,
    output_jsonfile: str,
    mode: str = None,
):
    # check input arguments
    input_jsonfiles = input_jsonfiles if isinstance(input_jsonfiles, list) else [input_jsonfiles]

    logger.info(f'Merging json files: {input_jsonfiles} into {output_jsonfile}')

    # read json files
    dict_output = {}
    for input_jsonfile in input_jsonfiles:
        dict_output = update_config(dict_output, read_json(input_jsonfile, mode))
    # write to json file
    save_json(dict_output, output_jsonfile)
