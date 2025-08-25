import logging

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.album")
module_logger.setLevel(logging.INFO)

class PlornAlbum:
    def __init__(self, name, path, dated, notes, copy_choice, photo_count):
        self.name = name
        self.path = path
        self.dated = dated
        self.notes = notes
        self.copy_choice = copy_choice
        self.photo_count = photo_count

        module_logger.debug("adding " + str(self))

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

    def set_copy_choice(self, copy_choice):
        self.copy_choice = copy_choice

    def get_copy_choice(self):
        return self.copy_choice

    def make_link(self):
        return self.copy_choice == "link"

    def set_photo_count(self, photo_count):
        self.photo_count = photo_count

    def get_photo_count(self):
        return self.photo_count

    def __str__(self):
        val = f"name: \"{self.name}\""
        val += f", path: \"{self.path}\""
        val += f", dated: \"{self.dated}\""
        val += f", notes: \"{self.notes}\""
        val += f", copy_choice: \"{self.copy_choice}\""
        val += f", photo_count: \"{self.photo_count}\""
        return val


class PlornAddAlbum(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        module_logger.debug("started PlornAddAlbum")
        tfont = font.nametofont("TkDefaultFont")

        self.geometry("800x600")
        self.title("Add an Album")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,11):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text="Name:")
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont)
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.album_path = StringVar(self.frame)
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.album_path,
                                    font=tfont)
        self.path_entry.grid(column=1, row=1, sticky=(W))
        self.bdir = ttk.Button(self.frame, text="Browse",
                               command=self.get_dirname)
        self.bdir.grid(column=2, row=1)

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont)
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        lab4 = ttk.Label(self.frame, text="Import via:")
        lab4.grid(column=0, row=6)
        self.choice_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        self.choice_frame.grid(column=1, row=6)
        self.copy_choice = StringVar(self.choice_frame)
        symlink = ttk.Radiobutton(self.choice_frame, text="Symbolic link?",
                                  value="link", variable=self.copy_choice)
        symlink.grid(column=0, row=0, sticky=W)
        cp = ttk.Radiobutton(self.choice_frame, text="Full copy?",
                             value="copy", variable=self.copy_choice)
        cp.grid(column=0, row=1, sticky=W)
        self.copy_choice.set(value="link")
        module_logger.debug(f"set connect choice to {self.copy_choice.get()}")

        sep3 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep3.grid(column=0, row=8, columnspan=3, sticky=(W+E))
        sep4 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep4.grid(column=0, row=9, columnspan=3, sticky=(W+E))

        self.photo_count = 0
        self.badd = ttk.Button(self.frame, text="Add",
                               command=self.add_album)
        self.badd.grid(column=0, row=10)
        self.bcancel = ttk.Button(self.frame, text="Cancel",
                                  command=self.destroy)
        self.bcancel.grid(column=2, row=10)

    def get_dirname(self):
        self.album_path = filedialog.askdirectory(parent=self,
                                       title="Select a Directory",
                                       mustexist=True)
        if self.album_path:
            self.path_entry.insert(0, self.album_path)

    def add_album(self):
        module_logger.debug("entered add_album")

        # need to figure out photo_count here ... and copy/link ...

        album = PlornAlbum(self.album_name.get(),
                           self.album_path.get(),
                           self.dated.get(),
                           self.notes.get("1.0", END),
                           self.copy_choice.get(),
                           self.photo_count,
                          )

        db = plorn_db.open()
        if db.album_exists(album):
            messagebox.showinfo(message="Album already exists")
        else:
            db.add_album(album)
            msg = f"Adding Album \"{self.album_name.get()}\""
            messagebox.showinfo(message=msg)

