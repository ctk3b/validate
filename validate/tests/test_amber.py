import itertools as it
import os
from pkg_resources import resource_filename

import parmed as pmd
from parmed.constants import SMALL
import pytest

from validate import SUPPORTED_ENGINES
import validate.amber as amb
from validate.utils import energy_diff
from validate.tests.basetest import BaseTest


class TestAmber(BaseTest):
    amber_dir = resource_filename('validate', 'tests/amber')
    unit_test_dir = os.path.join(amber_dir, 'unit_tests')
    unit_test_names = list(os.walk(unit_test_dir))[0][1]

    @pytest.mark.parametrize('engine,test_name',
                             it.product(SUPPORTED_ENGINES, unit_test_names))
    def test_amber_unit(self, engine, test_name):
        """Convert GROMACS unit tests to every supported engine. """
        prm_in = os.path.join(self.unit_test_dir, test_name, test_name + '.prmtop')
        crd_in = os.path.join(self.unit_test_dir, test_name, test_name + '.crd')
        mdin = self.choose_config_file('AMBER', test_name)

        input_energy = amb.energy(prm_in, crd_in, mdin)

        structure = pmd.load_file(prm_in, xyz=crd_in)
        output_energy = self.output_energy(engine, structure, test_name)

        diff = energy_diff(input_energy, output_energy)
        for key, energy in diff.items():
            if key == 'potential':
                assert energy._value < SMALL, \
                    '{} {} energy not within tolerance.'.format(test_name, key)
        return diff

if __name__ == '__main__':
    test = TestAmber()
    test_name = test.unit_test_names[1]
    print('Converting ', test_name)
    diff = test.test_amber_unit('AMBER', test_name)
    from pprint import pprint
    pprint(diff)
