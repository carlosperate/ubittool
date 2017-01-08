#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Description
"""
from __future__ import print_function, absolute_import
import sys
import logging
import argparse
from cStringIO import StringIO
from pyOCD.board import MbedBoard
from intelhex import bin2hex

#: MAJOR, MINOR, RELEASE, STATUS [alpha, beta, final], VERSION
__version__ = '0.1alpha1'


def get_version():
    """
    Returns a string representation of the version information of this project.
    """
    return __version__


def get_microbit():
    """
    Description.
    :return:
    """
    board = MbedBoard.chooseBoard()
    target = board.target
    target.resume()
    target.halt()
    return board


def read_flash(target, address=0x0, count=4):
    """
    The micro:bit flash memory space starts at 0x00000000 and ends at
    0x40000000.
    :param target:
    :param address:
    :param count:
    :return:
    """
    if not (0x0 <= address < 0x40000000):
        # TODO: Log an error, maybe through an exception ?
        return ''

    # TODO: Figure out what type of exceptions this can throw
    return target.readBlockMemoryUnaligned8(address, count)


def data_to_hex(data, hex_op):
    """
    Description.
    :param data:
    :param hex_op:
    :return:
    """
    fake_bin = StringIO()
    fake_bin.write(bytearray(data))
    fake_bin.seek(0)
    bin2hex(fake_bin, hex_op,offset=0x0000)


def flash_to_hex(file_path=None):
    """
    Reads all the microbit flash contents into a file if given by the file_path
    argument, or prints it into the stdout.
    :param file_path:
    :return:
    """
    board = get_microbit()
    flash_data = read_flash(board.target, address=0x0, count=(256*1024))
    board.uninit()

    if file_path:
        # TODO: Check file is valid
        # TODO: proper catch exception
        hex_file = open(file_path, 'w')
    else:
        hex_file = StringIO()

    data_to_hex(flash_data, hex_file)

    if not file_path:
        # TODO: Redirect hex_file to stdout instead of using StringIO ?
        print(hex_file.getvalue())

    hex_file.close()


def main(argv=None):
    """
    Entry point for the command line interface.
    :param argv:
    :return: None
    """
    HELP_TEXT = """ Usage:
    ubitextract extracted_script.py
    ubitextract -s extracted_script.py
    ubitextract --script extracted_script.py
    ubitextract -m extracted_micropython.hex
    ubitextract --micropython extracted_micropython.hex
    ubitextract -f full_flash.hex
    ubitextract --flash full_flash.hex
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
            print("The 'script' flag functionality is not implemented.")
        elif args.micropython:
            print("The 'micropython' flag functionality is not implemented.")
        elif args.flash:
            flash_to_hex(args.flash)
        else:
            print("what?")
    except Exception as ex:
        # The exception of no return. Print the exception information.
        print(ex)

    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])
