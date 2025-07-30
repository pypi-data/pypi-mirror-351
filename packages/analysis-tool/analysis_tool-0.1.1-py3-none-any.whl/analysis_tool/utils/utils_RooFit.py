'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-06-19 16:16:39 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2025-05-21 03:45:26 +0200
FilePath     : utils_RooFit.py
Description  :

Copyright (c) 2024 by everyone, All Rights Reserved.
'''

import os
import math
import json, yaml
import argparse
import cppyy
from array import array
import multiprocessing
from fnmatch import fnmatch

from pathlib import Path
import colorama
import warnings

import uproot as ur
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product

from typing import Any, List, Dict, Optional, Union


from ROOT import addressof
from ROOT import (
    kDashed,
    kRed,
    kGreen,
    kBlue,
    kBlack,
    kTRUE,
    kFALSE,
    gPad,
    std,
    TArrow,
    TGraph,
    TLine,
)
from ROOT import (
    TMath,
    TAxis,
    TH1,
    TH1F,
    TLegend,
    TLatex,
    TPaveText,
    TROOT,
    TSystem,
    TCanvas,
    TChain,
    TFile,
    TTree,
    TObject,
    gROOT,
    gStyle,
)
from ROOT import ROOT, RDataFrame, vector, gInterpreter, gSystem
from ROOT import (
    RooFit,
    RooFitResult,
    RooAbsData,
    RooAbsPdf,
    RooArgSet,
    RooArgList,
    RooAbsDataStore,
    RooAddModel,
    RooAddPdf,
    RooAddition,
    RooCBShape,
    RooChebychev,
    RooConstVar,
    RooDataSet,
    RooExponential,
    RooFFTConvPdf,
    RooFormulaVar,
    RooGaussian,
    #    RooGlobalFunc,
    RooHypatia2,
    RooMinimizer,
    RooPlot,
    RooPolynomial,
    RooProdPdf,
    RooRealVar,
    RooVoigtian,
    RooStats,
)


# Logging setup
from rich import print as rprint
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


from warnings import warn

from ..correlation.matrixHelper import plot_correlation_matrix, write_correlation_matrix_latex
from .utils_json import read_json
from .utils_ROOT import save_pic_from_tcanvas


# =============================================================#
# ----------------------RooFit area----------------------------#


def read_params(params_file: str) -> dict:
    """Common helper
    Read parameters from json file.
        params_file: [str] the address to the parameter file.
    """
    with open(params_file, "r") as stream:
        return json.load(stream)


def fix_param(par_name: str, mc_param: dict, pdfPars_Arg: RooArgSet) -> None:
    """
    Set the parameter to be fixed
        par_name: [str] the name of the parameter to be fixed
        mc_param: [dict] the parameter to be fixed (read from previous fit result)
        pdfPars_Arg: [RooArgSet] the RooArgSet containing parameters
    """
    par = pdfPars_Arg.find(par_name)
    if par:
        par.setVal(mc_param["Value"])
        par.setConstant(True)
        logger.info(f"Setting parameter {par_name} to constant with value {mc_param['Value']}")
    else:
        logger.warning(f"Could not find parameter {par_name} in the RooFit RooArgSet")


def params_to_fix_helper_json(
    params_to_fix_file: str,
    pdfPars_Arg: RooArgSet,
    params_to_fix_list: List[str],
    fuzzyMatch: bool = True,
    dict_key: str = "Params",
) -> None:
    """params_to_fix helper
    Helper function to fix parameters with the value derived from MC conveniently.
    MC fit results are stored in json format.
        params_to_fix_file: [str] the path to where json file stored.
        pdfPars_Arg: [RooArgSet] the RooArgList format class which stores all variables used in PDF construction.
        params_to_fix_list: [list] a list referes to the variables need to be read from file and then be fixed
        fuzzyMatch: [bool] whether use fuzzy match mode.
    """
    # Check if params list is empty
    if all(item == "" for item in params_to_fix_list):
        return None

    # Read parameters from JSON file
    cat_params = read_json(params_to_fix_file, dict_key) if params_to_fix_file else None
    if not cat_params:
        logger.warning(f"Could not find parameters in the JSON file {params_to_fix_file}")
        return None

    ##################################################
    # def find_param(param_toFind, fuzzyMatch, cat_params):
    #     # find the parameter to be fixed from previous fit result
    #     if fuzzyMatch:
    #         # support fuzzy matching
    #         mc_param_list = [p for p in cat_params if param_toFind in p['Name']]
    #         for mc_param in mc_param_list:
    #             par_name = mc_param['Name']

    #             if pdfPars_Arg.find(par_name):
    #                 return par_name

    ##################################################

    # if fix parameters in the fit
    for par in params_to_fix_list:
        if fuzzyMatch:
            # support fuzzy matching
            mc_param_list = [p for p in cat_params if fnmatch(p["Name"], par)]
            for mc_param in mc_param_list:
                par_name = mc_param["Name"]

                fix_param(par_name, mc_param, pdfPars_Arg)
                # if pdfPars_Arg.find(par_name):
                #     pdfPars_Arg.find(par_name).setVal(mc_param['Value'])
                #     pdfPars_Arg.find(par_name).setConstant(True)
                #     rprint(f"params_to_fix_helper_json::Setting parameter {par_name} to constant with value {mc_param['Value']}")
                # else:
                #     rprint(f"params_to_fix_helper_json::Could not find parameter {par_name} in the RooFit RooArgSet")
        else:
            # for par in params_to_fix_list:
            mc_param_matches = [p for p in cat_params if par in p["Name"]]
            if mc_param_matches:
                mc_param = mc_param_matches[0]
                par_name = mc_param["Name"]

                # par_name should be exactly the name stored in RooRealVar
                fix_param(par_name, mc_param, pdfPars_Arg)

                # if pdfPars_Arg.find(par_name):
                #     pdfPars_Arg.find(par_name).setVal(mc_param['Value'])
                #     pdfPars_Arg.find(par_name).setConstant(True)
                #     rprint(f"params_to_fix_helper_json::Setting parameter {par_name} to constant with value {mc_param['Value']}")
                # else:
                #     rprint(f"params_to_fix_helper_json::Could not find parameter {par_name} in the RooFit RooArgSet")


def params_to_fix_helper_func(
    params_to_fix_file: str,
    pdfPars_Arg: RooArgList,
    params_to_fix_list: list,
    fuzzyMatch: bool = True,
):
    """params_to_fix helper
    Helper function to fix parameters with the value derived from MC conveniently.
    MC fit results are stored in func format (stored by calling RooFit embedded writeToFile method).
        params_to_fix_file: [str] the path to where json file stored.
        pdfPars_Arg: [RooArgList] the RooArgList format class which stores all variables used in PDF construction.
        params_to_fix_list: [list] a list referes to the variables need to be read from file and then be fixed
        fuzzyMatch: [bool] whether use fuzzy match mode.
    """
    # Check input arguments
    if all(item == "" for item in params_to_fix_list):
        return None

    # Read parameters by using ROOT embedded methods
    pdfPars_List = RooArgList(pdfPars_Arg)
    for par in params_to_fix_list:
        for i in range(pdfPars_List.getSize()):
            party = RooRealVar(pdfPars_List.at(i))

            if (fuzzyMatch and fnmatch(party.GetName(), par)) or (not fuzzyMatch and par == party.GetName()):
                _party = pdfPars_Arg.find(party.GetName())
                # Read from params_to_fix_file and set them to be constant
                RooArgSet(_party).readFromFile(params_to_fix_file)
                _party.setConstant(True)
                logger.info(f"Setting parameter {_party.GetName()} to constant with value {_party.getVal()}")


def free_param(par_name: str, party: RooRealVar, pdfPars_Arg: RooArgList, fuzzyMatch: bool) -> None:
    """
    Set the parameter to be freed
        par_name: [str] the pattern to match for parameter freeing
        party: [RooRealVar] the parameter to check for potential freeing
        pdfPars_Arg: [RooArgList] list of all parameters
        fuzzyMatch: [bool] whether to use fuzzy matching
    """
    if (fuzzyMatch and fnmatch(party.GetName(), par_name)) or (not fuzzyMatch and par_name == party.GetName()):
        _party = pdfPars_Arg.find(party.GetName())
        _party.setConstant(False)
        logger.info(f"Setting parameter {_party.GetName()} to free with initial value {_party.getVal()} and range {list(_party.getRange())}")


def params_to_free_helper(pdfPars_Arg: RooArgList, params_to_free_list: List[str], fuzzyMatch: bool = True) -> None:
    """params_to_free helper
    Helper function to free parameters with the value which was fixed.
        pdfPars_Arg: [RooArgList] the RooArgList format class which stores all variables used in PDF construction.
        params_to_free_list: [list] a list referes to the variables need to be freed.
        fuzzyMatch: [bool] whether use fuzzy match mode.
    """
    # Check if params list is empty
    if all(item == "" for item in params_to_free_list):
        return None

    # Prepare info by using fuzzy matching
    pdfPars_List = RooArgList(pdfPars_Arg)
    for par in params_to_free_list:
        for i in range(pdfPars_List.getSize()):
            party = RooRealVar(pdfPars_List.at(i))

            free_param(par, party, pdfPars_Arg, fuzzyMatch)

            # if fuzzyMatch and par in party.GetName() or not fuzzyMatch and par == party.GetName():
            #     _party = pdfPars_Arg.find(party.GetName())
            #     _party.setConstant(False)
            #     rprint(f"Setting parameter {_party.GetName()} to free with initial value {_party.getVal()} and range {list(_party.getRange())}")


def add_unique_to_argset(
    argset: RooArgSet,
    arg: RooRealVar,
) -> None:
    """RooFit helper
    Add unique argument to RooArgSet
        argset: [RooArgSet] the RooArgSet object.
        arg: [RooAbsArg] the RooAbsArg object.
    """
    if not argset.find(arg.GetName()):
        argset.add(arg)
    else:
        warnings.warn(f"RooFit::add_unique_to_argset : {arg.GetName()} already exists in the RooArgSet")


def check_fit_convergence(r: RooFitResult, strategy: int) -> bool:
    """
    Check whether fit converged accoring to the following judging conditions
        1) covQual   | Fully accurate covariance matrix(after MIGRAD)
        2) edn       | Estimated distance to minimum
        3) fitStatus | Overall variable that characterises the goodness of the fit
    return:
        False : not converged
        True : converged
    """
    flag_covQual = r.covQual() == 3  # 0: not calculated, 1: approximated, 2: full matrix, 3: full accurate matrix
    flag_edm = r.edm() < 0.01 if strategy == 2 else r.edm() < 1  # 0.01 for strategy 2, 1 for strategy 1
    flag_fitStatus = r.status() == 0  # 0: OK, 1:Covariance was mad epos defined, 2:Hesse is invalid, 3:Edm is above max, 4:Reached call limit, 5:Any other failure

    return flag_covQual and flag_edm and flag_fitStatus


def RooMinimizer_helper(
    mCC: RooMinimizer,
    strategy: int = 1,
    verbose: int = 1,
    minos: bool = False,
    maxTries: int = 2,
) -> RooFitResult:
    """RooFit helper
    RooMinimizer manager.
        mCC: [RooMinimizer] the RooMinizer prepared.
        strategy: [int] the fit strategy (0,1,2).
        verbose: [int] verbosity level option of RooMinimizer object (0,1,2,3).
        minos: [bool] whether execute minos after migrad.
        maxTries: [int] the maximum number of attempts for migrad if failed.
    """
    logger.info("INFO::RooMinimizer_helper : Fit start")

    statusVal_migrad = -1  # Migrad status
    # statusVal_hesse = -1  # hesse status
    # statusVal_minos = -1  # minos status

    mCC.setStrategy(strategy)
    mCC.setVerbose(False)  # mCC.setVerbose(bool(verbose))
    mCC.setPrintLevel(verbose)
    # statusVal_migrad = mCC.migrad()
    statusVal_migrad = mCC.minimize("Minuit", "MIGRAD")  # minize with simplex and migrad
    RooFitRes = mCC.save()  # take snap-shot for roofit results, to retrieve fit info.(such as status info.)
    # Migrad status

    #  Check whether status of MIGRAD is OK
    #  0: OK, 1:Covariance was mad epos defined, 2:Hesse is invalid, 3:Edm is above max, 4:Reached call limit, 5:Any other failure
    Tries = max(maxTries, 2)

    while (not check_fit_convergence(RooFitRes, strategy)) and (Tries > 0):
        # statusVal_migrad = mCC.migrad()  # Migrad status
        if Tries == maxTries:
            statusVal_migrad = mCC.minimize("Minuit2", "SIMPLEX;MIGRAD")
        else:
            statusVal_migrad = mCC.minimize("Minuit", "MIGRAD")
        RooFitRes = mCC.save()
        Tries = Tries - 1
    if not check_fit_convergence(RooFitRes, strategy):
        warnings.warn(f"{colorama.Fore.YELLOW}migrad did not converge after {maxTries} tries\n{colorama.Style.RESET_ALL}")

    # Calculate error by using hesse
    statusVal_hesse = mCC.hesse()
    if minos:
        statusVal_minos = mCC.minos()

    RooFitRes = mCC.save()

    if verbose > 0:
        logger.info("INFO::RooMinimizer_helper : Fit status:")
        logger.info(f'    overall status = {RooFitRes.status()}')
        logger.info(f"    migrad = {statusVal_migrad}")
        logger.info(f"    hesse = {statusVal_hesse}")
        logger.info(f"    minos = {statusVal_minos}")

    return RooFitRes


def fitTo_helper(
    model: RooAbsPdf,
    data: RooDataSet,
    *,
    strategy: int = 1,
    minimizer: str = 'Minuit',
    minos: bool = False,
    max_tries: int = 5,
    n_threads: int = 1,
    sumW2Error: bool = False,
) -> RooFitResult:
    """
    Perform the fit with multiple attempts if needed.

    Args:
        model: Model to fit
        data: Dataset to fit against
        strategy: Strategy to use for the fit
        minimizer: Minimizer to use for the fit
        max_tries: Maximum number of attempts to perform the fit
        n_threads: Number of threads to use
        SumW2Error: Whether to use SumW2Error for the fit.  True:  reflect the error corresponding to the yields of input statistics;
                                                            False: reflect the error corresponding to the yields of weighted sum

    Returns:
        RooFitResult from the fit
    """
    # Initialize variables for the fit attempts
    fitresult_status = -1
    n_tries = 0

    # Try multiple fits until convergence or max attempts reached
    while (fitresult_status != 0) and (n_tries < max_tries):
        logger.info(f'Attempting fit {n_tries+1}/{max_tries} ...')

        # Use strategy 2 for the 2nd last attempt
        _strategy = 2 if n_tries == max_tries - 2 else strategy

        fitresult = model.fitTo(
            data,
            RooFit.Minimizer(minimizer),
            RooFit.Strategy(_strategy),
            RooFit.Save(True),
            RooFit.Minos(minos),
            RooFit.NumCPU(n_threads),
            RooFit.SumW2Error(sumW2Error),
        )
        fitresult_status = fitresult.status()
        n_tries += 1

    if fitresult_status != 0:
        logger.warning(f'Fit did not converge after {max_tries} attempts: status = {fitresult_status}')

    return fitresult


def show_chi_square(frame: RooPlot, fit_plt_name: str, data_plt_name: str, title: str) -> None:
    """RooFit helper
    Calculate chi2 according to given data and pdf
        frame: [RooPlot] frame constructed as RooPlot object.
        fit_plt_name: [str] the name of fit plot within frame.
        data_plt_name: [str] the name of data plot within frame.
        title: [str] title for the output output information.
    """
    chi2_ndof2 = frame.chiSquare(fit_plt_name, data_plt_name, 2)
    chi2_ndof4 = frame.chiSquare(fit_plt_name, data_plt_name, 4)
    logger.info("=========================================")
    logger.info(f"------------- {title} -------------")
    logger.info(f"chiSquare_NDOF(2) = {chi2_ndof2}")
    logger.info(f"chiSquare_NDOF(4) = {chi2_ndof4}")
    logger.info("=========================================")


def PDF_inspect(mypdf: RooAbsPdf) -> None:
    """RooFit helper
    Inspect given PDF infomation.
        mypdf: [RooAbsPdf] the given pdf.
    """
    logger.info("\n- - - - - - - - - - - - - - - - -")
    logger.info("Debug Info: Inspect PDF")
    logger.info(f"PDF name : {mypdf.GetName()}")
    mypdf.Print()
    mypdf.Print("t")
    logger.info("- - - - - - - - - - - - - - - - -\n")


def Par_inspect(mypdf: RooAbsPdf, mydata: RooDataSet) -> None:
    """RooFit helper
    Inspect parameters information within given PDF and corresponding dataset.
        mypdf: [RooAbsPdf] the given pdf.
        mydata: [RooDataSet] the corresponding dataset.
    """
    logger.info("\n- - - - - - - - - - - - - - - - -")
    logger.info("Debug Info: Inspect Parameters")
    logger.info(f"PDF name : {mypdf.GetName()}         data name: {mydata.GetName()}")
    paramList = mypdf.getParameters(mydata)
    paramList.Print()
    paramList.Print("v")
    logger.info("- - - - - - - - - - - - - - - - -\n")


def print_RooArgSet(params: RooArgSet, print_constants: bool = True, print_option: str = "") -> Dict[str, RooArgSet]:
    """
    Print contents of a RooArgSet, separating free and fixed parameters

    Args:
        params: RooArgSet containing parameters to print
        print_constants: Whether to print constant parameters
        print_option: Print option flag passed to RooRealVar.Print()

    Returns:
        Dictionary containing free and fixed parameters as RooArgSets
    """
    logger.info(f"INFO:printRooArgSet: Check RooArgSet {params.GetName()}")

    argSetFix = RooArgSet()
    argSetFree = RooArgSet()

    # Use range-based iteration
    for i in range(params.size()):
        arg = params[i]
        if isinstance(arg, RooRealVar):
            if arg.isConstant():
                argSetFix.add(arg)
            else:
                argSetFree.add(arg)

    def _print_arg_set(arg_set: RooArgSet, title: str) -> None:
        logger.info(f"--- {title} ---")

        if arg_set.getSize() == 0:
            logger.info("INFO:printRooArgSet: No parameters to print")
            return

        for i in range(arg_set.size()):
            arg_set[i].Print(print_option)

    # Print free parameters
    _print_arg_set(argSetFree, "Free parameters")

    # Print constants if requested
    if print_constants:
        _print_arg_set(argSetFix, "Constants")

    return {"free": argSetFree, "fix": argSetFix}


def plot_correlation_matrix_from_RooFitResult(r: RooFitResult, output_file: str) -> None:
    """Draw the correlation matrix using matplotlib

    Args:
        fitResult (RooFitResult): RooFitResult object containing the fit result
    """
    # Extract the correlation matrix as a numpy array
    correlationMatrix = np.zeros((r.correlationMatrix().GetNrows(), r.correlationMatrix().GetNcols()))
    for i, j in product(range(r.correlationMatrix().GetNrows()), range(r.correlationMatrix().GetNcols())):
        correlationMatrix[i][j] = r.correlationMatrix()[i][j]

    # varNames = [_spruce_varName(var.GetName()) for var in r.floatParsFinal()]
    varNames = [var.GetName() for var in r.floatParsFinal()]

    # def _latexnise_varName(varName):
    #     varName = varName.replace("delta", r"$\Delta$")
    #     varName = varName.replace("sigma", r"$\sigma$")
    #     varName = varName.replace("mean", r"$\mu$")
    #     varName = varName.replace("alpha", r"$\alpha$")
    #     varName = varName.replace("frac", r"f")

    #     varName = varName.replace("k_bkgcomb", r"$k_{comb}$")

    #     varName = varName.replace("nsig", r"$N_{sig}$")
    #     varName = varName.replace("n_bkgcomb", r"$N_{comb}$")

    #     # Bd -> B^0 and Bs -> B_s^0
    #     varName = varName.replace("Bd", r"$B^{0}$")
    #     varName = varName.replace("Bs", r"$B_{s}^{0}$")

    #     return varName

    # varNames = [_latexnise_varName(varName) for varName in varNames]

    # Draw the correlation matrix
    plot_correlation_matrix(correlationMatrix, varNames, output_file)


def write_correlation_matrix_latex_from_RooFitResult(
    r: RooFitResult,
    output_file: str,
    column_width: Optional[float] = None,
    rotate_column_headers: int = 90,
) -> None:
    """Write the correlation matrix to a latex file

    Args:
        r (RooFitResult): RooFitResult object containing the fit result
        output_file (str): Path to the output file
        column_width (float, optional): The column width will be fixed if specified (in the unit of cm). Defaults to None, automatically determined.
        rotate_column_headers (int, optional): Rotate the column headers. Defaults to 90.
    """
    # Extract the correlation matrix as a numpy array
    correlationMatrix_np = np.zeros((r.correlationMatrix().GetNrows(), r.correlationMatrix().GetNcols()))
    for i, j in product(range(r.correlationMatrix().GetNrows()), range(r.correlationMatrix().GetNcols())):
        correlationMatrix_np[i][j] = r.correlationMatrix()[i][j]

    # varNames = [_spruce_varName(var.GetName()) for var in r.floatParsFinal()]
    varNames = [var.GetName() for var in r.floatParsFinal()]

    write_correlation_matrix_latex(
        correlationMatrix=correlationMatrix_np,
        varNames=varNames,
        output_file=output_file,
        column_width=column_width,
        rotate_column_headers=rotate_column_headers,
    )


def EX_additional_FitRes(RooFitRes: RooFitResult, CorrMartix_PicName: str) -> None:
    """RooFit helper
    Extract additional fit results after fit (numerical results, Correlation matrix)
        RooFitResult: [RooFitRes] the fit result saved as RooFitRes object.
        CorrMartix_PicName: [str] the location where covariance and correlation matrix will be saved.
    """
    # Verbose printing: Basic info, values of constant parameters, initial and
    # final values of floating parameters, global correlations
    RooFitRes.Print("v")

    # The quality of covariance
    logger.info(f"covQual = {RooFitRes.covQual()}")
    # Extract covariance and correlation matrix as TMatrixDSym
    cor = RooFitRes.correlationMatrix()
    cov = RooFitRes.covarianceMatrix()

    # Print correlation, covariance matrix
    logger.info("correlation matrix")
    cor.Print()
    logger.info("covariance matrix")
    cov.Print()

    # Construct 2D color plot of correlation matrix
    gStyle.SetOptStat(0)
    gStyle.SetPalette(1)
    hcorr = RooFitRes.correlationHist()

    c_correlation = TCanvas("c_correlation", "", 1400, 1000)
    c_correlation.cd()
    gPad.SetLeftMargin(0.15)
    hcorr.GetYaxis().SetTitleOffset(1.4)
    hcorr.Draw("colz")

    extSuffix = [".pdf", ".png", ".C"]
    if os.path.splitext(CorrMartix_PicName)[1] in extSuffix:
        CorrMartix_PicName_full = CorrMartix_PicName
    else:
        CorrMartix_PicName_full = f"{CorrMartix_PicName}.pdf"

    c_correlation.SaveAs(CorrMartix_PicName_full)

    # Plot correlation matrix by using matplotlib
    plot_correlation_matrix_from_RooFitResult(
        r=RooFitRes,
        output_file=f"{CorrMartix_PicName_full.rsplit('.',1)[0]}_matplot.pdf",
    )

    # Save correlation matrix into a tex file in Latex format
    write_correlation_matrix_latex_from_RooFitResult(r=RooFitRes, output_file=f"{CorrMartix_PicName_full.rsplit('.',1)[0]}.tex")  # , column_width="1cm")


def _RooSaveFitPlot_helper_logo(logo: TPaveText) -> None:
    """RooFit helper sub"""
    logo.SetShadowColor(0)
    logo.SetFillStyle(0)
    logo.SetBorderSize(0)
    logo.SetTextAlign(12)
    # logo.SetTextSize(0.08)


def _RooSaveFitPlot_helper_latex(latex: TLatex) -> None:
    """RooFit helper sub"""
    latex.SetTextFont(132)
    latex.SetTextSize(0.05)
    latex.SetLineWidth(2)


def _RooSaveFitPlot_helper_leg(leg: TLegend) -> None:
    """RooFit helper sub"""
    leg.SetBorderSize(0)
    leg.SetTextFont(132)
    leg.SetTextSize(0.045)
    leg.SetFillColor(0)


def _RooSaveFitPlot_helper_pull(
    data: RooDataSet,
    fitpdf: RooAbsPdf,
    fitvar: RooRealVar,
    frame: RooPlot,
    pullstyle: int,
) -> RooPlot:
    """RooFit helper for preparing pull distribution

    Args:
        data: the dataset
        fitpdf: the corresponding pdf
        fitvar: the corresponding variable used
        frame: the corresponding frame respect to data and pdf
        pullstyle: pull distribution style option (0: not draw pull, 1: style1, 2: style2)

    Returns:
        RooPlot containing the pull distribution or None if pullstyle=0
    """

    if not pullstyle:
        return None

    # Get number of bins & [x_low,x_high] from plot
    nBin = frame.GetXaxis().GetNbins()
    x_l, x_h = frame.GetXaxis().GetXmin(), frame.GetXaxis().GetXmax()

    # Create frame for pull distribution
    pframe = fitvar.frame(RooFit.Title("Pull distribution"), RooFit.Bins(nBin), RooFit.Range(x_l, x_h))
    data.plotOn(pframe)
    fitpdf.plotOn(pframe)
    pull = fitvar.frame(RooFit.Bins(nBin), RooFit.Range(x_l, x_h))
    hpull = pframe.pullHist()

    # Helper to set Y-axis properties
    def helper_set_Yaxis(pull_frame):
        pull_frame.GetYaxis().SetRangeUser(-5, 5)
        pull_frame.GetYaxis().SetNdivisions(505)
        pull_frame.GetYaxis().SetLabelSize(0.20)

    if pullstyle == 1:
        # Style 1: filled histogram style
        hpull.SetFillColor(15)
        hpull.SetFillStyle(3144)
        pull.addPlotable(hpull, "L3")
        helper_set_Yaxis(pull)
        return pull

    elif pullstyle == 2:
        # Style 2: points with error bars and reference lines
        # First add the reference lines (so they'll be drawn behind the data points)
        xmin, xmax = pull.GetXaxis().GetXmin(), pull.GetXaxis().GetXmax()

        # Create and add reference lines
        lines = [
            TLine(xmin, 0, xmax, 0),  # Center line
            TLine(xmin, 3, xmax, 3),  # Upper line
            TLine(xmin, -3, xmax, -3),  # Lower line
        ]

        for line in lines:
            line.SetLineStyle(7)
            line.SetLineColor(2)
            line.SetLineWidth(2)
            pull.addObject(line)

        # Now add the data points on top of the lines
        hpull.SetLineWidth(1)
        hpull.SetFillStyle(3001)
        pull.addPlotable(hpull, "PE")

        pull.SetTitle("")
        pull.GetXaxis().SetTitle("")
        helper_set_Yaxis(pull)

        return pull


def RooSaveFitPlot_helper(
    data: RooDataSet,
    fitpdf: RooAbsPdf,
    fitvar: RooRealVar,
    frame: RooPlot,
    picname: str,
    logo: TPaveText = None,
    latex: TLatex = None,
    leg: TLegend = None,
    XTitle: str = "",
    YTitle: str = "",
    pullstyle: int = 2,
    SetYmax: float = 0,
) -> None:
    """RooFit helper
    Save plots
        data: [RooDataSet] the dataset.
        fitpdf: [RooAbsPdf] the corresponing pdf.
        fitvar: [RooRealVar] the corresponding variable used.
        frame: [RooPlot] the corresponding frame respect to data and pdf.
        logo: [TPaveText] add a logo.
        latex: [TLatex] add a latex.
        leg: [TLegend] add a legend.
        picname: [string] path to where picture be stored.
        XTitle: [str] title of x-axis.
        YTitle: [str] title of y-axis.
        pullstyle: [int] pull distribution syle option (0: not draw pull, 1: style1, 2: style2).
        SetYmax: [int] raw an additional plot with user customized height of y-axis.
    """
    gROOT.SetBatch(1)

    # minimum/maxmimum of y-axis
    YMIN = frame.GetMaximum()
    YMAX = frame.GetMaximum()
    # Intrinsic minimum/maximum of y-axis
    ymin = 1e-2
    ymax = YMAX * 1.3
    frame.SetMinimum(1e-2)  # we only want positive value while has negative caused by weight
    frame.SetMaximum(ymax)

    # set X/Y axis related
    # title
    if XTitle:
        frame.SetXTitle(XTitle)
    if YTitle:
        frame.SetYTitle(YTitle)

    xAxis, yAxis = [frame.GetXaxis(), frame.GetYaxis()]

    if ymax < 1e2:
        yoff = 0.9
    elif ymax >= 1e2 and ymax < 1e3:
        yoff = 0.95
    elif ymax >= 1e3 and ymax < 1e4:
        yoff = 1.10
    else:  # ymax >= 1e4:
        yoff = 1.20
    xAxis.SetTitleFont(132)
    yAxis.SetTitleFont(132)
    xAxis.SetTitleSize(0.06)
    yAxis.SetTitleSize(0.06)
    xAxis.SetTitleOffset(1.15)
    yAxis.SetTitleOffset(yoff)
    xAxis.SetLabelOffset(0.02)
    yAxis.SetLabelOffset(0.01)

    # Set LHCb logo
    if logo:
        _RooSaveFitPlot_helper_logo(logo)
        frame.addObject(logo)

    # Set latex
    if latex:
        _RooSaveFitPlot_helper_latex(latex)
        frame.addObject(latex)

    # Set legend
    if leg:
        _RooSaveFitPlot_helper_leg(leg)
        frame.addObject(leg)

    # Create a helper function for setting pad margins
    def helper_set_gPad_common(yl, yh):
        gPad.SetLeftMargin(0.15)
        gPad.SetRightMargin(0.03)
        gPad.SetPad(0.02, yl, 0.98, yh)

    # Draw the plot - handle differently based on whether we need a pull plot
    pic2 = TCanvas("pic2", "", 800, 600)

    if pullstyle:
        # We need a pull plot - divide canvas into two pads
        pic2.Divide(1, 2, 0, 0, 0)

        # Bottom pad for main plot (larger)
        pic2.cd(2)
        gPad.SetTopMargin(0.015)
        gPad.SetBottomMargin(0.15)
        helper_set_gPad_common(yl=0.02, yh=0.77)
        frame.Draw()

        # Top pad for pull plot (smaller)
        pic2.cd(1)
        gPad.SetTopMargin(0)
        helper_set_gPad_common(yl=0.8, yh=0.98)

        pull = _RooSaveFitPlot_helper_pull(data, fitpdf, fitvar, frame, pullstyle)
        pull.Draw()
    else:
        # No pull plot - use the full canvas for the main plot
        pic2.cd()
        gPad.SetTopMargin(0.05)
        gPad.SetBottomMargin(0.15)
        gPad.SetLeftMargin(0.15)
        gPad.SetRightMargin(0.03)
        frame.Draw()

    # prepare for saving plots
    extSuffix = [".pdf", ".png", ".C"]

    if os.path.splitext(picname)[1] in extSuffix:
        picname_noExt = os.path.splitext(picname)[0]
        picname_Ext = os.path.splitext(picname)[1]
    else:
        picname_noExt = picname
        picname_Ext = extSuffix

    # 1) Nominal plot
    save_pic_from_tcanvas(pic2, picname_noExt, picname_Ext)

    # 2) Log plot
    if pullstyle:
        pic2.cd(2)  # Select the main plot pad if we have a pull plot
    else:
        pic2.cd()  # Select the only pad if no pull plot

    frame.SetMaximum(frame.GetMaximum() * 20.0)
    frame.SetMinimum(1e-1)
    gPad.SetLogy(1)
    picname_noExt_log = f"{picname_noExt}_log"
    save_pic_from_tcanvas(pic2, picname_noExt_log, picname_Ext)

    # 3) plot with customized height
    if SetYmax:
        if pullstyle:
            pic2.cd(2)  # Select the main plot pad if we have a pull plot
        else:
            pic2.cd()  # Select the only pad if no pull plot

        frame.SetMaximum(SetYmax)
        frame.SetMinimum(1e-1)
        gPad.SetLogy(0)
        picname_noExt_customizedYmax = f"{picname_noExt}_customizedYmax"
        save_pic_from_tcanvas(pic2, picname_noExt_customizedYmax, picname_Ext)
