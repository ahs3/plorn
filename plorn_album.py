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

import plorn_db
import plorn_common
import plorn_config
from plorn_config import FONTSIZE
import plorn_photo

module_logger = logging.getLogger('plorn.album')
module_logger.setLevel(logging.DEBUG)

class PlornAlbum:
    def __init__(self, name, id=None, dated='', notes='', photo_count=0,
                 names=[], places=[], tags=[]):
        self.id = id
        self.name = name
        self.dated = dated
        self.notes = notes
        self.photo_count = photo_count
        self.name_list = names
        self.place_list = places
        self.tag_list = tags

        module_logger.debug('initializing album object: ' + str(self))

    def __copy__(self):
        album = PlornAlbum(self.name, id=self.id,
                           dated=self.dated, notes=self.notes,
                           photo_count=self.photo_count)
        album.set_name_list(self.get_names_for_album(album))
        album.set_place_list(self.get_places_for_album(album))
        album.set_tag_list(self.get_tags_for_album(album))
        return album

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

    def set_name_list(self, name_list):
        self.name_list.clear()
        self.name_list = name_list

    def get_name_list(self):
        return self.name_list

    def add_name_to_list(self, name):
        self.name_list.append(name)

    def remove_name_from_list(self, name):
        self.name_list.remove(name)

    def set_place_list(self, place_list):
        self.place_list.clear()
        self.place_list = place_list

    def get_place_list(self):
        return self.place_list

    def add_place_to_list(self, place):
        self.place_list.append(place)

    def remove_place_from_list(self, place):
        self.place_list.remove(place)

    def set_tag_list(self, tag_list):
        self.tag_list.clear()
        self.tag_list = tag_list

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
        val += f', photo_count: \'{self.photo_count}\''
        val += f', name_list: \'{str(self.name_list)}\''
        val += f', place_list: \'{str(self.place_list)}\''
        val += f', tag_list: \'{str(self.tag_list)}\''
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


def build_left_frame(db, parent, album, default_state='normal'):
    tfont=font.nametofont('TkDefaultFont')
    lframedict = {}
    lframe = ttk.Frame(parent, padding='10 10 10 10')
    lframe.columnconfigure(0, weight=1)
    for ii in range(0,7):
        lframe.rowconfigure(ii, weight=1)
    lframedict['frame'] = lframe

    lab1 = ttk.Label(lframe, width=10, text='Name:')
    lab1.grid(column=0, row=0, sticky=(W))
    lframedict['lab1'] = lab1
    album_name = StringVar(lframe)
    album_name.set(album.get_name())
    lframedict['album_name'] = album_name
    album_entry = ttk.Entry(lframe, width=40,
                            textvariable=album_name,
                            font=tfont, state=default_state)
    album_entry.grid(column=1, row=0, sticky=(W))
    album_entry.focus_set()
    lframedict['album_entry'] = album_entry

    lab2 = ttk.Label(lframe, width=10, text='Dated:')
    lab2.grid(column=0, row=1, sticky=(W))
    lframedict['lab2'] = lab2
    dated = StringVar(lframe)
    dated.set(album.get_dated())
    lframedict['dated'] = dated
    date_entry = ttk.Entry(lframe, width=40,
                           textvariable=dated,
                           font=tfont, state=default_state)
    date_entry.grid(column=1, row=1, sticky=(W))
    lframedict['date_entry'] = date_entry

    lab3 = ttk.Label(lframe, width=10, text='Notes:')
    lab3.grid(column=0, row=2, sticky=(N, W))
    lframedict['lab3'] = lab3
    notes = Text(lframe, height=10, width=40, font=tfont)
    notes.insert('1.0', album.get_notes())
    note_state = 'normal'
    if default_state == 'readonly':
        note_state = 'disabled'
    notes.configure(state=note_state)
    notes.grid(column=1, row=2, sticky=(N, W, E, S))
    lframedict['notes'] = notes

    lab4 = ttk.Label(lframe, width=10, text='Photos:')
    lab4.grid(column=0, row=3, sticky=(N, W))
    lframedict['lab3'] = lab3
    photo_count = StringVar(lframe)
    photo_count.set(album.get_photo_count())
    lframedict['photo_count'] = photo_count
    photos = ttk.Entry(lframe, width=40,
                            textvariable=photo_count,
                            font=tfont, state=default_state)
    photos.grid(column=1, row=3, sticky=(W))
    lframedict['photos'] = photos

    return lframedict

def build_right_frame(db, parent, album, edit_lists=False,
                      name_cmds=(), place_cmds=(), tag_cmds=()):
    rframedict = {}
    rframe = ttk.Frame(parent, padding='10 10 10 10')
    rframe.columnconfigure(0, weight=20)
    rframe.columnconfigure(1, weight=1)
    for ii in range(0,3):
        rframe.rowconfigure(ii, weight=1)
    rframedict['frame'] = rframe

    add_icon = tk.PhotoImage(file='list-add.png')
    rframedict['add_icon'] = add_icon
    rm_icon = tk.PhotoImage(file='list-remove.png')
    rframedict['rm_icon'] = rm_icon

    name_listbox = build_listbox(rframe, "Names")
    name_listbox['frame'].grid(column=0, row=0, sticky=(N,W,E,S))
    names = album.get_name_list()
    name_listbox['listvar'].set([])
    name_list = []
    namedict = {}
    for ii in names:
        fullname = db.get_full_name(ii.get_id())
        namedict[ii.get_id()] = fullname
        name_list.append(fullname)
    name_listbox['listvar'].set(name_list)
    rframedict['names'] = names
    rframedict['namedict'] = namedict
    rframedict['name_listbox'] = name_listbox
    if edit_lists:
        add_cmd = None
        remove_cmd = None
        if name_cmds != None:
            add_cmd, remove_cmd = name_cmds
        nbframe = ttk.Frame(rframe, padding=(5,5,5,5))
        nbframe.columnconfigure(0, weight=1)
        nbframe.rowconfigure(0, weight=8)
        nbframe.rowconfigure(1, weight=1)
        nbframe.rowconfigure(2, weight=1)
        name_add = ttk.Button(nbframe, image=add_icon, command=add_cmd)
        name_add.grid(column=0, row=1)
        rframedict['name_add'] = name_add
        name_remove = ttk.Button(nbframe, image=rm_icon, command=remove_cmd)
        name_remove.grid(column=0, row=2)
        rframedict['name_remove'] = name_remove
        nbframe.grid(column=1, row=0, sticky=(N,W,E,S))

    place_listbox = build_listbox(rframe, "Places")
    place_listbox['frame'].grid(column=0, row=1, sticky=(N,W,E,S))
    places = album.get_place_list()
    place_listbox['listvar'].set([])
    place_list = []
    for ii in places:
        p = ', '.join(db.get_full_place(ii.get_id()))
        place_list.append(p)
    place_listbox['listvar'].set(place_list)
    rframedict['places'] = places
    rframedict['place_listbox'] = place_listbox
    if edit_lists:
        add_cmd = None
        remove_cmd = None
        if place_cmds != None:
            add_cmd, remove_cmd = place_cmds
        pbframe = ttk.Frame(rframe, padding=(5,5,5,5))
        pbframe.columnconfigure(0, weight=1)
        pbframe.rowconfigure(0, weight=8)
        pbframe.rowconfigure(1, weight=1)
        pbframe.rowconfigure(2, weight=1)
        place_add = ttk.Button(pbframe, image=add_icon, command=add_cmd)
        place_add.grid(column=0, row=1)
        rframedict['name_add'] = place_add
        place_remove = ttk.Button(pbframe, image=rm_icon, command=remove_cmd)
        place_remove.grid(column=0, row=2)
        rframedict['name_remove'] = place_remove
        pbframe.grid(column=1, row=1, sticky=(N,W,E,S))

    tag_listbox = build_listbox(rframe, "Tags")
    tag_listbox['frame'].grid(column=0, row=2, sticky=(N,W,E,S))
    tags = album.get_tag_list()
    tag_listbox['listvar'].set([])
    tag_list = []
    for ii in tags:
        p = '-'.join(db.get_full_tag(ii.get_id()))
        tag_list.append(p)
    tag_listbox['listvar'].set(tag_list)
    rframedict['tags'] = tags
    rframedict['tag_listbox'] = tag_listbox
    if edit_lists:
        add_cmd = None
        remove_cmd = None
        if tag_cmds != None:
            add_cmd, remove_cmd = tag_cmds
        tbframe = ttk.Frame(rframe, padding=(5,5,5,5))
        tbframe.columnconfigure(0, weight=1)
        tbframe.rowconfigure(0, weight=8)
        tbframe.rowconfigure(1, weight=1)
        tbframe.rowconfigure(2, weight=1)
        tag_add = ttk.Button(tbframe, image=add_icon, command=add_cmd)
        tag_add.grid(column=0, row=1)
        rframedict['tag_add'] = tag_add
        tag_remove = ttk.Button(tbframe, image=rm_icon, command=remove_cmd)
        tag_remove.grid(column=0, row=2)
        rframedict['tag_remove'] = tag_remove
        tbframe.grid(column=1, row=2, sticky=(N,W,E,S))

    return rframedict


class PlornShowAlbum(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornShowAlbum')
        self.tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.album = self.db.get_album(album_id)

        self.geometry('950x650')
        self.title('Album Info')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)

        self.lframe = build_left_frame(self.db, self, self.album,
                                       default_state='readonly')
        self.lframe['frame'].grid(column=0, row=0, sticky=(N,W,E,S))

        self.name_tree = None
        self.name_frame = None
        self.place_tree = None
        self.tag_tree = None
        self.rframe = plorn_common.PlornAttrFrame(self.db, self,
                base_obj=self.album,
                get_name_list=self.db.get_names_for_album,
                get_place_list=self.db.get_places_for_album,
                get_tag_list=self.db.get_tags_for_album,
        )
        self.rframe.get_frame().grid(column=1, row=0, sticky=(N,W,E,S))

        sep1 = ttk.Separator(self, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=2, sticky=(W+E))
        sep2 = ttk.Separator(self, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=2, sticky=(W+E))

        self.bdone = ttk.Button(self, text='Done',
                               command=self.destroy)
        self.bdone.grid(column=1, row=3)


class PlornRemoveAlbum(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornRemoveAlbum')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.album_id = album_id
        self.album = self.db.get_album(album_id)
        self.name_listbox = {}
        self.place_listbox = {}
        self.tag_listbox = {}

        self.geometry('950x650')
        self.title('Album to Remove')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.lframe = build_left_frame(self.db, self, self.album,
                                       default_state='readonly')
        self.lframe['frame'].grid(column=0, row=0, sticky=(N,W,E,S))

        self.name_tree = None
        self.name_frame = None
        self.place_tree = None
        self.tag_tree = None
        self.rframe = build_right_frame(self.db, self, self.album)
        self.rframe['frame'].grid(column=1, row=0, sticky=(N,W,E,S))

        sep1 = ttk.Separator(self, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=3, sticky=(W+E))

        self.do_remove = ttk.Button(self, text='Remove',
                                    command=self.confirm_remove)
        self.do_remove.grid(column=0, row=3, sticky=(E))
        self.cancel = ttk.Button(self, text='Cancel',
                                 command=self.destroy)
        self.cancel.grid(column=1, row=3, sticky=(W))

    def confirm_remove(self):
        album_name = self.lframe['album_name'].get()
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
        self.name_listbox = {}
        self.place_listbox = {}
        self.tag_listbox = {}

        self.geometry('950x650')
        self.title('Edit Album')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.lframe = build_left_frame(self.db, self, self.album,
                                       default_state='normal')
        self.lframe['photos'].configure(state='readonly')
        self.lframe['frame'].grid(column=0, row=0, sticky=(N,W,E,S))

        self.name_tree = None
        self.name_frame = None
        self.place_tree = None
        self.tag_tree = None
        self.rframe = build_right_frame(self.db, self, self.album,
                                edit_lists=True,
                                name_cmds=(self.add_name, self.remove_name),
                                place_cmds=(self.add_place, self.remove_place),
                                tag_cmds=(self.add_tag, self.remove_tag),
                               )
        self.rframe['frame'].grid(column=1, row=0, sticky=(N,W,E,S))

        sep1 = ttk.Separator(self, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=3, sticky=(W+E))

        self.bupdate = ttk.Button(self, text='Update',
                               command=self.update_album)
        self.bupdate.grid(column=0, row=3, sticky=(E))
        self.bcancel = ttk.Button(self, text='Cancel',
                                  command=self.destroy)
        self.bcancel.grid(column=1, row=3, sticky=(W))

    def add_name(self):
        messagebox.showinfo(parent=self,
                            title='Add Name to Album',
                            message='add_name called',
                            detail='do something here',
                           )

    def remove_name(self):
        global module_logger

        sel = self.rframe['name_listbox']['listbox'].curselection()
        if sel == ():
            messagebox.showerror(parent=self,
                                title='Remove Name from Album',
                                message='No name selected',
                                detail='Please select a name to be removed',
                           )
        else:
            idx = sel[0]
            nlist = list(self.rframe['name_listbox']['listvar'].get())
            lval = list(nlist.pop(idx))
            for ii in self.rframe['namedict'].keys():
                if self.rframe['namedict'][ii] == lval:
                    del self.rframe['namedict'][ii]
                    break
            self.rframe['name_listbox']['listvar'].set(nlist)

    def add_place(self):
        messagebox.showinfo(parent=self,
                            title='Add Place to Album',
                            message='add_place called',
                            detail='do something here',
                           )

    def remove_place(self):
        messagebox.showinfo(parent=self,
                            title='Remove Place from Album',
                            message='remove_place called',
                            detail='do something here',
                           )

    def add_tag(self):
        messagebox.showinfo(parent=self,
                            title='Add Tag to Album',
                            message='add_tag called',
                            detail='do something here',
                           )

    def remove_tag(self):
        messagebox.showinfo(parent=self,
                            title='Remove Tag from Album',
                            message='remove_tag called',
                            detail='do something here',
                           )

    def get_name_id_list(self, album):
        nlist = album.get_name_list()
        result = []
        for ii in nlist:
            result.append(ii.get_id())
        return result

    def rm_names(self, name_list, removal_list):
        result = []
        for ii in name_list:
            if ii.get_id() in removal_list:
                result.append(ii)
        return result

    def update_album(self):
        global module_logger

        prelist = self.get_name_id_list(self.album)
        module_logger.debug(f'update album pre: {str(prelist)}')

        album_copy = copy.deepcopy(self.album)
        if self.lframe['album_name'].get() != self.album.get_name():
            if self.db.album_exists(self.lframe['album_name'].get()):
                messagebox.showerror(parent=self,
                                     title='Updating an Album',
                                     message='Album already exists',
                                     detail='Please use another name',
                                    )
                return

        album_copy.set_name(self.lframe['album_name'].get())
        album_copy.set_dated(self.lframe['dated'].get())
        album_copy.set_notes(self.lframe['notes'].get('1.0', END))
        album_copy.set_photo_count(self.lframe['photo_count'].get())

        klist = list(self.rframe['namedict'].keys())
        module_logger.debug(f'update album to: {str(klist)}')
        nlist = self.rm_names(self.album.get_name_list(), klist)
        album_copy.set_name_list(nlist)

        plist = []
        for ii in self.rframe['places']:
            plist.append(ii.get_id())
        album_copy.set_place_list(plist)
        tlist = []
        for ii in self.rframe['tags']:
            tlist.append(ii.get_id())
        album_copy.set_tag_list(tlist)

        self.album = self.db.update_album(self.album, album_copy)

        aname = self.lframe['album_name'].get()
        msg = f'Updated Album \'{aname}\''
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

