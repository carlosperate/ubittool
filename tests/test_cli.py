#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Tests for..."""
try:
    from unittest import mock
except ImportError:
    import mock

from click.testing import CliRunner
import pytest

from ubitflashtool import cli, cmds


@pytest.fixture
def check_no_board_connected():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    try:
        cmds._read_continuous_memory(address=0x00, count=16)
    except Exception:
        # Good: If no board is found exception is raised
        pass
    else:
        raise Exception('Found an Mbed device connected, please unplug.')


@mock.patch('ubitflashtool.cli.os.path.exists', autospec=True)
@mock.patch('ubitflashtool.cli.click.echo', autospec=True)
@mock.patch('ubitflashtool.cli.sys.exit', autospec=True)
def test_file_checker(mock_exit, mock_echo, mock_exists):
    """."""
    mock_exists.return_value = False

    cli._file_checker('subject', 'file/path.py')

    mock_exists.assert_called_once_with('file/path.py')
    assert mock_echo.call_count == 1
    # echo_calls = [call[0] for call in mock_echo.call_args_list]
    assert 'subject will be written to: file/path.py' in mock_echo.call_args[0]
    assert mock_exit.call_count == 0


@mock.patch('ubitflashtool.cli.os.path.exists', autospec=True)
@mock.patch('ubitflashtool.cli.click.echo', autospec=True)
@mock.patch('ubitflashtool.cli.sys.exit', autospec=True)
def test_file_checker_existing_path(mock_exit, mock_echo, mock_exists):
    """."""
    mock_exists.return_value = True

    cli._file_checker('subject', 'file/path.py')

    mock_exists.assert_called_once_with('file/path.py')
    assert mock_echo.call_count == 1
    assert 'Abort: The file/path.py file already exists.' in \
        mock_echo.call_args[0][0]
    mock_exit.assert_called_once_with(1)


@mock.patch('ubitflashtool.cli.click.echo', autospec=True)
@mock.patch('ubitflashtool.cli.sys.exit', autospec=True)
def test_file_checker_no_path(mock_exit, mock_echo):
    """."""
    cli._file_checker('subject', None)

    assert mock_echo.call_count == 1
    assert 'subject will be output to console.' in mock_echo.call_args[0]
    assert mock_exit.call_count == 0


@mock.patch('ubitflashtool.cli.read_python_code', autospec=True)
def test_read_code(mock_read_python_code, check_no_board_connected):
    """."""
    mock_read_python_code.return_value = 'Python code here'
    runner = CliRunner()

    result = runner.invoke(cli.read_code)

    assert 'MicroPython code will be output to console.' in result.output
    assert 'Printing the MicroPython code' in result.output
    assert 'Python code here' in result.output
    assert 'Finished successfully' in result.output
    assert result.exit_code == 0


def test_read_code_no_board(check_no_board_connected):
    """."""
    runner = CliRunner()

    result = runner.invoke(cli.read_code)

    assert result.exit_code == 1
    assert 'MicroPython code will be output to console.' in result.output
    assert 'Error: Did not find any connected boards.' in result.output


@mock.patch('ubitflashtool.cli.read_python_code', autospec=True)
def test_read_code_path(mock_read_python_code, check_no_board_connected):
    """."""
    mock_read_python_code.return_value = 'Python code here'
    runner = CliRunner()

    with mock.patch('ubitflashtool.cli.open', mock.mock_open()) as m_open:
        result = runner.invoke(cli.read_code, ['--file_path', 'thisfile.py'])

    m_open.assert_called_once_with('thisfile.py', 'w')
    m_open().write.assert_called_once_with('Python code here')
    assert 'MicroPython code will be written to: thisfile.py' in result.output
    assert 'Saving the MicroPython code...' in result.output
    assert 'Finished successfully' in result.output
    assert result.exit_code == 0


def test_read_code_path_no_board(check_no_board_connected):
    """."""
    runner = CliRunner()

    result = runner.invoke(cli.read_code, ['-f', 'thisfile.py'])

    assert result.exit_code == 1
    assert 'MicroPython code will be written to: thisfile.py' in result.output
    assert 'Error: Did not find any connected boards.' in result.output
