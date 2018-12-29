#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Tests for GUI."""
import sys

import pytest

from ubitflashtool.gui import UBitFlashToolWindow

if sys.version_info.major == 3:
    from tkinter import TclError
elif sys.version_info.major == 2:
    from Tkinter import TclError


@pytest.fixture()
def gui_window():
    """Fixture to create and destroy GUI window."""
    app = UBitFlashToolWindow()
    app.wait_visibility()
    yield app
    if app:
        try:
            app.winfo_exists()
        except TclError:
            # App destroyed, nothing left to do
            pass
        else:
            app.update()
            app.destroy()


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
                label = menu.entrycget(x, 'label')
            except TclError:
                pass
            else:
                labels.append(label)
        return labels

    menu_bar = gui_window.menu_bar
    assert menu_bar.winfo_exists(), 'Menu bar exists'

    top_labels = get_labels(menu_bar)
    assert 'File' == top_labels[file_index], 'File present in window menu'
    assert 'micro:bit' == top_labels[microbit_index], \
           'micro:bit present in window menu'
    assert 'nrf' == top_labels[nrf_index], 'nrf present in window menu'

    file_labels = get_labels(menu_bar.winfo_children()[file_index])
    assert len(file_labels) == 3, 'File menu has 3 items'
    assert 'Open' == file_labels[0], 'Open present in File menu'
    assert 'Save As' == file_labels[1], 'Save As present in File menu'
    assert 'Exit' == file_labels[2], 'Exit present in File menu'

    microbit_labels = get_labels(menu_bar.winfo_children()[microbit_index])
    assert len(microbit_labels) == 2, 'micro:bit menu has 3 items'
    assert 'Read MicroPython code' == microbit_labels[0], \
           'Read Code present in micro:bit menu'
    assert 'Read MicroPython runtime' == microbit_labels[1], \
           'Read Runtime present in micro:bit menu'

    nrf_labels = get_labels(menu_bar.winfo_children()[nrf_index])
    assert len(nrf_labels) == 5, 'nrf menu has 5 items'
    assert 'Read full flash contents (Intel Hex)' == nrf_labels[0], \
           'Read Flash Hex present in nrf menu'
    assert 'Read full flash contents (Pretty Hex)' == nrf_labels[1], \
           'Read Flash Pretty present in nrf menu'
    assert 'Read UICR Customer' == nrf_labels[2], \
           'Read UICR present in nrf menu'
    assert 'Compare full flash contents (Intel Hex)' == nrf_labels[3], \
           'Compare Flash present in nrf menu'
    assert 'Compare UICR Customer (Intel Hex)' == nrf_labels[4], \
           'Compare UICR in nrf menu'
