'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2023-10-11 10:32:26 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-05-21 10:04:20 +0200
FilePath     : train_xgboost_model.py
Description  :

Copyright (c) 2023 by everyone, All Rights Reserved.
'''

###################
import sys, os
import argparse
from typing import Dict, List, Optional, Union, Tuple, Any, NamedTuple, Callable
import gc

import pandas as pd
import numpy as np

import multiprocessing

from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import auc

import xgboost as xgb
from xgboost import XGBClassifier, plot_importance

from scipy import stats
from matplotlib.patches import Rectangle

import matplotlib
import matplotlib.pyplot as plt

import concurrent.futures
from functools import partial

# import mplhep as hep

from pathlib import Path
from dataclasses import dataclass, asdict, field

from tqdm import tqdm
from itertools import product
from copy import deepcopy


from analysis_tool.utils.utils_yaml import read_yaml
from analysis_tool.utils.utils_uproot import load_variables_to_pd_by_uproot
from analysis_tool.correlation.matrixHelper import plot_correlation_heatmap


from analysis_tool.plotter.compare_distributions import plot_individual_variable_comparison, collect_all_plots_in_one_canvas

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


###################
# Batch mode for matplotlib
matplotlib.use("Agg")

# Set the style of the plots
# hep.style.use("LHCb2")


def check_n_threads(n_threads: int) -> int:
    """
    Check and adjust the number of threads to use for fitting.

    Args:
        n_threads: Requested number of threads (0=auto, negative=cpu_count+n_threads)

    Returns:
        Adjusted number of threads to use
    """
    cpu_count = multiprocessing.cpu_count()

    if n_threads == 0:
        # Auto mode: use half of available CPUs but at least 1
        n_threads = max(cpu_count // 2 - 1, 1)
    elif n_threads < 0:
        # Negative: cpu_count + n_threads (e.g., -1 = all but one CPU)
        n_threads = max(cpu_count + n_threads, 1)
    else:
        # Positive: use requested threads but cap at available CPUs
        n_threads = max(min(n_threads, cpu_count), 1)

    return n_threads


def GetModelPath(dir_main: str = "output/models", name_model="xgb_model.json", nFold: int = 0):
    if nFold == 0:
        return {0: f"{dir_main}/{name_model}"}
    else:
        return {iFold: f"{dir_main}/{iFold}/{name_model}" for iFold in range(nFold)}


def compare_train_test(model, dataTrainTest):
    """
    Given a trained classifier, get the distribution of the classifier output for the signal
    and background categories of the training and testing datasets.
    This allows to check for overtraining.
    """

    @dataclass
    class predictions:
        trainS: list = None
        trainB: list = None
        testS: list = None
        testB: list = None

    # Get predictions
    predictions.trainS = model.predict_proba(dataTrainTest.X_train[dataTrainTest.y_train > 0.5])[:, 1].ravel()
    predictions.trainB = model.predict_proba(dataTrainTest.X_train[dataTrainTest.y_train < 0.5])[:, 1].ravel()
    predictions.testS = model.predict_proba(dataTrainTest.X_test[dataTrainTest.y_test > 0.5])[:, 1].ravel()
    predictions.testB = model.predict_proba(dataTrainTest.X_test[dataTrainTest.y_test < 0.5])[:, 1].ravel()

    return predictions


def plot_compare_train_test(decisions, bins: int, ws, output_plot_name: str = None, iFold: int = -1):
    """
    Plot the distribution of the classifier output for the signal and background categories
    of the training and testing datasets.
    """
    low = min(np.min(d) for d in [decisions.trainS, decisions.trainB, decisions.testS, decisions.testB])
    high = max(np.max(d) for d in [decisions.trainS, decisions.trainB, decisions.testS, decisions.testB])

    if low > 0 and (low < 5e-2):
        low = 0
    if high < 1 and (high > 1 - 5e-2):
        high = 1
    low_high = (low, high)

    # Plot with python.
    plt.figure(figsize=(8, 6))

    # Train samples
    plt.hist(
        decisions.trainS,
        color="b",
        alpha=0.5,
        range=low_high,
        bins=bins,
        histtype="stepfilled",
        density=True,
        label="S (train)",
        weights=ws.train_signal,
    )
    plt.hist(
        decisions.trainB,
        color="r",
        alpha=0.5,
        range=low_high,
        bins=bins,
        histtype="stepfilled",
        density=True,
        label="B (train)",
        weights=ws.train_background,
    )

    # Test samples
    hist, bins = np.histogram(decisions.testS, bins=bins, range=low_high, density=True, weights=ws.test_signal)
    center = (bins[:-1] + bins[1:]) / 2
    scale = sum(ws.test_signal) / sum(hist) if sum(hist) > 0 else 1
    err = np.sqrt(hist * scale) / scale if scale > 0 else np.zeros_like(hist)
    plt.errorbar(center, hist, yerr=err, fmt="o", c="b", label="S (test)")

    hist, bins = np.histogram(decisions.testB, bins=bins, range=low_high, density=True, weights=ws.test_background)
    scale = sum(ws.test_background) / sum(hist) if sum(hist) > 0 else 1
    err = np.sqrt(hist * scale) / scale if scale > 0 else np.zeros_like(hist)
    plt.errorbar(center, hist, yerr=err, fmt="o", c="r", label="B (test)")

    # Perform KS tests
    # For signal samples (train vs test)
    ks_stat_signal, p_value_signal = stats.ks_2samp(decisions.trainS, decisions.testS)
    # For background samples (train vs test)
    ks_stat_bkg, p_value_bkg = stats.ks_2samp(decisions.trainB, decisions.testB)

    # Create text box with KS test results
    ks_text = f"Kolmogorov-Smirnov Test:\n" f"Signal: stat={ks_stat_signal:.3f}\n" f"Background: stat={ks_stat_bkg:.3f}"

    # Add a background rectangle to make the text more readable
    ax = plt.gca()
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    ax.text(0.20, 0.95, ks_text, transform=ax.transAxes, fontsize='medium', verticalalignment='top', bbox=props)

    plt.xticks(np.arange(low, high * (1 + 1e-2), step=0.1))
    plt.xlabel("Classifier output") if iFold == -1 else plt.xlabel(f"Classifier output (Fold {iFold})")
    plt.ylabel("(1/N) dN/dx")
    plt.legend(loc="best", ncol=2, fontsize='medium')

    # Tight layout
    plt.tight_layout()

    # Save plot
    if output_plot_name:
        Path(output_plot_name).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_plot_name)
        logger.info(f"Saved plot to {output_plot_name}")

    plt.close()
    return plt


def PlotSingleROC(
    X_test,
    y_test,
    weights,
    model,
    classifier: str,
    color,
    output_plot_name: str = None,
    label=None,
):
    # Get ROC curve elements
    y_pred = model.predict_proba(X_test)[:, 1]

    fpr, tpr, thresholds = roc_curve(y_test, y_pred, sample_weight=weights)
    roc = roc_auc_score(y_test, y_pred, sample_weight=weights)
    areaUC = auc(fpr, tpr)

    # Print ROC information
    logger.info("Classifier ROC information: ")
    logger.info(classification_report(y_test, model.predict(X_test), target_names=["background", "signal"], sample_weight=weights))
    logger.info("Area under ROC curve: %.4f" % (roc))

    # Plot ROC curve
    plt.figure()
    plt.xlim([-0.01, 1.00])
    plt.ylim([-0.01, 1.01])
    plt.plot([0, 1], [0, 1], color="grey", linestyle="--")

    if label:
        plt.plot(fpr, tpr, label=f"{label} (area = {areaUC:.3f})")
    else:
        plt.plot(fpr, tpr, lw=1, color=color, label=f"ROC curve (area = {areaUC:.3f})")

    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title(f"ROC curve {classifier}", fontsize=14)
    plt.legend(loc="lower right", fontsize=12)

    # Save plot
    if output_plot_name:
        Path(output_plot_name).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_plot_name)

    plt.close()
    return output_plot_name


def PlotMultipleROC(
    folds_data: dict,
    models_dict: dict,
    output_plot_name: str,
    classifier_name: str = "XGBoost",
    colors: list = None,
) -> str:
    """
    Plot ROC curves from multiple folds on a single plot for comparison

    Parameters:
    -----------
    folds_data : dict
        Dictionary of fold data where keys are fold indices and values are dataTrainTest objects
    models_dict : dict
        Dictionary of trained models where keys are fold indices and values are model objects
    output_plot_name : str
        Path to save the output plot
    classifier_name : str, optional
        Name of the classifier for the plot title
    colors : list, optional
        List of colors for the ROC curves. If None, will use default colormap

    Returns:
    --------
    str
        Path to the saved plot
    """
    # Create figure
    plt.figure(figsize=(10, 8))
    plt.xlim([-0.01, 1.00])
    plt.ylim([-0.01, 1.01])
    plt.plot([0, 1], [0, 1], color='grey', linestyle='--', label='Random classifier')

    # Generate colors if not provided
    if colors is None:
        import matplotlib.cm as cm

        colors = cm.tab10(np.linspace(0, 1, len(folds_data)))

    # Plot ROC curve for each fold
    mean_tpr = np.zeros([100])
    mean_fpr = np.linspace(0, 1, 100)
    aucs = []

    for i, (fold_idx, data) in enumerate(folds_data.items()):
        model = models_dict[fold_idx]
        X_test, y_test = data.X_test, data.y_test
        weights = data.ws.test  # Test weights

        # Get predictions and ROC curve
        y_pred = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_pred, sample_weight=weights)
        roc_auc = roc_auc_score(y_test, y_pred, sample_weight=weights)
        aucs.append(roc_auc)

        # Interpolate to common fpr grid for averaging
        interp_tpr = np.interp(mean_fpr, fpr, tpr)
        interp_tpr[0] = 0.0
        mean_tpr += interp_tpr

        # Plot individual ROC curve
        color = colors[i] if isinstance(colors, list) else f'C{i}'
        plt.plot(fpr, tpr, lw=1, alpha=0.7, color=color, label=f'Fold {fold_idx} (AUC = {roc_auc:.3f})')

    # Plot mean ROC curve
    mean_tpr /= len(folds_data)
    mean_tpr[-1] = 1.0
    mean_auc = np.mean(aucs)
    std_auc = np.std(aucs)

    plt.plot(mean_fpr, mean_tpr, 'b-', lw=2, alpha=0.9, label=f'Mean ROC (AUC = {mean_auc:.3f} ± {std_auc:.3f})')

    # Plot standard deviation area
    std_tpr = np.std(
        [
            np.interp(mean_fpr, fpr, tpr)
            for fold_idx, data in folds_data.items()
            for fpr, tpr, _ in [roc_curve(data.y_test, models_dict[fold_idx].predict_proba(data.X_test)[:, 1], sample_weight=data.ws.test)]
        ],
        axis=0,
    )

    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    plt.fill_between(
        mean_fpr,
        tprs_lower,
        tprs_upper,
        color='grey',
        alpha=0.2,
        label='± 1 std. dev.',
    )

    # Add plot details
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title(f'ROC Curves for {classifier_name} K-Fold Cross-Validation', fontsize=14)
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(alpha=0.3)

    # Save plot
    Path(output_plot_name).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_name, bbox_inches='tight', dpi=300)
    plt.close()

    return output_plot_name


def PlotSignificance(X_test, y_test, weights, model, n_sig, n_bkg, output_plot_name, label=None) -> str:
    # Get predictions
    y_pred = model.predict_proba(X_test)[:, 1]

    # Get ROC curve elements
    fpr, tpr, thresholds = roc_curve(y_test, y_pred, sample_weight=weights)

    S = n_sig * tpr
    B = n_bkg * fpr
    # Safely calculate significance metric
    metric = np.divide(S, np.sqrt(S + B), out=np.zeros_like(S), where=(S + B) > 0)

    # Find the threshold for maximum significance
    max_significance = np.max(metric)
    optimal_idx = np.argmax(metric)
    optimal_cut = thresholds[optimal_idx] if optimal_idx < len(thresholds) else 0.5

    # Plot significance
    plt.figure()
    plt.plot(thresholds, metric, label=label if label else "Significance")
    plt.xlabel("BDT cut value")
    plt.ylabel(r"$S/\sqrt{S+B}$")
    plt.xlim(0, 1.0)

    # Draw horizontal line at the maximum significance
    plt.axhline(max_significance, color="red", linestyle="--", alpha=0.8)

    # Draw vertical line at optimal cut
    plt.axvline(optimal_cut, color="green", linestyle="--", alpha=0.8)

    # Annotate the plot with the optimal BDT cut value
    plt.text(0.5, 0.4, f"Optimal BDT cut: {optimal_cut:.2f}", fontsize=12)

    # Save plot
    Path(output_plot_name).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_name)

    plt.close()
    return output_plot_name


def PlotFeatureImportance(
    model,
    output_plot_name: str,
    feature_names: list = None,
    importance_type: str = "gain",
) -> tuple[plt.Figure, plt.Axes]:
    """Plot feature importance using XGBoost's built-in function"""
    # Set feature names if provided
    if feature_names:
        model.get_booster().feature_names = feature_names

    # Plot feature importance in percentage
    fig, ax = plt.subplots(figsize=(10, 10))
    plot_importance(model, ax=ax, xlabel=f"F score ({importance_type})", importance_type=importance_type, grid=False, height=0.8, values_format="{v:.2f}")

    # Tight layout
    plt.tight_layout()

    # Save plot
    Path(output_plot_name).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_name, bbox_inches="tight")
    plt.close(fig)

    return output_plot_name


def PlotLossEvolution(
    model,
    output_plot_name: str,
    metrics: list[str] = None,
    figsize: tuple = (10, 8),
) -> str:
    """
    Plot the evolution of metrics during training for both training and validation sets.

    Parameters:
    -----------
    model : XGBClassifier
        The trained XGBoost model
    output_plot_name : str
        Path to save the output plot
    metrics : list[str], optional
        List of metrics to plot. If None, will plot all available metrics
    figsize : tuple, optional
        Figure size
    """
    # Get evaluation results using the official method
    results = model.evals_result()

    # Check if results are empty
    if not results:
        raise ValueError("Model evaluation results are empty. Loss evolution failed.")

    # Get available metrics if not specified
    if metrics is None:
        # Get first dataset's metrics
        first_dataset = list(results.values())[0]
        metrics = list(first_dataset.keys())

    # Create figure with subplots for each metric
    fig, axes = plt.subplots(len(metrics), 1, figsize=figsize, sharex=True)
    if len(metrics) == 1:
        axes = [axes]  # Make it iterable for single metric case

    # Plot each metric
    for i, metric in enumerate(metrics):
        ax = axes[i]

        # Plot training and validation metrics
        for j, (dataset, dataset_results) in enumerate(results.items()):
            if metric in dataset_results:
                iterations = range(len(dataset_results[metric]))
                ax.plot(iterations, dataset_results[metric], label=f"{dataset} {metric}", alpha=0.8, linewidth=2)

        ax.set_title(f"{metric.upper()} Evolution", fontsize=12)
        ax.set_ylabel(metric, fontsize=10)
        ax.grid(alpha=0.3)
        ax.legend(loc='best')

    # Set common x label for all subplots
    ax.set_xlabel("Iterations", fontsize=12)

    # Add a title for the whole figure
    plt.suptitle("Training and Validation Metrics Evolution", fontsize=14)

    # Adjust spacing between subplots
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)  # Make room for the suptitle

    # Save the plot
    Path(output_plot_name).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    logger.info(f"Loss evolution plot saved to {output_plot_name}")
    return output_plot_name


def PlotParticleMass(
    mass_var: str,
    df_data: pd.DataFrame,
    BDTcut: float,
    weightName: str,
    output_plot_name: str,
    particle_name: str = "",
    unit: str = "MeV",
    figsize: tuple = (18, 5),
    bins: int = 30,
):
    """
    Plot particle mass distributions with BDT cuts.

    Parameters:
    -----------
    df_data : pd.DataFrame
        DataFrame containing mass and BDT score columns
    BDTcut : float
        BDT score cut value to separate signal from background
    weightName : str
        Name of the weight column in df_data
    output_plot_name : str
        Path to save the output plot
    mass_var : str, optional
        Name of the mass variable column in df_data
    particle_name : str, optional
        Name of the particle for plot labels, can include LaTeX formatting
    unit : str, optional
        Unit of the mass variable (e.g., "MeV", "GeV")
    figsize : tuple, optional
        Figure size (width, height)
    bins : int, optional
        Number of bins for histograms

    Returns:
    --------
    str
        Path to the saved plot
    """

    particle_name = particle_name or mass_var

    # Extract masses passing/failing BDT cut
    mass_s = df_data[mass_var].where(df_data["_XGBDT"] > BDTcut).dropna()
    mass_b = df_data[mass_var].where(df_data["_XGBDT"] < BDTcut).dropna()
    mass_tot = df_data[mass_var]

    # Extract weights
    w_s = df_data[weightName].where(df_data["_XGBDT"] > BDTcut).dropna()
    w_b = df_data[weightName].where(df_data["_XGBDT"] < BDTcut).dropna()
    w_tot = df_data[weightName]

    # Mass range
    mass_range = (mass_tot.min(), mass_tot.max())

    # Plot options
    figOpts = {
        "alpha": 0.9,
        "density": False,
        "bins": bins,
        "histtype": "step",
        "lw": 2,
        "range": mass_range,
    }

    # Create figure with 3 subplots
    fig2 = plt.figure(figsize=figsize)

    # 1) Signal subplot
    plt_s = plt.subplot(1, 3, 1)
    plt_s.set_xlabel(f"{particle_name} mass ({unit})")
    plt.hist(mass_s, color="blue", bins=bins, edgecolor="k")
    plt_s.set_title(f"BDT > {str(BDTcut)}")

    # 2) Background subplot
    plt_b = plt.subplot(1, 3, 2, sharex=plt_s)
    plt_b.set_xlabel(f"{particle_name} mass ({unit})")
    plt.hist(mass_b, color="red", bins=bins, edgecolor="k")
    plt_b.set_title(f"BDT < {str(BDTcut)}")

    # 3) Total subplot
    plt_tot = plt.subplot(1, 3, 3, sharex=plt_s)
    plt_tot.set_xlabel(f"{particle_name} mass ({unit})")
    plt_tot.hist(mass_tot, color="green", label="No cut", weights=w_tot, **figOpts)
    plt_tot.hist(mass_b, color="red", label=f"BDT < {str(BDTcut)}", weights=w_b, **figOpts)
    plt_tot.hist(mass_s, color="blue", label=f"BDT > {str(BDTcut)}", weights=w_s, **figOpts)
    plt_tot.legend(prop={"size": 10})

    # Save plot
    Path(output_plot_name).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_plot_name, bbox_inches="tight")
    plt.close(fig2)

    return output_plot_name


def dfKFoldSampleSplit(df: pd.DataFrame, nFold: int, splitVar: str) -> dict[int, pd.DataFrame]:
    # Check input arguments
    assert nFold > 1, f"nFold must be greater than 1, not {nFold}"

    # Check splitVar in the dataframe
    assert splitVar in df.columns, f"{splitVar} is not in the dataframe"

    df = df.copy()
    df[splitVar] = df[splitVar].astype("int64")
    # Split the dataframe into nFold samples according to the splitVar
    return {i: df.query(f"{splitVar}%{nFold} != {i}") for i in range(nFold)}


class WeightSet(NamedTuple):
    train: np.ndarray  # All training weights
    test: np.ndarray  # All test weights
    train_signal: np.ndarray  # Training weights for signal
    train_background: np.ndarray  # Training weights for background
    test_signal: np.ndarray  # Test weights for signal
    test_background: np.ndarray  # Test weights for background


@dataclass
class DataTrainTest:
    df_sig: pd.DataFrame = field(default_factory=pd.DataFrame)
    df_bkg: pd.DataFrame = field(default_factory=pd.DataFrame)
    X_train: np.ndarray = field(default_factory=lambda: np.array([]))
    X_test: np.ndarray = field(default_factory=lambda: np.array([]))
    y_train: np.ndarray = field(default_factory=lambda: np.array([]))
    y_test: np.ndarray = field(default_factory=lambda: np.array([]))
    ws: Optional[WeightSet] = None
    BDTvars: list = field(default_factory=list)
    sig_weightVar: str = field(default_factory=str)
    bkg_weightVar: str = field(default_factory=str)
    bdt_weightVar: str = field(default_factory=lambda: "bdtWeight")


def dfCreateTrainTest(
    sig_file: str,
    bkg_file: str,
    signal_tree_name: str,
    background_tree_name: str,
    BDTvars: list,
    sig_weightVar: str = None,
    bkg_weightVar: str = None,
    nFold: int = 0,
    splitVar: str = None,
    sig_max_entries: int = -1,
    bkg_max_entries: int = -1,
    additional_variables_to_load_sig: list = [],
    additional_variables_to_load_bkg: list = [],
) -> dict:

    logger.info(f"Processing:\n    signal: {sig_file}\n    background: {bkg_file}")

    dataTrainTest: DataTrainTest = DataTrainTest()

    # Get the variables to load from the signal file
    variables_to_load_sig: list = []
    variables_to_load_sig += BDTvars
    variables_to_load_sig += [sig_weightVar] if sig_weightVar else []
    variables_to_load_sig += [splitVar] if splitVar else []
    variables_to_load_sig += additional_variables_to_load_sig

    # Get the variables to load from the background file
    variables_to_load_bkg: list = []
    variables_to_load_bkg += BDTvars
    variables_to_load_bkg += [bkg_weightVar] if bkg_weightVar else []
    variables_to_load_bkg += [splitVar] if splitVar else []
    variables_to_load_bkg += additional_variables_to_load_bkg

    # Load the branches from ROOT files to pandas dataframes
    df_sig_read = load_variables_to_pd_by_uproot(sig_file, input_tree_name=signal_tree_name, variables=variables_to_load_sig, library="pd", num_workers=4)
    df_bkg_read = load_variables_to_pd_by_uproot(bkg_file, input_tree_name=background_tree_name, variables=variables_to_load_bkg, library="pd", num_workers=4)

    # Drop NaNs in training variables
    df_sig = df_sig_read.dropna(subset=BDTvars)
    df_bkg = df_bkg_read.dropna(subset=BDTvars)

    # Reduce the number of events if requested
    df_sig = df_sig_read if sig_max_entries == -1 else df_sig[:sig_max_entries]
    df_bkg = df_bkg_read if bkg_max_entries == -1 else df_bkg[:bkg_max_entries]

    # Reduce the number of background events to at most 10 times the number of signal events
    nFactor = 10
    if df_bkg.shape[0] > df_sig.shape[0] * nFactor:
        logger.info(f"Reducing the number of background events to {df_sig.shape[0] * nFactor}")
        df_bkg = df_bkg[: df_sig.shape[0] * nFactor]  # Out of 200000 used only 40000 events in the training
    else:
        df_bkg = df_bkg

    # Set the weight variables to the same name within BDT context and for further processing
    def _add_bdt_weightVar(df, weightVar):
        result = df.copy()
        if weightVar is None or weightVar.upper() in {"NONE", "1"}:
            result[dataTrainTest.bdt_weightVar] = np.ones(result.shape[0])
        else:
            result[dataTrainTest.bdt_weightVar] = result.eval(weightVar)
        return result

    df_sig = _add_bdt_weightVar(df_sig, sig_weightVar)
    df_bkg = _add_bdt_weightVar(df_bkg, bkg_weightVar)

    # Check if there are any negative weights in the events, if so, drop them (not supported by the BDT)
    if df_sig[dataTrainTest.bdt_weightVar].min() < 0:
        logger.warning("Found negative weights in the signal events, will drop those events")
        logger.warning(f"Number of negative weights in signal events: [bold yellow]{df_sig.query(f'{dataTrainTest.bdt_weightVar} < 0').shape[0]}[/]", extra={"markup": True})
        df_sig = df_sig.query(f"{dataTrainTest.bdt_weightVar} > 0").dropna(subset=[dataTrainTest.bdt_weightVar])
    if df_bkg[dataTrainTest.bdt_weightVar].min() < 0:
        logger.warning("Found negative weights in the background events, will drop those events")
        logger.warning(f"Number of negative weights in background events: [bold yellow]{df_bkg.query(f'{dataTrainTest.bdt_weightVar} < 0').shape[0]}[/]", extra={"markup": True})
        df_bkg = df_bkg.query(f"{dataTrainTest.bdt_weightVar} > 0").dropna(subset=[dataTrainTest.bdt_weightVar])

    # Scale the weights to the same integral, use the one with the minimum integral as the target
    sig_sum = df_sig[dataTrainTest.bdt_weightVar].sum()
    bkg_sum = df_bkg[dataTrainTest.bdt_weightVar].sum()
    if sig_sum < bkg_sum:
        logger.info(f"Scaling the background weights integral {bkg_sum} to the signal integral {sig_sum}")
        df_bkg[dataTrainTest.bdt_weightVar] = df_bkg[dataTrainTest.bdt_weightVar] * sig_sum / bkg_sum
    else:
        logger.info(f"Scaling the signal weights integral {sig_sum} to the background integral {bkg_sum}")
        df_sig[dataTrainTest.bdt_weightVar] = df_sig[dataTrainTest.bdt_weightVar] * bkg_sum / sig_sum

    def _get_dataTrainTest(df_sig, df_bkg, BDTvars, weightVar):
        # Ensure data types are float for numeric computations
        _df_sig = df_sig[BDTvars + [weightVar]].astype(float)
        _df_bkg = df_bkg[BDTvars + [weightVar]].astype(float)

        # Check and handle infinite values
        _df_sig.replace([np.inf, -np.inf], np.nan, inplace=True)
        _df_bkg.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Prepare the input data for the BDT
        X = np.concatenate((_df_sig[BDTvars], _df_bkg[BDTvars]))
        y = np.concatenate((np.ones(_df_sig.shape[0]), np.zeros(_df_bkg.shape[0])))  # Sigs: 1, Bkgs: 0
        weights = np.concatenate((_df_sig[weightVar].values, _df_bkg[weightVar].values))

        # Train-test split with stratification for balanced classes
        X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(X, y, weights, test_size=0.3, random_state=42, stratify=y)

        logger.info(f"Number of events in the training sample: {X_train.shape[0]}")
        logger.info(f"Number of events in the test sample: {X_test.shape[0]}")

        # Prepare the weights
        ws_train_sig = w_train[y_train > 0.5]
        ws_train_bkg = w_train[y_train <= 0.5]
        ws_test_sig = w_test[y_test > 0.5]
        ws_test_bkg = w_test[y_test <= 0.5]
        ws = WeightSet(w_train, w_test, ws_train_sig, ws_train_bkg, ws_test_sig, ws_test_bkg)

        return DataTrainTest(
            df_sig,
            df_bkg,
            X_train,
            X_test,
            y_train,
            y_test,
            ws,
            BDTvars,
            sig_weightVar,
            bkg_weightVar,
            dataTrainTest.bdt_weightVar,
        )

    # Get the train and test samples
    result = {}
    if nFold > 1:
        # Split the samples into nFold samples
        df_sig_split: Dict[int, pd.DataFrame] = dfKFoldSampleSplit(df_sig, nFold, splitVar)
        df_bkg_split: Dict[int, pd.DataFrame] = dfKFoldSampleSplit(df_bkg, nFold, splitVar)

        # Prepare the data for each fold
        for i in range(nFold):
            logger.info(f"Processing fold {i} of {nFold}")
            logger.info(f"Number of signal events: {df_sig_split[i].shape[0]} of {df_sig.shape[0]}, number of background events: {df_bkg_split[i].shape[0]} of {df_bkg.shape[0]}")

            result[i] = _get_dataTrainTest(df_sig_split[i], df_bkg_split[i], BDTvars, dataTrainTest.bdt_weightVar)
    else:
        result[0] = _get_dataTrainTest(df_sig, df_bkg, BDTvars, dataTrainTest.bdt_weightVar)

    return result


def TrainModel(
    X_train,
    y_train,
    sample_wghts: list,
    *,
    X_test=None,  # Add X_test as an input parameter
    y_test=None,  # Add y_test as an input parameter
    test_wghts=None,  # Add test_wghts as an input parameter
    output_model: str = "model.json",
    gamma: float = 2,
    learning_rate: float = 0.005,
    max_delta_step: float = 0,
    max_depth: int = 9,
    min_child_weight: float = 0.08,
    n_estimators: int = 5000,
    n_jobs: int = -1,
    feature_names: list = None,
) -> XGBClassifier:

    logger.info(f"Training XGBoost model with {n_jobs} jobs ({n_jobs} CPUs)")

    # Create XGBClassifier with optimized parameters and set feature_names properly
    model = XGBClassifier(
        objective='binary:logistic',
        booster='gbtree',
        learning_rate=learning_rate,
        max_delta_step=max_delta_step,
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_child_weight=min_child_weight,
        gamma=gamma,
        subsample=0.85,
        colsample_bytree=0.8,
        colsample_bylevel=1.0,
        reg_alpha=0,
        reg_lambda=1,
        scale_pos_weight=1,
        tree_method='hist',
        importance_type='gain',
        eval_metric=['auc', 'logloss', 'error'],  # Only specify once here
        early_stopping_rounds=int(n_estimators * 0.25),
        n_jobs=n_jobs,
        verbosity=1,
        random_state=42,
    )

    # Train the model with early stopping using the pre-split test set
    logger.info("Training BDT...")

    if X_test is not None and y_test is not None:
        # Use the provided test set for validation during training
        eval_set = [(X_train, y_train), (X_test, y_test)]
        eval_weights = [sample_wghts, test_wghts] if test_wghts is not None else None

        model.fit(
            X_train,
            y_train,
            sample_weight=sample_wghts,
            eval_set=eval_set,
            sample_weight_eval_set=eval_weights,
            verbose=True,
        )
    else:
        # No test set provided, use training data only
        logger.warning("No test set provided. Early stopping will not be effective.")
        model.fit(
            X_train,
            y_train,
            sample_weight=sample_wghts,
            eval_set=[(X_train, y_train)],
            sample_weight_eval_set=[sample_wghts],
            verbose=True,
        )

    # Set feature names
    if feature_names:
        model.get_booster().feature_names = feature_names

    # Save model in XGBoost's native format without changing the extension
    Path(output_model).parent.mkdir(parents=True, exist_ok=True)
    model.save_model(output_model)
    logger.info(f"Model saved to {output_model}")

    return model


def PrintModelPerformance(model, dataTrainTest):
    # Get predictions
    y_pred_train = model.predict_proba(dataTrainTest.X_train)[:, 1]
    y_pred_test = model.predict_proba(dataTrainTest.X_test)[:, 1]

    # Calculate performance metrics
    train_auc = roc_auc_score(dataTrainTest.y_train, y_pred_train, sample_weight=dataTrainTest.ws.train)
    test_auc = roc_auc_score(dataTrainTest.y_test, y_pred_test, sample_weight=dataTrainTest.ws.test)

    train_pred_binary = (y_pred_train > 0.5).astype(int)
    test_pred_binary = (y_pred_test > 0.5).astype(int)

    train_accuracy = accuracy_score(dataTrainTest.y_train, train_pred_binary, sample_weight=dataTrainTest.ws.train)
    test_accuracy = accuracy_score(dataTrainTest.y_test, test_pred_binary, sample_weight=dataTrainTest.ws.test)

    # Print performance metrics
    logger.info("Performance on training sample:")
    logger.info(f"  AUC score: {train_auc:.3f}")
    logger.info(f"  Accuracy:  {train_accuracy:.3f}")

    logger.info("\nPerformance on test sample:")
    logger.info(f"  AUC score: {test_auc:.3f}")
    logger.info(f"  Accuracy:  {test_accuracy:.3f}")

    # Print more detailed classification report for test set
    logger.info("\nDetailed classification report for test set:")
    logger.info(classification_report(dataTrainTest.y_test, test_pred_binary, target_names=["background", "signal"], sample_weight=dataTrainTest.ws.test))

    return test_auc


def Validate_Classifier(
    model,
    dataTrainTest,
    *,
    BDTcut=0.5,
    output_dir: str = "plots",
    iFold: int = -1,
    # Optional arguments for PlotParticleMass
    plot_mass_var: str = None,
    plot_mass_var_name: str = None,
):
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Plot the train test comparison
    predictions = compare_train_test(model, dataTrainTest)
    plot_compare_train_test(
        decisions=predictions,
        bins=40,
        ws=dataTrainTest.ws,
        output_plot_name=f"{output_dir}/plt_xgboost_output.pdf",
        iFold=iFold,
    )

    # Plot the ROC curve
    PlotSingleROC(
        dataTrainTest.X_test,
        dataTrainTest.y_test,
        dataTrainTest.ws.test,
        model,
        "xgboost",
        "navy",
        output_plot_name=f"{output_dir}/ROCcurve_xgboost.pdf",
    )

    # Plot significance
    PlotSignificance(
        dataTrainTest.X_test,
        dataTrainTest.y_test,
        weights=dataTrainTest.ws.test,
        model=model,
        n_sig=dataTrainTest.df_sig.shape[0],
        n_bkg=dataTrainTest.df_bkg.shape[0],
        output_plot_name=f"{output_dir}/Significance_xgboost.pdf",
    )

    # Plot the feature importance
    PlotFeatureImportance(
        model,
        output_plot_name=f"{output_dir}/FeatureImportance_xgboost.pdf",
        feature_names=dataTrainTest.BDTvars,
    )

    # Plot the loss evolution
    PlotLossEvolution(
        model,
        output_plot_name=f"{output_dir}/LossEvolution_xgboost.pdf",
        metrics=None,
        figsize=(10, 8),
    )

    # ------------------ Plot the particle mass distribution ------------------
    if plot_mass_var:
        # Apply trained model to data and MC
        df_bkg = dataTrainTest.df_bkg
        y_predicted = model.predict_proba(df_bkg[dataTrainTest.BDTvars])[:, 1]
        df_bkg = df_bkg.assign(_XGBDT=y_predicted)

        df_sig = dataTrainTest.df_sig
        y_predicted = model.predict_proba(df_sig[dataTrainTest.BDTvars])[:, 1]
        df_sig = df_sig.assign(_XGBDT=y_predicted)

        # Find common columns
        common_cols = df_bkg.columns.intersection(df_sig.columns)
        df_bkg_aligned = df_bkg[common_cols]
        df_sig_aligned = df_sig[common_cols]

        df_all_aligned = pd.concat([df_bkg_aligned, df_sig_aligned])

        # Plot the Lc mass distribution for signal+bkg
        PlotParticleMass(
            plot_mass_var,
            df_bkg,
            BDTcut,
            dataTrainTest.bdt_weightVar,
            output_plot_name=f"{output_dir}/massWithBDT_{plot_mass_var}_data.pdf",
            particle_name=plot_mass_var_name or plot_mass_var,
        )

        PlotParticleMass(
            plot_mass_var,
            df_sig,
            BDTcut,
            dataTrainTest.bdt_weightVar,
            output_plot_name=f"{output_dir}/massWithBDT_{plot_mass_var}_MC.pdf",
            particle_name=plot_mass_var_name or plot_mass_var,
        )

        PlotParticleMass(
            plot_mass_var,
            df_all_aligned,
            BDTcut,
            dataTrainTest.bdt_weightVar,
            output_plot_name=f"{output_dir}/massWithBDT_{plot_mass_var}_data_and_MC.pdf",
            particle_name=plot_mass_var_name or plot_mass_var,
        )

    # Plot the signal and background distribution comparison for each variable
    # Plot individual variables
    path_to_single_figs: list[str] = []
    plot_dir_path_individual = Path(output_dir) / "BDTvar_comparison" / "individual"
    plot_dir_path_individual.mkdir(parents=True, exist_ok=True)

    for var_title in dataTrainTest.BDTvars:
        _path = plot_individual_variable_comparison(
            var_title=var_title,
            datas=[dataTrainTest.df_sig[var_title], dataTrainTest.df_bkg[var_title]],
            weights=[dataTrainTest.df_sig[dataTrainTest.bdt_weightVar], dataTrainTest.df_bkg[dataTrainTest.bdt_weightVar]],
            labels=["Signal", "Background"],
            output_plot_dir=str(plot_dir_path_individual),
        )
        path_to_single_figs.append(_path)

    # Collect all plots in one canvas
    plot_dir_path_collective = Path(output_dir) / "BDTvar_comparison" / "collective"
    collect_all_plots_in_one_canvas(
        path_to_single_figs=path_to_single_figs,
        output_plot_dir=str(plot_dir_path_collective),
        exts=["pdf", "png"],
    )


# ------------------ main functions ------------------
def train_fold_model(iFold: int, dataTrainTest: DataTrainTest, model_path: str, n_threads: int, BDTvars: list[str]):
    """Train the model"""

    # Train model only
    model = TrainModel(
        dataTrainTest.X_train,
        dataTrainTest.y_train,
        dataTrainTest.ws.train,
        X_test=dataTrainTest.X_test,
        y_test=dataTrainTest.y_test,
        test_wghts=dataTrainTest.ws.test,
        output_model=model_path,
        gamma=2,
        learning_rate=0.005,
        max_depth=12,
        min_child_weight=0.05,
        n_estimators=8500,
        n_jobs=n_threads,
        feature_names=BDTvars,
    )

    return iFold, model


def train_xgboost_model(
    signal_file: str,
    signal_tree_name: str,
    background_file: str,
    background_tree_name: str,
    signal_weight: str,
    background_weight: str,
    bdt_vars: str,
    mode: str,
    num_folds: int,
    split_var: str,
    output_dir: str,
    model_json_name: str,
    n_threads: int,
    # Optional arguments for PlotParticleMass
    plot_mass_var: str = None,
    plot_mass_var_name: str = None,
    sig_max_entries: int = -1,
    bkg_max_entries: int = -1,
    timeout: int = 12 * 60 * 60,  # 12 hours
):
    # Check input arguments
    signal_file_str = ';'.join(signal_file)
    background_file_str = ';'.join(background_file)

    n_threads = check_n_threads(n_threads)

    # Read the BDT variables
    BDTvars = read_yaml(bdt_vars, mode)

    # ------------------ 1. Create the training and testing samples ------------------
    dataTrainTests = dfCreateTrainTest(
        sig_file=signal_file_str,
        bkg_file=background_file_str,
        signal_tree_name=signal_tree_name,
        background_tree_name=background_tree_name,
        BDTvars=BDTvars,
        sig_weightVar=signal_weight,
        bkg_weightVar=background_weight,
        sig_max_entries=sig_max_entries,
        bkg_max_entries=bkg_max_entries,
        nFold=num_folds,
        splitVar=split_var,
        additional_variables_to_load_sig=[plot_mass_var],
        additional_variables_to_load_bkg=[plot_mass_var],
    )

    # ------------------ 2. Train BDT ------------------
    # Get the model paths
    model_paths = GetModelPath(dir_main=output_dir, name_model=model_json_name, nFold=num_folds)

    # Dictionary to store all trained models for combined ROC plot
    trained_models = {}

    # Create fold directories in advance
    for iFold in range(num_folds):
        fold_dir = f"{output_dir}/{iFold}" if num_folds > 0 else output_dir
        Path(fold_dir).mkdir(parents=True, exist_ok=True)

    # * Process training in parallel
    # STEP 1: PARALLEL TRAINING
    logger.info("Starting parallel training of models...")
    n_threads_per_model = max(1, n_threads // num_folds)
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_threads) as executor:
        # Submit training tasks
        future_to_fold = {executor.submit(train_fold_model, iFold, dataTrainTest, model_paths[iFold], n_threads_per_model, BDTvars): iFold for iFold, dataTrainTest in dataTrainTests.items()}

        # Process results as they complete
        for future in tqdm(concurrent.futures.as_completed(future_to_fold, timeout=timeout), total=len(future_to_fold), desc="Training models in parallel", colour="blue"):
            iFold = future_to_fold[future]
            try:
                iFold, model = future.result()
                trained_models[iFold] = model
                logger.info(f"Training for fold {iFold} completed successfully")
            except Exception as exc:
                logger.error(f"Training for fold {iFold} failed with error: {exc}")
                raise

    # STEP 2: SEQUENTIAL VALIDATION AND PLOTTING
    logger.info("All training complete. Starting sequential validation and plotting...")
    for iFold, dataTrainTest in tqdm(dataTrainTests.items(), desc="Validating models", colour="green", ascii=" >━"):
        model = trained_models[iFold]

        # Set the number of threads
        model.get_booster().set_param('nthread', n_threads)

        # Verify model performanceL
        auc_score = PrintModelPerformance(model, dataTrainTest)
        if auc_score < 0.5:  # Basic sanity check for binary classification
            logger.warning(f"Model for fold [bold yellow]{iFold}[/] has poor performance (AUC: [bold yellow]{auc_score:.3f}[/])", extra={"markup": True})

        # Validation and plotting
        output_dir_fold = f"{Path(model_paths[iFold]).parent}/Validate_Classifier"
        _iFold = -1 if num_folds <= 0 else iFold

        Validate_Classifier(model, dataTrainTest, output_dir=output_dir_fold, iFold=_iFold, plot_mass_var=plot_mass_var, plot_mass_var_name=plot_mass_var_name, BDTcut=0.5)

        # Plot correlation matrices
        for cluster in [True, False]:
            plot_correlation_heatmap(
                dataTrainTest.df_sig[dataTrainTest.BDTvars],
                output_plot_name=f"{output_dir_fold}/correlation_matrix_sig_cluster{cluster}.pdf",
                df_weight=dataTrainTest.df_sig[dataTrainTest.bdt_weightVar],
                figsize=(14, 12),
                title="Feature Correlation - Signal",
                cluster=cluster,
            )
            plot_correlation_heatmap(
                dataTrainTest.df_bkg[dataTrainTest.BDTvars],
                output_plot_name=f"{output_dir_fold}/correlation_matrix_bkg_cluster{cluster}.pdf",
                df_weight=dataTrainTest.df_bkg[dataTrainTest.bdt_weightVar],
                figsize=(14, 12),
                title="Feature Correlation - Background",
                cluster=cluster,
            )

    # Combined ROC plot
    if num_folds > 1:
        logger.info("Generating combined ROC curve for all folds...")
        combined_roc_path = f"{output_dir}/combined_roc_curves.pdf"
        PlotMultipleROC(
            folds_data=dataTrainTests,
            models_dict=trained_models,
            output_plot_name=combined_roc_path,
            classifier_name="XGBoost",
        )
        logger.info(f"Combined ROC curve saved to {combined_roc_path}")

    # # * Process training in single thread
    # # Use tqdm to show the progress bar
    # for iFold, dataTrainTest in tqdm(dataTrainTests.items(), desc="Training BDT", colour="green"):
    #     if num_folds > 0:
    #         logger.info(f"Training BDT with {num_folds}-fold cross validation... {iFold}th fold ...")

    #     # Create output directory for this fold
    #     fold_dir = f"{output_dir_fold_main}/{iFold}" if num_folds > 0 else output_dir_fold_main
    #     Path(fold_dir).mkdir(parents=True, exist_ok=True)

    #     # Pass X_test and y_test to the train function to use as validation set
    #     model = TrainModel(
    #         dataTrainTest.X_train,
    #         dataTrainTest.y_train,
    #         dataTrainTest.ws.train,
    #         X_test=dataTrainTest.X_test,
    #         y_test=dataTrainTest.y_test,
    #         test_wghts=dataTrainTest.ws.test,
    #         output_model=model_paths[iFold],
    #         gamma=2,
    #         learning_rate=0.005,
    #         max_depth=12,
    #         min_child_weight=0.05,
    #         n_estimators=8500,
    #         n_jobs=n_threads,
    #         feature_names=BDTvars,
    #     )

    #     # Store the trained model for combined ROC plot
    #     trained_models[iFold] = model

    #     logger.info(f"Model trained and saved to {model_paths[iFold]}, generating validation plots...")

    #     # Verify model performance to ensure it's acceptable
    #     auc_score = PrintModelPerformance(model, dataTrainTest)
    #     if auc_score < 0.5:  # Basic sanity check for binary classification
    #         logger.warning(f"Model for fold [bold yellow]{iFold}[/] has poor performance (AUC: [bold yellow]{auc_score:.3f}[/])", extra={"markup": True})

    #     output_dir_fold = f"{Path(model_paths[iFold]).parent}/Validate_Classifier"

    #     _iFold = -1 if num_folds <= 0 else iFold
    #     Validate_Classifier(model, dataTrainTest, output_dir=output_dir_fold, iFold=_iFold, plot_mass_var=plot_mass_var, plot_mass_var_name=plot_mass_var_name, BDTcut=0.5)

    #     # Plot correlation matrices for features
    #     for cluster in [True, False]:
    #         plot_correlation_heatmap(
    #             dataTrainTest.df_sig[dataTrainTest.BDTvars],
    #             output_plot_name=f"{output_dir_fold}/correlation_matrix_sig_cluster{cluster}.pdf",
    #             df_weight=dataTrainTest.df_sig[dataTrainTest.bdt_weightVar],
    #             figsize=(14, 12),
    #             title="Feature Correlation - Signal",
    #             cluster=cluster,
    #         )
    #         plot_correlation_heatmap(
    #             dataTrainTest.df_bkg[dataTrainTest.BDTvars],
    #             output_plot_name=f"{output_dir_fold}/correlation_matrix_bkg_cluster{cluster}.pdf",
    #             df_weight=dataTrainTest.df_bkg[dataTrainTest.bdt_weightVar],
    #             figsize=(14, 12),
    #             title="Feature Correlation - Background",
    #             cluster=cluster,
    #         )

    # # Plot combined ROC curves if multiple folds were trained
    # if num_folds > 1:
    #     logger.info("Generating combined ROC curve for all folds...")
    #     combined_roc_path = f"{output_dir_fold_main}/combined_roc_curves.pdf"
    #     PlotMultipleROC(
    #         folds_data=dataTrainTests,
    #         models_dict=trained_models,
    #         output_plot_name=combined_roc_path,
    #         classifier_name="XGBoost",
    #     )
    #     logger.info(f"Combined ROC curve saved to {combined_roc_path}")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('--signal-file', type=str, required=True, nargs='+', help='Signal file')
    parser.add_argument('--signal-tree-name', type=str, default='DecayTree', help='Signal tree name')
    parser.add_argument('--background-file', type=str, required=True, nargs='+', help='Background file')
    parser.add_argument('--background-tree-name', type=str, default='DecayTree', help='Background tree name')

    parser.add_argument('--signal-weight', type=str, required=False, default='1', help='Signal weight')
    parser.add_argument('--background-weight', type=str, required=False, default='1', help='Background weight')

    parser.add_argument('--bdt-vars', type=str, required=True, help='BDT variables')
    parser.add_argument('--mode', type=str, required=True, help='Mode')
    parser.add_argument('--num-folds', type=int, default=10, help='Number of folds')
    parser.add_argument('--split-var', type=str, default='eventNumber', help='Split variable')

    parser.add_argument('--output-dir', type=str, default='output/models', help='Output directory for models and plots')
    parser.add_argument(
        '--model-json-name',
        type=str,
        default='xgb_model.json',
        help='Output model JSON name, will be saved in the output directory (k-fold models will be saved in the output directory/kFolds subdirectory, be handled automatically)',
    )

    parser.add_argument('--n-threads', type=int, default=0, help='Number of threads to use. Default: 0. [0: half of the threads, -1: all threads, other: specific number of threads]')

    # Optional arguments for PlotParticleMass
    parser.add_argument('--plot-mass-var', type=str, default=None, help='Plot the particle mass distribution for the given variable')
    parser.add_argument('--plot-mass-var-name', type=str, default=None, help='Plot the particle mass distribution for the given variable name')

    parser.add_argument('--sig-max-entries', type=int, default=-1, help='Maximum number of entries to use for signal training and testing')
    parser.add_argument('--bkg-max-entries', type=int, default=-1, help='Maximum number of entries to use for background training and testing')

    parser.add_argument('--timeout', type=int, default=12 * 60 * 60, help='Timeout for training in seconds')

    return parser


def main(args=None):
    """Main entry point for the script."""
    if args is None:
        args = get_parser().parse_args()
    train_xgboost_model(**vars(args))


if __name__ == "__main__":

    # Run the main function
    main()
