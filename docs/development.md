---
layout: page
title: Set Up Development Environment
---

# Install

Install the development dependencies using pipenv:

```
pip install pipenv
pipenv install --editable . --dev
```

## make.py

Rather than having a Makefile, which can be difficult to get running on
Windows, there is a make.py file that can execute the types of commands that
would go on a Makefile.

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

### Check

Run all the checkers (`linter` and `test`):

```
python make.py check
```

### Build

Builds the CLI and GUI executables using PyInstaller:

```
python make.py build
```
