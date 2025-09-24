import copy
import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger('plorn.attr')
module_logger.setLevel(logging.DEBUG)

class PlornAttr:
    '''
    Base class for the attributes of albums and photos,
    i.e., names, places, and tags
    '''
    def __init__(self, value, id=None, parent_id=None, table_name=''):
        self.value = value
        self.id = id
        self.parent_id = parent_id
        self.db_table_name = table_name

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def set_db_table_name(self, table_name):
        self.db_table_name = table_name

    def get_db_table_name(self):
        return self.db_table_name

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', value: \'{self.value}\''
        val += f', parent_id: \'{self.parent_id}\''
        val += f', db_table_name: \'{self.db_table_name}\''
        return val

