#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions to read data from the micro:bit using PyOCD."""
from collections import namedtuple

from pyocd.core.helpers import ConnectHelper


MemoryRegions = namedtuple(
    "MemoryRegions",
    [
        "flash_start",
        "flash_size",
        "ram_start",
        "ram_size",
        "uicr_start",
        "uicr_size",
        "uicr_customer_offset",
        "uicr_customer_size",
    ],
)

MEM_REGIONS_MB_V1 = MemoryRegions(
    flash_start=0x0000_0000,
    flash_size=256 * 1024,
    ram_start=0x2000_0000,
    ram_size=16 * 1024,
    uicr_start=0x1000_1000,
    uicr_size=0x100,
    uicr_customer_offset=0x80,
    uicr_customer_size=0x100 - 0x80,
)
MEM_REGIONS_MB_V2 = MemoryRegions(
    flash_start=0x0000_0000,
    flash_size=512 * 1024,
    ram_start=0x2000_0000,
    ram_size=128 * 1024,
    uicr_start=0x1000_1000,
    uicr_size=0x308,
    uicr_customer_offset=0x80,
    uicr_customer_size=0x200 - 0x80,
)
MICROBIT_MEM_REGIONS = {
    "9900": MEM_REGIONS_MB_V1,
    "9901": MEM_REGIONS_MB_V1,
    "9903": MEM_REGIONS_MB_V2,
    "9904": MEM_REGIONS_MB_V2,
    "9905": MEM_REGIONS_MB_V2,
    "9906": MEM_REGIONS_MB_V2,
}

# Assumes code attached to fixed location instead of using the filesystem
PYTHON_CODE_START = 0x3E000
PYTHON_CODE_END = 0x40000

# MicroPython will contain unnecessary empty space between end of interpreter
# and begginning of code at a fixed location, assumes no file system used
MICROPYTHON_START = 0x0
MICROPYTHON_END = PYTHON_CODE_START


class MicrobitMcu(object):
    """Read data from main microcontroller on the micro:bit board."""

    def __init__(self):
        """Declare all instance variables."""
        self.session = None
        self.board = None
        self.target = None
        self.board_id = None
        self.mem = None

    def _connect(self):
        """Connect PyOCD to the main micro:bit microcontroller."""
        if not self.session:
            try:
                self.session = ConnectHelper.session_with_chosen_probe(
                    blocking=False,
                    auto_unlock=False,
                    halt_on_connect=True,
                    resume_on_disconnect=True,
                )
                if self.session is None:
                    raise Exception("Could not open the debugger session.")
                self.session.open()
                self.board = self.session.board
                self.target = self.board.target
                self.board_id = self.board.unique_id[:4]
            except Exception as e:
                raise Exception(
                    "{}\n{}\n".format(str(e), "-" * 70)
                    + "Error: Did not find any connected boards."
                )
            if self.board_id not in MICROBIT_MEM_REGIONS:
                self._disconnect()
                raise Exception("Incompatible board ID from connected device.")
            self.mem = MICROBIT_MEM_REGIONS[self.board_id]

    def _disconnect(self):
        """."""
        if self.session:
            self.session.close()
        self.session = None

    def __enter__(self):
        """."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """."""
        self._disconnect()

    def _read_memory(self, address=None, count=None):
        """Read any continuous memory area from the micro:bit.

        Reads the contents of any micro:bit continuous memory area, starting
        from the 'address' argument for as many bytes as indicated by 'count'.
        There is no input sanitation in this function and is the responsibility
        of the caller to input values within range of the target board or deal
        with any exceptions raised by PyOCD.

        :param address: Integer indicating the start address to read.
        :param count: Integer, how many bytes to read.
        :return: A list of integers, each representing a byte of data.
        """
        self._connect()
        return self.target.read_memory_block8(address, count)

    def read_flash(self, address=None, count=None):
        """Read data from flash and returns it as a list of bytes.

        :param address: Integer indicating the start address to read.
        :param count: Integer indicating how many bytes to read.
        :return: The start address from the read and a list of integers,
            each representing a byte of data.
        """
        self._connect()

        if address is None:
            address = self.mem.flash_start
        if count is None:
            count = self.mem.flash_size
        flash_end = self.mem.flash_start + self.mem.flash_size

        end = address + count
        if (
            not (self.mem.flash_start <= address < flash_end)
            or end > flash_end
        ):
            raise ValueError(
                "Cannot read a flash address out of boundaries.\n"
                "Reading from {} to {},\nlimits are from {} to {}".format(
                    address, end, self.mem.flash_start, flash_end,
                )
            )

        return address, self._read_memory(address=address, count=count)

    def read_ram(self, address=None, count=None):
        """Read the contents of the micro:bit RAM memory.

        :param address: Integer indicating the start address to read.
        :param count: Integer indicating how many bytes to read.
        :return: The start address from the read and a list of integers,
            each representing a byte of data.
        """
        self._connect()

        if address is None:
            address = self.mem.ram_start
        if count is None:
            count = self.mem.ram_size
        ram_end = self.mem.ram_start + self.mem.ram_size

        last_byte = address + count
        if (
            not (self.mem.ram_start <= address < ram_end)
            or last_byte > ram_end
        ):
            raise ValueError(
                "Cannot read a RAM location out of boundaries.\n"
                "Reading from {} to {},\nlimits from {} to {}".format(
                    address, last_byte, self.mem.ram_start, ram_end
                )
            )
        return address, self._read_memory(address=address, count=count)

    def read_uicr(self, address=None, count=None):
        """Read data from UICR and returns it as a list of bytes.

        :param address: Integer indicating the start address to read.
        :param count: Integer indicating how many bytes to read.
        :return: The start address from the read and a list of integers,
            each representing a byte of data.
        """
        self._connect()

        if address is None:
            address = self.mem.uicr_start
        if count is None:
            count = self.mem.uicr_size
        uicr_end = self.mem.uicr_start + self.mem.uicr_size

        end = address + count
        if not (self.mem.uicr_start <= address < uicr_end) or end > uicr_end:
            raise ValueError(
                "Cannot read a UICR location out of boundaries.\n"
                "Reading from {} to {},\nlimits are from {} to {}".format(
                    address, end, self.mem.uicr_start, uicr_end,
                )
            )

        return address, self._read_memory(address=address, count=count)

    def read_uicr_customer(self):
        """Read all the UICR customer data and return it as a list of bytes.

        :param address: Integer indicating the start address to read.
        :param count: Integer indicating how many bytes to read.
        :return: The start address from the read and a list of integers,
            each representing a byte of data.
        """
        self._connect()

        return self.read_uicr(
            address=self.mem.uicr_start + self.mem.uicr_customer_offset,
            count=self.mem.uicr_customer_size,
        )
