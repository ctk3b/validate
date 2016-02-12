import itertools as it
import os

import parmed as pmd
import pytest

from validate import SUPPORTED_ENGINES
import validate.gromacs as gmx
from validate.tests.basetest import (BaseTest, GROMACS_UNIT_TESTS,
                                     GROMACS_UNIT_TEST_DIR)


class TestGromacs(BaseTest):
    @pytest.mark.parametrize('engine,test_name',
                             it.product(SUPPORTED_ENGINES, GROMACS_UNIT_TESTS))
    def test_gromacs_unit(self, engine, test_name):
        """Convert GROMACS unit tests to every supported engine. """
        top_in = os.path.join(GROMACS_UNIT_TEST_DIR, test_name, test_name + '.top')
        gro_in = os.path.join(GROMACS_UNIT_TEST_DIR, test_name, test_name + '.gro')
        mdp = self.choose_config_file('GROMACS', test_name)

        input_energy = gmx.energy(top_in, gro_in, mdp)
        structure = pmd.load_file(top_in, xyz=gro_in)
        return self.compare_energy(structure, engine, input_energy, test_name)

if __name__ == '__main__':
    test = TestGromacs()
    test_name = GROMACS_UNIT_TESTS[1]
    print('Converting ', test_name)
    diff = test.test_gromacs_unit('AMBER', test_name)
    from pprint import pprint
    pprint(diff)
