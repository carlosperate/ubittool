#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Description
"""
from __future__ import print_function, absolute_import
import sys
from cStringIO import StringIO
from pyOCD.board import MbedBoard
from intelhex import IntelHex
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
    board = MbedBoard.chooseBoard(blocking=False)
    target = board.target
    target.resume()
    target.halt()
    # TODO: Figure out what type of exceptions this can throw as well
    flash_data = target.readBlockMemoryUnaligned8(address, count)
    board.uninit()
    return flash_data


def bytes_to_intel_hex(data, offset=0x0000):
    """
    Takes a list of bytes and returns a string in the Intel Hex format.
    :param data: List of integers, each representing a single byte.
    :param offset: Start address offset.
    :return: A string with the Intel Hex encoded data.
    """
    i_hex = IntelHex()
    i_hex.frombytes(data, offset)

    fake_file = StringIO()
    try:
        i_hex.tofile(fake_file, format='hex')
    except IOError as e:
        sys.stderr.write("ERROR: File write: %s\n%s" % (fake_file, str(e)))
        return

    intel_hex_str = fake_file.getvalue()
    fake_file.close()
    return intel_hex_str


def bytes_to_pretty_hex(data, offset=0x0000):
    """
    Takes a list of bytes and converts it into a string of a nicely formatted
    and ASCII decoded hex.
    :param data: List of integers, each representing a single byte.
    :param offset: Start address offset.
    :return: A string with the formatted hex data.
    """
    i_hex = IntelHex()
    i_hex.frombytes(data, offset)

    fake_file = StringIO()
    try:
        i_hex.dump(tofile=fake_file, width=16, withpadding=False)
    except IOError as e:
        sys.stderr.write("ERROR: File write: %s\n%s" % (fake_file, str(e)))
        return

    pretty_hex_str = fake_file.getvalue()
    fake_file.close()
    return pretty_hex_str


def read_flash_hex(start_address=0x0, count=4, decoded_hex=False):
    """
    Reads the as many bytes of the micro:bit flash and from the given address
    as indicated by the arguments. Can return it in Intel Hex of pretty
    formatted and decoded hex string.
    :param address: Integer indicating the start address to read.
    :param count: Hoy many bytes to read.
    :param decoded_hex: True selects nice decided format, False selects Intel
            Hex format.
    :return: String with the hex formatted as indicated.
    """
    flash_data = read_flash(address=start_address, count=count)
    if decoded_hex:
        return bytes_to_pretty_hex(flash_data)
    else:
        return bytes_to_intel_hex(flash_data)


def read_full_flash_hex(decoded_hex=False):
    """
    Shortcut to read all flash contents without exposing the internal
    addresses.
    :param decoded_hex: True selects nice decided format, False selects Intel
            Hex format.
    :return: String with the hex formatted as indicated.
    """
    return read_flash_hex(
        start_address=MICROBIT_START_ADDRESS, count=MICROBIT_FLASH_SIZE_BYTES,
        decoded_hex=decoded_hex)


def read_python_code():
    """
    Reads the MicroPython script from the micro:bit flash contents.
    :return: String with the MicroPython code.
    """
    flash_data = read_flash(
            address=MICROPYTHON_START_ADDRESS,
            count=(MICROBIT_FLASH_SIZE_BYTES - MICROPYTHON_START_ADDRESS))
    py_code_hex = bytes_to_intel_hex(flash_data,
                                     offset=MICROPYTHON_START_ADDRESS)
    python_code = extract_script(py_code_hex)
    return python_code
