'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-02-10 17:45:40 +0100
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-05-23 03:34:57 +0200
FilePath     : apply_selection.py
Description  :

Copyright (c) 2024 by everyone, All Rights Reserved.
'''

import os, sys, argparse, glob
import yaml
import cppyy
from pathlib import Path
from typing import Dict, List, Optional, Union
import multiprocessing
import colorama
import copy

import ROOT as r
from ROOT import vector, gInterpreter, RDataFrame, TObject, std
from ROOT import gErrorIgnoreLevel, kPrint, kInfo, kWarning, kError, kBreak, kSysError, kFatal


from rich import print as rprint

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


from .utils.utils_ROOT import load_cpp_file
from .constants.constants import constant_table_flattened as CONSTANTS


def read_from_yaml(mode: Optional[str], selection_files: Union[str, List[str]]) -> Dict:
    """
    Read and merge selection dictionaries from YAML files.

    Args:
        mode: Selection mode to extract from YAML
        selection_files: YAML file(s) containing selection criteria

    Returns:
        Dictionary of merged selection criteria
    """
    # Check input arguments
    selection_files = selection_files if isinstance(selection_files, list) else [selection_files]

    selection_dict = {}
    for file in selection_files:
        with open(file, 'r') as stream:
            loaded_data = yaml.safe_load(stream)
            # If mode is specified, extract that section; otherwise use the whole file
            if mode:
                if mode not in loaded_data:
                    raise ValueError(f"Mode {mode} not found in {file}")
                section_data = loaded_data[mode]
            else:
                section_data = loaded_data

            # Merge the section data into the selection dictionary
            selection_dict |= section_data

    return selection_dict


def apply_cuts(cuts: Dict[str, str], dataframe: RDataFrame, year: str) -> RDataFrame:
    """
    Apply cuts defined in the cuts dictionary to the dataframe.

    Args:
        cuts: Dictionary mapping cut names to their expressions
        dataframe: RDataFrame to apply cuts to
        year: Year to format into cut strings

    Returns:
        Filtered RDataFrame
    """
    for key in cuts:
        if cut := cuts[key].format(year=year, **CONSTANTS):
            dataframe = dataframe.Filter(cut, key)

    # Print cut efficiencies
    report = dataframe.Report()
    report.Print()
    return dataframe


def apply_selection(
    input_files: Union[str, List[str]],
    input_tree_name: str,
    output_file: str,
    output_tree_name: str,
    mode: Optional[str],
    cut_keys: List[str],
    cut_string: Optional[str],
    selection_files: Optional[List[str]],
    branches_files: Optional[List[str]],
    keep_all_original_branches: str,
    year: str,
    input_cpp_func_file: Optional[str] = None,
    n_threads: int = 1,
    n_events: int = -1,  # Only run first n_events, -1 means all events
) -> None:
    """
    Apply selection criteria to ROOT files and save results.

    Args:
        input_files: Input ROOT file(s) to process
        input_tree_name: Name of the input tree
        output_file: Path to the output ROOT file
        output_tree_name: Name of the output tree
        mode: Selection mode from YAML files
        cut_keys: Names of cuts to apply from YAML files
        cut_string: Optional explicit cut string
        selection_files: YAML files containing selection criteria
        branches_files: YAML files containing branch definitions
        keep_all_original_branches: Whether to retain all original branches ('TRUE'/'FALSE')
        year: Data-taking year for parameter substitution
        input_cpp_func_file: Optional C++ file with custom functions
        n_threads: Number of threads for parallel processing
        n_events: Number of events to process (-1 for all)
    """
    # Configure multithreading
    if n_threads == 1 or n_events != -1:
        r.ROOT.DisableImplicitMT()
    else:
        n_threads = multiprocessing.cpu_count() if n_threads < 0 else n_threads
        logger.info(f'Setting number of threads to {n_threads}')
        r.ROOT.EnableImplicitMT(n_threads)

    # Validate and prepare output path
    output_file = str(Path(output_file).resolve())
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Validate keep_all_original_branches
    keep_all = keep_all_original_branches.upper()
    if keep_all not in {'TRUE', 'FALSE'}:
        raise ValueError(f'keep_all_original_branches must be either TRUE or FALSE, got {keep_all_original_branches}')

    # Load the custom cpp functions to be used in the dataframe
    if input_cpp_func_file:
        load_cpp_file(input_cpp_func_file)
    # else:
    #     # Load the default cpp files
    #     input_cpp_func_file_default = f'{_current_module_dir}/cppfuncs'
    #     print(f'INFO::apply_selection: Loading default cpp files from {input_cpp_func_file_default}')
    #     load_cpp_file(input_cpp_func_file_default)

    # Prepare input files
    input_files: List[str] = input_files if isinstance(input_files, list) else [input_files]
    names = std.vector('string')()
    for n in input_files:
        names.push_back(n if n.endswith('.root') else f'{n}*.root')
    logger.info(f'Specified input files:\n{names}')

    # Create RDataFrame and apply range if specified
    dataframe = RDataFrame(input_tree_name, names)
    if n_events > 0:
        logger.info(f'Running on the first {n_events} events only')
        dataframe = dataframe.Range(0, n_events)

    # Read and prepare cuts
    cuts = {}
    if selection_files:
        cuts |= read_from_yaml(mode, selection_files)

    # if cut keys are specified apply only desired cuts for given mode
    if 'all' not in cut_keys:
        _cuts = copy.deepcopy(cuts)
        cuts = {}
        for cut_key in cut_keys:
            if cut_key in _cuts:
                cuts[cut_key] = _cuts[cut_key]
            else:
                raise ValueError(f'Cut key {cut_key} not found in selection files')

    # if cut string is specified create corresponding cuts dictionary
    if (cut_string) and (cut_string.strip().upper() not in {'NONE', '(1>0)', '1>0'}):
        cuts |= {cut_string: cut_string}

    # read branches from all input files
    branches_to_add = read_from_yaml(mode, branches_files) if branches_files else {}

    if branches_to_add:  # If wanted to add new branches
        # get list of existing branches
        branches_in_df = dataframe.GetColumnNames()

        # define new branches and keep original branches if specified
        branches = vector('string')()
        if keep_all_original_branches.upper() == 'TRUE':
            branches = branches_in_df

        # add new branches
        for branch in branches_to_add.keys():
            # Format branch expression with constants
            branch_value = branches_to_add[branch].format(year=year, **CONSTANTS)

            # Check the validity of the branch value, if it is empty, then skip the branch
            if not branch_value:
                logger.warn(f"Branch [bold yellow]{branch}[/] value is empty. Skipping branch.", extra={"markup": True})
                continue

            # Check if the branch is already present in the original tree
            # 1.) Overwrite the existing branch if it is already present in the original tree
            if branch in branches_in_df:
                # If branch == branch_value, then just push the branch into the list; if not, then define the branch
                if branch != branch_value:

                    # Check whether the branch_value can be parsed correctly or not. Otherwise, keep the original branch value.
                    try:
                        # Set the error level to suppress certain messages
                        # kFatal, kError, kWarning, kInfo, kDebug are the levels you can use
                        gErrorIgnoreLevel = kFatal  # Suppress warnings and below

                        # Try to redefine the branch with the new value
                        __dataframe_tmp = dataframe.Redefine(branch, branch_value)
                        # Reset the error level to default (typically kInfo to see all messages)
                        gErrorIgnoreLevel = kInfo

                        # If the branch value can be parsed correctly, then redefine the branch
                        logger.warn(f"Branch [bold yellow]{branch}[/] is already present in the original tree. OVERWRITING the branch with [bold yellow]{branch_value}[/].", extra={"markup": True})

                        dataframe = dataframe.Redefine(branch, branch_value)
                    except Exception:
                        logger.warn(
                            f"Branch [bold yellow]{branch}[/] is already present in the original tree. And [bold yellow]{branch_value}[/] did NOT parse correctly, KEEP the ORIGINAL value.",
                            extra={"markup": True},
                        )

            else:
                # 2.) If the branch value is the same as the branch name, then it is a constant value
                if branch == branch_value:
                    logger.warn(f"Branch [bold yellow]{branch}[/] is not present in the original tree. Setting value to [bold yellow]-99999.0[/].", extra={"markup": True})

                    dataframe = dataframe.Define(branch, "-99999.0")
                # 3.) Add new branch if not present in the original tree
                else:
                    dataframe = dataframe.Define(branch, branch_value)

            # Add branch to output if not already included
            if branch not in branches:
                branches.push_back(branch)

        # apply all cuts
        if cuts:
            dataframe = apply_cuts(cuts, dataframe, year)

        # save new tree
        logger.info('Branches kept in the pruned tree:')
        rprint(branches)
        dataframe.Snapshot(output_tree_name, output_file, branches)
    else:
        # apply all cuts
        if cuts:
            dataframe = apply_cuts(cuts, dataframe, year)
        # save new tree
        logger.info('All branches are kept in the tree')
        dataframe.Snapshot(output_tree_name, output_file)


def get_parser() -> argparse.ArgumentParser:
    """Create and configure command line argument parser."""
    parser = argparse.ArgumentParser(description="Apply selection criteria to ROOT files")
    parser.add_argument('--input-files', nargs='+', required=True, help='Path to input ROOT file(s)')
    parser.add_argument('--input-tree-name', default='DecayTree', help='Name of the input tree')
    parser.add_argument('--output-file', required=True, help='Output ROOT file path')
    parser.add_argument('--output-tree-name', default='DecayTree', help='Name of the output tree')
    parser.add_argument('--mode', help='Selection mode from YAML files')
    parser.add_argument('--cut-keys', default=['all'], nargs='+', help='Specific cuts to apply from YAML')
    parser.add_argument('--cut-string', default=None, help='Alternatively, specify cut string directly')
    parser.add_argument('--selection-files', nargs='+', help='YAML files with selection criteria')
    parser.add_argument('--branches-files', nargs='+', help='YAML files with branch definitions')
    parser.add_argument('--keep-all-original-branches', type=str, default='False', help='Keeps all original branches if True, only adds specified branches if False')
    parser.add_argument('--year', required=True, help='Data-taking year')
    parser.add_argument('--input-cpp-func-file', default=None, help='Path to the cpp file with custom functions')
    parser.add_argument('--n-threads', type=int, default=1, help='Number of threads to use. Default is 1 (No multithreading enabled), set to -1 to use all available cores.')
    parser.add_argument('--n-events', type=int, default=-1, help='Number of events to process. Default is -1 (All events)')

    return parser


def main(args=None):
    """Main entry point for the script."""
    if args is None:
        args = get_parser().parse_args()
    apply_selection(**vars(args))


if __name__ == '__main__':
    main()
