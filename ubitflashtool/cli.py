#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Command line interface entry point.
"""
from __future__ import print_function, absolute_import
import os
import sys
import logging
import argparse
from ubitflashtool.cmd import read_full_flash_hex, read_python_code


def extract_py_script(file_path=None):
    """
    Extracts the MicroPython script and writes it a file if given by the
    argument, or prints it into the std out.
    :param file_path: Path to the output file to write the MicroPython code.
    :return: Nothing.
    """
    print('Extracting MicroPython script from flash:')

    if file_path:
        if os.path.isfile(file_path):
            print('Abort: The %s file already exists.' % file_path)
            return
        else:
            print('Writing MicroPython code into file: %s' % file_path)
    else:
        print('Will output MicroPython code into console.')

    print('Reading the micro:bit flash contents...')
    python_code = read_python_code()

    print('Saving the MicroPython code...')
    if file_path:
        with open(file_path, 'w') as python_script:
            python_script.write(python_code)
    else:
        print(python_code)

    print('Finished successfully!')


def extract_full_hex(file_path=None):
    """
    Reads all the micro:bit flash contents into a file if given by the argument,
    or prints it into the std out.
    :param file_path: Path to the output file to write the flash contents.
    :return: Nothing.
    """
    print('Extracting the full flash contents:')

    if file_path:
        if os.path.isfile(file_path):
            print('Abort: The %s file already exists.' % file_path)
            return
        else:
            print('Writing flash into file: %s' % file_path)
    else:
        print('Will output flash into console.')

    print('Reading the micro:bit flash contents...')
    flash_data = read_full_flash_hex()

    print('Saving the flash contents...')
    if file_path:
        with open(file_path, 'w') as hex_file:
            hex_file.write(flash_data)
    else:
        print(flash_data)

    print('Finished successfully!')


def main(argv=None):
    """
    Entry point for the command line interface.
    :param argv:
    :return: None
    """
    HELP_TEXT = """ Usage:
    ubitflashtool extracted_script.py
    ubitflashtool -s extracted_script.py
    ubitflashtool --script extracted_script.py
    ubitflashtool -m extracted_micropython.hex
    ubitflashtool --micropython extracted_micropython.hex
    ubitflashtool -f full_flash.hex
    ubitflashtool --flash full_flash.hex
    """
    logging.basicConfig(level=logging.INFO)

    if not argv:
        print(HELP_TEXT)
        sys.exit(0)
    try:
        parser = argparse.ArgumentParser(description=HELP_TEXT)
        # FIXME: This is an incorrect usage of ArgumentParser, read the docs
        parser.add_argument('-f', '--flash',
                            nargs='?',
                            help=("Extract all microbit flash contents."), )
        parser.add_argument('-s', '--script',
                            nargs='?',
                            help=("Extract python source from the microbit."), )
        parser.add_argument('-m', '--micropython',
                            nargs='?',
                            help='Extract the micropython source code')
        args = parser.parse_args(argv)

        if args.script:
            extract_py_script(args.script)
        elif args.micropython:
            print("The 'micropython' flag functionality is not implemented.")
        elif args.flash:
            extract_full_hex(args.flash)
        else:
            print("what?")
    except Exception as ex:
        # The exception of no return. Print the exception information.
        print(ex)

    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
