#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Tests for..."""
import os
try:
    from unittest import mock
except ImportError:
    import mock

from ubitflashtool import cmds


@mock.patch('ubitflashtool.cmds.Timer')
@mock.patch('ubitflashtool.cmds.webbrowser.open')
def test_open_temp_html(mock_browser_open, mock_timer):
    """."""
    html_content = 'hello world'

    cmds._open_temp_html(html_content)

    # Get the URL sent to the browser and check the content
    url = mock_browser_open.call_args_list[0][0][0]
    if not url.startswith('file://'):
        assert False
    file_path = url[7:]
    with open(file_path, 'r') as tmp_file:
        read_content = tmp_file.read()
    assert read_content == html_content

    # Timer was mocked, so remove file manually
    os.remove(file_path)
