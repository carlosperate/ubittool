---
layout: page
title: Set Up A Development Environment
nav_order: 4
---

# Set Up A Development Environment

## Installing from Source

Originally this project used [pipenv](https://docs.pipenv.org/), however it is
now transitioning to [poetry](https://poetry.eustace.io/).

### Installing with Pipenv

You can install pipenv by simply doing:

```
$ pip install --user pipenv
```

Then clone the repository and install the development dependencies using
`pipenv`:

```
$ git clone https://github.com/carlosperate/ubittool.git
$ cd ubittool
$ pipenv install --dev
```

If you prefer to only install the dependencies necessary to run the tool and
skip all the development dependencies you can replace the last command with:

```
$ pipenv install
```

Then to run uBitTool:

```
$ pipenv run ubit --help
```

### Installing with Poetry

Install poetry using their
[installation instructions](https://poetry.eustace.io/docs/#installation).

Then clone the repository and install the development dependencies using
`poetry`:

```
$ git clone https://github.com/carlosperate/ubittool.git
$ cd ubittool
$ poetry install
```

If you prefer to only install the dependencies necessary to run the tool and
skip all the development dependencies you can replace the last command with:

```
$ poetry install --no-dev
```

Then to run uBitTool:

```
$ poetry run ubit --help
```

## make.py

Rather than having a Makefile, which can be difficult to get running on
Windows, there is a make.py file that can execute the type of commands that
would normally go in a Makefile.

To get an up-to-date overview of what commands are available you can run the
`--help` flag:

```
$ python make.py --help
Usage: python make.py [OPTIONS] COMMAND [ARGS]...

  Run make-like commands from a Python script instead of a MakeFile.

  No dependencies outside of what is on the Pipfile, so it works on all
  platforms without installing other stuff (e.g. Make on Windows).

Options:
  --help  Show this message and exit.

Commands:
  build   Build the CLI and GUI executables.
  check   Run all the checkers and tests.
  clean   Remove unnecessary files (like build outputs).
  linter  Run Flake8 linter with all its plugins.
  test    Run PyTests with the coverage plugin.
```

These docs will only cover the most important commands for development, but
feel free to explore the other commands with the `--help` flag.

### Check

Run all the checkers (`linter`, `test`, and `style`):

```
$ python make.py check
```

### Build

Builds the CLI and GUI executables using PyInstaller:

```
$ python make.py build
```
