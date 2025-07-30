'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-06-19 16:49:33 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-05-14 09:48:07 +0200
FilePath     : utils_histo.py
Description  :

Copyright (c) 2024 by everyone, All Rights Reserved.
'''

import sys, os
import random
from datetime import datetime
from typing import Union, Dict, List, Tuple, Optional


import math
import pandas as pd
import numpy as np
import ROOT as r
from ROOT import gROOT, gStyle
from ROOT import RDF, RDataFrame, TFile
from ROOT import TCanvas, TLegend, TGraph, TRatioPlot
from ROOT import TH1, TH2, TH3, TH1D, TH2D, TH3D, TH1F, TH2F, TH3F

from pathlib import Path
from itertools import product
import colorama
import warnings
from rich import print as rprint

from .utils_yaml import read_yaml
from .utils_ROOT import apply_cut_to_rdf, add_tmp_var_to_rdf, add_tmp_weight_to_rdf, create_selected_dataframe


def get_full_hist_title(hist: TH1 | TH2 | TH3) -> str:
    """
    Get the full title of a histogram including all axis titles.

    Args:
        hist: ROOT histogram object (TH1, TH2, or TH3)

    Returns:
        str: Complete title with axis labels separated by semicolons
    """
    # Get the main title
    title: str = hist.GetTitle()
    titles: list[str] = [title]

    # Map dimension index to axis name
    axes: dict[int, str] = {0: 'X', 1: 'Y', 2: 'Z'}

    # Get the title for each axis based on histogram dimension
    for i in range(hist.GetDimension()):
        axis = getattr(hist, f'Get{axes[i]}axis')()
        titles.append(axis.GetTitle())

    # Join all titles with semicolons (ROOT title format)
    return ";".join(titles)


def construct_histo_template_from_yaml(input_yaml_file: str | dict, mode: str | list, histo_name: str = None) -> TH1 | TH2 | TH3:
    """
    Construct a ROOT histogram from a YAML configuration file.

    Args:
        input_yaml_file: Path to YAML file or dict with histogram configuration
        mode: Mode or section to read from the YAML file
        histo_name: Optional name for the created histogram

    Returns:
        A ROOT histogram (TH1D, TH2D, or TH3D) based on the configuration

    Raises:
        AssertionError: If input file doesn't exist
        KeyError: If required configuration keys are missing
    """
    # Check whether input file exists
    if isinstance(input_yaml_file, str):
        assert Path(input_yaml_file).is_file(), f"Input file {input_yaml_file} does not exist!"

    # Read histogram template from the yaml file
    config = read_yaml(input_yaml_file, mode)

    # Validate dimension
    dim = config.get('dim')
    if dim not in [1, 2, 3]:
        raise ValueError(f"Invalid histogram dimension: {dim}. Must be 1, 2, or 3.")

    # Create histogram based on dimension
    if dim == 1:
        axis_x = config['x']
        hist = TH1D(
            config['name'],
            f";{axis_x['title']}",
            int(axis_x['nbins']),
            float(axis_x['min']),
            float(axis_x['max']),
        )
    elif dim == 2:
        axis_x, axis_y = config['x'], config['y']
        hist = TH2D(
            config['name'],
            f";{axis_x['title']};{axis_y['title']}",
            int(axis_x['nbins']),
            float(axis_x['min']),
            float(axis_x['max']),
            int(axis_y['nbins']),
            float(axis_y['min']),
            float(axis_y['max']),
        )
    elif dim == 3:
        axis_x, axis_y, axis_z = config['x'], config['y'], config['z']
        hist = TH3D(
            config['name'],
            f";{axis_x['title']};{axis_y['title']};{axis_z['title']}",
            int(axis_x['nbins']),
            float(axis_x['min']),
            float(axis_x['max']),
            int(axis_y['nbins']),
            float(axis_y['min']),
            float(axis_y['max']),
            int(axis_z['nbins']),
            float(axis_z['min']),
            float(axis_z['max']),
        )

    # Return the histogram, cloning if a new name is provided
    return hist if histo_name is None else hist.Clone(histo_name)


def copy_histo_to_float_precision(hist: TH1 | TH2 | TH3) -> TH1F | TH2F | TH3F:
    """
    Copy a histogram to a float precision histogram.
    """

    assert isinstance(hist, TH1 | TH2 | TH3), f"Input must be a ROOT histogram (TH1, TH2, or TH3), not {type(hist)}"

    # Create the appropriate histogram type
    if isinstance(hist, TH3):
        hist_d = r.TH3F()
    elif isinstance(hist, TH2):
        hist_d = r.TH2F()
    else:
        hist_d = r.TH1F()

    # Copy template to the new histogram
    hist.Copy(hist_d)
    hist_d.SetName(hist.GetName())

    return hist_d


def copy_histo_to_double_precision(hist: TH1 | TH2 | TH3) -> TH1D | TH2D | TH3D:
    """
    Copy a histogram to a double precision histogram.
    """

    assert isinstance(hist, TH1 | TH2 | TH3), f"Input must be a ROOT histogram (TH1, TH2, or TH3), not {type(hist)}"

    # Create the appropriate histogram type
    if isinstance(hist, TH3):
        hist_d = r.TH3D()
    elif isinstance(hist, TH2):
        hist_d = r.TH2D()
    else:
        hist_d = r.TH1D()

    # Copy template to the new histogram
    hist.Copy(hist_d)
    hist_d.SetName(hist.GetName())

    return hist_d


def set_bins_to_value(hist: TH1 | TH2 | TH3, value: float = 1.0e-6, error: float = 1.0) -> TH1 | TH2 | TH3:
    """
    Set all bins of a histogram to a specific value and error.

    Args:
        hist: ROOT histogram (TH1, TH2, or TH3)
        value: Value to set for each bin content (default: 1.0e-6)
        error: Error to set for each bin (default: 1.0)

    Returns:
        The modified histogram

    Raises:
        TypeError: If the input is not a valid ROOT histogram
    """
    # Determine histogram dimension
    if isinstance(hist, TH3):
        # 3D histogram
        for i, j, k in product(range(1, hist.GetNbinsX() + 1), range(1, hist.GetNbinsY() + 1), range(1, hist.GetNbinsZ() + 1)):
            hist.SetBinContent(i, j, k, value)
            hist.SetBinError(i, j, k, abs(error))

    elif isinstance(hist, TH2):
        # 2D histogram
        for i, j in product(range(1, hist.GetNbinsX() + 1), range(1, hist.GetNbinsY() + 1)):
            hist.SetBinContent(i, j, value)
            hist.SetBinError(i, j, abs(error))

    elif isinstance(hist, TH1):
        # 1D histogram
        for i in range(1, hist.GetNbinsX() + 1):
            hist.SetBinContent(i, value)
            hist.SetBinError(i, abs(error))

    else:
        raise TypeError(f"Unsupported histogram type: {type(hist)}")

    return hist


def fill_hist_template_from_rdf(rdf: RDataFrame, variables: str | list[str], weight: str, hist_template: TH1 | TH2 | TH3) -> TH1 | TH2 | TH3:
    """Fill a histogram from RDataFrame data using the template."""

    assert isinstance(hist_template, TH1 | TH2 | TH3), f"Input must be a ROOT histogram (TH1, TH2, or TH3), not {type(hist_template)}"

    # Normalize variables to list format
    vars_list = variables if isinstance(variables, list) else [variables]

    # Add variables to RDataFrame
    temp_vars = []
    for i, var in enumerate(vars_list):
        rdf, temp_var = add_tmp_var_to_rdf(rdf, var, f'__var{i}')
        temp_vars.append(temp_var)

    # Add weight variable
    rdf, temp_weight = add_tmp_weight_to_rdf(rdf, weight)

    # copy the histogram to double precision which is required by RDF
    hist_d = copy_histo_to_double_precision(hist_template)

    # Reset the histogram to remove any existing content
    hist_d.Reset()

    # Create the appropriate histogram type with double precision
    if isinstance(hist_template, TH3):
        result: TH3 = rdf.Histo3D(r.ROOT.RDF.TH3DModel(hist_d), *temp_vars, temp_weight).GetValue()
    elif isinstance(hist_template, TH2):
        result: TH2 = rdf.Histo2D(r.ROOT.RDF.TH2DModel(hist_d), *temp_vars, temp_weight).GetValue()
    else:
        result: TH1 = rdf.Histo1D(r.ROOT.RDF.TH1DModel(hist_d), *temp_vars, temp_weight).GetValue()

    # Proper error handling (THn::Clone copies the Sumw2 setting, but THnDModel only copies name, title and axes parameters, not further settings.)
    result.Sumw2()

    # Ensure title is preserved
    result.SetTitle(get_full_hist_title(hist_template))

    return result


def get_histo_with_given_template_from_rdf(
    rdf: RDataFrame,
    variables: str | list[str],
    weight: str,
    hist_template: TH1 | TH2 | TH3,
    output_hist_name: str,
    *,
    cut_str: str = 'NONE',
    fill_histo_if_empty: bool = False,
) -> TH1 | TH2 | TH3:
    """
    Create a histogram from data using a template histogram for binning and axis properties.

    Args:
        rdf: RDataFrame containing the data
        variables: Variable(s) to plot (must match histogram dimension)
        weight: Expression for the event weight
        hist_template: Template histogram defining binning and axes
        output_hist_name: Name for the output histogram
        cut_str: Selection criteria to apply to the data
        fill_histo_if_empty: If True, fills histogram with small values when dataframe is empty

    Returns:
        Filled histogram with properties from the template

    Raises:
        ValueError: If number of variables doesn't match histogram dimension
        TypeError: If inputfile has invalid type
    """
    # Create the histogram from template
    hist = hist_template.Clone(output_hist_name)
    hist.Sumw2()  # Enable proper error calculation

    # Create RDataFrame from input
    rdf = apply_cut_to_rdf(rdf, cut_str)

    # Process data if available
    if rdf.Count().GetValue() > 0:

        # fill the histogram from the rdf
        hist = fill_hist_template_from_rdf(rdf, variables, weight, hist)

    else:
        warnings.warn(f'The dataframe is empty after applying the cut: {cut_str}')
        if fill_histo_if_empty:
            rprint(f'Filling histogram "{output_hist_name}" with default values (1e-6)')

            # copy the histogram to double precision which is required by RDF
            hist_d = copy_histo_to_double_precision(hist)

            # fill the histogram with default values
            hist = set_bins_to_value(hist_d, 1e-6)

    # Preserve full title information from template
    hist.SetTitle(get_full_hist_title(hist_template))

    return hist


def get_histo_with_given_template_from_file(
    inputfile: str | list | RDataFrame,
    variables: str | list[str],
    weight: str,
    hist_template: TH1 | TH2 | TH3,
    output_hist_name: str,
    tree_name: str = 'DecayTree',
    cut_str: str = 'NONE',
    fill_histo_if_empty: bool = False,
) -> TH1 | TH2 | TH3:
    """
    Create a histogram from data using a template histogram for binning and axis properties.

    Args:
        inputfile: ROOT file path(s) or RDataFrame containing the data
        variables: Variable(s) to plot (must match histogram dimension)
        weight: Expression for the event weight
        hist_template: Template histogram defining binning and axes
        output_hist_name: Name for the output histogram
        tree_name: Name of the tree in ROOT file(s) (ignored if inputfile is RDataFrame)
        cut_str: Selection criteria to apply to the data
        fill_histo_if_empty: If True, fills histogram with small values when dataframe is empty

    Returns:
        Filled histogram with properties from the template

    Raises:
        ValueError: If number of variables doesn't match histogram dimension
        TypeError: If inputfile has invalid type
    """

    # Create RDataFrame from input
    rdf = create_selected_dataframe(inputfile, tree_name, cut_str)

    # Get the histogram from the RDataFrame
    hist = get_histo_with_given_template_from_rdf(
        rdf,
        variables,
        weight,
        hist_template,
        output_hist_name,
        cut_str=cut_str,
        fill_histo_if_empty=fill_histo_if_empty,
    )

    return hist


def normalize_histogram_integral(h, value_target: float = 1) -> TH1 | TH2 | TH3:
    scale = value_target / h.Integral()
    h.Scale(scale)
    return h


def get_legend_option_from_draw_option(obj):
    # draw_option = draw_option.lower()

    draw_option = obj.GetDrawOption().lower()

    if isinstance(obj, TH1):
        if "hist" in draw_option:
            return "l"  # Histogram drawn as a line
        elif "e" in draw_option:
            return "lep"  # Histogram with error bars
        elif obj.GetFillStyle() != 0:
            return "f"  # Filled histograms
        else:
            return "l"  # Default to line if unsure
    elif isinstance(obj, TGraph):
        if "p" in draw_option:
            return "p"  # Graph with markers
        elif "l" in draw_option:
            return "l"  # Graph with a line
        elif "f" in draw_option:
            return "f"  # Filled graph (rare)
        else:
            return "lp"  # Default to line and marker if unsure
    # ... Additional checks for other ROOT object types
    return ""


def calculate_y_axis_range(histos, optimise_range: bool = True):
    """
    Calculate the Y-axis range for a set of histograms.

    Parameters:
    histos (list or ROOT.TH1): A list of histograms or a single histogram.
    optimise_range (bool): If True, optimizes the y-axis range.

    Returns:
    tuple: A tuple containing the minimum and maximum Y-axis values.

    Raises:
    ValueError: If 'histos' is empty or contains invalid elements.
    """

    if not isinstance(histos, list):
        histos = [histos]
    if not histos or any(not hasattr(h, 'GetMinimum') for h in histos):
        raise ValueError("Invalid input: 'histos' must be a list of histograms.")

    y_min = min(h.GetMinimum() for h in histos)
    y_max = max(h.GetMaximum() for h in histos)

    if optimise_range:
        y_min = max(y_min, 0) if y_min >= 0 else y_min * 1.1
        y_max *= 1.1

    return (y_min, y_max)


def get_unique_hist_name(target_name: str) -> str:
    """
    Generate a unique name for a histogram.
    """

    attempt = 0
    while gROOT.FindObject(target_name):
        attempt += 1
        timestamp = datetime.now().strftime('%S%f')
        target_name = f"{target_name}_{attempt}_{timestamp}"
        rprint(f"Object with name {target_name.rsplit('_', 2)[0]} already exists.")

    rprint(f"Using {target_name} as the histogram name.")

    return target_name


def get_hist_from_file(file_path: str, hist_name: str, new_hist_name: str = None) -> TH1 | TH2 | TH3:
    """
    Retrieve a histogram from a ROOT file with proper memory management.

    Args:
        file_path: Path to the ROOT file
        hist_name: Name of the histogram to retrieve
        new_hist_name: Optional new name for the retrieved histogram

    Returns:
        The retrieved histogram (TH1, TH2, or TH3)

    Raises:
        FileNotFoundError: If file cannot be opened or histogram not found
    """
    # Generate a unique name if none provided
    target_name = hist_name if new_hist_name is None else new_hist_name

    # Check if an object with this name already exists
    if gROOT.FindObject(target_name):
        warnings.warn(f"Object with name {target_name} already exists, please consider using a unique name for the histogram.")

        # Generate a unique name
        # target_name = get_unique_hist_name(target_name)

    # Open the file
    root_file = TFile.Open(file_path, "READ")
    if not root_file or root_file.IsZombie():
        raise FileNotFoundError(f"{colorama.Fore.RED}Unable to open file: {file_path}{colorama.Style.RESET_ALL}")

    # Get the histogram
    hist_obj = root_file.Get(hist_name)
    if not hist_obj:
        root_file.Close()
        raise FileNotFoundError(f"{colorama.Fore.RED}Unable to find histogram: {hist_name} in file: {file_path}{colorama.Style.RESET_ALL}")

    # Clone and verify the histogram

    histogram = hist_obj.Clone(target_name)

    if not histogram or not histogram.InheritsFrom("TH1"):
        root_file.Close()
        raise ValueError(f"{colorama.Fore.RED}Object {hist_name} in file {file_path} is not a valid histogram{colorama.Style.RESET_ALL}")

    # Detach from file and close
    histogram.SetDirectory(0)

    root_file.Close()

    return histogram


def get_hists_from_ROOT_to_dict(input_file_path: str, hist_name_suffix: str = "") -> dict[str, TH1]:
    """
    Extract all histograms from a ROOT file into a dictionary.

    Args:
        input_file_path: Path to the ROOT file
        hist_name_suffix: Optional suffix to append to histogram names (default: "")

    Returns:
        Dictionary mapping original histogram names to their cloned objects

    Raises:
        FileNotFoundError: If the file cannot be opened
        RuntimeError: If no histograms are found in the file
    """
    # Log the operation
    rprint(f'Reading histograms from {input_file_path}')

    # Open the ROOT file
    root_file = TFile.Open(input_file_path, "READ")
    if not root_file or root_file.IsZombie():
        raise FileNotFoundError(f"{colorama.Fore.RED}Unable to open file: {input_file_path}{colorama.Style.RESET_ALL}")

    # Dictionary to store the histograms
    histograms = {}

    # Process histogram suffix
    suffix = f"_{hist_name_suffix}" if hist_name_suffix else ""

    # Loop over all keys in the ROOT file
    for key in root_file.GetListOfKeys():
        obj = key.ReadObj()

        # Check if object is a histogram
        if obj and obj.InheritsFrom("TH1"):
            orig_name = obj.GetName()
            new_name = f"{orig_name}{suffix}"

            # Clone the histogram with the new name
            hist_clone = obj.Clone(new_name)

            # Detach from file to prevent deletion when file is closed
            hist_clone.SetDirectory(0)

            # Store in dictionary using original name as key
            histograms[orig_name] = hist_clone

    # Close the file after processing all objects
    root_file.Close()

    # Check if any histograms were found
    if not histograms:
        rprint(f"{colorama.Fore.YELLOW}Warning: No histograms found in {input_file_path}{colorama.Style.RESET_ALL}")
    else:
        rprint(f"Successfully loaded {len(histograms)} histograms from {input_file_path}")

    return histograms


###########################!TODO TESTING########################
def zero_histogram_bins(hist: TH1 | TH2 | TH3, bins_to_modify: dict, enable=True):
    """
    Modify specific bins of a ROOT histogram (1D to 3D) by zeroing out or retaining data
    based on the 'enable' flag. This function is robust to handle different histogram dimensions.

    Args:
        hist (TH1, TH2, TH3): The ROOT histogram to modify.
        bins_to_modify (dict): A dictionary specifying bins to modify for each dimension.
                               Example: {'x': [1, 5, 10], 'y': [2, 3]}.
        enable (bool): If True, retains data in the specified bins and zeros out the rest.
                       If False, zeros out data in the specified bins only.

    Raises:
        ValueError: If inappropriate dimensions are provided or bins are out of range.
    """
    # Check histogram dimension
    ndim = hist.GetDimension()
    allowed_dims = ['x', 'y', 'z'][:ndim]

    # Validate the input dictionary dimensions against the histogram's allowed dimensions
    if any(dim not in allowed_dims for dim in bins_to_modify):
        raise ValueError(
            f"{colorama.Fore.RED}ERROR::zero_histogram_binsInvalid dimension(s) in bins_to_modify. Allowed dimensions: {allowed_dims}, Provided: {bins_to_modify.keys()}{colorama.Style.RESET_ALL}"
        )

    # Validate and normalize bins_to_modify: ensure values are lists
    bins_to_modify = {k: v if isinstance(v, list) else [v] for k, v in bins_to_modify.items()}

    # Set bin ranges for each axis of the histogram
    bin_range = {
        'x': (1, hist.GetNbinsX() + 1),
        'y': (1, hist.GetNbinsY() + 1 if ndim > 1 else 2),
        'z': (1, hist.GetNbinsZ() + 1 if ndim > 2 else 2),
    }

    # Loop over all bins and modify based on enable flag
    for binx in range(*bin_range['x']):
        x_condition = 'x' in bins_to_modify and binx in bins_to_modify['x']

        for biny in range(*bin_range['y']):
            y_condition = 'y' in bins_to_modify and biny in bins_to_modify['y']

            for binz in range(*bin_range['z']):
                z_condition = 'z' in bins_to_modify and binz in bins_to_modify['z']

                # Determine if the current bin should be modified based on the axis conditions and enable flag
                condition = (x_condition if 'x' in bins_to_modify else True) and (y_condition if 'y' in bins_to_modify else True) and (z_condition if 'z' in bins_to_modify else True)

                # Modify bins: zero out if (enabled and not this bin) or (disabled and this bin)
                if (enable and not condition) or (not enable and condition):
                    if ndim == 1:
                        hist.SetBinContent(binx, 0)
                    elif ndim == 2:
                        hist.SetBinContent(binx, biny, 0)
                    elif ndim == 3:
                        hist.SetBinContent(binx, biny, binz, 0)


# # Example usage:
# if __name__ == "__main__":
#     # Load a 2D histogram from a ROOT file
#     hist_2d = get_hist_from_file("path_to_file.root", "hist2d_name")

#     # Enable specific bins: keep only specified bins in 'x' and 'y' dimensions, zero the rest
#     zero_histogram_bins(hist_2d, {'x': [1, 5, 10], 'y': [2, 3]}, enable=True)

#     # Disable specific bins: zero out the specified bins in 'x' and 'y' dimensions
#     zero_histogram_bins(hist_2d, {'x': [1, 5, 10], 'y': [2, 3]}, enable=False)

###########################!TODO TESTING########################


# ----------------------------------------------------------------------------------------------------------------------
# Draw the comparison of histograms
# ----------------------------------------------------------------------------------------------------------------------


def define_plots_nx_ny(nplots: int) -> list[int, int]:
    nx: int = int(math.sqrt(nplots)) if (nplots > 3) else nplots
    ny: int = math.ceil(nplots / nx)

    return [nx, ny]


def draw_histo_comparison(
    h_ref: list,
    h_cmp: list,
    output_file: str,
    rp_type: str = 'divsym',
    legend_ref: str = '',
    legend_cmp: str = '',
    normalize_opt: int = 1,
) -> None:
    """
    Draws a comparison of histograms with ratio plots.

    Parameters:
    h_ref (list): List of reference histograms, the errors are used from these histograms.
    h_cmp (list): List of comparison histograms (Should be at the same order as h_ref). The errors from these histograms are not used.
    output_file (str): Path to save the output file.
    rp_type (str): Type of ratio plot. Options: 'divsym', 'diff', 'diffsig'.
    legend_ref (str): Legend entry for reference histograms.
    legend_cmp (str): Legend entry for comparison histograms.
    normalize_opt (int): Normalization option. 0: no normalization; 1: normalize all histograms to 1; 2: normalize comparison histograms to reference histograms.
    """

    # rp_type: []"divsym", "diff", "diffsig"]
    # normalize_opt. 0: no normalization; 1: normalize all histograms to 1; 2: normalize the comparison histograms to the reference histograms accordingly.

    # Check input arguments
    h_ref = h_ref if isinstance(h_ref, list) else [h_ref]
    h_cmp = h_cmp if isinstance(h_cmp, list) else [h_cmp]

    assert len(h_ref) == len(h_cmp), f"{colorama.Fore.RED}ERROR::draw_histo_comparison: The number of reference histograms and comparison histograms should be the same.{colorama.Style.RESET_ALL}"
    assert rp_type in {"divsym", "diff", "diffsig"}, "ERROR::draw_histo_comparison: Invalid ratio plot type."
    assert normalize_opt in {0, 1, 2}, f"{colorama.Fore.RED}ERROR::draw_histo_comparison: Invalid normalization option.{colorama.Style.RESET_ALL}"

    # Create a canvas and divide it based on the number of histograms
    c1 = TCanvas("canvas", "canvas", 950 * len(h_ref), 800)

    nx, ny = define_plots_nx_ny(len(h_ref))
    c1.Divide(nx, ny)

    # List to keep ratio plots in scope
    ratio_plots = []

    for i, h1 in enumerate(h_ref):
        c1.cd(i + 1)
        h2 = h_cmp[i]

        # Rebin the histograms of h2 to the binning of h1
        if h1.GetNbinsX() != h2.GetNbinsX():
            rprint(f"WARNING::draw_histo_comparison: Rebinning {h2.GetName()} to the binning of {h1.GetName()}")
            h2 = h2.Rebin(h1.GetNbinsX(), f'{h2.GetName()}_rebin', h1.GetXaxis().GetXbins().GetArray())

        # Ensure bin limits match
        assert (
            h1.GetXaxis().GetXmin() == h2.GetXaxis().GetXmin()
        ), f"{colorama.Fore.RED}ERROR: {h1.GetName()} and {h2.GetName()} have different bin left limits, {h1.GetXaxis().GetXmin()} != {h2.GetXaxis().GetXmin()}{colorama.Style.RESET_ALL}"
        assert (
            h1.GetXaxis().GetXmax() == h2.GetXaxis().GetXmax()
        ), f"{colorama.Fore.RED}ERROR: {h1.GetName()} and {h2.GetName()} have different bin right limits, {h1.GetXaxis().GetXmax()} != {h2.GetXaxis().GetXmax()}{colorama.Style.RESET_ALL}"

        # Print out all bin limits
        # import numpy as np
        # rprint(f'--- {h1.GetName()} ---')
        # rprint(np.array([h1.GetXaxis().GetBinLowEdge(i) for i in range(1, h1.GetNbinsX() + 2)]))
        # rprint(f'--- {h2.GetName()} ---')
        # rprint(np.array([h2.GetXaxis().GetBinLowEdge(i) for i in range(1, h2.GetNbinsX() + 2)]))

        # Normalize the histograms
        if normalize_opt == 1:
            h1.Scale(1.0 / h1.Integral())
            h2.Scale(1.0 / h2.Integral())
        elif normalize_opt == 2:
            h2.Scale(h1.Integral() / h2.Integral())

        # Set the line color
        h1.SetLineColor(r.kRed)
        h2.SetLineColor(r.kBlue)

        # Create and configure ratio plot
        rp = TRatioPlot(h1, h2, rp_type)  #  "divsym", "diff", "diffsig"

        rp.SetH1DrawOpt("E1")
        rp.SetH2DrawOpt("E1")

        # h1.GetXaxis().SetTitle("x")
        # h1.GetYaxis().SetTitle("y")

        # c1.SetTicks(0, 1)
        # rp.SetLeftMargin(0.05)
        rp.SetRightMargin(0.03)
        # rp.SetUpTopMargin(0.05)
        # rp.SetLowBottomMargin(0.05)
        rp.GetLowYaxis().SetNdivisions(505)
        rp.SetSeparationMargin(0.0)

        # Draw lines in the ratio plot
        lines = [0]
        if rp_type == "divsym":
            lines = [1]
        elif rp_type == "diffsig":
            lines = [3, -3]
        rp.SetGridlines(lines)

        ratio_plots.append(rp)
        rp.SetGraphDrawOpt("LE0")

        rp.Draw()
        # rp.GetUpperRefObject.SetTitle(f'{h_ref[dim]["title"]}; {h_ref[dim]["unit"]}')

        # Configure y-axis titles and ranges
        rp.GetUpperRefYaxis().SetTitle("p.d.f.")
        rp.GetUpperRefYaxis().SetRangeUser(0, max(h1.GetMaximum(), h2.GetMaximum()) * 1.1)

        # Set the y axis title of the ratio plot
        title_ratio = "ratio" if rp_type == "divsym" else "difference" if rp_type == "diff" else "pull"
        rp.GetLowerRefYaxis().SetTitle(title_ratio)

        # Set the y range of the lower plot
        if rp_type == "divsym":
            rp.GetLowerRefGraph().SetMinimum(0)
            rp.GetLowerRefGraph().SetMaximum(3)
            # pass
        elif rp_type == "diffsig":
            rp.GetLowerRefGraph().SetMinimum(-5)
            rp.GetLowerRefGraph().SetMaximum(5)

        # Add legend
        rp.GetUpperPad().cd()
        legend = TLegend(0.65, 0.75, 0.98, 0.90)
        legend_ref = legend_ref or h1.GetName()
        legend_cmp = legend_cmp or h2.GetName()
        legend.AddEntry(h1, legend_ref, "lpe")
        legend.AddEntry(h2, legend_cmp, "lpe")

        # Add legend to the plotable
        rp.GetUpperRefObject().GetListOfFunctions().Add(legend)

    # Update canvas and turn off stats box
    c1.Update()

    # Turn off stats box
    gStyle.SetOptStat(0)

    # Save the canvas
    output_file = str(Path(output_file).resolve())
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    c1.SaveAs(output_file)

    # Close the canvas
    c1.Close()


def draw_histo_comparison_no_pulls(
    input_histos: list,
    histo_names: list,
    output_pic: str,
    histo_draw_options: list = None,
    normalise=True,
    set_y_min: float = None,
    legend_labels: list = None,
):
    # Check input arguments
    input_histos = input_histos if isinstance(input_histos, list) else [input_histos]
    histo_names = histo_names if isinstance(histo_names, list) else [histo_names]
    assert len(input_histos) == len(histo_names), f'Erorr: the number of input histos ({len(input_histos)}) does not match the number of histo names ({len(histo_names)})'

    if histo_draw_options:
        histo_draw_options = histo_draw_options if isinstance(histo_draw_options, list) else [histo_draw_options] * len(input_histos)
        assert len(input_histos) == len(histo_draw_options), f'Erorr: the number of input histos ({len(input_histos)}) does not match the number of histo draw options ({len(histo_draw_options)})'
    else:
        histo_draw_options = ['PE0'] + ['histo sames'] * (len(input_histos) - 1)

    if len(histo_draw_options) > 1:
        # Make sure that the following options all with sames, to be drawn in the same plot
        for i, opt in enumerate(histo_draw_options):
            if i == 0:
                continue
            if 'sames' not in opt:
                histo_draw_options[i] = f'{opt} sames'

    # Define some variables
    dim_map = {0: 'X', 1: 'Y', 2: 'Z'}
    colors = {0: r.kBlack, 1: r.kBlue, 2: r.kRed, 3: r.kGreen, 4: r.kMagenta, 5: r.kOrange}

    ndim = input_histos[0].GetDimension()

    # Create a dictionary of input histos
    histos = {name: {'h': h} for name, h in zip(histo_names, input_histos)}

    # Project the histos to 1D
    for cat in histos:
        for i_dim in range(ndim):
            if ndim > 1:
                histos[cat][i_dim] = histos[cat]['h'].__getattribute__(f'Projection{dim_map[i_dim]}')(f'{histos[cat]["h"].GetName()}_{dim_map[i_dim]}')
            else:
                histos[cat][i_dim] = histos[cat]['h']

            histos[cat][i_dim] = normalize_histogram_integral(histos[cat][i_dim], 1) if normalise else histos[cat][i_dim]

    # Create a canvas
    c1 = TCanvas('c1', '', ndim * 950, 800)
    c1.Divide(ndim, 1)

    def __set_common_histo_features(h: TH1, color, y_range: tuple | list = None):
        h.GetYaxis().SetLabelSize(0.045)
        h.GetXaxis().SetLabelSize(0.045)
        h.GetXaxis().SetTitleSize(0.045)
        # h.GetYaxis().SetTitleSize(0.045)
        # h.GetYaxis().SetTitleOffset(1.2)
        # h.GetXaxis().SetTitleOffset(1.2)

        h.SetMarkerStyle(20)
        h.SetMarkerSize(1)
        h.SetLineColor(color)

        # Set y range
        h.GetYaxis().SetRangeUser(*y_range) if y_range else None

        return h

    # Calculate the y-axis range

    # Draw the histos
    for i_dim in range(ndim):
        c1.cd(i_dim + 1)

        y_range = calculate_y_axis_range([histos[cat][i_dim] for cat in histos])

        for j, cat in enumerate(histos):
            __set_common_histo_features(histos[cat][i_dim], colors[j], y_range)
            # histos[cat][i_dim].Draw('PE0') if j == 0 else histos[cat][i_dim].Draw('histo sames')

            if set_y_min is not None:
                histos[cat][i_dim].SetMinimum(set_y_min)

            if normalise:
                # The y-axis title is set to 'p.d.f.' if the histograms are normalized
                histos[cat][i_dim].GetYaxis().SetTitle('p.d.f.')
                # make title get closer to the axis
                histos[cat][i_dim].GetYaxis().SetTitleOffset(1.55)

            histos[cat][i_dim].Draw(histo_draw_options[j])

    # Set legend
    c1.cd(1)
    l1 = TLegend(0.1, 0.75, 0.3, 0.9)

    if legend_labels:
        assert len(legend_labels) == len(
            histos
        ), f'{colorama.Fore.RED}ERROR:: the number of legend entries ({len(legend_labels)}) does not match the number of histos ({len(histos)}){colorama.Style.RESET_ALL}'
    else:
        legend_labels = histo_names

    for i, cat in enumerate(histos):
        l1.AddEntry(histos[cat][0], legend_labels[i], get_legend_option_from_draw_option(histos[cat][0]))

    l1.Draw()

    # Remove the stats box
    gStyle.SetOptStat(0)

    # Save the plots
    output_pic = str(Path(output_pic).resolve())
    Path(output_pic).parent.mkdir(parents=True, exist_ok=True)
    c1.SaveAs(output_pic)
