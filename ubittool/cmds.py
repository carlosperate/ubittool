#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commands to carry out all the actions for uBitTool control.

This module internal functions can read any memory location from the micro:bit
via PyOCD, which uses the CMSIS interface provided by DAPLink.

The exposed function for the command line and GUI interfaces can safely read
areas of Flash (full flash, MicroPython, Python code) and UICR (to read the
customer data), and format the output into Intel Hex, a nicely decoded string
format, or human readable text (for the Python code).
"""
import os
import sys
import tempfile
import webbrowser
from io import StringIO
from threading import Timer
from difflib import HtmlDiff, unified_diff
from traceback import format_exc

from intelhex import IntelHex
from uflash import extract_script

from ubittool import programmer


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
        i_hex.tofile(fake_file, format="hex")
    except IOError as e:
        sys.stderr.write("ERROR: File write: {}\n{}".format(fake_file, str(e)))
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
        sys.stderr.write("ERROR: File write: {}\n{}".format(fake_file, str(e)))
        return

    pretty_hex_str = fake_file.getvalue()
    fake_file.close()
    return pretty_hex_str


#
# Reading data commands
#
def read_flash_hex(decode_hex=False, **kwargs):
    """Read data from the flash memory and return as a hex string.

    Read as a number of bytes of the micro:bit flash from the given address.
    Can return it in Intel Hex format or a pretty formatted and decoded hex
    string.

    :param address: Integer indicating the start address to read.
    :param count: Integer indicating hoy many bytes to read.
    :param decode_hex: True selects nice decoded format, False selects Intel
            Hex format.
    :return: String with the hex formatted as indicated.
    """
    with programmer.MicrobitMcu() as mb:
        start_address, flash_data = mb.read_flash(**kwargs)
    to_hex = _bytes_to_pretty_hex if decode_hex else _bytes_to_intel_hex
    return to_hex(flash_data, offset=start_address)


def read_ram_hex(decode_hex=False, **kwargs):
    """Read data from RAM and return as a hex string.

    Read as a number of bytes of the micro:bit RAM from the given address.
    Can return it in Intel Hex format or a pretty formatted and decoded hex
    string.

    :param address: Integer indicating the start address to read.
    :param count: Integer indicating hoy many bytes to read.
    :param decode_hex: True selects nice decoded format, False selects Intel
            Hex format.
    :return: String with the hex formatted as indicated.
    """
    with programmer.MicrobitMcu() as mb:
        start_address, ram_data = mb.read_ram(**kwargs)
    to_hex = _bytes_to_pretty_hex if decode_hex else _bytes_to_intel_hex
    return to_hex(ram_data, offset=start_address)


def read_uicr_hex(decode_hex=False):
    """Read the full UICR data.

    :return: String with the nicely decoded UICR area data.
    """
    with programmer.MicrobitMcu() as mb:
        start_address, uicr_data = mb.read_uicr()
    to_hex = _bytes_to_pretty_hex if decode_hex else _bytes_to_intel_hex
    return to_hex(uicr_data, offset=start_address)


def read_uicr_customer_hex(decode_hex=False):
    """Read the UICR Customer data.

    :return: String with the nicely decoded UICR Customer area data.
    """
    with programmer.MicrobitMcu() as mb:
        start_address, uicr_data = mb.read_uicr_customer()
    to_hex = _bytes_to_pretty_hex if decode_hex else _bytes_to_intel_hex
    return to_hex(uicr_data, offset=start_address)


def read_micropython():
    """Read the MicroPython runtime from the micro:bit flash.

    :return: String with Intel Hex format for the MicroPython runtime.
    """
    with programmer.MicrobitMcu() as mb:
        start_address, flash_data = mb.read_flash(
            address=programmer.MICROPYTHON_START,
            count=programmer.MICROPYTHON_END - programmer.MICROPYTHON_START,
        )
    return _bytes_to_intel_hex(flash_data, offset=start_address)


def read_python_code():
    """Read the MicroPython user code from the micro:bit flash.

    :return: String with the MicroPython code.
    """
    with programmer.MicrobitMcu() as mb:
        start_address, flash_data = mb.read_flash(
            address=programmer.PYTHON_CODE_START,
            count=(programmer.PYTHON_CODE_END - programmer.PYTHON_CODE_START),
        )
    py_code_hex = _bytes_to_intel_hex(flash_data, offset=start_address)
    try:
        python_code = extract_script(py_code_hex)
    except Exception:
        sys.stderr.write(format_exc() + "\n" + "-" * 70 + "\n")
        raise Exception("Could not decode the MicroPython code from flash")
    return python_code


#
# Hex comparison commands
#
def _open_temp_html(html_str):
    """Create a temporary html file, open it in a browser and delete it.

    :param html_str: String to write to the temporary file.
    """
    fd, path = tempfile.mkstemp(suffix=".html")
    try:
        with os.fdopen(fd, "w") as tmp:
            # do stuff with temp file
            tmp.write(html_str)
        webbrowser.open("file://{}".format(os.path.realpath(path)))
    finally:
        # It can take a bit of time for the browser to open the file,
        # so wait some time before deleting it
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
        diff_table=differ.make_table(from_lines, to_lines),
    )
    return filled_template


def compare_full_flash_hex(hex_file_path):
    """Compare the micro:bit flash contents with a hex file.

    Opens the default browser to display an HTML page with the comparison
    output.

    :param hex_file_path: File path to the hex file to compare against.
    """
    with open(hex_file_path, encoding="utf-8") as f:
        file_hex_lines = f.read().splitlines()
    flash_hex_lines = read_flash_hex(decode_hex=False).splitlines()

    html_code = _gen_diff_html(
        "micro:bit", flash_hex_lines, "Hex file", file_hex_lines,
    )
    _open_temp_html(html_code)

    diffs = list(unified_diff(flash_hex_lines, file_hex_lines))
    return 1 if len(diffs) else 0


def compare_uicr_customer(hex_file_path):
    """Compare the micro:bit User UICR contents with a hex file.

    Opens the default browser to display an HTML page with the comparison
    output.

    :param hex_file_path: File path to the hex file to compare against.
    """
    with open(hex_file_path, encoding="utf-8") as f:
        file_hex_str = f.readlines()
    flash_hex_str = read_uicr_customer_hex(decode_hex=False)

    html_code = _gen_diff_html(
        "micro:bit", flash_hex_str.splitlines(), "Hex file", file_hex_str
    )
    _open_temp_html(html_code)
