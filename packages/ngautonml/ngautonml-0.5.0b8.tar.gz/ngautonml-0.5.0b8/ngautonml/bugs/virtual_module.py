'''Build a virtual environment and install a module in it.

Based loosely on https://gist.github.com/mpurdon/be7f88ee4707f161215187f41c3077f6
'''

from pathlib import Path
from shutil import rmtree
import subprocess
import sys


class VirtualModule:
    '''Create a virtual environment to install a package in.'''
    def __init__(self, virtual_dir: Path):
        self.virtual_dir = virtual_dir
        self.virtual_python = self.virtual_dir / 'bin' / 'python'

    def install_virtual_env(self) -> None:
        '''Install a virtual environment at self.virtual_dir.'''
        subprocess.run([sys.executable, '-m', 'virtualenv', self.virtual_dir], check=True)

    def install_under_venv(self, module: Path) -> None:
        '''Install a module under the virtual environment.'''

        # pypi was flaking several times in a row, so we retry the install up to n-1 times.
        n = 5
        for i in range(n):
            try:
                subprocess.run(
                    [str(self.virtual_python), '-m', 'pip', 'install', str(module)], check=True)
            except subprocess.CalledProcessError:
                if i < n - 1:
                    continue  # Try again.
                raise
            break  # Yay! We're done.

    def finalize(self) -> None:
        '''Clean up the virtual environment.'''
        rmtree(str(self.virtual_dir))
