# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import torch as pt
import logging

logger = logging.getLogger("acemd")


class TorchMDNETForce(pt.nn.Module):
    def __init__(
        self,
        model_file,
        atomic_numbers,
        group_indices,
        total_charges,
        max_num_neighbors,
        device="cuda",
    ):
        super().__init__()
        from torchmdnet.models.model import load_model

        assert len(group_indices) == len(total_charges)

        self.model = load_model(
            model_file,
            derivative=False,
            max_num_neighbors=max_num_neighbors,
            remove_ref_energy=False,
            static_shapes=True,
            check_errors=False,
        ).to(device)
        for parameter in self.model.parameters():
            parameter.requires_grad = False

        self.register_buffer(
            "all_atom_indices",
            pt.tensor(sum(group_indices, []), dtype=pt.long, device=device),
        )
        self.register_buffer(
            "atomic_numbers", pt.tensor(atomic_numbers, dtype=pt.long, device=device)
        )
        batch = sum(
            [[i] * len(atom_indices) for i, atom_indices in enumerate(group_indices)],
            [],
        )
        self.register_buffer("batch", pt.tensor(batch, dtype=pt.long, device=device))
        self.register_buffer(
            "total_charges", pt.tensor(total_charges, dtype=pt.long, device=device)
        )

    def forward(self, positions):
        # This is needed for the minimizer because it switches to CPU when there are large forces
        pos_device = positions.device.type
        if pos_device != self.atomic_numbers.device.type:
            positions = positions.to(self.atomic_numbers.device)

        positions = (
            pt.index_select(positions, 0, self.all_atom_indices).to(pt.float32) * 10
        )  # nm --> A
        energies, *_ = self.model(
            self.atomic_numbers, positions, batch=self.batch, q=self.total_charges
        )
        energy = energies.sum() * 96.4915666370759  # eV -> kJ/mol

        # Also only needed for the minimizer
        if pos_device != self.atomic_numbers.device.type:
            energy = energy.to(pos_device)
        return energy


class ANITorch(pt.nn.Module):

    def __init__(self, indexes, atomic_numbers, model, modelIndex=None, device="cuda"):
        import torchani

        super().__init__()

        self.indexes = pt.tensor(indexes, dtype=pt.long, device=device)

        # Store the atomic numbers
        self.atomic_numbers = pt.tensor(atomic_numbers, device=device).unsqueeze(0)

        # Create an ANI-2x model
        modeldict = {
            "ani1x": torchani.models.ANI1x,
            "ani2x": torchani.models.ANI2x,
            "ani1ccx": torchani.models.ANI1ccx,
        }
        self.model = modeldict[model](
            model_index=modelIndex, periodic_table_index=True
        ).to(device)

        # Accelerate the model
        if model == "ani2x" and device == "cuda":
            try:
                from NNPOps import OptimizedTorchANI

                self.model = OptimizedTorchANI(self.model, self.atomic_numbers).to(
                    device
                )
            except ImportError:
                logger.warning(
                    "NNPOps library not found. Using the standard ANI-2x model. Please install NNPOps for better performance."
                )

    def forward(self, positions):
        # This is needed for the minimizer because it switches to CPU when there are large forces
        pos_device = positions.device.type
        if pos_device != self.atomic_numbers.device.type:
            positions = positions.to(self.atomic_numbers.device)

        # Prepare the positions
        positions = positions[self.indexes].unsqueeze(0).float() * 10  # nm --> Å

        # Run ANI-2x
        result = self.model((self.atomic_numbers, positions))

        # Get the potential energy
        energy = result.energies[0] * 2625.5  # Hartree --> kJ/mol

        # Also only needed for the minimizer
        if pos_device != self.atomic_numbers.device.type:
            energy = energy.to(pos_device)
        return energy


def setup_pure_nnp_system(
    structure, coordinates, hmr, hydrogenmass, hbondconstr, rigidwater
):
    import openmm as mm
    from moleculekit.molecule import Molecule
    from moleculekit.periodictable import periodictable
    import numpy as np
    import tempfile
    import os
    from openmm import app

    if hbondconstr:
        logger.warning(
            "HBonds are not supported for pure NNP simulations and were disabled"
        )
    if rigidwater:
        logger.warning(
            "Rigid water is not supported for pure NNP simulations and was disabled"
        )

    system = mm.System()
    # Create an OpenMM system directly from the moleculekit Molecule
    mol = Molecule(structure)
    mol.read(coordinates)
    masses = mol.masses
    if np.any(masses == 0):
        masses = [periodictable[el].mass for el in mol.element]

    if hmr:
        if len(mol.bonds) == 0:
            raise ValueError(
                "No bonds found in the structure file. Cannot perform HMR. Either fix "
                "the structure file or set `hmr: false` in the input config file."
            )
        new_masses = masses.copy()
        gg = mol.toGraph()
        if hydrogenmass <= 0:
            raise ValueError("Hydrogen mass must be positive")
        for i in range(mol.numAtoms):
            if mol.element[i] == "H":
                heavy_atom = None
                for a2 in gg.neighbors(i):
                    if mol.element[a2] != "H":
                        heavy_atom = a2
                        break
                if heavy_atom is not None:
                    new_masses[i] = hydrogenmass
                    new_masses[heavy_atom] -= hydrogenmass - masses[i]
        masses = new_masses

    for mass in masses:
        system.addParticle(mass)

    with tempfile.TemporaryDirectory() as tmpdir:
        mol.write(os.path.join(tmpdir, "mol.pdb"), writebonds=True)
        topology = app.PDBFile(os.path.join(tmpdir, "mol.pdb")).topology
    return system, topology


def setup_nnp(system, nnp, mol, device, pure_nnp):
    from openmmtorch import TorchForce
    from moleculekit.periodictable import periodictable
    from acemd.acemd import FGROUPS
    import numpy as np

    device = device.lower()

    logger.info("#")
    logger.info(f"# Setting up NNP model {nnp['name']}")
    if pure_nnp:
        logger.info("#     Pure NNP simulation")
    else:
        logger.info("#     NNP/MM mixed simulation")

    if nnp["type"].lower() != "torch":
        raise ValueError(
            f"NNP type {nnp['type']} not supported. Only `torch` models are supported at the moment"
        )

    if not pure_nnp:
        indexes = mol.atomselect(nnp["sel"], indexes=True, guessBonds=False)
        logger.info(f"#     Selected atoms: {len(indexes)}")
    else:
        indexes = np.arange(mol.numAtoms)

    atomic_numbers = [periodictable[el].number for el in mol.element[indexes]]
    total_charge = int(np.round(mol.charge[indexes].sum()))

    if len(nnp.get("file", "")) == 0:
        logger.info("#     Loading NNP model from TorchANI")
        if total_charge != 0:
            logger.warning(
                f"ANI NNP models cannot correctly describe molecules with total charge different than 0. "
                f"Your selection has a total charge of {total_charge}. Proceed at your own risk."
            )
        name = nnp["name"].lower().replace("-", "")
        if name in ("ani1x", "ani2x", "ani1ccx"):
            ani = ANITorch(indexes, atomic_numbers, model=name, device=device)
            force = TorchForce(pt.jit.script(ani))
        else:
            raise ValueError(
                f"NNP model {nnp['name']} not supported. Please specify a file."
            )
    else:
        logger.info(f"#     Loading NNP model from file {nnp['file']}")
        name = nnp["name"].lower().replace("-", "")
        if name != "torchmdnet":
            raise ValueError(
                f"NNP model {nnp['name']} not supported. Only `torchmdnet` models are supported with model files at the moment"
            )

        max_num_neighbors = min(len(indexes), nnp.get("max_num_neighbors", 128))
        logger.info(f"#     Max num. neighbors: {max_num_neighbors}")

        group_indices = [indexes.tolist()]

        if total_charge not in (0, -1, 1):
            logger.warning(
                f"AceFF v1.0 cannot correctly describe molecules with total charge different than 0, -1 or 1. "
                f"Your selection has a total charge of {total_charge}. Proceed at your own risk."
            )
        logger.info(f"#     Total charge: {total_charge}")
        tmd = TorchMDNETForce(
            nnp["file"],
            atomic_numbers,
            group_indices,
            [float(total_charge)],
            max_num_neighbors,
            device=device,
        )
        force = TorchForce(pt.jit.script(tmd))
        force.setProperty("useCUDAGraphs", "true" if "cuda" in device else "false")
        if "cuda" in device:
            logger.info(
                f"#     Device: {device}. CUDA graphs: {'true' if 'cuda' in device else 'false'}"
            )

    # force.setForceGroup(FGROUP_NNP)
    force.setUsesPeriodicBoundaryConditions(False)  # For NNP/MM we don't need PBC
    force.setForceGroup(FGROUPS.NNP.value)
    system.addForce(force)

    if not pure_nnp:
        # Check that there are no bonds between the selected atoms and the rest of the system
        if any(np.sum(np.isin(mol.bonds, indexes), axis=1) == 1):
            raise ValueError(
                f"NNP atoms {nnp['sel']} are bonded to the rest of the system. Please select a different set of atoms."
            )

        # Remove all bonded terms from system between atoms in indexes
        rb = _remove_bonds(system, indexes)
        ra = _remove_angles(system, indexes)
        rt = _remove_torsions(system, indexes)
        logger.info(f"#     Removed {rb} bonds, {ra} angles and {rt} torsions")

        # Set all LJ and electrostatic terms to zero between the atoms in indexes
        _add_nonbonded_exceptions(system, indexes)


def _remove_bonds(system, indexes):
    import openmm as mm

    removed = 0

    # Find HarmonicBondForce
    match = [isinstance(ff, mm.HarmonicBondForce) for ff in system.getForces()]
    try:
        idx = match.index(True)
    except ValueError:
        return removed
    bond = system.getForce(idx)

    # Create the new harmonic bond force
    bond_new = mm.HarmonicBondForce()
    bond_new.setForceGroup(bond.getForceGroup())
    for i in range(bond.getNumBonds()):
        p1, p2, l, k = bond.getBondParameters(i)
        if p1 in indexes and p2 in indexes:  # Skip bonds between atoms in indexes
            removed += 1
            continue
        bond_new.addBond(p1, p2, l, k)

    # Remove the current harmonic bond force and add the new one
    system.removeForce(idx)
    if bond_new.getNumBonds() > 0:
        system.addForce(bond_new)

    return removed


def _remove_angles(system, indexes):
    import openmm as mm

    removed = 0

    # Find HarmonicAngleForce
    match = [isinstance(ff, mm.HarmonicAngleForce) for ff in system.getForces()]
    try:
        idx = match.index(True)
    except ValueError:
        return removed
    angle = system.getForce(idx)

    # Create the new harmonic angle force
    angle_new = mm.HarmonicAngleForce()
    angle_new.setForceGroup(angle.getForceGroup())
    for i in range(angle.getNumAngles()):
        p1, p2, p3, aa, k = angle.getAngleParameters(i)
        if all(p in indexes for p in (p1, p2, p3)):
            removed += 1
            continue
        angle_new.addAngle(p1, p2, p3, aa, k)

    # Remove the current harmonic angle force and add the new one
    system.removeForce(idx)
    if angle_new.getNumAngles() > 0:
        system.addForce(angle_new)

    return removed


def _remove_torsions(system, indexes):
    import openmm as mm

    removed = 0

    # Find PeriodicTorsionForce
    match = [isinstance(ff, mm.PeriodicTorsionForce) for ff in system.getForces()]
    try:
        idx = match.index(True)
    except ValueError:
        return removed
    force = system.getForce(idx)

    torsions = []
    for j in range(force.getNumTorsions()):
        p1, p2, p3, p4, per, phi, k = force.getTorsionParameters(j)
        if all(p in indexes for p in (p1, p2, p3, p4)):
            removed += 1
            continue
        torsions.append((p1, p2, p3, p4, per, phi, k))

    force_new = mm.PeriodicTorsionForce()
    force_new.setForceGroup(force.getForceGroup())
    for t in torsions:
        force_new.addTorsion(*t)
    system.removeForce(idx)
    if force_new.getNumTorsions() > 0:
        system.addForce(force_new)

    return removed


def _add_nonbonded_exceptions(system, indexes):
    import openmm as mm

    # Find NonbondedForce
    match = [isinstance(ff, mm.NonbondedForce) for ff in system.getForces()]
    try:
        idx = match.index(True)
    except ValueError:
        return

    force: mm.NonbondedForce = system.getForce(idx)
    for i in range(len(indexes)):
        for j in range(i + 1, len(indexes)):
            force.addException(indexes[i], indexes[j], 0, 0.5, 0, replace=True)
