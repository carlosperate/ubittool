# uBitFlashTool

[![codecov](https://codecov.io/gh/carlosperate/ubitflashtool/branch/master/graph/badge.svg)](https://codecov.io/gh/carlosperate/ubitflashtool)
[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/byfv99vlf6rinxne?svg=true)](https://ci.appveyor.com/project/carlosperate/ubitextract)
[![Travis build Status](https://travis-ci.org/carlosperate/ubitflashtool.svg?branch=master)](https://travis-ci.org/carlosperate/ubitflashtool)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Utility to extract a MicroPython program and/or interpreter from a microbit.

Install in a Python 2.7 virtual environment:

```
pip install .
```

Although pipenv is recommended:

```
pip install pipenv
pipenv install .
```

To run:

```
ubitflashtool read-code -f extracted_script.py
```

To run the GUI:

```
ubitflashtool gui
```

or from this directory:

```
python -m ubitflashtool gui
```

To run the tests, from this directory execute:

```
python make.py check
```

To see what other make actions there are run:

```
python make.py --help
```
