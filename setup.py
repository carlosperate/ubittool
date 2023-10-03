#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup.py."""
import sys
from setuptools import setup

from ubittool import __version__


if sys.version_info.major != 3 or sys.version_info.minor < 6:
    print("This package only supports Python 3.6+")
    sys.exit(1)

# Open the readme and requirements file
with open("README.md") as f:
    readme = f.read()
with open("requirements.txt") as f:
    requires = f.read().splitlines()


setup(
    name="ubittool",
    version=__version__,
    description="A module and utility to read the memory contents of the "
    "BBC micro:bit.",
    long_description=readme,
    author="Carlos Pereira Atencio",
    author_email="carlosperate@embeddedlog.com",
    url="https://github.com/carlosperate/ubittool",
    install_requires=requires,
    packages=["ubittool"],
    license="MIT license",
    keywords=["microbit", "micro:bit", "bbcmicrobit", "ubittool"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Education",
        "Topic :: Software Development :: Embedded Systems",
    ],
    python_requires=">=3.6, <3.10",
    entry_points={"console_scripts": ["ubit=ubittool.__main__:main"]},
)
