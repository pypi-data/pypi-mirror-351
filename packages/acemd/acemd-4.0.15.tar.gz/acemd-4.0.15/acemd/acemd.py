# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import openmm as mm
import openmm.app as app
import openmm.unit as unit
from pathlib import Path
from moleculekit.molecule import Molecule
from acemd.reporters import setup_reporters
from acemd.charmm import cleanup_charmm_prm
from typing import Optional, Union
from enum import Enum
import os
import logging

logger = logging.getLogger("acemd")


class FGROUPS(Enum):
    BONDS = 0
    ANGLES = 1
    DIHEDRALS = 2
    UREYBRADLEY = 3
    IMPROPER = 4
    CMAP = 5
    NONBONDED = 11  # For default MM forces we use up to fgroup 13
    BAROSTAT = 14  # The following are our own fgroups
    PLUMED = 15
    IMPLICIT = 16
    NNP = 17
    DEBUG = 18
    EXTERNAL = 19  # Must be the last fgroup since we use following numbers for each restraint individually


def _disable_dispersion_correction(system: mm.System):
    # According to openMM:
    # The long range dispersion correction is primarily useful when running simulations at constant pressure, since it
    # produces a more accurate variation in system energy with respect to volume.
    from openmm import NonbondedForce, CustomNonbondedForce

    for f in system.getForces():
        if isinstance(f, NonbondedForce):
            f.setUseDispersionCorrection(False)
        if isinstance(f, CustomNonbondedForce):
            f.setUseLongRangeCorrection(False)


def setup_barostat(
    thermostat,
    barostatanisotropic,
    barostatconstratio,
    barostatconstxy,
    barostatpressure,
    thermostattemperature,
    system,
):
    if not thermostat:
        raise RuntimeError("Barostat requires thermostat")
    if sum(map(int, [barostatanisotropic, barostatconstxy, barostatconstratio])) > 1:
        raise RuntimeError("Only one barostat option can be used")
    tension = 0
    if barostatanisotropic:
        omm_barostat = mm.MonteCarloAnisotropicBarostat(
            [barostatpressure * unit.bar] * 3,
            thermostattemperature,
            True,  # scaleX
            True,  # scaleY
            True,  # scaleZ
        )
    elif barostatconstratio:
        omm_barostat = mm.MonteCarloMembraneBarostat(
            barostatpressure * unit.bar,
            tension,  # defaultSurfaceTension
            thermostattemperature,  # defaultTemperature
            mm.MonteCarloMembraneBarostat.XYIsotropic,  # xymode
            mm.MonteCarloMembraneBarostat.ZFree,  # zmode
        )
    elif barostatconstxy:
        omm_barostat = mm.MonteCarloAnisotropicBarostat(
            [barostatpressure * unit.bar] * 3,
            thermostattemperature,
            False,  # scaleX
            False,  # scaleY
            True,  # scaleZ
        )
    else:
        omm_barostat = mm.MonteCarloBarostat(
            barostatpressure * unit.bar, thermostattemperature
        )
    omm_barostat.setForceGroup(FGROUPS.BAROSTAT.value)
    system.addForce(omm_barostat)


DEFAULTS = {
    "structure": None,
    "pme": True,
    "cutoff": 9.0,
    "switching": True,
    "switchdistance": 7.5,
    "implicitsolvent": False,
    "igb": 2,
    "extforces": None,
    "fbrefcoor": None,
    "plumedfile": None,
    "coordinates": None,
    "boxsize": None,
    "velocities": 298.15,
    "timestep": 4.0,
    "slowperiod": 1,
    "thermostat": False,
    "thermostattemperature": 298.15,
    "thermostatdamping": 1,  # 1/ps is the recommended value from OMM
    "barostat": False,
    "barostatpressure": 1.0,
    "barostatanisotropic": False,
    "barostatconstratio": False,
    "barostatconstxy": False,
    "trajectoryfile": "output.xtc",
    "trajvelocityfile": None,
    "trajforcefile": None,
    "trajectoryperiod": 25000,
    "restart": False,
    "parameters": None,
    "run": 0,
    "minimize": 0,
    "stepzero": False,
    "nnp": None,
    "hydrogenmass": 4.032,
    "hmr": None,
    "hbondconstr": None,
    "rigidwater": None,
}
DEPRECATIONS = {  # The order is important. If multiple keys point to the same value the last non-null one wins
    "bincoordinates": "coordinates",
    "temperature": "velocities",  # Temperature is overridden by velocities and velocities by binvelocities
    "velocities": "velocities",  # Not a real deprectation. Just to specify the order priority
    "binvelocities": "velocities",
    "parmfile": "structure",
    "celldimension": "boxsize",
    "extendedsystem": "boxsize",
    "thermostattemp": "thermostattemperature",
    "switchdist": "switchdistance",
    "trajectoryfreq": "trajectoryperiod",
    "implicit": "implicitsolvent",
    "atomrestraint": "extforces",
    "grouprestraint": "extforces",
}
DEPRECATIONS_MSG = {
    "temperature": "The `temperature` option is deprecated in favor of the `velocities` option which can accept a temperature value to generate initial velocities from a Maxwell-Boltzmann distribution",
    "extendedsystem": "The `extendedsystem` option is deprecated in favor of the `boxsize` option which can accept a list of 3 numbers or a filename of a NAMD XSC file",
}

PDBVELFACTOR = 20.45482706  # Ang/internal --> A/fs
ANGSTROM_PER_NM = 10
VEL_CONVERSION_FACTOR = ANGSTROM_PER_NM / PDBVELFACTOR


def _handle_deprecations(_input_args, error=False):
    to_delete = []
    _input_args = {key.lower(): val for key, val in _input_args.items()}
    input_args = _input_args.copy()
    for key in DEPRECATIONS:
        if key in _input_args and _input_args[key] is not None:
            val = _input_args[key]
            newkey = DEPRECATIONS[key].lower()

            if key in DEPRECATIONS_MSG:
                warn = f"# Deprecation: {DEPRECATIONS_MSG[key]}"
            else:
                warn = f"# Deprecation: `{key}` is deprecated in favor of `{newkey}`"

            if key == "parmfile" and _input_args.get("structure", None) is not None:
                if error:
                    raise ValueError(warn + ". Ignoring the parmfile option")
                else:
                    logger.warning(warn + ". Ignoring the parmfile option")
                to_delete.append(key)
                continue  # Ignore the parmfile option

            if _input_args.get(newkey, None) is not None and _input_args[newkey] != val:
                warn += (
                    f". Replacing {newkey} value '{_input_args[newkey]}' with '{val}'"
                )

            if key == newkey:  # No deprecation, just making sure ordering is maintained
                input_args[newkey] = val
                continue

            if error:
                raise ValueError(warn)
            else:
                logger.warning(warn)

            to_delete.append(key)

            if key in ("atomrestraint", "grouprestraint"):
                if newkey not in input_args or input_args[newkey] is None:
                    input_args[newkey] = []
                if isinstance(val, str):
                    input_args[newkey].append(val)
                elif isinstance(val, list):
                    input_args[newkey].extend(val)
                else:
                    raise ValueError(f"Invalid restraint type: {type(val)}")
            else:
                input_args[newkey] = val

    for key in to_delete:
        del input_args[key]
    return input_args


def _parse_runtime(runtime, timestep):
    if isinstance(runtime, int):
        return runtime
    if runtime is None:
        return 0
    if isinstance(runtime, str):
        if runtime.endswith("fs"):
            runtime = float(runtime.replace("fs", ""))
        elif runtime.endswith("ps"):
            runtime = float(runtime.replace("ps", "")) * 1e3
        elif runtime.endswith("ns"):
            runtime = float(runtime.replace("ns", "")) * 1e6
        elif runtime.endswith("us"):
            runtime = float(runtime.replace("us", "")) * 1e9
        else:
            raise ValueError(
                f"Invalid runtime format: {runtime}. Must be in fs, ps, ns or us"
            )
    return int(float(runtime) / timestep)


def detect_input_file(directory: Path, input_file: Optional[Path]):
    if input_file is None:
        fnames = ["input.yaml", "input.yml", "input.json", "input"]
        for fname in fnames:
            if os.path.isfile(os.path.join(directory, fname)):
                return os.path.join(directory, fname)
        raise FileNotFoundError(
            f"No input file found in directory: {directory} (valid names: `{'`, `'.join(fnames)}`). Please specify an input file."
        )
    elif os.path.isfile(os.path.join(directory, input_file)):
        return os.path.join(directory, input_file)
    elif os.path.isfile(input_file):
        return input_file
    else:
        raise FileNotFoundError(f"Input file {input_file} not found")


def parse_input_file(input_file: Optional[Path], directory: Path):
    from acemd.restraints import PositionalRestraint
    import yaml
    import json
    import re

    new_format = os.path.splitext(input_file)[-1] in (".yaml", ".yml", ".json")
    if not new_format:
        logger.warning(
            "# Parsing input file with old input file parser. We recommend using the new YAML or JSON inputs instead."
        )
        _input_args = {}
        with open(input_file, "r") as f:
            for line in f:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"):
                    continue
                pieces = line.split()
                key = pieces[0].lower()

                # Remove the key from the line to get the rest
                pattern = re.compile(f"^{key}", re.IGNORECASE)
                val = pattern.sub("", line).strip()

                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass

                if key.lower() in ("atomrestraint", "grouprestraint"):
                    val = key.lower() + " " + val
                    if key not in _input_args or _input_args[key] is None:
                        _input_args[key] = []
                    _input_args[key].append(val)
                else:
                    _input_args[key] = val
    elif input_file.endswith(".yaml") or input_file.endswith(".yml"):
        with open(input_file, "r") as f:
            _input_args = yaml.load(f, Loader=yaml.FullLoader)
            _input_args = {k.lower(): v for k, v in _input_args.items()}
    elif input_file.endswith(".json"):
        with open(input_file, "r") as f:
            _input_args = json.load(f)
            _input_args = {k.lower(): v for k, v in _input_args.items()}

    # Handle the deprecations
    input_args = _handle_deprecations(_input_args, error=new_format)

    if (
        input_args.get("boxsize", None) is not None
        and isinstance(input_args["boxsize"], str)
        and not input_args["boxsize"].endswith(".xsc")
    ):
        input_args["boxsize"] = [float(x) for x in input_args["boxsize"].split()]

    # Convert string restraints to dict
    if input_args.get("extforces", None) is not None:
        new_extfrc = []
        for rr in input_args["extforces"]:
            if new_format and isinstance(rr, str):
                raise RuntimeError(
                    f"# Deprecation: restraint '{rr}' is using the old format. Please convert it to the new yaml format."
                )
            if new_format and rr["type"].lower() != "positionalrestraint":
                raise ValueError(
                    f"# Error: Currently only positional restraints are supported with type: positionalRestraint. You used type {rr['type']}"
                )
            new_extfrc.append(PositionalRestraint.parse_restraint(rr))
        input_args["extforces"] = new_extfrc

    # Defaults
    for key, val in input_args.items():
        if isinstance(val, str) and val.lower() in ["on", "off"]:
            val = {"on": True, "off": False}[val.lower()]
        if isinstance(val, str) and val.lower() in ["true", "false"]:
            val = {"true": True, "false": False}[val.lower()]
        input_args[key] = val

    # Create input.yaml.new to ease user transition from old to new format
    if not new_format:
        logger.info(
            "# Writing input file in the new YAML format to input.yaml.new. Feel free to use it in future runs by renaming it to input.yaml"
        )
        # Convert the extforces to dict
        input_args_c = input_args.copy()
        if "extforces" in input_args_c:
            input_args_c["extforces"] = [
                rr.to_dict() for rr in input_args_c["extforces"]
            ]
        with open(os.path.join(directory, "input.yaml.new"), "w") as f:
            yaml.dump(input_args_c, f)

    args = DEFAULTS.copy()
    args.update(input_args)
    args["run"] = _parse_runtime(args["run"], args["timestep"])
    return args


def _print_input_args(args):
    logger.info("#")
    logger.info("# Input arguments")
    for key, value in sorted(args.items()):
        if key == "igb" and not args["implicitsolvent"]:
            continue
        if key == "switchdistance" and not args["switching"]:
            continue
        if (
            key in ("thermostattemperature", "thermostatdamping")
            and not args["thermostat"]
        ):
            continue
        if (
            key
            in (
                "barostatpressure",
                "barostatanisotropic",
                "barostatconstratio",
                "barostatconstxy",
            )
            and not args["barostat"]
        ):
            continue
        logger.info(f"#   {key}: {value}")


def get_acemd_system(
    directory: Path,
    inputfile=None,
    include_extforces=False,
    set_velocities=False,
    **kwargs,
):
    inputfile = detect_input_file(directory, inputfile)
    input_args = parse_input_file(inputfile, directory)
    return setup_acemd(
        **input_args,
        directory=directory,
        include_extforces=include_extforces,
        set_velocities=set_velocities,
        **kwargs,
    )


def _acemd_cli():
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=".", help="The input file/directory"
    )
    parser.add_argument(
        "--platform",
        type=str,
        default="CUDA",
        help="The platform to use for the simulation",
    )
    parser.add_argument(
        "--device",
        type=int,
        nargs="*",
        help="The device indices to use for the simulation",
    )
    parser.add_argument(
        "--ngpus", type=int, help="The number of GPUs to use for the simulation"
    )
    parser.add_argument(
        "--ncpus", type=int, help="The number of CPU threads to use for the simulation"
    )
    parser.add_argument(
        "--precision",
        type=str,
        default="mixed",
        help="The precision to use for the simulation",
    )
    parser.add_argument(
        "--version", action="store_true", help="Print the version and exit"
    )
    parser.add_argument(
        "--license", action="store_true", help="Print the license and exit"
    )
    # These do nothing but are here for backwards compatibility
    parser.add_argument(  # hidden argument
        "--boinc", action="store_true", help=argparse.SUPPRESS
    )
    parser.add_argument(  # hidden argument
        "--playmolecule", action="store_true", help=argparse.SUPPRESS
    )
    args = parser.parse_args()

    if args.version:
        from acemd import __version__

        print(f"ACEMD {__version__}")
        sys.exit(0)
    if args.license:
        from acemd.licensing import _check_license

        _check_license(_print=True)
        sys.exit(0)

    if os.path.isfile(args.input):
        directory = os.path.dirname(args.input)
        inputfile = os.path.basename(args.input)
    else:
        directory = args.input
        inputfile = None

    if args.ngpus is not None:
        args.device = list(range(args.ngpus))

    acemd(
        directory,
        inputfile=inputfile,
        platform=args.platform,
        device=args.device,
        precision=args.precision,
        ncpus=args.ncpus,
    )


ACEMD_HEADER = """#
# ACEMD version {version}
#
# Copyright (C) 2017-{year} Acellera (www.acellera.com)
#
# By using ACEMD, you accept the terms and conditions of the ACEMD license
# Check the license by running "acemd --license"
# More details: https://software.acellera.com/acemd/licence.html
#
# When publishing, please cite:
#   ACEMD: Accelerating Biomolecular Dynamics in the Microsecond Time Scale
#   M. J. Harvey, G. Giupponi and G. De Fabritiis,
#   J Chem. Theory. Comput. 2009 5(6), pp1632-1639
#   DOI: 10.1021/ct9000685
#
#   OpenMM 8: Molecular Dynamics Simulation with Machine Learning Potentials
#   P. Eastman, R. Galvelis, R. P. Peláez, C. R. A. Abreu, S. E. Farr, E. Gallicchio,
#   A. Gorenko, M. M. Henry, F. Hu, J. Huang, A. Krämer, J. Michel, J. A. Mitchell,
#   V. S. Pande, J. PGLM Rodrigues, J. Rodriguez-Guerra, A. C. Simmonett, S. Singh,
#   J. Swails, P. Turner, Y. Wang, I. Zhang, J. D. Chodera, G. De Fabritiis, and T. E. Markland
#   J. Phys. Chem. B 2024 128 (1), 109-116
#   DOI: 10.1021/acs.jpcb.3c06662
#"""


def acemd(directory: Path, inputfile=None, dump_simulation_xml=False, **kwargs):
    from acemd.minimizer import minimize
    from acemd import __version__
    import datetime

    header = ACEMD_HEADER.format(version=__version__, year=datetime.date.today().year)
    for hl in header.split("\n"):
        logger.info(hl)

    inputfile = detect_input_file(directory, inputfile)
    input_args = parse_input_file(inputfile, directory)

    # Override input file arguments with function arguments
    for key in kwargs:
        if key.lower() in input_args:
            key = key.lower()
            logger.warning(
                f"# Warning: overriding '{key}' from input file with {kwargs[key]}"
            )
        input_args[key] = kwargs[key]

    _print_input_args(input_args)

    system, simulation, mol, extforces = setup_acemd(
        **input_args, directory=directory, include_extforces=True, set_velocities=False
    )

    if input_args["minimize"] > 0 and simulation.currentStep == 0:
        minimize(
            system,
            simulation.context,
            input_args["minimize"],
            os.path.join(directory, "minimized.coor"),
        )

    run(
        directory,
        simulation,
        nsteps=input_args["run"],
        extforces=extforces,
        period=input_args["trajectoryperiod"],
        velocities=input_args["velocities"],
        stepzero=input_args["stepzero"],
        dump_simulation_xml=dump_simulation_xml,
    )
    return simulation


def _set_velocities(simulation, velocities, directory):
    try:
        velocities = float(velocities)
    except ValueError:
        pass

    logger.info("#")
    logger.info("# Initial velocities")
    if velocities is not None and isinstance(velocities, float):
        logger.info("#   Distribution: Maxwell-Boltzmann")
        logger.info(f"#   Temperature: {velocities:.2f} K")
        simulation.context.setVelocitiesToTemperature(velocities * unit.kelvin)
    elif velocities is not None and velocities.endswith(".vel"):
        logger.info(f"#   File: {velocities}")
        start_vels = Molecule(find_file(velocities, directory), type="coor").coords[
            :, :, 0
        ]
        simulation.context.setVelocities(start_vels / VEL_CONVERSION_FACTOR)
    elif velocities is not None and velocities.endswith(".pdb"):
        logger.info(f"#   File: {velocities}")
        start_vels = Molecule(find_file(velocities, directory)).coords[:, :, 0]
        simulation.context.setVelocities(start_vels * (unit.angstrom / unit.picosecond))


def _set_force_groups(system):
    MAPPING = {
        "HarmonicBondForce": FGROUPS.BONDS,
        "HarmonicAngleForce": FGROUPS.ANGLES,
        "PeriodicTorsionForce": FGROUPS.DIHEDRALS,
        "NonbondedForce": FGROUPS.NONBONDED,
        "CustomNonbondedForce": FGROUPS.NONBONDED,
        "CustomTorsionForce": FGROUPS.IMPROPER,
        "CustomGBForce": FGROUPS.IMPLICIT,
        "CustomExternalForce": FGROUPS.EXTERNAL,
        "CustomCentroidBondForce": FGROUPS.EXTERNAL,
        "CMAPTorsionForce": FGROUPS.CMAP,
        "TorchForce": FGROUPS.NNP,
        "PlumedForce": FGROUPS.PLUMED,
        "CMMotionRemover": FGROUPS.BONDS,  # practically just to assign it to 0 group
    }

    # Renumber force groups to match our force group numbers
    seen_bonded = False
    for force in system.getForces():
        # Handling the Urey-Bradley force group in CHARMM systems which comes second
        if force.getName() == "HarmonicBondForce":
            if not seen_bonded:
                seen_bonded = True
            else:
                force.setForceGroup(FGROUPS.UREYBRADLEY.value)
                continue
        force.setForceGroup(MAPPING[force.getName()].value)


def find_file(filename: Optional[str], directory: Path):
    if filename is None:
        return None
    directory = os.path.abspath(directory)
    if os.path.isfile(os.path.join(directory, filename)):
        return os.path.join(directory, filename)
    elif os.path.isfile(filename):
        return os.path.abspath(filename)
    else:
        raise FileNotFoundError(f"File {filename} not found in directory {directory}")


def load_molecule(filename, mol=None):
    # Ugly hack for PDB files to skip element validation
    if mol is None:
        if filename.lower().endswith(".pdb"):
            return Molecule(filename, validateElements=False)
        else:
            return Molecule(filename)
    else:
        if filename.lower().endswith(".pdb"):
            mol.read(filename, validateElements=False)
        else:
            mol.read(filename)
        return mol


def setup_acemd(
    platform: str = "CUDA",
    device: list[int] = None,
    precision: str = "mixed",
    structure: Path = DEFAULTS["structure"],
    pme: bool = DEFAULTS["pme"],
    cutoff: float = DEFAULTS["cutoff"],
    switching: bool = DEFAULTS["switching"],
    switchdistance: float = DEFAULTS["switchdistance"],
    implicitsolvent: bool = DEFAULTS["implicitsolvent"],
    igb: int = DEFAULTS["igb"],
    extforces: Optional[list[str]] = DEFAULTS["extforces"],
    fbrefcoor: Optional[Path] = DEFAULTS["fbrefcoor"],
    plumedfile: Optional[Path] = DEFAULTS["plumedfile"],
    coordinates: Optional[Path] = DEFAULTS["coordinates"],
    boxsize: Optional[Union[list[float], Path]] = DEFAULTS["boxsize"],
    velocities: Optional[Union[Path, float]] = DEFAULTS["velocities"],
    timestep: float = DEFAULTS["timestep"],
    slowperiod: int = DEFAULTS["slowperiod"],
    thermostat: bool = DEFAULTS["thermostat"],
    thermostattemperature: float = DEFAULTS["thermostattemperature"],
    thermostatdamping: float = DEFAULTS["thermostatdamping"],
    barostat: bool = DEFAULTS["barostat"],
    barostatpressure: float = DEFAULTS["barostatpressure"],
    barostatanisotropic: bool = DEFAULTS["barostatanisotropic"],
    barostatconstratio: bool = DEFAULTS["barostatconstratio"],
    barostatconstxy: bool = DEFAULTS["barostatconstxy"],
    trajectoryfile: str = DEFAULTS["trajectoryfile"],
    trajvelocityfile: str = DEFAULTS["trajvelocityfile"],
    trajforcefile: str = DEFAULTS["trajforcefile"],
    trajectoryperiod: int = DEFAULTS["trajectoryperiod"],
    restart: bool = DEFAULTS["restart"],
    parameters: Optional[Path] = DEFAULTS["parameters"],
    run=DEFAULTS["run"],
    minimize=DEFAULTS["minimize"],
    directory=".",
    include_extforces: bool = False,
    set_velocities: bool = True,
    stepzero: bool = DEFAULTS["stepzero"],
    deterministic: bool = False,
    rfdielectric: float = 78.5,
    ncpus: int = None,
    nnp: Optional[dict] = None,
    hydrogenmass: float = DEFAULTS["hydrogenmass"],
    hmr: Optional[bool] = DEFAULTS["hmr"],
    hbondconstr: Optional[bool] = DEFAULTS["hbondconstr"],
    rigidwater: Optional[bool] = DEFAULTS["rigidwater"],
):
    import numpy as np
    from moleculekit.util import ensurelist
    from moleculekit.unitcell import (
        box_vectors_to_lengths_and_angles,
        lengths_and_angles_to_box_vectors,
    )

    structure = find_file(structure, directory)
    coordinates = find_file(coordinates, directory)
    plumedfile = find_file(plumedfile, directory)
    fbrefcoor = find_file(fbrefcoor, directory)
    if parameters is not None:
        parameters = ensurelist(parameters)
        if not any(p.lower().endswith(".xml") for p in parameters):
            parameters = [find_file(p, directory) for p in parameters]

    mol = load_molecule(structure)
    if coordinates is not None:
        coormol = load_molecule(coordinates, mol=mol)
        mol.coords = coormol.coords
        if np.all(coormol.box != 0) and np.all(coormol.boxangles != 0):
            mol.box = coormol.box
            mol.boxangles = coormol.boxangles
        if mol.coords.shape[0] != len(mol.name):
            raise ValueError(
                "coordinates file must have the same number of atoms as the structure file"
            )
    mol.dropFrames(keep=mol.numFrames - 1)

    if os.environ.get("CI", None) is not None:
        platform = "CPU"  # No GPUs on GitHub Actions
        if deterministic:
            platform = "Reference"

    if boxsize is not None:
        if not isinstance(boxsize, (list, tuple)):
            box = Molecule(find_file(boxsize, directory)).boxvectors[:, :, -1]
        else:
            boxsize = np.array(boxsize)
            if boxsize.size == 3:  # Just box lengths
                bv = boxsize
                box = np.array([[bv[0], 0, 0], [0, bv[1], 0], [0, 0, bv[2]]])
            elif boxsize.shape == (6,):  # Box lengths and angles
                box = lengths_and_angles_to_box_vectors(*boxsize.astype(np.float64))
                box = np.stack(box, axis=1).T
            elif boxsize.shape == (3, 3):  # Box vectors
                box = boxsize
            else:
                raise ValueError("Box vectors must be a 3x1 or 3x3 array")
    elif np.all(mol.box != 0) and np.all(mol.boxangles != 0):
        box = mol.boxvectors[:, :, -1]
    else:
        box = None

    box_vectors = None
    if box is not None:
        # Make sure boxes are in the reduced form required by OpenMM.
        box[2] = box[2] - box[1] * np.round(box[2][1] / box[1][1])
        box[2] = box[2] - box[0] * np.round(box[2][0] / box[0][0])
        box[1] = box[1] - box[0] * np.round(box[1][0] / box[0][0])
        a = unit.Quantity(box[0] * unit.angstrom)
        b = unit.Quantity(box[1] * unit.angstrom)
        c = unit.Quantity(box[2] * unit.angstrom)
        box_vectors = (a, b, c)

        # Set box lenght and angles in mol
        bx, by, bz, alpha, beta, gamma = box_vectors_to_lengths_and_angles(
            box_vectors[0], box_vectors[1], box_vectors[2]
        )
        mol.box[:, 0] = np.array([bx, by, bz])
        mol.boxangles[:, 0] = np.array([alpha, beta, gamma])
    periodic = box is not None

    pure_nnp = False
    if structure.lower().endswith(".prmtop"):
        from openmm.app.amberprmtopfile import AmberPrmtopFile

        omm_structure = AmberPrmtopFile(structure, periodicBoxVectors=box_vectors)
        prm = []
        topology = omm_structure.topology
    elif structure.lower().endswith(".psf"):
        from openmm.app.charmmpsffile import CharmmPsfFile
        from openmm.app.charmmparameterset import CharmmParameterSet

        omm_structure = CharmmPsfFile(structure, periodicBoxVectors=box_vectors)
        if parameters is None:
            raise RuntimeError(
                "Parameters are required for CHARMM simulations. Please pass them in the input.yaml file or with the `parameters` argument."
            )
        if len(parameters) == 1:
            prm = [cleanup_charmm_prm(structure, parameters[0], loader="openmm")]
        else:
            prm = [CharmmParameterSet(*parameters)]
        topology = omm_structure.topology
    elif structure.lower().endswith(".pdb") and nnp is None:
        from openmm.app.pdbfile import PDBFile
        from openmm.app.forcefield import ForceField

        omm_structure = PDBFile(structure)
        topology = omm_structure.topology
        topology.setPeriodicBoxVectors(box_vectors)

        for prm in parameters:
            if not prm.lower().endswith(".xml"):
                raise ValueError(
                    f"Only OpenMM XML force field files are supported for PDB files: {prm}"
                )

        # This is a disgusting hack...
        # But necessary because this is how you create a system from a ForceField
        # system = forcefield.createSystem(topology, nonbondedMethod=nonbondedMethod,
        #                                  constraints=constraints, rigidWater=rigidWater)
        omm_structure = ForceField(*parameters)
        prm = [topology]
    elif os.path.splitext(structure)[1].lower() in (
        ".cif",
        ".pdb",
        ".sdf",
        ".mol2",
        ".bcif",
    ):
        if nnp is None:
            raise ValueError(
                "PDB, CIF, bCIF, SDF and MOL2 structure files are only supported for pure NNP simulations, "
                "however the NNP configuration is missing. "
                "Please set the `nnp` configuration in the input file or use a CHARMM PSF or AMBER PRMTOP file "
                "for a classical MD simulation."
            )
        pure_nnp = True
    else:
        raise ValueError(f"Unsupported structure file type: {structure}")

    if not pure_nnp and box is None and not implicitsolvent:
        raise RuntimeError(
            "A boxsize must be provided for explicit solvent simulations"
        )

    if hmr is None:
        # Use heavy hydrogen mass repartitioning for timestep > 2fs or if using NNPs
        hmr = timestep > 2 or nnp is not None
    if hbondconstr is None:
        # Constrain HBonds if timestep > 0.5
        hbondconstr = timestep > 0.5
    if rigidwater is None:
        # Make water molecules rigid if timestep > 0.5
        rigidwater = timestep > 0.5

    if pure_nnp:
        from acemd.nnp import setup_pure_nnp_system

        system, topology = setup_pure_nnp_system(
            structure, coordinates, hmr, hydrogenmass, hbondconstr, rigidwater
        )
        hbondconstr = False
        rigidwater = False
    elif not implicitsolvent:
        system = omm_structure.createSystem(
            *prm,
            nonbondedMethod=app.PME if pme else app.CutoffPeriodic,
            nonbondedCutoff=cutoff * unit.angstrom,
            constraints=app.HBonds if hbondconstr else None,
            hydrogenMass=hydrogenmass * unit.amu if hmr else None,
            rigidWater=rigidwater,
            switchDistance=switchdistance * unit.angstrom if switching else 0,
            flexibleConstraints=True,
        )

        # Change PME parameter to reaction field dielectric
        for ff in system.getForces():
            if ff.getName() == "NonbondedForce":
                ff.setReactionFieldDielectric(rfdielectric)
    else:
        # TODO: Currently missing Debye-Huckel screening parameter for modeling non-zero salt concentration
        # The implicitSolventKappa argument can be calculated as:
        # kappa = 367.434915 * sqrt(ionic_strength_moles_per_liter / (solvent_dielectric * T))
        imp_map = {1: app.HCT, 2: app.OBC1, 5: app.OBC2, 7: app.GBn, 8: app.GBn2}
        system = omm_structure.createSystem(
            nonbondedMethod=app.CutoffNonPeriodic,
            nonbondedCutoff=20 * unit.angstrom,  # Large cutoff for implicit solvent
            implicitSolvent=imp_map[igb],
            soluteDielectric=1.0,
            solventDielectric=78.3,
            constraints=app.HBonds if hbondconstr else None,
            hydrogenMass=hydrogenmass * unit.amu if hmr else None,
            rigidWater=rigidwater,
            flexibleConstraints=True,
        )

    _set_force_groups(system)

    for i in range(system.getNumParticles()):
        mass = system.getParticleMass(i).value_in_unit(unit.amu)
        if mass < 0:
            raise RuntimeError(
                f"Mass of atom {i} and element {mol.element[i]} is negative: {mass}. Possibly an issue with HMR. Try setting `hydrogenmass: 3.024` in the input config file."
            )
        if mol.element[i] == "C" and mass < 2.937 and mass != 0:
            raise RuntimeError(
                f"Heavy atom mass of atom {i} and element {mol.element[i]} is less than 2.939 amu. Try setting `hydrogenmass: 3.024` in the input config file."
            )

    if os.environ.get("TEST_DISABLE_DISPERSION_CORRECTION", None) is not None:
        _disable_dispersion_correction(system)

    if slowperiod > 1:
        logger.warning(
            "Setting slowperiod to 1 as the Multistep integrator is not supported in this ACEMD version"
        )

    if thermostat:
        integrator = mm.LangevinMiddleIntegrator(
            thermostattemperature * unit.kelvin,
            thermostatdamping / unit.picoseconds,
            timestep * unit.femtoseconds,
        )
    else:
        integrator = mm.VerletIntegrator(timestep * unit.femtoseconds)
    # integrator.setIntegrationForceGroups(mm.ForceGroup.TOTAL)
    integrator.setConstraintTolerance(1e-6)

    if barostat:
        if not periodic:
            raise RuntimeError(
                "Barostat is not supported for non-periodic systems. Please define a box size."
            )

        setup_barostat(
            thermostat,
            barostatanisotropic,
            barostatconstratio,
            barostatconstxy,
            barostatpressure,
            thermostattemperature,
            system,
        )

    platform_obj = mm.Platform.getPlatformByName(platform)
    platformprops = {}
    if platform == "CUDA":
        if precision not in ("mixed", "single", "double"):
            raise ValueError(
                f"Precision {precision} not supported. Please use 'mixed', 'single' or 'double'"
            )
        if device is not None:
            platformprops["CudaDeviceIndex"] = ",".join(map(str, device))
        platformprops["Precision"] = precision
        platformprops["CudaUseBlockingSync"] = "false"
    elif platform == "CPU":
        if ncpus is not None:
            platformprops["Threads"] = str(ncpus)
    elif platform == "OpenCL":
        if precision not in ("mixed", "single", "double"):
            raise ValueError(
                f"Precision {precision} not supported. Please use 'mixed', 'single' or 'double'"
            )
        if device is not None:
            platformprops["OpenCLDeviceIndex"] = ",".join(map(str, device))
        platformprops["Precision"] = precision

    if deterministic and platform != "Reference":
        if platform == "CPU" or (platform == "CUDA" and precision == "single"):
            raise RuntimeError(
                "Deterministic forces are not supported on CPU or single precision CUDA"
            )
        platformprops["DeterministicForces"] = "true"
        logger.warning("Deterministic forces enabled!")

    simulation = app.Simulation(
        topology,
        system,
        integrator,
        platform=platform_obj,
        platformProperties=platformprops,
    )

    _log_simulation_info(
        simulation, hmr, hbondconstr, hydrogenmass, barostat, thermostat, rigidwater
    )

    simulation.context.setPositions(mol.coords[:, :, 0] * unit.angstrom)

    restart_file = os.path.join(directory, "restart.chk")
    if restart and os.path.exists(restart_file):
        simulation.loadCheckpoint(restart_file)

    # If minimization is performed the velocities will need to be set again after minimization
    if set_velocities and simulation.currentStep == 0:
        _set_velocities(simulation, velocities, directory)

    extforces_out = []
    if extforces is not None:
        from acemd.restraints import setup_extforces

        if include_extforces:
            extforces_out, nonperiodic_restraints = setup_extforces(
                mol, extforces, fbrefcoor, system, timestep, directory
            )
        else:
            logger.warning(
                "External forces in the input file were ignored during the setup. To include them set `include_extforces=True`"
            )

        if include_extforces and nonperiodic_restraints:
            msg = "When using non-periodic restraints (+- x/y/z), all atoms must have coordinates inside the [0 - boxsize] box in the starting structure"
            if np.any(mol.coords < 0):
                raise RuntimeError(msg)
            if np.any(mol.coords > (mol.box + 20)):
                logger.warning("Some atoms are more than 20A outside the box. " + msg)
            if np.any(mol.coords > (mol.box + mol.box / 2)):
                raise RuntimeError(
                    "Some atoms are more than half the box size outside the box" + msg
                )

    setup_reporters(
        simulation,
        directory,
        trajectoryfile,
        trajvelocityfile,
        trajforcefile,
        trajectoryperiod,
        restart,
        restart_file,
        mol.masses.sum(),
        extforces_out,
        run,
    )

    if plumedfile is not None:
        from acemd.utils import plumed_parser

        try:
            from openmmplumed import PlumedForce
        except ImportError:
            raise ImportError(
                'PLUMED support requires the `openmm-plumed` package. Install it with `conda install -c conda-forge "openmm-plumed>2"`'
            )

        script = plumed_parser(plumedfile)
        if len(script) == 0:
            raise FileNotFoundError(f"PLUMED file {plumedfile} empty or not found")

        logger.info("# PLUMED")
        logger.info(f"#   Input file: {plumedfile}")
        logger.warning(
            "#   PLUMED support is currently experimental and there are some known issues https://github.com/openmm/openmm-plumed/issues. "
            "Until these are resolved, run at your own risk."
        )
        plumed = PlumedForce(script)
        plumed.setForceGroup(FGROUPS.PLUMED.value)
        plumed.setRestart(simulation.currentStep != 0)
        if thermostat:  # Set temperature for PLUMED
            plumed.setTemperature(thermostattemperature)
        # Set masses for PLUMED Note: PLUMED needs the physical masses, i.e. before the mass repartitioning
        plumed.setMasses(mol.masses.tolist())
        system.addForce(plumed)

    if nnp is not None:
        from acemd.nnp import setup_nnp

        if timestep > 2:
            logger.warning(
                "NNPs should be used with a timestep <= 2fs. They are currently too unstable for larger timesteps"
            )
        _device = platform if device is None else f"{platform}:{device[0]}"
        setup_nnp(system, nnp, mol, _device, pure_nnp)

    logger.info("#")
    logger.info("# Removing bonded terms with zero force constants")
    _optimize_bonds(system)
    _optimize_torsions(system)
    simulation.context.reinitialize(preserveState=True)

    return system, simulation, mol, extforces_out


def _log_simulation_info(
    simulation, hmr, hbond_constr, hydrogenmass, barostat, thermostat, rigidwater
):
    import openmm

    ensemble_map = {(False, False): "NVE", (False, True): "NVT", (True, True): "NPT"}

    logger.info("#")
    logger.info("# Initializing engine")
    logger.info(f"# Version: {openmm.__version__}")
    logger.info("#   Available platforms")
    platform = simulation.context.getPlatform()
    for i in range(platform.getNumPlatforms()):
        logger.info(f"#     {platform.getPlatform(i).getName()}")

    logger.info(f"# Selected platform: {platform.getName()}")
    logger.info("# Platform properties")
    for prop in platform.getPropertyNames():
        logger.info(
            f"#   {prop}: {platform.getPropertyValue(simulation.context, prop)}"
        )

    logger.info("#")
    logger.info("# Creating simulation system")
    logger.info(f"#   Ensemble: {ensemble_map[(barostat, thermostat)]}")
    logger.info(f"#   Number of particles: {simulation.system.getNumParticles()}")
    logger.info(f"#   Number of degrees of freedom {_get_dof(simulation.system)}")
    box = simulation.context.getState().getPeriodicBoxVectors()
    box = box.value_in_unit(unit.angstrom)
    logger.info(
        f"#   Periodic box size: {box[0][0]:.3f} {box[1][1]:.3f} {box[2][2]:.3f} A"
    )

    intg = simulation.integrator
    logger.info("#")
    logger.info("# Integrator")
    logger.info(f"#   Type: {intg.__class__.__name__}")
    logger.info(
        f"#   Step size: {intg.getStepSize().value_in_unit(unit.femtosecond):.2f} fs"
    )
    logger.info(f"#   Constraint tolerance: {intg.getConstraintTolerance()}")

    # Print the barostat parameters
    if barostat:
        for ff in simulation.system.getForces():
            if ff.getName() in (
                "MonteCarloBarostat",
                "MonteCarloAnisotropicBarostat",
                "MonteCarloMembraneBarostat",
            ):
                logger.info("#")
                logger.info("# Barostat")
                logger.info(f"#   Pressure: {ff.getDefaultPressure()}")
                logger.info(f"#   Temperature: {ff.getDefaultTemperature()}")
                if ff.getName() == "MonteCarloMembraneBarostat":
                    xy_map = {0: "isotropic", 1: "anisotropic", 2: "constant volume"}
                    z_map = {0: "free", 1: "fixed", 2: "constant volume"}
                    logger.info(f"#   Surface tension: {ff.getDefaultSurfaceTension()}")
                    logger.info(f"#   XYMode: {xy_map[ff.getXYMode()]}")
                    logger.info(f"#   ZMode: {z_map[ff.getZMode()]}")
                if ff.getName() == "MonteCarloAnisotropicBarostat":
                    logger.info(f"#   Scale X: {ff.getScaleX()}")
                    logger.info(f"#   Scale Y: {ff.getScaleY()}")
                    logger.info(f"#   Scale Z: {ff.getScaleZ()}")

    # Log information on the non-bonded force like cutoff and switching distance
    for ff in simulation.system.getForces():
        if ff.getName() == "NonbondedForce":
            logger.info("#")
            logger.info("# Non-bonded interactions")
            logger.info(
                f"#   Cutoff distance: {ff.getCutoffDistance().value_in_unit(unit.angstrom):.3f} A"
            )
            switch = ff.getSwitchingDistance().value_in_unit(unit.angstrom)
            if switch <= 0:
                logger.info("#   Switching: off")
            else:
                logger.info(
                    f"#   Switching distance: {ff.getSwitchingDistance().value_in_unit(unit.angstrom):.3f} A"
                )

            # Coulombic term and PME ewald tolerance
            if ff.getNonbondedMethod() == openmm.NonbondedForce.PME:
                logger.info(f"#   PME: Ewald tolerance: {ff.getEwaldErrorTolerance()}")
                logger.info(
                    f"#   Reaction field dielectric: {ff.getReactionFieldDielectric()}"
                )
            else:
                logger.info("#   PME: Not used")

    # Log information on hydrogen constraints
    if hbond_constr:
        logger.info("#")
        logger.info("# Hydrogen constraints")
        logger.info("#   Bonds involving hydrogen are constrained")
    else:
        logger.info("#")
        logger.info("# No hydrogen constraints were applied")

    if rigidwater:
        logger.info("#   Making water molecules rigid")

    if hmr:
        logger.info("#")
        logger.info("# Heavy hydrogen mass repartitioning")
        logger.info(f"#   Hydrogen mass increased to {hydrogenmass} amu")
    else:
        logger.info("#")
        logger.info("# No hydrogen mass repartitioning was applied")


def run(
    directory,
    simulation,
    nsteps: int = 0,
    extforces: list = (),
    period=25000,
    velocities=DEFAULTS["velocities"],
    dump_simulation_xml=False,
    stepzero=DEFAULTS["stepzero"],
):
    from acemd.restraints import update_restraints
    from moleculekit.unitcell import box_vectors_to_lengths_and_angles
    from openmm import XmlSerializer
    import numpy as np

    start_step = simulation.currentStep

    if start_step == 0:  # Only set velocities when starting a new simulation
        _set_velocities(simulation, velocities, directory)

    _optimize_constraints(simulation.system)
    simulation.context.reinitialize(preserveState=True)

    if dump_simulation_xml or os.environ.get("DUMP_SIMULATION_XML", None) is not None:
        with open(os.path.join(directory, "system.xml"), "w") as f:
            f.write(XmlSerializer.serialize(simulation.system))
        with open(os.path.join(directory, "integrator.xml"), "w") as f:
            f.write(XmlSerializer.serialize(simulation.integrator))

    logger.info("#")
    logger.info("# Running simulation")
    logger.info(f"#   Current step: {start_step}")
    logger.info(f"#   Number of steps: {nsteps}")
    logger.info(f"#   Trajectory period: {period}")
    logger.info("#")

    if stepzero and start_step == 0:
        update_restraints(simulation, extforces, start_step, log=True)

        # Trigger all reporters to print log and write trajectory, velocity and forces
        for reporter in simulation.reporters:
            reporter.report(
                simulation,
                simulation.context.getState(
                    getPositions=True,
                    getVelocities=True,
                    getForces=True,
                    getEnergy=True,
                ),
            )

    # How many steps to run before updating the restraint force constants
    restr_upd_freq = 1

    # Main MD loop
    for step in range(start_step, nsteps, restr_upd_freq):
        update_restraints(simulation, extforces, step)
        simulation.step(min(restr_upd_freq, nsteps - step))

    # Write final coordinates and velocities
    state = simulation.context.getState(getPositions=True, getVelocities=True)
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
    # Velocities convert: nm/ps --> Ang/internal
    vel = state.getVelocities(asNumpy=True).value_in_unit(
        unit.nanometer / unit.picosecond
    )
    mol = Molecule().empty(pos.shape[0])
    logger.info("# Writing final coordinates to 'output.coor'")
    mol.coords = pos.astype(np.float32)[:, :, None].copy()
    mol.write(os.path.join(directory, "output.coor"))
    logger.info("# Writing final velocities to 'output.vel'")
    mol.coords = vel.astype(np.float32)[:, :, None].copy() * VEL_CONVERSION_FACTOR
    mol.write(os.path.join(directory, "output.vel"), type="coor")

    # Write final box size
    logger.info("# Writing final simulation box size to 'output.xsc'")
    boxvectors = state.getPeriodicBoxVectors(asNumpy=True).value_in_unit(unit.angstrom)
    bx, by, bz, alpha, beta, gamma = box_vectors_to_lengths_and_angles(
        boxvectors[0], boxvectors[1], boxvectors[2]
    )
    mol.box = np.array([bx, by, bz])[:, None].astype(np.float32).copy()
    mol.boxangles = np.array([alpha, beta, gamma])[:, None].astype(np.float32).copy()
    mol.step = np.array([nsteps], dtype=np.int32)
    mol.write(os.path.join(directory, "output.xsc"))

    logger.info("#")
    logger.info("# Simulation completed!")


def _optimize_constraints(system):
    logger.info("#")
    logger.info("# Removing bonded terms for constrainted atoms")
    constraints = []
    for i in range(system.getNumConstraints()):
        p1, p2, d = system.getConstraintParameters(i)
        constraints.append((p1, p2))
        constraints.append((p2, p1))
    constraints = set(constraints)
    logger.info(f"#   Number of constraints: {int(len(constraints) / 2)}")

    if len(constraints):
        # Find HarmonicBondForce
        match = [ff.getName() == "HarmonicBondForce" for ff in system.getForces()]
        try:
            idx = match.index(True)
        except ValueError:
            return
        bond = system.getForce(idx)
        logger.info("#   Harmonic bond interations")
        logger.info(f"#     Initial number of terms: {bond.getNumBonds()}")

        # Create the new harmonic bond force
        bond_new = mm.HarmonicBondForce()
        bond_new.setForceGroup(bond.getForceGroup())
        for i in range(bond.getNumBonds()):
            p1, p2, l, k = bond.getBondParameters(i)
            if (p1, p2) in constraints:
                continue
            bond_new.addBond(p1, p2, l, k)
        logger.info(f"#     Optimized number of terms: {bond_new.getNumBonds()}")

        # Remove the current harmonic bond force and add the new one
        system.removeForce(idx)
        if bond_new.getNumBonds() > 0:
            system.addForce(bond_new)
        else:
            logger.info("#     NOTE: harmonic bond interactions skipped")


def _optimize_torsions(system):
    # Remove torsions with 0 force constant

    # Find PeriodicTorsionForce
    match = [ff.getName() == "PeriodicTorsionForce" for ff in system.getForces()]
    try:
        idx = match.index(True)
    except ValueError:
        return

    logger.info("#   Torsion interactions")
    force = system.getForce(idx)
    logger.info(f"#     Initial number of terms: {force.getNumTorsions()}")
    torsions = []
    for j in range(force.getNumTorsions()):
        p1, p2, p3, p4, per, phi, k = force.getTorsionParameters(j)
        if k.value_in_unit(unit.kilocalorie_per_mole) == 0:
            continue
        torsions.append((p1, p2, p3, p4, per, phi, k))
    logger.info(f"#     Optimized number of terms: {len(torsions)}")
    force_new = mm.PeriodicTorsionForce()
    force_new.setForceGroup(force.getForceGroup())
    for t in torsions:
        force_new.addTorsion(*t)
    system.removeForce(idx)
    if force_new.getNumTorsions() > 0:
        system.addForce(force_new)
    else:
        logger.info("#     NOTE: torsion interactions skipped")


def _optimize_bonds(system):
    # Find HarmonicBondForce
    match = [ff.getName() == "HarmonicBondForce" for ff in system.getForces()]
    try:
        idx = match.index(True)
    except ValueError:
        return

    bond = system.getForce(idx)
    logger.info("#   Harmonic bond interations")
    logger.info(f"#     Initial number of terms: {bond.getNumBonds()}")

    # Create the new harmonic bond force
    bond_new = mm.HarmonicBondForce()
    bond_new.setForceGroup(bond.getForceGroup())
    for i in range(bond.getNumBonds()):
        p1, p2, l, k = bond.getBondParameters(i)
        if k < (1e-24 * unit.kilojoule_per_mole / unit.nanometer**2):
            continue
        bond_new.addBond(p1, p2, l, k)
    logger.info(f"#     Optimized number of terms: {bond_new.getNumBonds()}")

    # Remove the current harmonic bond force and add the new one
    system.removeForce(idx)
    if bond_new.getNumBonds() > 0:
        system.addForce(bond_new)
    else:
        logger.info("#     NOTE: harmonic bond interactions skipped")


def get_energy_decomposition(context, state):
    energy_terms = {}
    mapping = {
        "HarmonicBondForce": "Bond",
        "HarmonicAngleForce": "Angle",
        "PeriodicTorsionForce": "Dihedral",
        "NonbondedForce": "Non-bonded",
        "CustomTorsionForce": "Improper",
        "CustomGBForce": "Implicit",
        "CustomExternalForce": "External",
        "CustomCentroidBondForce": "External",
        "CMAPTorsionForce": "CMAP",
        "TorchForce": "NNP",
        "PlumedForce": "PLUMED",
    }  # TODO: Improve this by using the force group numbers to categorize the forces
    ignore = (
        "CMMotionRemover",
        "MonteCarloBarostat",
        "MonteCarloMembraneBarostat",
        "MonteCarloAnisotropicBarostat",
        "CustomNonbondedForce",  # Already in the group of NonbondedForce
    )
    for force in context.getSystem().getForces():
        fname = force.getName()
        if fname in ignore:
            continue
        fgroup = force.getForceGroup()
        ene = context.getState(getEnergy=True, groups={fgroup}).getPotentialEnergy()
        ene = ene.value_in_unit(unit.kilocalorie_per_mole)

        fname = mapping.get(fname, fname)

        # If we have one group per restraint. Only doable with few extforces due to OpenMM force group limit
        if fname == "External" and fgroup > FGROUPS.EXTERNAL.value:
            fname = f"External {fgroup - FGROUPS.EXTERNAL.value - 1}"

        if fname not in energy_terms:
            energy_terms[fname] = 0

        if fgroup == FGROUPS.DEBUG.value:
            energy_terms["DEBUG"] = ene
        else:
            energy_terms[fname] += ene

    energy_terms["Potential"] = state.getPotentialEnergy().value_in_unit(
        unit.kilocalorie_per_mole
    )
    energy_terms["Kinetic"] = state.getKineticEnergy().value_in_unit(
        unit.kilocalorie_per_mole
    )
    energy_terms["Total"] = energy_terms["Potential"] + energy_terms["Kinetic"]
    return energy_terms


def print_energy_decomposition(energy_terms):
    print("#" + "".join([f"{key:>20s}" for key in energy_terms.keys()]))
    print(" " + "".join([f"{energy_terms[key]:20.2f}" for key in energy_terms]))


def get_sim_properties(context, totalMass, dof):
    state = context.getState(getEnergy=True)
    box = state.getPeriodicBoxVectors()
    volume = box[0][0] * box[1][1] * box[2][2]
    density = (totalMass * unit.dalton / volume).value_in_unit(
        unit.gram / unit.item / unit.milliliter
    )
    volume = volume.value_in_unit(unit.angstrom**3)
    integrator = context.getIntegrator()
    if hasattr(integrator, "computeSystemTemperature"):
        temperature = integrator.computeSystemTemperature().value_in_unit(unit.kelvin)
    else:
        if dof == 0:
            temperature = 0
        else:
            temperature = (
                2 * state.getKineticEnergy() / (dof * unit.MOLAR_GAS_CONSTANT_R)
            ).value_in_unit(unit.kelvin)
    time = state.getTime().value_in_unit(unit.nanosecond)
    return time, temperature, volume, density


def _get_dof(system):
    # Compute the number of degrees of freedom.
    dof = 0
    for i in range(system.getNumParticles()):
        if system.getParticleMass(i) > 0 * unit.dalton:
            dof += 3
    for i in range(system.getNumConstraints()):
        p1, p2, _ = system.getConstraintParameters(i)
        if (
            system.getParticleMass(p1) > 0 * unit.dalton
            or system.getParticleMass(p2) > 0 * unit.dalton
        ):
            dof -= 1
    if any(
        type(system.getForce(i)) == mm.CMMotionRemover
        for i in range(system.getNumForces())
    ):
        dof -= 3
    return dof
