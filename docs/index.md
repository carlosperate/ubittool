---
layout: page
homepage: true
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
ubitflashtool --help
```

Or from this directory:

```
python -m ubitflashtool --help
```

To retrieve the user Python code:
```
ubitflashtool read-code -f extracted_script.py
```

To read the entire flash contents:
```
ubitflashtool read-flash
```

To compare the flash contents with a hex file:
```
ubitflashtool compare-flash
```

To run the GUI:
```
ubitflashtool gui
```
