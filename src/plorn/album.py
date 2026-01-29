
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

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

from PIL import Image as pilImage
from PIL.ExifTags import TAGS as pilTAGS
from PIL.ExifTags import GPSTAGS as pilGPSTAGS

import plorn.attr
import plorn.base_obj
import plorn.db
import plorn.common
import plorn.config
from plorn.config import FONTSIZE
import plorn.photo

module_logger = logging.getLogger('plorn.album')
module_logger.setLevel(logging.INFO)

class PlornAlbum(plorn.base_obj.PlornBaseObj):
    def __init__(self, name, id=None, dated='', notes='', photo_count=0,
                 names=[], places=[], tags=[]):
        self.photo_count = photo_count
        super().__init__(name, id, dated, notes, names, places, tags)
        module_logger.debug('initializing album object: ' + str(self))

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
        val += f', name_list: \'{str(self.name_list)}\''
        val += f', place_list: \'{str(self.place_list)}\''
        val += f', tag_list: \'{str(self.tag_list)}\''
        return val


class PlornAlbumLeftFrame:
    '''
    Factor out common code for building the left frame for building
    responses to commands on the album notebook tab
    '''
    def __init__(self, db, parent, album=None, default_state='normal'):
        self.db = db
        self.parent = parent
        self.album = album
        self.default_state = default_state
        self.tfont=font.nametofont('TkDefaultFont')
        self.lframe = ttk.Frame(self.parent, padding='10 10 10 10')
        self.lframe.columnconfigure(0, weight=1)
        self.lframe.columnconfigure(1, weight=2)
        for ii in range(0,7):
            self.lframe.rowconfigure(ii, weight=1)

        self.lab1 = ttk.Label(self.lframe, width=10, text='Name:')
        self.lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.lframe, value='')
        if self.album != None:
            self.album_name.set(self.album.get_name())
        self.album_entry = ttk.Entry(self.lframe, width=40,
                                     textvariable=self.album_name,
                                     font=self.tfont, state=self.default_state)
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        self.lab2 = ttk.Label(self.lframe, width=10, text='Dated:')
        self.lab2.grid(column=0, row=1, sticky=(W))
        self.dated = StringVar(self.lframe, value='')
        if self.album != None:
            self.dated.set(self.album.get_dated())
        self.date_entry = ttk.Entry(self.lframe, width=40,
                                    textvariable=self.dated,
                                    font=self.tfont, state=self.default_state)
        self.date_entry.grid(column=1, row=1, sticky=(W))

        self.lab3 = ttk.Label(self.lframe, width=10, text='Notes:')
        self.lab3.grid(column=0, row=2, sticky=(N, W))
        self.notes = Text(self.lframe, height=10, width=40, font=self.tfont)
        if self.album != None:
            self.notes.insert('1.0', self.album.get_notes())
        self.note_state = 'normal'
        if self.default_state == 'readonly':
            self.note_state = 'disabled'
        self.notes.configure(state=self.note_state)
        self.notes.grid(column=1, row=2, sticky=(N, W, E, S))

        self.lab4 = ttk.Label(self.lframe, width=10, text='Photos:')
        self.lab4.grid(column=0, row=3, sticky=(N, W))
        self.photo_count = StringVar(self.lframe, value='0')
        if self.album != None:
            self.photo_count.set(self.album.get_photo_count())
        self.photos = ttk.Entry(self.lframe, width=40,
                                textvariable=self.photo_count,
                                font=self.tfont, state='readonly')
        self.photos.grid(column=1, row=3, sticky=(W))

    def get_frame(self):
        return self.lframe

    def get_photos_field(self):
        return self.photos

    def get_album_name(self):
        return self.album_name.get()

    def get_dated(self):
        return self.dated.get()

    def get_notes(self):
        return self.notes.get('1.0', END)

    def get_photo_count(self):
        return self.photo_count.get()


class PlornAddAlbum(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        module_logger.debug('started PlornAddAlbum')
        tfont = font.nametofont('TkDefaultFont')
        self.name = ''
        self.new_album = PlornAlbum('')
        self.db = plorn.db.open()
        self.cfg = plorn.config.get_config()
        self.photo_count = 0

        self.geometry('950x650')
        self.title('Add an Album')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=2)

        self.lframe = PlornAlbumLeftFrame(self.db, self, album=None)
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn.common.PlornAttrFrame(self.db, self,
                base_obj=None,
                get_name_list=self.db.get_names_for_album,
                get_place_list=self.db.get_places_for_album,
                get_tag_list=self.db.get_tags_for_album,
                edit_lists=True,
        )
        self.rframe.get_frame().grid(column=1, row=0, sticky=(N,W,E,S))
        self.rframe.set_name_commands(self.add_name, self.remove_name)
        self.rframe.set_place_commands(self.add_place, self.remove_place)
        self.rframe.set_tag_commands(self.add_tag, self.remove_tag)

        self.sep1 = ttk.Separator(self, orient=HORIZONTAL)
        self.sep1.grid(column=0, row=1, columnspan=2, sticky=(W+E))
        self.sep2 = ttk.Separator(self, orient=HORIZONTAL)
        self.sep2.grid(column=0, row=2, columnspan=2, sticky=(W+E))

        self.bframe = ttk.Frame(self, padding='10 10 10 10')
        self.bframe.grid(column=0, row=3, columnspan=2, sticky=(W+E))
        self.add_buttons = [
            ttk.Button(self.bframe, text='Add', command=self.add_album),
            ttk.Button(self.bframe, text='Clear', command=self.clear_entries),
            ttk.Button(self.bframe, text='Cancel', command=self.destroy),
            ttk.Button(self.bframe, text='Done', command=self.destroy),
        ]
        self.bframe.rowconfigure(0, weight=1)
        self.bframe.columnconfigure(0, weight=50)
        for n in range(0, len(self.add_buttons)):
            self.bframe.columnconfigure(n+1, weight=1)
            self.add_buttons[n].grid(column=n, row=0, sticky=(E))

    def add_name(self):
        global module_logger

        name_list = self.db.get_all_names()
        selectone = plorn.attr.PlornSelectAttr('Name', table_name='names',
                                               attr_list=name_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        name = self.db.get_name(entry['id'])
        self.new_album.add_name_to_list(name)
        self.rframe.set_name_listbox_values(self.new_album.get_name_list())
        module_logger.debug('add name, selected: ' + str(name))

    def remove_name(self):
        global module_logger

        name = self.rframe.get_name_listbox_value()
        module_logger.debug(f'remove_name: {str(name)}')
        if name == None:
            messagebox.showinfo(parent=self,
                                title='Remove Name from Album',
                                message='No name selected',
                                detail='Please select a name to remove',
                               )
        else:
            self.new_album.remove_name_from_list(name)
            self.rframe.set_name_listbox_values(self.new_album.get_name_list())

    def add_place(self):
        global module_logger

        place_list = self.db.get_all_places()
        selectone = plorn.attr.PlornSelectAttr('Place', table_name='places',
                                               attr_list=place_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        place = self.db.get_place(entry['id'])
        self.new_album.add_place_to_list(place)
        self.rframe.set_place_listbox_values(self.new_album.get_place_list())
        module_logger.debug('add place, selected: ' + str(place))

    def remove_place(self):
        global module_logger

        place = self.rframe.get_place_listbox_value()
        module_logger.debug(f'remove_place: {str(place)}')
        if place == None:
            messagebox.showinfo(parent=self,
                                title='Remove Place from Album',
                                message='No place selected',
                                detail='Please select a place to remove',
                               )
        else:
            self.new_album.remove_place_from_list(place)
            self.rframe.set_place_listbox_values(self.new_album.get_place_list())

    def add_tag(self):
        global module_logger

        tag_list = self.db.get_all_tags()
        selectone = plorn.attr.PlornSelectAttr('Tag', table_name='tags',
                                               attr_list=tag_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        tag = self.db.get_tag(entry['id'])
        self.new_album.add_tag_to_list(tag)
        self.rframe.set_tag_listbox_values(self.new_album.get_tag_list())
        module_logger.debug('add tag, selected: ' + str(tag))

    def remove_tag(self):
        global module_logger

        tag = self.rframe.get_tag_listbox_value()
        module_logger.debug(f'remove_tag: {str(tag)}')
        if tag == None:
            messagebox.showinfo(parent=self,
                                title='Remove Tag from Album',
                                message='No tag selected',
                                detail='Please select a tag to remove',
                               )
        else:
            self.new_album.remove_tag_from_list(place)
            self.rframe.set_tag_listbox_values(self.new_album.get_tag_list())

    def add_album(self):
        module_logger.debug('entered add_album')
        self.name = self.lframe.get_album_name()
        if self.name == '':
            messagebox.showerror(parent=self,
                                 title='Adding an Album',
                                 message='Album must have non-blank name',
                                 detail='Please provide a name',
                                )
            return

        module_logger.debug(f'add album name: {self.name}')
        self.new_album.set_name(self.name)
        self.new_album.set_dated(self.lframe.get_dated())
        self.new_album.set_notes(self.lframe.get_notes())
        self.new_album.set_photo_count(self.lframe.get_photo_count())
        self.new_album.set_name_list(self.rframe.get_listbox_names())
        self.new_album.set_place_list(self.rframe.get_listbox_places())
        self.new_album.set_tag_list(self.rframe.get_listbox_tags())

        if self.db.album_exists(self.new_album):
            messagebox.showerror(parent=self,
                                 title='Adding an Album',
                                 message='Album already exists',
                                 detail='Please use another name',
                                )
        else:
            # now it's reasonable to add the album ....
            self.new_album = self.db.add_album(self.new_album)
            msg = f'Added Album \'{self.new_album.get_name()}\''
            messagebox.showinfo(message=msg, parent=self)

    def clear_entries(self):
        self.name = ''
        self.album_name.set(self.name)
        self.dated.set('')
        self.notes.delete('1.0', END)
        self.photo_count = 0
        self.photo_list.clear()

    def get_new_album(self):
        return self.new_album


class PlornShowAlbum(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornShowAlbum')
        self.tfont = font.nametofont('TkDefaultFont')
        self.db = plorn.db.open()
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

        self.lframe = PlornAlbumLeftFrame(self.db, self, album=self.album,
                                          default_state='readonly')
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn.common.PlornAttrFrame(self.db, self,
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
        self.db = plorn.db.open()
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

        self.lframe = PlornAlbumLeftFrame(self.db, self, album=self.album,
                                          default_state='readonly')
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn.common.PlornAttrFrame(self.db, self,
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

        self.do_remove = ttk.Button(self, text='Remove',
                                    command=self.confirm_remove)
        self.do_remove.grid(column=0, row=3, sticky=(E))
        self.cancel = ttk.Button(self, text='Cancel',
                                 command=self.destroy)
        self.cancel.grid(column=1, row=3, sticky=(W))

    def confirm_remove(self):
        album_name = self.lframe.get_album_name()
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
        self.db = plorn.db.open()
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

        self.lframe = PlornAlbumLeftFrame(self.db, self, album=self.album,
                                          default_state='normal')
        self.lframe.get_photos_field().configure(state='readonly')
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn.common.PlornAttrFrame(self.db, self,
                base_obj=self.album,
                get_name_list=self.db.get_names_for_album,
                get_place_list=self.db.get_places_for_album,
                get_tag_list=self.db.get_tags_for_album,
                edit_lists=True,
        )
        self.rframe.get_frame().grid(column=1, row=0, sticky=(N,W,E,S))
        self.rframe.set_name_commands(self.add_name, self.remove_name)
        self.rframe.set_place_commands(self.add_place, self.remove_place)
        self.rframe.set_tag_commands(self.add_tag, self.remove_tag)

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
        global module_logger

        name_list = self.db.get_all_names()
        selectone = plorn.attr.PlornSelectAttr('Name', table_name='names',
                                               attr_list=name_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        name = self.db.get_name(entry['id'])
        self.album.add_name_to_list(name)
        self.rframe.set_name_listbox_values(self.album.get_name_list())
        module_logger.debug('add name, selected: ' + str(name))

    def remove_name(self):
        global module_logger

        name = self.rframe.get_name_listbox_value()
        module_logger.debug(f'remove_name: {str(name)}')
        if name == None:
            messagebox.showinfo(parent=self,
                                title='Remove Name from Album',
                                message='No name selected',
                                detail='Please select a name to remove',
                               )
        else:
            self.album.remove_name_from_list(name)
            self.rframe.set_name_listbox_values(self.album.get_name_list())

    def add_place(self):
        global module_logger

        place_list = self.db.get_all_places()
        selectone = plorn.attr.PlornSelectAttr('Place', table_name='places',
                                               attr_list=place_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        place = self.db.get_place(entry['id'])
        self.album.add_place_to_list(place)
        self.rframe.set_place_listbox_values(self.album.get_place_list())
        module_logger.debug('add place, selected: ' + str(place))

    def remove_place(self):
        global module_logger

        place = self.rframe.get_place_listbox_value()
        module_logger.debug(f'remove_place: {str(place)}')
        if place == None:
            messagebox.showinfo(parent=self,
                                title='Remove Place from Album',
                                message='No place selected',
                                detail='Please select a place to remove',
                               )
        else:
            self.album.remove_place_from_list(place)
            self.rframe.set_place_listbox_values(self.album.get_place_list())

    def add_tag(self):
        global module_logger

        tag_list = self.db.get_all_tags()
        selectone = plorn.attr.PlornSelectAttr('Tag', table_name='tags',
                                               attr_list=tag_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        tag = self.db.get_tag(entry['id'])
        self.album.add_tag_to_list(tag)
        self.rframe.set_tag_listbox_values(self.album.get_tag_list())
        module_logger.debug('add tag, selected: ' + str(tag))

    def remove_tag(self):
        global module_logger

        tag = self.rframe.get_tag_listbox_value()
        module_logger.debug(f'remove_tag: {str(tag)}')
        if tag == None:
            messagebox.showinfo(parent=self,
                                title='Remove Tag from Album',
                                message='No tag selected',
                                detail='Please select a tag to remove',
                               )
        else:
            self.album.remove_tag_from_list(tag)
            self.rframe.set_tag_listbox_values(self.album.get_tag_list())

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
        if self.lframe.get_album_name() != self.album.get_name():
            if self.db.album_exists(self.lframe.get_album_name()):
                messagebox.showerror(parent=self,
                                     title='Updating an Album',
                                     message='Album already exists',
                                     detail='Please use another name',
                                    )
                return

        album_copy.set_name(self.lframe.get_album_name())
        album_copy.set_dated(self.lframe.get_dated())
        album_copy.set_notes(self.lframe.get_notes())
        album_copy.set_photo_count(self.lframe.get_photo_count())
        album_copy.set_name_list(self.rframe.get_listbox_names())
        album_copy.set_place_list(self.rframe.get_listbox_places())
        album_copy.set_tag_list(self.rframe.get_listbox_tags())

        self.album = self.db.update_album(self.album, album_copy)

        aname = self.lframe.get_album_name()
        self.destroy()

    def get_updated_album(self):
        return self.album


class PlornImportToAlbum:
    def __init__(self, parent, album_id):
        module_logger.debug('started PlornImportAlbum')
        self.parent = parent
        self.album_id = album_id
        self.added_count = 0
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn.db.open()
        self.album = self.db.get_album(self.album_id)

        image_list = self.collect_images()
        for path in image_list:
            name = os.path.basename(path)
            dated, notes = self.get_metadata(path)
            tmp = plorn.photo.PlornPhoto(name, id=None, album_id=album_id,
                                         path=path, dated=dated, notes=notes,
                                        )
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

    def get_metadata(self, path):
        '''
        Get EXIF metadata from the image if we can
        '''

        def format_dms(degrees, minutes, seconds, direction):
            degree_symbol = u'\N{DEGREE SIGN}'
            value  = float(degrees)
            value += float(float(minutes) / 60.0)
            value += float(float(seconds) / 3600.0)
            return f'{value:.6}{degree_symbol} {direction}'

        exif_data = {}
        try:
            with pilImage.open(path) as img:
                info = img._getexif()
                for tag, value in info.items():
                    decoded_tag = pilTAGS.get(tag, tag)
                    if decoded_tag == 'DateTime':
                        exif_data[decoded_tag] = value
                    elif decoded_tag == 'OffsetTime':
                        exif_data[decoded_tag] = value
                    elif decoded_tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag in value:
                            sub_decoded_tag = pilGPSTAGS.get(gps_tag, gps_tag)
                            gps_data[sub_decoded_tag] = value[gps_tag]
                        exif_data[decoded_tag] = gps_data
                    else:
                        continue
            img.close()
        except (IOError, AttributeError, KeyError, IndexError):
            pass

        result = ''
        dated = ''
        if 'DateTime' in exif_data:
            dt = exif_data['DateTime'].split()
            date = dt[0].replace(':', '-')
            tm = dt[1]
            dated = f'{date}  {tm}'
            msg = f'Date and Time: {date}  {tm}'
            if 'OffsetTime' in exif_data:
                msg += f'{exif_data["OffsetTime"]}'
            result += msg

        if 'GPSInfo' in exif_data:
            loc = exif_data['GPSInfo']
            if len(loc) > 0:
                lat_deg = None
                lat_min = None
                lat_sec = None
                long_deg = None
                long_min = None
                long_sec = None
                if 'GPSLatitude' in loc:
                    lat_deg, lat_min, lat_sec = loc['GPSLatitude']
                    lat_dir = loc['GPSLatitudeRef']
                if 'GPSLongitude' in loc:
                    long_deg, long_min, long_sec = loc['GPSLongitude']
                    long_dir = loc['GPSLongitudeRef']
                if (lat_deg and lat_min and lat_sec) and \
                   (long_deg and long_min and long_sec):
                    lat = format_dms(lat_deg, lat_min, lat_sec, lat_dir)
                    long = format_dms(long_deg, long_min, long_sec, long_dir)
                    result += f'\nLatitude, Longitude: {lat}, {long}'

        return dated, result

