from collections import OrderedDict
import os

import parmed.unit as u

from validate.utils import which, run_subprocess, normalize_energy_keys


# energy terms we are ignoring
UNWANTED_ENERGY_TERMS = ['Kinetic En.', 'Total Energy', 'Temperature', 'Volume',
                         'Pressure', 'Box-X', 'Box-Y', 'Box-Z',
                         'Box-atomic_number', 'Pres. DC', 'Vir-XY', 'Vir-XX',
                         'Vir-XZ', 'Vir-YY', 'Vir-YX', 'Vir-YZ', 'Vir-ZX',
                         'Vir-ZY', 'Vir-ZZ', 'pV', 'Density', 'Enthalpy']


def gmx_structure_energy(structure, mdp, output_dir, file_name='output'):
    """Write a structure out to a .top/.gro pair and evaluate its energy.

    Parameters
    ----------
    structure : pmd.Structure
    mdp : str
        Path to a .mdp file to use when evaluating the energy.
    output_dir : str
        The directory to write the .top and .gro files in.
    file_name : str
        The base name of the .top and .gro files.

    Returns
    -------
    output_energy : OrderedDict

    """
    top_out = os.path.join(output_dir, '{}.top'.format(file_name))
    gro_out = os.path.join(output_dir, '{}.gro'.format(file_name))
    structure.save(top_out, overwrite=True)
    structure.save(gro_out, overwrite=True)
    return energy(top_out, gro_out, mdp)


def energy(top, gro, mdp):
    """Evaluate the energy of a .top, .gro and .mdp file combination.

    Parameters
    ----------
    top : str
    gro : str
    mdp : str

    Returns
    -------
    energies : OrderedDict

    """
    mdp = os.path.abspath(mdp)

    directory, _ = os.path.split(os.path.abspath(top))

    tpr = os.path.join(directory, 'topol.tpr')
    ener = os.path.join(directory, 'ener.edr')
    ener_xvg = os.path.join(directory, 'energy.xvg')
    conf = os.path.join(directory, 'confout.gro')
    mdout = os.path.join(directory, 'mdout.mdp')
    state = os.path.join(directory, 'state.cpt')
    traj = os.path.join(directory, 'traj.trr')
    log = os.path.join(directory, 'md.log')
    stdout_path = os.path.join(directory, 'gromacs_stdout.txt')
    stderr_path = os.path.join(directory, 'gromacs_stderr.txt')

    grompp, mdrun, genergy = binaries()

    # Run grompp.
    grompp.extend(['-f', mdp,
                   '-c', gro,
                   '-p', top,
                   '-o', tpr,
                   '-po', mdout,
                   '-maxwarn', '5'])
    proc = run_subprocess(grompp, stdout_path, stderr_path)
    if proc.returncode != 0:
        raise RuntimeError('grompp failed. See %s' % stderr_path)

    # Run single-point calculation with mdrun.
    mdrun.extend(['-nt', '1',
                  '-s', tpr,
                  '-o', traj,
                  '-cpo', state,
                  '-c', conf,
                  '-e', ener,
                  '-g', log])
    proc = run_subprocess(mdrun, stdout_path, stderr_path)
    if proc.returncode != 0:
        raise RuntimeError('mdrun failed. See %s' % stderr_path)

    # Extract energies using g_energy
    select = " ".join(map(str, range(1, 20))) + " 0 "
    genergy.extend(['-f', ener,
                    '-o', ener_xvg,
                    '-dp'])
    proc = run_subprocess(genergy, stdout_path, stderr_path, stdin=select)
    if proc.returncode != 0:
        raise RuntimeError('g_energy failed. See %s' % stderr_path)

    energy = _parse_energy_xvg(ener_xvg)
    energy = _group_energy_terms(energy)
    return normalize_energy_keys(energy)


def _parse_energy_xvg(energy_xvg):
    """Parse energy.xvg file to extract energy terms into a dict. """
    with open(energy_xvg) as f:
        all_lines = f.readlines()
    energy_types = [line.split('"')[1]
                    for line in all_lines
                    if line[:3] == '@ s']
    energy_values = [float(x) * u.kilojoule_per_mole
                     for x in all_lines[-1].split()[1:]]
    energy = OrderedDict(zip(energy_types, energy_values))
    return energy


def _group_energy_terms(energy):
    """Group energy terms into broader categories """
    # Discard non-energy terms.
    for group in UNWANTED_ENERGY_TERMS:
        if group in energy:
            del energy[group]

    # Dispersive energies.
    # TODO: Do buckingham energies also get dumped here?
    dispersive = ['LJ (SR)', 'LJ-14', 'Disper. corr.']
    energy['Dispersive'] = 0 * u.kilojoules_per_mole
    for group in dispersive:
        if group in energy:
            energy['Dispersive'] += energy[group]

    # Electrostatic energies.
    electrostatic = ['Coulomb (SR)', 'Coulomb-14', 'Coul. recip.']
    energy['Electrostatic'] = 0 * u.kilojoules_per_mole
    for group in electrostatic:
        if group in energy:
            energy['Electrostatic'] += energy[group]

    energy['Non-bonded'] = energy['Electrostatic'] + energy['Dispersive']

    # All the various dihedral energies.
    all_dihedrals = ['Ryckaert-Bell.', 'Proper Dih.', 'Improper Dih.']
    energy['All dihedrals'] = 0 * u.kilojoules_per_mole
    for group in all_dihedrals:
        if group in energy:
            energy['All dihedrals'] += energy[group]

    return energy


def binaries():
    """Locate the paths to the best available gromacs binaries. """
    if which('gmx_d'):
        print("Using double precision binaries for gromacs")
        main_binary = 'gmx_d'
        grompp_bin = [main_binary, 'grompp']
        mdrun_bin = [main_binary, 'mdrun']
        genergy_bin = [main_binary, 'energy']
    elif which('grompp_d') and which('mdrun_d') and which('g_energy_d'):
        print("Using double precision binaries")
        grompp_bin = ['grompp_d']
        mdrun_bin = ['mdrun_d']
        genergy_bin = ['g_energy_d']
    elif which('gmx'):
        print("Using double precision binaries")
        main_binary = 'gmx'
        grompp_bin = [main_binary, 'grompp']
        mdrun_bin = [main_binary, 'mdrun']
        genergy_bin = [main_binary, 'energy']
    elif which('grompp') and which('mdrun') and which('g_energy'):
        print("Using single precision binaries")
        grompp_bin = ['grompp']
        mdrun_bin = ['mdrun']
        genergy_bin = ['g_energy']
    else:
        raise IOError('Unable to find gromacs executables.')
    return grompp_bin, mdrun_bin, genergy_bin
