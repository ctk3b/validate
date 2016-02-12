import os
from pkg_resources import resource_filename

from parmed.constants import SMALL
import pytest

import validate.amber as amb
import validate.gromacs as gmx
from validate.utils import energy_diff


class BaseTest(object):
    structure_energy_evaluators = {'GROMACS': gmx.structure_energy,
                                   'AMBER': amb.structure_energy}

    gromacs_dir = resource_filename('validate', 'tests/gromacs')
    mdp = os.path.join(gromacs_dir, 'grompp.mdp')
    mdp_vacuum = os.path.join(gromacs_dir, 'grompp_vacuum.mdp')

    amber_dir = resource_filename('validate', 'tests/amber')
    mdin = os.path.join(amber_dir, 'mdin.in')
    mdin_vacuum = os.path.join(amber_dir, 'mdin_vacuum.in')

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
        energy_evaluator = self.structure_energy_evaluators[engine]
        output_energy = energy_evaluator(structure, config_file, test_name)
        diff = energy_diff(input_energy, output_energy)
        assert diff['potential']._value < SMALL, \
            '{} potential energy not within tolerance.'.format(test_name)
        return diff

    def choose_config_file(self, engine, test_name):
        if engine == 'GROMACS':
            if '_vacuum' in test_name:
                return self.mdp_vacuum
            else:
                return self.mdp
        if engine == 'AMBER':
            if '_vacuum' in test_name:
                return self.mdin_vacuum
            else:
                return self.mdin

