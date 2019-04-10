#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for cmds.py module."""
import os
from unittest import mock

from ubitflashtool import cmds

INTEL_HEX_EOF = ':00000001FF\n'


def test_bytes_to_intel_hex():
    """Test the data to Intel Hex string conversion."""
    data = [1, 2, 3, 4, 5]
    expected_hex_str = '\n'.join([':050000000102030405EC', INTEL_HEX_EOF])

    result = cmds._bytes_to_intel_hex(data=data)

    assert expected_hex_str == result


def test_bytes_to_intel_hex_offset():
    """Test the data to Intel Hex string conversion with an offset."""
    data = [1, 2, 3, 4, 5]
    offset = 0x2000000
    expected_hex_str = '\n'.join(
        [':020000040200F8', ':050000000102030405EC', INTEL_HEX_EOF]
    )

    result = cmds._bytes_to_intel_hex(data=data, offset=offset)

    assert expected_hex_str == result


@mock.patch('ubitflashtool.cmds.sys.stderr.write', autospec=True)
@mock.patch('ubitflashtool.cmds.StringIO', autospec=True)
def test_bytes_to_intel_hex_io_error(mock_string_io, mock_stderr):
    """Test the exception handling when an IOError is encountered."""
    data = [1, 2, 3, 4, 5]
    mock_string_io.return_value.write.side_effect = IOError()

    result = cmds._bytes_to_intel_hex(data=data)

    assert result is None
    assert mock_stderr.call_count == 1


def test_bytes_to_intel_hex_invalid_data():
    """Test there is an error thrown if the input data is invalid."""
    data = [1, 2, 3, 4, '500']

    try:
        cmds._bytes_to_intel_hex(data=data)
    except Exception:
        # The exception that bubbles up from IntelHex is implementation detail
        # from that library, so it could be anything
        assert True, 'Exception raised'
    else:
        assert False, 'Exception NOT raised'


def test_bytes_to_pretty_hex():
    """Test the data to Intel Hex string conversion."""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    expected = (
        '0000  01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10  '
        '|................|\n'
    )

    result = cmds._bytes_to_pretty_hex(data=data)

    assert expected == result


def test_bytes_to_pretty_hex_offset():
    """Test the data to Intel Hex string conversion with an offset."""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    offset = 0x2000001
    expected = (
        '2000000  -- 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  '
        '| ...............|\n'
        '2000010  10 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --  '
        '|.               |\n'
    )

    result = cmds._bytes_to_pretty_hex(data=data, offset=offset)

    assert expected == result


@mock.patch('ubitflashtool.cmds.sys.stderr.write', autospec=True)
@mock.patch('ubitflashtool.cmds.StringIO', autospec=True)
def test_bytes_to_pretty_hex_io_error(mock_string_io, mock_stderr):
    """Test the exception handling when an IOError is encountered."""
    data = [1, 2, 3, 4, 5]
    mock_string_io.return_value.write.side_effect = IOError()

    result = cmds._bytes_to_pretty_hex(data=data)

    assert result is None
    assert mock_stderr.call_count == 1


def test_bytes_to_pretty_hexinvalid_data():
    """Test there is an error thrown if the input data is invalid."""
    try:
        cmds._bytes_to_pretty_hex(data=[1, 2, 3, 4, '500'])
    except Exception:
        # The exception that bubbles up from IntelHex is implementation detail
        # from that library, so it could be anything
        assert True, 'Exception raised'
    else:
        assert False, 'Exception NOT raised'


@mock.patch('ubitflashtool.cmds.programmer.read_flash', autospec=True)
@mock.patch('ubitflashtool.cmds._bytes_to_intel_hex', autospec=True)
def test_read_python_code(mock_bytes_to_intel_hex, mock_read_flash):
    """."""
    python_code_hex = '\n'.join(
        [
            ':020000040003F7',
            ':10E000004D509600232041646420796F7572205032',
            ':10E010007974686F6E20636F646520686572652E21',
            ':10E0200020452E672E0A66726F6D206D6963726FD0',
            ':10E0300062697420696D706F7274202A0A7768694A',
            ':10E040006C6520547275653A0A202020206469733B',
            ':10E05000706C61792E7363726F6C6C282748656CE5',
            ':10E060006C6F2C20576F726C642127290A202020A6',
            ':10E0700020646973706C61792E73686F7728496DBD',
            ':10E080006167652E4845415254290A20202020739B',
            ':10E090006C656570283230303029000000000000C7',
            ':10E0A000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF80',
        ]
    )
    python_code = '\n'.join(
        [
            '# Add your Python code here. E.g.',
            'from microbit import *',
            'while True:',
            '    display.scroll(\'Hello, World!\')',
            '    display.show(Image.HEART)',
            '    sleep(2000)',
        ]
    )
    mock_bytes_to_intel_hex.return_value = python_code_hex

    result = cmds.read_python_code()

    assert result == python_code


@mock.patch('ubitflashtool.cmds.programmer.read_flash', autospec=True)
@mock.patch('ubitflashtool.cmds._bytes_to_intel_hex', autospec=True)
def test_read_python_code_empty(mock_bytes_to_intel_hex, mock_read_flash):
    """Check error thrown if failing to find Python code in flash."""
    python_code_hex = '\n'.join(
        [
            ':020000040003F7',
            ':10E00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF20',
            ':10E01000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF10',
            ':10E02000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00',
            ':10E03000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0',
        ]
    )
    mock_bytes_to_intel_hex.return_value = python_code_hex

    try:
        cmds.read_python_code()
    except Exception:
        assert True, 'Could not decode Python user code'
    else:
        assert False, 'Decoded Python user code without throwing exception'


@mock.patch('ubitflashtool.cmds.Timer', autospec=True)
@mock.patch('ubitflashtool.cmds.webbrowser.open', autospec=True)
def test_open_temp_html(mock_browser_open, mock_timer):
    """Check browser is requested with a file containing the given text."""
    html_content = 'hello world'

    cmds._open_temp_html(html_content)

    # Get the URL sent to the browser and check the content
    assert mock_browser_open.call_count == 1
    url = mock_browser_open.call_args[0][0]
    assert url.startswith('file://')
    file_path = url[7:]
    with open(file_path, 'r') as tmp_file:
        read_content = tmp_file.read()
    assert read_content == html_content

    # Timer was mocked, so remove file manually
    os.remove(file_path)


@mock.patch('ubitflashtool.cmds.HtmlDiff', autospec=True)
def test_gen_diff_html(mock_diff):
    """Check the HTML returned contains the provided inputs."""
    from_title = 'from_title_content'
    from_lines = 'left content here'
    to_title = 'to_title_content'
    to_lines = 'different content on the right here'
    mock_diff.return_value.make_table.return_value = '<t>{} {}</t>'.format(
        from_lines, to_lines
    )

    html = cmds._gen_diff_html(from_title, [from_lines], to_title, [to_lines])

    assert html.count(from_title) == 2
    assert html.count(from_lines) == 1
    assert html.count(to_title) == 2
    assert html.count(to_lines) == 1


@mock.patch('ubitflashtool.cmds.read_flash_hex', autospec=True)
@mock.patch('ubitflashtool.cmds._gen_diff_html', autospec=True)
@mock.patch('ubitflashtool.cmds._open_temp_html', autospec=True)
def test_compare_full_flash_hex(
    mock_open_temp_html, mock_gen_diff_html, mock_read_flash_hex
):
    """Check that file contents."""
    file_hex_path = os.path.join('path', 'to', 'file.hex')
    file_hex_content = 'This is the hex file content'
    flash_hex_content = 'This is the flash hex content'
    mock_read_flash_hex.return_value = flash_hex_content

    with mock.patch(
        'ubitflashtool.cmds.open', mock.mock_open(read_data=file_hex_content)
    ) as m_open:
        cmds.compare_full_flash_hex(file_hex_path)

    m_open.assert_called_once_with(file_hex_path, encoding='utf-8')
    assert mock_read_flash_hex.call_count == 1
    assert mock_read_flash_hex.call_args[1] == {'decode_hex': False}
    assert mock_gen_diff_html.call_count == 1
    assert mock_gen_diff_html.call_args[0] == (
        'micro:bit',
        [flash_hex_content],
        'Hex file',
        [file_hex_content],
    )
    assert mock_open_temp_html.call_count == 1


@mock.patch('ubitflashtool.cmds.read_uicr_customer_hex', autospec=True)
@mock.patch('ubitflashtool.cmds._gen_diff_html', autospec=True)
@mock.patch('ubitflashtool.cmds._open_temp_html', autospec=True)
def test_compare_uicr_customer(
    mock_open_temp_html, mock_gen_diff_html, mock_read_uicr_customer
):
    """Check that file contents."""
    file_hex_path = os.path.join('path', 'to', 'file.hex')
    file_hex_content = 'This is the hex file content'
    flash_hex_content = 'This is the flash hex content'
    mock_read_uicr_customer.return_value = flash_hex_content

    with mock.patch(
        'ubitflashtool.cmds.open', mock.mock_open(read_data=file_hex_content)
    ) as m_open:
        cmds.compare_uicr_customer(file_hex_path)

    m_open.assert_called_once_with(file_hex_path, encoding='utf-8')
    assert mock_read_uicr_customer.call_count == 1
    assert mock_read_uicr_customer.call_args[1] == {'decode_hex': False}
    assert mock_gen_diff_html.call_count == 1
    assert mock_gen_diff_html.call_args[0] == (
        'micro:bit',
        [flash_hex_content],
        'Hex file',
        [file_hex_content],
    )
    assert mock_open_temp_html.call_count == 1
