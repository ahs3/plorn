#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import filetype
import logging
import os
import re
import shutil
import sys
import time
from PIL import Image as pilImage
from PIL import ImageTk

from tkinter import font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.tableview import Tableview, TableRow
from ttkbootstrap.dialogs.message import Messagebox

import plorn.album
import plorn.attr
import plorn.common
from plorn.common import SearchDomains, SearchDomainStrings
from plorn.common import SearchFields, SearchFieldStrings
from plorn.common import AlbumSearchInfo, PhotoSearchInfo
from plorn.config import get_config
import plorn.db
import plorn.photo
import plorn.search
from plorn.widgets import *


#-- set up logging
root_logger = logging.getLogger('')
root_logger.setLevel(logging.INFO)
fh = logging.FileHandler('plorn.log')
fh.setLevel(logging.DEBUG)
fhformat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fhformat)
fh.setFormatter(formatter)
root_logger.addHandler(fh)

module_logger = logging.getLogger('plorn.gui')
module_logger.setLevel(logging.INFO)

root_window = None

#-- the application
class Plorn(ttk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geometry('1280x1024')
        self.title('plorn')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        #-- get the config file
        config_name = None
        if len(sys.argv) > 1:
            config_name = sys.argv[1]
        self.config = get_config(config_name)
        self.db = plorn.db.open(self.config.get_dbname())
        self.style.theme_use(self.config.get_theme())
        self.font = font.nametofont('TkDefaultFont')
        self.font.configure(size=self.config.get_fontsize())
        self.option_add('*TCombobox*Listbox.font', self.font)
        self.option_add('*TEntry.font', self.font)

        #-- create the main app frame
        self.mainframe = ttk.Frame(self, padding='10 10 10 10')
        self.mainframe['borderwidth'] = 5
        self.mainframe['relief'] = 'groove'
        self.mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.rowconfigure(1, weight=40)
        self.mainframe.rowconfigure(2, weight=1)
        self.static_widgets = {}

        #-- add in title info
        self.header = self.setup_header(self.mainframe)
        self.header.grid(column=0, row=0, sticky=(N,E,S,W))

        #-- footer information that changes over time
        self.album_count_str = StringVar()
        self.album_count_label = None
        self.photo_count_str = StringVar()
        self.photo_count_label = None

        #-- create these as placeholders
        self.albums_tab = 0
        self.aview = None
        self.album_name_list = []
        self.album_count = 0
        self.current_album = None
        self.current_album_name = StringVar()
        self.album_label = StringVar()
        self.album_coldata = []
        self.album_rowdata = []

        self.photos_tab = 1
        self.pview = None
        self.current_photo = None
        self.current_photo_name = StringVar()
        self.current_photo_button = None
        self.album_selector = None
        self.album_selector_cbox = None
        self.album_selector_label = None
        self.selected_album = StringVar()
        self.photo_coldata = []
        self.photo_rowdata = []
        self.thumbnails = {}
        self.plorn_thumbnail = None
        img = pilImage.open(plorn.config.plorn_photo_path())
        img.thumbnail((125,125), pilImage.Resampling.LANCZOS)
        self.plorn_thumbnail = ImageTk.PhotoImage(image=img)

        self.names_tab  = 2
        self.nview = None
        self.name_list = []
        self.last_name_id = None
        self.name_open = False

        self.places_tab = 3
        self.place_tree = None
        self.place_list = []
        self.last_place_id = None
        self.place_open = False

        self.tags_tab = 4
        self.tag_tree = None
        self.tag_list = []
        self.last_tag_id = None
        self.tag_open = False

        self.search_tab = 5
        self.s_domain_box = None
        self.s_domain = StringVar()
        self.s_field_choice = None
        self.s_field = StringVar()
        self.s_regex_box = None
        self.s_regex = StringVar()
        self.s_regex.set('.*')

        self.settings_tab = 6
        self.rebuild_progress = None        # progress bar place holder

        #-- create tabbed pane windows for albums, photos, names, places,
        #   and so on
        self.notebook = self.setup_notebook()
        self.notebook.grid(column=0, row=1, sticky=(N, W, E, S))
        self.current_tab = self.notebook.index('current')

        #-- add in footer info, including an exit button
        self.footer = self.setup_footer(self.mainframe)
        self.footer.grid(column=0, row=2, sticky=(N,E,S,W))

    def setup_header(self, parent):
        #-- header for the application
        header = ttk.Frame(parent, padding='10 10 10 10')
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=8)
        header.columnconfigure(2, weight=1)
        header.rowconfigure(0, weight=4)
        header.rowconfigure(1, weight=1)
        header.rowconfigure(2, weight=1)

        label_text = 'plorn: photo catalog'
        lheader = make_header_label(header, width=30, text=f'{label_text:<30}',
                                    size=self.config.get_fontsize())
        lheader.grid(column=0, row=0, sticky=(W))
        self.static_widgets['header.left'] = lheader

        mheader = ttk.Label(header, width=30, text=' ', state='hidden')
        mheader.grid(column=1, row=0)
        self.static_widgets['header.middle'] = mheader

        msg = f'version {self.config.get_version()}'
        value = f'{msg: >50}'
        rheader = make_header_label(header, width=30, text=value,
                                    size=self.config.get_fontsize())
        rheader.grid(column=2, row=0, sticky=(E))
        self.static_widgets['header.right'] = rheader

        sep1 = ttk.Separator(header, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=3, sticky=(W+E))
        self.static_widgets['header.sep1'] = rheader
        sep2 = ttk.Separator(header, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=3, sticky=(W+E))
        self.static_widgets['header.sep2'] = rheader

        return header

    def setup_notebook(self):
        #-- build up a tabbed notebook
        notebook = ttk.Notebook(self.mainframe)
        notebook.columnconfigure(0, weight=1)
        notebook.rowconfigure(0, weight=1)

        #   ... that has an album list
        self.album_frame = ttk.Frame(notebook, padding='5 5 5 5')
        self.album_frame['borderwidth'] = 2
        self.album_frame['relief'] = 'groove'
        self.album_buttons = []
        self.build_album_view(self.album_frame)
        notebook.add(self.album_frame, text=' Albums ', sticky='nwes')
        self.albums_tab = 0

        #   ... and that has a photo list for the current album
        self.photo_frame = ttk.Frame(notebook, padding='5 5 5 5')
        self.photo_frame['borderwidth'] = 2
        self.photo_frame['relief'] = 'groove'
        self.photo_buttons = []
        self.build_photo_view(self.photo_frame)
        notebook.add(self.photo_frame, text=' Photos ', sticky='nwes')
        self.photos_tab = 1

        #   ... and there are all sorts of names to choose from
        self.names = ttk.Frame(notebook, padding='5 5 5 5')
        self.names['borderwidth'] = 2
        self.names['relief'] = 'groove'
        self.names.columnconfigure(0, weight=1)
        self.names.rowconfigure(0, weight=1)
        self.build_name_list(self.names)
        notebook.add(self.names, text=' Names ')
        self.names_tab = 2

        #   ... and there are all sorts of places to choose from
        self.places = ttk.Frame(notebook, padding='5 5 5 5')
        self.places['borderwidth'] = 2
        self.places['relief'] = 'groove'
        self.places.columnconfigure(0, weight=1)
        self.places.rowconfigure(0, weight=1)
        self.build_place_list(self.places)
        notebook.add(self.places, text=' Places ')
        self.places_tab = 3

        #   ... and there are all sorts of tags to choose from
        self.tags = ttk.Frame(notebook, padding='5 5 5 5')
        self.tags['borderwidth'] = 2
        self.tags['relief'] = 'groove'
        self.tags.columnconfigure(0, weight=1)
        self.tags.rowconfigure(0, weight=1)
        self.build_tag_list(self.tags)
        notebook.add(self.tags, text=' Tags ')
        self.tags_tab = 4

        #   ... and has a way to search for pictures and albums
        self.search = ttk.Frame(notebook, padding='5 5 5 5')
        self.search['borderwidth'] = 2
        self.search['relief'] = 'groove'
        self.search.columnconfigure(0, weight=1)
        self.search.rowconfigure(0, weight=1)
        self.build_search_options(self.search)
        notebook.add(self.search, text=' Search ')
        self.search_tab = 5

        #   ... and that has a config table for the application
        self.settings = ttk.Frame(notebook, padding='5 5 5 5')
        self.settings['borderwidth'] = 2
        self.settings['relief'] = 'groove'
        self.settings.columnconfigure(0, weight=1)
        self.settings.columnconfigure(1, weight=2)
        self.build_settings_view(self.settings)
        notebook.add(self.settings, text=' Settings ')
        self.settings_tab = 6

        notebook.bind('<<NotebookTabChanged>>', self.tab_changed)
        return notebook

    def tab_changed(self, e):
        global module_logger

        current = self.notebook.index('current')
        if current == self.photos_tab:
            module_logger.debug(f'tab_changed: {current}')
            self.reset_album_selector()

    def setup_footer(self, parent):
        #-- footer for the main app
        footer = ttk.Frame(parent, padding='10 10 10 10')
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=4)
        footer.columnconfigure(2, weight=1)
        footer.rowconfigure(0, weight=4)
        footer.rowconfigure(1, weight=1)
        footer.rowconfigure(2, weight=1)
        footer.rowconfigure(3, weight=4)

        #-- and some counts of albums and photos ....
        sep3 = ttk.Separator(footer, orient=HORIZONTAL)
        sep3.grid(column=0, row=0, columnspan=3, sticky=(W+E))
        self.static_widgets['footer.sep3'] = sep3
        self.album_count_label = ttk.Label(footer, width=16,
                                      textvariable=self.album_count_str)
        self.album_count_label.grid(column=0, row=1, sticky=(W))
        self.photo_count_label = ttk.Label(footer, width=16,
                                      textvariable=self.photo_count_str)
        self.photo_count_label.grid(column=1, row=1, sticky=(W))
        self.update_counts()

        #-- and an exit button ....
        sep4 = ttk.Separator(footer, orient=HORIZONTAL)
        sep4.grid(column=0, row=2, columnspan=3, sticky=(W+E))
        self.static_widgets['footer.sep4'] = sep4

        b = make_button(footer, text='Quit', command=self.destroy)
        b.grid(column=2, row=3, padx=10, pady=10)
        self.static_widgets['footer.exit_button'] = b

        return footer

    def build_album_view(self, parent):
        global module_logger

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        lframe = ttk.Frame(parent, padding=(5, 5, 5, 5))
        lframe.columnconfigure(0, weight=1)
        lframe.rowconfigure(0, weight=1)
        lframe.grid(column=0, row=0, sticky=(N,W,E,S))
        self.static_widgets['album.lframe'] = lframe

        rframe = ttk.Frame(parent, padding=(5, 5, 5, 5))
        rframe.columnconfigure(0, weight=1)
        rframe.grid(column=1, row=0, sticky=(N,W,E,S))
        self.static_widgets['album.rframe'] = rframe

        def album_selected(rows):
            if len(rows) > 0:
                album_id, photo_count, album_name = rows[0].values
                self.current_album = album_id
                self.current_album_name.set(album_name)
                module_logger.debug(f'album_selected: {self.current_album} [{album_id}]')
                module_logger.debug(f'album_selected: {self.current_album_name.get()} [{album_name}]')

        self.album_coldata = [
            {'text': 'ID', 'stretch': False, 'width': 120,},
            {'text': 'Photos', 'stretch': False},
            {'text': 'Name', 'stretch': True},
        ]
        self.album_rowdata = self.get_all_album_data()
        if len(self.album_rowdata) > 0:
            iid, count, name = self.album_rowdata[0]
            self.current_album = iid
            self.current_album_name.set(name)
        aview = Tableview(master=lframe,
                          coldata=self.album_coldata, 
                          rowdata=self.album_rowdata,
                          paginated=True,
                          searchable=True, bootstyle=PRIMARY,
                          autofit=True,
                          pagesize=20,
                          iid_field=0,      # first col as iid
                          on_select=album_selected,
                          disable_right_click=True,
                         )
        aview.align_heading_center(cid=0)
        aview.align_heading_center(cid=1)
        aview.align_column_center(cid=0)
        aview.align_column_center(cid=1)
        aview.align_column_left(cid=2)
        aview.grid(column=0, row=0, sticky=(N,W,E,S))
        aview.focus()
        self.aview = aview

        button_info = [
            (0, 'info',   self.album_info),
            (1, 'add',    self.add_album),
            (2, 'remove', self.remove_album),
            (3, 'edit',   self.edit_album),
            (4, 'import', self.import_photos),
        ]
        self.album_buttons = []
        for row, txt, cmd in button_info:
            rframe.rowconfigure(row, weight=1)
            b = make_button(rframe, text=txt, command=cmd)
            b.grid(column=0, row=row, pady=10)
            self.album_buttons.append(b)

    def update_counts(self):
        self.album_count_str.set(f'Albums: {self.db.album_count()}')
        self.photo_count_str.set(f'Photos: {self.db.photo_count()}')

    def get_all_album_data(self):
        global module_logger

        cursor = self.db.get_album_cursor()
        data = []
        for ii in cursor:
            data.append((f'{ii['id']:04}', ii['photo_count'], ii['name']))
        rows = sorted(data, key=lambda x: x[0])
        module_logger.debug(f'get all albums: {str(rows)}')
        return rows

    def add_album(self):
        global module_logger

        module_logger.debug('adding album')
        addone = plorn.album.PlornAddAlbum(self)
        addone.grab_set()
        self.wait_window(addone)
        album = addone.get_new_album()
        
        if album != None and album.get_id() != None:
            self.current_album = album.get_id()
            self.current_album_name.set(album.get_name())
            self.aview.insert_row(self.current_album,
                                  (f'{self.current_album:04}',
                                   album.get_photo_count(),
                                   self.current_album_name.get()))
            self.update_counts()
            album_names = self.get_album_view_names()
            self.album_selector['values'] = album_names

    def remove_album(self):
        if self.current_album:
            rmone = plorn.album.PlornRemoveAlbum(self, self.current_album)
            rmone.grab_set()
            self.wait_window(rmone)
            self.aview.delete_row(iid=f'{self.current_album:04}')
            self.update_counts()
            album_names = self.get_album_view_names()
            self.album_selector['values'] = album_names
        else:
            Messagebox.show_error('Please select an album to remove',
                                  parent=self, title='Select an Album')

    def album_info(self):
        global module_logger

        if self.current_album:
            module_logger.debug(f'show info for {self.current_album_name.get()}')
            showone = plorn.album.PlornShowAlbum(self, self.current_album)
            showone.grab_set()
            self.wait_window(showone)
        else:
            Messagebox.show_error('Please select an album to show',
                                  parent=self, title='Select an Album')

    def import_photos(self):
        global module_logger

        if self.current_album:
            module_logger.debug(f'show info for {self.current_album_name.get()}')
            added = plorn.album.PlornImportToAlbum(self, self.current_album)    
            count = added.get_photo_count()
            album_row = self.db.get_album_row_by_id(self.current_album)
            module_logger.debug(f'import_photos updated: {album_row}')
            album_id = album_row['id']
            name = album_row['name']
            total = album_row['photo_count']
            suffix=''
            if count != 1:
                suffix = 's'
            detail  = f'Added {count} photo{suffix} to album \"{name}\"'
            Messagebox.show_info(detail,
                                 parent=self, title='Import Photos to Album')
            trow = self.aview.iidmap[f'{album_id:04}']
            trow.values = [f'{album_id:04}', total, name]
            trow.refresh()
            self.update_counts()
        else:
            Messagebox.show_error('Please select an album to import into',
                                  parent=self, title='Select an Album')

    def edit_album(self):
        global module_logger

        if self.current_album:
            module_logger.debug(f'edit album {self.current_album_name.get()}')
            showone = plorn.album.PlornEditAlbum(self, self.current_album)
            showone.grab_set()
            self.wait_window(showone)
            album_names = self.get_album_view_names()
            self.album_selector['values'] = album_names
        else:
            Messagebox.show_error('Please select an album to edit',
                                  parent=self, title='Select an Album')


    def get_album_view_names(self):
        all_names = []
        for ii in self.aview.get_rows(visible=True):
            iid, pcount, name = ii.values
            all_names.append(name)
        return all_names

    def get_all_photo_data(self):
        global module_logger

        cursor = self.db.get_photo_cursor(album_id=self.current_album)
        data = []
        thumbnails = {}
        for ii in cursor:
            data.append((f'{ii['id']:04}', ii['name'], ii['path']))
            fullpath = os.path.expandvars(os.path.expanduser(ii['path']))
            with pilImage.open(fullpath) as img:
                img.thumbnail((125,125), pilImage.Resampling.LANCZOS)
                thumb = ImageTk.PhotoImage(image=img)
                thumbnails[int(ii['id'])] = thumb
        rows = sorted(data, key=lambda x: x[0])
        module_logger.debug(f'get all photos: {str(rows)}')
        return rows, thumbnails

    def change_albums(self, e):
        album_name = self.album_selector_cbox.get()
        self.current_album_name.set(album_name)
        album_names = self.get_album_view_names()
        current = album_names.index(self.current_album_name.get())
        self.album_selector_cbox.current(current)

        for iid, count, name in self.album_rowdata:
            if name == album_name:
                module_logger.debug(f'build_album_selector: found {name}')
                self.current_album = iid
                self.current_album_name.set(name)
                break
        self.pview.delete_rows()
        self.thumbnails.clear()
        self.photo_rowdata, self.thumbnails = self.get_all_photo_data()
        if len(self.photo_rowdata) > 0:
            self.pview.insert_rows(0, self.photo_rowdata)
            iid, pname, ppath = self.photo_rowdata[0]
            self.current_photo = iid
            self.current_photo_name.set(pname)
            self.current_photo_button.config(image=self.thumbnails[int(iid)])
            self.pview._select_first_visible_item()
        else:
            self.current_photo_button.config(image=self.plorn_thumbnail)
            self.pview._select_first_visible_item()

    def build_album_selector(self, parent):
        global module_logger

        aframe = ttk.Frame(parent, padding=(5,5,5,5))
        aframe.columnconfigure(0, weight=1)
        aframe.columnconfigure(1, weight=5)
        aframe.rowconfigure(0, weight=1)
        self.album_selector = aframe

        module_logger.debug(f'build_album_selector: {self.current_album}, {self.current_album_name.get()}')
        albuml = ttk.Label(aframe, text='Album:')
        albuml.grid(column=0, row=0, pady=5)
        current_album = ttk.Label(master=aframe,
                                  text=self.current_album_name.get(),
                                  font=self.font,
                                  width=40)
        current_album.grid(column=1, row=0, pady=5)
        if self.current_album_name.get() != '':
            self.album_selector_label = current_album
            album_names = self.get_album_view_names()
        else:
            album_names = []

        albumcb = ttk.Combobox(master=current_album,
                               values=album_names,
                               font=self.font,
                               width=40)
        albumcb.grid(column=1, row=0, pady=5)
        if self.current_album != None:
            albumcb.current(album_names.index(self.current_album_name.get()))
        albumcb.bind("<<ComboboxSelected>>", self.change_albums)
        self.album_selector_cbox = albumcb

    def reset_album_selector(self):
        global module_logger

        album_names = self.get_album_view_names()
        module_logger.debug(f'reset_album_selector names: {str(album_names)}')
        module_logger.debug(f'reset_album_selector current: {self.current_album_name.get()}')
        self.album_selector_label.config(text=self.current_album_name.get())
        self.album_selector_cbox.config(values=album_names)
        self.album_selector_cbox.set(self.current_album_name.get())
        self.change_albums(None)

    def build_photo_view(self, parent):
        global module_logger

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=4)
        parent.rowconfigure(2, weight=1)

        self.build_album_selector(parent)
        self.album_selector.grid(column=0, row=0, columnspan=2,
                                 sticky=(N,W,E,S))
        self.selected_album.set(self.current_album_name.get())
        module_logger.debug(f'build photo album "{self.selected_album.get()}"')
        self.static_widgets['photo.sframe'] = self.album_selector

        tframe = ttk.Frame(parent, padding=(5,5,5,5))
        tframe.columnconfigure(0, weight=4)
        tframe.columnconfigure(0, weight=1)
        tframe.rowconfigure(0, weight=1)
        tframe.grid(column=0, row=1, sticky=(N,W,E,S))
        self.static_widgets['photo.tframe'] = tframe

        lframe = ttk.Frame(tframe, padding=(5,5,5,5))
        lframe.columnconfigure(0, weight=1)
        lframe.rowconfigure(0, weight=1)
        lframe.grid(column=0, row=0, sticky=(N,W,E,S))
        self.static_widgets['photo.lframe'] = lframe

        rframe = ttk.Frame(tframe, padding=(5, 5, 5, 5))
        rframe.columnconfigure(0, weight=1)
        rframe.rowconfigure(0, weight=1)
        rframe.grid(column=1, row=0, sticky=(N,W,E,S))
        self.static_widgets['photo.rframe'] = rframe

        self.photo_coldata = [
            {'text': 'ID', 'stretch': False, 'width': 120,},
            {'text': 'Name', 'stretch': True, 'width': 400},
            {'text': 'Path', 'stretch': True, 'width': 400},
        ]
        self.photo_rowdata, self.thumbnails = self.get_all_photo_data()
        thumbnail = None
        bname = 'Plorn'
        if len(self.photo_rowdata) > 0:
            iid, pname, ppath = self.photo_rowdata[0]
            bname = os.path.basename(ppath)
            self.current_photo = iid
            self.current_photo_name.set(pname)
            thumbnail = self.thumbnails[int(iid)]
        else:
            img = pilImage.open(plorn.config.plorn_photo_path())
            img.thumbnail((125,125), pilImage.Resampling.LANCZOS)
            thumbnail = ImageTk.PhotoImage(image=img)
        self.current_photo_button = make_button(rframe,
                                        state='readonly',
                                        compound='image',
                                        image=thumbnail,
                                        text=bname)
        self.current_photo_button.grid(column=0, row=0)

        def photo_selected(rows):
            if len(rows) > 0:
                iid, pname, ppath = rows[0].values
                self.current_photo = iid
                self.current_photo_name.set(pname)
                self.current_photo_button.configure(image=self.thumbnails[int(iid)])

        pview = Tableview(master=lframe,
                          coldata=self.photo_coldata, 
                          rowdata=self.photo_rowdata,
                          paginated=True,
                          searchable=True, bootstyle=PRIMARY,
                          autofit=True,
                          pagesize=20,
                          iid_field=0,      # first col as iid
                          on_select=photo_selected,
                          disable_right_click=True,
                         )
        pview.align_heading_center(cid=0)
        pview.align_heading_left(cid=1)
        pview.align_heading_left(cid=2)
        pview.align_column_center(cid=0)
        pview.align_column_left(cid=1)
        pview.align_column_left(cid=2)
        pview.grid(column=0, row=0, sticky=(N,W,E,S))
        pview._select_first_visible_item()
        self.pview = pview

        self.photo_buttons = [
            make_button(rframe, text='info', command=self.photo_info),
            make_button(rframe, text='add photo', command=self.add_photo),
            make_button(rframe, text='remove', command=self.remove_photo),
            make_button(rframe, text='edit', command=self.edit_photo),
        ]
        for n in range(0, len(self.photo_buttons)):
            rframe.rowconfigure(n+1, weight=1)
            self.photo_buttons[n].grid(column=0, row=n+1, pady=10)

    def photo_info(self):
        global module_logger

        if self.current_photo:
            showone = plorn.photo.PlornShowPhoto(self, self.current_photo)
            showone.grab_set()
            self.wait_window(showone)
        else:
            Messagebox.show_error('Please select a photo to show',
                                  parent=self, title='Select a Photo')

    def remove_photo(self):
        global module_logger

        if self.current_photo:
            photo = self.db.get_photo(self.current_photo)
            module_logger.debug(f'remove_photo: id {photo.get_id()}')
            rmone = plorn.photo.PlornRemovePhoto(self, self.current_photo)
            rmone.grab_set()
            self.wait_window(rmone)
            if rmone.was_removed():
                self.pview.delete_row(iid=f'{self.current_photo:04}')
                self.update_counts()
        else:
            Messagebox.show_error('Please select a photo to remove',
                                  parent=self, title='Select a Photo')

    def edit_photo(self):
        if self.current_photo:
            rmone = plorn.photo.PlornEditPhoto(self, self.current_photo)
            rmone.grab_set()
            self.wait_window(rmone)
            self.update_photoview(photo.get_album_id())
        else:
            Messagebox.show_error('Please select a photo to edit',
                                  parent=self, title='Select a Photo')

    def add_photo(self):
        global module_logger

        module_logger.debug('adding photo')
        album_id = self.current_album
        addone = plorn.photo.PlornAddPhoto(self, album_id)
        addone.grab_set()
        self.wait_window(addone)
        photo = addone.get_new_photo()
        
        if photo != None and photo.get_id() != None:
            self.photo_rowdata.clear()
            self.thumbnails.clear()
            self.photo_rowdata, self.thumbnails = self.get_all_photo_data()
            self.pview.insert_row(self.current_photo,
                                  (f'{self.current_photo:04}',
                                   self.current_photo_name.get(),
                                   photo.get_path()))
            self.update_counts()

    def build_name_list(self, parent):
        self.name_tree = plorn.attr.PlornAttrTreeview(parent, heading='Name')
        self.name_tree.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        bframe = ttk.Frame(parent, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=1)
        self.name_buttons = [
            make_button(bframe, text='expand', command=self.toggle_names),
            make_button(bframe, text='add', command=self.add_name),
            make_button(bframe, text='remove', command=self.remove_name),
            make_button(bframe, text='edit', command=self.edit_name),
        ]
        for n in range(0, len(self.name_buttons)):
            bframe.rowconfigure(n+1, weight=1)
            self.name_buttons[n].grid(column=0, row=n+1, pady=10)
        bframe.grid(column=1, row=0, sticky=(N,S))

        self.update_nameview()

    def update_nameview(self):
        self.name_list.clear()
        self.name_list = self.db.get_all_names()
        self.name_tree.update_treeview(self.name_list)

    def toggle_names(self):
        self.name_open = not self.name_tree.get_toggle()
        if self.name_open:
            self.name_buttons[0].configure(text="collapse")
        else:
            self.name_buttons[0].configure(text="expand")
        self.name_tree.toggle_treeview(self.name_open)

    def add_name(self):
        global module_logger

        module_logger.debug(f'adding name')
        parent = self.name_tree.focus()
        if parent == '':
            pid = 0
        else:
            entry = self.name_tree.item(parent)
            pid = entry['values'][0]
        addone = plorn.attr.PlornAddAttr(self, parent_id=pid,
                                         attr_name='Name',
                                         table_name='names')
        addone.grab_set()
        self.wait_window(addone)
        attr = addone.get_new_attr()
        
        if attr and attr['id'] != None:
            name = plorn.attr.PlornName(attr['value'], id=attr['id'],
                                          parent_id=attr['parent_id'])
            module_logger.debug(f'add name {name.get_value()}')
            self.update_nameview()

    def remove_name(self):
        global module_logger

        entry_id = self.name_tree.focus()
        if entry_id == '':
            Messagebox.show_error('Please select a name to remove',
                                  parent=self, title='Remove Name')
            return
        entry = self.name_tree.item(entry_id)
        module_logger.debug(f'entry: {str(entry)}')
        name = plorn.attr.PlornName(entry['text'],
                                      id=entry['values'][0],
                                      parent_id=entry['values'][1])
        
        kids = self.db.get_name_children(name)
        if len(kids) > 0:
            msg = 'Cannot remove a name that still contains other names'
            Messagebox.show_error(msg, parent=self, title='Remove Name')
            return

        name = self.db.get_name(entry['values'][0])
        parent_id = name.get_parent_id()
        module_logger.debug(f'removing name {name.get_value()} from {parent_id}')
        rmone = plorn.attr.PlornRemoveAttr(self, name, attr_name='Name')
        rmone.grab_set()
        self.wait_window(rmone)
        self.update_nameview()

    def edit_name(self):
        entry = self.name_tree.focus()
        if entry != '':
            name_entry = self.name_tree.item(entry)
            name = plorn.attr.PlornName(name_entry['text'],
                                           id=name_entry['values'][0],
                                           parent_id=name_entry['values'][1])
            showone = plorn.attr.PlornEditAttr(self, name,
                                               attr_name='Name',
                                               table_name='names')
            showone.grab_set()
            self.wait_window(showone)
            self.update_nameview()
        else:
            Messagebox.show_error('Please select a name to edit',
                                  parent=self, title='Select a Name')

    def build_place_list(self, parent):
        self.place_tree = plorn.attr.PlornAttrTreeview(parent, heading='Place')
        self.place_tree.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        bframe = ttk.Frame(parent, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=1)
        self.place_buttons = [
            make_button(bframe, text='expand', command=self.toggle_places),
            make_button(bframe, text='add', command=self.add_place),
            make_button(bframe, text='remove', command=self.remove_place),
            make_button(bframe, text='edit', command=self.edit_place),
        ]
        for n in range(0, len(self.place_buttons)):
            bframe.rowconfigure(n+1, weight=1)
            self.place_buttons[n].grid(column=1, row=n+1, pady=10)
        bframe.grid(column=1, row=0, sticky=(N,S))

        self.update_placeview()

    def update_placeview(self):
        self.place_list.clear()
        self.place_list = self.db.get_all_places()
        self.place_tree.update_treeview(self.place_list)

    def toggle_places(self):
        self.place_open = not self.place_tree.get_toggle()
        if self.place_open:
            self.place_buttons[0].configure(text="collapse")
        else:
            self.place_buttons[0].configure(text="expand")
        self.place_tree.toggle_treeview(self.place_open)

    def add_place(self):
        global module_logger

        module_logger.debug(f'adding place')
        parent = self.place_tree.focus()
        if parent == '':
            pid = 0
        else:
            entry = self.place_tree.item(parent)
            pid = entry['values'][0]
        addone = plorn.attr.PlornAddAttr(self, parent_id=pid,
                                         attr_name='Place',
                                         table_name='places')
        addone.grab_set()
        self.wait_window(addone)
        attr = addone.get_new_attr()
        
        if attr and attr['id'] != None:
            place = plorn.attr.PlornPlace(attr['value'], id=attr['id'],
                                          parent_id=attr['parent_id'])
            module_logger.debug(f'add place {place.get_value()}')
            self.update_placeview()

    def remove_place(self):
        global module_logger

        entry_id = self.place_tree.focus()
        if entry_id == '':
            Messagebox.show_error('Please select a place to remove',
                                  parent=self, title='Remove Place')
            return
        entry = self.place_tree.item(entry_id)
        module_logger.debug(f'entry: {str(entry)}')
        place = plorn.attr.PlornPlace(entry['text'],
                                      id=entry['values'][0],
                                      parent_id=entry['values'][1])
        
        kids = self.db.get_place_children(place)
        if len(kids) > 0:
            msg = 'Cannot remove a place that still contains other places'
            Messagebox.show_error(msg, parent=self, title='Remove Place')
            return

        place = self.db.get_place(entry['values'][0])
        parent_id = place.get_parent_id()
        module_logger.debug(f'removing place {place.get_value()} from {parent_id}')
        rmone = plorn.attr.PlornRemoveAttr(self, place, attr_name='Place')
        rmone.grab_set()
        self.wait_window(rmone)
        self.update_placeview()

    def edit_place(self):
        entry = self.place_tree.focus()
        if entry != '':
            place_entry = self.place_tree.item(entry)
            place = plorn.attr.PlornPlace(place_entry['text'],
                                           id=place_entry['values'][0],
                                           parent_id=place_entry['values'][1])
            showone = plorn.attr.PlornEditAttr(self, place,
                                               attr_name='Place',
                                               table_name='places')
            showone.grab_set()
            self.wait_window(showone)
            self.update_placeview()
        else:
            Messagebox.show_error('Please select a place to edit',
                                  parent=self, title='Select a Place')

    def build_tag_list(self, parent):
        self.tag_tree = plorn.attr.PlornAttrTreeview(parent, heading='Tag')
        self.tag_tree.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        bframe = ttk.Frame(parent, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=1)
        self.tag_buttons = [
            make_button(bframe, text='expand', command=self.toggle_tags),
            make_button(bframe, text='add', command=self.add_tag),
            make_button(bframe, text='remove', command=self.remove_tag),
            make_button(bframe, text='edit', command=self.edit_tag),
        ]
        for n in range(0, len(self.tag_buttons)):
            bframe.rowconfigure(n+1, weight=1)
            self.tag_buttons[n].grid(column=1, row=n+1, pady=10)
        bframe.grid(column=1, row=0, sticky=(N,S))

        self.update_tagview()

    def update_tagview(self):
        self.tag_list.clear()
        self.tag_list = self.db.get_all_tags()
        self.tag_tree.update_treeview(self.tag_list)

    def toggle_tags(self):
        self.tag_open = not self.tag_tree.get_toggle()
        if self.tag_open:
            self.tag_buttons[0].configure(text="collapse")
        else:
            self.tag_buttons[0].configure(text="expand")
        self.tag_tree.toggle_treeview(self.tag_open)

    def add_tag(self):
        global module_logger

        module_logger.debug(f'adding tag')
        parent = self.tag_tree.focus()
        if parent == '':
            pid = 0
        else:
            entry = self.tag_tree.item(parent)
            pid = entry['values'][0]
        addone = plorn.attr.PlornAddAttr(self, parent_id=pid,
                                         attr_name='Tag',
                                         table_name='tags')
        addone.grab_set()
        self.wait_window(addone)
        attr = addone.get_new_attr()
        
        if attr and attr['id'] != None:
            tag = plorn.attr.PlornTag(attr['value'], id=attr['id'],
                                      parent_id=attr['parent_id'])
            module_logger.debug(f'add tag {tag.get_value()}')
            self.update_tagview()

    def remove_tag(self):
        global module_logger

        entry_id = self.tag_tree.focus()
        if entry_id == '':
            Messagebox.show_error('Please select a tag to remove',
                                  parent=self, title='Remove Tag')
            return
        entry = self.tag_tree.item(entry_id)
        module_logger.debug(f'entry: {str(entry)}')
        tag = plorn.attr.PlornTag(entry['text'],
                                  id=entry['values'][0],
                                  parent_id=entry['values'][1])
        
        kids = self.db.get_tag_children(tag)
        if len(kids) > 0:
            msg = 'Cannot remove a tag that still contains other tags'
            Messagebox.show_error(msg, parent=self, title='Remove Tag')
            return

        tag = self.db.get_tag(entry['values'][0])
        parent_id = tag.get_parent_id()
        module_logger.debug(f'removing tag {tag.get_value()} from {parent_id}')
        rmone = plorn.attr.PlornRemoveAttr(self, tag, attr_name='Tag')
        rmone.grab_set()
        self.wait_window(rmone)
        self.update_tagview()

    def edit_tag(self):
        entry = self.tag_tree.focus()
        if entry != '':
            tag_entry = self.tag_tree.item(entry)
            tag = plorn.attr.PlornTag(tag_entry['text'],
                                      id=tag_entry['values'][0],
                                      parent_id=tag_entry['values'][1])
            showone = plorn.attr.PlornEditAttr(self, tag,
                                               attr_name='Tag',
                                               table_name='tags')
            showone.grab_set()
            self.wait_window(showone)
            self.update_tagview()
        else:
            Messagebox.show_error('Please select a tag to edit',
                                  parent=self, title='Select a Tag')

    def build_search_options(self, parent):
        tfont = font.nametofont('TkDefaultFont')

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=5)
        for ii in range(0,6):
            parent.rowconfigure(ii, weight=1)

        text = 'Simple Search:'
        header1 = ttk.Label(parent, width=len(text), text=text)
        header1.config(font=(tfont, self.config.get_fontsize()+4, 'bold'))
        header1.grid(column=0, row=0, sticky=W, columnspan=2)

        lab1 = ttk.Label(parent, width=20, text='What to Search:')
        lab1.grid(column=0, row=1, sticky=E)
        self.s_domain_box = ttk.Combobox(parent, font=tfont,
                                         textvariable=self.s_domain)
        choices = [
                SearchDomainStrings[SearchDomains.ALBUMS],
                SearchDomainStrings[SearchDomains.PHOTOS],
                SearchDomainStrings[SearchDomains.ALL],
        ]
        self.s_domain_box.config(values=choices)
        self.s_domain_box.config(state="readonly")
        self.s_domain_box.grid(column=1, row=1, sticky=(W,E))
        self.s_domain.set(SearchDomainStrings[SearchDomains.ALL])

        self.s_field_choice = ttk.Combobox(parent, font=tfont,
                                           textvariable=self.s_field)

        lab2 = ttk.Label(parent, width=20, text='Field to Search:')
        lab2.grid(column=0, row=2, sticky=E)
        choices = [
            SearchFieldStrings[SearchFields.NAME],
            SearchFieldStrings[SearchFields.PATH],
            SearchFieldStrings[SearchFields.DATED],
            SearchFieldStrings[SearchFields.NOTES],
            SearchFieldStrings[SearchFields.PHOTO_COUNTS],
            SearchFieldStrings[SearchFields.NAME_ATTR],
            SearchFieldStrings[SearchFields.PLACE_ATTR],
            SearchFieldStrings[SearchFields.TAG_ATTR],
        ]
        self.s_field_choice.config(values=choices)
        self.s_field_choice.config(state="readonly")
        self.s_field_choice.grid(column=1, row=2, sticky=(W,E))
        self.s_field.set(SearchFieldStrings[SearchFields.NAME])

        lab3 = ttk.Label(parent, width=20, text='Regular Expression:')
        lab3.grid(column=0, row=3, sticky=E)
        self.s_regex_box = ttk.Entry(parent, width=40, font=tfont,
                                      text=self.s_regex)
        self.s_regex_box.grid(column=1, row=3, sticky=W)

        bframe = ttk.Frame(parent, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=8)
        self.search_buttons = [
            ttk.Button(bframe, text='Clear', command=self.clear_search),
            ttk.Button(bframe, text='Search', command=self.do_search),
            ttk.Button(bframe, text='Advanced Search', command=self.adv_search),
        ]
        for n in range(0, len(self.search_buttons)):
            bframe.columnconfigure(n, weight=1)
            self.search_buttons[n].grid(column=n, row=0, padx=20)
        bframe.grid(column=0, row=4, sticky=(S), columnspan=2)
    
    def clear_search(self):
        self.s_domain.set(SearchDomainStrings[SearchDomains.ALL])
        self.s_field.set(SearchFieldStrings[SearchFields.NAME])
        self.s_regex.set('.*')
        self.s_domain_box.focus_set()

    def do_search(self):
        global module_logger

        module_logger.debug('do_search: started...')
        try:
            srch = plorn.search.PlornSearch(self.s_domain.get(),
                                            self.s_field.get(),
                                            self.s_regex.get(),
                                           )
            albums, photos = srch.do_search()
            #module_logger.debug(f'do_search: albums found -- {albums}')
            #module_logger.debug(f'do_search: photos found -- {photos}')
            res = plorn.search.PlornSearchResults(self, albums, photos,
                                                  self.s_domain.get(),
                                                  self.s_field.get(),
                                                  self.s_regex.get())

        except plorn.search.SearchException as se:
            Messagebox.show_error(f'{se}', parent=self, title='Invalid Search')

    def adv_search(self):
        return plorn.search.PlornAdvancedSearch(self)

    def build_settings_view(self, parent):
        plorn_label = make_header_label(parent, width=20,
                                        text='Global Settings:')
        plorn_label.grid(column=0, row=0, pady=10)
        items = [
            ['User Name:',        1, self.config.get_username()],
            ['Full Name:',        2, self.config.get_fullname()],
            ['Config Directory:', 3, self.config.get_configdir()],
            ['Data Directory:',   4, self.config.get_datadir()],
            ['SQLite Database:',  5, self.config.get_dbname()],
        ]

        num = 0
        labels = {}
        entries = {}
        for label_text, row, value in items:
            labels[row] = ttk.Label(parent, width=20, text=label_text)
            labels[row].grid(column=0, row=row, pady=5)
            entries[row] = ttk.Entry(parent, width=30, font=self.font)
            entries[row].insert(0, value)
            entries[row].grid(column=1, row=row, pady=5)
            entries[row].configure(state='readonly')

        #-- allow for some user interface adjustments
        row = len(labels) + 1
        spacing_label = ttk.Label(parent, width=20, state='hidden')
        spacing_label.grid(column=0, row=row, pady=5)
        row += 1
        gui_label = make_header_label(parent, width=20, text='User Interface:')
        gui_label.grid(column=0, row=row, pady=5)
        row += 1

        themel = ttk.Label(parent, width=20, text='Theme')
        themel.grid(column=0, row=row, pady=5)
        current_theme = ttk.Label(master=parent, text=self.config.get_theme(),
                                  font=self.font)
        current_theme.grid(column=1, row=row, pady=5)
        themecb = ttk.Combobox(master=current_theme, width=29,
                               values=self.style.theme_names(),
                               font=self.font)
        themecb.grid(column=1, row=row, pady=5)
        themecb.current(self.style.theme_names().index(self.style.theme.name))

        def change_theme(e):
            t = themecb.get()
            self.style.theme_use(t)
            current_theme.configure(text=t)
            themecb.selection_clear()

        themecb.bind("<<ComboboxSelected>>", change_theme)
        row += 1

        def change_fontsize():
            default = font.nametofont('TkDefaultFont')
            default.configure(size=current_size.get())

        fsl = ttk.Label(parent, width=20, text='Font Size')
        fsl.grid(column=0, row=row, pady=5)
        current_size = IntVar(value=self.config.get_fontsize())
        fse = ttk.Spinbox(master=parent, from_=0, to=100,
                          width=28, font=self.font,
                          textvariable=current_size,
                          command=change_fontsize)
        fse.grid(column=1, row=row, pady=5)
        row += 1


#-- the plorn GUI
def user_interface():
    global root_window

    root_window = Plorn(iconphoto=plorn.config.plorn_photo_path())
    root_window.mainloop()

