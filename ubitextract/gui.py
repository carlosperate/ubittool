#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# A text viewer that can read and save a Python script from the micro:bit
# flash or a hex file.
#
from __future__ import absolute_import, print_function
from sys import version_info
from idlelib.WidgetRedirector import WidgetRedirector
from cmd import read_python_code
if version_info.major == 3:
    # Tkinter imports
    from tkinter import (Tk, Text, Scrollbar, Menu, messagebox, filedialog,
                         Frame)
elif version_info.major == 2:
    # Tkinter imports
    from Tkinter import (Tk, Text, Scrollbar, Menu, Frame)
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


class UBitExtractFrame():
    """
    Attaches a Frame to a TK window with a text editor.
    """

    def __init__(self, root):
        self.root = root
        self.root.title('uBitExtract')

        frame = Frame(root)
        self.y_scrollbar = Scrollbar(frame, orient='vertical')
        self.editor = ReadOnlyEditor(frame, yscrollcommand=self.y_scrollbar.set)
        self.editor.pack(side='left', fill='both', expand=1)
        self.editor.config(wrap='char', width=1)
        self.editor.focus()
        self.y_scrollbar.pack(side='right', fill='y')
        self.y_scrollbar.config(command=self.editor.yview)
        frame.pack(fill='both', expand=1)

        # instead of closing the window, execute a function
        self.root.protocol('WM_DELETE_WINDOW', self.file_quit)

        self.add_menu_bad()
        self.bind_shorcuts()

    def add_menu_bad(self):
        # create a top level menu
        self.menubar = Menu(self.root)
        # Menu item File
        file_menu = Menu(self.menubar, tearoff=0)
        file_menu.add_command(label='Open', underline=1,
                              command=self.file_open, accelerator='Ctrl+O')
        file_menu.add_command(label='Save As', underline=5,
                              command=self.file_save_as, accelerator='Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', underline=2,
                              command=self.file_quit, accelerator='Alt+F4')
        self.menubar.add_cascade(label='File', underline=0, menu=file_menu)
        # Menu item micro:bit
        ubit_menu = Menu(self.menubar, tearoff=0)
        ubit_menu.add_command(label='Read micro:bit', underline=1,
                              command=self.open_microbit_code, accelerator='Ctrl+N')
        ubit_menu.add_command(label='Open Hex file', underline=1,
                              command=self.unimplemented, accelerator='Ctrl+H')
        self.menubar.add_cascade(
                label='micro:bit', underline=0, menu=ubit_menu)
        # display the menu
        self.root.config(menu=self.menubar)

    def bind_shorcuts(self, event=None):
        self.editor.bind('<Control-o>', self.file_open)
        self.editor.bind('<Control-O>', self.file_open)
        self.editor.bind('<Control-S>', self.file_save_as)
        self.editor.bind('<Control-s>', self.file_save_as)

    def unimplemented(self):
        messagebox.showinfo('Not Implemented',
                            'This feature has not yet been implemented.')
        # messagebox.askyesnocancel('Title', 'Question?')
        # yes = True, no = False, cancel = None

    def open_microbit_code(self):
        python_code = read_python_code()
        self.editor.delete(1.0, 'end')
        self.editor.insert(1.0, python_code)

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
        self.root.destroy()


def open_editor():
    root = Tk()
    root.geometry('{}x{}'.format(600, 480))
    editor = UBitExtractFrame(root)
    root.mainloop()


if __name__ == '__main__':
    open_editor()
