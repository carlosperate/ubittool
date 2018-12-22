#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""A text viewer that can can perform the ubitflashtool actions."""
from __future__ import absolute_import, print_function
import sys
import logging
from idlelib.WidgetRedirector import WidgetRedirector

from ubitflashtool import __version__
from ubitflashtool.cmd import (read_python_code, read_micropython,
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


class StdoutRedirector(object):
    """A class to redirect stdout to a text widget."""

    def __init__(self, text_area, text_color=None):
        """Get the text area widget as a reference and configure its colour."""
        self.text_area = text_area
        self.text_color = text_color
        self.tag = 'colour_change_%s' % text_color
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


class UBitFlashToolWindow(Tk):
    """Main app window.

    Attaches a Frame to a TK window with a text editor and menus for options.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the window."""
        Tk.__init__(self, *args, **kwargs)
        self.title('uBitFlashTool v{}'.format(__version__))
        self.geometry('{}x{}'.format(600, 480))

        self.frame_editor = Frame(self)
        self.frame_console = Frame(self)
        self.menu_bar = Menu(self)
        self.editor = None
        self.console = None

        self.set_menu_bar(self.menu_bar)
        self.set_editor(self.frame_editor)
        self.set_console(self.frame_console)
        self.activate_console()

        # instead of closing the window, execute a function
        self.protocol('WM_DELETE_WINDOW', self.file_quit)

        self.bind_shortcuts()

    def set_menu_bar(self, menu):
        """Create the menu bar with all user options.

        :param menu: A Menu() instance to attach all options.
        """
        # Menu item File
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label='Open', underline=1,
                              command=self.file_open, accelerator='Ctrl+O')
        file_menu.add_command(label='Save As', underline=5,
                              command=self.file_save_as, accelerator='Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', underline=2,
                              command=self.file_quit, accelerator='Alt+F4')
        menu.add_cascade(label='File', underline=0, menu=file_menu)
        # Menu item micro:bit
        ubit_menu = Menu(menu, tearoff=0)
        ubit_menu.add_command(label='Read MicroPython code', underline=1,
                              command=self.read_python_code)
        ubit_menu.add_command(label='Read MicroPython runtime', underline=1,
                              command=self.read_micropython)
        menu.add_cascade(label='micro:bit', underline=0, menu=ubit_menu)
        # Menu item nrf
        nrf_menu = Menu(menu, tearoff=0)
        nrf_menu.add_command(label='Read full flash contents (Intel Hex)',
                             underline=1, command=self.read_full_flash_intel)
        nrf_menu.add_command(label='Read full flash contents (Pretty Hex)',
                             underline=1, command=self.read_full_flash_pretty)
        nrf_menu.add_command(label='Read UICR Customer', underline=1,
                             command=self.read_uicr_customer)
        nrf_menu.add_separator()
        nrf_menu.add_command(label='Compare full flash contents (Intel Hex)',
                             underline=1,
                             command=self.compare_full_flash_intel)
        nrf_menu.add_command(label='Compare UICR Customer (Intel Hex)',
                             underline=1,
                             command=self.compare_uicr_customer_intel)
        menu.add_cascade(label='nrf', underline=0, menu=nrf_menu)
        # display the menu
        self.config(menu=menu)

    def set_editor(self, frame):
        """Set a read-only the text editor to a frame to display text.

        :param frame: A Frame() instance to set a text editor.
        """
        scrollbar = Scrollbar(frame, orient='vertical')
        self.editor = ReadOnlyEditor(frame, yscrollcommand=scrollbar.set)
        self.editor.pack(side='left', fill='both', expand=1)
        self.editor.config(wrap='char', width=1)
        self.editor.focus()
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=self.editor.yview)
        frame.pack(fill='both', expand=1)

    def set_console(self, frame):
        """Set a read-only editor to a frame to display std out and in streams.

        :param frame: A Frame() instance to set a text editor.
        """
        scrollbar = Scrollbar(frame, orient='vertical')
        self.console = ReadOnlyEditor(frame, yscrollcommand=scrollbar.set,
                                      background="#222", foreground="#DDD")
        self.console.pack(side='left', fill='both', expand=1)
        self.console.config(wrap='char', width=1)
        self.console.focus()
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=self.console.yview)
        frame.pack(fill='both', expand=1)

    def activate_console(self):
        """Configure std out/in to send to write to the console text widget."""
        sys.stdout = StdoutRedirector(self.console, text_color='#0D4')
        sys.stderr = StdoutRedirector(self.console, text_color='#D00')
        logger = logging.getLogger()
        logger.setLevel(level=logging.INFO)
        logging_handler_out = logging.StreamHandler(sys.stdout)
        logging_handler_out.setLevel(logging.INFO)
        logger.addHandler(logging_handler_out)
        logging_handler_err = logging.StreamHandler(sys.stderr)
        logging_handler_err.setLevel(logging.WARNING)
        logger.addHandler(logging_handler_err)

    def deactivate_console(self):
        """Restore std out/in."""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def bind_shortcuts(self, event=None):
        """Bind shortcuts to operations."""
        self.editor.bind('<Control-o>', self.file_open)
        self.editor.bind('<Control-O>', self.file_open)
        self.editor.bind('<Control-S>', self.file_save_as)
        self.editor.bind('<Control-s>', self.file_save_as)

    def unimplemented(self):
        """Display an window to show the user a feature is not implemented."""
        messagebox.showinfo('Not Implemented',
                            'This feature has not yet been implemented.')

    def read_python_code(self):
        """Read the Python user code from the micro:bit flash.

        Displays it as text code in the read-only text editor.
        """
        python_code = read_python_code()
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, python_code)

    def read_micropython(self):
        """Read the Python user code from the micro:bit flash.

        Displays it as Intel Hex in the read-only text editor.
        """
        hex_str = read_micropython()
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, hex_str)

    def read_full_flash_intel(self):
        """Read the full contents of flash.

        Displays it as Intel Hex in the read-only text editor.
        """
        hex_str = read_full_flash_hex(decode_hex=False)
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, hex_str)

    def read_full_flash_pretty(self):
        """Read the full contents of flash.

        Displays it as a pretty hex and ASCII string in the read-only text
        editor.
        """
        hex_str = read_full_flash_hex(decode_hex=True)
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, hex_str)

    def read_uicr_customer(self):
        """Read the full contents of flash.

        Displays it as Intel Hex in the read-only text editor.
        """
        uicr_hex_str = read_uicr_customer(decode_hex=True)
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, uicr_hex_str)

    def compare_full_flash_intel(self):
        """Compare a hex file with the micro:bit flash.

        Ask the user to select a hex file, compares it with flash contents and
        opens the default web browser to display the comparison results.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            self.editor.delete(1.0, 'end')
            self.editor.insert(1.0, 'Reading flash contents...')
            compare_full_flash_hex(file_path)
            self.editor.delete(1.0, 'end')
            self.editor.insert(1.0, 'Diff content loaded in default browser.')

    def compare_uicr_customer_intel(self):
        """Compare a hex file with the micro:bit user UICR memory.

        Ask the user to select a hex file, compares it with the user UICR
        contents and opens the default web browser to display the comparison
        results.
        """
        file_path = filedialog.askopenfilename()
        if file_path:
            self.editor.delete(1.0, 'end')
            self.editor.insert(1.0, 'Reading User UICR contents...')
            compare_uicr_customer(file_path)
            self.editor.delete(1.0, 'end')
            self.editor.insert(1.0, 'Diff content loaded in default browser.')

    def file_open(self, event=None, file_path=None):
        """Open a file picker and loads a file into the editor."""
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, encoding='utf-8') as f:
                file_contents = f.read()
            # Set current text to file contents
            self.editor.delete(1.0, 'end')
            self.editor.insert(1.0, file_contents)

    def file_save_as(self, event=None,):
        """Save the text in the text editor into a file."""
        file_path = filedialog.asksaveasfilename(filetypes=(
                ('Python files', '*.py *.pyw'), ('All files', '*.*')))
        if file_path:
            with open(file_path, 'wb') as f:
                text = self.editor.get(1.0, 'end-1c')
                f.write(text.encode('utf-8'))
                return file_path
        else:
            return None

    def file_quit(self, event=None):
        """Confirm with the user to quite the app."""
        if messagebox.askyesnocancel('Exit', 'Exit?'):
            self.deactivate_console()
            self.destroy()


def open_editor():
    """Create the app window and launch it."""
    app = UBitFlashToolWindow()
    app.lift()
    app.attributes('-topmost', True)
    app.after_idle(app.attributes, '-topmost', False)
    app.mainloop()


if __name__ == '__main__':
    open_editor()
