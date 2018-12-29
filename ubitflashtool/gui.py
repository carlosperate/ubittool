#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""A GUI that display the content from performing the uBitFlashTool actions."""
from __future__ import absolute_import, print_function
import sys
import logging
import platform
from idlelib.WidgetRedirector import WidgetRedirector

from ubitflashtool import __version__
from ubitflashtool.cmds import (read_python_code, read_micropython,
                                read_full_flash_hex, read_uicr_customer,
                                compare_full_flash_hex, compare_uicr_customer)

if sys.version_info.major == 3:
    # Tkinter imports
    from tkinter import (Tk, Text, Scrollbar, Menu, messagebox, filedialog,
                         Frame)
elif sys.version_info.major == 2:
    # Tkinter imports
    from Tkinter import Tk, Text, Scrollbar, Menu, Frame
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    # open() with encodings
    from io import open


class ReadOnlyEditor(Text):
    """Implement a read only mode text editor class.

    Done by replacing the bindings for the insert and delete events. From:
    http://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
    """

    def __init__(self, *args, **kwargs):
        """Init the class and set the insert and delete event bindings."""
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register(
                'insert', lambda *args, **kw: 'break')
        self.delete = self.redirector.register(
                'delete', lambda *args, **kw: 'break')

    def clear(self):
        """Remove all the content in the editor."""
        self.delete(1.0, 'end')

    def replace(self, new_content):
        """Remove all editor content and inserts the new content.

        :param new_content: String to insert.
        """
        self.delete(1.0, 'end')
        self.insert(1.0, new_content)


class StdoutRedirector(object):
    """A class to redirect stdout to a text widget."""

    def __init__(self, text_area, text_color=None):
        """Get the text area widget as a reference and configure its colour."""
        self.text_area = text_area
        self.text_color = text_color
        self.tag = 'colour_change_{}'.format(text_color)
        if self.text_color:
            self.text_area.tag_configure(self.tag, foreground=text_color)

    def write(self, string):
        """Write text to the fake stream."""
        start_position = self.text_area.index('insert')
        self.text_area.insert('end', string)
        if self.text_color:
            self.text_area.tag_add(
                    self.tag, start_position, self.text_area.index('insert'))

    def flush(self):
        """All flushed immediately on each write call."""
        pass


class TextViewer(ReadOnlyEditor):
    """A read-only text editor for viewing text."""

    def __init__(self, parent, *args, **kwargs):
        """Construct the editor into a parent frame.

        :param frame: A Frame() instance to set the text editor.
        """
        self.scrollbar = Scrollbar(parent, orient='vertical')
        ReadOnlyEditor.__init__(
            self, parent, yscrollcommand=self.scrollbar.set, *args, **kwargs)
        self.pack(side='left', fill='both', expand=1)
        self.config(wrap='char', width=1)
        self.scrollbar.pack(side='right', fill='y')
        self.scrollbar.config(command=self.yview)
        parent.pack(fill='both', expand=1)


class ConsoleOutput(ReadOnlyEditor):
    """A read-only editor to display std out and err streams."""

    def __init__(self, parent, *args, **kwargs):
        """Construct the read-only editor into a parent frame.

        :param frame: A Frame() instance to set this text editor.
        """
        self.scrollbar = Scrollbar(parent, orient='vertical')
        ReadOnlyEditor.__init__(
                self, parent, yscrollcommand=self.scrollbar.set,
                background="#222", foreground="#DDD", *args, **kwargs)
        self.pack(side='left', fill='both', expand=1)
        self.config(wrap='char', width=1)
        self.scrollbar.pack(side='right', fill='y')
        self.scrollbar.config(command=self.yview)
        parent.pack(fill='both', expand=1)
        self.activate()

    def activate(self):
        """Configure std out/in to send to write to the console text widget."""
        sys.stdout = StdoutRedirector(self, text_color='#0D4')
        sys.stderr = StdoutRedirector(self, text_color='#D00')
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


class UBitFlashToolWindow(Tk):
    """Main app window.

    Creates a TK window with a text viewer, console viewer, and menus for
    executing actions.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the window."""
        Tk.__init__(self, *args, **kwargs)
        self.title('uBitFlashTool v{}'.format(__version__))
        self.geometry('{}x{}'.format(600, 480))

        self.menu_bar = Menu(self)
        self.set_menu_bar(self.menu_bar)
        self.bind_shortcuts()

        self.frame_viewer = Frame(self)
        self.text_viewer = TextViewer(self.frame_viewer)
        self.text_viewer.focus()

        self.frame_console = Frame(self)
        self.console = ConsoleOutput(self.frame_console)

        # instead of closing the window, execute a function
        self.protocol('WM_DELETE_WINDOW', self.app_quit)

    def set_menu_bar(self, menu):
        """Create the menu bar with all user options.

        :param menu: A Menu() instance to attach all options.
        """
        # In macOS we use the command key instead of option
        cmd_key = 'Command' if platform.system() == 'Darwin' else 'Ctrl'
        # Menu item File
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label='Open', underline=0,
                              command=self.file_open,
                              accelerator='{}+O'.format(cmd_key))
        file_menu.add_command(label='Save As', underline=0,
                              command=self.file_save_as,
                              accelerator='{}+S'.format(cmd_key))
        file_menu.add_separator()
        file_menu.add_command(label='Exit',
                              command=self.app_quit, accelerator='Alt+F4')
        menu.add_cascade(label='File', underline=0, menu=file_menu)
        # Menu item micro:bit
        ubit_menu = Menu(menu, tearoff=0)
        ubit_menu.add_command(label='Read MicroPython code',
                              command=self.read_python_code)
        ubit_menu.add_command(label='Read MicroPython runtime',
                              command=self.read_micropython)
        menu.add_cascade(label='micro:bit', underline=0, menu=ubit_menu)
        # Menu item nrf
        nrf_menu = Menu(menu, tearoff=0)
        nrf_menu.add_command(label='Read full flash contents (Intel Hex)',
                             command=self.read_full_flash_intel)
        nrf_menu.add_command(label='Read full flash contents (Pretty Hex)',
                             command=self.read_full_flash_pretty)
        nrf_menu.add_command(label='Read UICR Customer',
                             command=self.read_uicr_customer)
        nrf_menu.add_separator()
        nrf_menu.add_command(label='Compare full flash contents (Intel Hex)',
                             command=self.compare_full_flash_intel)
        nrf_menu.add_command(label='Compare UICR Customer (Intel Hex)',
                             command=self.compare_uicr_customer_intel)
        menu.add_cascade(label='nrf', underline=0, menu=nrf_menu)
        # display the menu
        self.config(menu=menu)

    def bind_shortcuts(self, event=None):
        """Bind shortcuts to operations."""
        # In macOS we use the command key instead of option
        cmd_key = 'Command' if platform.system() == 'Darwin' else 'Control'
        self.bind('<{}-o>'.format(cmd_key), self.file_open)
        self.bind('<{}-O>'.format(cmd_key), self.file_open)
        self.bind('<{}-S>'.format(cmd_key), self.file_save_as)
        self.bind('<{}-s>'.format(cmd_key), self.file_save_as)

    def unimplemented(self):
        """Display an window to show the user a feature is not implemented."""
        messagebox.showinfo('Not Implemented',
                            'This feature has not yet been implemented.')

    def read_python_code(self):
        """Read the Python user code from the micro:bit flash.

        Displays it as text code in the read-only text viewer.
        """
        python_code = read_python_code()
        self.text_viewer.replace(python_code)

    def read_micropython(self):
        """Read the Python user code from the micro:bit flash.

        Displays it as Intel Hex in the read-only text viewer.
        """
        hex_str = read_micropython()
        self.text_viewer.replace(hex_str)

    def read_full_flash_intel(self):
        """Read the full contents of flash.

        Displays it as Intel Hex in the read-only text viewer.
        """
        hex_str = read_full_flash_hex(decode_hex=False)
        self.text_viewer.replace(hex_str)

    def read_full_flash_pretty(self):
        """Read the full contents of flash.

        Displays it as a pretty hex and ASCII string in the read-only text
        viewer.
        """
        hex_str = read_full_flash_hex(decode_hex=True)
        self.text_viewer.replace(hex_str)

    def read_uicr_customer(self):
        """Read the full contents of flash.

        Displays it as Intel Hex in the read-only text viewer.
        """
        uicr_hex_str = read_uicr_customer(decode_hex=True)
        self.text_viewer.replace(uicr_hex_str)

    def compare_full_flash_intel(self):
        """Compare a hex file with the micro:bit flash.

        Ask the user to select a hex file, compares it with flash contents and
        opens the default web browser to display the comparison results.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            self.text_viewer.replace('Reading flash contents...')
            compare_full_flash_hex(file_path)
            self.text_viewer.replace('Diff content loaded in default browser.')

    def compare_uicr_customer_intel(self):
        """Compare a hex file with the micro:bit user UICR memory.

        Ask the user to select a hex file, compares it with the user UICR
        contents and opens the default web browser to display the comparison
        results.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            self.text_viewer.replace('Reading User UICR contents...')
            compare_uicr_customer(file_path)
            self.text_viewer.replace('Diff content loaded in default browser.')

    def file_open(self, event=None):
        """Open a file picker and load a file into the text viewer."""
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, encoding='utf-8') as f:
                file_contents = f.read()
            # Set current text to file contents
            self.text_viewer.replace(file_contents)

    def file_save_as(self, event=None):
        """Save the text from the text viewer into a file."""
        file_path = filedialog.asksaveasfilename(filetypes=(
                ('Python files', '*.py *.pyw'), ('All files', '*.*')))
        if file_path:
            with open(file_path, 'wb') as f:
                text = self.text_viewer.get(1.0, 'end-1c')
                f.write(text.encode('utf-8'))
                return file_path
        else:
            return None

    def app_quit(self, event=None):
        """Quit the app."""
        self.console.deactivate()
        self.destroy()


def open_gui():
    """Create the app window and launch it."""
    app = UBitFlashToolWindow()
    app.lift()
    app.attributes('-topmost', True)
    app.after_idle(app.attributes, '-topmost', False)
    app.mainloop()


if __name__ == '__main__':
    open_gui()
