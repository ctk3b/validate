from collections import OrderedDict
import os

import parmed.unit as u

from validate.utils import (run_subprocess, canonicalize_energy_names,
                            amber_to_canonical)


def structure_energy(structure, mdin, file_name='output'):
    """Write a structure out to a .prmtop/.inpcrd pair and evaluate its energy.

    Parameters
    ----------
    structure : pmd.Structure
        The ParmEd structure to write and evaluate.
    mdin : str
        Path to a .mdp file to use when evaluating the energy.
    file_name : str
        The base name of the .top and .gro files.

    Returns
    -------
    output_energy : OrderedDict

    """
    crd_out = '{}.inpcrd'.format(file_name)
    prm_out = '{}.prmtop'.format(file_name)
    structure.save(crd_out, overwrite=True)
    structure.save(prm_out, overwrite=True)
    return energy(prm_out, crd_out, mdin)


def energy(prm, crd, mdin):
    """Evaluate the energy of a .prmtop, .inpcrd and .in file combination.

    Parameters
    ----------
    prm : str
    crd : str
    mdin : str

    Returns
    -------
    energies : OrderedDict

    """
    mdin = os.path.abspath(mdin)

    directory, _ = os.path.split(os.path.abspath(prm))

    mdout = ''
    stdout_path = os.path.join(directory, 'amber_stdout.txt')
    stderr_path = os.path.join(directory, 'amber_stderr.txt')


    # Run sander.
    sander = ['sander']
    sander.extend(['-i', mdin,
                   '-O', mdout,
                   '-p', prm,
                   '-c', crd,
                   '-O', mdout])
    run_subprocess(sander, stdout_path, stderr_path)

    # TODO: Fix mdout filenaming.
    energy = _parse_energy_mdout(mdout or 'mdout')
    return canonicalize_energy_names(energy, 'amber')


def _parse_energy_mdout(mdout):
    """Parse mdout file to extract energy terms into a dict. """
    energy = OrderedDict.fromkeys(amber_to_canonical,
                                  0 * u.kilocalories_per_mole)
    ranges = [[1, 24], [26, 49], [51, 77]]  # Spacings between energy terms.
    # TODO: Could probably be replaced by a more elegant regex.
    with open(mdout) as f:
        reading = False
        for line in f:
            if 'NSTEP' in line:
                reading = True
                # Get the potential energy from the next line.
                potential = float(next(f).split()[1]) * u.kilocalories_per_mole
                energy['ENERGY'] = potential
                next(f)  # Skip blank line after summary.
            elif not reading or not line.strip():
                continue
            elif '=' in line:
                for r in ranges:
                    term = line[r[0]:r[1]]
                    energy_type, value = term.split('=')
                    energy[energy_type] = float(value) * u.kilocalories_per_mole
            else:
                break
    return energy
