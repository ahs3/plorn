#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import datetime
import filetype
import logging
import os
import re
import shutil
import sys
import time
from PIL import Image as pilImage
from PIL import ImageTk

from tkinter import font
import ttkbootstrap as ttk
from ttkbootstrap import StringVar, IntVar
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.tableview import Tableview, TableRow, TableColumn
from ttkbootstrap.dialogs.message import Messagebox

from plorn.config import get_config

module_logger = logging.getLogger('plorn.widgets')
module_logger.setLevel(logging.INFO)

def make_button(parent, text='Button', command=None, width=10, **kwargs):
    return ttk.Button(parent, text=text, command=command, width=width,
                      bootstyle="outline-primary", **kwargs)

def make_header_label(parent, width=20, text='', size=None):
    lbl = ttk.Label(parent, width=width, text=text)
    if not size:
        size = get_config().get_fontsize()+4
    lbl.configure(font=(font.nametofont('TkDefaultFont'),
                        size, 'bold', 'italic'))
    return lbl

class PlornFileDialog(ttk.Toplevel):
    '''
    It seems kind of silly to have to build my own file selection
    dialog but here we are ....
    '''
    def __init__(self, parent=None, allow_many=True,
                 title='Plorn File Dialog', show_hidden=False):
        super().__init__(parent)
        self.choices = []
        self.parent = parent
        self.allow_many = allow_many
        self.total_selected = 0
        self.show_hidden = show_hidden

        self.geometry('900x600')
        self.title(title)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=20)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=3)

        row = 0
        self.dirframe = ttk.Frame(self, padding='10 10 10 10')
        self.dirframe.grid(column=0, row=row, sticky=(E,W))
        self.dirframe.columnconfigure(0, weight=1)
        self.dirframe.columnconfigure(1, weight=4)
        self.dirframe.rowconfigure(0, weight=1)
        lab1 = ttk.Label(self.dirframe, text='Path:')
        lab1.grid(column=0, row=0)
        self.path = StringVar(self.dirframe)
        self.path.set(self.default_dir())
        self.path_box = ttk.Entry(self.dirframe, width=40,
                                  textvariable=self.path)
        self.path_box.grid(column=1, row=0)
        row += 1

        sep0 = ttk.Separator(self, orient=HORIZONTAL)
        sep0.grid(column=0, row=row, sticky=(E,W))
        row += 1
        sep1 = ttk.Separator(self, orient=HORIZONTAL)
        sep1.grid(column=0, row=row, sticky=(E,W))
        row += 1

        self.nameframe = ttk.Frame(self, padding='10 10 10 10')
        self.nameframe.grid(column=0, row=row, sticky=(N,S,E,W))
        self.nameframe.columnconfigure(0, weight=1)
        self.nameframe.rowconfigure(0, weight=1)
        self.coldata = []
        self.rowdata = []
        self.tview = self.build_table(self.nameframe)
        self.tview.grid(column=0, row=0, sticky=(N,S,E,W))
        self.fill_table()
        row += 1

        sep2 = ttk.Separator(self, orient=HORIZONTAL)
        sep2.grid(column=0, row=row, sticky=(E,W))
        row += 1
        sep3 = ttk.Separator(self, orient=HORIZONTAL)
        sep3.grid(column=0, row=row, sticky=(E,W))
        row += 1

        self.bframe = ttk.Frame(self, padding='10 10 10 10')
        self.bframe.grid(column=0, row=row, sticky=(E,W))
        self.buttons = [
            make_button(self.bframe, text='cancel', command=self.destroy),
            make_button(self.bframe, text=self.get_hidden_label(),
                        command=self.toggle_hidden, width=16),
            make_button(self.bframe, text='done', command=self.set_choices),
        ]
        self.hidden_button = self.buttons[1]
        row += 1

        self.bframe.rowconfigure(0, weight=1)
        for n in range(0, len(self.buttons)):
            self.bframe.columnconfigure(n, weight=1)
            self.buttons[n].grid(column=n, row=0, padx=10)

    def default_dir(self):
        result = ''
        home = os.path.expanduser('~/')
        path = os.path.join(home, 'Pictures')
        if os.path.exists(path) and os.path.isdir(path):
            result = path
        else:
            result = home
        return result

    def toggle_hidden(self):
        if self.show_hidden:
            self.show_hidden = False
        else:
            self.show_hidden = True
        self.hidden_button.configure(text=self.get_hidden_label())

    def get_hidden_label(self):
        result = 'show hidden'
        if self.show_hidden:
            result = 'hide hidden'
        return result

    def file_selected(self, rows):
        global module_logger

        n = 0
        for ii in rows:
            module_logger.info(f'DBG> file_selected: [{n}] {ii.values}')

    def build_table(self, parent):
        global module_logger

        self.coldata = [
            {'text': 'Name', 'stretch': True, 'minwidth': 375},
            {'text': 'Size', 'stretch': True,},
            {'text': 'Type', 'stretch': True,},
            {'text': 'Last Change', 'stretch': True, 'minwidth': 200},
        ]
        tview = Tableview(master=parent,
                          coldata=self.coldata,
                          rowdata=self.rowdata,
                          paginated=True,
                          searchable=True,
                          bootstyle=PRIMARY,
                          autofit=True,
                          pagesize=10,
                          on_select=self.file_selected,
                          disable_right_click=True,
                         )
        tview.align_heading_left(cid=0)
        tview.align_heading_center(cid=1)
        tview.align_heading_left(cid=2)
        tview.align_column_left(cid=0)
        tview.align_column_center(cid=1)
        tview.align_column_left(cid=2)
        return tview

    def get_file_rows(self):
        #-- some helper functions first
        def get_size_str(size):
            n = int(size)
            if n < 10**3:
                return f'{n}B'
            elif n < 10**6:
                return f'{n/10**3:.1f}kB'
            elif n < 10**9:
                return f'{n/10**6:.1f}MB'
            elif n < 10**12:
                return f'{n/10**9:.1f}GB'
            else:
                return f'{n/10**12:.1f}TB'
            
        def get_time_str(timestamp):
            modtime = datetime.datetime.fromtimestamp(timestamp)
            return datetime.datetime.strftime(modtime, '%Y-%m-%d %H:%M:%S')

        def get_file_type(direntry):
            if direntry.is_dir():
                return 'Directory'
            elif direntry.is_file():
                return 'File'
            elif direntry.is_symlink():
                return 'Symlink'
            else:
                return 'Bytes'

        parent_dir = os.path.expandvars(os.path.join(self.path.get(), '..'))
        full_parent = os.path.expanduser(parent_dir)
        statinfo = os.stat(full_parent)
        mtime = get_time_str(statinfo.st_mtime)
        rows = [('..', get_size_str(statinfo.st_size), 'Directory', mtime)]
        try:
            for ii in os.scandir(self.path.get()):
                if (not self.show_hidden) and ii.name.startswith('.'):
                    continue
                statinfo = ii.stat()
                size = get_size_str(statinfo.st_size)
                ftype = get_file_type(ii)
                changed = get_time_str(statinfo.st_mtime)
                rows.append((ii.name, f'{size}', f'{ftype}', f'{changed}'))
        except FileNotFoundError:
            msg = f'The directory {self.path.get()} does not exist.'
            Messagebox.show_error(msg, parent=self, title='File Selection')

        return rows

    def fill_table(self):
        global module_logger

        if len(self.path.get()) < 1:
            self.path.set(os.path.expanduser('~/'))
        self.tview.delete_rows()
        files = self.get_file_rows()
        self.tview.insert_rows(0, files)
        module_logger.debug(f'fill table: dir {self.path.get()}')
        module_logger.debug(f'fill table: files {files}')
        return

    def set_choices(self):
        # not sure there's anything to do yet ...
        self.destroy()

    def selections(self):
        return self.choices

def get_many_file_names(parent):
    fdlg = PlornFileDialog(parent=parent, allow_many=True,
                           title='Import Selected Photos')
    fdlg.grab_set()
    parent.wait_window(fdlg)
    choices = fdlg.selections()
    return choices


