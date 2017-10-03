# setup.py
from cx_Freeze import setup, Executable

build_exe_options = {
    'optimize': 2,
    'packages': ['idna'],
    'includes': ['_cffi_backend'],
    'include_files': ['icons'],
}

exe = Executable(
    'PyRexecd.pyw',
    base = 'Win32GUI',
    icon = 'icons/PyRexec.ico'
)
    
setup(
    name = 'PyRexecd',
    version = '0.2.1',
    description = 'Standalone SSH server for Windows',
    url = 'https://github.com/euske/pyrexecd',
    author = 'Yusuke Shinyama',
    author_email = 'yusuke@shinyama.jp',
    license = 'MIT',
    packages = [],
    executables = [exe],
    options = { 'build_exe': build_exe_options },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
    ],
)
