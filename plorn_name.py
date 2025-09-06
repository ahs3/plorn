import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.name")
module_logger.setLevel(logging.DEBUG)

class PlornName:
    def __init__(self, name, id=None, parent_id=None):
        self.name = name
        self.id = id
        self.parent_id = parent_id

    def __copy__(self):
        return PlornName(self.name, id=self.id, parent_id=self.parent_id)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def __str__(self):
        val  = f"id: \"{self.id}\""
        val += f", name: \"{self.name}\""
        val += f", parent_id: \"{self.parent_id}\""
        return val

