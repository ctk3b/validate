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

    unit_test_dir = os.path.join(test_dir, 'unit_tests')
    unit_test_names = list(os.walk(unit_test_dir))[0][1]

    def choose_mdp(self, test_name):
        if '_vacuum' in test_name:
            return self.mdp_vacuum
        else:
            return self.mdp

    @pytest.mark.parametrize('test_name', unit_test_names)
    def test_gromacs_unit(self, test_name):
        top_in = os.path.join(self.unit_test_dir, test_name, test_name + '.top')
        gro_in = os.path.join(self.unit_test_dir, test_name, test_name + '.gro')
        mdp = self.choose_mdp(test_name)

        cwd = os.getcwd()

        input_energy = gmx_energy(top_in, gro_in, mdp)

        structure = pmd.load_file(top_in, xyz=gro_in)

        for engine in SUPPORTED_ENGINES:
            if engine == 'GROMACS':
                top_out = os.path.join(cwd, 'out_{}.top'.format(test_name))
                gro_out = os.path.join(cwd, 'out_{}.gro'.format(test_name))
                structure.save(top_out, overwrite=True)
                structure.save(gro_out, overwrite=True)

                output_energy = gmx_energy(top_out, gro_out, mdp)
                diff = energy_diff(input_energy, output_energy)


if __name__ == '__main__':
    test = TestGromacs()
    test.test_gromacs_unit(*test.unit_test_files[0])
