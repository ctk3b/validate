from collections import OrderedDict
import os
from subprocess import PIPE, Popen

from validate.exceptions import ValidateError


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
    return proc


def normalize_energy_keys(energy_dict):
    return energy_dict


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
    diff = OrderedDict()
    for term in e_in:
        if term not in e_out:
            raise ValidateError('"{}" energy present in input but not output.'.format(term))
        diff[term] = e_out[term] - e_in[term]
    return diff
