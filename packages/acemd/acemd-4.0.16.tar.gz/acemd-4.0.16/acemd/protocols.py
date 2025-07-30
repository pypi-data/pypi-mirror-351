from pathlib import Path
from typing import Union
from moleculekit.molecule import Molecule
import numpy as np
import shutil
import yaml
import os
import logging

logger = logging.getLogger("acemd")

# Taken from lipid21.lib in AMBER
LIPIDSEL = (
    "(lipid or resname AR CHL DHA LAL MY OL PA PC PE PGR PGS PS SA SPM ST) and noh"
)


def _detect_cis_peptide_bonds(mol: Molecule):
    import networkx as nx

    protsel = mol.atomselect("protein and backbone and name C CA N", guessBonds=False)
    if np.sum(protsel) < 4:  # Less atoms than dihedral
        return

    original_idx = np.where(protsel)[0]
    molc = mol.copy(sel=protsel)
    molg = molc.toGraph(fields=("name", "resid"), distances=False)

    for i in range(molc.numAtoms - 3):
        idx = list(range(i, i + 4))
        if np.all(molc.name[idx] == np.array(["CA", "C", "N", "CA"])):
            if nx.is_connected(molg.subgraph(idx)):
                dih = np.rad2deg(molc.getDihedral(idx))
                if np.abs(dih) < 120:
                    descr = ""
                    _idx = original_idx[idx]
                    for j in _idx:
                        descr += f"({mol.resname[j]} {mol.resid[j]} {mol.name[j]} {mol.chain[j]} {mol.segid[j]}) "
                    logger.warning(
                        f"Found cis peptide bond with dihedral angle {dih:.2f} deg in the omega diheral {descr}with indexes {_idx}"
                    )


def _search_and_copy(search_paths, outdir, single=True, error_on_not_found=True):
    from glob import glob

    outfiles = []
    for ff in search_paths:
        matches = glob(ff)
        if single and len(matches) > 1:
            raise RuntimeError(
                f"Multiple files found matching {ff}. Please specify a single file."
            )

        for mm in matches:
            basename = os.path.basename(mm)
            if "output." in basename:
                basename = basename.replace("output.", "input.")
            outfile = os.path.join(outdir, basename)

            logger.info(f"Copying {mm} to {outfile}")
            shutil.copy(mm, outfile)
            if single:
                return outfile
            outfiles.append(outfile)

    if len(outfiles) == 0:
        if error_on_not_found:
            raise FileNotFoundError(f"No file found at paths {search_paths}")
        else:
            return None
    return outfiles


def get_cellular_restraints(
    mol: Molecule,
    extracellular_sel: str,
    intracellular_sel: str,
    membrane_rel_z: float,
    lipidsel: str = "(lipid or resname AR CHL DHA LAL MY OL PA PC PE PGR PGS PS SA SPM ST) and noh",
    extracellular_crossing: Union[str, None] = "cross",
    intracellular_crossing: Union[str, None] = "cross",
):
    """Utility function for getting restraints for membrane-ligand simulations.

    Get restraints to keep given molecules from changing from extracellular to intracellular
    or vice versa through the periodic images of the simulation.

    This assumes that the membrane is in the xy plane and the positive z axis is pointing
    from the intracellular side to the extracellular side. It utilizes a flat-bottomed
    potential which is only applied on the molecules when they exit from the box defined
    by this function.

    Additionally the function allows the user to specify if the molecules should be allowed
    to enter the membrane or cross it (useful for example in ion channel simulations).

    Note: Only use these restraints in NVT simulations as they require the box size to remain
    constant. When equilibrating such a system using NPT please restrain your molecules
    with positional restraints to their original locations.

    Parameters
    ----------
    mol : Molecule
        The simulation system
    extracellular_sel : str
        Atom selection for the molecules which should be kept on the extracellular side
    intracellular_sel : str
        Atom selection for the molecules which should be kept on the intracellular side
    membrane_rel_z : float
        The relative position of the membrane in the z direction. 0.5 means the membrane is in the middle of the box
        meaning half the solvent is above the membrane and half below.
    lipidsel : str, optional
        The selection of lipids to use for the membrane
    extracellular_crossing : str, optional
        Whether to allow the extracellular molecules to cross the membrane. If set to "cross" it will allow crossing.
        If set to "enter" it will allow entering the membrane but not crossing it. If set to None it will not allow entering the membrane.
    intracellular_crossing : str, optional
        Whether to allow the intracellular molecules to cross the membrane. If set to "cross" it will allow crossing.
        If set to "enter" it will allow entering the membrane but not crossing it. If set to None it will not allow entering the membrane.
    """
    if np.all(mol.box == 0):
        raise ValueError("Box size is 0. Please set the correct box size in the mol.")
    boxz = mol.box[2, -1]  # Box of the last frame

    lipidsel_mask = mol.atomselect(lipidsel, guessBonds=False)
    if lipidsel_mask.sum() == 0:
        raise ValueError(
            "No lipids found in the system. Please set the correct lipidsel selection."
        )

    cross_opt = ["enter", "cross"]
    if extracellular_crossing is not None and extracellular_crossing not in cross_opt:
        raise ValueError(
            "Invalid extracellular_crossing value. Please set to 'cross', 'enter' or None."
        )
    if intracellular_crossing is not None and intracellular_crossing not in cross_opt:
        raise ValueError(
            "Invalid intracellular_crossing value. Please set to 'cross', 'enter' or None."
        )

    memb_z = mol.coords[lipidsel_mask, 2, -1]  # Last frame
    wrap_center = memb_z[0]  # First lipid
    # wrap the lipids to origin so the max/min is periodic
    memb_z = memb_z - boxz * np.round((memb_z - wrap_center) / boxz)

    memb_width = float(memb_z.max() - memb_z.min())
    memb_meanz = float(boxz * membrane_rel_z)
    memb_minz = memb_meanz - memb_width / 2
    memb_maxz = memb_meanz + memb_width / 2

    restr = []
    if extracellular_sel is not None:
        if extracellular_crossing is None:
            top_fb_width = boxz - memb_maxz
            top_offset = float(top_fb_width / 2 + (memb_maxz - memb_meanz))
        elif extracellular_crossing == "enter":
            top_fb_width = boxz - memb_minz
            top_offset = float(top_fb_width / 2 - (memb_meanz - memb_minz))
        elif extracellular_crossing == "cross":
            top_fb_width = boxz
            top_offset = float(boxz / 2 - memb_meanz)

        restr.append(
            {
                "type": "positionalrestraint",
                "sel": extracellular_sel,
                "axes": "z",
                "fbwidth": float(top_fb_width),
                "fbcenter": lipidsel,
                "fbcenteroffset": [0, 0, top_offset],
                "setpoints": ["1@0"],
            }
        )

    if intracellular_sel is not None:
        if intracellular_crossing is None:
            bottom_fb_width = memb_minz
            bottom_offset = -float(bottom_fb_width / 2 + (memb_meanz - memb_minz))
        elif intracellular_crossing == "enter":
            bottom_fb_width = memb_maxz
            bottom_offset = -float(bottom_fb_width / 2 - (memb_maxz - memb_meanz))
        elif intracellular_crossing == "cross":
            bottom_fb_width = boxz
            bottom_offset = float(boxz / 2 - memb_meanz)

        restr.append(
            {
                "type": "positionalrestraint",
                "sel": intracellular_sel,
                "axes": "z",
                "fbwidth": float(bottom_fb_width),
                "fbcenter": lipidsel,
                "fbcenteroffset": [0, 0, bottom_offset],
                "setpoints": ["1@0"],
            }
        )

    return restr


def setup_equilibration(
    builddir: Path,
    outdir: Path,
    run: Union[str, int],
    temperature: float = 300,
    minimize: int = 500,
    extforces: list[dict] = None,
    coordinates: Union[Path, None] = None,
    structure: Union[Path, None] = None,
    parameters: Union[Path, None] = None,
    barostatconstratio: bool = False,
    defaultrestraints: bool = True,
    restraintdecay: Union[str, int, None] = None,
    cispeptidebondcheck: bool = True,
    **kwargs,
):
    """
    Set up an ACEMD equilibration simulation.

    Parameters
    ----------
    builddir : Path
        The directory containing the input files. Usually the output of a builder.
    outdir : Path
        The directory to write the input files and simulation output to.
    run : int or str
        The number of steps to run the simulation for.
    temperature : float, optional
        The temperature to equilibrate the system to.
    minimize : int, optional
        The number of minimization steps to perform before starting the simulation.
    extforces : list[dict], optional
        External forces to apply to the system
    coordinates : Path, optional
        The coordinates file to use for the simulation. If None it will be auto-detected.
    structure : Path, optional
        The structure file to use for the simulation. If None it will be auto-detected.
    parameters : Path, optional
        The parameters file to use for the simulation. If None it will be auto-detected.
    barostatconstratio : bool, optional
        Whether to use the barostatconstratio option. This is required for membrane
        simulations where the box should scale isotropically in the xy plane.
    defaultrestraints : bool, optional
        Whether to use the default restraints. This will apply positional restraints to
        all protein CA atoms with 1 kcal/mol/A^2, all non-hydrogen protein atoms with
        0.1 kcal/mol/A^2, all nucleic acid backbone atoms with 1 kcal/mol/A^2 and all
        nucleic acid atoms that are not part of the backbone with 0.1 kcal/mol/A^2.
    restraintdecay : int or str, optional
        The restraint decay time. If set to a timestep or time, the restraints will scale to their initial value
        to 0 over the given restraintdecay time. Otherwise the restraints will scale to 0 over half the simulation time.
    cispeptidebondcheck : bool, optional
        Whether to check for cis peptide bonds in the system. This will print a warning
        if any are found.

    Notes
    -----
    The function accepts additional keyword arguments to pass to the ACEMD input file. Please refer to the ACEMD documentation.
    All input file options can be used here.

    Examples
    --------
    >>> from acemd.protocols import setup_equilibration
    >>> setup_equilibration(builddir, outdir, run="10ns")
    >>> setup_equilibration(builddir, outdir, run="10ns", minimize=1000)
    In the second example we override the default minimization steps of the protocol.
    You can override any of the input file options of ACEMD.
    >>> setup_equilibration(builddir, outdir, run="10ns", extforces=[{"type": "positionalRestraint", "sel": "resname MOL", "setpoints": ["1@0"]}])
    In this example we add a positional restraint to the molecule MOL during equilibration in addition to the default restraints.
    """
    from acemd.acemd import _parse_runtime, DEFAULTS, load_molecule

    os.makedirs(outdir, exist_ok=True)

    for key in kwargs:
        if key.lower() not in DEFAULTS:
            raise ValueError(
                f"Invalid keyword argument: {key}. Valid arguments are {DEFAULTS.keys()}"
            )

    # Tries to find default files if the given don't exist
    search_paths = {
        "coordinates": ("structure.pdb", "*.pdb"),
        "structure": ("structure.prmtop", "structure.psf", "*.prmtop", "*.psf"),
        "parameters": ("parameters", "*.prm"),
    }
    for key in search_paths:
        search_paths[key] = [os.path.join(builddir, ff) for ff in search_paths[key]]

    if coordinates is not None:
        search_paths["coordinates"] = [coordinates]
    if structure is not None:
        search_paths["structure"] = [structure]
    if parameters is not None:
        search_paths["parameters"] = [parameters]
    if extforces is not None:
        if isinstance(extforces, dict):
            extforces = [extforces]

    coordinates = _search_and_copy(search_paths["coordinates"], outdir)
    structure = _search_and_copy(search_paths["structure"], outdir)
    parameters = _search_and_copy(
        search_paths["parameters"], outdir, single=False, error_on_not_found=False
    )

    input_dict = {
        "structure": os.path.basename(structure),
        "coordinates": os.path.basename(coordinates),
        "thermostat": True,
        "thermostattemperature": temperature,
        "velocities": temperature,
        "barostat": True,
        "barostatconstratio": barostatconstratio,
        "extforces": extforces if extforces is not None else [],
        "minimize": minimize,
        "restart": True,
        "run": run,
        **kwargs,
    }
    if parameters is not None:
        input_dict["parameters"] = [os.path.basename(p) for p in parameters]

    mol = load_molecule(structure)
    mol = load_molecule(coordinates, mol=mol)

    if cispeptidebondcheck:
        _detect_cis_peptide_bonds(mol)

    if mol.atomselect(LIPIDSEL, guessBonds=False).sum() > 0 and not barostatconstratio:
        logger.warning(
            "Lipids detected but barostatconstratio is not set. If you are simulating a "
            "membrane system please set barostatconstratio to True."
        )

    if input_dict.get("boxsize") is None:
        coords = mol.get("coords", sel="water", guessBonds=False)
        if coords.size == 0:  # It's a vacuum simulation
            coords = mol.get("coords", sel="all")
            dim = np.ptp(coords, axis=0) + 12
        else:
            # Add 1 angstrom to avoid water clashes over periodic images
            dim = np.ptp(coords, axis=0) + 1
        input_dict["boxsize"] = dim.tolist()

    if defaultrestraints:
        timestep = input_dict.get("timestep", DEFAULTS["timestep"])
        if restraintdecay is None:
            restraintdecay = _parse_runtime(run, timestep) / 2
        else:
            restraintdecay = _parse_runtime(restraintdecay, timestep)

        default_restr = (
            ("protein and name CA", 1),
            ("protein and noh and not name CA", 0.1),
            ("nucleic and backbone", 1),
            ("nucleic and not backbone and noh", 0.1),
        )
        for sel, kk in default_restr:
            if mol.atomselect(sel, guessBonds=False).sum() > 0:
                input_dict["extforces"].append(
                    {
                        "type": "positionalRestraint",
                        "sel": sel,
                        "setpoints": [f"{kk}@0", f"0@{int(restraintdecay)}"],
                    }
                )

    with open(os.path.join(outdir, "input.yaml"), "w") as fd:
        yaml.dump(input_dict, fd)

    current_env = os.getenv("CONDA_DEFAULT_ENV")
    with open(os.path.join(outdir, "run.sh"), "w") as fd:
        fd.write(
            f'#!/bin/bash\neval "$(conda shell.bash hook)"\nconda activate {current_env}\nacemd >log.txt 2>&1'
        )
    os.chmod(os.path.join(outdir, "run.sh"), 0o700)


def setup_production(
    equildir: Path,
    outdir: Path,
    run: Union[str, int],
    temperature: float = 300,
    extforces: list[dict] = None,
    coordinates: Union[Path, None] = None,
    structure: Union[Path, None] = None,
    parameters: Union[Path, None] = None,
    cispeptidebondcheck: bool = True,
    **kwargs,
):
    """
    Set up an ACEMD production simulation.

    Parameters
    ----------
    equildir : Path
        The directory containing the equilibrated system
    outdir : Path
        The directory to write the input files and simulation output to
    run : int or str
        The number of steps to run the simulation for
    temperature : float, optional
        The temperature to run the simulation at
    extforces : list[dict], optional
        External forces to apply to the system
    coordinates : Path, optional
        The coordinates file to use for the simulation. If None it will be auto-detected.
    structure : Path, optional
        The structure file to use for the simulation. If None it will be auto-detected.
    parameters : Path, optional
        The parameters file to use for the simulation. If None it will be auto-detected.
    cispeptidebondcheck : bool, optional
        Whether to check for cis peptide bonds in the system. This will print a warning
        if any are found.

    Notes
    -----
    The function accepts additional keyword arguments to pass to the ACEMD input file. Please refer to the ACEMD documentation.
    All input file options can be used here.

    Examples
    --------
    >>> from acemd.protocols import setup_production
    >>> setup_production(equildir, outdir, run="10ns")
    This will autodetect the final coordinates and box size from the equilibrated system
    and copy them over to set up a production simulation of 10 ns.
    """
    from acemd.acemd import DEFAULTS, load_molecule

    os.makedirs(outdir, exist_ok=True)

    for key in kwargs:
        if key.lower() not in DEFAULTS:
            raise ValueError(
                f"Invalid keyword argument: {key}. Valid arguments are {DEFAULTS.keys()}"
            )

    # Tries to find default files if the given don't exist
    search_paths = {
        "coordinates": ("output.coor", "*.pdb", "*.coor"),
        "boxsize": ("output.xsc",),
        "structure": ("structure.prmtop", "structure.psf", "*.prmtop", "*.psf"),
        "parameters": ("parameters", "*.prm"),
    }
    for key in search_paths:
        search_paths[key] = [os.path.join(equildir, ff) for ff in search_paths[key]]

    if coordinates is not None:
        search_paths["coordinates"] = [coordinates]
    if structure is not None:
        search_paths["structure"] = [structure]
    if parameters is not None:
        search_paths["parameters"] = [parameters]

    coordinates = _search_and_copy(search_paths["coordinates"], outdir)
    boxsize = _search_and_copy(search_paths["boxsize"], outdir)
    structure = _search_and_copy(search_paths["structure"], outdir)
    parameters = _search_and_copy(
        search_paths["parameters"], outdir, single=False, error_on_not_found=False
    )

    input_dict = {
        "structure": os.path.basename(structure),
        "coordinates": os.path.basename(coordinates),
        "boxsize": os.path.basename(boxsize),
        "thermostat": True,
        "thermostattemperature": temperature,
        "velocities": temperature,
        "barostat": False,
        "restart": True,
        "run": run,
        **kwargs,
    }
    if parameters is not None:
        input_dict["parameters"] = [os.path.basename(p) for p in parameters]
    if extforces is not None:
        if isinstance(extforces, dict):
            extforces = [extforces]
        input_dict["extforces"] = extforces

    if cispeptidebondcheck:
        mol = load_molecule(structure)
        mol = load_molecule(coordinates, mol=mol)
        _detect_cis_peptide_bonds(mol)

    with open(os.path.join(outdir, "input.yaml"), "w") as fd:
        yaml.dump(input_dict, fd)

    current_env = os.getenv("CONDA_DEFAULT_ENV")
    with open(os.path.join(outdir, "run.sh"), "w") as fd:
        fd.write(
            f'#!/bin/bash\neval "$(conda shell.bash hook)"\nconda activate {current_env}\nacemd >log.txt 2>&1'
        )
    os.chmod(os.path.join(outdir, "run.sh"), 0o700)
