import copy
import filetype
import getpass
import logging
import os
import shutil

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db
import plorn_config
from plorn_config import FONTSIZE

module_logger = logging.getLogger('plorn.common')
module_logger.setLevel(logging.DEBUG)

class PlornAttrListbox:
    '''
    Build a common listbox for use by PlornAttr lists
    '''
    def __init__(self, parent, title='Attributes'):
        self.parent = parent
        self.title = title
    
        self.lsframe = ttk.Frame(self.parent, padding='5 5 5 5')
        self.lsframe.columnconfigure(0, weight=9)
        self.lsframe.columnconfigure(1, weight=1)
        self.lsframe.rowconfigure(0, weight=1)
        self.lsframe.rowconfigure(1, weight=8)

        self.lab1 = ttk.Label(self.lsframe, text=f'Associated {title}:')
        self.lab1.grid(column=0, row=0, sticky=(W))

        self.listvar = tk.Variable(value=[])
        self.listbox = tk.Listbox(self.lsframe,
                                  listvariable=self.listvar,
                                  height=2,
                                  selectmode=tk.BROWSE,
                                 )
        self.listbox.grid(column=0, row=1, sticky=(N,W,E,S))

    def get_frame(self):
        return self.lsframe

    def get_listvar(self):
        return list(self.listvar.get())

    def set_listvar(self, value_list):
        self.listvar.set(value_list)


class PlornAttrFrame:
    '''
    This is common code for the right frame of the album or photo
    notebook pages.
    '''
    def __init__(self, db, parent,
                 base_obj=None,         # current object (album or photo)
                 get_name_list=None,    # callback for list of name objects
                 get_place_list=None,   # callback for list of place objects
                 get_tag_list=None,     # callback for list of tag objects
                 edit_lists=False,      # should i add +/- buttons or not?
                ):
        self.db = db
        self.parent = parent
        self.base_obj = base_obj
        self.get_name_list = get_name_list
        self.get_place_list = get_place_list
        self.get_tag_list = get_tag_list
        self.edit_lists = edit_lists

        self.rframe = ttk.Frame(parent, padding='10 10 10 10')
        self.rframe.columnconfigure(0, weight=20)
        self.rframe.columnconfigure(1, weight=1)
        for ii in range(0,3):
            self.rframe.rowconfigure(ii, weight=1)

        self.add_icon = tk.PhotoImage(file='list-add.png')
        self.rm_icon = tk.PhotoImage(file='list-remove.png')

        self.name_listbox = PlornAttrListbox(self.rframe, title='Names')
        self.name_listbox.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))
        self.names = []
        self.names_dict = {}
        self.name_listbox.set_listvar([])
        if self.base_obj != None:
            self.names = self.get_name_list(self.base_obj)
            if len(self.names) > 0:
                for ii in self.names:
                    fullname = ', '.join(self.db.get_full_name(ii))
                    self.names_dict[fullname] = ii
                self.name_listbox.set_listvar(list(self.names_dict.keys()))

        self.name_add_cmd = None
        self.name_remove_cmd = None
        self.nbframe, self.name_add, self.name_remove = \
                self.add_edit_frame(self.name_add_cmd, self.name_remove_cmd)
        if self.nbframe != None:
            self.nbframe.grid(column=1, row=0, sticky=(N,W,E,S))

        self.place_listbox = PlornAttrListbox(self.rframe, title='Places')
        self.place_listbox.get_frame().grid(column=0, row=1, sticky=(N,W,E,S))
        self.places = []
        self.places_dict = {}
        self.place_listbox.set_listvar([])
        if self.base_obj != None:
            self.places = self.get_place_list(base_obj)
            module_logger.debug(f'place list: {str(self.places)}')
            if len(self.places) > 0:
                for ii in self.places:
                    fullplace = ', '.join(self.db.get_full_place(ii))
                    self.places_dict[fullplace] = ii
                self.place_listbox.set_listvar(list(self.places_dict.keys()))

        self.place_add_cmd = None
        self.place_remove_cmd = None
        self.pbframe, self.place_add, self.place_remove = \
                self.add_edit_frame(self.place_add_cmd, self.place_remove_cmd)
        if self.pbframe != None:
            self.pbframe.grid(column=1, row=1, sticky=(N,W,E,S))

        self.tag_listbox = PlornAttrListbox(self.rframe, title='Tags')
        self.tag_listbox.get_frame().grid(column=0, row=2, sticky=(N,W,E,S))
        self.tags = []
        self.tags_dict = {}
        self.tag_listbox.set_listvar([])
        if self.base_obj != None:
            self.tags = self.get_tag_list(base_obj)
            module_logger.debug(f'tag list: {str(self.tags)}')
            if len(self.tags) > 0:
                for ii in self.tags:
                    fulltag = '/'.join(self.db.get_full_tag(ii))
                    self.tags_dict[fulltag] = ii
                self.tag_listbox.set_listvar(list(self.tags_dict.keys()))

        self.tag_add_cmd = None
        self.tag_remove_cmd = None
        self.tbframe, self.tag_add, self.tag_remove = \
                self.add_edit_frame(self.tag_add_cmd, self.tag_remove_cmd)
        if self.tbframe != None:
            self.tbframe.grid(column=1, row=2, sticky=(N,W,E,S))

    def get_frame(self):
        return self.rframe

    def add_edit_frame(self, add_cmd, remove_cmd):
        bframe = None
        add_button = None
        remove_button = None

        if not self.edit_lists:
            return (bframe, add_button, remove_button)

        bframe = ttk.Frame(self.rframe, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=8)
        bframe.rowconfigure(1, weight=1)
        bframe.rowconfigure(2, weight=1)
        add_button = ttk.Button(bframe, image=self.add_icon, command=add_cmd)
        add_button.grid(column=0, row=1)
        remove_button = ttk.Button(bframe, image=self.rm_icon,
                                   command=remove_cmd)
        remove_button.grid(column=0, row=2)
        return (bframe, add_button, remove_button)

