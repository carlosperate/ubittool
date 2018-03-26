#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
A text viewer that can can perform the ubitflashtool actions.
"""
from __future__ import absolute_import, print_function
import sys
import logging
from idlelib.WidgetRedirector import WidgetRedirector
from ubitflashtool.cmd import (read_python_code, read_micropython,
                               read_full_flash_hex, read_uicr_customer)
if sys.version_info.major == 3:
    # Tkinter imports
    from tkinter import (Tk, Text, Scrollbar, Menu, messagebox, filedialog,
                         Frame)
elif sys.version_info.major == 2:
    # Tkinter imports
    from Tkinter import Tk, Text, Scrollbar, Menu, Frame
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    # Open with encodings
    from io import open


class ReadOnlyEditor(Text):
    """
    Implement a read only mode by replacing the bindings for the
    insert and delete events. From:
    http://stackoverflow.com/questions/3842155/is-there-a-way-to-make-the-tkinter-text-widget-read-only
    """

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register(
                'insert', lambda *args, **kw: 'break')
        self.delete = self.redirector.register(
                'delete', lambda *args, **kw: 'break')


class StdoutRedirector(object):
    """
    A class to redirect stdout to a text widget.
    """
    def __init__(self, text_area, text_color=None):
        self.text_area = text_area
        self.text_color = text_color
        self.tag = 'colour_change_%s' % text_color
        if self.text_color:
            self.text_area.tag_configure(self.tag, foreground=text_color)

    def write(self, string):
        start_position = self.text_area.index('insert')
        self.text_area.insert('end', string)
        if self.text_color:
            self.text_area.tag_add(
                    self.tag, start_position, self.text_area.index('insert'))

    def flush(self):
        pass


class UBitFlashToolWindow(Tk):
    """
    Attaches a Frame to a TK window with a text editor.
    """

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('uBitFlashTool')
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
        menu.add_cascade(label='nrf', underline=0, menu=nrf_menu)
        # display the menu
        self.config(menu=menu)

    def set_editor(self, frame):
        scrollbar = Scrollbar(frame, orient='vertical')
        self.editor = ReadOnlyEditor(frame, yscrollcommand=scrollbar.set)
        self.editor.pack(side='left', fill='both', expand=1)
        self.editor.config(wrap='char', width=1)
        self.editor.focus()
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=self.editor.yview)
        frame.pack(fill='both', expand=1)

    def set_console(self, frame):
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
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def bind_shortcuts(self, event=None):
        self.editor.bind('<Control-o>', self.file_open)
        self.editor.bind('<Control-O>', self.file_open)
        self.editor.bind('<Control-S>', self.file_save_as)
        self.editor.bind('<Control-s>', self.file_save_as)

    def unimplemented(self):
        messagebox.showinfo('Not Implemented',
                            'This feature has not yet been implemented.')

    def read_python_code(self):
        python_code = read_python_code()
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, python_code)

    def read_micropython(self):
        hex_str = read_micropython()
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, hex_str)

    def read_full_flash_intel(self):
        hex_str = read_full_flash_hex(decode_hex=False)
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, hex_str)

    def read_full_flash_pretty(self):
        hex_str = read_full_flash_hex(decode_hex=True)
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, hex_str)

    def read_uicr_customer(self):
        uicr_hex_str = read_uicr_customer()
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, uicr_hex_str)

    def file_open(self, event=None, file_path=None):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, encoding='utf-8') as f:
                file_contents = f.read()
            # Set current text to file contents
            self.editor.delete(1.0, 'end')
            self.editor.insert(1.0, file_contents)

    def file_save_as(self, event=None,):
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
        if messagebox.askyesnocancel('Exit', 'Exit?'):
            self.deactivate_console()
            self.destroy()


def open_editor():
    app = UBitFlashToolWindow()
    app.mainloop()


if __name__ == '__main__':
    open_editor()
