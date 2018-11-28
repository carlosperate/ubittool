#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
from ubitflashtool.cli import main as cli_main
from ubitflashtool.gui import open_editor

def main():
    if len(sys.argv) > 1 and (sys.argv[1] == '-g' or sys.argv[1] == '--gui'):
        open_editor()
    else:
        cli_main(sys.argv[1:])

if __name__ == "__main__":
    main()
