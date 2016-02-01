import pytest
from validate.gromacs import gmx_structure_energy


class BaseTest(object):
    output_energy = {'GROMACS': gmx_structure_energy}

    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()
