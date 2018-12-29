#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Run make-like commands from a Python script instead of a MakeFile.

No dependencies outside of what is on the Pipfile, so it works on all platforms
without installing other stuff (e.g. Make on Windows).
"""
import os
import sys
import subprocess

import click


def _run_cli_cmd(cmd_list):
    """Run a shell command and return the error code.

    :param cmd_list: A list of strings that make up the command to execute.
    """
    try:
        return subprocess.call(cmd_list)
    except Exception as e:
        print(str(e))
        sys.exit(1)


def _this_file_dir():
    """:return: Path to this file directory."""
    return os.path.dirname(os.path.realpath(__file__))


def _set_cwd():
    """Set cwd to the path necessary for these commands to work correctly.

    All commands depend on this file folder being the current working
    directory.
    """
    os.chdir(_this_file_dir())


@click.group(help=__doc__)
def make():
    """Click entry point."""
    pass


@make.command()
def linter():
    """Run Flake8 linter with all its plugins."""
    _set_cwd()
    print('Running linter...')
    return_code = _run_cli_cmd(['flake8', 'ubitflashtool/', 'tests/'])
    if return_code == 0:
        print('All good :)')
        return return_code
    else:
        sys.exit(return_code)


@make.command()
def test():
    """Run PyTests with the coverage plugin."""
    _set_cwd()
    return _run_cli_cmd([sys.executable, '-m', 'pytest', '-v',
                         '--cov=ubitflashtool', 'tests/'])


@make.command()
@click.pass_context
def check(ctx):
    """Run all the checkers and tests."""
    commands = [linter, test]
    for cmd in commands:
        ctx.invoke(cmd)


@make.command()
def build():
    """Build the CLI and GUI executables."""
    _set_cwd()
    print('------------------------')
    print('Building CLI executable:')
    print('------------------------')
    rtn_code = _run_cli_cmd(['pyinstaller', 'package/pyinstaller-cli.spec'])
    if rtn_code != 0:
        sys.exit(1)
    print('\n------------------------')
    print('Building GUI executable:')
    print('------------------------')
    return _run_cli_cmd(['pyinstaller', 'package/pyinstaller-gui.spec'])


def main():
    """Script entry point, launches click."""
    make(prog_name='python make.py')


if __name__ == '__main__':
    main()
