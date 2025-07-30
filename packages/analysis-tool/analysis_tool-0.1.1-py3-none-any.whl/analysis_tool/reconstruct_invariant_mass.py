'''
Author       : Jie Wu j.wu@cern.ch
Date         : 2024-09-21 10:46:18 +0200
LastEditors  : Jie Wu j.wu@cern.ch
LastEditTime : 2024-09-21 13:59:56 +0200
FilePath     : reconstruct_invariant_mass.py
Description  : 

Copyright (c) 2024 by everyone, All Rights Reserved. 
'''

import ROOT as r
from ROOT import gROOT, gInterpreter
from ROOT import RDataFrame
from ROOT import TFile, TTree
import itertools
from pathlib import Path
import colorama


def reconstruct_invariant_mass(
    input_file_name: str,
    input_tree_name: str,
    track_names: list[str],
    mass_hypotheses: list[str] = None,
    maximum_combinations: int = -1,
    output_file_name: str = "output.root",
    output_tree_name: str = "output_tree",
    use_energy_instead_of_momentum: bool = False,
    save_new_branches_only: bool = False,
    momentum_units: str = "MeV",
    verbose: bool = False,
):
    """
    Reconstructs the invariant mass of combinations of particles with different mass hypotheses,
    and saves each combination as a separate branch in the output TTree.

    Args:
        input_file_name (str): Name of the input ROOT file.
        input_tree_name (str): Name of the input TTree.
        track_names (List[str]): List of prefixes for the branches saved in the input file corresponding to different tracks.
        mass_hypotheses (List[str], optional): List of mass hypotheses to be used for each particle.
                                               Defaults to ['pion', 'kaon', 'proton', 'muon', 'electron'].
        maximum_combinations (int, optional): Maximum number of particles to combine. -1 for all combinations.
                                              Defaults to -1 (all combinations).
        output_file_name (str, optional): Name of the output ROOT file. Defaults to "output.root".
        output_tree_name (str, optional): Name of the output TTree. Defaults to "output_tree".
        use_energy_instead_of_momentum (bool, optional): Use energy from branches if True. Defaults to False.
        save_new_branches_only (bool, optional): If True, only the new branches are saved in the output file.
                                                 Defaults to False.
        momentum_units (str, optional): Units of momentum in the input file. Defaults to "MeV".
    """
    # Default mass hypotheses (in GeV/c^2)
    mass_dict = {'PION': 0.13957039, 'KAON': 0.493677, 'PROTON': 0.9382720813, 'MUON': 0.1056583745, 'ELECTRON': 0.0005109989461}
    if momentum_units.upper() == "MEV":
        mass_dict = {k: v * 1e3 for k, v in mass_dict.items()}
    elif momentum_units.upper() != "GEV":
        raise ValueError(f"{colorama.Fore.RED}ERROR::reconstruct_invariant_mass: Invalid momentum_units '{momentum_units}'. Valid options are 'MeV' and 'GeV'{colorama.Style.RESET_ALL}")

    if mass_hypotheses is None:
        mass_hypotheses = ['PION', 'KAON', 'PROTON', 'MUON', 'ELECTRON']
    else:
        mass_hypotheses = [mass_hypotheses] if isinstance(mass_hypotheses, str) else mass_hypotheses
        mass_hypotheses = [mass.upper() for mass in mass_hypotheses]

    # Check if provided mass hypotheses are valid
    for mass_name in mass_hypotheses:
        if mass_name not in mass_dict:
            raise ValueError(f"{colorama.Fore.RED}ERROR::reconstruct_invariant_mass: Invalid mass hypothesis '{mass_name}'. Valid options are: {list(mass_dict.keys())}{colorama.Style.RESET_ALL}")

    # Open the input ROOT file and get the TTree
    input_file = TFile.Open(input_file_name, "READ")
    if not input_file or input_file.IsZombie():
        raise FileNotFoundError(f"{colorama.Fore.RED}ERROR::reconstruct_invariant_mass: Cannot open input file '{input_file_name}'{colorama.Style.RESET_ALL}")
    input_tree = input_file.Get(input_tree_name)
    if not input_tree:
        raise ValueError(f"{colorama.Fore.RED}ERROR::reconstruct_invariant_mass:Cannot find tree '{input_tree_name}' in file '{input_file_name}'{colorama.Style.RESET_ALL}")

    # Create RDataFrame
    rdf = RDataFrame(input_tree)

    # Generate combinations of particles
    particle_indices = list(range(len(track_names)))
    if maximum_combinations == -1 or maximum_combinations > len(track_names):
        max_comb = len(track_names)
    else:
        max_comb = maximum_combinations

    # List to keep track of all branches to be created
    branch_names = []

    # Loop over combination sizes (from 2 up to max_comb)
    for r in range(2, max_comb + 1):
        # Generate all combinations of particles of size r
        particle_combinations = list(itertools.combinations(particle_indices, r))

        for particle_combo in particle_combinations:
            # Get the prefixes for the current combination
            combo_prefixes = [track_names[i] for i in particle_combo]

            # Generate all possible mass hypothesis assignments for this particle combination
            mass_hypotheses_per_particle = [mass_hypotheses] * len(combo_prefixes)
            mass_assignment_combinations = list(itertools.product(*mass_hypotheses_per_particle))

            for mass_combo in mass_assignment_combinations:
                # Create a unique branch name
                combo_name_parts = [f"{prefix}_{mass}" for prefix, mass in zip(combo_prefixes, mass_combo)]
                branch_name = f"invMass_{'_'.join(combo_name_parts)}"
                branch_names.append(branch_name)

                # Create C++ code to compute the invariant mass. Temporary variables are created for each particle in the combination.
                code_lines = []
                for i, (prefix, mass_name) in enumerate(zip(combo_prefixes, mass_combo)):
                    mass_value = mass_dict[mass_name]
                    # Prepare variable names
                    px_name = f"{prefix}_PX"
                    py_name = f"{prefix}_PY"
                    pz_name = f"{prefix}_PZ"
                    energy_expr = ""
                    if use_energy_instead_of_momentum:
                        energy_name = f"{prefix}_PE"
                        energy_expr = f"auto E_{i} = {energy_name};"
                    else:
                        energy_expr = f"""
                        auto P_{i} = sqrt({px_name}*{px_name} + {py_name}*{py_name} + {pz_name}*{pz_name});
                        auto E_{i} = sqrt(P_{i}*P_{i} + {mass_value}*{mass_value});
                        """
                    code_lines.append(
                        f"""
                        // Particle {i}: {prefix} with mass hypothesis '{mass_name}'
                        {energy_expr}
                        ROOT::Math::PxPyPzEVector vec_{i}({px_name}, {py_name}, {pz_name}, E_{i});
                    """
                    )
                # Sum the vectors and compute the invariant mass
                sum_vec = " + ".join([f"vec_{i}" for i in range(len(combo_prefixes))])
                code = "\n".join(code_lines)
                code += f"""
                    auto total_vec = {sum_vec};
                    return total_vec.M();
                """
                # Print the code if verbose
                print('- ' * 50, code) if verbose else None
                # Define a new column with the invariant mass
                rdf = rdf.Define(branch_name, code)

    # Select the branches to save
    if save_new_branches_only:
        branches_to_save = branch_names
    else:
        branches_to_save = list(rdf.GetColumnNames())

    # Write the new branches to the output file
    output_file_name = Path(output_file_name).resolve().as_posix()
    Path(output_file_name).parent.mkdir(parents=True, exist_ok=True)
    rdf.Snapshot(output_tree_name, output_file_name, branches_to_save)
    print(f"INFO::reconstruct_invariant_mass: Processing completed. Output saved to '{output_file_name}'")


if __name__ == '__main__':
    # Enable multi-threading
    r.ROOT.EnableImplicitMT()

    # Batch mode
    gROOT.SetBatch(True)

    # Test the function
    input_file_name = "/home/uzh/wjie/repository/RLcMuonic2016/output/v1r0/FitTemplates/20240918/fullSim/DATA__sw_sigLc_1__MC__Event_PIDCalibEffWeight__w_LbCorr_new_RpK__Event_TrackCalibcorr2__Event_FFcorr/baseline/Kenriched/Lb_Lc2625taunu.root"
    input_tree_name = "DecayTree"

    track_names = ["p", "K", "pi", "mu"]
    mass_hypotheses = ["MUON", "PION"]

    reconstruct_invariant_mass(
        input_file_name=input_file_name,
        input_tree_name=input_tree_name,
        track_names=track_names,
        mass_hypotheses=mass_hypotheses,
        maximum_combinations=-1,
        output_file_name="tmp/output.root",
        output_tree_name=input_tree_name,
        use_energy_instead_of_momentum=False,
        save_new_branches_only=True,
        verbose=True,
    )
