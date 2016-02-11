import os
from pkg_resources import resource_filename

import pytest

import validate.gromacs as gmx
import validate.amber as amb


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

    def output_energy(self, engine, structure, test_name):
        config_file = self.choose_config_file(engine, test_name)
        energy_evaluator = self.structure_energy_evaluators[engine]
        return energy_evaluator(structure, config_file, test_name)

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
