#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for GUI."""
import sys
from unittest import mock
import tkinter

import pytest

from ubittool.gui import UBitToolWindow, open_gui


@pytest.fixture()
def gui_window():
    """Fixture to create and destroy GUI window."""
    app = UBitToolWindow()
    app.wait_visibility()
    yield app
    if app:
        try:
            app.winfo_exists()
        except tkinter.TclError:
            # App destroyed, nothing left to do
            pass
        else:
            app.update()
            app.destroy()


def test_window_console(capsys):
    """Test the std our and err go to the console widget."""
    std_out_content = "This is content in the std out\n"
    std_err_content = "And this goes to the std err\n"

    with capsys.disabled():
        app = UBitToolWindow()
        # app.wait_visibility()

        sys.stdout.write(std_out_content)
        sys.stderr.write(std_err_content)
        console_widget_content = app.console.get(1.0, "end")

        app.update()
        app.destroy()

    assert std_out_content in console_widget_content
    assert std_err_content in console_widget_content


def test_menu_bar_presence(gui_window):
    """Test that the window menu is present with all expected options."""
    file_index = 0
    microbit_index = 1
    nrf_index = 2

    def get_labels(menu):
        """Get all the labels from a menu."""
        menu_len = menu.index("end") + 1
        labels = []
        for x in range(menu_len):
            try:
                label = menu.entrycget(x, "label")
            except tkinter.TclError:
                pass
            else:
                labels.append(label)
        return labels

    menu_bar = gui_window.menu_bar
    assert menu_bar.winfo_exists(), "Menu bar exists"

    top_labels = get_labels(menu_bar)
    assert "File" == top_labels[file_index], "File present in window menu"
    assert (
        "micro:bit" == top_labels[microbit_index]
    ), "micro:bit present in window menu"
    assert "nrf" == top_labels[nrf_index], "nrf present in window menu"

    file_labels = get_labels(menu_bar.winfo_children()[file_index])
    assert len(file_labels) == 3, "File menu has 3 items"
    assert "Open" == file_labels[0], "Open present in File menu"
    assert "Save As" == file_labels[1], "Save As present in File menu"
    assert "Exit" == file_labels[2], "Exit present in File menu"

    microbit_labels = get_labels(menu_bar.winfo_children()[microbit_index])
    assert len(microbit_labels) == 2, "micro:bit menu has 3 items"
    assert (
        "Read MicroPython code" == microbit_labels[0]
    ), "Read Code present in micro:bit menu"
    assert (
        "Read MicroPython runtime" == microbit_labels[1]
    ), "Read Runtime present in micro:bit menu"

    nrf_labels = get_labels(menu_bar.winfo_children()[nrf_index])
    assert len(nrf_labels) == 8, "nrf menu has 6 items"
    assert (
        "Read full flash contents (Intel Hex)" == nrf_labels[0]
    ), "Read Flash Hex present in nrf menu"
    assert (
        "Read full flash contents (Pretty Hex)" == nrf_labels[1]
    ), "Read Flash Pretty present in nrf menu"
    assert (
        "Read full RAM contents (Intel Hex)" == nrf_labels[2]
    ), "Read RAM Hex present in nrf menu"
    assert (
        "Read full RAM contents (Pretty Hex)" == nrf_labels[3]
    ), "Read RAM Pretty present in nrf menu"
    assert "Read UICR" == nrf_labels[4], "Read UICR present in nrf menu"
    assert (
        "Read UICR Customer" == nrf_labels[5]
    ), "Read UICR Customer present in nrf menu"
    assert (
        "Compare full flash contents (Intel Hex)" == nrf_labels[6]
    ), "Compare Flash present in nrf menu"
    assert (
        "Compare UICR Customer (Intel Hex)" == nrf_labels[7]
    ), "Compare UICR in nrf menu"


@mock.patch("ubittool.gui.cmds.read_python_code", autospec=True)
def test_read_python_code(mock_read_python_code, gui_window):
    """Tests the READ_CODE command."""
    python_code = "The Python code from the flash"
    mock_read_python_code.return_value = python_code

    gui_window.ubit_menu.invoke(0)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert python_code == editor_content
    assert mock_read_python_code.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_CODE
    )


@mock.patch("ubittool.gui.cmds.read_micropython", autospec=True)
def test_read_micropython(mock_read_micropython, gui_window):
    """Tests the READ_UPY command."""
    upy_hex = "The MicroPython runtime in Intel Hex format data"
    mock_read_micropython.return_value = upy_hex

    gui_window.ubit_menu.invoke(1)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert upy_hex == editor_content
    assert mock_read_micropython.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_UPY
    )


@mock.patch("ubittool.gui.cmds.read_flash_hex", autospec=True)
def test_read_full_flash_intel(mock_read_flash_hex, gui_window):
    """Tests the READ_FLASH_HEX command."""
    flash_data = "The full flash in Intel Hex format data"
    mock_read_flash_hex.return_value = flash_data

    gui_window.nrf_menu.invoke(0)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert flash_data == editor_content
    assert mock_read_flash_hex.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_FLASH_HEX
    )


@mock.patch("ubittool.gui.cmds.read_flash_hex", autospec=True)
def test_read_full_flash_pretty(mock_read_flash_hex, gui_window):
    """Tests the READ_FLASH_PRETTY command."""
    flash_data = "The full flash in pretty format data"
    mock_read_flash_hex.return_value = flash_data

    gui_window.nrf_menu.invoke(1)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert flash_data == editor_content
    assert mock_read_flash_hex.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_FLASH_PRETTY
    )


@mock.patch("ubittool.gui.cmds.read_ram_hex", autospec=True)
def test_read_ram_intel(mock_read_ram_hex, gui_window):
    """Tests the CMD_READ_RAM_HEX command."""
    ram_data = "The full RAM in Intel Hex format data"
    mock_read_ram_hex.return_value = ram_data

    gui_window.nrf_menu.invoke(2)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert ram_data == editor_content
    assert mock_read_ram_hex.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_RAM_HEX
    )


@mock.patch("ubittool.gui.cmds.read_ram_hex", autospec=True)
def test_read_ram_pretty(mock_read_ram_hex, gui_window):
    """Tests the CMD_READ_RAM_PRETTY command."""
    ram_data = "The full RAM in pretty format data"
    mock_read_ram_hex.return_value = ram_data

    gui_window.nrf_menu.invoke(3)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert ram_data == editor_content
    assert mock_read_ram_hex.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_RAM_PRETTY
    )


@mock.patch("ubittool.gui.cmds.read_uicr_hex", autospec=True)
def test_read_uicr(mock_read_uicr, gui_window):
    """Tests the READ_UICR command."""
    uicr_data = "The UICR data"
    mock_read_uicr.return_value = uicr_data

    gui_window.nrf_menu.invoke(4)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert uicr_data == editor_content
    assert mock_read_uicr.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_UICR
    )


@mock.patch("ubittool.gui.cmds.read_uicr_customer_hex", autospec=True)
def test_read_uicr_customer(mock_read_uicr_customer, gui_window):
    """Tests the READ_UICR_CUSTOMER command."""
    uicr_data = "The UICR CUSTOMER data"
    mock_read_uicr_customer.return_value = uicr_data

    gui_window.nrf_menu.invoke(5)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert uicr_data == editor_content
    assert mock_read_uicr_customer.call_count == 1
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_READ_UICR_CUSTOMER
    )


@mock.patch("ubittool.gui.cmds.compare_full_flash_hex", autospec=True)
@mock.patch("ubittool.gui.tkFileDialog.askopenfilename", autospec=True)
def test_compare_full_flash_intel(
    mock_compare_full_flash, mock_open_file, gui_window
):
    """Tests the READ_UICR command."""
    mock_open_file.return_value = "/some/path"

    gui_window.nrf_menu.invoke(7)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert mock_compare_full_flash.call_count == 1
    assert editor_content == "Diff content loaded in default browser."
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_COMPARE_FLASH
    )


@mock.patch("ubittool.gui.cmds.compare_uicr_customer", autospec=True)
@mock.patch("ubittool.gui.tkFileDialog.askopenfilename", autospec=True)
def test_compare_uicr_customer(
    mock_compare_uicr_customer, mock_open_file, gui_window
):
    """Tests the READ_UICR command."""
    mock_open_file.return_value = "/some/path"

    gui_window.nrf_menu.invoke(8)

    editor_content = gui_window.text_viewer.get(1.0, "end-1c")
    assert mock_compare_uicr_customer.call_count == 1
    assert editor_content == "Diff content loaded in default browser."
    assert gui_window.cmd_title.cmd_title.get() == "Command: {}".format(
        gui_window.CMD_COMPARE_UICR
    )


@mock.patch("ubittool.gui.UBitToolWindow", autospec=True)
def test_open_gui(mock_window):
    """Test the app instance is created and main loop invoked."""
    open_gui()

    assert mock_window.return_value.lift.call_count == 1
    assert mock_window.return_value.mainloop.call_count == 1


def test_quit():
    """Test that when the window is closed it deactivates the console."""
    app = UBitToolWindow()
    app.wait_visibility()

    assert sys.stdout != sys.__stdout__
    assert sys.stderr != sys.__stderr__

    app.app_quit()

    assert sys.stdout == sys.__stdout__
    assert sys.stderr == sys.__stderr__
    try:
        app.winfo_exists()
    except tkinter.TclError:
        # App destroyed, nothing left to do
        assert True, "Window was already destroyed"
    else:
        raise AssertionError("Window is not destroyed")
