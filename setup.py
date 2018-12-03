#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup.py."""
import sys
from setuptools import setup

from ubitflashtool import __version__


# Stop if not using Python 2
if sys.version_info.major != 2:
    print("Due to dependencies, this package is Python 2 only.")
    sys.exit(1)

# Open the readme and requirements file
with open('README.md') as f:
    readme = f.read()
with open('requirements.txt') as f:
    requires = f.read().splitlines()


setup(
    name='ubitflashtool',
    version=__version__,
    description='A module and utility to read the memory contents of the '
                'BBC micro:bit.',
    long_description=readme,
    author='Carlos Pereira Atencio',
    author_email='carlosperate@embeddedlog.com',
    url='https://github.com/carlosperate/ubitflashtool',
    install_requires=requires,
    packages=['ubitflashtool'],
    license='MIT license',
    keywords=['microbit', 'micro:bit', 'bbcmicrobit', 'ubitflashtool'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Software Development :: Embedded Systems',
    ],
    entry_points={
        'console_scripts': ['ubitflashtool=ubitflashtool.__main__:main'],
    }
)
