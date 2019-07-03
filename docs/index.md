---
layout: page
homepage: true
nav_order: 1
---

# Intro

uBitTool is a command line and GUI application to interface with the micro:bit.

It can:

- Read the micro:bit nRF51 flash contents
- Extract user Python code from the micro:bit flash
- Flash the micro:bit nRF51
- Compare the contents of the micro:bit nRF51 flash against a local hex file

These docs are still a WIP.

## Basic Introduction

### Basic Installation

The easiest way to use uBitTool is to open the application GUI.

If you have downloaded the app via the GH releases, you can double click on
the gui file for your platform.

If you are using the command line application you can open the GUI with:

```
ubit gui
```

The command line help flag will provide information about how to use the
uBitTool in the terminal:

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
