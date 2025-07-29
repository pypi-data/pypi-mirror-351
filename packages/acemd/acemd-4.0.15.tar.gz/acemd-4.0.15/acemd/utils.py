import logging

logger = logging.getLogger(__name__)


def plumed_parser(fn):
    # Hack to workaround https://github.com/openmm/openmm-plumed/pull/27
    # Joins continuation lines and strips comments
    out = []
    continuing = False
    with open(fn) as f:
        for line in f:
            line = line.strip()
            if "#" in line:
                line = line[: line.find("#")]  # Strip comments
            dots = line.find("...")
            if not continuing:
                if dots == -1:
                    out.append(line)
                else:
                    out.append(line[:dots])
                    continuing = True
            else:
                if dots == -1:
                    out[-1] = out[-1] + " " + line
                else:
                    out[-1] = out[-1] + " " + line[:dots]
                    continuing = False
    return "\n".join(out)


def _draw_force(start, vec):
    assert start.ndim == 1 and vec.ndim == 1
    from moleculekit.vmdviewer import getCurrentViewer

    vmd = getCurrentViewer()
    vmd.send(
        """
    proc vmd_draw_arrow {start end} {
        # an arrow is made of a cylinder and a cone
        draw color green
        set middle [vecadd $start [vecscale 0.9 [vecsub $end $start]]]
        graphics top cylinder $start $middle radius 0.15
        graphics top cone $middle $end radius 0.25
    }
    """
    )
    vmd.send(
        "vmd_draw_arrow {{ {} }} {{ {} }}".format(
            " ".join(map(str, start)), " ".join(map(str, start + vec))
        )
    )


def view_forces(mol, forcefile, step=0, threshold=500, normalize=True, scalef=100):
    """Visualize force vectors in VMD

    Parameters
    ----------
    mol : Molecule
        The Molecule with the coordinates on which to visualize the forces
    forcefile : str
        The force file produced by ACEMD
    step : int
        The simulation step for which to show the forces and coordinates
    threshold : float
        Will only visualize forces with a magnitude above this threshold
    normalize : bool
        If set to True it will normalize the force vectors to unit length
    scalef : float
        Scaling factor by which to divide the force vectors (not used if normalize=True)
    """
    from moleculekit.molecule import Molecule
    import numpy as np

    mol.view()
    coords = mol.coords[:, :, step]
    forces = Molecule(forcefile).coords[:, :, step]
    force_mag = np.linalg.norm(forces, axis=1)

    idx = np.where(force_mag > threshold)[0]
    if len(idx) == 0:
        logger.info(f"No forces above threshold {threshold}.")
        return
    logger.info(
        f"Found {len(idx)} atoms with force magnitudes above the threshold of {threshold} kcal/mol/A. They belong to atoms with indexes {idx}"
    )

    for cc, ff in zip(coords[idx], forces[idx]):
        ff /= scalef
        if normalize:
            ff /= np.linalg.norm(ff)
        _draw_force(cc, ff)
