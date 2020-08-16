#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2020-, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 1.0 International Public License.
#
# The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------


"""Provide humidity and temperature using EPICS and Raspberry Pi."""


__project__     = u'dhtioc'
__description__ = u"Provide humidity and temperature using EPICS and Raspberry Pi."
__copyright__   = u'2020-, Pete Jemian'
__authors__     = [u'Pete Jemian', ]
__author__      = ', '.join(__authors__)
__author_email__= u"prjemian@gmail.com"
__url__         = u"https://dhtioc.readthedocs.org"
__license__     = u"(c) " + __copyright__
__license__     += u" (see LICENSE file for details)"
__platforms__   = 'any'
__zip_safe__    = False
__exclude_project_dirs__ = "docs examples tests".split()
__python_version_required__ = ">=3.6"

__package_name__ = __project__
__long_description__ = __description__

from ._requirements import learn_requirements   # lgtm [py/import-own-module]
__install_requires__ = learn_requirements()
del learn_requirements

__classifiers__ = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: Freely Distributable',
    'License :: Public Domain',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Astronomy',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Chemistry',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development',
    'Topic :: Utilities',
]


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
