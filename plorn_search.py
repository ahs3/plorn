# -*- coding: UTF-8 -*-

import copy
import filetype
import logging
import os
from PIL import Image as pilImage
from PIL import ImageTk
import re

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_attr
import plorn_base_obj
import plorn_common
from plorn_common import SearchDomains, SearchDomainStrings
from plorn_common import SearchFields, SearchFieldStrings
from plorn_common import AlbumSearchInfo, PhotoSearchInfo, AttrSearchInfo
import plorn_config
from plorn_config import FONTSIZE
import plorn_db

module_logger = logging.getLogger('plorn.search')
module_logger.setLevel(logging.DEBUG)


class SearchException(Exception):
    '''
    Not all searches are allowed or even make sense
    '''
    def __init__(self, fault, *args):
        super().__init__(args)
        self.fault = fault

    def __str__(self):
        return f'{self.fault}'

class PlornSearch:
    '''
    Search engine, when provided a given set of conditions
    '''
    def __init__(self, domainstr, fieldstr, regex):
        global module_logger

        module_logger.debug('started PlornAdvancedSearch')
        self.tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()

        #-- what do we search?
        self.domainstr = domainstr
        self.domain = SearchDomainStrings.index(domainstr)

        #-- what field do we look through?
        self.fieldstr = fieldstr
        self.field = SearchFieldStrings.index(fieldstr)

        #-- using what regex (or value for photo_count)?
        self.regex = regex
        try:
            self.cregex = re.compile(regex)
        except re.PatternError as rats:
            raise SearchException(f'Search Pattern Error: {rats.msg}')

        #-- set some things so we don't have to do it repeatedly
        self.search_albums = False
        self.search_photos = False
        self.set_search_flags()

        #-- and finally, does the search make sense?
        self.is_search_allowed()

    def set_search_flags(self):
        if self.domain == SearchDomains.ALBUMS:
            self.search_albums = True
        elif self.domain == SearchDomains.PHOTOS:
            self.search_photos = True
        elif self.domain == SearchDomains.ALL:
            self.search_albums = True
            self.search_photos = True

    def is_search_allowed(self):
        result = False
        if self.domain == None:
            raise SearchException('Internal error: no search domain')
        elif self.field == None:
            raise SearchException('Internal error: no search field')
        elif self.regex == None or self.regex == '':
            raise SearchException('Please enter a search expression')
        elif self.domain == SearchDomains.ALBUMS:
            if self.field not in AlbumSearchInfo.keys() and \
               self.field not in AttrSearchInfo.keys():
                msg = f'Albums do not have a {self.fieldstr} field'
                raise SearchException(msg)
        elif self.domain == SearchDomains.PHOTOS:
            if self.field not in PhotoSearchInfo.keys() and \
               self.field not in AttrSearchInfo.keys():
                msg = f'Photos do not have a {self.fieldstr} field'
                raise SearchException(msg)
        else:
            result = True
        return result

    def do_search(self):
        global module_logger

        module_logger.debug(f'do_search: field [{self.field}] {self.fieldstr}')

        #-- collect pertinent albums and photos
        if self.field in AttrSearchInfo.keys():
            albums, photos = self.do_attr_search()
        else:
            albums, photos = self.do_field_search()
        return (albums, photos)

    def do_attr_search(self):
        '''
        search attribute tables which are a little funky
        '''
        AttrSearchFunctions = {
            SearchDomains.ALBUMS : {
                SearchFields.NAME_ATTR: {
                    'func': self.db.get_names_for_album_by_id,
                    'get' : self.db.get_name,
                },
                SearchFields.PLACE_ATTR: {
                    'func': self.db.get_places_for_album_by_id,
                    'get' : self.db.get_place,
                },
                SearchFields.TAG_ATTR: {
                    'func': self.db.get_tags_for_album_by_id,
                    'get' : self.db.get_tag,
                },
            },
            SearchDomains.PHOTOS : {
                SearchFields.NAME_ATTR: {
                    'func': self.db.get_names_for_photo_by_id,
                    'get' : self.db.get_name,
                },
                SearchFields.PLACE_ATTR: {
                    'func': self.db.get_places_for_photo_by_id,
                    'get' : self.db.get_place,
                },
                SearchFields.TAG_ATTR: {
                    'func': self.db.get_tags_for_photo_by_id,
                    'get' : self.db.get_tag,
                },
            },
        }

        albums = []
        photos = []
        if self.search_albums:
            func = AttrSearchFunctions[self.domain][self.field]['func']
            get  = AttrSearchFunctions[self.domain][self.field]['get ']
            cursor = self.db.get_album_cursor()
            for row in cursor:
                data = func(row['id'])
                for ii in data:
                    attr = get(ii['id'])
                    if self.cregex.match(attr['value']):
                        albums.append(row)

        if self.search_photos:
            func = AttrSearchFunctions[self.domain][self.field]['func']
            get  = AttrSearchFunctions[self.domain][self.field]['get ']
            cursor = self.db.get_photo_cursor()
            for row in cursor:
                data = func(row['id'])
                for ii in data:
                    attr = get(ii['id'])
                    if self.cregex.match(attr['value']):
                        photos.append(row)

        return (albums, photos)


    def do_field_search(self):
        '''
        search field values
        '''
        FieldSearchNames = {
            SearchFields.NAME: 'name',
            SearchFields.PATH: 'path',
            SearchFields.DATED: 'dated',
            SearchFields.NOTES: 'notes',
            SearchFields.PHOTO_COUNTS: 'photo_count',
        }

        albums = []
        photos = []
        if self.search_albums:
            cursor = self.db.get_album_cursor()
            for row in cursor:
                value = row[FieldSearchNames[self.field]]
                if self.cregex.match(value):
                    albums.append(row)

        if self.search_photos:
            cursor = self.db.get_photo_cursor()
            for row in cursor:
                value = row[FieldSearchNames[self.field]]
                if self.cregex.match(value):
                    photos.append(row)

        return (albums, photos)


class PlornAdvancedSearch(Toplevel):
    '''
    Allow for more complicated searchs
    '''
    def __init__(self, parent):
        super().__init__(parent)
        module_logger.debug('started PlornAdvancedSearch')
        self.tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()

        self.geometry('1200x600')
        self.title('Advanced Search')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=1)
        for ii in range(0, 9):
            self.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self, width=30, text='    Advanced Search:')
        lab1.configure(font=(self.tfont, FONTSIZE+4, 'bold'))
        lab1.grid(column=0, row=0, sticky=(W,E), pady=20)

        lab2 = ttk.Label(self, width=20, text='What to Search:')
        lab2.grid(column=0, row=1, sticky=E, pady=20)
        self.domain = StringVar()
        self.domain_box = ttk.Combobox(self, font=self.tfont, width=30,
                                       textvariable=self.domain)
        self.domain_choices = ['Album', 'Photos', 'Albums & Photos']
        self.domain_box.config(values=self.domain_choices)
        self.domain_box.config(state='readonly')
        self.domain_box.grid(column=1, row=1, sticky=(W,E),
                             columnspan=2, padx=20)
        self.domain.set('Albums & Photos')

        lab3 = ttk.Label(self, width=20, text='Field to Search')
        lab3.configure(font=(self.tfont, FONTSIZE, 'bold'))
        lab3.grid(column=0, row=2, sticky=(W,E), padx=20)
        lab4 = ttk.Label(self, width=20, text='Regular Expression')
        lab4.configure(font=(self.tfont, FONTSIZE, 'bold'))
        lab4.grid(column=1, row=2, sticky=(W,E), padx=20)
        lab5 = ttk.Label(self, width=20, text='Operator')
        lab5.configure(font=(self.tfont, FONTSIZE, 'bold'))
        lab5.grid(column=2, row=2, sticky=(W), padx=20)

        self.field_boxes = []
        self.field_chosen = []
        self.field_choices = [
            'Album Name', 'Album Path', 'Album Dated', 'Album Notes',
            'Album Photo Count',
            'Photo Name', 'Photo Path', 'Photo Dated', 'Photo Notes',
            'Name Attribute', 'Place Attribute', 'Tag Attribute',
        ]
        for ii in range(0,4):
            self.field_chosen.append(StringVar())
            box = ttk.Combobox(self, font=self.tfont,
                               textvariable=self.field_chosen[ii])
            box.config(values=self.field_choices)
            box.config(state='readonly')
            box.grid(column=0, row=ii+3, sticky=(W,E), padx=20)
            self.field_chosen[ii].set('Albums & Photos')
            self.field_boxes.append(box)

        self.regex_boxes = []
        self.regex = []
        for ii in range(0,4):
            self.regex.append(StringVar())
            box = ttk.Entry(self, width=40, font=self.tfont,
                            text=self.regex[ii])
            box.grid(column=1, row=ii+3, sticky=(W,E), padx=20)
            self.regex_boxes.append(box)

        self.op_boxes = []
        self.op_chosen = []
        self.op_choices = ['AND', 'OR']
        for ii in range(0,3):
            self.op_chosen.append(StringVar())
            box = ttk.Combobox(self, font=self.tfont,
                               textvariable=self.op_chosen[ii])
            box.config(values=self.op_choices)
            box.config(state='readonly')
            box.grid(column=2, row=ii+3, sticky=(W,E), padx=20)
            self.op_chosen[ii].set('AND')
            self.op_boxes.append(box)

        self.bframe = ttk.Frame(self, padding=(5,5,5,5))
        self.bframe.rowconfigure(0, weight=1)
        self.buttons = [
            ttk.Button(self.bframe, text='Clear', command=self.clear_entries),
            ttk.Button(self.bframe, text='Search', command=self.destroy),
            ttk.Button(self.bframe, text='Done', command=self.destroy),
        ]
        for ii in range(0, len(self.buttons)):
            self.bframe.columnconfigure(ii, weight=1)
            self.buttons[ii].grid(column=ii, row=0, padx=20, sticky=(N,S))
        self.bframe.grid(column=0, row=8, columnspan=3)

    def clear_entries(self):
        self.domain.set('Albums & Photos')
        for ii in range(0,4):
            self.field_chosen[ii].set('Albums & Photos')
            self.regex[ii].set('')
        for ii in range(0,3):
            self.op_chosen[ii].set('AND')
        self.domain_box.focus_set()


class PlornSearchResults(Toplevel):
    '''
    Show what we found searchs
    '''
    def __init__(self, parent, albums, photos, domainstr, fieldstr, regex):
        super().__init__(parent)
        module_logger.debug('started PlornAdvancedSearch')
        self.albums = albums
        self.photos = photos
        self.domainstr = domainstr
        self.fieldstr = fieldstr
        self.regex = regex
        self.tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()

        with pilImage.open('photo-album.png') as img:
            img.thumbnail((25,25), pilImage.Resampling.LANCZOS)
            self.album_icon = ImageTk.PhotoImage(image=img)
        with pilImage.open('photo.png') as img:
            img.thumbnail((25,25), pilImage.Resampling.LANCZOS)
            self.photo_icon = ImageTk.PhotoImage(image=img)

        self.title('Search Results')
        self.geometry('1200x650')
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=5)
        self.rowconfigure(2, weight=1)

        title_frame = ttk.Frame(self, padding=(5, 5, 5, 5))
        title_frame.columnconfigure(0, weight=1)
        title_frame.rowconfigure(0, weight=1)
        title_frame.rowconfigure(1, weight=1)
        title_frame.rowconfigure(2, weight=1)
        title_frame.rowconfigure(3, weight=1)
        title_frame.grid(column=0, row=0, sticky=(N,W,E,S), columnspan=2)
        title_frame.columnconfigure(0, weight=1)
        title_frame.columnconfigure(1, weight=1)
        title_frame.columnconfigure(2, weight=1)

        lab1 = ttk.Label(title_frame, width=20, text='Search Results')
        lab1.configure(font=(self.tfont, FONTSIZE, 'bold'))
        lab1.grid(column=0, row=0, sticky=(W), padx=20)

        lab2 = ttk.Label(title_frame, width=20, text='Objects Searched:')
        lab2.grid(column=0, row=1, sticky=(W), padx=20)
        lab2a = ttk.Label(title_frame, width=40, text=f'{self.domainstr}',
                          borderwidth=1, relief='sunken')
        lab2a.grid(column=1, row=1, sticky=(W), padx=20)

        lab3 = ttk.Label(title_frame, width=20, text='Field Searched:')
        lab3.grid(column=0, row=2, sticky=(W), padx=20)
        lab3a = ttk.Label(title_frame, width=40, text=f'{self.fieldstr}',
                          borderwidth=1, relief='sunken')
        lab3a.grid(column=1, row=2, sticky=(W), padx=20)

        lab4 = ttk.Label(title_frame, width=20, text='Search Expression:')
        lab4.grid(column=0, row=3, sticky=(W), padx=20)
        lab4a = ttk.Label(title_frame, width=40, text=f'{self.regex}',
                          borderwidth=1, relief='sunken')
        lab4a.grid(column=1, row=3, sticky=(W), padx=20)

        lframe = ttk.Frame(self, padding=(5, 5, 5, 5))
        lframe.columnconfigure(0, weight=1)
        lframe.rowconfigure(0, weight=1)
        lframe.grid(column=0, row=1, sticky=(N,W,E,S))

        rframe = ttk.Frame(self, padding=(5, 5, 5, 5))
        rframe.columnconfigure(0, weight=1)
        rframe.rowconfigure(0, weight=1)
        rframe.rowconfigure(1, weight=1)
        rframe.rowconfigure(2, weight=1)
        rframe.rowconfigure(3, weight=1)
        rframe.rowconfigure(4, weight=1)
        rframe.grid(column=1, row=1, sticky=(N,W,E,S))

        style = ttk.Style()
        style.layout('plorn.Treeview',
            [('Treeview.field', {'sticky': 'nwes', 'border': 1, 'children': [
                ('Treeview.padding', {'sticky': 'nwes', 'children': [
                    ('Treeview.treearea', {'sticky': 'nwes'})
                    ]})
                ]})
            ])
        style.configure('plorn.Treeview',
                        font=('TkDefaultFont', FONTSIZE),
                        rowheight=30,
                       )
        style.configure('plorn.Treeview.Heading',
                        font=('TkDefaultFont', FONTSIZE))
        tview = ttk.Treeview(lframe,
                             columns=('dated', 'id'),
                             selectmode='browse',
                             style='plorn.Treeview',
                            )
        tview.column('#0', anchor='w', width=400, stretch=True)
        tview.heading('#0', text='Name')
        tview.column('dated', anchor='w', minwidth=400, stretch=True)
        tview.heading('dated', text='Dated')
        tview.column('id', anchor='w', minwidth=100, stretch=False)
        tview.heading('id', text='ID')
        tview.grid(column=0, row=0, sticky=(N,W,E,S))
        xscrollbar = ttk.Scrollbar(lframe, orient='vertical',
                                  command=tview.yview)
        xscrollbar.grid(column=1, row=0, sticky=(N,S,E,W))
        yscrollbar = ttk.Scrollbar(lframe, orient='horizontal',
                                  command=tview.xview)
        yscrollbar.grid(column=0, row=1, sticky=(N,S,E,W))
        tview.configure(xscrollcommand=yscrollbar.set)
        tview.configure(yscrollcommand=xscrollbar.set)
        tview['displaycolumns'] = ('dated')
        self.tview = tview
        self.tview_info = {}
        self.update_view()

        info = ttk.Button(rframe, text='info', command=self.destroy)
        info.grid(column=0, row=1)
        edit = ttk.Button(rframe, text='edit', command=self.destroy)
        edit.grid(column=0, row=3)

        footer = ttk.Frame(self, padding=(5, 5, 5, 5))
        footer.columnconfigure(0, weight=1)
        footer.rowconfigure(0, weight=1)
        footer.rowconfigure(1, weight=1)
        footer.rowconfigure(2, weight=50)
        footer.grid(column=0, row=2, sticky=(N,W,E,S), columnspan=2)
        sep1 = ttk.Separator(footer, orient=HORIZONTAL)
        sep1.grid(column=0, row=0, sticky=(W+E))
        sep2 = ttk.Separator(footer, orient=HORIZONTAL)
        sep2.grid(column=0, row=1, sticky=(W+E))
        quit_button = ttk.Button(footer, text='Quit', command=self.destroy)
        quit_button.grid(column=0, row=2, sticky=(E), padx=20, pady=20)

    def update_view(self):
        def make_key(obj_type, value):
            return f'{obj_type}{value:04}'

        for ii in self.tview.get_children():
            self.tview.delete(ii)
        self.tview_info.clear()
        for ii in self.albums:
            name = f'📖 {ii['name']}'
            entry = self.tview.insert('', END,
                                      text=f'{ii['name']}',
                                      values=(ii['dated'],),
                                      image=self.album_icon)
            key = make_key('album', ii['id'])
            self.tview_info[key] = { 'entry': entry, 'row': ii }
        for ii in self.photos:
            album_key = make_key('album', ii['album_id'])
            entry = self.tview.insert(self.tview_info[album_key]['entry'], END,
                                      text=f'{ii['name']}',
                                      values=(ii['dated']),
                                      image=self.photo_icon)
            key = make_key('photo', ii['id'])
            self.tview_info[key] = { 'entry': entry, 'row': ii }
        self.tview.focus_set()
        kids = self.tview.get_children()
        if len(kids) > 0:
            child_id = kids[0]
            if child_id != '':
                self.tview.focus(child_id)
                self.tview.selection_set(child_id)

