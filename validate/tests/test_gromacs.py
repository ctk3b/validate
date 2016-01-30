from glob import glob
import os
from os.path import basename, splitext
from pkg_resources import resource_filename

import parmed as pmd
import pytest

from validate import SUPPORTED_ENGINES
from validate.exceptions import ValidateError
from validate.gromacs import energy as gmx_energy
from validate.utils import energy_diff
from validate.tests.basetest import BaseTest


class TestGromacs(BaseTest):
    test_dir = resource_filename('validate', 'tests/gromacs')

    mdp = os.path.join(test_dir, 'grompp.mdp')
    mdp_vacuum = os.path.join(test_dir, 'grompp_vacuum.mdp')

    unit_gros = sorted(glob(os.path.join(test_dir, 'unit_tests/*/*.gro')))
    unit_tops = sorted(glob(os.path.join(test_dir, 'unit_tests/*/*.top')))

    unit_test_files = list()
    for gro, top in zip(unit_gros, unit_tops):
        if not splitext(basename(gro))[0] == splitext(basename(top))[0]:
            raise ValidateError('.gro and .top files are expected to share the'
                                ' same basename.')

        if '_vacuum' in gro:
            mdp_to_use = mdp_vacuum
        else:
            mdp_to_use = mdp
        unit_test_files.append((top, gro, mdp_to_use))

    @pytest.mark.parametrize('top_in,gro_in,mdp', unit_test_files)
    def test_gromacs_unit(self, top_in, gro_in, mdp):
        base_path, top = os.path.split(top_in)
        base_path, gro = os.path.split(gro_in)

        input_energy = gmx_energy(top_in, gro_in, mdp)

        structure = pmd.load_file(top_in, xyz=gro_in)

        for engine in SUPPORTED_ENGINES:
            if engine == 'GROMACS':
                top_out = os.path.join(base_path, 'out_' + top)
                gro_out = os.path.join(base_path, 'out_' + gro)
                structure.save(top_out, overwrite=True)
                structure.save(gro_out, overwrite=True)

                output_energy = gmx_energy(top_out, gro_out, mdp)
                diff = energy_diff(input_energy, output_energy)

        from pprint import pprint
        pprint(diff)

if __name__ == '__main__':
    test = TestGromacs()
    test.test_gromacs_unit(*test.unit_test_files[0])
