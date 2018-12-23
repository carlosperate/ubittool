#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Commands to carry out all the actions for ubitflashtool control.

This module internal functions can read any memory location from the micro:bit
via PyOCD, which uses the CMSIS interface provided by DAPLink.

The exposed function for the command line and GUI interfaces can safely read
areas of Flash (full flash, MicroPython, Python code) and UICR (to read the
customer data), and format the output into Intel Hex, a nicely decoded string
format, or human readable text (for the Python code).
"""
from __future__ import print_function, absolute_import
import os
import sys
import tempfile
import webbrowser
from threading import Timer
from difflib import HtmlDiff
from cStringIO import StringIO
from traceback import format_exc

from pyOCD.board import MbedBoard
from intelhex import IntelHex
from uflash import extract_script

if sys.version_info.major == 2:
    # open() with encodings
    from io import open


# nRF51 256 KBs of flash starts at address 0
MICROBIT_FLASH_START = 0x00000000
MICROBIT_FLASH_SIZE_BYTES = 256 * 1024
MICROBIT_FLASH_END = MICROBIT_FLASH_START + MICROBIT_FLASH_SIZE_BYTES

# Assumes code attached to fixed location instead of using the filesystem
PYTHON_CODE_OFFSET = 0x3E000
PYTHON_CODE_START = MICROBIT_FLASH_START + PYTHON_CODE_OFFSET
PYTHON_CODE_END = MICROBIT_FLASH_END

# MicroPython will contain unnecessary empty space between end of interpreter
# and begginning of code at a fixed location, assumes no file system used
MICROPYTHON_OFFSET = 0x0
MICROPYTHON_START = MICROBIT_FLASH_START + MICROPYTHON_OFFSET
MICROPYTHON_END = PYTHON_CODE_START

# nRF51 User Information Configuration Registers
UICR_START = 0x10001000
UICR_SIZE_BYTES = 0x100
UICR_END = UICR_START + UICR_SIZE_BYTES

# UICR reserved data for customer
UICR_CUSTOMER_OFFSET = 0x80
UICR_CUSTOMER_SIZE_BYTES = 32 * 4
UICR_CUSTOMER_START = UICR_START + UICR_CUSTOMER_OFFSET
UICR_CUSTOMER_END = UICR_CUSTOMER_START + UICR_CUSTOMER_SIZE_BYTES


#
# Memory read operations
#
def _read_continuous_memory(address=0x0, count=4):
    """Read any continuous memory area from the micro:bit.

    Reads the contents of any micro:bit continuous memory area, starting from
    the 'address' argument for as many bytes as indicated by 'count'.
    There is no input sanitation in this function and is the responsibility of
    the caller to input values within range of the target board or deal with
    any exceptions raised by PyOCD.

    :param address: Integer indicating the start address to read.
    :param count: Integer, how many bytes to read.
    :return: A list of integers, each representing a byte of data.
    """
    # TODO: Implement a time out, figure out possible exceptions
    board = MbedBoard.chooseBoard(blocking=False)
    target = board.target
    target.resume()
    target.halt()
    # TODO: Figure out what type of exceptions this can throw as well
    read_data = target.readBlockMemoryUnaligned8(address, count)
    board.uninit()
    return read_data


def read_flash(address=MICROBIT_FLASH_START, count=4):
    """Read the contents of the micro:bit flash memory.

    Start from the 'address' argument for as many bytes as indicated by the
    'count' argument.

    :param address: Integer indicating the start address to read.
    :param count: Integer indicating how many bytes to read.
    :return: A list of integers, each representing a byte of data.
    """
    last_byte = address + count
    if not (MICROBIT_FLASH_START <= address < MICROBIT_FLASH_END) or \
            last_byte > MICROBIT_FLASH_END:
        raise ValueError('Cannot read a flash location out of boundaries.\n'
                         'Reading from {} to {},\nlimits from {} to {}'.format(
                             address, last_byte,
                             MICROBIT_FLASH_START, MICROBIT_FLASH_END))
    return _read_continuous_memory(address=address, count=count)


def read_uicr(address=UICR_START, count=4):
    """Read the contents of the micro:bit UICR memory.

    Start from the 'address' argument for as many bytes as indicated by the
    'count' argument.

    :param address: Integer indicating the start address to read.
    :param count: Integer indicating how many bytes to read.
    :return: A list of integers, each representing a byte of data.
    """
    last_byte = address + count
    if not (UICR_START <= address < UICR_END) or (address + count) > UICR_END:
        raise ValueError('Cannot read a UICR location out of boundaries.\n'
                         'Reading from {} to {},\nlimits from {} to {}'.format(
                             address, last_byte, UICR_START, UICR_END))
    return _read_continuous_memory(address=address, count=count)


#
# Data format conversions
#
def _bytes_to_intel_hex(data, offset=0x0000):
    """Take a list of bytes and return a string in the Intel Hex format.

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
        sys.stderr.write('ERROR: File write: {}\n{}'.format(fake_file, str(e)))
        return

    intel_hex_str = fake_file.getvalue()
    fake_file.close()
    return intel_hex_str


def _bytes_to_pretty_hex(data, offset=0x0000):
    """Convert a list of bytes to a nicely formatted ASCII decoded hex string.

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
        sys.stderr.write('ERROR: File write: {}\n{}'.format(fake_file, str(e)))
        return

    pretty_hex_str = fake_file.getvalue()
    fake_file.close()
    return pretty_hex_str


#
# Commands
#
def read_uicr_customer(decode_hex=False):
    """Read the UICR Customer data.

    :return: String with the nicely decoded UIR Customer area data.
    """
    uicr_data = read_uicr(address=UICR_CUSTOMER_START,
                          count=UICR_CUSTOMER_SIZE_BYTES)
    if decode_hex:
        return _bytes_to_pretty_hex(uicr_data, UICR_CUSTOMER_START)
    else:
        return _bytes_to_intel_hex(uicr_data, UICR_CUSTOMER_START)


def read_flash_hex(address=MICROBIT_FLASH_START, count=4, decode_hex=False):
    """Read flash memory and return as a hex string.

    Read as a number of bytes of the micro:bit flash from the given address.
    Can return it in Intel Hex format or a pretty formatted and decoded hex
    string.

    :param address: Integer indicating the start address to read.
    :param count: Integer indicating hoy many bytes to read.
    :param decode_hex: True selects nice decoded format, False selects Intel
            Hex format.
    :return: String with the hex formatted as indicated.
    """
    flash_data = read_flash(address=address, count=count)
    if decode_hex:
        return _bytes_to_pretty_hex(flash_data, address)
    else:
        return _bytes_to_intel_hex(flash_data, address)


def read_full_flash_hex(decode_hex=False):
    """Shortcut to read all flash without exposing the internal addresses.

    :param decode_hex: True selects nice decided format, False selects Intel
            Hex format.
    :return: String with the hex formatted as indicated.
    """
    return read_flash_hex(address=MICROBIT_FLASH_START,
                          count=MICROBIT_FLASH_SIZE_BYTES,
                          decode_hex=decode_hex)


def read_micropython():
    """Read the MicroPython runtime from the micro:bit flash.

    :return: String with Intel Hex format for the MicroPython runtime.
    """
    return read_flash_hex(address=MICROPYTHON_START,
                          count=MICROPYTHON_END - MICROPYTHON_START,
                          decode_hex=False)


def read_python_code():
    """Read the MicroPython user code from the micro:bit flash.

    :return: String with the MicroPython code.
    """
    flash_data = read_flash(address=PYTHON_CODE_START,
                            count=(PYTHON_CODE_END - PYTHON_CODE_START))
    py_code_hex = _bytes_to_intel_hex(flash_data, offset=PYTHON_CODE_START)
    try:
        python_code = extract_script(py_code_hex)
    except Exception as e:
        sys.stderr.write(format_exc(e))
        raise Exception('Could not decode the MicroPython code from flash')
    return python_code


#
# Hex comparison
#
def _open_temp_html(html_str):
    """Create a temporary html file, open it in a browser and delete it.

    :param html_str: String to write to the temporary file.
    """
    fd, path = tempfile.mkstemp(suffix='.html')
    try:
        with os.fdopen(fd, 'w') as tmp:
            # do stuff with temp file
            tmp.write(html_str)
        webbrowser.open('file://{}'.format(os.path.realpath(path)))
    finally:
        t = Timer(30.0, lambda del_f: os.remove(del_f), args=[path])
        t.start()


def _gen_diff_html(from_title, from_lines, to_title, to_lines):
    """Compare two strings and string of HTML code with the output.

    :param from_title: Title of the left content to compare.
    :param from_lines: List of lines to compare.
    :param to_title: Title of the right content to compare.
    :param to_lines: List of lines to compare.
    :return: String of HTML code with the comparison output.
    """
    html_template = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Diff {from_title} vs. {to_title}</title>
        <style type="text/css">
            table {{font-family:Courier; border:medium}}
            .diff_header {{background-color:#e0e0e0; padding:0px 10px}}
            td.diff_header {{text-align:right}}
            .diff_next {{background-color:#c0c0c0; padding:0px 10px}}
            .diff_add {{background-color:#aaffaa}}
            .diff_chg {{background-color:#ffff77}}
            .diff_sub {{background-color:#ffaaaa}}
        </style>
    </head>
    <body>
        <table>
            <tr><td><table>
                <tr><th>Colors</th></tr>
                <tr><td class="diff_add">Added</td></tr>
                <tr><td class="diff_chg">Changed</td></tr>
                <tr><td class="diff_sub">Deleted</td></tr>
            </table></td><td><table>
                <tr><th>Links<th></tr>
                <tr><td>(f)irst change</td></tr>
                <tr><td>(n)ext change</td></tr>
                <tr><td>(t)op</td></tr>
            </table></td><td><table>
                <tr><th>Files<th></tr>
                <tr><td>Left: {from_title}</td></tr>
                <tr><td>Right: {to_title}</td></tr>
            </table></td></tr>
        </table>
        {diff_table}
    </body>
    </html>"""
    differ = HtmlDiff()
    filled_template = html_template.format(
            from_title=from_title,
            to_title=to_title,
            diff_table=differ.make_table(from_lines, to_lines))
    return filled_template


def compare_full_flash_hex(hex_file_path):
    """Compare the micro:bit flash contents with a hex file.

    Opens the default browser to display an HTML page with the comparison
    output.

    :param hex_file_path: File path to the hex file to compare against.
    """
    with open(hex_file_path, encoding='utf-8') as f:
        file_hex_str = f.readlines()
    flash_hex_str = read_full_flash_hex(decode_hex=False)

    html_code = _gen_diff_html('micro:bit', flash_hex_str.splitlines(),
                               'Hex file', file_hex_str)
    _open_temp_html(html_code)


def compare_uicr_customer(hex_file_path):
    """Compare the micro:bit User UICR contents with a hex file.

    Opens the default browser to display an HTML page with the comparison
    output.

    :param hex_file_path: File path to the hex file to compare against.
    """
    with open(hex_file_path, encoding='utf-8') as f:
        file_hex_str = f.readlines()
    flash_hex_str = read_uicr_customer(decode_hex=False)

    html_code = _gen_diff_html('micro:bit', flash_hex_str.splitlines(),
                               'Hex file', file_hex_str)
    _open_temp_html(html_code)
