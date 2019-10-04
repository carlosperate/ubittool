---
layout: page
title: Installation
nav_order: 2
---

# How To Install uBitTool

There are three ways to install uBitTool:

- Download the executables (no installation required, they are ready to run)
- Install as a Python 3 package from PyPI
- Install the Python 3 package from source

## Executables

WIP

## Python Package

This application is provided as a Python 3 (>3.5) package.

Using [pipx](https://pipxproject.github.io/pipx/) is encouraged, as it will
automatically create a virtual environment and add the resulting uBitTool
executable to the system path. This way the command can be used from any
terminal session without the need to manually activate a virtual environment.

If you don't have pipx already installed, follow the
[pipx installation instructions](https://pipxproject.github.io/pipx/installation/).

Then:

```
pipx install ubittool
```

Alternatively, crate a Python 3 (>3.5) virtual environment and install the `ubittool` package:

```
pip install ubittool
```

## Installing from source

For information about how to install uBitTool from source please consult the
[uBitTool Development documentation](development.html).
