#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entry point for the program, checks to run GUI or CLI."""
from ubitflashtool.cli import main as cli


def main():
    """Launch the command line interface."""
    cli()


if __name__ == "__main__":
    main()
