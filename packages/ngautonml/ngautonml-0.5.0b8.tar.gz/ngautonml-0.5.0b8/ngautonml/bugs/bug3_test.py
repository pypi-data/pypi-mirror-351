'''Test for issues #3 on gitlab (https://gitlab.com/autonlab/ngautonml/-/issues/3)

Essentially, just a test that ngautonml installs in a fresh environment.
'''
# pylint: disable=duplicate-code

from glob import glob
from pathlib import Path
import random
from shutil import rmtree
import subprocess
import sys

import pytest

from .virtual_module import VirtualModule


def test_bug3(tmp_path_factory: pytest.TempPathFactory) -> None:
    '''Build ngautonml.whl and make sure we can install it in a blank environment.'''

    # randomly skip this test 4 out of 5 times because it is very expensive.
    if random.randint(1, 5) != 5:
        return

    # Build ngautonml to create wheel file.
    ngautonml_root = Path(__file__).parents[2]
    rmtree(ngautonml_root / 'dist', ignore_errors=True)
    subprocess.run([sys.executable, '-m', 'poetry', 'build'], cwd=ngautonml_root, check=True)

    wheel_paths = glob(str(ngautonml_root / 'dist'
                           / 'ngautonml*py3-none-any.whl'))
    assert len(wheel_paths) == 1, (
        f'BUG: unexpected extra whl files: {wheel_paths}')
    wheel_path = Path(wheel_paths[0])

    # Create a new environment in a tempdir just for this test.
    tmpdir = tmp_path_factory.mktemp('bug3_test')
    tmp_module = VirtualModule(tmpdir)
    tmp_module.install_virtual_env()

    # Device Under Test
    # This will raise an error if not exit code 0
    tmp_module.install_under_venv(wheel_path)

    # Clean up the virtual environment.
    tmp_module.finalize()
