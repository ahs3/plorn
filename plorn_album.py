import filetype
import getpass
import logging
import os
import shutil

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db
import plorn_config
import plorn_photo

module_logger = logging.getLogger('plorn.album')
module_logger.setLevel(logging.DEBUG)

class PlornAlbum:
    def __init__(self, name, id=None, dated='', notes='', photo_count=0):
        self.id = id
        self.name = name
        self.dated = dated
        self.notes = notes
        self.photo_count = photo_count

        module_logger.debug('adding ' + str(self))

    def __copy__(self):
        return PlornAlbum(self.name, id=self.id,
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
        val  = f'id: \'{self.id}\''
        val += f', name: \'{self.name}\''
        val += f', dated: \'{self.dated}\''
        val += f', notes: \'{self.notes}\''
        val += f', photo_count: \'{self.photo_count}\''
        return val


class PlornAddAlbum(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        module_logger.debug('started PlornAddAlbum')
        tfont = font.nametofont('TkDefaultFont')
        self.name = ''
        self.new_album = None
        self.photo_list = {}
        self.db = plorn_db.open()
        self.cfg = plorn_config.get_config()

        self.geometry('800x600')
        self.title('Add an Album')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,6):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text='Name:')
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont)
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text='Dated:')
        lab2.grid(column=0, row=1, sticky=(W))
        self.dated = StringVar(self.frame)
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont)
        self.date_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text='Notes:')
        lab3.grid(column=0, row=2, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.grid(column=1, row=2, sticky=(N, W, E, S))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=3, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=4, columnspan=3, sticky=(W+E))

        self.photo_count = 0
        self.badd = ttk.Button(self.frame, text='Add',
                               command=self.add_album)
        self.badd.grid(column=0, row=6)

        bframe = ttk.Frame(self.frame, padding='10 10 10 10')
        bframe.grid(column=1, row=6, sticky=(NS))
        self.bclear = ttk.Button(bframe, text='Clear',
                               command=self.clear_entries)
        self.bclear.grid(column=0, row=0)
        self.bcancel = ttk.Button(bframe, text='Cancel',
                                  command=self.destroy)
        self.bcancel.grid(column=1, row=0)
        self.bdone = ttk.Button(self.frame, text='Done',
                               command=self.destroy)
        self.bdone.grid(column=2, row=6)

    def get_dirname(self):
        self.path = filedialog.askdirectory(parent=self,
                                            title='Select a Directory',
                                            mustexist=True)
        if self.path:
            self.path_entry.insert(0, self.path)

    def get_new_album(self):
        return self.new_album

    def get_photo_list(self):
        return self.photo_list

    def clear_entries(self):
        self.name = ''
        self.album_name.set(self.name)
        self.dated.set('')
        self.notes.delete('1.0', END)
        self.photo_count = 0
        self.photo_list.clear()

    def add_album(self):
        module_logger.debug('entered add_album')
        self.name = self.album_name.get()
        module_logger.debug(f'add album name: {self.name}')
        album = PlornAlbum(self.album_name.get(),
                           id=None,
                           dated=self.dated.get(),
                           notes=self.notes.get('1.0', END),
                           photo_count=self.photo_count,
                          )

        if self.db.album_exists(album):
            messagebox.showerror(parent=self,
                                 title='Adding an Album',
                                 message='Album already exists',
                                 detail='Please use another name',
                                )
        else:
            self.new_album = self.db.add_album(album)
            msg = f'Adding Album \'{album.get_name()}\''
            messagebox.showinfo(message=msg, parent=self)


class PlornShowAlbum(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornShowAlbum')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.album = self.db.get_album(album_id)

        self.geometry('800x600')
        self.title('Album Info')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,7):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text='Name:')
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_name.set(self.album.get_name())
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont, state='readonly')
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text='Dated:')
        lab2.grid(column=0, row=1, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(self.album.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state='readonly')
        self.date_entry.grid(column=1, row=1, sticky=(W))

        lab3 = ttk.Label(self.frame, width=10, text='Notes:')
        lab3.grid(column=0, row=2, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert('1.0', self.album.get_notes())
        self.notes.configure(state='disabled')
        module_logger.debug(f'notes: {self.album.get_notes()}')
        self.notes.grid(column=1, row=2, sticky=(N, W, E, S))

        lab4 = ttk.Label(self.frame, width=10, text='Photos:')
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.photo_count = StringVar(self.frame)
        self.photo_count.set(self.album.get_photo_count())
        self.photos = ttk.Entry(self.frame, width=40,
                                textvariable=self.photo_count,
                                font=tfont, state='readonly')
        self.photos.grid(column=1, row=3, sticky=(W))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        self.bdone = ttk.Button(self.frame, text='Done',
                               command=self.destroy)
        self.bdone.grid(column=1, row=6)


class PlornRemoveAlbum(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornRemoveAlbum')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.album_id = album_id
        self.album = self.db.get_album(album_id)

        self.geometry('800x600')
        self.title('Album to Remove')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,7):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text='Name:')
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_name.set(self.album.get_name())
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont, state='readonly')
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab3 = ttk.Label(self.frame, width=10, text='Dated:')
        lab3.grid(column=0, row=1, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(self.album.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont, state='readonly')
        self.date_entry.grid(column=1, row=1, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text='Notes:')
        lab4.grid(column=0, row=2, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert('1.0', self.album.get_notes())
        self.notes.configure(state='disabled')
        module_logger.debug(f'notes: {self.album.get_notes()}')
        self.notes.grid(column=1, row=2, sticky=(N, W, E, S))

        lab5 = ttk.Label(self.frame, width=10, text='Photos:')
        lab5.grid(column=0, row=3, sticky=(N, W))
        self.photo_count = StringVar(self.frame)
        self.photo_count.set(self.album.get_photo_count())
        self.photos = ttk.Entry(self.frame, width=40,
                                textvariable=self.photo_count,
                                font=tfont, state='readonly')
        self.photos.grid(column=1, row=3, sticky=(W))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        self.do_remove = ttk.Button(self.frame, text='Remove',
                                    command=self.confirm_remove)
        self.do_remove.grid(column=1, row=6, sticky=(E))
        self.cancel = ttk.Button(self.frame, text='Cancel',
                                 command=self.destroy)
        self.cancel.grid(column=2, row=6, sticky=(W))

    def confirm_remove(self):
        album_name = self.album_name.get()
        result = messagebox.askyesnocancel('Confirm Removal',
                    message=f'Remove album {album_name}?',
                    detail='Removes only the catalog entries, not the files.',
                    parent=self,
                 )
        if result is True:
            idx = 0
            self.db.remove_album(self.album)
            self.destroy()

class PlornEditAlbum(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornEditAlbum')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.album = self.db.get_album(album_id)

        self.geometry('800x600')
        self.title('Edit Album')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,7):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text='Name:')
        lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.frame)
        self.album_name.set(self.album.get_name())
        self.album_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.album_name,
                                     font=tfont)
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        lab3 = ttk.Label(self.frame, width=10, text='Dated:')
        lab3.grid(column=0, row=1, sticky=(W))
        self.dated = StringVar(self.frame)
        self.dated.set(self.album.get_dated())
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont)
        self.date_entry.grid(column=1, row=1, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text='Notes:')
        lab4.grid(column=0, row=2, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.insert('1.0', self.album.get_notes())
        self.notes.grid(column=1, row=2, sticky=(N, W, E, S))

        lab5 = ttk.Label(self.frame, width=10, text='Photos:')
        lab5.grid(column=0, row=3, sticky=(N, W))
        self.photo_count = StringVar(self.frame)
        self.photo_count.set(self.album.get_photo_count())
        self.photos = ttk.Entry(self.frame, width=40,
                                textvariable=self.photo_count,
                                font=tfont, state="readonly")
        self.photos.grid(column=1, row=3, sticky=(W))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        self.bupdate = ttk.Button(self.frame, text='Update',
                               command=self.update_album)
        self.bupdate.grid(column=1, row=7, sticky=(E))
        self.bcancel = ttk.Button(self.frame, text='Cancel',
                                  command=self.destroy)
        self.bcancel.grid(column=2, row=7, sticky=(W))

    def update_album(self):
        album_copy = self.album
        self.db = plorn_db.open()
        if self.album_name.get() != self.album.get_name():
            if self.db.album_exists(self.album_name.get()):
                messagebox.showerror(parent=self,
                                    title='Adding an Album',
                                    message='Album already exists',
                                    detail='Please use another name',
                                    )
                return

        album_copy.set_name(self.album_name.get())
        album_copy.set_dated(self.dated.get())
        album_copy.set_notes(self.notes.get('1.0', END))
        album_copy.set_photo_count(self.photo_count.get())
        self.album = self.db.update_album(self.album, album_copy)

        msg = f'Updated Album \'{self.album_name.get()}\''
        messagebox.showinfo(message=msg, parent=self)
        self.destroy()


class PlornImportToAlbum:
    def __init__(self, parent, album_id):
        module_logger.debug('started PlornImportAlbum')
        self.parent = parent
        self.album_id = album_id
        self.added_count = 0
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.album = self.db.get_album(self.album_id)

        image_list = self.collect_images()
        for path in image_list:
            name = os.path.basename(path)
            tmp = plorn_photo.PlornPhoto(name, path, id=None, album_id=album_id)
            photo = self.db.add_photo(tmp)
            self.added_count += 1

    def get_photo_count(self):
        return self.added_count

    def collect_images(self):
        home = os.path.expanduser('~/Pictures')
        startdir = os.path.expandvars(home)
        filelist = filedialog.askopenfilenames(parent=self.parent,
                                    initialdir=startdir,
                                    title='Select Images to Import',
                                    multiple=True,
                                   )
        
        image_list = []
        for ii in filelist:
            module_logger.debug(f'checking file type of {ii}')
            if os.path.isfile(ii):
                if filetype.is_image(ii):
                    module_logger.debug(f'collected image {ii}')
                    image_list.append(ii)
        module_logger.debug(f'selected images: {image_list}')
        return image_list

