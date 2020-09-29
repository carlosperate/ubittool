#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions to read data from the micro:bit using PyOCD."""
from pyocd.core.helpers import ConnectHelper


# nRF51 256 KBs of flash starts at address 0
MICROBIT_FLASH_START = {
    "9900": 0x00000000,
    "9901": 0x00000000,
    "9903": 0x00000000,
    "9904": 0x00000000,
}
MICROBIT_FLASH_SIZE_BYTES = {
    "9900": 256 * 1024,
    "9901": 256 * 1024,
    "9903": 512 * 1024,
    "9904": 512 * 1024,
}
MICROBIT_FLASH_END = {
    "9900": MICROBIT_FLASH_START["9900"] + MICROBIT_FLASH_SIZE_BYTES["9900"],
    "9901": MICROBIT_FLASH_START["9901"] + MICROBIT_FLASH_SIZE_BYTES["9901"],
    "9903": MICROBIT_FLASH_START["9903"] + MICROBIT_FLASH_SIZE_BYTES["9903"],
    "9904": MICROBIT_FLASH_START["9904"] + MICROBIT_FLASH_SIZE_BYTES["9904"],
}

# nRF51 User Information Configuration Registers
UICR_START = {
    "9900": 0x10001000,
    "9901": 0x10001000,
    "9903": 0x10001000,
    "9904": 0x10001000,
}
UICR_SIZE_BYTES = {
    "9900": 0x100,
    "9901": 0x100,
    "9903": 0x100,
    "9904": 0x100,
}
UICR_END = {
    "9900": UICR_START["9900"] + UICR_SIZE_BYTES["9900"],
    "9901": UICR_START["9901"] + UICR_SIZE_BYTES["9901"],
    "9903": UICR_START["9903"] + UICR_SIZE_BYTES["9903"],
    "9904": UICR_START["9904"] + UICR_SIZE_BYTES["9904"],
}

# UICR reserved data for customer
UICR_CUSTOMER_OFFSET = 0x80
UICR_CUSTOMER_SIZE_BYTES = 32 * 4
UICR_CUSTOMER_START = UICR_START["9900"] + UICR_CUSTOMER_OFFSET
UICR_CUSTOMER_END = UICR_CUSTOMER_START + UICR_CUSTOMER_SIZE_BYTES

# Assumes code attached to fixed location instead of using the filesystem
PYTHON_CODE_START = 0x3E000
PYTHON_CODE_END = 0x40000

# MicroPython will contain unnecessary empty space between end of interpreter
# and begginning of code at a fixed location, assumes no file system used
MICROPYTHON_START = 0x0
MICROPYTHON_END = PYTHON_CODE_START


class MicrobitMicrocontroller(object):
    """Read data from main microcontroller on the micro:bit board."""

    def __init__(self):
        """Declare all instance variables."""
        self.session = None
        self.board = None
        self.target = None
        self.board_id = None
        self.flash_start = None
        self.flash_size = None
        self.flash_end = None
        self.uicr_start = None
        self.uicr_size = None
        self.uicr_end = None
        # TODO: Set the UICR values for the different board IDs
        self.uicr_customer_start = UICR_CUSTOMER_START
        self.uicr_customer_size = UICR_CUSTOMER_SIZE_BYTES
        self.uicr_customer_end = UICR_CUSTOMER_END

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
            if self.board_id not in MICROBIT_FLASH_START:
                raise Exception("Incompatible board ID from connected device.")
            self.flash_start = MICROBIT_FLASH_START[self.board_id]
            self.flash_size = MICROBIT_FLASH_SIZE_BYTES[self.board_id]
            self.flash_end = self.flash_start + self.flash_size
            self.uicr_start = UICR_START[self.board_id]
            self.uicr_size = UICR_SIZE_BYTES[self.board_id]
            self.uicr_end = self.uicr_start + self.uicr_size

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
            address = self.flash_start
        if count is None:
            count = self.flash_size

        end = address + count
        if (
            not (self.flash_start <= address < self.flash_end)
            or end > self.flash_end
        ):
            raise ValueError(
                "Cannot read a flash address out of boundaries.\n"
                "Reading from {} to {},\nlimits are from {} to {}".format(
                    address, end, self.flash_start, self.flash_end
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
            address = self.uicr_start
        if count is None:
            count = self.uicr_size

        end = address + count
        if (
            not (self.uicr_start <= address < self.uicr_end)
            or end > self.uicr_end
        ):
            raise ValueError(
                "Cannot read a UICR location out of boundaries.\n"
                "Reading from {} to {},\nlimits are from {} to {}".format(
                    address, end, self.uicr_start, self.uicr_end
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
        return self.read_uicr(
            address=self.uicr_customer_start, count=self.uicr_customer_size
        )
