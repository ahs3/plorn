import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.place")
module_logger.setLevel(logging.DEBUG)

class PlornPlace:
    def __init__(self, place, id=None, parent_id=None):
        self.place = place
        self.id = id
        self.parent_id = parent_id

    def __copy__(self):
        return PlornPlace(self.place, id=self.id, parent_id=self.parent_id)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_place(self, place):
        self.place = place

    def get_place(self):
        return self.place

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def __str__(self):
        val  = f"id: \"{self.id}\""
        val += f", place: \"{self.place}\""
        val += f", parent_id: \"{self.parent_id}\""
        return val

