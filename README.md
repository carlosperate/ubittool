# uBitTool

[![Code coverage](https://codecov.io/gh/carlosperate/ubittool/branch/master/graph/badge.svg)](https://codecov.io/gh/carlosperate/ubittool)
[![AppVeyor build status](https://ci.appveyor.com/api/projects/status/byfv99vlf6rinxne?svg=true)](https://ci.appveyor.com/project/carlosperate/ubitextract)
[![Travis build status](https://travis-ci.org/carlosperate/ubittool.svg?branch=master)](https://travis-ci.org/carlosperate/ubittool)
[![PyPI versions](https://img.shields.io/pypi/pyversions/ubittool.svg)](https://pypi.org/project/ubittool/)
[![Code style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPI - License](https://img.shields.io/pypi/l/ubittool.svg)](LICENSE)

uBitTool is a command line and GUI application to interface with the micro:bit.

It can:

- Read the micro:bit flash contents
- Extract user Python code from the micro:bit flash
- Flash the micro:bit
- Compare the contents of the micro:bit flash against a local hex file

![screenshots](docs/assets/img/screenshots-white.png)

![terminal recording demo](docs/assets/img/terminal-recording.svg)

## Docs

The documentation is online at
[https://carlosperate.github.io/ubittool/](https://carlosperate.github.io/ubittool/),
and its source can be found in `docs` directory.

## Basic Introduction

The easiest way to use uBitTool is via the application GUI.

- Download one of the latest GUI executables for macOS or Windows from the
  [GitHub Releases Page](https://github.com/carlosperate/ubittool/releases).
- Plug-in your micro:bit to the computer via USB
- Open the GUI executable file
- On the application menu click "nrf > Read Full Flash contents (Intel Hex)".
- A full image of the micro:bit flash should now be displayed in the GUI :)

For more information and instructions for other platforms please visit the
[Documentation](https://carlosperate.github.io/ubittool/).
