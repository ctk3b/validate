import os
from pkg_resources import resource_filename

import parmed as pmd
import pytest

from validate import SUPPORTED_ENGINES
from validate.exceptions import ValidateError
from validate.gromacs import gmx_structure_energy
from validate.gromacs import energy as gmx_energy
from validate.utils import energy_diff
from validate.tests.basetest import BaseTest


class TestGromacs(BaseTest):
    test_dir = resource_filename('validate', 'tests/gromacs')

    mdp = os.path.join(test_dir, 'grompp.mdp')
    mdp_vacuum = os.path.join(test_dir, 'grompp_vacuum.mdp')

    unit_test_dir = os.path.join(test_dir, 'unit_tests')
    unit_test_names = list(os.walk(unit_test_dir))[0][1]

    repeated_engines = list()
    tests_per_engine = list()
    for engine in SUPPORTED_ENGINES:
        repeated_engines.extend([engine] * len(unit_test_names))
        tests_per_engine.extend(unit_test_names)

    def choose_mdp(self, test_name):
        if '_vacuum' in test_name:
            return self.mdp_vacuum
        else:
            return self.mdp

    @pytest.mark.parametrize('engine,test_name',
                             zip(repeated_engines, tests_per_engine))
    def test_gromacs_unit(self, engine, test_name):
        """Convert GROMACS unit tests to every supported engine. """
        top_in = os.path.join(self.unit_test_dir, test_name, test_name + '.top')
        gro_in = os.path.join(self.unit_test_dir, test_name, test_name + '.gro')
        mdp = self.choose_mdp(test_name)
        cwd = os.getcwd()

        input_energy = gmx_energy(top_in, gro_in, mdp)
        structure = pmd.load_file(top_in, xyz=gro_in)
        output_energy = self.output_energy[engine](structure, mdp, cwd)
        diff = energy_diff(input_energy, output_energy)

        return diff

if __name__ == '__main__':
    test = TestGromacs()
    diff = test.test_gromacs_unit('GROMACS', test.unit_test_names[-1])
    from pprint import pprint
    pprint(diff)
