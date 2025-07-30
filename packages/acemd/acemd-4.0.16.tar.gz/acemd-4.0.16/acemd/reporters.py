# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import openmm.app as app
import openmm.unit as unit
from openmm.app import XTCFile, DCDFile
import time
import os
import logging

logger = logging.getLogger("acemd")


class SpeedLogger:
    def __init__(self, simulation, nsteps):
        self.simulation = simulation
        self.nsteps = nsteps
        self.start_step = simulation.currentStep
        self.SEC_IN_DAY = 24 * 60 * 60
        self._initialized = False

    def _initialize(self):
        self.init_real_time = time.time()
        self.prev_real_time = self.init_real_time
        self.init_sim_time = (
            self.simulation.context.getState().getTime().value_in_unit(unit.nanosecond)
        )
        self.prev_sim_time = self.init_sim_time
        self._initialized = True

    def step(self, curr_step):
        import datetime

        if not self._initialized:
            self._initialize()

        if curr_step == self.start_step:
            return 0, 0, 0, datetime.datetime.now(), datetime.timedelta(0)

        # Calculate simulation speed, mean and current
        curr_real_time = time.time()

        simtime = self.simulation.context.getState().getTime()
        curr_sim_time = simtime.value_in_unit(unit.nanosecond)
        mean_speed = (curr_sim_time - self.init_sim_time) / (
            (curr_real_time - self.init_real_time) / self.SEC_IN_DAY
        )
        curr_speed = (curr_sim_time - self.prev_sim_time) / (
            (curr_real_time - self.prev_real_time) / self.SEC_IN_DAY
        )

        # Calculate completed percentage and ETA of simulation
        progress = curr_step / self.nsteps
        time_per_step = (curr_real_time - self.init_real_time) / (
            curr_step - self.start_step
        )
        remaining = (self.nsteps - curr_step) * time_per_step
        completion_date = datetime.datetime.fromtimestamp(curr_real_time + remaining)
        remaining_time = completion_date - datetime.datetime.now()

        self.prev_real_time = curr_real_time
        self.prev_sim_time = curr_sim_time
        return (
            curr_speed,
            mean_speed,
            progress,
            completion_date,
            max(remaining_time, datetime.timedelta(0)),
        )


class LoggingReporter:
    """LoggingReporter prints MD logs

    To use it, create a LoggingReporter, then add it to the Simulation's list of reporters.
    """

    field_widths = {
        "Step": 10,
        "Time (ns)": 8,
        "Progress (%)": 5,
        "Mean speed (ns/day)": 8,
        "Current speed (ns/day)": 8,
        "Remaining time": 9,
        "Completion date": 15,
        "Temperature (K)": 7,
        "Volume (A^3)": 10,
        "Density (g/cm^3)": 6,
        "k0": 6,
        "k1": 6,
        "k2": 6,
        "k3": 6,
        "k4": 6,
    }
    aliases = {
        "Time (ns)": "Time",
        "Progress (%)": "Compl",
        "Mean speed (ns/day)": "Mean Sp",
        "Current speed (ns/day)": "Curr Sp",
        "Remaining time": "ETA",
        "Temperature (K)": "Temp",
        "Volume (A^3)": "Volume",
        "Density (g/cm^3)": "Dens",
    }
    aliases2 = {  # Second line of header aliases
        "Time (ns)": "ns",
        "Progress (%)": "%",
        "Temperature (K)": "K",
        "Mean speed (ns/day)": "ns/day",
        "Current speed (ns/day)": "ns/day",
        "Remaining time": "H:MM:SS",
        "Density (g/cm^3)": "g/cm^3",
        "Volume (A^3)": "A^3",
        "Completion date": "DD/MM HH:MM:SS",
    }

    def __init__(
        self, logfile, simulation, totalmass, reportInterval, restraints, nsteps
    ):
        """Create a LoggingReporter.

        Parameters
        ----------
        reportInterval : int
            The interval (in time steps) at which to write frames
        """
        from acemd.acemd import _get_dof

        self._simulation = simulation
        self._reportInterval = reportInterval
        self._dof = _get_dof(simulation.system)
        self._totalmass = totalmass
        self._restraints = restraints
        self.speedl = SpeedLogger(simulation, nsteps)
        self._logfile = logfile
        self._initialized = False
        self._header = None

    def _initialize(self):
        from acemd.acemd import get_energy_decomposition

        # Print header
        header = "Step,Time (ns),Progress (%),Mean speed (ns/day),Current speed (ns/day),Remaining time,Completion date,Temperature (K),Volume (A^3),Density (g/cm^3),"
        energy_terms = get_energy_decomposition(
            self._simulation.context, self._simulation.context.getState(getEnergy=True)
        )
        header += ",".join(energy_terms.keys())
        if len(self._restraints) > 0:
            header += "," + ",".join([f"k{i}" for i in range(len(self._restraints))])

        pieces = header.split(",")
        formatted = ""
        for piece in pieces:
            formatted += f"{self.aliases.get(piece, piece): >{self.field_widths.get(piece, 11)}} "
        logger.info(formatted)
        formatted = ""
        for piece in pieces:
            formatted += (
                f"{self.aliases2.get(piece, ''): >{self.field_widths.get(piece, 11)}} "
            )
        logger.info(formatted)

        # Only write header if file does not exist
        if not os.path.exists(self._logfile):
            with open(self._logfile, "w") as f:
                f.write(header + "\n")

        self.speedl._initialize()
        self._initialized = True
        self._header = pieces

    def describeNextReport(self, simulation):
        """Get information about the next report this object will generate.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for

        Returns
        -------
        tuple
            A six element tuple. The first element is the number of steps
            until the next report. The next four elements specify whether
            that report will require positions, velocities, forces, and
            energies respectively.  The final element specifies whether
            positions should be wrapped to lie in a single periodic box.
        """
        if not self._initialized:
            self._initialize()

        steps = self._reportInterval - (simulation.currentStep % self._reportInterval)
        pos = False
        vel = False
        forces = False
        energies = True
        periodic = False
        return (steps, pos, vel, forces, energies, periodic)

    def report(self, simulation, state):
        """Generate a report.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for
        state : State
            The current state of the simulation
        """
        from acemd.acemd import get_energy_decomposition, get_sim_properties

        if not self._initialized:
            self._initialize()

        curr_s, mean_s, progress, compl_date, remain_time = self.speedl.step(
            simulation.currentStep
        )
        energies = get_energy_decomposition(simulation.context, state)
        time, temperature, volume, density = get_sim_properties(
            simulation.context, self._totalmass, self._dof
        )
        energies_str = ",".join([f"{e:.2f}" for e in energies.values()])

        # Get restraint values

        from_units = unit.kilojoules_per_mole / unit.nanometer**2
        to_units = unit.kilocalories_per_mole / unit.angstrom**2

        curr_k = ""
        if len(self._restraints) > 0:
            curr_k = []
            for i in range(len(self._restraints)):
                k = simulation.context.getParameter(f"k{i}") * from_units
                curr_k.append(k.value_in_unit(to_units))
            curr_k = "," + ",".join([f"{k:.2f}" for k in curr_k])

        # Convert remain_time to nice format
        hours, remainder = divmod(remain_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        remain_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

        current_info = (
            f"{simulation.currentStep},{time:.2f},{progress*100:.1f},{mean_s:.2f},{curr_s:.2f},"
            f"{remain_time},{compl_date.strftime('%d/%m %H:%M:%S')},{temperature:.2f},"
            f"{volume:.2f},{density:.2f},{energies_str}{curr_k}"
        )
        pieces = current_info.split(",")
        formatted = ""
        for i, piece in enumerate(pieces):
            formatted += f"{piece: >{self.field_widths.get(self._header[i], 11)}} "
        logger.info(formatted)

        with open(self._logfile, "a") as f:
            f.write(current_info + "\n")


class CustomReporter(object):
    """CustomReporter outputs 3D properties from a Simulation to a XTC file.

    To use it, create a CustomReporter, then add it to the Simulation's list of reporters.
    """

    def __init__(
        self, file, reportInterval, property, append=False, enforcePeriodicBox=None
    ):
        """Create a CustomReporter.

        Parameters
        ----------
        file : string
            The file to write to
        reportInterval : int
            The interval (in time steps) at which to write frames
        property : str
            The property to write to the XTC file. Can be either "positions" or "forces" or "velocities"
        append : bool=False
            If True, open an existing XTC file to append to.  If False, create a new file.
        enforcePeriodicBox: bool
            Specifies whether particle positions should be translated so the center of every molecule
            lies in the same periodic box.  If None (the default), it will automatically decide whether
            to translate molecules based on whether the system being simulated uses periodic boundary
            conditions.
        """
        self._property = property
        self._reportInterval = reportInterval
        self._append = append
        self._enforcePeriodicBox = enforcePeriodicBox
        self._fileName = file
        self._writer = None

    def describeNextReport(self, simulation):
        """Get information about the next report this object will generate.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for

        Returns
        -------
        tuple
            A six element tuple. The first element is the number of steps
            until the next report. The next four elements specify whether
            that report will require positions, velocities, forces, and
            energies respectively.  The final element specifies whether
            positions should be wrapped to lie in a single periodic box.
        """
        steps = self._reportInterval - (simulation.currentStep % self._reportInterval)
        pos = self._property == "positions"
        vel = self._property == "velocities"
        forces = self._property == "forces"
        energies = False
        return (steps, pos, vel, forces, energies, self._enforcePeriodicBox)

    def report(self, simulation, state):
        """Generate a report.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for
        state : State
            The current state of the simulation
        """
        from openmm import unit
        from openmm import Vec3

        fake_box = unit.Quantity(
            value=[
                Vec3(x=-1, y=0, z=0),
                Vec3(x=0, y=-1, z=0),
                Vec3(x=0, y=0, z=-1),
            ],
            unit=unit.angstrom,
        )

        if self._writer is None:
            if self._fileName.endswith(".xtc"):
                self._writer = XTCFile(
                    self._fileName,
                    simulation.topology,
                    simulation.integrator.getStepSize(),
                    self._reportInterval,
                    self._reportInterval,
                    self._append,
                )
            elif self._fileName.endswith(".dcd"):
                mode = "wb" if not self._append else "rb+"
                self._writer = DCDFile(
                    open(self._fileName, mode),
                    simulation.topology,
                    simulation.integrator.getStepSize(),
                    self._reportInterval,
                    self._reportInterval,
                    self._append,
                )

        if self._property == "positions":
            self._writer.writeModel(
                state.getPositions(), periodicBoxVectors=state.getPeriodicBoxVectors()
            )
        if self._property == "velocities":
            vel = state.getVelocities(asNumpy=True).value_in_unit(
                unit.nanometer / unit.picosecond
            )
            PDBVELFACTOR = 20.45482706  # nm/internal --> nm/fs
            vel /= PDBVELFACTOR

            self._writer.writeModel(vel, periodicBoxVectors=fake_box)
        if self._property == "forces":
            forces = state.getForces(asNumpy=True).value_in_unit(
                unit.kilocalorie_per_mole / unit.angstrom
            )
            forces /= 10  # divide by 10 to counter the *10 inside the DCD/XTC writer
            self._writer.writeModel(forces, periodicBoxVectors=fake_box)


def _backup_file(outfile):
    import shutil

    ext = os.path.splitext(outfile)[1]

    if os.path.exists(outfile):
        i = 1
        while True:
            new_name = outfile.replace(ext, f".{i}{ext}")
            if not os.path.exists(new_name):
                shutil.move(outfile, new_name)
                break
            i += 1


def setup_reporters(
    simulation,
    directory,
    trajectoryfile,
    trajvelocityfile,
    trajforcefile,
    trajectoryperiod,
    restart,
    restart_file,
    totalmass,
    restraints,
    nsteps,
):
    output_csv = os.path.join(directory, "output.csv")
    if not restart:
        _backup_file(output_csv)

    simulation.reporters.append(
        LoggingReporter(
            output_csv,
            simulation,
            totalmass,
            trajectoryperiod,
            restraints,
            nsteps,
        )
    )

    output_trj = os.path.join(directory, trajectoryfile)
    if not restart:
        _backup_file(output_trj)

    simulation.reporters.append(
        CustomReporter(
            output_trj,
            trajectoryperiod,
            "positions",
            append=os.path.exists(output_trj),
            enforcePeriodicBox=False,
        )
    )

    simulation.reporters.append(app.CheckpointReporter(restart_file, trajectoryperiod))

    if trajvelocityfile is not None:
        if not (trajvelocityfile.endswith(".xtc") or trajvelocityfile.endswith(".dcd")):
            raise RuntimeError(
                f"Unsupported trajectory file format for {trajvelocityfile}. Only XTC and DCD are supported."
            )

        output_vel = os.path.join(directory, trajvelocityfile)
        if not restart:
            _backup_file(output_vel)

        simulation.reporters.append(
            CustomReporter(
                output_vel,
                trajectoryperiod,
                "velocities",
                append=os.path.exists(output_vel),
                enforcePeriodicBox=False,
            )
        )

    if trajforcefile is not None:
        if not (trajforcefile.endswith(".xtc") or trajforcefile.endswith(".dcd")):
            raise RuntimeError(
                f"Unsupported trajectory file format for {trajforcefile}. Only XTC and DCD are supported."
            )

        output_frc = os.path.join(directory, trajforcefile)
        if not restart:
            _backup_file(output_frc)

        simulation.reporters.append(
            CustomReporter(
                output_frc,
                trajectoryperiod,
                "forces",
                append=os.path.exists(output_frc),
                enforcePeriodicBox=False,
            )
        )
