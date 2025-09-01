import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.album")
module_logger.setLevel(logging.DEBUG)

class PlornAlbum:
    def __init__(self, name, path, id=None, dated="", notes="", photo_count=0):
        self.id = id
        self.name = name
        self.path = path
        self.dated = dated
        self.notes = notes
        self.photo_count = photo_count

        module_logger.debug("adding " + str(self))

    def __copy__(self):
        return PlornAlbum(self.name, self.path, id=self.id,
                          dated=self.dated, notes=self.notes,
                          photo_count=self.photo_count)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

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

    def set_photo_count(self, photo_count):
        self.photo_count = photo_count

    def get_photo_count(self):
        return self.photo_count

    def __str__(self):
        val  = f"id: \"{self.id}\""
        val += f", name: \"{self.name}\""
        val += f", path: \"{self.path}\""
        val += f", dated: \"{self.dated}\""
        val += f", notes: \"{self.notes}\""
        val += f", photo_count: \"{self.photo_count}\""
        return val


class PlornAddAlbum(Toplevel):
    def __init__(self, parent, album_list):
        super().__init__(parent)
        module_logger.debug("started PlornAddAlbum")
        tfont = font.nametofont("TkDefaultFont")
        self.name = ""
        self.path = ""
        self.album_list = album_list

        self.geometry("800x600")
        self.title("Add an Album")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,7):
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

        self.photo_count = 0
        self.badd = ttk.Button(self.frame, text="Add",
                               command=self.add_album)
        self.badd.grid(column=0, row=6)

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=1, row=6, sticky=(NS))
        self.bclear = ttk.Button(bframe, text="Clear",
                               command=self.clear_entries)
        self.bclear.grid(column=0, row=0)
        self.bcancel = ttk.Button(bframe, text="Cancel",
                                  command=self.destroy)
        self.bcancel.grid(column=1, row=0)
        self.bdone = ttk.Button(self.frame, text="Done",
                               command=self.destroy)
        self.bdone.grid(column=2, row=6)

    def get_dirname(self):
        self.path = filedialog.askdirectory(parent=self,
                                            title="Select a Directory",
                                            mustexist=True)
        if self.path:
            self.path_entry.insert(0, self.path)

    def clear_entries(self):
        self.name = ""
        self.album_name.set(self.name)
        self.path = ""
        self.album_path.set(self.path)
        self.dated.set("")
        self.notes.delete("1.0", END)
        self.photo_count = 0

    def add_album(self):
        global last_album

        module_logger.debug("entered add_album")
        self.name = self.album_name.get()
        self.path = self.album_path.get()
        module_logger.debug(f"add album name: {self.name}, path: {self.path}")
        album = PlornAlbum(self.album_name.get(),
                                        self.album_path.get(),
                                        id=None,
                                        dated=self.dated.get(),
                                        notes=self.notes.get("1.0", END),
                                        photo_count=self.photo_count,
                                       )

        db = plorn_db.open()
        if db.album_exists(album):
            messagebox.showerror(parent=self,
                                 title="Adding an Album",
                                 message="Album already exists",
                                 detail="Please use another name",
                                )
        else:
            fullpath = os.path.expandvars(os.path.expanduser(self.path))
            module_logger.debug(f"new album {self.name} from {fullpath}")
            if os.path.isdir(fullpath):
                id = db.add_album(album)
                album.set_id(id)
                self.album_list.append({"id": album.get_id(),
                                        "name": album.get_name(),
                                        "path": album.get_path(),
                                        "dated": album.get_dated(),
                                        "notes": album.get_notes(),
                                        "photo_count": album.get_photo_count()}
                                      )
                msg = f"Adding Album \"{album.get_name()}\""
                messagebox.showinfo(message=msg, parent=self)
            else:
                messagebox.showerror(parent=self,
                                     title="Adding an Album",
                                     message="Path is not a directory",
                                     detail="Please choose another path",
                                    )

def retrieve_album_record(name):
    db = plorn_db.open()
    record = db.get_album_by_name(name)
    return PlornAlbum(record["name"],
                      record["path"],
                      id=record["id"],
                      dated=record["dated"],
                      notes=record["notes"],
                      photo_count=record["photo_count"],
                     )

def delete_album_by_name(name):
    db = plorn_db.open()
    db.remove_album_by_name(name)
    return

class PlornShowAlbum(Toplevel):
    def __init__(self, parent, album_name):
        super().__init__(parent)
        module_logger.debug("started PlornShowAlbum")
        tfont = font.nametofont("TkDefaultFont")
        album = retrieve_album_record(album_name)

        self.geometry("800x600")
        self.title("Album Info")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,8):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text="Name:")
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_name.set(album.get_name())
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont, state="readonly")
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.album_path = StringVar(self.frame)
        self.album_path.set(album.get_path())
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.album_path,
                                    font=tfont, state="readonly")
        self.path_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(album.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state="readonly")
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", album.get_notes())
        self.notes.configure(state="disabled")
        module_logger.debug(f"notes: {album.get_notes()}")
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        lab5 = ttk.Label(self.frame, width=10, text="Photos:")
        lab5.grid(column=0, row=4, sticky=(N, W))
        self.photo_count = StringVar(self.frame)
        self.photo_count.set(album.get_photo_count())
        self.photos = ttk.Entry(self.frame, width=40,
                                textvariable=self.photo_count,
                                font=tfont, state="readonly")
        self.photos.grid(column=1, row=4, sticky=(W))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=5, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=6, columnspan=3, sticky=(W+E))

        self.bdone = ttk.Button(self.frame, text="Done",
                               command=self.destroy)
        self.bdone.grid(column=1, row=7)


class PlornRemoveAlbum(Toplevel):
    def __init__(self, parent, album_name, album_list):
        super().__init__(parent)
        module_logger.debug("started PlornRemoveAlbum")
        tfont = font.nametofont("TkDefaultFont")
        album = retrieve_album_record(album_name)
        self.album_list = album_list

        self.geometry("800x600")
        self.title("Album to Remove")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,8):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text="Name:")
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_name.set(album.get_name())
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont, state="readonly")
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.album_path = StringVar(self.frame)
        self.album_path.set(album.get_path())
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.album_path,
                                    font=tfont, state="readonly")
        self.path_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text="Dated:")
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(album.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state="readonly")
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", album.get_notes())
        self.notes.configure(state="disabled")
        module_logger.debug(f"notes: {album.get_notes()}")
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        lab5 = ttk.Label(self.frame, width=10, text="Photos:")
        lab5.grid(column=0, row=4, sticky=(N, W))
        self.photo_count = StringVar(self.frame)
        self.photo_count.set(album.get_photo_count())
        self.photos = ttk.Entry(self.frame, width=40,
                                textvariable=self.photo_count,
                                font=tfont, state="readonly")
        self.photos.grid(column=1, row=4, sticky=(W))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=5, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=6, columnspan=3, sticky=(W+E))

        self.do_remove = ttk.Button(self.frame, text="Remove",
                                    command=self.confirm_remove)
        self.do_remove.grid(column=1, row=7, sticky=(E))
        self.cancel = ttk.Button(self.frame, text="Cancel",
                                 command=self.destroy)
        self.cancel.grid(column=2, row=7, sticky=(W))

    def confirm_remove(self):
        album_name = self.album_name.get()
        result = messagebox.askyesnocancel("Confirm Removal",
                    message=f"Remove album {album_name}?",
                    detail="Only removes the catalog entry, not the files.",
                    parent=self,
                 )
        if result is True:
            idx = 0
            for ii in self.album_list:
                if ii["name"] == album_name:
                    break
                else:
                    idx += 1
            delete_album_by_name(album_name)
            self.album_list.pop(idx)
            self.destroy()

class PlornEditAlbum(Toplevel):
    def __init__(self, parent, album_name, album_list):
        super().__init__(parent)
        module_logger.debug("started PlornEditAlbum")
        tfont = font.nametofont("TkDefaultFont")
        self.album = retrieve_album_record(album_name)
        self.album_list = album_list

        self.geometry("800x600")
        self.title("Edit Album")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,8):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text="Name:")
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_name.set(self.album.get_name())
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont)
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text="Path:")
        lab2.grid(column=0, row=1, sticky=(W))
        self.album_path = StringVar(self.frame)
        self.album_path.set(self.album.get_path())
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
        self.dated.set(self.album.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont)
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text="Notes:")
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert("1.0", self.album.get_notes())
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        lab5 = ttk.Label(self.frame, width=10, text="Photos:")
        lab5.grid(column=0, row=4, sticky=(N, W))
        self.photo_count = StringVar(self.frame)
        self.photo_count.set(self.album.get_photo_count())
        self.photos = ttk.Entry(self.frame, width=40,
                                textvariable=self.photo_count,
                                font=tfont)
        self.photos.grid(column=1, row=4, sticky=(W))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=5, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=6, columnspan=3, sticky=(W+E))

        self.bupdate = ttk.Button(self.frame, text="Update",
                               command=self.update_album)
        self.bupdate.grid(column=1, row=7, sticky=(E))
        self.bcancel = ttk.Button(self.frame, text="Cancel",
                                  command=self.destroy)
        self.bcancel.grid(column=2, row=7, sticky=(W))

    def get_dirname(self):
        self.path = filedialog.askdirectory(parent=self,
                                            title="Select a Directory",
                                            mustexist=True)
        if self.path:
            self.path_entry.insert(0, self.path)

    def update_album(self):
        fullpath = os.path.expandvars(os.path.expanduser(self.album_path.get()))
        if not os.path.isdir(fullpath):
            messagebox.showerror(parent=self,
                                     title="Adding an Album",
                                     message="Path is not a directory",
                                     detail="Please choose another path",
                                    )
            return

        album_copy = self.album.copy()
        db = plorn_db.open()
        if db.album_exists(album_copy):
            messagebox.showerror(parent=self,
                                 title="Adding an Album",
                                 message="Album already exists",
                                 detail="Please use another name",
                                )
            return

        album_copy.set_name(self.album_name.get())
        album_copy.set_name(self.album_name.get())
        album_copy.set_path(self.album_path.get())
        album_copy.set_dated(self.dated.get())
        album_copy.set_notes(self.notes.get("1.0", END))
        album_copy.set_photo_count(self.photo_count.get())
        id = db.update_album(self.album, album_copy)

        msg = f"Updated Album \"{self.album_name.get()}\""
        messagebox.showinfo(message=msg, parent=self)
        idx = 0
        for ii in self.album_list:
            if ii["name"] == self.album_name.get():
                break
            else:
                idx += 1
        self.album_list.pop(idx)
        self.album_list.append({"id": album_copy.get_id(),
                                "name": album_copy.get_name(),
                                "path": album_copy.get_path(),
                                "dated": album_copy.get_dated(),
                                "notes": album_copy.get_notes(),
                                "photo_count": album_copy.get_photo_count()}
                              )
        self.destroy()

