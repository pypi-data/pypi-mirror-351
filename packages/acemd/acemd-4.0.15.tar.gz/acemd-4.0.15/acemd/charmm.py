# (c) 2015-2024 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from pathlib import Path
from moleculekit.molecule import Molecule
import os

HEADERS = {
    "^ATOMS": """ """,
    "^BOND": """!
!V(bond) = Kb(b - b0)**2
!
!Kb: kcal/mole/A**2
!b0: A
!
!atom type Kb          b0
!
""",
    "^ANGL": """!
!V(angle) = Ktheta(Theta - Theta0)**2
!
!V(Urey-Bradley) = Kub(S - S0)**2
!
!Ktheta: kcal/mole/rad**2
!Theta0: degrees
!Kub: kcal/mole/A**2 (Urey-Bradley)
!S0: A
!
!atom types     Ktheta    Theta0   Kub     S0
!
""",
    "^DIHE": """!
!V(dihedral) = Kchi(1 + cos(n(chi) - delta))
!
!Kchi: kcal/mole
!n: multiplicity
!delta: degrees
!
!atom types             Kchi    n   delta
!
""",
    "^IMPR": """!
!V(improper) = Kpsi(psi - psi0)**2
!
!Kpsi: kcal/mole/rad**2
!psi0: degrees
!note that the second column of numbers (0) is ignored
!
!atom types           Kpsi                   psi0
!
""",
    "^CMAP": """! 2D grid correction data. 
! Finalfix3, Feig/Best/MacKerell 2010

! Jing Huang/Alex MacKerell adjustments to correct for 
! oversampling of alpha L conformation.  2016/1
""",
    "^NONB": """cutnb 14.0 ctofnb 12.0 ctonnb 10.0 eps 1.0 e14fac 1.0 wmin 1.5 
                !adm jr., 5/08/91, suggested cutoff scheme
!
!V(Lennard-Jones) = Eps,i,j[(Rmin,i,j/ri,j)**12 - 2(Rmin,i,j/ri,j)**6]
!
!epsilon: kcal/mole, Eps,i,j = sqrt(eps,i * eps,j)
!Rmin/2: A, Rmin,i,j = Rmin/2,i + Rmin/2,j
!
!atom  ignored    epsilon      Rmin/2   ignored   eps,1-4       Rmin/2,1-4
!
""",
    "^NBON": """cutnb 14.0 ctofnb 12.0 ctonnb 10.0 eps 1.0 e14fac 1.0 wmin 1.5 
                !adm jr., 5/08/91, suggested cutoff scheme
!
!V(Lennard-Jones) = Eps,i,j[(Rmin,i,j/ri,j)**12 - 2(Rmin,i,j/ri,j)**6]
!
!epsilon: kcal/mole, Eps,i,j = sqrt(eps,i * eps,j)
!Rmin/2: A, Rmin,i,j = Rmin/2,i + Rmin/2,j
!
!atom  ignored    epsilon      Rmin/2   ignored   eps,1-4       Rmin/2,1-4
!
""",
    "^HBON": """! READ PARAM APPEND CARD
! to append hbond parameters from the file: par_hbond.inp
""",
    "^NBFI": """!               Emin        Rmin
!            (kcal/mol)     (A)
!
""",
}


def cleanup_charmm_prm(structure, parameters: Path, loader="openmm", outfile=None):
    import tempfile
    import re

    def _is_number(x):
        try:
            float(x)
            return True
        except ValueError:
            return False

    sections = (
        "^ATOMS",
        "^BOND",
        "^ANGL",
        "^DIHE",
        "^THET",
        "^IMPR",
        "^IMPH",
        "^CMAP",
        "^NBON",
        "^NONB",
        "^NBFI",
        "^HBON",
    )

    mol = Molecule(structure)
    atom_masses = {
        at.upper(): mol.masses[mol.atomtype == at][0] for at in set(mol.atomtype)
    }
    atom_masses["X"] = 0

    in_section = None

    with open(parameters, encoding="utf-8") as old_prm, tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", suffix=".prm", delete=outfile is None
    ) as new_prm:
        new_prm.write("ATOMS\n")
        for at in atom_masses:
            new_prm.write(f"MASS  -1  {at} {atom_masses[at]:.5f}\n")
        new_prm.write("\n")

        wrote_newline = False
        for line in old_prm.readlines():
            line = line.strip()
            if line.startswith("*") or line.startswith("!"):
                continue
            if line.startswith("ATOMS") or line.startswith("MASS"):
                continue

            if len(line) == 0:
                if not wrote_newline:
                    new_prm.write("\n")
                wrote_newline = True
                continue

            # Get stuff before inline comments
            pre_comment = line.split("!")[0].strip()
            if len(pre_comment) == 0:
                continue

            is_section = [re.search(s, pre_comment) is not None for s in sections]
            if any(is_section):
                new_prm.write(f"\n{line}\n")
                new_prm.write(HEADERS[sections[is_section.index(True)]])
                in_section = sections[is_section.index(True)]
                wrote_newline = False
                continue

            non_numbers = [
                pp.strip() for pp in pre_comment.split() if not _is_number(pp)
            ]
            types_in_system = [pp.upper() in atom_masses for pp in non_numbers]
            type_line = len(types_in_system)
            if type_line and not all(types_in_system):
                # print("Skipped", line, "PIECES", pieces, pieces1)
                if in_section == "^CMAP":
                    skip_cmap_terms = True
                continue
            if type_line and all(types_in_system) and in_section == "^CMAP":
                skip_cmap_terms = False
            if in_section == "^CMAP" and skip_cmap_terms and not type_line:
                continue
            new_prm.write(f"{line}\n")
            wrote_newline = False
        new_prm.flush()
        if loader == "parmed":
            import parmed

            parameters = parmed.charmm.CharmmParameterSet(new_prm.name)
        elif loader == "openmm":
            from openmm.app.charmmparameterset import CharmmParameterSet

            parameters = CharmmParameterSet(new_prm.name)
    if outfile is not None:
        os.rename(new_prm.name, outfile)
    return parameters
