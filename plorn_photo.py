import logging
import os
from PIL import Image as pilImage
from PIL import ImageTk

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

def retrieve_photo_record(photo_id):
    db = plorn_db.open()
    record = db.get_photo_by_id(photo_id)
    return PlornPhoto(name=record["name"],
                      path=record["path"],
                      id=record["id"],
                      dated=record["dated"],
                      notes=record["notes"],
                     )

class PlornShowPhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug("started PlornShowPhoto")
        tfont = font.nametofont("TkDefaultFont")
        photo = retrieve_photo_record(photo_id)

        self.geometry("1250x600")
        self.title("Photo Info")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=5)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,8):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text="Name:")
        lab1.grid(column=0, row=0, sticky=(W))
        self.photo_name = StringVar(self.frame)
        self.photo_name.set(photo.get_name())
        self.photo_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.photo_name,
                                     font=tfont, state="readonly")
        self.photo_entry.grid(column=1, row=0, sticky=(W))
        self.photo_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.photo_path = StringVar(self.frame)
        self.photo_path.set(photo.get_path())
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.photo_path,
                                    font=tfont, state="readonly")
        self.path_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(photo.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state="readonly")
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", photo.get_notes())
        self.notes.configure(state="disabled")
        module_logger.debug(f"notes: {photo.get_notes()}")
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        self.bdone = ttk.Button(self.frame, text="Done",
                               command=self.destroy)
        self.bdone.grid(column=1, row=6)

        self.canvas = Canvas(self.frame, width=600, height=450)
        self.canvas.grid(column=2, row=1, rowspan=3, sticky=NE,
                         padx=(20,20))
        self.img = pilImage.open(photo.get_path())
        self.resize_img = self.img.resize((600, 450))
        self.canvas_img = ImageTk.PhotoImage(image=self.resize_img)
        self.canvas.create_image(10, 10, anchor=NW, image=self.canvas_img)


def delete_photo_by_id(photo_id):
    module_logger.debug(f"removing photo {photo_id}")
    db = plorn_db.open()
    db.remove_photo_by_id(photo_id)

class PlornRemovePhoto(Toplevel):
    def __init__(self, parent, photo_id, photo_list):
        super().__init__(parent)
        module_logger.debug("started PlornRemovePhoto")
        tfont = font.nametofont("TkDefaultFont")
        photo = retrieve_photo_record(photo_id)
        self.photo_id = photo_id
        self.photo_list = photo_list

        self.geometry("1250x600")
        self.title("Photo to Remove")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=5)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,8):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text="Name:")
        lab1.grid(column=0, row=0, sticky=(W))
        self.photo_name = StringVar(self.frame)
        self.photo_name.set(photo.get_name())
        self.photo_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.photo_name,
                                     font=tfont, state="readonly")
        self.photo_entry.grid(column=1, row=0, sticky=(W))
        self.photo_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.photo_path = StringVar(self.frame)
        self.photo_path.set(photo.get_path())
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.photo_path,
                                    font=tfont, state="readonly")
        self.path_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(photo.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state="readonly")
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", photo.get_notes())
        self.notes.configure(state="disabled")
        module_logger.debug(f"notes: {photo.get_notes()}")
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        self.bcancel = ttk.Button(self.frame, text="Cancel",
                                  command=self.destroy)
        self.bcancel.grid(column=0, row=6)
        self.bremove = ttk.Button(self.frame, text="Remove",
                               command=self.confirm_remove)
        self.bremove.grid(column=1, row=6)

        self.canvas = Canvas(self.frame, width=600, height=450)
        self.canvas.grid(column=2, row=1, rowspan=3, sticky=NE,
                         padx=(20,20))
        self.img = pilImage.open(photo.get_path())
        self.resize_img = self.img.resize((600, 450))
        self.canvas_img = ImageTk.PhotoImage(image=self.resize_img)
        self.canvas.create_image(10, 10, anchor=NW, image=self.canvas_img)

    def confirm_remove(self):
        photo_name = self.photo_name.get()
        photo_path = self.photo_path.get()
        result = messagebox.askyesnocancel("Confirm Removal",
                    message=f"Remove photo {photo_name}?",
                    detail="Only removes the catalog entry, not the file.",
                    parent=self,
                 )
        if result is True:
            idx = 0
            for ii in self.photo_list:
                if ii["path"] == photo_path:
                    break
                else:
                    idx += 1
            delete_photo_by_id(self.photo_id)
            self.photo_list.pop(idx)
            self.destroy()

