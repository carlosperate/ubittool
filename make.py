#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Run make-like commands from a Python script instead of a MakeFile.

No dependencies outside of what is on the Pipfile, so it works on all platforms
without installing other stuff (e.g. Make on Windows).
"""
from __future__ import print_function
import os
import sys
import shutil
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


def _rm_dir(dir_to_remove):
    """:param dir_to_remove: Directory to remove."""
    if os.path.isdir(dir_to_remove):
        print('Removing directory: {}'.format(dir_to_remove))
        shutil.rmtree(dir_to_remove)
    else:
        print('Directory {} was not found.'.format(dir_to_remove))


def _rm_folder_named(scan_path, folder_name):
    """Remove all folders named folder_name from the given directory tree.

    :param scan_path: Directory to scan for folders with specific name.
    """
    for root, dirs, files in os.walk(scan_path, topdown=False):
        for name in dirs:
            if name == folder_name:
                _rm_dir(os.path.join(root, name))


def _rm_file(file_to_remove):
    """:param file_to_remove: File to remove."""
    if os.path.isfile(file_to_remove):
        print('Removing file: {}'.format(file_to_remove))
        os.remove(file_to_remove)
    else:
        print('File {} was not found.'.format(file_to_remove))


def _rm_file_extension(scan_path, file_extension):
    """Remove all files with an specific extension from a given directory.

    :param scan_path: Directory to scan for file removal.
    :param file_extension: File extension of the files to remove
    """
    for root, dirs, files in os.walk(scan_path, topdown=False):
        for file_ in files:
            if file_.endswith('.{}'.format(file_extension)):
                file_path = os.path.join(root, file_)
                _rm_file(file_path)


@click.group(help=__doc__)
def make():
    """Click entry point."""
    pass


@make.command()
def linter():
    """Run Flake8 linter with all its plugins."""
    _set_cwd()
    print('---------------')
    print('Running linter:')
    print('---------------')
    return_code = _run_cli_cmd(['flake8', 'ubitflashtool/', 'tests/'])
    if return_code != 0:
        sys.exit(return_code)
    print('All good :)')
    return return_code


@make.command()
def style():
    """Run Flake8 linter with all its plugins."""
    _set_cwd()
    print('----------------------')
    print('Running Style Checker:')
    print('----------------------')
    try:
        import black
    except ImportError:
        print('Black Python module not found, style check skipped.')
        return 0
    black_cmd = [
        'black',
        '.',
        '--target-version', 'py35',
        '--line-length', '79',
        '--check',
        '--diff',
    ]
    return_code = _run_cli_cmd(black_cmd)
    if return_code != 0:
        sys.exit(return_code)
    return return_code


@make.command()
def test():
    """Run PyTests with the coverage plugin."""
    _set_cwd()
    return_code = _run_cli_cmd([
        sys.executable, '-m', 'pytest', '-v', '--cov=ubitflashtool', 'tests/'
    ])
    if return_code != 0:
        sys.exit(return_code)
    return 0


@make.command()
@click.pass_context
def check(ctx):
    """Run all the checkers and tests."""
    commands = [linter, test, style]
    for cmd in commands:
        ctx.invoke(cmd)
    return 0


@make.command()
@click.pass_context
def build(ctx):
    """Build the CLI and GUI executables."""
    ctx.invoke(clean)
    _set_cwd()
    print('------------------------')
    print('Building CLI executable:')
    print('------------------------')
    rtn_code = _run_cli_cmd(['pyinstaller', 'package/pyinstaller-cli.spec'])
    if rtn_code != 0:
        sys.exit(rtn_code)
    print('------------------------')
    print('Building GUI executable:')
    print('------------------------')
    rtn_code = _run_cli_cmd(['pyinstaller', 'package/pyinstaller-gui.spec'])
    if rtn_code != 0:
        sys.exit(rtn_code)
    return 0


@make.command()
def clean():
    """Remove unnecessary files (like build outputs)."""
    _set_cwd()
    print('---------')
    print('Cleaning:')
    print('---------')
    folders_to_remove = [
        '.pytest_cache',
        'build',
        'dist',
        'ubitflashtool.egg-info'
    ]
    files_to_remove = [
        '.coverage',
    ]
    for folder in folders_to_remove:
        _rm_dir(folder)
    for f in files_to_remove:
        _rm_file(f)

    _rm_folder_named('.', '__pycache__')
    _rm_file_extension('.', 'pyc')
    return 0


def main():
    """Script entry point, launches click."""
    make(prog_name='python make.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
