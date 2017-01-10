#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys
from ubitextract.cmd import main
from ubitextract.gui import open_editor


if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] == '-g' or sys.argv[1] == '--gui'):
         open_editor()
    else:
        main(sys.argv[1:])
