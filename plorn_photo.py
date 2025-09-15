import filetype
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


class PlornShowPhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug("started PlornShowPhoto")
        tfont = font.nametofont("TkDefaultFont")
        self.db = plorn_db.open()
        self.photo = self.db.get_photo(photo_id)

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
        self.photo_name.set(self.photo.get_name())
        self.photo_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.photo_name,
                                     font=tfont, state="readonly")
        self.photo_entry.grid(column=1, row=0, sticky=(W))
        self.photo_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.photo_path = StringVar(self.frame)
        self.photo_path.set(self.photo.get_path())
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.photo_path,
                                    font=tfont, state="readonly")
        self.path_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(self.photo.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state="readonly")
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", self.photo.get_notes())
        self.notes.configure(state="disabled")
        module_logger.debug(f"notes: {self.photo.get_notes()}")
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
        self.img = pilImage.open(self.photo.get_path())
        self.resize_img = self.img.resize((600, 450))
        self.canvas_img = ImageTk.PhotoImage(image=self.resize_img)
        self.canvas.create_image(10, 10, anchor=NW, image=self.canvas_img)


class PlornRemovePhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug("started PlornRemovePhoto")
        tfont = font.nametofont("TkDefaultFont")
        self.db = plorn_db.open()
        self.photo = self.db.get_photo(photo_id)
        self.photo_id = photo_id

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
        self.photo_name.set(self.photo.get_name())
        self.photo_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.photo_name,
                                     font=tfont, state="readonly")
        self.photo_entry.grid(column=1, row=0, sticky=(W))
        self.photo_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.photo_path = StringVar(self.frame)
        self.photo_path.set(self.photo.get_path())
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.photo_path,
                                    font=tfont, state="readonly")
        self.path_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(self.photo.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state="readonly")
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", self.photo.get_notes())
        self.notes.configure(state="disabled")
        module_logger.debug(f"notes: {self.photo.get_notes()}")
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
        self.img = pilImage.open(self.photo.get_path())
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
            self.db.remove_photo_by_id(self.photo_id)
            self.destroy()

class PlornEditPhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug("started PlornEditPhoto")
        tfont = font.nametofont("TkDefaultFont")
        self.db = plorn_db.open()
        self.photo = self.db.get_photo(photo_id)
        self.photo_id = photo_id

        self.geometry("1250x600")
        self.title("Edit Photo")
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
        self.photo_name.set(self.photo.get_name())
        self.photo_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.photo_name,
                                     font=tfont)
        self.photo_entry.grid(column=1, row=0, sticky=(W))
        self.photo_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.photo_path = StringVar(self.frame)
        self.photo_path.set(self.photo.get_path())
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.photo_path,
                                    font=tfont)
        self.path_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(self.photo.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont)
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", self.photo.get_notes())
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        self.bupdate = ttk.Button(self.frame, text="Update",
                                  command=self.update_photo)
        self.bupdate.grid(column=0, row=6)
        self.bcancel = ttk.Button(self.frame, text="Cancel",
                                  command=self.destroy)
        self.bcancel.grid(column=1, row=6)
        self.bdone = ttk.Button(self.frame, text="Done",
                                command=self.destroy)
        self.bdone.grid(column=2, row=6)

        self.canvas = Canvas(self.frame, width=600, height=450)
        self.canvas.grid(column=2, row=1, rowspan=3, sticky=NE,
                         padx=(20,20))
        self.img = pilImage.open(self.photo.get_path())
        self.resize_img = self.img.resize((600, 450))
        self.canvas_img = ImageTk.PhotoImage(image=self.resize_img)
        self.canvas.create_image(10, 10, anchor=NW, image=self.canvas_img)

    def update_photo(self):
        fullpath = os.path.expandvars(os.path.expanduser(self.photo_path.get()))
        if os.path.isfile(fullpath):
            if filetype.is_image(fullpath):
                photo_copy = self.photo
                photo_copy.set_name(self.photo_name.get())
                photo_copy.set_path(self.photo_path.get())
                photo_copy.set_dated(self.dated.get())
                photo_copy.set_notes(self.notes.get("1.0", END))
                self.photo = self.db.update_photo(self.photo, photo_copy)
                msg = f"Updated Photo \"{self.photo_name.get()}\""
                messagebox.showinfo(parent=self, message=msg)
            else:
                messagebox.showerror(parent=self,
                                    title="Update a Photo",
                                    message="File is not a known image type",
                                    detail="Please choose another path.")
        else:
            messagebox.showerror(parent=self,
                                 title="Update a Photo",
                                 message="Image is not a regular file",
                                 detail="Please choose another path.")

        return


class PlornAddPhoto(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug("started PlornAddPhoto")
        tfont = font.nametofont("TkDefaultFont")
        self.album_id = album_id
        self.db = plorn_db.open()
        self.album = self.db.get_album(album_id)
        self.path = None
        self.new_photo = None

        self.geometry("800x600")
        self.title("Add Photo")
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
        self.photo_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.photo_name,
                                     font=tfont)
        self.photo_entry.grid(column=1, row=0, sticky=(W))
        self.photo_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.photo_path = StringVar(self.frame)
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.photo_path,
                                    font=tfont)
        self.path_entry.grid(column=1, row=1, sticky=(W))
        self.bdir = ttk.Button(self.frame, text="Browse",
                               command=self.get_image_name)
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

        self.bupdate = ttk.Button(self.frame, text="Add",
                                  command=self.add_photo)
        self.bupdate.grid(column=0, row=6)
        self.bcancel = ttk.Button(self.frame, text="Cancel",
                                  command=self.destroy)
        self.bcancel.grid(column=1, row=6)
        self.bdone = ttk.Button(self.frame, text="Done",
                                command=self.destroy)
        self.bdone.grid(column=2, row=6)

    def get_image_name(self):
        self.path = filedialog.askopenfilename(parent=self,
                                       title="Select an Image",
                                       initialdir=self.album.get_path(),
                                      )
        if self.path:
            self.path_entry.insert(0, self.path)

    def get_new_photo(self):
        return self.new_photo

    def add_photo(self):
        albumpath = os.path.expandvars(os.path.expanduser(self.album.get_path()))
        basename = os.path.basename(self.photo_path.get())
        if not os.path.exists(os.path.join(albumpath, basename)):
            messagebox.showerror(parent=self,
                                 title="Add a Photo",
                                 message=f"No path to image in {albumpath}",
                                 detail="Please choose another image.")
            return

        fullpath = os.path.expandvars(os.path.expanduser(self.photo_path.get()))
        if os.path.isfile(fullpath):
            if filetype.is_image(fullpath):
                photo = PlornPhoto(self.photo_name.get(),
                                   self.photo_path.get(),
                                   id=None,
                                   album_id=self.album_id,
                                   dated=self.dated.get(),
                                   notes=self.notes.get("1.0", END))
                self.new_photo = self.db.add_photo(photo)
                msg = f"Added Photo \"{self.photo_name.get()}\""
                messagebox.showinfo(parent=self, message=msg)
            else:
                messagebox.showerror(parent=self,
                                    title="Add a Photo",
                                    message="File is not a known image type",
                                    detail="Please choose another path.")
        else:
            messagebox.showerror(parent=self,
                                 title="Add a Photo",
                                 message="Image is not a regular file",
                                 detail="Please choose another path.")

