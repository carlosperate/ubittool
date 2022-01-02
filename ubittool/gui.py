#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A GUI to display the content from performing the uBitTool actions."""
import sys
import logging
import platform
import tkinter as tk
from tkinter import filedialog as tkFileDialog
from tkinter.scrolledtext import ScrolledText as tkScrolledText

try:
    from idlelib.WidgetRedirector import WidgetRedirector
except ImportError:
    from idlelib.redirector import WidgetRedirector

from ubittool import __version__
from ubittool import cmds


class ReadOnlyEditor(tkScrolledText):
    """Implement a read only mode text editor class with scroll bar.

    Done by replacing the bindings for the insert and delete events. From:
    http://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
    """

    def __init__(self, *args, **kwargs):
        """Init the class and set the insert and delete event bindings."""
        super().__init__(*args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register(
            "insert", lambda *args, **kw: "break"
        )
        self.delete = self.redirector.register(
            "delete", lambda *args, **kw: "break"
        )

    def clear(self):
        """Clear the contents of the text area."""
        self.delete(1.0, "end")

    def replace(self, new_content):
        """Remove all editor content and inserts the new content.

        :param new_content: String to insert.
        """
        self.clear()
        self.insert(1.0, new_content)


class StdoutRedirector(object):
    """A class to redirect stdout to a text widget."""

    def __init__(self, text_area, text_color=None):
        """Get the text area widget as a reference and configure its colour."""
        self.text_area = text_area
        self.text_color = text_color
        self.tag = "colour_change_{}".format(text_color)
        if self.text_color:
            self.text_area.tag_configure(self.tag, foreground=text_color)

    def write(self, string):
        """Write text to the fake stream."""
        start_position = self.text_area.index("insert")
        self.text_area.insert("end", string)
        if self.text_color:
            self.text_area.tag_add(
                self.tag, start_position, self.text_area.index("insert")
            )

    def flush(self):  # pragma: no cover
        """All flushed immediately on each write call."""
        pass


class TextViewer(ReadOnlyEditor):
    """A read-only text editor for viewing text."""

    def __init__(self, *args, **kwargs):
        """Construct the editor widget.

        :param frame: A Frame() instance to set the text editor.
        """
        super().__init__(*args, **kwargs)
        self.pack(side="left", fill="both", expand=1)
        self.config(wrap="char", width=1)


class ConsoleOutput(ReadOnlyEditor):
    """A read-only editor to display std out and err streams."""

    def __init__(self, *args, **kwargs):
        """Construct the read-only editor widget.

        :param frame: A Frame() instance to set this text editor.
        """
        super().__init__(background="#222", foreground="#DDD", *args, **kwargs)
        self.config(wrap="char", width=1)
        self.activate()

    def activate(self):
        """Configure std out/in to send to write to the console text widget."""
        sys.stdout = StdoutRedirector(self, text_color="#0D4")
        sys.stderr = StdoutRedirector(self, text_color="#D00")
        logger = logging.getLogger()
        logger.setLevel(level=logging.INFO)
        logging_handler_out = logging.StreamHandler(sys.stdout)
        logging_handler_out.setLevel(logging.INFO)
        logger.addHandler(logging_handler_out)
        logging_handler_err = logging.StreamHandler(sys.stderr)
        logging_handler_err.setLevel(logging.WARNING)
        logger.addHandler(logging_handler_err)

    def deactivate(self):
        """Restore std out/in."""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


class CmdLabel(tk.Label):
    """A text label to contain the name of the last command executed."""

    def __init__(self, parent, default_text, *args, **kwargs):
        """Set the colours in the constructor.

        :param frame: A Frame() instance to set this text editor.
        """
        self.bg_colour = "#E5E5E5"
        self.cmd_title = tk.StringVar(value="Command: Select from the Menu")
        parent.config(borderwidth=1, background=self.bg_colour)
        super().__init__(
            parent, background=self.bg_colour, textvariable=self.cmd_title
        )
        self.set_text(default_text)
        self.pack(side="left", fill="x")
        parent.pack(fill="x", expand=False)

    def set_text(self, new_text):
        """Set the text of the command."""
        self.cmd_title.set("Command: {}".format(new_text))


class UBitToolWindow(tk.Tk):
    """Main app window.

    Creates a TK window with a text viewer, console viewer, and menus for
    executing actions.
    """

    CMD_OPEN = "Open"
    CMD_SAVE = "Save As"
    CMD_EXIT = "Exit"
    CMD_READ_CODE = "Read MicroPython code"
    CMD_READ_UPY = "Read MicroPython runtime"
    CMD_READ_FLASH_HEX = "Read full flash contents (Intel Hex)"
    CMD_READ_FLASH_PRETTY = "Read full flash contents (Pretty Hex)"
    CMD_READ_RAM_HEX = "Read full RAM contents (Intel Hex)"
    CMD_READ_RAM_PRETTY = "Read full RAM contents (Pretty Hex)"
    CMD_READ_UICR = "Read UICR"
    CMD_READ_UICR_CUSTOMER = "Read UICR Customer"
    CMD_COMPARE_FLASH = "Compare full flash contents (Intel Hex)"
    CMD_COMPARE_UICR = "Compare UICR Customer (Intel Hex)"

    def __init__(self, *args, **kwargs):
        """Initialise the window."""
        super().__init__(*args, **kwargs)
        self.title("uBitTool v{}".format(__version__))
        self.geometry("{}x{}".format(600, 480))

        self.menu_bar = tk.Menu(self)
        self.set_menu_bar(self.menu_bar)
        self.bind_shortcuts()

        self.frame_title = tk.Frame(self)
        self.cmd_title = CmdLabel(self.frame_title, "Select from the Menu")

        self.paned_window = tk.PanedWindow(
            orient=tk.VERTICAL,
            sashrelief="groove",
            sashpad=0,
            sashwidth=5,
            showhandle=True,
            handlesize=10,
        )
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.text_viewer = TextViewer()
        self.paned_window.add(self.text_viewer)

        self.console = ConsoleOutput()
        self.paned_window.add(self.console)

        # instead of closing the window, execute a function
        self.protocol("WM_DELETE_WINDOW", self.app_quit)

    def set_menu_bar(self, menu):
        """Create the menu bar with all user options.

        :param menu: A Menu() instance to attach all options.
        """
        # In macOS we use the command key instead of option
        cmd_key = "Command" if platform.system() == "Darwin" else "Ctrl"
        # Menu item File
        self.file_menu = tk.Menu(menu, tearoff=0)
        self.file_menu.add_command(
            label=self.CMD_OPEN,
            command=self.file_open,
            accelerator="{}+O".format(cmd_key),
            underline=1,
        )
        self.file_menu.add_command(
            label=self.CMD_SAVE,
            command=self.file_save_as,
            accelerator="{}+S".format(cmd_key),
            underline=1,
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label=self.CMD_EXIT, command=self.app_quit, accelerator="Alt+F4"
        )
        menu.add_cascade(label="File", underline=0, menu=self.file_menu)
        # Menu item micro:bit
        self.ubit_menu = tk.Menu(menu, tearoff=0)
        self.ubit_menu.add_command(
            label=self.CMD_READ_CODE, command=self.read_python_code
        )
        self.ubit_menu.add_command(
            label=self.CMD_READ_UPY, command=self.read_micropython
        )
        menu.add_cascade(label="micro:bit", underline=0, menu=self.ubit_menu)
        # Menu item nrf
        self.nrf_menu = tk.Menu(menu, tearoff=0)
        self.nrf_menu.add_command(
            label=self.CMD_READ_FLASH_HEX, command=self.read_full_flash_intel
        )
        self.nrf_menu.add_command(
            label=self.CMD_READ_FLASH_PRETTY,
            command=self.read_full_flash_pretty,
        )
        self.nrf_menu.add_command(
            label=self.CMD_READ_RAM_HEX, command=self.read_ram_intel,
        )
        self.nrf_menu.add_command(
            label=self.CMD_READ_RAM_PRETTY, command=self.read_ram_pretty,
        )
        self.nrf_menu.add_command(
            label=self.CMD_READ_UICR, command=self.read_uicr
        )
        self.nrf_menu.add_command(
            label=self.CMD_READ_UICR_CUSTOMER, command=self.read_uicr_customer
        )
        self.nrf_menu.add_separator()
        self.nrf_menu.add_command(
            label=self.CMD_COMPARE_FLASH, command=self.compare_full_flash_intel
        )
        self.nrf_menu.add_command(
            label=self.CMD_COMPARE_UICR,
            command=self.compare_uicr_customer_intel,
        )
        menu.add_cascade(label="nrf", underline=0, menu=self.nrf_menu)
        # display the menu
        self.config(menu=menu)

    def bind_shortcuts(self, event=None):
        """Bind shortcuts to operations."""
        # In macOS we use the command key instead of option
        cmd_key = "Command" if platform.system() == "Darwin" else "Control"
        self.bind("<{}-o>".format(cmd_key), self.file_open)
        self.bind("<{}-O>".format(cmd_key), self.file_open)
        self.bind("<{}-S>".format(cmd_key), self.file_save_as)
        self.bind("<{}-s>".format(cmd_key), self.file_save_as)

    def set_next_cmd(self, cmd_name):
        """Prepare the window for the next command to be executed."""
        self.text_viewer.clear()
        self.console.clear()
        self.cmd_title.set_text(cmd_name)

    def read_python_code(self):
        """Read the Python user code from the micro:bit flash.

        Displays it as text code in the read-only text viewer.
        """
        self.set_next_cmd(self.CMD_READ_CODE)
        python_code = cmds.read_python_code()
        self.text_viewer.replace(python_code)

    def read_micropython(self):
        """Read the MicroPython interpreter from the micro:bit flash.

        Displays it as Intel Hex in the read-only text viewer.
        """
        self.set_next_cmd(self.CMD_READ_UPY)
        hex_str = cmds.read_micropython()
        self.text_viewer.replace(hex_str)

    def read_full_flash_intel(self):
        """Read the full contents of flash.

        Displays it as Intel Hex in the read-only text viewer.
        """
        self.set_next_cmd(self.CMD_READ_FLASH_HEX)
        hex_str = cmds.read_flash_hex(decode_hex=False)
        self.text_viewer.replace(hex_str)

    def read_full_flash_pretty(self):
        """Read the full contents of flash.

        Displays it as a pretty hex and ASCII string in the read-only text
        viewer.
        """
        self.set_next_cmd(self.CMD_READ_FLASH_PRETTY)
        hex_str = cmds.read_flash_hex(decode_hex=True)
        self.text_viewer.replace(hex_str)

    def read_ram_intel(self):
        """Read the full contents of RAM.

        Displays it as Intel Hex in the read-only text viewer.
        """
        self.set_next_cmd(self.CMD_READ_RAM_HEX)
        ram_hex_str = cmds.read_ram_hex(decode_hex=False)
        self.text_viewer.replace(ram_hex_str)

    def read_ram_pretty(self):
        """Read the full contents of RAM.

        Displays it as a pretty hex and ASCII string in the read-only text
        viewer.
        """
        self.set_next_cmd(self.CMD_READ_RAM_PRETTY)
        ram_hex_str = cmds.read_ram_hex(decode_hex=True)
        self.text_viewer.replace(ram_hex_str)

    def read_uicr(self):
        """Read the full contents of UICR.

        Displays it as Intel Hex in the read-only text viewer.
        """
        self.set_next_cmd(self.CMD_READ_UICR)
        uicr_hex_str = cmds.read_uicr_hex(decode_hex=True)
        self.text_viewer.replace(uicr_hex_str)

    def read_uicr_customer(self):
        """Read the Customer section of the UICR.

        Displays it as Intel Hex in the read-only text viewer.
        """
        self.set_next_cmd(self.CMD_READ_UICR_CUSTOMER)
        uicr_hex_str = cmds.read_uicr_customer_hex(decode_hex=True)
        self.text_viewer.replace(uicr_hex_str)

    def compare_full_flash_intel(self):
        """Compare a hex file with the micro:bit flash.

        Ask the user to select a hex file, compares it with flash contents and
        opens the default web browser to display the comparison results.
        """
        self.set_next_cmd(self.CMD_COMPARE_FLASH)
        file_path = tkFileDialog.askopenfilename()
        if file_path:
            self.text_viewer.replace("Reading flash contents...")
            cmds.compare_full_flash_hex(file_path)
            self.text_viewer.replace("Diff content loaded in default browser.")

    def compare_uicr_customer_intel(self):
        """Compare a hex file with the micro:bit user UICR memory.

        Ask the user to select a hex file, compares it with the user UICR
        contents and opens the default web browser to display the comparison
        results.
        """
        self.set_next_cmd(self.CMD_COMPARE_UICR)
        file_path = tkFileDialog.askopenfilename()
        if file_path:
            self.text_viewer.replace("Reading User UICR contents...")
            cmds.compare_uicr_customer(file_path)
            self.text_viewer.replace("Diff content loaded in default browser.")

    def file_open(self, event=None):
        """Open a file picker and load a file into the text viewer."""
        file_path = tkFileDialog.askopenfilename()
        if file_path:
            self.set_next_cmd(self.CMD_OPEN)
            with open(file_path, encoding="utf-8") as f:
                file_contents = f.read()
            # Set current text to file contents
            self.text_viewer.replace(file_contents)

    def file_save_as(self, event=None):
        """Save the text from the text viewer into a file."""
        file_path = tkFileDialog.asksaveasfilename(
            filetypes=(("Python files", "*.py *.pyw"), ("All files", "*.*"))
        )
        if file_path:
            with open(file_path, "wb") as f:
                text = self.text_viewer.get(1.0, "end-1c")
                f.write(text.encode("utf-8"))
                return file_path
        else:
            return None

    def app_quit(self, event=None):
        """Quit the app."""
        self.console.deactivate()
        self.destroy()


def open_gui():
    """Create the app window and launch it."""
    app = UBitToolWindow()
    app.lift()
    app.attributes("-topmost", True)
    app.after_idle(app.attributes, "-topmost", False)
    app.mainloop()


if __name__ == "__main__":
    open_gui()
