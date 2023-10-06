#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI and GUI utility to read content from the micro:bit."""
import os
import sys

import click

from ubittool import __version__
from ubittool.cmds import (
    read_flash_hex,
    read_flash_uicr_hex,
    read_python_code,
    flash_drag_n_drop,
    compare_full_flash_hex,
)

# GUI depends on tkinter, which could be packaged separately from Python or
# excluded from CLI-only packing, but the other CLI commands should still work
try:
    from ubittool.gui import open_gui

    GUI_AVAILABLE = True
except ImportError:  # pragma: no cover
    GUI_AVAILABLE = False


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


@cli.command(
    short_help="Read the micro:bit flash and UICR into a hex file or console."
)
@click.option(
    "-f",
    "--file_path",
    "file_path",
    type=click.Path(),
    help="Path to the output file to write micro:bit flash content.",
)
def read_flash_uicr(file_path=None):
    """Read the micro:bit flash and UICR into a hex file or console."""
    click.echo("Executing: {}\n".format(read_flash_uicr.__doc__))
    _file_checker("micro:bit flash and UICR hex", file_path)

    click.echo("Reading the micro:bit flash and UICR contents...")
    try:
        flash_data = read_flash_uicr_hex()
    except Exception as e:
        click.echo(click.style("Error: {}", fg="red").format(e), err=True)
        sys.exit(1)

    if file_path:
        click.echo("Saving the flash and UICR contents...")
        with open(file_path, "w") as hex_file:
            hex_file.write(flash_data)
    else:
        click.echo("Printing the flash and UICR contents")
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
    help="Path to the hex file to compare against the micro:bit.",
)
def compare(file_path):
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


@cli.command(
    short_help="Copy a hex file into the MICROBIT drive, read back the "
    "flash contents, and compare them with a hex file."
)
@click.option(
    "-i",
    "--input_file_path",
    "input_file_path",
    type=click.Path(),
    required=True,
    help="Path to the hex file to flash into the micro:bit.",
)
@click.option(
    "-c",
    "--compare_file_path",
    "compare_file_path",
    type=click.Path(),
    required=True,
    help="Path to the hex file to compare against the micro:bit flash.",
)
def flash_compare(compare_file_path, input_file_path):
    """Flash the micro:bit and compare its flash contents with a hex file.

    Opens the default browser to display an HTML page with the comparison
    output.
    """
    click.echo("Executing: Compare the micro:bit flash with a hex file.\n")
    abort = "Abort: File '{}' does not exists"
    if not input_file_path or not os.path.isfile(input_file_path):
        click.echo(
            click.style(abort.format(input_file_path), fg="red"), err=True
        )
        sys.exit(1)
    if not compare_file_path or not os.path.isfile(compare_file_path):
        click.echo(
            click.style(abort.format(compare_file_path), fg="red"), err=True
        )
        sys.exit(1)

    try:
        click.echo(
            "Copying '{}' file to MICROBIT drive...".format(input_file_path)
        )
        flash_drag_n_drop(input_file_path)
        click.echo("Reading the micro:bit flash contents...")
        compare_full_flash_hex(compare_file_path)
    except Exception as e:
        click.echo(click.style("Error: {}", fg="red").format(e), err=True)
        sys.exit(1)
    click.echo("Diff output loaded in the default browser.")

    click.echo("\nFinished successfully!")


if GUI_AVAILABLE:

    @cli.command()
    def gui():
        """Launch the GUI version of this app (has more options)."""
        open_gui()


def main():
    """Command line interface entry point."""
    cli(prog_name="ubit")


if __name__ == "__main__":
    main()
