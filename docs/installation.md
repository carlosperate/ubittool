---
layout: page
title: Installation
nav_order: 2
---

# How To Install uBitTool

There are two ways to install uBitTool:

- Download and run the executables
- Install as a Python 3 package

### Executables

WIP

### Python Package

This application is provided as a Python 3 (>3.5) package.

Using [pipx](https://github.com/pipxproject/pipx) is encouraged:

```
pipx install ubittool
```

Pipx will automatically create a virtual environment, and add the uBitTool
executable to the system path, so that the command can be used from any
terminal session (no need to manually activate a virtual environment).

Alternatively, crate a Python 3 (>3.5) virtual environment and install the `ubittool` package:

```
pip install ubittool
```

#### Installing from source

For information about how to instal uBitTool from source please consult the
[Development](development.html) documentation.
