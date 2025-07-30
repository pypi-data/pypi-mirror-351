'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-07-10 17:47:25 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-05-22 10:08:07 +0200
FilePath     : utils_ROOT.py
Description  :

Copyright (c) 2024 by everyone, All Rights Reserved.
'''

# Import the necessary modules
import os
import sys
import glob
from pathlib import Path
import colorama
import warnings
from typing import List, Tuple, Optional, Union
import random

import ROOT as r
from ROOT import (
    vector,
    gInterpreter,
    RDataFrame,
    TObject,
    std,
    gErrorIgnoreLevel,
    kPrint,
    kInfo,
    kWarning,
    kError,
    kBreak,
    kSysError,
    kFatal,
    RDF,
    TFile,
    TChain,
    TCanvas,
    TLegend,
    TGraph,
    gStyle,
    TH1,
    TH2,
    TH3,
    TH1D,
    TH2D,
    TH3D,
)

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


def check_root_file(input_file_name: str, tree_name: str) -> bool:
    """
    Checks if a ROOT file exists, contains a specified tree, and that the tree has non-zero entries.

    Parameters:
        input_file_name (str): The path to the input ROOT file.
        tree_name (str): The name of the tree to check in the ROOT file.

    Returns:
        bool: True if the file exists, contains the tree, and the tree has non-zero entries. False otherwise.
    """
    # Step 1: Check if the file exists
    if not Path(input_file_name).exists():
        logger.error(f'File does not exist: [bold red]{input_file_name}[/]', extra={"markup": True})
        return False

    # Step 2: Open the ROOT file
    try:
        root_file = TFile.Open(input_file_name, "READ")
        if not root_file or root_file.IsZombie():
            logger.error(f'Cannot open ROOT file: [bold red]{input_file_name}[/]', extra={"markup": True})
            return False
    except Exception as e:
        logger.error(f'Error opening file: [bold red]{e}[/]', extra={"markup": True})
        return False

    # Step 3: Check if the specified tree exists
    if not root_file.GetListOfKeys().Contains(tree_name):
        logger.error(f'Tree does not exist: [bold red]{tree_name}[/]', extra={"markup": True})
        root_file.Close()
        return False

    # Step 4: Access the tree and check the number of entries
    tree = root_file.Get(tree_name)
    if not tree:
        logger.error(f'Error retrieving tree: [bold red]{tree_name}[/]', extra={"markup": True})
        root_file.Close()
        return False

    num_entries = tree.GetEntries()
    if num_entries > 0:
        logger.info(f"Tree '{tree_name}' in file '{input_file_name}' has {num_entries} entries.")
        root_file.Close()
        return True
    else:
        logger.error(f'Tree has zero entries: [bold red]{tree_name}[/]', extra={"markup": True})
        root_file.Close()
        return False


# Load the cpp files
global_loaded_cpp_files = []


def load_cpp_file(input_cpp_func_file: Union[str, Path]) -> Tuple[bool, List[Path]]:
    global global_loaded_cpp_files

    if not input_cpp_func_file:
        logger.warning('No input file provided thus no action taken.')
        return (False, global_loaded_cpp_files)

    # Convert input to Path object for easier manipulation
    input_cpp_func_file = Path(input_cpp_func_file).resolve()

    # ------ create a list of all .cpp files to load ------
    # Check if the input is a directory, a specific file, or a pattern
    if input_cpp_func_file.is_dir():
        # It's a directory, load all .cpp files in it
        cpp_files = list(input_cpp_func_file.glob('*.cpp'))
    elif '*' in str(input_cpp_func_file):
        # It's a wildcard pattern
        cpp_files = glob.glob(str(input_cpp_func_file))
        cpp_files = [Path(file).resolve() for file in cpp_files if file.endswith('.cpp')]
    elif input_cpp_func_file.suffix == '.cpp':
        # It's a specific file
        cpp_files = [input_cpp_func_file]
    else:
        logger.warning('No valid .cpp files found or incorrect input')
        return (False, global_loaded_cpp_files)

    # ------ Load each .cpp file found ------
    logger.info(f'Trying to load {len(cpp_files)} .cpp files: \n{cpp_files}')
    for cpp_file in cpp_files:
        # Check if the file has been loaded already
        if cpp_file in global_loaded_cpp_files:
            logger.warning(f'Already loaded [bold yellow]{cpp_file}[/] , will not load again.', extra={"markup": True})
            continue

        gInterpreter.LoadMacro(str(cpp_file))
        logger.info(f'Successfully loaded {cpp_file}')

        # Add the file to the global list of loaded files
        global_loaded_cpp_files.append(cpp_file)

    return (True, global_loaded_cpp_files)


def reset_tree_reshuffled_bit(tree: r.TTree) -> r.TTree:
    # Unset the kEntriesReshuffled bit
    if tree.TestBit(r.TTree.kEntriesReshuffled):
        tree.ResetBit(r.TTree.kEntriesReshuffled)
        logger.warning('Unset the kEntriesReshuffled bit, be careful with this option, it may cause chaos in branch order.')
    return tree


def rdfMergeFriends(
    input_file_nominal: str,
    input_file_friends: Union[str, List[str]],
    tree_nominal: str,
    tree_friends: Union[str, List[str]],
    output_file_name: str,
    output_tree_name: str = 'DecayTree',
    output_branches: Optional[Union[List[str], str]] = None,
    BuildIndex_names: Optional[List[str]] = None,  # [majorname, minorname = '0']
    strict_on_entries: bool = True,
    ignore_kEntriesReshuffled: bool = False,
) -> str:
    # Check input arguments
    input_file_friends = input_file_friends if isinstance(input_file_friends, list) else [input_file_friends]
    tree_friends = tree_friends if isinstance(tree_friends, list) else [tree_friends] * len(input_file_friends)

    BuildIndex_names = BuildIndex_names if isinstance(BuildIndex_names, list) and len(BuildIndex_names) == 2 else [None, '0']
    if BuildIndex_names[0] is None and r.ROOT.IsImplicitMTEnabled():

        raise ValueError(
            f'You are using {colorama.Fore.RED}r.ROOT.EnableImplicitMT(){colorama.Style.RESET_ALL} but you did not specify the {colorama.Fore.RED}BuildIndex_names{colorama.Style.RESET_ALL}. This will result in a crash. Please specify the {colorama.Fore.RED}BuildIndex_names{colorama.Style.RESET_ALL}.'
        )

    # Load the nominal file
    # nominal_tree = TFile(input_file_nominal).Get(tree_nominal)
    nominal_file = TFile(input_file_nominal)
    nominal_tree = nominal_file.Get(tree_nominal)

    # Get the unique branches to save
    unique_branches_to_save = [branch.GetName() for branch in nominal_tree.GetListOfBranches()]

    # Unset the kEntriesReshuffled bit if requested (to carefull with this option)
    if nominal_tree.TestBit(r.TTree.kEntriesReshuffled):
        logger.warning('The nominal tree has been reshuffled')
        if ignore_kEntriesReshuffled:
            logger.warning('Here we will try to reset the status bit and add the friend tree, but please take your own risk')
            reset_tree_reshuffled_bit(nominal_tree)
        else:
            raise RuntimeError('Please check the file')

    # Add the friends
    for i, (input_file_friend, tree_friend) in enumerate(zip(input_file_friends, tree_friends)):
        logger.info(f'Adding friend: {input_file_friend}:{tree_friend}')
        friend_file = TFile(input_file_friend)
        frind_tree = friend_file.Get(tree_friend)

        # Assert the friend tree has the same number of entries as the nominal tree
        if nominal_tree.GetEntries() != frind_tree.GetEntries():
            if strict_on_entries:
                raise AssertionError(
                    f'{colorama.Fore.RED}the friend tree {input_file_friend}:{tree_friend} has a different number of entries than the nominal tree {input_file_nominal}:{tree_nominal}{colorama.Style.RESET_ALL}'
                )
            else:
                logger.warning(
                    f'The friend tree [bold yellow]{input_file_friend}:{tree_friend}[/] has a different number of entries than the nominal tree [bold yellow]{input_file_nominal}:{tree_nominal}[/]',
                    extra={"markup": True},
                )

        # Build index if requested
        friend_tree_column_names = [branch.GetName() for branch in frind_tree.GetListOfBranches()]
        if BuildIndex_names[0] is not None:
            assert BuildIndex_names[0] in friend_tree_column_names, f'ERROR::rdfMergeFriends: The friend tree {input_file_friend}:{tree_friend} does not have the branch {BuildIndex_names[0]}'
            logger.info(f'Building index: {BuildIndex_names[0]}:{BuildIndex_names[1]}')
            frind_tree.BuildIndex(BuildIndex_names[0], BuildIndex_names[1])
            # nominal_tree.BuildIndex('runNumber', 'eventNumber')

        # Unset the kEntriesReshuffled bit if requested (to carefull with this option)
        if frind_tree.TestBit(r.TTree.kEntriesReshuffled):
            logger.warning(f'The friend tree {input_file_friend}:{tree_friend} has been reshuffled')
            if ignore_kEntriesReshuffled:
                logger.warning('Here we will try to reset the status bit, but please take your own risk')
                reset_tree_reshuffled_bit(frind_tree)
            else:
                raise RuntimeError(f'Please check the file')

        nominal_tree.AddFriend(frind_tree, f'{tree_friend}_{i}')
        unique_branches_to_save += [branch.GetName() for branch in frind_tree.GetListOfBranches()]

    unique_branches_to_save = list(set(unique_branches_to_save))

    # Save to the output file
    Path(output_file_name).parent.mkdir(parents=True, exist_ok=True)
    rdf = RDataFrame(nominal_tree)
    if isinstance(output_branches, str) and output_branches.upper() == 'ALL':
        logger.info(f'Saving all branches to {output_file_name}')
        rdf.Snapshot(output_tree_name, output_file_name)
    else:
        unique_branches_to_save = output_branches or unique_branches_to_save
        logger.info(f'Saving branches: {unique_branches_to_save}\n    to {output_file_name}')
        rdf.Snapshot(output_tree_name, output_file_name, unique_branches_to_save)

    return output_file_name


def apply_cut_to_rdf(rdf: RDataFrame, cut_str: str = 'NONE') -> RDataFrame:
    # Apply the cut_str
    cut_str = '' if cut_str.upper().replace(' ', '') in {'NONE', '1>0', '(1>0)'} else cut_str

    if cut_str:
        if rdf.Count().GetValue() > 0:
            logger.info(f'Applying cut: {cut_str}')
            rdf = rdf.Filter(cut_str)
        else:
            logger.warning(f'The dataframe is empty before applying the cut: [bold yellow]{cut_str}[/]', extra={"markup": True})

    return rdf


def add_tmp_var_to_rdf(rdf: RDataFrame, var_expression: str, var_name: Optional[str] = None) -> Tuple[RDataFrame, str]:
    # Define the temporary variable
    var_name = var_name or '__var'
    __variable = var_name

    # Check if the variable name already exists in the dataframe
    n_random_number = 0
    while __variable in rdf.GetColumnNames():
        __variable = f'{__variable}_random{n_random_number}'
        n_random_number += 1

    if n_random_number > 0:
        logger.warning(
            f'The variable name [bold yellow]{var_name}[/] already exists in the dataframe. A random number is added as suffix. The new variable name is [bold yellow]{__variable}[/]',
            extra={"markup": True},
        )

    # Define the variable
    rdf = rdf.Define(__variable, var_expression)

    # Return the dataframe and the temporary variable name
    return rdf, __variable


def add_tmp_weight_to_rdf(
    rdf: RDataFrame,
    weight_expr: str = 'NONE',
    output_weight_name: Optional[str] = None,
) -> Tuple[RDataFrame, str]:
    # Prepare the weight variable

    # Define the temporary weight variable
    output_weight_name = output_weight_name or '__weight'
    __weight_name = output_weight_name

    if (weight_expr) and (weight_expr.replace(' ', '').upper() not in {'NONE', 'ONE', '1'}):
        # Parse the weight string
        weight_expr = weight_expr
    else:
        weight_expr = '1.0'

    # Check if the weight name already exists in the dataframe
    n_random_number = 0
    while __weight_name in rdf.GetDefinedColumnNames():
        __weight_name = f'{__weight_name}_random{n_random_number}'
        n_random_number += 1

    if n_random_number > 0:
        logger.warning(
            f'The weight name [bold yellow]{output_weight_name}[/] already exists in the dataframe. A random number is added as suffix. The new weight name is [bold yellow]{__weight_name}[/]',
            extra={"markup": True},
        )

    # Define the weight variable
    rdf = rdf.Define(__weight_name, weight_expr)

    # Return the dataframe and the temporary weight variable name
    return rdf, __weight_name


def get_sum_weight(rdf: RDataFrame, weight_expr: str, cut: str = 'None') -> float:
    # Apply the cut
    rdf = apply_cut_to_rdf(rdf, cut)

    # Define the temporary weight variable
    __weight_name = '__weight'
    rdf, __weight_name = add_tmp_weight_to_rdf(rdf, weight_expr, __weight_name)

    # Return the sum of the weight
    return rdf.Sum(__weight_name).GetValue()


def get_branch_names(input_file_path: str, input_tree_name: str) -> List[str]:
    """
    Function to get the names of all the branches (columns) in a ROOT TTree.

    Parameters:
    - input_file_path: Path to the input ROOT file.
    - input_tree_name: Name of the TTree in the ROOT file.

    Returns:
    - List of branch (column) names.
    """
    # Open the ROOT file
    tfile = TFile.Open(input_file_path)
    if tfile.IsZombie():
        raise RuntimeError(f"{colorama.Fore.RED}cannot open file {input_file_path}{colorama.Style.RESET_ALL}")

    # Get the TTree from the file
    ttree = tfile.Get(input_tree_name)
    if not ttree:
        raise RuntimeError(f"{colorama.Fore.RED}cannot find tree {input_tree_name} in file {input_file_path}{colorama.Style.RESET_ALL}")

    # Get the list of branch names
    branches = ttree.GetListOfBranches()
    branch_names = [branch.GetName() for branch in branches]

    tfile.Close()

    return branch_names


def get_rdf_with_branches(
    input_file_path: str | list[str],
    input_tree_name: str,
    branches_to_read: str | list[str],
    fill_missing_branches: bool = True,
) -> RDataFrame:
    """
    Function to create an RDataFrame with specified branches from a ROOT file.
    If a branch is missing, it sets that branch to 0 if `fill_missing_branches` is True.

    Parameters:
    - input_file_path: Path or list of paths to the input ROOT files.
    - input_tree_name: Name of the TTree in the ROOT file.
    - branches_to_read: List or single branch name to read.
    - fill_missing_branches: If True, missing branches are set to 0. If False, missing branches are ignored.

    Returns:
    - RDataFrame: A dataframe with the requested branches.
    """

    # Convert the input to a list if it's a single string
    input_file_path = input_file_path if isinstance(input_file_path, list) else [input_file_path]

    # Convert the input to a list if it's a single string
    branches_to_read = branches_to_read if isinstance(branches_to_read, list) else [branches_to_read]
    rprint(f'INFO::get_rdf_with_branches: Requested branches: {branches_to_read}')

    # Get the branch names that are available in the tree
    branches_exist_in_tree = get_branch_names(input_file_path[0], input_tree_name)

    # Identify existing and missing branches
    existing_branches = [br for br in branches_to_read if br in branches_exist_in_tree]
    missing_branches = [br for br in branches_to_read if br not in branches_exist_in_tree]

    # If no branches are missing, create the RDataFrame directly with the requested branches
    # So, at the moment, we could not simply call 'RDataFrame(input_tree_name, input_file_path, branches_to_read)' to read only the requested branches.
    # Hopefully, this will be fixed in the future.
    if not missing_branches:
        rdf = RDataFrame(input_tree_name, input_file_path, branches_to_read)

    # Otherwise, create the RDataFrame with existing branches
    else:
        # There is a bug in RDataFrame. Even if only selected branches are requested, RDataFrame will read all branches.
        rdf = RDataFrame(input_tree_name, input_file_path, existing_branches)

        logger.warning(f'Missing required branches: [bold yellow]{missing_branches}[/]', extra={"markup": True})

        # Handle missing branches
        if fill_missing_branches:
            for branch in missing_branches:
                logger.warning(f'Filling missing branch: [bold yellow]{branch:<40}[/] with 0.0', extra={"markup": True})
                rdf = rdf.Define(branch, "0.0")

        else:
            logger.warning('Ignoring missing branches', extra={"markup": True})

    # Return the RDataFrame
    return rdf


def create_selected_dataframe(input_file: str | list | RDataFrame, tree_name: str, cut_str: str = 'None') -> RDataFrame:
    """Create and prepare a RDataFrame from various input sources."""
    if isinstance(input_file, (str, list)):
        rdf = RDataFrame(tree_name, input_file)
        logger.info(f'Loading tree [bold green]"{tree_name}"[/] from [bold green]{input_file}[/]', extra={"markup": True})
    elif ('ROOT.RDF.RInterface' in str(type(input_file))) or ('ROOT.RDataFrame' in str(type(input_file))):
        rdf = input_file
    else:
        raise TypeError(f"Invalid input type: {type(input_file)}. Expected string, list, or RDataFrame.")

    # Apply selection criteria
    return apply_cut_to_rdf(rdf, cut_str)


def set_branch_status(
    ch: TChain,
    keep_all_branches: bool,
    branch_list: Union[List[str], str],
    status: bool,
) -> None:
    """set branch status helper
    Set branch status.
        ch: [TTree/TChain] tree/chain of the file.
        keep_all_branches: [bool] whether keep all branchs, this operation is on the top of all other status operation.
        branchList: [list] branch which status will be changed (wildcard is supported).
        status: [bool] set branch status, if True: set certain branch status to be true, vice versa.
    Return sum of the weights [float].
    """
    branch_list = [branch_list] if type(branch_list) != type([]) else branch_list

    ch.SetBranchStatus("*", 0) if keep_all_branches else None

    if branch_list:
        for b in branch_list:
            ch.SetBranchStatus(b, status)


def make_TChain(
    input_files: Union[List[str], str],
    input_tree_name: str = "DecayTree",
    cut_string: Optional[str] = None,
    max_run_events: int = -1,
    keep_all_branches: bool = True,
    branch_list: Optional[Union[List[str], str]] = None,
    branch_satus: bool = True,
) -> TChain:
    """make TChain helper
    Helper function to make TChain.
        input_files: [list] input file list which will be cooperated togerther into chain.
        input_tree_name: [str] the name of input tree.
        cut_string: [str] add cuts to the tree if specified.
        max_run_events: [int] maximum of events to run.
        keep_all_branches: [bool] whether keep all branchs, this operation is on the top of all other status operation.
        branchList: [list] branch which status will be changed (wildcard is supported).
        status: [bool] set branch status, if True: set certain branch status to be true, vice versa.
    Return TChain
    """

    input_files = [input_files] if type(input_files) != type([]) else input_files
    ch = TChain(input_tree_name)
    for it in input_files:
        ch.Add(it)

    if branch_list:
        set_branch_status(
            ch=ch,
            keep_all_branches=keep_all_branches,
            branch_list=branch_list,
            status=branch_satus,
        )

    if max_run_events != -1:
        MaxEntries = min(ch.GetEntries(), max_run_events)
        rprint(f"The input file has {ch.GetEntries()} events, and set the maximum of events to run is {max_run_events}.")
    else:
        MaxEntries = ch.GetEntries()

    # MaxEntries = ch.GetEntries() if max_run_events == -1 else max_run_events

    ch_selected = ch.CopyTree(cut_string, "", MaxEntries, 0) if cut_string else ch.CopyTree("1>0", "", MaxEntries, 0)
    if ch_selected.GetEntries() == 0:
        logger.warning('The selected chain has 0 entries.', extra={"markup": True})

    return ch_selected


# save plots from TCanvas
def save_pic_from_tcanvas(canvas: TCanvas, outpic: str, formats: Union[str, List[str]] = "") -> None:
    """Root helper
    Print picture as *.png, *.pdf, *.eps, *.C or customized format.
        canvas: [TCanvas] the prepared canvas to be drawn.
        outpic: [string] the output address of picture to be saved.
        format: [str | list] format of picture to be saved.
    """
    extSuffix = [".pdf", ".png", ".C"]

    outpic = Path(outpic).resolve().as_posix()
    Path(outpic).parent.mkdir(parents=True, exist_ok=True)

    if os.path.splitext(outpic)[1] in extSuffix:
        outpic_noExt = os.path.splitext(outpic)[0]
    else:
        outpic_noExt = outpic

    if not formats:
        formats = extSuffix

    formats = [formats] if type(formats) != type([]) else formats
    for _f in formats:
        _outpic = outpic_noExt + _f
        canvas.SaveAs(_outpic)
