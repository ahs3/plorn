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

import plorn_attr
import plorn_db
import plorn_common
import plorn_config
from plorn_config import FONTSIZE
import plorn_photo

module_logger = logging.getLogger('plorn.base_obj')
module_logger.setLevel(logging.DEBUG)

class PlornBaseObj:
    def __init__(self, name, id=None, dated='', notes='',
                 names=[], places=[], tags=[]):
        global module_logger

        self.name = name
        self.id = id
        self.dated = dated
        self.notes = notes
        self.name_list = names
        self.place_list = places
        self.tag_list = tags
        self.tk_parent = None

        module_logger.debug('initializing base object: ' + str(self))

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_dated(self, dated):
        self.dated = dated

    def get_dated(self):
        return self.dated

    def set_notes(self, notes):
        self.notes = notes

    def get_notes(self):
        return self.notes

    def set_name_list(self, name_list):
        self.name_list.clear()
        self.name_list = copy.deepcopy(name_list)

    def get_name_list(self):
        return self.name_list

    def add_name_to_list(self, name):
        self.name_list.append(name)

    def remove_name_from_list(self, name):
        for ii in range(0, len(self.name_list)):
            if self.name_list[ii].get_id() == name.get_id():
                del self.name_list[ii]
                break

    def set_place_list(self, place_list):
        #print(f'-- base: set_place_list')
        #print(f'-- base: input place_list')
        #for ii in place_list:
        #    print(f'   {str(ii)}')
        self.place_list.clear()
        self.place_list = copy.deepcopy(place_list)

    def get_place_list(self):
        return self.place_list

    def add_place_to_list(self, place):
        self.place_list.append(place)

    def remove_place_from_list(self, place):
        self.place_list.remove(place)

    def set_tag_list(self, tag_list):
        self.tag_list.clear()
        self.tag_list = copy.deepcopy(tag_list)

    def get_tag_list(self):
        return self.tag_list

    def add_tag_to_list(self, tag):
        self.tag_list.append(tag)

    def remove_tag_from_list(self, tag):
        self.tag_list.remove(tag)

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', name: \'{self.name}\''
        val += f', dated: \'{self.dated}\''
        val += f', notes: \'{self.notes}\''
        val += f', name_list: \'{str(self.name_list)}\''
        val += f', place_list: \'{str(self.place_list)}\''
        val += f', tag_list: \'{str(self.tag_list)}\''
        return val

