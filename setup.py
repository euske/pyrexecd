# setup.py
import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    'optimize': 2,
    'packages': ['idna'],
    'includes': ['_cffi_backend'],
    'include_files': ['icons'],
}

exe = Executable(
    'PyRexecd.py',
    base='Win32GUI',
    icon='icons/PyRexec.ico'
)
    
setup(
    name = 'PyRexecd',
    version = '0.1',
    description = 'PyRexecd',
    options = { 'build_exe': build_exe_options },
    executables = [exe]
)
