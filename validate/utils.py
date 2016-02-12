from collections import OrderedDict
import os
from subprocess import PIPE, Popen

import parmed.unit as u

from validate.exceptions import ValidateError

canonical_energy_names = [
    'bond', 'angle', 'urey_bradley', 'dihedral', 'improper', 'rb_torsion',
    'cmap', 'nonbonded', 'vdw', 'vdw-14', 'coulomb', 'coulomb-14', 'potential']

gromacs_to_canonical = {
    'Bond': 'bond',
    'Angle': 'angle',
    'Proper Dih.': 'dihedral',
    'Ryckaert-Bell.': 'rb_torsion',
    'Improper Dih.': 'improper',
    'LJ (SR)': 'vdw',
    'LJ-14': 'vdw-14',
    'Disper. corr.': 'vdw',
    'Coulomb (SR)': 'coulomb',
    'Coulomb-14': 'coulomb-14',
    'Coul. recip.': 'coulomb',
    'Potential': 'potential'
}

amber_to_canonical = {
    'BOND': 'bond',
    'ANGLE': 'angle',
    'DIHED': 'dihedral',
    'VDWAALS': 'vdw',
    '1-4 VDW': 'vdw-14',
    'EEL': 'coulomb',
    '1-4 EEL': 'coulomb-14',
    'ENERGY': 'potential'
}

key_converters = {'gromacs': gromacs_to_canonical,
                  'amber': amber_to_canonical}


def canonicalize_energy_names(energy_dict, engine):
    normalized = OrderedDict.fromkeys(canonical_energy_names,
                                      0 * u.kilojoules_per_mole)
    canonical_keys = key_converters[engine]
    for key, energy in energy_dict.items():
        canonical_key = canonical_keys.get(key)
        if not canonical_key:
            continue
        normalized[canonical_key] += energy.in_units_of(u.kilojoules_per_mole)
    normalized['nonbonded'] = (normalized['vdw'] + normalized['coulomb'] +
                               normalized['vdw-14'] + normalized['coulomb-14'])
    return normalized


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def run_subprocess(cmd, stdout_path, stderr_path, stdin=None):
    """Run a subprocess and log the stdout and stderr. """
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    out, err = proc.communicate(input=stdin)
    with open(stdout_path, 'a') as stdout, open(stderr_path, 'a') as stderr:
        stdout.write(out)
        stderr.write(err)
        if proc.returncode != 0:
            err_msg = ('Subprocess with following command failed: \n\n{:s}\n\n '
                       'See {:s}'.format(' '.join(cmd), stderr_path))
            stderr.write(err_msg)
            raise ValidateError(err_msg)
    return proc


def energy_diff(e_in, e_out):
    """Return the energy difference between two energy dicts in a new dict.

    Parameters
    ----------
    e_in : OrderedDict
    e_out : OrderedDict

    Returns
    -------
    diff : OrderedDict

    """
    # TODO: Look into creating an `EnergyDict` class.
    diff = OrderedDict()
    for term in e_in:
        if term not in e_out:
            raise ValidateError('"{}" energy present in input but not output.'.format(term))
        diff[term] = e_out[term] - e_in[term]
    return diff
