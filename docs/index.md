---
layout: page
homepage: true
nav_order: 1
---

# Intro

These docs are still WIP.

# Install

Install in a Python 2.7 virtual environment:

```
pip install .
```

Although pipenv is recommended:

```
pip install pipenv
pipenv install .
```

# Run

To see the available commands:

```
ubit --help
```

Or from this directory:

```
python -m ubit --help
```

To retrieve the user Python code:

```
ubit read-code -f extracted_script.py
```

To read the entire flash contents:

```
ubit read-flash
```

To compare the flash contents with a hex file:

```
ubit compare-flash
```

To run the GUI:

```
ubit gui
```
