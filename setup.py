#!/usr/bin/env python

"""
Packaging setup for dhtioc.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
#from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))
sys.path.insert(0, path.join('dhtioc', ))
import dhtioc as package
import versioneer


__entry_points__  = {
    'console_scripts': [
        'dhtioc = dhtioc.ioc:main',
        ],
    #'gui_scripts': [],
}


setup(
    author           = package.__author__,
    author_email     = package.__author_email__,
    classifiers      = package.__classifiers__,
    description      = package.__description__,
    entry_points     = __entry_points__,
    license          = package.__license__,
    long_description = package.__long_description__,
    install_requires = package.__install_requires__,
    name             = package.__project__,
    packages         = find_packages(exclude=package.__exclude_project_dirs__),
    include_package_data=True,
    url              = package.__url__,
    zip_safe         = package.__zip_safe__,
    python_requires  = package.__python_version_required__,
    version          = versioneer.get_version(),
    cmdclass         = versioneer.get_cmdclass(),
 )
