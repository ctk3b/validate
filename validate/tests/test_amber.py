import itertools as it
import os

import parmed as pmd
import pytest

from validate import SUPPORTED_ENGINES
import validate.amber as amb
from validate.tests.basetest import (BaseTest, AMBER_UNIT_TESTS,
                                     AMBER_UNIT_TEST_DIR)


class TestAmber(BaseTest):
    @pytest.mark.parametrize('engine,test_name',
                             it.product(SUPPORTED_ENGINES, AMBER_UNIT_TESTS))
    def test_amber_unit(self, engine, test_name):
        """Convert AMBER unit tests to every supported engine. """
        prm_in = os.path.join(AMBER_UNIT_TEST_DIR, test_name, test_name + '.prmtop')
        crd_in = os.path.join(AMBER_UNIT_TEST_DIR, test_name, test_name + '.crd')
        mdin = self.choose_config_file('AMBER', test_name)

        input_energy = amb.energy(prm_in, crd_in, mdin)
        structure = pmd.load_file(prm_in, xyz=crd_in)
        return self.compare_energy(structure, engine, input_energy, test_name)

if __name__ == '__main__':
    test = TestAmber()
    test_name = AMBER_UNIT_TESTS[1]
    print('Converting ', test_name)
    diff = test.test_amber_unit('AMBER', test_name)
    from pprint import pprint
    pprint(diff)
