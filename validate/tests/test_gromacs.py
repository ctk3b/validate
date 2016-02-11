import os
from pkg_resources import resource_filename

import parmed as pmd
from parmed.constants import SMALL
import pytest

from validate import SUPPORTED_ENGINES
import validate.gromacs as gmx
from validate.utils import energy_diff
from validate.tests.basetest import BaseTest




class TestGromacs(BaseTest):
    gromacs_dir = resource_filename('validate', 'tests/gromacs')
    unit_test_dir = os.path.join(gromacs_dir, 'unit_tests')
    unit_test_names = list(os.walk(unit_test_dir))[0][1]

    repeated_engines = list()
    tests_per_engine = list()
    for engine in SUPPORTED_ENGINES:
        repeated_engines.extend([engine] * len(unit_test_names))
        tests_per_engine.extend(unit_test_names)

    @pytest.mark.parametrize('engine,test_name',
                             zip(repeated_engines, tests_per_engine))
    def test_gromacs_unit(self, engine, test_name):
        """Convert GROMACS unit tests to every supported engine. """
        top_in = os.path.join(self.unit_test_dir, test_name, test_name + '.top')
        gro_in = os.path.join(self.unit_test_dir, test_name, test_name + '.gro')
        mdp = self.choose_config_file('GROMACS', test_name)

        input_energy = gmx.energy(top_in, gro_in, mdp)

        structure = pmd.load_file(top_in, xyz=gro_in)
        output_energy = self.output_energy(engine, structure, test_name)

        diff = energy_diff(input_energy, output_energy)
        for key, energy in diff.items():
            if key == 'potential':
                assert energy._value < SMALL, \
                    '{} {} energy not within tolerance.'.format(test_name, key)
        return diff

if __name__ == '__main__':
    test = TestGromacs()
    test_name = test.unit_test_names[1]
    print('Converting ', test_name)
    diff = test.test_gromacs_unit('AMBER', test_name)
    from pprint import pprint
    pprint(diff)
