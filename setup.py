#!/usr/bin/env python2
from setuptools import setup
from ubitextract import get_version

# TODO: Add change list by reading data from github releases
with open('README.md') as f:
    readme = f.read()


setup(
    name='ubitextract',
    version=get_version(),
    description='A module and utility to read the memory contents of the BBC micro:bit.',
    long_description=readme,
    author='carlosperate',
    author_email='carlosperate@embeddedlog.com',
    url='https://github.com/carlosperate/ubitextract',
    py_modules=['ubitextract', ],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Software Development :: Embedded Systems',
    ],
    entry_points={
        'console_scripts': ['ubitextract=ubitextract:main'],
    }
)
