# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import openmm.unit as unit
import openmm as mm
import numpy as np
import logging

logger = logging.getLogger("acemd")


def parse_setpoint(setpoint, timestep):
    if isinstance(setpoint, str):
        pieces = setpoint.split("@")
        if len(pieces) != 2:
            raise ValueError(
                f"Setpoint {setpoint} is not in the correct format. It should be `k@time`. k must be in kcal/mol/A^2 "
                "and time can be either just a number for timestep like `50000` or in us, ns, ps, or fs like `100ns`."
            )
        k = float(pieces[0])
        time = pieces[1]
    elif isinstance(setpoint, dict):
        k = setpoint["k"]
        time = setpoint["time"]
    else:
        raise ValueError(f"Setpoint {setpoint} is not in the correct format.")

    if time.endswith("us"):
        step = float(time.replace("us", "")) * 1e9
    elif time.endswith("ns"):
        step = float(time.replace("ns", "")) * 1e6
    elif time.endswith("ps"):
        step = float(time.replace("ps", "")) * 1e3
    elif time.endswith("fs"):
        step = float(time.replace("fs", ""))
    else:
        return int(time), k
    return int(step / timestep), k


def parse_setpoints(_setpoints, timestep):
    setpoints = [parse_setpoint(x, timestep) for x in _setpoints]

    # Check for monotonically increasing setpoints
    for i in range(len(setpoints) - 1):
        if setpoints[i][0] >= setpoints[i + 1][0]:
            raise ValueError(
                f"Setpoint {_setpoints[i]} is at timestep {setpoints[i][0]} "
                f"and setpoint {_setpoints[i+1]} is at timestep {setpoints[i+1][0]}."
                " The setpoints must be in increasing order."
            )

    # Check if the first setpoint is at 0 step. Else start from k=0
    if setpoints[0][0] != 0:
        setpoints = [(0, 0)] + setpoints

    return setpoints


class PositionalRestraint:
    _valid_keys = set(
        (
            "sel",
            "axes",
            "fbwidth",
            "fbcenter",
            "fbcenteroffset",
            "setpoints",
            "legacy",
            "type",
        )
    )

    def __init__(
        self,
        sel,
        axes="xyz",
        fb_width=None,
        fb_center=None,
        fb_center_offset=None,
        setpoints=None,
        legacy=False,
    ):
        self.sel = sel
        self.axes = axes

        self.fb_width = fb_width
        if self.fb_width is not None:
            if isinstance(self.fb_width, (int, float)):
                self.fb_width = [self.fb_width] * 3
            elif isinstance(self.fb_width, (list, tuple)) and len(self.fb_width) == 1:
                self.fb_width = self.fb_width * 3

            if "x" not in self.axes:
                self.fb_width[0] = 0
            if "y" not in self.axes:
                self.fb_width[1] = 0
            if "z" not in self.axes:
                self.fb_width[2] = 0
            self.fb_width = np.array(self.fb_width)

        self.fb_center = fb_center
        if isinstance(self.fb_center, (list, tuple)):
            self.fb_center = np.array(self.fb_center)
        self.fb_center_offset = np.array([0, 0, 0])
        if fb_center_offset is not None:
            self.fb_center_offset = np.array(fb_center_offset)
        self.setpoints = setpoints
        self.legacy = legacy

    @staticmethod
    def from_restraint_str(restraint_str):
        import shlex

        pieces = shlex.split(restraint_str)
        pieces = pieces[1:]
        sel = pieces[0]
        axes = "xyz"
        fb_width = None
        fb_center = None
        for j in range(1, len(pieces), 2):
            if pieces[j].lower() == "axes":
                axes = pieces[j + 1].lower()
            if pieces[j].lower() == "width":
                fb_width = [float(x) for x in pieces[j + 1].split()]
            if pieces[j].lower() == "setpoints":
                setpoints = pieces[j + 1 :]
            if pieces[j].lower() in ("fbcentre", "fbcenter"):
                fb_center = [float(x) for x in pieces[j + 1].split()]
            if pieces[j].lower() in ("fbcentresel", "fbcentersel"):
                fb_center = pieces[j + 1]

        return PositionalRestraint(
            sel, axes, fb_width, fb_center, setpoints=setpoints, legacy=True
        )

    @staticmethod
    def from_restraint_dict(restraint_dict):
        restraint_dict_lower = {k.lower(): v for k, v in restraint_dict.items()}

        extra_keys = set(restraint_dict_lower.keys()) - PositionalRestraint._valid_keys
        if len(extra_keys) > 0:
            raise ValueError(
                f"Restraint dictionary {restraint_dict} contains invalid keys: {extra_keys}. Valid keys are {PositionalRestraint._valid_keys}."
            )

        return PositionalRestraint(
            restraint_dict_lower["sel"],
            restraint_dict_lower.get("axes", "xyz"),
            restraint_dict_lower.get("fbwidth", None),
            restraint_dict_lower.get("fbcenter", None),
            restraint_dict_lower.get("fbcenteroffset", None),
            restraint_dict_lower.get("setpoints", []),
        )

    @staticmethod
    def parse_restraint(restraint):
        if isinstance(restraint, str):
            return PositionalRestraint.from_restraint_str(restraint)
        elif isinstance(restraint, dict):
            return PositionalRestraint.from_restraint_dict(restraint)
        else:
            raise ValueError(f"Restraint {restraint} is not in the correct format.")

    def to_dict(self):
        _dict = {
            "type": "positionalRestraint",
            "sel": self.sel,
            "axes": self.axes,
        }
        if self.fb_width is not None:
            _dict["fbwidth"] = self.fb_width.tolist()
        if self.fb_center is not None:
            _dict["fbcenter"] = (
                self.fb_center
                if isinstance(self.fb_center, str)
                else self.fb_center.tolist()
            )
        if self.fb_center_offset is not None and not np.all(self.fb_center_offset == 0):
            _dict["fbcenteroffset"] = self.fb_center_offset.tolist()
        if isinstance(self.fb_center, str) and self.legacy:
            _dict["legacy"] = self.legacy
        _dict["setpoints"] = self.setpoints
        return _dict

    def setupForce(self, idx, mol, fbrefmol, timestep, directory):
        import os

        # Parse the setpoints
        self.setpoints = parse_setpoints(self.setpoints, timestep)

        atomidx = mol.atomselect(self.sel, indexes=True, guessBonds=False)
        with open(os.path.join(directory, f"restraint_{idx}.sel"), "w") as f:
            f.write(f'# Selection: "{self.sel}"\n')
            f.write(f"# Number of atoms: {len(atomidx)}\n")
            f.write("# Atom indices (0-based)\n")
            f.write(" ".join([str(x) for x in atomidx]))

        start_k = self.setpoints[0][1] * unit.kilocalories_per_mole / unit.angstrom**2
        start_k = start_k.value_in_unit(unit.kilojoule_per_mole / unit.nanometer**2)

        if self.legacy and isinstance(self.fb_center, str):
            self.fb_center = fbrefmol.getCenter(sel=atomidx, com=True)

        if self.fb_width is not None:
            if any(np.array(self.fb_width) > mol.box[:, 0]):
                raise RuntimeError(
                    f"Restraint {idx} width {self.fb_width} A is larger than the box size {mol.box[:, 0]} A."
                )

        if self.fb_center is None:
            ff = _restrain_atoms_to_points(
                self.axes, idx, self.fb_width, atomidx, start_k, fbrefmol
            )
        elif isinstance(self.fb_center, str):
            ff = _restrain_group_to_com(
                self.axes,
                idx,
                self.fb_width,
                mol.atomselect(self.fb_center, indexes=True, guessBonds=False),
                atomidx,
                mol.masses,
                start_k,
                self.fb_center_offset,
            )
        elif isinstance(self.fb_center, (list, tuple, np.ndarray)):
            ff = _restrain_group_to_point(
                self.axes,
                idx,
                self.fb_width,
                atomidx,
                start_k,
                self.fb_center,
                fbrefmol,
                self.fb_center_offset,
            )
        # elif rr.rtype == "com":
        #     ff = _restraint_com_to_point(
        #         rr.axes,
        #         i,
        #         rr.fb_width,
        #         atomidx,
        #         mol.masses,
        #         start_k,
        #         rr.fb_center,
        #         rr.fb_center_offset,
        #     )
        else:
            raise ValueError(
                f"Restraint {self.to_dict()} is not in the correct format."
            )

        logger.info(f"#   External force: {idx}")
        logger.info(f"#     Type: {self.__class__.__name__}")
        logger.info(f'#     Atom selection: "{self.sel}"')
        logger.info(f"#     Axes: {self.axes}")
        if self.fb_width is not None:
            logger.info(
                f"#     FB width: [{', '.join(f'{x:.2f}' for x in self.fb_width)}] Å"
            )
        if self.fb_center is not None:
            logger.info(f"#     FB center: {self.fb_center}")
        if self.fb_center_offset is not None and not np.all(self.fb_center_offset == 0):
            logger.info(
                f"#     FB center offset: [{', '.join(f'{x:.2f}' for x in self.fb_center_offset)}] Å"
            )
        logger.info(f"#     Number of atoms: {len(atomidx)}")
        logger.info("#     Setpoints")
        for k, setp in enumerate(self.setpoints):
            logger.info(f"#       {k} {setp[1]:12.2f} kcal/mol/Å^2 @ step {setp[0]}")
        return ff


def get_force_str(axes, i, x1, x2, y1, y2, z1, z2, center_offset, distfun):
    forcestr = ""
    if "x" in axes:
        forcestr += "(step(dist_x) * dist_x)^2"
    if "y" in axes:
        if len(forcestr) > 0:
            forcestr += " + "
        forcestr += "(step(dist_y) * dist_y)^2"
    if "z" in axes:
        if len(forcestr) > 0:
            forcestr += " + "
        forcestr += "(step(dist_z) * dist_z)^2"

    co = center_offset / 10  # Convert offset from A to nm
    forcestr = f"k{i} * ( {forcestr} )"
    if "x" in axes:
        if "+x" in axes:
            forcestr += f"; dist_x = {x2} - ({x1} + {co[0]}) - wx0{i}"
        elif "-x" in axes:
            forcestr += f"; dist_x = ({x1} + {co[0]}) - {x2} - wx0{i}"
        else:
            forcestr += (
                f"; dist_x = {distfun}({x2}, 0, 0, ({x1} + {co[0]}), 0, 0) - wx0{i}"
            )
    if "y" in axes:
        if "+y" in axes:
            forcestr += f"; dist_y = {y2} - ({y1} + {co[1]}) - wy0{i}"
        elif "-y" in axes:
            forcestr += f"; dist_y = ({y1} + {co[1]}) - {y2} - wy0{i}"
        else:
            forcestr += (
                f"; dist_y = {distfun}(0, {y2}, 0, 0, ({y1} + {co[1]}), 0) - wy0{i}"
            )
    if "z" in axes:
        if "+z" in axes:
            forcestr += f"; dist_z = {z2} - ({z1} + {co[2]}) - wz0{i}"
        elif "-z" in axes:
            forcestr += f"; dist_z = ({z1} + {co[2]}) - {z2} - wz0{i}"
        else:
            forcestr += (
                f"; dist_z = {distfun}(0, 0, {z2}, 0, 0, ({z1} + {co[2]})) - wz0{i}"
            )

    return forcestr


def _restrain_atoms_to_points(axes, i, width, sel_idx, start_k, fbrefmol):
    forcestr = get_force_str(
        axes,
        i,
        f"x0{i}",
        "x",
        f"y0{i}",
        "y",
        f"z0{i}",
        "z",
        np.zeros(3),
        "periodicdistance",
    )
    ff = mm.CustomExternalForce(forcestr)
    ff.addGlobalParameter(f"k{i}", start_k)

    ff.addPerParticleParameter(f"x0{i}")
    ff.addPerParticleParameter(f"y0{i}")
    ff.addPerParticleParameter(f"z0{i}")
    if width is None:
        width = [0, 0, 0]

    ff.addGlobalParameter(f"wx0{i}", width[0] / 2 / 10)
    ff.addGlobalParameter(f"wy0{i}", width[1] / 2 / 10)
    ff.addGlobalParameter(f"wz0{i}", width[2] / 2 / 10)

    for idx in sel_idx:
        params = fbrefmol.coords[idx, :, 0] / 10  # convert to nm
        ff.addParticle(idx, params.tolist())

    return ff


def _restrain_group_to_point(
    axes, i, width, sel_idx, start_k, fb_center, fbrefmol, fb_center_offset
):
    forcestr = get_force_str(
        axes,
        i,
        f"x0{i}",
        "x",
        f"y0{i}",
        "y",
        f"z0{i}",
        "z",
        fb_center_offset,
        "periodicdistance",
    )
    ff = mm.CustomExternalForce(forcestr)

    ff.addGlobalParameter(f"k{i}", start_k)
    ff.addGlobalParameter(f"x0{i}", fb_center[0] / 10)
    ff.addGlobalParameter(f"y0{i}", fb_center[1] / 10)
    ff.addGlobalParameter(f"z0{i}", fb_center[2] / 10)
    if width is None:  # Include all atoms in the flat-bottom box
        width = np.ptp(fbrefmol.coords[sel_idx, :, 0], axis=0)
    ff.addGlobalParameter(f"wx0{i}", width[0] / 2 / 10)
    ff.addGlobalParameter(f"wy0{i}", width[1] / 2 / 10)
    ff.addGlobalParameter(f"wz0{i}", width[2] / 2 / 10)

    for idx in sel_idx:
        ff.addParticle(idx)

    return ff


def _restrain_group_to_com(
    axes, i, width, fbcenter_idx, sel_idx, masses, start_k, fb_center_offset
):
    forcestr = get_force_str(
        axes, i, "x1", "x2", "y1", "y2", "z1", "z2", fb_center_offset, "pointdistance"
    )
    ff = mm.CustomCentroidBondForce(2, forcestr)

    if np.sum(masses[fbcenter_idx]) == 0:
        raise RuntimeError(
            "All atoms in the flat-bottom center selection have zero mass."
        )
    g0 = ff.addGroup(fbcenter_idx, masses[fbcenter_idx])
    for idx in sel_idx:
        gi = ff.addGroup([idx], [masses[idx]])
        ff.addBond([g0, gi])

    ff.addGlobalParameter(f"k{i}", start_k)
    if f"wx0{i}" in forcestr:
        ff.addGlobalParameter(f"wx0{i}", width[0] / 2 / 10)
    if f"wy0{i}" in forcestr:
        ff.addGlobalParameter(f"wy0{i}", width[1] / 2 / 10)
    if f"wz0{i}" in forcestr:
        ff.addGlobalParameter(f"wz0{i}", width[2] / 2 / 10)

    ff.setUsesPeriodicBoundaryConditions(True)
    return ff


def _restraint_com_to_point(
    axes, i, width, sel_idx, masses, start_k, fb_center, fb_center_offset
):
    # TODO: would be good to check that the COM selection is a single molecule
    forcestr = get_force_str(
        axes,
        i,
        f"x0{i}",
        "x1",
        f"y0{i}",
        "y1",
        f"z0{i}",
        "z1",
        fb_center_offset,
        "pointdistance",
    )
    ff = mm.CustomCentroidBondForce(1, forcestr)
    g0 = ff.addGroup(sel_idx, masses[sel_idx])
    ff.addBond([g0])

    ff.addGlobalParameter(f"k{i}", start_k)
    ff.addGlobalParameter(f"wx0{i}", width[0] / 2 / 10)
    ff.addGlobalParameter(f"wy0{i}", width[1] / 2 / 10)
    ff.addGlobalParameter(f"wz0{i}", width[2] / 2 / 10)
    ff.addGlobalParameter(f"x0{i}", fb_center[0] / 10)
    ff.addGlobalParameter(f"y0{i}", fb_center[1] / 10)
    ff.addGlobalParameter(f"z0{i}", fb_center[2] / 10)

    ff.setUsesPeriodicBoundaryConditions(True)
    return ff


def setup_extforces(mol, restraints, fbrefcoor, system, timestep, directory):
    from acemd.acemd import FGROUPS

    fbrefmol = mol
    if fbrefcoor is not None:
        fbrefmol = mol.copy()
        fbrefmol.read(fbrefcoor)
        if any(fbrefmol.masses == 0):
            raise RuntimeError(
                "Cannot calculate center of mass for flat-bottom potential since input structures have no masses."
            )

    i = 0
    logger.info("#")
    logger.info("# External forces")
    restrs = []
    # If any of the restraints are non-periodic the coordinates need to start from [0, 0, 0]
    nonperiodic_restraints = False
    for rr in restraints:
        ff = rr.setupForce(i, mol, fbrefmol, timestep, directory)

        if len(restraints) + FGROUPS.EXTERNAL.value + 1 <= 31:
            # OpenMM allows only 31 force groups. Add a plus 1 to signify individual groups per restraint
            ff.setForceGroup(FGROUPS.EXTERNAL.value + i + 1)
        else:
            # If we have more than 31 restraints, we need to use the default force group
            ff.setForceGroup(FGROUPS.EXTERNAL.value)

        system.addForce(ff)
        restrs.append((f"k{i}", rr.setpoints))

        if "+" in rr.axes or "-" in rr.axes:
            nonperiodic_restraints = True

        i += 1
    return restrs, nonperiodic_restraints


def update_restraints(simulation, restraints, step, log=False):
    # increment the location of the CV based on the pulling velocity
    curr_vals = []
    for i, (k_var, setpoints) in enumerate(restraints):
        # Interpolate the k values between setpoints. After the last setpoint, keep the last k value
        for j in range(len(setpoints) - 1):
            if setpoints[j][0] <= step < setpoints[j + 1][0]:
                current_k = setpoints[j][1] + (
                    setpoints[j + 1][1] - setpoints[j][1]
                ) * (step - setpoints[j][0]) / (setpoints[j + 1][0] - setpoints[j][0])
                break
        else:
            current_k = setpoints[-1][1]

        current_k_val = current_k * unit.kilocalories_per_mole / unit.angstrom**2
        simulation.context.setParameter(
            k_var,
            current_k_val.value_in_unit(unit.kilojoule_per_mole / unit.nanometer**2),
        )
        if log:
            logger.info(f"# Restraint {i}: k = {current_k:.2f} kcal/mol/A^2")
        # ff.updateParametersInContext(simulation.context)
        curr_vals.append(current_k)
    return curr_vals
