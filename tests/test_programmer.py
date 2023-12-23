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
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    start_addres1, result_data1 = mb1.read_flash()
    start_addres2, result_data2 = mb2.read_flash()

    assert start_addres1 == 0
    assert result_data2 == data_bytes
    assert start_addres1 == 0
    assert result_data2 == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_flash_with_args(mock_read_memory):
    """Test read_flash() with providedarguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    start_addres1, result_data1 = mb1.read_flash(address=0, count=256 * 1024)
    start_addres2, result_data2 = mb2.read_flash(address=0, count=512 * 1024)

    assert start_addres1 == 0
    assert result_data1 == data_bytes
    assert start_addres2 == 0
    assert result_data2 == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_flash_bad_address(mock_read_memory):
    """Test read_flash() with bad address arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    with pytest.raises(ValueError) as execinfo11:
        start_addres, result_data = mb1.read_flash(address=-1, count=1)
    with pytest.raises(ValueError) as execinfo12:
        start_addres, result_data = mb1.read_flash(
            address=(256 * 1024) + 1, count=1
        )
    with pytest.raises(ValueError) as execinfo21:
        start_addres, result_data = mb2.read_flash(address=-1, count=1)
    with pytest.raises(ValueError) as execinfo22:
        start_addres, result_data = mb2.read_flash(
            address=(512 * 1024) + 1, count=1
        )

    assert "Cannot read a flash address out of" in str(execinfo11.value)
    assert "Cannot read a flash address out of" in str(execinfo12.value)
    assert "Cannot read a flash address out of" in str(execinfo21.value)
    assert "Cannot read a flash address out of" in str(execinfo22.value)


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_flash_bad_count(mock_read_memory):
    """Test read_flash() with bad values in the count argument."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    with pytest.raises(ValueError) as execinfo11:
        start_addres, result_data = mb1.read_flash(
            address=0, count=(256 * 1024) + 1
        )
    with pytest.raises(ValueError) as execinfo12:
        start_addres, result_data = mb1.read_flash(
            address=(256 * 1024) - 10, count=11
        )
    with pytest.raises(ValueError) as execinfo21:
        start_addres, result_data = mb2.read_flash(
            address=0, count=(512 * 1024) + 1
        )
    with pytest.raises(ValueError) as execinfo22:
        start_addres, result_data = mb2.read_flash(
            address=(512 * 1024) - 10, count=11
        )

    assert "Cannot read a flash address out of" in str(execinfo11.value)
    assert "Cannot read a flash address out of" in str(execinfo12.value)
    assert "Cannot read a flash address out of" in str(execinfo21.value)
    assert "Cannot read a flash address out of" in str(execinfo22.value)


###############################################################################
# MicrobitMcu.read_ram()
###############################################################################
@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_ram(mock_read_memory):
    """Test read_ram() with default arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    start_addres1, result_data1 = mb1.read_ram()
    start_addres2, result_data2 = mb2.read_ram()

    assert start_addres1 == 0x2000_0000
    assert result_data2 == data_bytes
    assert start_addres1 == 0x2000_0000
    assert result_data2 == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_ram_with_args(mock_read_memory):
    """Test read_ram() with providedarguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    start_addres1, result_data1 = mb1.read_ram(
        address=0x2000_0000, count=16 * 1024
    )
    start_addres2, result_data2 = mb2.read_ram(
        address=0x2000_0000, count=128 * 1024
    )

    assert start_addres1 == 0x2000_0000
    assert result_data1 == data_bytes
    assert start_addres2 == 0x2000_0000
    assert result_data2 == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_ram_bad_address(mock_read_memory):
    """Test read_ram() with bad address arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    with pytest.raises(ValueError) as execinfo11:
        start_addres, result_data = mb1.read_ram(
            address=0x2000_0000 - 1, count=1
        )
    with pytest.raises(ValueError) as execinfo12:
        start_addres, result_data = mb1.read_ram(
            address=(16 * 1024) + 1, count=1
        )
    with pytest.raises(ValueError) as execinfo21:
        start_addres, result_data = mb2.read_ram(
            address=0x2000_0000 - 1, count=1
        )
    with pytest.raises(ValueError) as execinfo22:
        start_addres, result_data = mb2.read_ram(
            address=(128 * 1024) + 1, count=1
        )

    assert "Cannot read a RAM location out of" in str(execinfo11.value)
    assert "Cannot read a RAM location out of" in str(execinfo12.value)
    assert "Cannot read a RAM location out of" in str(execinfo21.value)
    assert "Cannot read a RAM location out of" in str(execinfo22.value)


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_ram_bad_count(mock_read_memory):
    """Test read_ram() with bad values in the count argument."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    with pytest.raises(ValueError) as execinfo11:
        start_addres, result_data = mb1.read_ram(
            address=0x2000_0000, count=(16 * 1024) + 1
        )
    with pytest.raises(ValueError) as execinfo12:
        start_addres, result_data = mb1.read_ram(
            address=0x2000_0000 + (16 * 1024) - 10, count=11
        )
    with pytest.raises(ValueError) as execinfo21:
        start_addres, result_data = mb2.read_ram(
            address=0x2000_0000, count=(128 * 1024) + 1
        )
    with pytest.raises(ValueError) as execinfo22:
        start_addres, result_data = mb2.read_ram(
            address=0x2000_0000 + (128 * 1024) - 10, count=11
        )

    assert "Cannot read a RAM location out of" in str(execinfo11.value)
    assert "Cannot read a RAM location out of" in str(execinfo12.value)
    assert "Cannot read a RAM location out of" in str(execinfo21.value)
    assert "Cannot read a RAM location out of" in str(execinfo22.value)


###############################################################################
# MicrobitMcu.read_uicr()
###############################################################################
@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_uicr(mock_read_memory):
    """Test read_uicr() with default arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    start_addres1, result_data1 = mb1.read_uicr()
    start_addres2, result_data2 = mb2.read_uicr()

    assert start_addres1 == 0x1000_1000
    assert result_data1 == data_bytes
    assert start_addres2 == 0x1000_1000
    assert result_data2 == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_uicr_with_args(mock_read_memory):
    """Test read_uicr() with providedarguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    start_addres1, result_data1 = mb1.read_uicr(
        address=0x1000_1000, count=0x100
    )
    start_addres2, result_data2 = mb2.read_uicr(
        address=0x1000_1000, count=0x308
    )

    assert start_addres1 == 0x1000_1000
    assert result_data1 == data_bytes
    assert start_addres2 == 0x1000_1000
    assert result_data2 == data_bytes


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_uicr_bad_address(mock_read_memory):
    """Test read_uicr() with bad address arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    with pytest.raises(ValueError) as execinfo11:
        start_addres, result_data = mb1.read_uicr(
            address=0x1000_1000 - 1, count=1
        )
    with pytest.raises(ValueError) as execinfo12:
        start_addres, result_data = mb1.read_uicr(address=0x100 + 1, count=1)
    with pytest.raises(ValueError) as execinfo21:
        start_addres, result_data = mb2.read_uicr(
            address=0x1000_1000 - 1, count=1
        )
    with pytest.raises(ValueError) as execinfo22:
        start_addres, result_data = mb2.read_uicr(address=0x308 + 1, count=1)

    assert "Cannot read a UICR location out of" in str(execinfo11.value)
    assert "Cannot read a UICR location out of" in str(execinfo12.value)
    assert "Cannot read a UICR location out of" in str(execinfo21.value)
    assert "Cannot read a UICR location out of" in str(execinfo22.value)


@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_uicr_bad_count(mock_read_memory):
    """Test read_uicr() with bad values in the count argument."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    with pytest.raises(ValueError) as execinfo11:
        start_addres, result_data = mb1.read_uicr(
            address=0x1000_1000, count=(16 * 1024) + 1
        )
    with pytest.raises(ValueError) as execinfo12:
        start_addres, result_data = mb1.read_uicr(
            address=0x1000_1000 + (16 * 1024) - 10, count=11
        )
    with pytest.raises(ValueError) as execinfo21:
        start_addres, result_data = mb2.read_uicr(
            address=0x1000_1000, count=(128 * 1024) + 1
        )
    with pytest.raises(ValueError) as execinfo22:
        start_addres, result_data = mb2.read_uicr(
            address=0x1000_1000 + (128 * 1024) - 10, count=11
        )

    assert "Cannot read a UICR location out of" in str(execinfo11.value)
    assert "Cannot read a UICR location out of" in str(execinfo12.value)
    assert "Cannot read a UICR location out of" in str(execinfo21.value)
    assert "Cannot read a UICR location out of" in str(execinfo22.value)


###############################################################################
# MicrobitMcu.read_uicr_customer()
###############################################################################
@mock.patch.object(programmer.MicrobitMcu, "_read_memory", autospec=True)
def test_read_uicr_customer(mock_read_memory):
    """Test read_uiread_uicr_customercr() with default arguments."""
    data_bytes = bytes([x for x in range(256)] * 4)
    mock_read_memory.return_value = data_bytes
    mb1 = MicrobitMcu_instance(v=1)
    mb2 = MicrobitMcu_instance(v=2)

    start_addres1, result_data1 = mb1.read_uicr_customer()
    start_addres2, result_data2 = mb2.read_uicr_customer()

    assert start_addres1 == 0x1000_1080
    assert result_data1 == data_bytes
    assert start_addres2 == 0x1000_1080
    assert result_data2 == data_bytes


###############################################################################
# find_microbit_ids()
###############################################################################
@mock.patch(
    "ubittool.programmer.ConnectHelper.get_all_connected_probes", autospec=True
)
def test_find_microbit_ids(mock_get_all_connected_probes):
    """Test find_microbit_ids()."""

    class MockProbe:
        def __init__(self, _id):
            self.unique_id = _id

    mock_get_all_connected_probes.return_value = [
        MockProbe("9900"),
        MockProbe("9901"),
        MockProbe("9903"),
        MockProbe("9904"),
        MockProbe("9905"),
    ]

    ids = programmer.find_microbit_ids()

    assert ids == ("9900", "9901", "9903", "9904", "9905")


@mock.patch(
    "ubittool.programmer.ConnectHelper.get_all_connected_probes", autospec=True
)
def test_find_microbit_ids_empty(mock_get_all_connected_probes):
    """Test find_microbit_ids()."""
    mock_get_all_connected_probes.return_value = []

    ids = programmer.find_microbit_ids()

    assert ids == tuple()
