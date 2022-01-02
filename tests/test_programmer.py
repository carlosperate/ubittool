#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for programmer.py module."""
import types
from unittest import mock

import pytest

from ubittool import programmer


###############################################################################
# Helpers
###############################################################################
def MicrobitMcu_instance(v=1):
    """Patched version for v1."""

    def _connec_v1(self):
        self.mem = programmer.MEM_REGIONS_MB_V1

    def _connec_v2(self):
        self.mem = programmer.MEM_REGIONS_MB_V2

    mb = programmer.MicrobitMcu()
    if v == 1:
        mb._connect = types.MethodType(_connec_v1, mb)
    elif v == 2:
        mb._connect = types.MethodType(_connec_v2, mb)
    return mb


###############################################################################
# MicrobitMcu.read_flash()
###############################################################################
@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_flash(mock_read_memory):
    """Test read_flash() with default arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb = MicrobitMcu_instance(v=1)

    start_addres, result_data = mb.read_flash()

    assert start_addres == 0
    assert result_data == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_flash_with_args(mock_read_memory):
    """Test read_flash() with providedarguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb = MicrobitMcu_instance(v=1)

    start_addres, result_data = mb.read_flash(address=0, count=256 * 1024)

    assert start_addres == 0
    assert result_data == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_flash_bad_address(mock_read_memory):
    """Test read_flash() with bad address arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb = MicrobitMcu_instance(v=1)

    with pytest.raises(ValueError) as execinfo1:
        start_addres, result_data = mb.read_flash(address=-1, count=1)
    with pytest.raises(ValueError) as execinfo2:
        start_addres, result_data = mb.read_flash(
            address=(256 * 1024) + 1, count=1
        )

    assert "Cannot read a flash address out of" in str(execinfo1.value)
    assert "Cannot read a flash address out of" in str(execinfo2.value)


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_flash_bad_count(mock_read_memory):
    """Test read_flash() with bad values in the count argument."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb = MicrobitMcu_instance(v=1)

    with pytest.raises(ValueError) as execinfo1:
        start_addres, result_data = mb.read_flash(
            address=0, count=(256 * 1024) + 1
        )
    with pytest.raises(ValueError) as execinfo2:
        start_addres, result_data = mb.read_flash(
            address=(256 * 1024) - 10, count=11
        )

    assert "Cannot read a flash address out of" in str(execinfo2.value)
    assert "Cannot read a flash address out of" in str(execinfo1.value)
