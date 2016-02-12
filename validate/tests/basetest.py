import os
from pkg_resources import resource_filename

from parmed.constants import SMALL
import pytest

import validate.amber as amb
import validate.gromacs as gmx
from validate.utils import energy_diff

structure_energy_evaluators = {'GROMACS': gmx.structure_energy,
                               'AMBER': amb.structure_energy}

GROMACS_DIR = resource_filename('validate', 'tests/gromacs')
MDP = os.path.join(GROMACS_DIR, 'grompp.mdp')
MDP_VACUUM = os.path.join(GROMACS_DIR, 'grompp_vacuum.mdp')
GROMACS_UNIT_TEST_DIR = os.path.join(GROMACS_DIR, 'unit_tests')
GROMACS_UNIT_TESTS = list(os.walk(GROMACS_UNIT_TEST_DIR))[0][1]

AMBER_DIR = resource_filename('validate', 'tests/amber')
MDIN = os.path.join(AMBER_DIR, 'mdin.in')
MDIN_VACUUM = os.path.join(AMBER_DIR, 'mdin_vacuum.in')
AMBER_UNIT_TEST_DIR = os.path.join(AMBER_DIR, 'unit_tests')
AMBER_UNIT_TESTS = list(os.walk(AMBER_UNIT_TEST_DIR))[0][1]


class BaseTest:
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()

    def compare_energy(self, structure, engine, input_energy, test_name):
        """Compute energy of a structure and compare it to an input energy.

        Parameters
        ----------
        structure : pmd.Structure
        engine : str
        input_energy : OrderedDict
        test_name : str

        Returns
        -------
        diff : OrderedDict

        """
        config_file = self.choose_config_file(engine, test_name)
        energy_evaluator = structure_energy_evaluators[engine]
        output_energy = energy_evaluator(structure, config_file, test_name)
        diff = energy_diff(input_energy, output_energy)
        assert diff['potential']._value < SMALL, \
            '{} potential energy not within tolerance.'.format(test_name)
        return diff

    @staticmethod
    def choose_config_file(engine, test_name):
        if engine == 'GROMACS':
            if '_vacuum' in test_name:
                return MDP_VACUUM
            else:
                return MDP
        if engine == 'AMBER':
            if '_vacuum' in test_name:
                return MDIN_VACUUM
            else:
                return MDIN
