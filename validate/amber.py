from collections import OrderedDict
import os

import parmed.unit as u

from validate.utils import run_subprocess, normalize_energy_keys


def amb_structure_energy(structure, output_dir, mdin, file_name='output'):
    """Write a structure out to a .prmtop/.inpcrd pair and evaluate its energy.

    Parameters
    ----------
    structure : pmd.Structure
        The ParmEd structure to write and evaluate.
    mdin : str
        Path to a .mdp file to use when evaluating the energy.
    output_dir : str
        The directory to write the .top and .gro files in.
    file_name : str
        The base name of the .top and .gro files.

    Returns
    -------
    output_energy : OrderedDict

    """
    crd_out = os.path.join(output_dir, '{}.inpcrd'.format(file_name))
    prm_out = os.path.join(output_dir, '{}.prmtop'.format(file_name))
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

    sander = ['sander']

    # Run grompp.
    sander.extend(['-i', mdin,
                   '-o', mdout,
                   '-p', prm,
                   '-c', crd,
                   '-o', mdout])
    proc = run_subprocess(sander, stdout_path, stderr_path)
    if proc.returncode != 0:
        raise RuntimeError('sander failed. See %s' % stderr_path)

    # energy = _parse_energy_xvg(ener_xvg)
    energy = OrderedDict()
    return normalize_energy_keys(energy)
