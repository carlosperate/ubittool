# ubitflashtool

[![codecov](https://codecov.io/gh/carlosperate/ubitflashtool/branch/master/graph/badge.svg)](https://codecov.io/gh/carlosperate/ubitflashtool)
[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/byfv99vlf6rinxne?svg=true)](https://ci.appveyor.com/project/carlosperate/ubitextract)
[![Travis build Status](https://travis-ci.org/carlosperate/ubitflashtool.svg?branch=master)](https://travis-ci.org/carlosperate/ubitflashtool)

Utility to extract a MicroPython program and/or interpreter from a microbit.

Install in a virtual environment:

```
python setup.py install
```

To run:

```
ubitflashtool -s extracted_script.py
```

To run the GUI:

```
ubitflashtool --gui
```

or from this directory:

```
python -m ubitflashtool --gui
```

To run the tests, from this directory execute:

```
pytest -v --cov=ubitflashtool tests/
```
