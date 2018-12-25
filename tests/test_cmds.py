#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Tests for cmds.py module."""
import os
try:
    from unittest import mock
except ImportError:
    import mock

from ubitflashtool import cmds


@mock.patch('ubitflashtool.cmds.Timer')
@mock.patch('ubitflashtool.cmds.webbrowser.open')
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


@mock.patch('ubitflashtool.cmds.HtmlDiff')
def test_gen_diff_html(mock_diff):
    """Check the HTML returned contains the provided inputs."""
    from_title = 'from_title_content'
    from_lines = 'left content here'
    to_title = 'to_title_content'
    to_lines = 'different content on the right here'
    mock_diff.return_value.make_table.return_value = '<t>{} {}</t>'.format(
        from_lines, to_lines)

    html = cmds._gen_diff_html(from_title, [from_lines], to_title, [to_lines])

    assert html.count(from_title) == 2
    assert html.count(from_lines) == 1
    assert html.count(to_title) == 2
    assert html.count(to_lines) == 1


@mock.patch('ubitflashtool.cmds.read_full_flash_hex')
@mock.patch('ubitflashtool.cmds._gen_diff_html')
@mock.patch('ubitflashtool.cmds._open_temp_html')
def test_compare_full_flash_hex(
        mock_open_temp_html, mock_gen_diff_html, mock_read_full_flash_hex):
    """Check that file contents."""
    file_hex_path = os.path.join('path', 'to', 'file.hex')
    file_hex_content = 'This is the hex file content'
    flash_hex_content = 'This is the flash hex content'
    mock_read_full_flash_hex.return_value = flash_hex_content

    with mock.patch('ubitflashtool.cmds.open', mock.mock_open(
            read_data=file_hex_content)) as m_open:
        cmds.compare_full_flash_hex(file_hex_path)

    m_open.assert_called_once_with(file_hex_path, encoding='utf-8')
    assert mock_read_full_flash_hex.call_count == 1
    assert mock_read_full_flash_hex.call_args[1] == {'decode_hex': False}
    assert mock_gen_diff_html.call_count == 1
    assert mock_gen_diff_html.call_args[0] == (
            'micro:bit', [flash_hex_content], 'Hex file', [file_hex_content])
    assert mock_open_temp_html.call_count == 1


@mock.patch('ubitflashtool.cmds.read_uicr_customer')
@mock.patch('ubitflashtool.cmds._gen_diff_html')
@mock.patch('ubitflashtool.cmds._open_temp_html')
def test_compare_uicr_customer(
        mock_open_temp_html, mock_gen_diff_html, mock_read_uicr_customer):
    """Check that file contents."""
    file_hex_path = os.path.join('path', 'to', 'file.hex')
    file_hex_content = 'This is the hex file content'
    flash_hex_content = 'This is the flash hex content'
    mock_read_uicr_customer.return_value = flash_hex_content

    with mock.patch('ubitflashtool.cmds.open', mock.mock_open(
            read_data=file_hex_content)) as m_open:
        cmds.compare_uicr_customer(file_hex_path)

    m_open.assert_called_once_with(file_hex_path, encoding='utf-8')
    assert mock_read_uicr_customer.call_count == 1
    assert mock_read_uicr_customer.call_args[1] == {'decode_hex': False}
    assert mock_gen_diff_html.call_count == 1
    assert mock_gen_diff_html.call_args[0] == (
            'micro:bit', [flash_hex_content], 'Hex file', [file_hex_content])
    assert mock_open_temp_html.call_count == 1
