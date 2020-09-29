#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI and GUI utility to read content from the micro:bit."""
import os
import sys

import click

from ubittool import __version__
from ubittool.cmds import (
    read_flash_hex,
    read_python_code,
    compare_full_flash_hex,
)


@click.group(help="uBitTool v{}.\n\n{}".format(__version__, __doc__))
def cli():
    """Click entry point."""
    pass


def _file_checker(subject, file_path):
    """Check if a file exists and informs user about content output.

    :param subject: Very short file description, subject for printed sentences.
    :param file_path: Path to the file to check.
    """
    if file_path:
        if os.path.exists(file_path):
            click.echo(
                click.style(
                    "Abort: The {} file already exists.", fg="red"
                ).format(file_path),
                err=True,
            )
            sys.exit(1)
        else:
            click.echo("{} will be written to: {}".format(subject, file_path))
    else:
        click.echo("{} will be output to console.".format(subject))


@cli.command()
@click.option(
    "-f",
    "--file_path",
    "file_path",
    type=click.Path(),
    help="Path to the output file to write the MicroPython code.",
)
def read_code(file_path=None):
    """Extract the MicroPython code to a file or print it."""
    click.echo("Executing: {}\n".format(read_code.__doc__))
    _file_checker("MicroPython code", file_path)

    click.echo("Reading the micro:bit flash contents...")
    try:
        python_code = read_python_code()
    except Exception as e:
        click.echo(click.style("Error: {}", fg="red").format(e), err=True)
        sys.exit(1)

    if file_path:
        click.echo("Saving the MicroPython code...")
        with open(file_path, "w") as python_file:
            python_file.write(python_code)
    else:
        click.echo("Printing the MicroPython code")
        click.echo("----------------------------------------")
        click.echo(python_code)
        click.echo("----------------------------------------")

    click.echo("\nFinished successfully!")


@cli.command(
    short_help="Read the micro:bit flash contents into a hex file or console."
)
@click.option(
    "-f",
    "--file_path",
    "file_path",
    type=click.Path(),
    help="Path to the output file to write micro:bit flash content.",
)
def read_flash(file_path=None):
    """Read the micro:bit flash contents into a hex file or console."""
    click.echo("Executing: {}\n".format(read_flash.__doc__))
    _file_checker("micro:bit flash hex", file_path)

    click.echo("Reading the micro:bit flash contents...")
    try:
        flash_data = read_flash_hex()
    except Exception as e:
        click.echo(click.style("Error: {}", fg="red").format(e), err=True)
        sys.exit(1)

    if file_path:
        click.echo("Saving the flash contents...")
        with open(file_path, "w") as hex_file:
            hex_file.write(flash_data)
    else:
        click.echo("Printing the flash contents")
        click.echo("----------------------------------------")
        click.echo(flash_data)
        click.echo("----------------------------------------")

    click.echo("\nFinished successfully!")


@cli.command()
@click.option(
    "-f",
    "--file_path",
    "file_path",
    type=click.Path(),
    required=True,
    help="Path to to the hex file to compare against the micro:bit.",
)
def compare_flash(file_path):
    """Compare the micro:bit flash contents with a hex file.

    Opens the default browser to display an HTML page with the comparison
    output.
    """
    click.echo("Executing: Compare the micro:bit flash with a hex file.\n")
    if not file_path or not os.path.isfile(file_path):
        click.echo(
            click.style("Abort: File does not exists", fg="red"), err=True
        )
        sys.exit(1)

    click.echo("Reading the micro:bit flash contents...")
    try:
        exit_code = compare_full_flash_hex(file_path)
    except Exception as e:
        click.echo(click.style("Error: {}", fg="red").format(e), err=True)
        sys.exit(1)
    click.echo("Diff output loaded in the default browser.")

    if exit_code:
        click.echo("\nThere are some differences in the micro:bit flash!")
        sys.exit(exit_code)
    else:
        click.echo("\nNo diffs between micro:bit flash and hex file :)")
        click.echo("Finished successfully.")


@cli.command()
def gui():
    """Launch the GUI version of this app (has more options)."""
    # GUI depends on tkinter, which could be packaged separately from Python
    # for users that only want the CLI we can still use all the other commands
    from ubittool.gui import open_gui

    open_gui()


def main():
    """Command line interface entry point."""
    cli(prog_name="ubit")


if __name__ == "__main__":
    main()
