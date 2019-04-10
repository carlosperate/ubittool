#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for cli.py."""
import os
from unittest import mock

from click.testing import CliRunner
import pytest

from ubitflashtool import cli, cmds


@pytest.fixture
def check_no_board_connected():
    """Check that there is no mbed board that PyOCD can connect to."""
    try:
        cmds._read_continuous_memory(address=0x00, count=16)
    except Exception:
        # Good: Exception raised if no board is found
        pass
    else:
        raise Exception("Found an Mbed device connected, please unplug.")


@mock.patch("ubitflashtool.cli.os.path.exists", autospec=True)
@mock.patch("ubitflashtool.cli.click.echo", autospec=True)
@mock.patch("ubitflashtool.cli.sys.exit", autospec=True)
def test_file_checker(mock_exit, mock_echo, mock_exists):
    """Test the file checker perform the required checks and prints info."""
    mock_exists.return_value = False

    cli._file_checker("subject", "file/path.py")

    mock_exists.assert_called_once_with("file/path.py")
    assert mock_echo.call_count == 1
    assert "subject will be written to: file/path.py" in mock_echo.call_args[0]
    assert mock_exit.call_count == 0


@mock.patch("ubitflashtool.cli.os.path.exists", autospec=True)
@mock.patch("ubitflashtool.cli.click.echo", autospec=True)
@mock.patch("ubitflashtool.cli.sys.exit", autospec=True)
def test_file_checker_existing_path(mock_exit, mock_echo, mock_exists):
    """Test file checker exits with error if the file exists."""
    mock_exists.return_value = True

    cli._file_checker("subject", "file/path.py")

    mock_exists.assert_called_once_with("file/path.py")
    assert mock_echo.call_count == 1
    assert (
        "Abort: The file/path.py file already exists."
        in mock_echo.call_args[0][0]
    )
    mock_exit.assert_called_once_with(1)


@mock.patch("ubitflashtool.cli.click.echo", autospec=True)
@mock.patch("ubitflashtool.cli.sys.exit", autospec=True)
def test_file_checker_no_path(mock_exit, mock_echo):
    """Test the file check informs about console output if no file is given."""
    cli._file_checker("subject", None)

    assert mock_echo.call_count == 1
    assert "subject will be output to console." in mock_echo.call_args[0]
    assert mock_exit.call_count == 0


@mock.patch("ubitflashtool.cli.read_python_code", autospec=True)
def test_read_code(mock_read_python_code, check_no_board_connected):
    """Test the read-code command without a file option."""
    python_code = "Python code here"
    mock_read_python_code.return_value = python_code
    runner = CliRunner()

    result = runner.invoke(cli.read_code)

    assert "MicroPython code will be output to console." in result.output
    assert "Printing the MicroPython code" in result.output
    assert python_code in result.output
    assert "Finished successfully" in result.output
    assert result.exit_code == 0


def test_read_code_no_board(check_no_board_connected):
    """Test the read-code command when no board is connected."""
    runner = CliRunner()

    result = runner.invoke(cli.read_code)

    assert result.exit_code != 0
    assert "MicroPython code will be output to console." in result.output
    assert "Did not find any connected boards." in result.output


@mock.patch("ubitflashtool.cli.read_python_code", autospec=True)
def test_read_code_path(mock_read_python_code, check_no_board_connected):
    """Test the read-code command with a file option."""
    mock_read_python_code.return_value = "Python code here"
    runner = CliRunner()

    with mock.patch("ubitflashtool.cli.open", mock.mock_open()) as m_open:
        result = runner.invoke(cli.read_code, ["--file_path", "thisfile.py"])

    m_open.assert_called_once_with("thisfile.py", "w")
    m_open().write.assert_called_once_with("Python code here")
    assert "MicroPython code will be written to: thisfile.py" in result.output
    assert "Saving the MicroPython code..." in result.output
    assert "Finished successfully" in result.output
    assert result.exit_code == 0


def test_read_code_path_no_board(check_no_board_connected):
    """Test read-code command with a file option and no board connected."""
    file_name = "thisfile.py"
    runner = CliRunner()

    results = [
        runner.invoke(cli.read_code, ["--file_path", file_name]),
        runner.invoke(cli.read_code, ["-f", file_name]),
    ]

    for result in results:
        assert result.exit_code != 0, "Exit code non-zero"
        assert (
            "MicroPython code will be written to: {}".format(file_name)
            in result.output
        ), "Message written to file"
        assert (
            "Did not find any connected boards." in result.output
        ), "Message error, board not found"
    # File not mocked, so checking command hasn't created it
    assert not os.path.isfile(file_name), "File does not exist"


@mock.patch("ubitflashtool.cli.read_flash_hex", autospec=True)
def test_read_flash(mock_read_flash_hex, check_no_board_connected):
    """Test the read-flash command without a file option."""
    flash_hex_content = "Intel Hex lines here"
    mock_read_flash_hex.return_value = flash_hex_content
    runner = CliRunner()

    result = runner.invoke(cli.read_flash)

    assert "micro:bit flash hex will be output to console." in result.output
    assert "Printing the flash contents" in result.output
    assert flash_hex_content in result.output
    assert "Finished successfully" in result.output
    assert result.exit_code == 0


def test_read_flash_no_board(check_no_board_connected):
    """Test the read-flash command when no board is connected."""
    runner = CliRunner()

    result = runner.invoke(cli.read_flash)

    assert result.exit_code != 0
    assert "micro:bit flash hex will be output to console." in result.output
    assert "Did not find any connected boards." in result.output


@mock.patch("ubitflashtool.cli.read_flash_hex", autospec=True)
def test_read_flash_path(mock_read_flash_hex, check_no_board_connected):
    """Test the read-code command with a file option."""
    flash_hex_content = "Intel Hex lines here"
    mock_read_flash_hex.return_value = flash_hex_content
    file_name = "thisfile.py"
    runner = CliRunner()

    with mock.patch("ubitflashtool.cli.open", mock.mock_open()) as m_open:
        results = [runner.invoke(cli.read_flash, ["--file_path", file_name])]
    with mock.patch("ubitflashtool.cli.open", mock.mock_open()) as m_open2:
        results.append(runner.invoke(cli.read_flash, ["-f", file_name]))

    m_open.assert_called_once_with(file_name, "w")
    m_open2.assert_called_once_with(file_name, "w")
    m_open().write.assert_called_once_with(flash_hex_content)
    m_open2().write.assert_called_once_with(flash_hex_content)
    for result in results:
        assert (
            "micro:bit flash hex will be written to: {}".format(file_name)
            in result.output
        )
        assert "Saving the flash contents..." in result.output
        assert "Finished successfully" in result.output
        assert result.exit_code == 0


def test_read_flash_path_no_board(check_no_board_connected):
    """Test read-flash command with a file option and no board connected."""
    file_name = "thisfile.py"
    runner = CliRunner()

    results = [
        runner.invoke(cli.read_flash, ["--file_path", file_name]),
        runner.invoke(cli.read_flash, ["-f", file_name]),
    ]

    for result in results:
        assert result.exit_code != 0, "Exit code non-zero"
        assert (
            "micro:bit flash hex will be written to: {}".format(file_name)
            in result.output
        ), "Message written to file"
        assert (
            "Did not find any connected boards." in result.output
        ), "Message error, board not found"
    # File not mocked, so checking command hasn't created it
    assert not os.path.isfile(file_name), "File does not exist"


@mock.patch("ubitflashtool.cli.os.path.isfile", autospec=True)
@mock.patch("ubitflashtool.cli.compare_full_flash_hex", autospec=True)
def test_compare_flash(mock_compare, mock_isfile, check_no_board_connected):
    """Test the compare-flash command."""
    file_name = "random_file_name.hex"
    mock_isfile.return_value = True
    runner = CliRunner()

    results = [
        runner.invoke(cli.compare_flash, ["-f", file_name]),
        runner.invoke(cli.compare_flash, ["--file_path", file_name]),
    ]

    assert mock_compare.call_count == len(results)
    for result in results:
        assert "Diff output loaded in default browser." in result.output
        assert "Finished successfully!" in result.output
        assert result.exit_code == 0, "Exit code 0"


@mock.patch("ubitflashtool.cli.os.path.isfile", autospec=True)
def test_compare_flash_no_board(mock_isfile, check_no_board_connected):
    """Test the compare-flash command when no board is connected."""
    file_name = "random_file_name.hex"
    file_content = "Intel Hex lines here"
    mock_isfile.return_value = True
    runner = CliRunner()

    with mock.patch(
        "ubitflashtool.cmds.open", mock.mock_open(read_data=file_content)
    ) as m_open:
        results = [
            runner.invoke(cli.compare_flash, ["-f", file_name]),
            runner.invoke(cli.compare_flash, ["--file_path", file_name]),
        ]

    assert m_open.call_count == len(results)
    for result in results:
        assert result.exit_code != 0, "Exit code non-zero"
        assert "Did not find any connected boards." in result.output


def test_compare_flash_invalid_file():
    """Check error is thrown when compare-flash file does not exist."""
    file_name = "random_file_does_not_exist.hex"
    runner = CliRunner()

    results = [
        runner.invoke(cli.compare_flash, ["--file_path", file_name]),
        runner.invoke(cli.compare_flash, ["-f", file_name]),
    ]

    for result in results:
        assert result.exit_code != 0, "Exit code non-zero"
        assert "Abort: File does not exists" in result.output


def test_compare_flash_no_file():
    """Test there is an error when compare-flash doesn't have a file arg."""
    runner = CliRunner()

    result = runner.invoke(cli.compare_flash)

    assert result.exit_code != 0, "Exit code non-zero"
    assert 'Error: Missing option "-f" / "--file_path".' in result.output


@mock.patch("ubitflashtool.gui.open_gui", autospec=True)
def test_gui(mock_open_gui, check_no_board_connected):
    """Test the gui command."""
    runner = CliRunner()

    result = runner.invoke(cli.gui)

    assert result.exit_code == 0, "Exit code 0"
    assert mock_open_gui.call_count == 1, "open_gui() function called"
