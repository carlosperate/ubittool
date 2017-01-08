#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Description
"""
from __future__ import print_function, absolute_import
import os
import sys
import logging
import argparse
from cStringIO import StringIO
from pyOCD.board import MbedBoard
from intelhex import bin2hex
from uflash import extract_script


MICROBIT_FLASH_SIZE_BYTES = (256*1024)
MICROBIT_START_ADDRESS = 0x0
MICROPYTHON_START_ADDRESS = 0x3E000


def read_flash(address=0x0, count=4):
    """
    Reads the contents of the micro:bit flash memory from the memory address
    and for as many bytes as indicated by the arguments.
    :param address: Integer indicating the start address to read.
    :param count: Hoy many bytes to read.
    :return: A list of integers, each representing a byte of data.
    """
    if not (MICROBIT_START_ADDRESS <= address < MICROBIT_FLASH_SIZE_BYTES) or \
            (address + count) > MICROBIT_FLASH_SIZE_BYTES:
        # TODO: Log an error, maybe through an exception ?
        return ''

    # TODO: Implement a time out, figure out possible exceptions
    board = MbedBoard.chooseBoard()
    target = board.target
    target.resume()
    target.halt()
    # TODO: Figure out what type of exceptions this can throw as well
    flash_data = target.readBlockMemoryUnaligned8(address, count)
    board.uninit()
    return flash_data


def bytes_to_hex(data, hex_op, offset=0x0000):
    """
    Takes a list of bytes and writes it into the hex_op file in the Intel
    Hex format.
    :param data: List of integers, each representing a single byte.
    :param hex_op: Output file to write the intel hex string.
    :param offset: Start address offset.
    :return: It does not return anything, all data written to hex_op argument.
    """
    fake_bin = StringIO()
    fake_bin.write(bytearray(data))
    fake_bin.seek(0)
    bin2hex(fake_bin, hex_op, offset=offset)
    fake_bin.close()


def read_python_code():
    """
    Reads the MicroPython script from the micro:bit flash contents
    :return: String with the MicroPython code.
    """
    flash_data = read_flash(
            address=MICROPYTHON_START_ADDRESS,
            count=(MICROBIT_FLASH_SIZE_BYTES - MICROPYTHON_START_ADDRESS))
    hex_file = StringIO()
    bytes_to_hex(flash_data, hex_file, offset=MICROPYTHON_START_ADDRESS)
    python_code = extract_script(hex_file.getvalue())
    hex_file.close()
    return python_code


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
        print('Writing MicroPython code into console.')

    print('Reading the micro:bit flash contents...')
    python_code = read_python_code()

    print('Saving the MicroPython code...')
    if file_path:
        with open(file_path, 'w') as python_script:
            python_script.write(python_code)
    else:
        hex_file = StringIO()
        bytes_to_hex(python_code, hex_file)
        print(hex_file.getvalue())
        hex_file.close()

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
        print('Writing flash into console.')

    print('Reading the micro:bit flash contents...')
    flash_data = read_flash(
            address=MICROBIT_START_ADDRESS, count=MICROBIT_FLASH_SIZE_BYTES)

    print('Saving the flash contents...')
    if file_path:
        with open(file_path, 'w') as hex_file:
            bytes_to_hex(flash_data, hex_file)
    else:
        hex_file = StringIO()
        bytes_to_hex(flash_data, hex_file)
        print(hex_file.getvalue())
        hex_file.close()

    print('Finished successfully!')


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
