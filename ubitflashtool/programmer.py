#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions to read data from the micro:bit using PyOCD."""
from pyocd.core.helpers import ConnectHelper


# nRF51 256 KBs of flash starts at address 0
MICROBIT_FLASH_START = 0x00000000
MICROBIT_FLASH_SIZE_BYTES = 256 * 1024
MICROBIT_FLASH_END = MICROBIT_FLASH_START + MICROBIT_FLASH_SIZE_BYTES

# nRF51 User Information Configuration Registers
UICR_START = 0x10001000
UICR_SIZE_BYTES = 0x100
UICR_END = UICR_START + UICR_SIZE_BYTES

# UICR reserved data for customer
UICR_CUSTOMER_OFFSET = 0x80
UICR_CUSTOMER_SIZE_BYTES = 32 * 4
UICR_CUSTOMER_START = UICR_START + UICR_CUSTOMER_OFFSET
UICR_CUSTOMER_END = UICR_CUSTOMER_START + UICR_CUSTOMER_SIZE_BYTES

# Assumes code attached to fixed location instead of using the filesystem
PYTHON_CODE_START = 0x3E000
PYTHON_CODE_END = 0x40000

# MicroPython will contain unnecessary empty space between end of interpreter
# and begginning of code at a fixed location, assumes no file system used
MICROPYTHON_START = 0x0
MICROPYTHON_END = PYTHON_CODE_START


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
    read_data = None
    try:
        with ConnectHelper.session_with_chosen_probe(
            blocking=False,
            auto_unlock=False,
            halt_on_connect=True,
            resume_on_disconnect=True,
        ) as session:
            board = session.board
            target = board.target
            read_data = target.read_memory_block8(address, count)
    except Exception as e:
        raise Exception(
            "{}\nDid not find any connected boards.".format(str(e))
        )
    return read_data


def read_flash(address=MICROBIT_FLASH_START, count=MICROBIT_FLASH_SIZE_BYTES):
    """Read the contents of the micro:bit flash memory.

    Start from the 'address' argument for as many bytes as indicated by the
    'count' argument.

    :param address: Integer indicating the start address to read.
    :param count: Integer indicating how many bytes to read.
    :return: A list of integers, each representing a byte of data.
    """
    last_byte = address + count
    if (
        not (MICROBIT_FLASH_START <= address < MICROBIT_FLASH_END)
        or last_byte > MICROBIT_FLASH_END
    ):
        raise ValueError(
            "Cannot read a flash location out of boundaries.\n"
            "Reading from {} to {},\nlimits from {} to {}".format(
                address, last_byte, MICROBIT_FLASH_START, MICROBIT_FLASH_END
            )
        )
    return _read_continuous_memory(address=address, count=count)


def read_uicr(address=UICR_START, count=UICR_SIZE_BYTES):
    """Read the contents of the micro:bit UICR memory.

    Start from the 'address' argument for as many bytes as indicated by the
    'count' argument.

    :param address: Integer indicating the start address to read.
    :param count: Integer indicating how many bytes to read.
    :return: A list of integers, each representing a byte of data.
    """
    last_byte = address + count
    if not (UICR_START <= address < UICR_END) or (address + count) > UICR_END:
        raise ValueError(
            "Cannot read a UICR location out of boundaries.\n"
            "Reading from {} to {},\nlimits from {} to {}".format(
                address, last_byte, UICR_START, UICR_END
            )
        )
    return _read_continuous_memory(address=address, count=count)
