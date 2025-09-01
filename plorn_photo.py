import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.photo")
module_logger.setLevel(logging.DEBUG)

class PlornPhoto:
    def __init__(self, name, path, id=None, album_id=None, dated="", notes=""):
        self.id = id
        self.album_id = album_id
        self.name = name
        self.path = path
        self.dated = dated
        self.notes = notes

        module_logger.debug("adding " + str(self))

    def __copy__(self):
        return PlornPhoto(self.name, self.path, id=self.id,
                          album_id=self.album_id,
                          dated=self.dated, notes=self.notes)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_album_id(self, album_id):
        self.album_id = album_id

    def get_album_id(self):
        return self.album_id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def set_dated(self, dated):
        self.dated = dated

    def get_dated(self):
        return self.dated

    def set_notes(self, notes):
        self.notes = notes

    def get_notes(self):
        return self.notes

    def __str__(self):
        val  = f"id: \"{self.id}\""
        val += f", album_id: \"{self.album_id}\""
        val += f", name: \"{self.name}\""
        val += f", path: \"{self.path}\""
        val += f", dated: \"{self.dated}\""
        val += f", notes: \"{self.notes}\""
        return val

