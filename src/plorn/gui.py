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

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview, TableRow
from plorn.widgets import *

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

#-- set up logging
root_logger = logging.getLogger('')
root_logger.setLevel(logging.DEBUG)
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
    def __init__(self):
        super().__init__(themename='darkly')
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
        self.font = font.nametofont('TkDefaultFont')
        self.font.configure(size=self.config.get_fontsize())
        style = ttk.Style()
        style.configure('TEntry', font=self.font)

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

        self.photos_tab = 1
        self.pview = None
        self.photo_list = []
        self.button_imgs = {}
        self.last_button_img = None
        self.photo_count = 0
        self.current_photo = None
        self.current_photo_button = None
        self.current_photo_name = StringVar()
        self.photo_label = StringVar()
        self.album_selector = None
        self.album_selected = StringVar()

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

        #-- create tabbed pane windows for albums, photos, names, places,
        #   and so on
        self.notebook = self.setup_notebook()
        self.notebook.grid(column=0, row=1, sticky=(N, W, E, S))

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
        self.album_selected.set('')
        self.build_album_view(self.album_frame)
        notebook.add(self.album_frame, text=' Albums ', sticky='nwes')
        self.albums_tab = 0

        #   ... and that has a photo list for the current album
        self.photo_frame = ttk.Frame(notebook, padding='5 5 5 5')
        self.photo_frame['borderwidth'] = 2
        self.photo_frame['relief'] = 'groove'
        self.photo_buttons = []
        self.current_album = None
        self.build_photo_list(self.photo_frame)
        notebook.add(self.photo_frame, text=' Photos ', sticky='nwes')
        self.photos_tab = 1

        #   ... and there are all sorts of names to choose from
        self.names = ttk.Frame(notebook, padding='5 5 5 5')
        self.names['borderwidth'] = 2
        self.names['relief'] = 'groove'
        self.names.columnconfigure(0, weight=1)
        self.names.rowconfigure(0, weight=1)
        self.current_photo = None
        self.build_name_list(self.names)
        notebook.add(self.names, text=' Names ')
        self.names_tab = 2

        #   ... and there are all sorts of places to choose from
        self.places = ttk.Frame(notebook, padding='5 5 5 5')
        self.places['borderwidth'] = 2
        self.places['relief'] = 'groove'
        self.places.columnconfigure(0, weight=1)
        self.places.rowconfigure(0, weight=1)
        self.current_photo = None
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
        self.build_settings(self.settings)
        notebook.add(self.settings, text=' Settings ')
        self.settings_tab = 6

        #   ... and let us know when the selected tab has changed
        notebook.bind('<<NotebookTabChanged>>', self.set_current_album)

        return notebook

    def set_current_album(self, event):
        global module_logger

        # we need this to pass on info to the photos tab only
        tab_no = self.notebook.index(self.notebook.select())
        if tab_no == self.photos_tab:
            row = self.aview.focus()
            if row != '':
                album_info = self.aview.item(row)
                album_id = album_info['text']
                album_name = album_info['values'][1]
                module_logger.debug(f'set_current_album: id {album_id}')
                module_logger.debug(f'set_current_album: name {album_name}')
                self.current_album = self.db.get_album(album_id)
                self.current_album_name = self.current_album.get_name()
                self.album_selector.set(self.current_album.get_name())
                self.update_photoview()

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

    def update_counts(self):
        self.album_count_str.set(f'Albums: {self.db.album_count()}')
        self.photo_count_str.set(f'Photos: {self.db.photo_count()}')

    def get_albums(self):
        result = []
        cursor = self.db.get_album_cursor()
        for ii in cursor:
            result.append(ii)
        result.sort(key=lambda x: int(x['id']))
        return result

    def get_photos(self, album_id=None):
        result = []
        cursor = self.db.get_photo_cursor(album_id)
        for ii in cursor:
            result.append(ii)
        result.sort(key=lambda x: int(x['id']))
        return result

    def get_all_album_data(self):
        data = []
        album_list = self.get_albums()
        for ii in album_list:
            data.append((f'{ii['id']:04}', ii['photo_count'], ii['name']))
        return data

    def update_albumview(self):
        global module_logger

        for ii in self.aview.get_children():
            self.aview.delete(ii)
        #self.album_list.clear()
        #self.album_list = self.get_albums()
        #for ii in self.album_list:
        #    self.aview.insert('', END,
        #                      text=f'{ii['id']:04}',
        #                      values=(ii['photo_count'], ii['name']))
        self.aview.focus_set()
        kids = self.aview.get_children()
        if len(kids) > 0:
            child_id = kids[0]
            if child_id != '':
                self.aview.focus(child_id)
                self.aview.selection_set(child_id)
                entry = self.aview.item(child_id)
                self.current_album = self.db.get_album(entry['text'])
                self.current_album_name = self.current_album.get_name()
                module_logger.debug(f'update_albumview: default is "{self.current_album_name}"')
        self.update_counts()

    def add_album(self):
        global module_logger

        module_logger.debug('adding album')
        addone = plorn.album.PlornAddAlbum(self)
        addone.grab_set()
        self.wait_window(addone)
        album = addone.get_new_album()
        
        if album != None and album.get_id() != None:
            self.current_album = album.get_id()
            self.current_album_name = album.get_name()
            self.aview.insert_row(self.current_album,
                                  (f'{self.current_album:04}',
                                   album.get_photo_count(),
                                   self.current_album_name))

    def remove_album(self):
        if self.current_album:
            rmone = plorn.album.PlornRemoveAlbum(self, self.current_album)
            rmone.grab_set()
            self.wait_window(rmone)
            self.aview.delete_row(iid=f'{self.current_album:04}')
        else:
            messagebox.showerror(parent=self,
                                 title='Select an Album',
                                 detail='Please select an album to remove')

    def album_info(self):
        global module_logger

        if self.current_album:
            module_logger.debug(f'show info for {self.current_album_name}')
            showone = plorn.album.PlornShowAlbum(self, self.current_album)
            showone.grab_set()
            self.wait_window(showone)
        else:
            messagebox.showerror(parent=self,
                                 title='Select an Album',
                                 detail='Please select an album to show')

    def import_photos(self):
        global module_logger

        if self.current_album:
            module_logger.debug(f'show info for {self.current_album_name}')
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
            messagebox.showinfo(parent=self,
                                title='Import Photos to Album',
                                detail=detail)
            trow = self.aview.iidmap[f'{album_id:04}']
            trow.values = [f'{album_id:04}', total, name]
            trow.refresh()
        else:
            messagebox.showerror(parent=self,
                                 title='Select an Album',
                                 detail='Please select an album to import into')

    def up_photo(self, event):
        global module_logger

        cur = self.last_button_img
        child = self.pview.prev(cur)
        if not child:
            child = cur
        module_logger.debug(f'up_photo selection: {str(cur)} -> {str(child)}')
        self.pview.selection_set(child)
        self.set_button_img(child)
        self.last_button_img = child

    def down_photo(self, event):
        global module_logger

        cur = self.last_button_img
        child = self.pview.next(cur)
        if not child:
            child = cur
        module_logger.debug(f'down_photo selection: {str(cur)} -> {str(child)}')
        self.pview.selection_set(child)
        self.set_button_img(child)
        self.last_button_img = child

    def select_photo(self, event):
        global module_logger

        child = self.pview.identify_row(event.y)
        if not self.last_button_img:
            return
        if not child:
            child = self.last_button_img
        module_logger.debug(f'select_photo selection: {str(child)}')
        self.pview.selection_set(child)
        self.set_button_img(child)
        self.last_button_img = child

    def set_button_img(self, child):
        global module_logger

        module_logger.debug(f'set_button_img entry: {str(child)}')
        if child != '':
            module_logger.debug(f'set_button_img: [{len(self.button_imgs)}] {str(child)}')
            self.current_photo_button.config(image=self.button_imgs[child])

    def update_photoview(self, album_id=None):
        global module_logger

        for ii in self.pview.get_children():
            self.pview.delete(ii)
        self.photo_list.clear()
        self.button_imgs.clear()

        if album_id == None:
            if self.current_album == None:
                module_logger.debug('update_photoview: no album provided')
                return
            else:
                album_id = self.current_album.get_id()

        self.photo_list = self.get_photos(album_id)
        for ii in self.photo_list:
            thumb_path = ii['thumbnail']
            child = self.pview.insert('', END,
                                      text=f'{ii['id']:04}',
                                      values=(ii['name'], ii['path'],
                                              thumb_path)
                                     )
            module_logger.debug(f'thumb_path: {thumb_path}')
            thumbnail = pilImage.open(thumb_path)
            button_img = ImageTk.PhotoImage(image=thumbnail)
            self.button_imgs[child] = button_img
            module_logger.debug(f'add btn img for child {child} from {ii['path']}')

        self.pview.focus_set()
        kids = self.pview.get_children()
        if len(kids) > 0:
            child_id = self.pview.get_children()[0]
            self.last_button_img = child_id
            self.pview.selection_set(child_id)
            self.pview.focus(child_id)
            self.set_button_img(child_id)
            db_id = self.pview.item(child_id)['text']
            self.current_photo = self.db.get_photo(db_id)
        self.update_counts()

    def open_album(self):
        global module_logger

        row = self.aview.focus()
        if row != '':
            album_info = self.aview.item(row)
            album_id = album_info['text']
            album_name = album_info['values'][0]
            self.current_album = self.db.get_album(album_id)
            module_logger.debug(f'open album {album_name}')
            self.notebook.select(self.photos_tab)
            self.update_photoview(album_id)
        else:
            messagebox.showerror(parent=self,
                                 title='Select an Album',
                                 detail='Please select an album to open')

    def edit_album(self):
        global module_logger

        if self.current_album:
            module_logger.debug(f'edit album {self.current_album_name}')
            showone = plorn.album.PlornEditAlbum(self, self.current_album)
            showone.grab_set()
            self.wait_window(showone)
        else:
            messagebox.showerror(parent=self,
                                 title='Select an Album',
                                 detail='Please select an album to edit')

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

        #style = ttk.Style()
        #style.layout('plorn.Treeview',
        #    [('Treeview.field', {'sticky': 'nwes', 'border': 1, 'children': [
        #        ('Treeview.padding', {'sticky': 'nwes', 'children': [
        #            ('Treeview.treearea', {'sticky': 'nwes'})
        #            ]})
        #        ]})
        #    ])
        #style.configure('plorn.Treeview',
        #                font=('TkDefaultFont', self.config.get_fontsize()),
        #                rowheight=30,
        #               )
        #style.configure('plorn.Treeview.Heading',
        #                font=('TkDefaultFont', self.config.get_fontsize()))
        #module_logger.debug(f'style: {str(style)}')

        def album_selected(rows):
            if len(rows) > 0:
                album_id, photo_count, album_name = rows[0].values
                self.current_album = album_id
                self.current_album_name = album_name

        coldata = [
            {'text': 'ID', 'stretch': False},
            {'text': 'Photos', 'stretch': False},
            {'text': 'Name', 'stretch': True},
        ]
        rowdata = self.get_all_album_data()
        module_logger.debug(f'rowdata: {rowdata}')
        #
        # foa reasons unknown, i cannot change the font size in the
        # search entry box to something readable by human eyes
        #
        # leaving this chunk o' code as a TODO reminder to fix it,
        # and then turn searchable back on
        #
        #style = ttk.Style()
        #style.configure('TEntry',
        #                font=('TkDefaultFont', self.config.get_fontsize()))
        #module_logger.info(f'TEntry: {ttk.Style().map("TEntry")}')

        aview = Tableview(master=lframe, coldata=coldata, rowdata=rowdata,
                          paginated=True,
                          searchable=True, bootstyle=PRIMARY,
                          autofit=True,
                          pagesize=20,
                          iid_field=0,      # first col as iid
                          on_select=album_selected,
                         )
        aview.align_heading_center(cid=0)
        aview.align_heading_center(cid=1)
        aview.align_column_center(cid=0)
        aview.align_column_center(cid=1)
        aview.align_column_left(cid=2)
        aview.grid(column=0, row=0, sticky=(N,W,E,S))
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

    def build_album_selector(self, parent):
        global module_logger 

        tfont = font.nametofont('TkDefaultFont')

        aframe = ttk.Frame(parent, padding=(5,5,5,5))
        aframe.columnconfigure(0, weight=1)
        aframe.columnconfigure(1, weight=5)
        aframe.rowconfigure(0, weight=1)
        aframe.option_add('*TCombobox*Listbox.font', tfont)

        lab1 = ttk.Label(aframe, width=10, text='Album:')
        lab1.grid(column=0, row=0, sticky=(W))
        self.static_widgets['photos.lab1'] = lab1

        self.album_selector = ttk.Combobox(aframe, font=tfont,
                                    textvariable=self.album_selected)
        self.update_album_selections()
        self.album_selector.config(values=self.album_name_list)
        self.album_selector.config(state="readonly")
        self.album_selector.bind('<<ComboboxSelected>>', self.album_chosen)
        self.album_selector.grid(column=1, row=0, sticky=(W+E))
        return aframe

    def album_chosen(self, event):
        global module_logger

        album_name = self.album_selected.get()
        album_id = None
        module_logger.debug(f'album chosen: {album_name}')
        if album_name == '':
            self.current_album = None
            album_id = None
        else:
            self.current_album = self.db.get_album_by_name(album_name)
            album_id = self.current_album.get_id()
        self.update_photoview(album_id)

    def update_album_selections(self):
        #self.album_list.clear()
        #self.album_list = self.get_albums()
        self.album_name_list.clear()
        self.album_name_list.append('')
        #for ii in self.album_list:
        #    self.album_name_list.append(ii['name'])

    def build_photo_list(self, parent):
        tfont = font.nametofont('TkDefaultFont')

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=4)
        parent.rowconfigure(2, weight=1)

        selected_album = ''
        if self.current_album != None:
            selected_album = self.current_album.get_name()
        self.album_selected.set(selected_album)
        sframe = self.build_album_selector(parent)
        sframe.grid(column=0, row=0, columnspan=2, sticky=(N,W,E,S))
        self.static_widgets['photo.sframe'] = sframe

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

        style = ttk.Style()
        style.layout('plorn.Treeview',
            [('Treeview.field', {'sticky': 'nwes', 'border': 1, 'children': [
                ('Treeview.padding', {'sticky': 'nwes', 'children': [
                    ('Treeview.treearea', {'sticky': 'nwes'})
                    ]})
                ]})
            ])
        style.configure('plorn.Treeview',
                        font=('TkDefaultFont', self.config.get_fontsize()),
                        rowheight=30,
                       )
        style.configure('plorn.Treeview.Heading',
                        font=('TkDefaultFont', self.config.get_fontsize()))
        pview = ttk.Treeview(lframe,
                             columns=('name', 'path', 'thumb'),
                             selectmode='browse',
                             style='plorn.Treeview')
        pview.column('#0', anchor='center', width=100, stretch=False)
        pview.heading('#0', text='ID')
        pview.column('name', anchor='w', width=200, stretch=True)
        pview.heading('name', text='Name')
        pview.column('path', anchor='w', width=200, stretch=True)
        pview.heading('path', text='Path')
        pview.grid(column=0, row=0, sticky=(N,W,E,S))
        pview['displaycolumns'] = ('name', 'path')
        xscrollbar = ttk.Scrollbar(lframe, orient='vertical',
                                  command=pview.yview)
        xscrollbar.grid(column=1, row=0, sticky=(N,W,E,S))
        yscrollbar = ttk.Scrollbar(lframe, orient='horizontal',
                                  command=pview.xview)
        yscrollbar.grid(column=0, row=1, sticky=(N,W,E,S))
        pview.configure(yscrollcommand=xscrollbar.set)
        pview.bind('<Up>', self.up_photo)
        pview.bind('<Down>', self.down_photo)
        pview.bind('<ButtonRelease-1>', self.select_photo)
        self.pview = pview
        self.update_photoview()

        self.current_photo_button = ttk.Button(rframe,
                                        state='readonly',
                                        compound='image')
        self.current_photo_button.grid(column=0, row=0)

        self.photo_buttons = [
            ttk.Button(rframe, text='info', command=self.photo_info),
            ttk.Button(rframe, text='add', command=self.add_photo),
            ttk.Button(rframe, text='remove', command=self.remove_photo),
            ttk.Button(rframe, text='edit', command=self.edit_photo),
        ]
        for n in range(0, len(self.photo_buttons)):
            self.photo_buttons[n].grid(column=0, row=n+1)

    def photo_info(self):
        global module_logger

        row = self.pview.focus()
        if row != '':
            photo = self.pview.item(row)
            photo_id = photo['text']
            module_logger.debug(f'show info for {photo_id}')
            showone = plorn.photo.PlornShowPhoto(self, photo_id)
            showone.grab_set()
            self.wait_window(showone)
        else:
            messagebox.showerror(parent=self,
                                 title='Select a Photo',
                                 detail='Please select a photo to show')

    def remove_photo(self):
        global module_logger

        row = self.pview.focus()
        if row != '':
            photo_entry = self.pview.item(row)
            photo_id = photo_entry['text']
            photo = self.db.get_photo(photo_id)
            module_logger.debug(f'remove_photo: row {row}, id {photo_id}, photo {str(photo)}')
            rmone = plorn.photo.PlornRemovePhoto(self, photo_id)
            rmone.grab_set()
            self.wait_window(rmone)
            del self.button_imgs[row]
            self.update_photoview(photo.get_album_id())
            self.update_albumview()
        else:
            messagebox.showerror(parent=self,
                                 title='Select a Photo',
                                 detail='Please select a photo to remove')

    def edit_photo(self):
        row = self.pview.focus()
        if row != '':
            photo_entry = self.pview.item(row)
            photo_id = photo_entry['text']
            photo = self.db.get_photo(photo_id)
            rmone = plorn.photo.PlornEditPhoto(self, photo_id)
            rmone.grab_set()
            self.wait_window(rmone)
            self.update_photoview(photo.get_album_id())
            self.update_albumview()
        else:
            messagebox.showerror(parent=self,
                                 title='Select a Photo',
                                 detail='Please select a photo to edit')

    def add_photo(self):
        global module_logger

        module_logger.debug('adding photo')
        album_id = self.current_album.get_id()
        addone = plorn.photo.PlornAddPhoto(self, album_id)
        addone.grab_set()
        self.wait_window(addone)
        photo = addone.get_new_photo()
        
        if photo != None and photo.get_id() != None:
            module_logger.debug(f'add a photo to {self.current_album.get_name()}')
            self.photo_list.clear()
            self.button_imgs.clear()
            module_logger.debug(f'add photo {photo.get_name()} with album_id {album_id}')
            for ii in self.get_photos(album_id):
                self.photo_list.append(ii)
            self.update_photoview(album_id)
            self.update_albumview()

    def build_name_list(self, parent):
        self.name_tree = plorn.attr.PlornAttrTreeview(parent, heading='Name')
        self.name_tree.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        bframe = ttk.Frame(parent, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=8)
        self.name_buttons = [
            ttk.Button(bframe, text='expand', command=self.toggle_names),
            ttk.Button(bframe, text='add', command=self.add_name),
            ttk.Button(bframe, text='remove', command=self.remove_name),
            ttk.Button(bframe, text='edit', command=self.edit_name),
        ]
        for n in range(0, len(self.name_buttons)):
            bframe.rowconfigure(n, weight=1)
            self.name_buttons[n].grid(column=1, row=n+1, sticky=(S))
        bframe.grid(column=1, row=0, sticky=(S))

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
            messagebox.showerror(parent=self,
                                 title='Remove Name',
                                 detail='Please select a name to remove')
            return
        entry = self.name_tree.item(entry_id)
        module_logger.debug(f'entry: {str(entry)}')
        name = plorn.attr.PlornName(entry['text'],
                                      id=entry['values'][0],
                                      parent_id=entry['values'][1])
        
        kids = self.db.get_name_children(name)
        if len(kids) > 0:
            msg = 'Cannot remove a name that still contains other names'
            messagebox.showerror(parent=self, title='Remove Name', detail=msg)
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
            messagebox.showerror(parent=self,
                                 title='Select a Name',
                                 detail='Please select a name to edit')

    def build_place_list(self, parent):
        self.place_tree = plorn.attr.PlornAttrTreeview(parent, heading='Place')
        self.place_tree.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        bframe = ttk.Frame(parent, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=8)
        self.place_buttons = [
            ttk.Button(bframe, text='expand', command=self.toggle_places),
            ttk.Button(bframe, text='add', command=self.add_place),
            ttk.Button(bframe, text='remove', command=self.remove_place),
            ttk.Button(bframe, text='edit', command=self.edit_place),
        ]
        for n in range(0, len(self.place_buttons)):
            bframe.rowconfigure(n, weight=1)
            self.place_buttons[n].grid(column=1, row=n+1, sticky=(S))
        bframe.grid(column=1, row=0, sticky=(S))

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
            messagebox.showerror(parent=self,
                                 title='Remove Place',
                                 detail='Please select a place to remove')
            return
        entry = self.place_tree.item(entry_id)
        module_logger.debug(f'entry: {str(entry)}')
        place = plorn.attr.PlornPlace(entry['text'],
                                      id=entry['values'][0],
                                      parent_id=entry['values'][1])
        
        kids = self.db.get_place_children(place)
        if len(kids) > 0:
            msg = 'Cannot remove a place that still contains other places'
            messagebox.showerror(parent=self, title='Remove Place', detail=msg)
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
            messagebox.showerror(parent=self,
                                 title='Select a Place',
                                 detail='Please select a place to edit')

    def build_tag_list(self, parent):
        self.tag_tree = plorn.attr.PlornAttrTreeview(parent, heading='Tag')
        self.tag_tree.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        bframe = ttk.Frame(parent, padding=(5,5,5,5))
        bframe.columnconfigure(0, weight=1)
        bframe.rowconfigure(0, weight=8)
        self.tag_buttons = [
            ttk.Button(bframe, text='expand', command=self.toggle_tags),
            ttk.Button(bframe, text='add', command=self.add_tag),
            ttk.Button(bframe, text='remove', command=self.remove_tag),
            ttk.Button(bframe, text='edit', command=self.edit_tag),
        ]
        for n in range(0, len(self.tag_buttons)):
            bframe.rowconfigure(n, weight=1)
            self.tag_buttons[n].grid(column=1, row=n+1, sticky=(S))
        bframe.grid(column=1, row=0, sticky=(S))

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
            messagebox.showerror(parent=self,
                                 title='Remove Tag',
                                 detail='Please select a tag to remove')
            return
        entry = self.tag_tree.item(entry_id)
        module_logger.debug(f'entry: {str(entry)}')
        tag = plorn.attr.PlornTag(entry['text'],
                                  id=entry['values'][0],
                                  parent_id=entry['values'][1])
        
        kids = self.db.get_tag_children(tag)
        if len(kids) > 0:
            msg = 'Cannot remove a tag that still contains other tags'
            messagebox.showerror(parent=self, title='Remove Tag', detail=msg)
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
            messagebox.showerror(parent=self,
                                 title='Select a Tag',
                                 detail='Please select a tag to edit')

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
            messagebox.showerror(parent=self,
                                 title='Invalid Search',
                                 detail=f'{se}')

    def adv_search(self):
        return plorn.search.PlornAdvancedSearch(self)

    def build_settings(self, parent):
        tfont = font.nametofont('TkDefaultFont')

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
            entries[row] = ttk.Entry(parent, width=30, font=tfont)
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
                                  font=tfont)
        current_theme.grid(column=1, row=row, pady=5)
        themecb = ttk.Combobox(master=current_theme, width=29,
                               values=self.style.theme_names(),
                               font=tfont)
        themecb.grid(column=1, row=row, pady=5)
        themecb.current(self.style.theme_names().index(self.style.theme.name))

        def change_theme(e):
            t = themecb.get()
            self.style.theme_use(t)
            current_them.configure(text=t)
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
                          width=28, font=tfont,
                          textvariable=current_size,
                          command=change_fontsize)
        fse.grid(column=1, row=row, pady=5)
        row += 1

#-- the plorn GUI
def user_interface():
    global root_window

    root_window = Plorn()
    root_window.mainloop()

