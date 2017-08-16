# setup.py
import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    'packages': ['idna'],
    'includes': ['_cffi_backend'],
    'include_files': ['icons'],
}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

setup(name = 'PyRexecd',
      version = '0.1',
      description = 'PyRexecd',
      options = { 'build_exe': build_exe_options },
      executables = [Executable('PyRexecd.py', base=base)])
