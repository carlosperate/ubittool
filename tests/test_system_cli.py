#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run simple system tests on the CLI program.

The actual unit tests for the cli module are in the test_cli.py file.
Here we only do a simple command line invocation to ensure we can access the
app via terminal, and we trust that the library click implements all the
commands as it is a fully tested package.
"""
import subprocess
import sys

import pytest

from ubitflashtool import cli, cmds, __version__


def _run_cli_cmd(cmd_list):
    """Run a shell command and return the output.

    :param cmd_list: A list of strings that make up the command to execute.
    """
    try:
        return subprocess.check_output(cmd_list, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.output


def _ubitflashtool_cmd(cmd_list):
    """Invoke the ubitflashtool app using different methods and return outputs.

    :param cmd_list: List of cli argument to add to ubitflashtool invocation.
    """
    module = [sys.executable, "-m", "ubitflashtool"]
    module.extend(cmd_list)
    cmd = ["ubitflashtool"]
    cmd.extend(cmd_list)
    script = [sys.executable, "ubitflashtool/cli.py"]
    script.extend(cmd_list)
    return [_run_cli_cmd(module), _run_cli_cmd(cmd), _run_cli_cmd(script)]


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


def test_help():
    """Check the help option works."""
    outputs = _ubitflashtool_cmd(["--help"])
    for output in outputs:
        assert b"Usage: ubitflashtool [OPTIONS] COMMAND [ARGS]..." in output
        assert str.encode("uBitFlashTool v{}".format(__version__)) in output
        assert str.encode(cli.__doc__) in output


def test_read_code(check_no_board_connected):
    """Check the read-code command returns an error when no board connected."""
    outputs = _ubitflashtool_cmd(["read-code"])
    for output in outputs:
        assert b"Executing: Extract the MicroPython code" in output
        assert b"Did not find any connected boards." in output
