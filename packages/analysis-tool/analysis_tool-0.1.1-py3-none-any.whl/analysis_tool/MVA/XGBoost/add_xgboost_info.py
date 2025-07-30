'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-08-22 04:36:31 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-05-21 10:04:37 +0200
FilePath     : add_xgboost_info.py
Description  :

Copyright (c) 2024 by everyone, All Rights Reserved.
'''

###################
import sys
import os
import argparse
from typing import Dict, List, Optional, Union, Tuple, Any

import pandas as pd
import numpy as np
import uproot as ur
import xgboost as xgb
from xgboost import XGBClassifier

from pathlib import Path
import tempfile

from tqdm import tqdm
from itertools import product
from copy import deepcopy

from .train_xgboost_model import GetModelPath


from analysis_tool.utils.utils_yaml import read_yaml
from analysis_tool.utils.utils_uproot import load_variables_to_pd_by_uproot
from analysis_tool.utils.utils_ROOT import rdfMergeFriends

# Use rich backend for logging
import logging
from rich.logging import RichHandler

# Configure rich logging globally
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%x %X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)

NAN_VALUE = -9999


def clean_data(df: pd.DataFrame, variables: List[str]) -> None:
    """Clean NaN and infinite values in the dataframe."""
    nan_count: int = df[variables].isna().sum().sum()
    inf_count: int = np.isinf(df[variables].values).sum()

    if nan_count > 0 or inf_count > 0:
        logger.warning(f"Found [bold yellow]{nan_count}[/] [bold yellow]NaN[/] values and [bold yellow]{inf_count}[/] [bold yellow]infinite[/] values.", extra={"markup": True})
        logger.info(f"Replacing [bold yellow]NaN[/] and [bold yellow]infinite[/] values with [bold yellow]{NAN_VALUE}[/].", extra={"markup": True})
        df[variables] = df[variables].replace([np.inf, -np.inf], np.nan).fillna(NAN_VALUE)


def read_input_data(
    input_file: str,
    input_tree_name: str,
    bdt_vars: str,
    mode: str,
    num_folds: int,
    split_var: Optional[str],
) -> Tuple[pd.DataFrame, List[str]]:
    """Read and preprocess input data for BDT evaluation."""
    # Read the BDT variables
    BDTvars: List[str] = read_yaml(bdt_vars, mode)

    # Variables to read from the input file to get the BDT response
    vars_to_read: List[str] = BDTvars + [split_var] if num_folds > 0 and split_var is not None else BDTvars

    # Read the input file
    logger.info(f"Reading input file {input_file} with tree {input_tree_name}")
    try:
        df_forpred: pd.DataFrame = load_variables_to_pd_by_uproot(
            input_file,
            input_tree_name=input_tree_name,
            variables=vars_to_read,
            library="pd",
        )
    except Exception as e:
        raise Exception(f"Failed to read input file: {e}")

    return df_forpred, BDTvars


def load_model(model_path: str) -> XGBClassifier:
    """Load XGBoost model from the given path."""
    try:
        model: XGBClassifier = XGBClassifier()
        model.load_model(model_path)
        logger.info(f"Successfully loaded model from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        raise


def apply_single_model(
    df: pd.DataFrame,
    BDTvars: List[str],
    model_path: str,
    output_branch_name: str,
    n_threads: int,
) -> None:
    """Apply a single BDT model to the dataframe."""
    # Load the model
    model: XGBClassifier = load_model(model_path)

    # Set the number of threads
    model.get_booster().set_param('nthread', n_threads)

    # Clean data if needed
    if df[BDTvars].isnull().values.any() or np.isinf(df[BDTvars].values).any():
        logger.warning("Found [bold yellow]NaN[/] or [bold yellow]infinite[/] values. Replacing with [bold yellow]0[/].", extra={"markup": True})
        df[BDTvars] = df[BDTvars].replace([np.inf, -np.inf], np.nan).fillna(-9999)

    # Get predictions
    df[output_branch_name] = model.predict_proba(df[BDTvars])[:, 1]
    logger.info(f"Applied BDT to {len(df)} events")


def apply_kfold_models(df: pd.DataFrame, BDTvars: List[str], model_paths: Dict[int, str], num_folds: int, split_var: str, output_branch_name: str, n_threads: int) -> None:
    """Apply k-fold BDT models to the dataframe based on split variable."""
    df[output_branch_name] = np.nan
    df[split_var] = df[split_var].astype("int64")

    # Process each fold
    for iFold in tqdm(range(num_folds), desc="Adding BDT response", colour="GREEN"):
        model_path: str = model_paths[iFold]
        model: XGBClassifier = load_model(model_path)

        # Set the number of threads
        model.get_booster().set_param('nthread', n_threads)

        # Get the mask for this fold
        fold_mask: np.ndarray = df[split_var] % num_folds == iFold

        # Make predictions only for this fold
        if fold_mask.any():
            fold_data: pd.DataFrame = df.loc[fold_mask, BDTvars]

            # Clean data if needed
            if fold_data.isnull().values.any() or np.isinf(fold_data.values).any():
                logger.warning(f"Found [bold yellow]NaN[/] or [bold yellow]infinite[/] values in fold [bold yellow]{iFold}[/]. Replacing with [bold yellow]{NAN_VALUE}[/].", extra={"markup": True})
                fold_data = fold_data.replace([np.inf, -np.inf], np.nan).fillna(NAN_VALUE)

            # Get predictions
            fold_predictions: np.ndarray = model.predict_proba(fold_data)[:, 1]
            df.loc[fold_mask, output_branch_name] = fold_predictions

            logger.info(f"Applied BDT to {fold_mask.sum()} events in fold {iFold}")
        else:
            logger.info(f"No events to process in fold {iFold}")

    # Check if any folds were not processed
    nan_count_after: int = df[output_branch_name].isna().sum()
    if nan_count_after > 0:
        logger.warning(f"[bold yellow]{nan_count_after}[/] events were not processed in any fold. Filling with [bold yellow]{NAN_VALUE}[/].", extra={"markup": True})
        df[output_branch_name] = df[output_branch_name].fillna(NAN_VALUE)


def save_and_merge_output(
    df: pd.DataFrame,
    input_file: str,
    input_tree_name: str,
    output_file: str,
    output_tree_name: str,
    output_branch_name: str,
    split_var: Optional[str] = None,
    num_folds: int = 0,
) -> None:
    """Save predictions to temporary file and merge with original tree."""

    # Create a reduced dataframe with only the prediction and split variable if needed
    df_output: pd.DataFrame = pd.DataFrame()

    if num_folds > 1 and split_var is not None:
        df_output[split_var] = df[split_var]
    df_output[output_branch_name] = df[output_branch_name]

    # Create the output directory if it doesn't exist
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Generate the temporary output file with the BDT response
    with tempfile.NamedTemporaryFile(prefix=f'{Path(output_file).stem}_temp', suffix=f'{Path(output_file).suffix}', dir=Path(output_file).parent, delete=False) as tmp:
        output_file_tmp: str = Path(tmp.name).resolve().as_posix()

    # Save to temporary ROOT file
    with ur.recreate(output_file_tmp) as f:
        f[output_tree_name] = df_output

    # Merge the BDT response with the original tree
    logger.info(f"Merging the BDT response with the original tree {input_file} -> {output_file}")
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    try:
        rdfMergeFriends(
            input_file_nominal=input_file,
            input_file_friends=[output_file_tmp],
            tree_nominal=input_tree_name,
            tree_friends=[output_tree_name],
            output_file_name=output_file,
            output_tree_name=output_tree_name,
            ignore_kEntriesReshuffled=True,
        )

        # Remove the temporary output file if merge was successful
        logger.info(f"Removing the temporary output file {output_file_tmp}")
        os.remove(output_file_tmp)
    except Exception as e:
        logger.error(f"Failed to merge files: {e}")
        logger.info(f"Keeping temporary file {output_file_tmp} for debugging")
        raise


def add_xgboost_info(
    input_file: str,
    input_tree_name: str,
    bdt_vars: str,
    model_dir: str,
    model_json_name: str,
    mode: str,
    num_folds: int,
    split_var: str,
    output_file: str,
    output_tree_name: str,
    output_branch_name: str,
    n_threads: int,
) -> bool:
    """
    Function:
    ---------
    Loads the trained MVA model and evaluates on both data and MC samples

    Arguments:
    ---------
    input_file:    full path to input file including it's name
    input_tree_name: ttree name in the input file
    bdt_vars: YAML file containing the BDT variables
    model_dir: directory containing the trained models
    model_json_name: name of the model file
    mode: mode to use from the YAML file
    num_folds: number of k-fold cross-validation folds
    split_var: variable to use for splitting the data

    output_file: full path to the output file where it will be written
    output_tree_name: name of the output tree
    output_branch_name: name of the output branch containing the BDT response

    n_threads: number of threads to use

    Output:
    ------
    Stores a root file with the BDT response added as a branch.
    """
    # Read and preprocess input data
    df_forpred, BDTvars = read_input_data(input_file, input_tree_name, bdt_vars, mode, num_folds, split_var)

    # Clean data
    clean_data(df_forpred, BDTvars)

    # Get model paths
    model_paths: Dict[int, str] = GetModelPath(dir_main=model_dir, name_model=model_json_name, nFold=num_folds)

    logger.info("Starting to add BDT response")

    # Apply models based on mode (k-fold or single model)
    if num_folds > 1 and split_var is not None:
        apply_kfold_models(df_forpred, BDTvars, model_paths, num_folds, split_var, output_branch_name, n_threads)
    else:
        apply_single_model(df_forpred, BDTvars, model_paths[0], output_branch_name, n_threads)

    # Save predictions and merge with original file
    save_and_merge_output(df_forpred, input_file, input_tree_name, output_file, output_tree_name, output_branch_name, split_var, num_folds)

    logger.info(f"Successfully added BDT response to {output_file}")
    return True


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-file', type=str, required=True)
    parser.add_argument('--input-tree-name', type=str, required=True)

    parser.add_argument('--bdt-vars', type=str, required=True)

    parser.add_argument('--model-dir', type=str, default='output/models')
    parser.add_argument('--model-json-name', type=str, default='xgb_model.json')

    parser.add_argument('--mode', type=str, required=True)
    parser.add_argument('--num-folds', type=int, default=10)
    parser.add_argument('--split-var', type=str, default='eventNumber')

    parser.add_argument('--output-file', type=str, required=True)
    parser.add_argument('--output-tree-name', type=str, default='DecayTree')

    parser.add_argument('--output-branch-name', type=str, default='bdt')

    parser.add_argument('--n-threads', type=int, default=1, help='Number of threads to use. Default: 0. [0: half of the threads, -1: all threads, other: specific number of threads]')

    return parser


def main(args: Optional[argparse.Namespace] = None) -> None:
    """Main entry point for the script."""
    if args is None:
        args = get_parser().parse_args()
    add_xgboost_info(**vars(args))


if __name__ == "__main__":
    # Run the main function
    main()
