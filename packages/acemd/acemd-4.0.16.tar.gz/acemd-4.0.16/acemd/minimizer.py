# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from openmm.openmm import Context, System
from openmm import unit
import openmm as mm
import numpy as np
import logging
import os

logger = logging.getLogger("acemd.minimizer")


def get_energy_forces(
    context: Context,
    positions: np.ndarray,
    getForces=True,
    zero_mass_particles: np.ndarray = None,
):
    """
    Calculate the potential energy and forces of the system.
    It takes as input positions in Angstrom and returns the potential energy in kcal/mol and forces in kcal/mol/Angstrom.

    Parameters
    ----------
    context: Context
        OpenMM context object
    positions: np.ndarray
        Positions of the atoms in Angstrom

    Returns
    -------
    ene: float
        Potential energy of the system in kcal/mol
    forces: np.ndarray
        Forces on the atoms in kcal/mol/Angstrom
    """
    context.setPositions(positions * unit.angstrom)
    context.computeVirtualSites()  # Recompute the positions of the virtual sites

    state = context.getState(getForces=getForces, getEnergy=True)
    ene = state.getPotentialEnergy().value_in_unit(unit.kilocalorie_per_mole)
    if getForces:
        forces = state.getForces(asNumpy=True).value_in_unit(
            unit.kilocalorie_per_mole / unit.angstrom
        )
        # Set forces to zero for virtual sites (and other zero mass particles)
        if zero_mass_particles is not None:
            forces[zero_mass_particles, :] = 0
        return ene, forces
    return ene


def bracket_and_golden_section_search(
    context, initpos, search_dir, u, zero_mass_particles
):
    """
    Bracket and golden section search algorithm.

    Parameters
    ----------
    context: Context
        OpenMM context object
    initpos: np.ndarray
        Initial position
    search_dir: np.ndarray
        Search direction
    u: float
        Should be initialized to be potential for pos, returns potential for min energy pos
    zero_mass_particles: np.ndarray
        Mask of particles with zero mass
    """
    zmp = zero_mass_particles

    tau = 0.618033988749895  # tau=(sqrt(5)-1)/2,  solution to  tau^2 = 1-tau
    dis = 1.0  # largest displacement along search direction
    tol = 1.0e-2  # tolerance for convergence of search interval
    u_amin = u

    # use s and dis2 to determine amax search factor
    smax2 = np.max(np.sum(search_dir**2, axis=1))
    smax = np.sqrt(smax2)

    amax = dis / smax
    amin = 0.0
    delta = amax - amin

    a1 = amin + (1 - tau) * delta
    a2 = amin + tau * delta

    # interval is considered trivially bracketed if small enough
    is_bracket = (delta * smax) <= tol

    # find potential for amax
    u_amax = get_energy_forces(context, initpos + amax * search_dir, False, zmp)

    # find potential for a1
    u_a1 = get_energy_forces(context, initpos + a1 * search_dir, False, zmp)

    # find potential for a2
    u_a2, forces = get_energy_forces(context, initpos + a2 * search_dir, True, zmp)

    # save most recent computation
    u = u_a2

    while not is_bracket:
        if u_a1 >= u_amin:
            # shrink bracketing interval to [amin,a1]
            # compute new u_a1, u_a2
            amax = a1
            u_amax = u_a1

            delta = amax - amin
            a1 = amin + (1 - tau) * delta
            a2 = amin + tau * delta

            # find potential for a1
            pos = initpos + a1 * search_dir
            u_a1 = get_energy_forces(context, pos, False, zmp)

            # find potential for a2
            pos = initpos + a2 * search_dir
            u_a2, forces = get_energy_forces(context, pos, True, zmp)

            # update is_bracket since interval has shrunk
            is_bracket = delta * smax <= tol

            # save most recent computation
            u = u_a2
        elif u_a2 >= u_amin:
            # shrink bracketing interval to [amin,a2]
            # compute new u_a1
            amax = a2
            u_amax = u_a2
            a2 = a1
            u_a2 = u_a1

            delta = amax - amin
            a1 = amin + (1 - tau) * delta

            # find potential for a1
            pos = initpos + a1 * search_dir
            u_a1, forces = get_energy_forces(context, pos, True, zmp)

            # update is_bracket since interval has shrunk
            is_bracket = delta * smax <= tol

            # save most recent computation
            u = u_a1
        elif u_amax < u_a1 and u_amax < u_a2:
            # shift bracketing interval to [a2,a2+delta]
            # compute new u_a2, u_amax
            amin = a2
            u_amin = u_a2
            a1 = amax
            u_a1 = u_amax

            amax = amin + delta
            a2 = amin + tau * delta

            # find potential for amax
            pos = initpos + amax * search_dir
            u_amax = get_energy_forces(context, pos, False, zmp)

            # find potential for a2
            pos = initpos + a2 * search_dir
            u_a2, forces = get_energy_forces(context, pos, True, zmp)
        else:
            # now we consider bracketed interval unimodal
            # continue with golden section search
            is_bracket = True

    # golden section search
    while delta * smax > tol:
        if u_a1 > u_a2:
            amin = a1
            u_amin = u_a1
            delta = amax - amin

            a1 = a2
            u_a1 = u_a2

            a2 = amin + tau * delta

            # find potential for a2
            pos = initpos + a2 * search_dir
            u_a2, forces = get_energy_forces(context, pos, True, zmp)

            # save most recent computation
            u = u_a2
        else:
            amax = a2
            u_amax = u_a2
            delta = amax - amin

            a2 = a1
            u_a2 = u_a1

            a1 = amin + (1 - tau) * delta

            # find potential for a1
            pos = initpos + a1 * search_dir
            u_a1, forces = get_energy_forces(context, pos, True, zmp)

            # save most recent computation
            u = u_a1

    assert forces is not None
    assert pos is not None

    return pos, forces, u


def cgmin_compute(
    context: Context,
    start_step: int,
    end_step: int,
    threshold: float,
    zero_mass_particles: np.ndarray,
):
    state = context.getState(getPositions=True)
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)

    # compute initial force
    u, forces = get_energy_forces(
        context, pos, getForces=True, zero_mass_particles=zero_mass_particles
    )

    # use force to set initial search direction
    search_dir = forces.copy()

    # find f dot f
    fdf = np.sum(forces**2)

    # conjugate gradient loop
    for step in range(start_step, end_step):

        # retain initial position
        initpos = pos.copy()

        # find minimum along search direction
        pos, forces, u = bracket_and_golden_section_search(
            context, initpos, search_dir, u, zero_mass_particles
        )

        old_fdf = fdf

        # find f dot f
        fdf = np.sum(forces**2)

        # determine new search direction
        beta = fdf / old_fdf
        maxforce = np.max(np.abs(forces))

        search_dir = forces + beta * search_dir

        energy, forces = get_energy_forces(context, pos, True, zero_mass_particles)

        # print results
        maxforce = np.max(np.abs(forces))
        logger.info(f"{step:12d} {energy:14.4f} {maxforce:16.4f}")

        # For testing purposes
        if os.getenv("MINIMIZATION_CSV_OUT") is not None:
            with open(os.getenv("MINIMIZATION_CSV_OUT"), "a") as fd:
                fd.write(f"{step},{energy},{maxforce}\n")

        # terminate
        if threshold is not None and maxforce < threshold:
            return step

    return end_step - 1


def minimize(system: System, context: Context, n_steps: int, outcoor=None):
    from moleculekit.molecule import Molecule

    zero_mass_particles = np.array(
        [system.getParticleMass(i) == 0 for i in range(system.getNumParticles())],
        dtype=bool,
    )

    logger.info("#")
    logger.info(f"# Minimizing system with CG for {n_steps} steps")
    logger.info("#       Step      Potential   Max Force Comp.")
    logger.info("#                [kcal/mol]      [kcal/mol/A]")

    # Check if velocities are present and if yes issue a warning
    state = context.getState(getVelocities=True)
    if np.max(np.abs(state.getVelocities(asNumpy=True))) > 1e-6:
        logger.info(
            "# WARNING: Initial velocities are not zero. The minimizer will reset them so be sure to set them again afterwards."
        )

    state = context.getState(getEnergy=True, getPositions=True, getForces=True)
    energy = state.getPotentialEnergy().value_in_unit(unit.kilocalorie_per_mole)
    forces = state.getForces(asNumpy=True).value_in_unit(
        unit.kilocalorie_per_mole / unit.angstrom
    )
    pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)

    logger.info(f"{0:12d} {energy:14.4f} {np.max(np.abs(forces)):16.4f}")
    # For testing purposes
    if os.getenv("MINIMIZATION_CSV_OUT") is not None:
        with open(os.getenv("MINIMIZATION_CSV_OUT"), "w") as fd:
            fd.write("Step,Potential,Max Force Comp\n")
            fd.write(f"{0},{energy},{np.max(np.abs(forces))}\n")

    force_threshold = 1e5  # This threshold was arbitrarily chosen by Stefan based on some test systems he had around
    step = 1
    if np.max(np.abs(forces)) > force_threshold:
        # Surprisingly this is not a matter of the precision of the platform. You can use double precision on the GPU and it will still fail.
        # The issue is probably in the accumulation of forces and the numerical stability of the force computation on CUDA vs CPU
        logger.info(
            f"# WARNING: due to large initial force components ({np.max(np.abs(forces)):.2f}) the minimization has to switch to the CPU platform"
        )
        # Create a fake integrator for an auxilary context
        integrator = mm.VerletIntegrator(0)

        # Create the auxilary context for CPU platform
        logger.info(
            f"# Creating an auxilary platform for CPU minimization until force reaches {force_threshold:.2f} kcal/mol/A"
        )
        platform = mm.Platform.getPlatformByName("CPU")
        properties = {"CpuThreads": "1"}

        aux_context = mm.Context(context.getSystem(), integrator, platform, properties)

        # Set positions and restraints
        aux_context.setPositions(pos * unit.angstrom)

        # Run minimization with CPU platform
        step = cgmin_compute(
            aux_context, 1, n_steps, force_threshold, zero_mass_particles
        )
        step += 1

        # Update the main context with the new positions
        context.setPositions(aux_context.getState(getPositions=True).getPositions())

        logger.info("# Switching back to the initial platform")

    if step < n_steps:
        cgmin_compute(context, step, n_steps, None, zero_mass_particles)

    if outcoor is not None:
        # Write minimized coordinates
        logger.info(f'# Writing minimized coordinates to "{outcoor}"')

        state = context.getState(getPositions=True)
        pos = state.getPositions(asNumpy=True).value_in_unit(unit.angstrom)
        mol = Molecule().empty(pos.shape[0])
        mol.coords = pos.astype(np.float32).copy()[:, :, None]
        mol.write(outcoor)

    logger.info("# Completed minimization!")
