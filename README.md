# uBitTool

[![Code coverage](https://codecov.io/gh/carlosperate/ubittool/branch/master/graph/badge.svg)](https://codecov.io/gh/carlosperate/ubittool)
[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/byfv99vlf6rinxne?svg=true)](https://ci.appveyor.com/project/carlosperate/ubitextract)
[![Travis build status](https://travis-ci.org/carlosperate/ubittool.svg?branch=master)](https://travis-ci.org/carlosperate/ubittool)
[![PyPI versions](https://img.shields.io/pypi/pyversions/ubittool.svg)](https://pypi.org/project/ubittool/)
[![Code style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPI - License](https://img.shields.io/pypi/l/ubittool.svg)](LICENSE)

uBitTool is a command line and GUI application to interface with the micro:bit.

It can:

- Read the micro:bit nRF51 flash contents
- Extract user Python code in the micro:bit flash
- Flash the micro:bit nRF51
- Compare the contents of the micro:bit nRF51 flash against a local hex file

## Docs

The documentation is online at [https://carlosperate.github.io/ubittool/](https://carlosperate.github.io/ubittool/), and the source can be found in `docs` directory.

## Basic introduction

The easiest way to use uBitTool is to open the application GUI.

If you have downloaded the app via the GH releases, you can double click on the gui file for your platform.

If you are using the command line application you can open the GUI with:

```
ubit gui
```

The command line help flag will also provide more information:

```
$ ubit --help
Usage: ubit [OPTIONS] COMMAND [ARGS]...

  uBitTool v0.5.0.

  CLI and GUI utility to read content from the micro:bit.

Options:
  --help  Show this message and exit.

Commands:
  compare-flash  Compare the micro:bit flash contents with a hex file.
  gui            Launch the GUI version of this app (has more options).
  read-code      Extract the MicroPython code to a file or print it.
  read-flash     Read the micro:bit flash contents into a hex file or...
```

## Installing

There are two ways to install uBitTool:

- Downloading executables
- Installing as a Python package

### Executables

WIP

### Python Package

Using [pipx](https://github.com/pipxproject/pipx) is encouraged:

```
pipx install ubittool
```

Otherwise, crate a virtual environment and

```
pip install ubittool
```

## Running

NOTE: This should be moved to the main docs.

To run:

```
ubit read-code -f extracted_script.py
```

To run the GUI:

```
ubit gui
```

or from this directory:

```
python -m ubittool gui
```

To run the tests, from this directory execute:

```
python make.py check
```

To see what other make actions there are run:

```
python make.py --help
```
