import itertools as it
import os
from pkg_resources import resource_filename

import parmed as pmd
import pytest

from validate import SUPPORTED_ENGINES
import validate.gromacs as gmx
from validate.tests.basetest import BaseTest


class TestGromacs(BaseTest):
    gromacs_dir = resource_filename('validate', 'tests/gromacs')
    unit_test_dir = os.path.join(gromacs_dir, 'unit_tests')
    unit_test_names = list(os.walk(unit_test_dir))[0][1]

    @pytest.mark.parametrize('engine,test_name',
                             it.product(SUPPORTED_ENGINES, unit_test_names))
    def test_gromacs_unit(self, engine, test_name):
        """Convert GROMACS unit tests to every supported engine. """
        top_in = os.path.join(self.unit_test_dir, test_name, test_name + '.top')
        gro_in = os.path.join(self.unit_test_dir, test_name, test_name + '.gro')
        mdp = self.choose_config_file('GROMACS', test_name)

        input_energy = gmx.energy(top_in, gro_in, mdp)
        structure = pmd.load_file(top_in, xyz=gro_in)
        return self.compare_energy(structure, engine, input_energy, test_name)

if __name__ == '__main__':
    test = TestGromacs()
    test_name = test.unit_test_names[1]
    print('Converting ', test_name)
    diff = test.test_gromacs_unit('AMBER', test_name)
    from pprint import pprint
    pprint(diff)
