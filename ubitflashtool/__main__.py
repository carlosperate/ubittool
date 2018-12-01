#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entry point for the program, checks to run GUI or CLI."""
import sys
from ubitflashtool.cli import main as cli_main
from ubitflashtool.gui import open_editor


def main():
    """Look at the first argument, launch it if GUI is requested."""
    if len(sys.argv) > 1 and (sys.argv[1] == '-g' or sys.argv[1] == '--gui'):
        open_editor()
    else:
        cli_main(sys.argv[1:])


if __name__ == "__main__":
    main()
