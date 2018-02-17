# setup.py
from setuptools import setup

setup(
    name = 'PyRExecd',
    version = '0.3.1',
    description = 'Standalone SSH server for Windows',
    url = 'https://github.com/euske/pyrexecd',
    author = 'Yusuke Shinyama',
    author_email = 'yusuke@shinyama.jp',
    license = 'MIT',
    packages = ['pyrexecd'],
    package_data = {
        'pyrexecd': ['icons/*.ico'],
    },
    install_requires = [
        'paramiko',
        'pypiwin32',
    ],
    scripts = ['PyRExecd.pyw'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
    ],
)
