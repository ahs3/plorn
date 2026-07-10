
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
import filetype
import getpass
import logging
import os
import shutil
from enum import IntEnum

#import ttkbootstrap as ttk
#from ttkbootstrap.constants import *
#from ttkbootstrap.widgets.tableview import Tableview, TableRow
#from ttkbootstrap.dialogs.message import Messagebox

#import plorn.db
from plorn.config import config

module_logger = logging.getLogger('plorn.common')
module_logger.setLevel(logging.INFO)


class SearchDomains(IntEnum):
    ALBUMS = 0
    PHOTOS = 1
    ALL    = 2

SearchDomainStrings = [ 'Albums', 'Photos', 'Albums & Photos', ]

class SearchFields(IntEnum):
    NAME = 0
    PATH = 1
    DATED = 2
    NOTES = 3
    PHOTO_COUNTS = 4
    NAME_ATTR = 5
    PLACE_ATTR = 6
    TAG_ATTR = 7

SearchFieldStrings = [
    'Name', 'Path', 'Dated', 'Notes', 'Photo Counts',
    'Name Attribute', 'Place Attribute', 'Tag Attribute',
]

AlbumSearchInfo = {
    SearchFields.NAME: 'name',
    SearchFields.DATED: 'dated',
    SearchFields.NOTES: 'notes',
    SearchFields.PHOTO_COUNTS: 'photo_count',
}

PhotoSearchInfo = {
    SearchFields.NAME: 'name',
    SearchFields.PATH: 'path',
    SearchFields.DATED: 'dated',
    SearchFields.NOTES: 'notes',
}

AttrSearchInfo = {
    SearchFields.NAME_ATTR: 'names',
    SearchFields.PLACE_ATTR: 'places',
    SearchFields.TAG_ATTR: 'tags',
}


#class PlornAttrListbox:
#    '''
#    Build a common listbox for use by PlornAttr lists
#    '''
#    def __init__(self, parent, title='Attributes'):
#        self.parent = parent
#        self.title = title
#    
#        self.lsframe = ttk.Frame(self.parent, padding='5 5 5 5')
#        self.lsframe.columnconfigure(0, weight=9)
#        self.lsframe.columnconfigure(1, weight=1)
#        self.lsframe.rowconfigure(0, weight=2)
#        self.lsframe.rowconfigure(1, weight=8)
#
#        self.lab1 = ttk.Label(self.lsframe, text=f'Associated {title}:')
#        self.lab1.grid(column=0, row=0, sticky=(W))
#
#        self.listvar = []
#        self.listscroll = ttk.Scrollbar(self.lsframe)
#        self.listbox = ttk.Treeview(self.lsframe,
#                                    yscrollcommand=self.listscroll.set,
#                                    show='tree',
#                                    height=4,
#                                    selectmode='browse',
#                                    selecttype='item')
#        self.listscroll.configure(command=self.listbox.yview)
#        self.listbox.grid(column=0, row=1, sticky=(N,W,E,S))
#        self.listscroll.grid(column=1, row=1, sticky=(N,W,E,S))
#
#    def get_frame(self):
#        return self.lsframe
#
#    def get_listvar(self):
#        self.listvar.clear()
#        for ii in self.listbox.get_children():
#            self.listvar.append(self.listbox.item(ii)['text'])
#        return self.listvar
#
#    def set_listvar(self, value_list):
#        self.listvar.clear()
#        self.listvar = value_list
#        for ii in self.listbox.get_children():
#            self.listbox.delete(ii)
#        for ii in self.listvar:
#            self.listbox.insert('', 'end', text=ii)
#
#    def curselection(self):
#        result = ''
#        item = self.listbox.focus()
#        if item != '':
#            result = item[1]
#        return result
#
#    def get(self, idx):
#        return self.listbox.get(idx)
#
#
#class PlornAttrFrame:
#    '''
#    This is common code for the right frame of the album or photo
#    notebook pages.
#    '''
#    def __init__(self, db, parent,
#                 base_obj=None,         # current object (album or photo)
#                 get_name_list=None,    # callback for list of name objects
#                 get_place_list=None,   # callback for list of place objects
#                 get_tag_list=None,     # callback for list of tag objects
#                 edit_lists=False,      # should i add +/- buttons or not?
#                ):
#        self.db = db
#        self.parent = parent
#        self.base_obj = base_obj
#        self.get_name_list = get_name_list
#        self.get_place_list = get_place_list
#        self.get_tag_list = get_tag_list
#        self.edit_lists = edit_lists
#
#        self.rframe = ttk.Frame(parent, padding='10 10 10 10')
#        self.rframe.columnconfigure(0, weight=20)
#        self.rframe.columnconfigure(1, weight=1)
#        for ii in range(0,3):
#            self.rframe.rowconfigure(ii, weight=1)
#
#        plus = os.path.join(os.path.dirname(__file__), 'list-add.png')
#        minus = os.path.join(os.path.dirname(__file__), 'list-remove.png')
#        self.add_icon = ttk.PhotoImage(file=plus)
#        self.rm_icon = ttk.PhotoImage(file=minus)
#
#        self.name_listbox = PlornAttrListbox(self.rframe, title='Names')
#        self.name_listbox.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))
#        self.names = []
#        self.names_dict = {}
#        names = []
#        if self.base_obj != None:
#            names = self.get_name_list(self.base_obj)
#        self.set_name_listbox_values(names)
#
#        self.name_add_cmd = None
#        self.name_remove_cmd = None
#        self.nbframe, self.name_add, self.name_remove = \
#                self.add_edit_frame(self.name_add_cmd, self.name_remove_cmd)
#        if self.nbframe != None:
#            self.nbframe.grid(column=1, row=0, sticky=(N,W,E,S))
#
#        self.place_listbox = PlornAttrListbox(self.rframe, title='Places')
#        self.place_listbox.get_frame().grid(column=0, row=1, sticky=(N,W,E,S))
#        self.places = []
#        self.places_dict = {}
#        places = []
#        if self.base_obj != None:
#            places = self.get_place_list(base_obj)
#        self.set_place_listbox_values(places)
#
#        self.place_add_cmd = None
#        self.place_remove_cmd = None
#        self.pbframe, self.place_add, self.place_remove = \
#                self.add_edit_frame(self.place_add_cmd, self.place_remove_cmd)
#        if self.pbframe != None:
#            self.pbframe.grid(column=1, row=1, sticky=(N,W,E,S))
#
#        self.tag_listbox = PlornAttrListbox(self.rframe, title='Tags')
#        self.tag_listbox.get_frame().grid(column=0, row=2, sticky=(N,W,E,S))
#        self.tags = []
#        self.tags_dict = {}
#        tags = []
#        if self.base_obj != None:
#            tags = self.get_tag_list(base_obj)
#        self.set_tag_listbox_values(tags)
#
#        self.tag_add_cmd = None
#        self.tag_remove_cmd = None
#        self.tbframe, self.tag_add, self.tag_remove = \
#                self.add_edit_frame(self.tag_add_cmd, self.tag_remove_cmd)
#        if self.tbframe != None:
#            self.tbframe.grid(column=1, row=2, sticky=(N,W,E,S))
#
#    def get_frame(self):
#        return self.rframe
#
#    def set_name_listbox_values(self, name_list):
#        self.names.clear()
#        self.names_dict.clear()
#        if len(name_list) > 0:
#            self.names = copy.deepcopy(name_list)
#            for ii in name_list:
#                fullname = ', '.join(self.db.get_full_name(ii))
#                self.names_dict[fullname] = ii
#            self.name_listbox.set_listvar(list(self.names_dict.keys()))
#        else:
#            self.name_listbox.set_listvar([])
#
#    def get_name_listbox_value(self):
#        global module_logger
#
#        value = self.name_listbox.curselection()
#        module_logger.debug(f'get_name_listbox_value: {str(value)}')
#        if value in self.names_dict:
#            return self.names_dict[value]
#        else:
#            return None
#
#    def get_listbox_names(self):
#        result = []
#        nlist = self.name_listbox.get_listvar()
#        module_logger.debug(f'get_listbox_names: {str(nlist)}')
#        for ii in nlist:
#            result.append(self.names_dict[ii])
#        return result
#
#    def set_place_listbox_values(self, place_list):
#        self.places.clear()
#        self.places_dict.clear()
#        if len(place_list) > 0:
#            self.places = copy.deepcopy(place_list)
#            for ii in place_list:
#                fullplace = ', '.join(self.db.get_full_place(ii))
#                self.places_dict[fullplace] = ii
#            self.place_listbox.set_listvar(list(self.places_dict.keys()))
#        else:
#            self.place_listbox.set_listvar([])
#
#    def get_place_listbox_value(self):
#        global module_logger
#
#        value = self.place_listbox.curselection()
#        module_logger.debug(f'get_place_listbox_value: {str(value)}')
#        if value in self.places_dict:
#            return self.places_dict[value]
#        else:
#            return None
#
#    def get_listbox_places(self):
#        result = []
#        for ii in self.places_dict.keys():
#            result.append(self.places_dict[ii])
#        return result
#
#    def set_tag_listbox_values(self, tag_list):
#        self.tags.clear()
#        self.tags_dict.clear()
#        if len(tag_list) > 0:
#            self.tags = copy.deepcopy(tag_list)
#            for ii in tag_list:
#                fulltag = '/'.join(self.db.get_full_tag(ii))
#                self.tags_dict[fulltag] = ii
#            self.tag_listbox.set_listvar(list(self.tags_dict.keys()))
#        else:
#            self.tag_listbox.set_listvar([])
#
#    def get_tag_listbox_value(self):
#        global module_logger
#
#        value = self.tag_listbox.curselection()
#        module_logger.debug(f'get_tag_listbox_value: {str(value)}')
#        if value in self.tags_dict:
#            return self.tags_dict[value]
#        else:
#            return None
#
#    def get_listbox_tags(self):
#        result = []
#        for ii in self.tags_dict.keys():
#            result.append(self.tags_dict[ii])
#        return result
#
#    def add_edit_frame(self, add_cmd, remove_cmd):
#        bframe = None
#        add_button = None
#        remove_button = None
#
#        if not self.edit_lists:
#            return (bframe, add_button, remove_button)
#
#        bframe = ttk.Frame(self.rframe, padding=(5,5,5,5))
#        bframe.columnconfigure(0, weight=1)
#        bframe.rowconfigure(0, weight=8)
#        bframe.rowconfigure(1, weight=1)
#        bframe.rowconfigure(2, weight=1)
#        add_button = ttk.Button(bframe, image=self.add_icon, command=add_cmd)
#        add_button.grid(column=0, row=1)
#        remove_button = ttk.Button(bframe, image=self.rm_icon,
#                                   command=remove_cmd)
#        remove_button.grid(column=0, row=2)
#        return (bframe, add_button, remove_button)
#
#    def set_name_commands(self, add_cmd, remove_cmd):
#        if self.edit_lists:
#            self.name_add.configure(command=add_cmd)
#            self.name_remove.configure(command=remove_cmd)
#
#    def set_place_commands(self, add_cmd, remove_cmd):
#        if self.edit_lists:
#            self.place_add.configure(command=add_cmd)
#            self.place_remove.configure(command=remove_cmd)
#
#    def set_tag_commands(self, add_cmd, remove_cmd):
#        if self.edit_lists:
#            self.tag_add.configure(command=add_cmd)
#            self.tag_remove.configure(command=remove_cmd)
#
