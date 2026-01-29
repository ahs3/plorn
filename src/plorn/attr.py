
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn.config
from plorn.config import FONTSIZE
import plorn.db

module_logger = logging.getLogger('plorn.attr')
module_logger.setLevel(logging.INFO)

class PlornAttr:
    '''
    Base class for the attributes of albums and photos,
    i.e., names, places, and tags
    '''
    def __init__(self, value, id=None, parent_id=None, table_name=''):
        self.value = value
        self.id = id
        self.parent_id = parent_id
        self.db_table_name = table_name

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def set_db_table_name(self, table_name):
        self.db_table_name = table_name

    def get_db_table_name(self):
        return self.db_table_name

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', value: \'{self.value}\''
        val += f', parent_id: \'{self.parent_id}\''
        val += f', db_table_name: \'{self.db_table_name}\''
        return val


class PlornName(PlornAttr):
    def __init__(self, name, id=None, parent_id=0):
        super().__init__(name, id=id, parent_id=parent_id, table_name='names')


class PlornPlace(PlornAttr):
    def __init__(self, place, id=None, parent_id=0):
        super().__init__(place, id=id, parent_id=parent_id, table_name='places')


class PlornTag(PlornAttr):
    def __init__(self, tag, id=None, parent_id=0):
        super().__init__(tag, id=id, parent_id=parent_id, table_name='tags')


class PlornAttrTreeview:
    '''
    Build a treeview within a frame that can be used by any of the
    derived PlornAttr classes.  Placement of the frame is controlled
    by the creator of a class instance.
    '''
    def __init__(self, parent, heading='Attribute',
                 table_name='', selectmode='browse'):
        self.parent = parent
        self.heading = heading
        self.table_name = table_name
        self.selectmode = selectmode
        self.tfont = font.nametofont('TkDefaultFont')
        self.attr_open = False

        self.tframe = ttk.Frame(self.parent, padding=(5,5,5,5))
        self.tframe.columnconfigure(0, weight=1)
        self.tframe.rowconfigure(0, weight=1)

        self.lframe = ttk.Frame(self.tframe, padding=(5, 5, 5, 5))
        self.lframe.columnconfigure(0, weight=1)
        self.lframe.rowconfigure(0, weight=1)
        self.lframe.grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = ttk.Frame(self.tframe, padding=(5, 5, 5, 5))
        self.rframe.columnconfigure(0, weight=1)
        self.rframe.rowconfigure(0, weight=1)
        self.rframe.grid(column=1, row=0, sticky=(N,W,E,S))

        self.style = ttk.Style()
        self.style.layout('plorn.Treeview',
            [('Treeview.field', {'sticky': 'nwes', 'border': 1, 'children': [
                ('Treeview.padding', {'sticky': 'nwes', 'children': [
                    ('Treeview.treearea', {'sticky': 'nwes'})
                    ]})
                ]})
            ])
        self.style.configure('plorn.Treeview',
                             font=('TkDefaultFont', FONTSIZE),
                             rowheight=30,
                            )
        self.style.configure('plorn.Treeview.Heading',
                             font=('TkDefaultFont', FONTSIZE))
        self.tview = ttk.Treeview(self.lframe,
                                  columns=('id', 'parent'),
                                  selectmode=self.selectmode,
                                  style='plorn.Treeview')
        self.tview.column('#0', anchor='w', minwidth=0, width=500)
        self.tview.heading('#0', text=self.heading)
        self.tview.column('id', anchor='w', minwidth=0, width=100)
        self.tview.heading('id', text='ID')
        self.tview.column('parent', anchor='w', minwidth=0, width=100)
        self.tview.heading('parent', text='Parent')
        self.tview['displaycolumns'] = ()
        self.tview.grid(column=0, row=0, sticky=(N,W,E,S))

        self.xscrollbar = ttk.Scrollbar(self.lframe, orient='vertical',
                                        command=self.tview.yview)
        self.xscrollbar.grid(column=1, row=0, sticky=(N,W,E,S))
        self.tview.configure(xscrollcommand=self.xscrollbar.set)

        self.yscrollbar = ttk.Scrollbar(self.lframe, orient='horizontal',
                                        command=self.tview.xview)
        self.yscrollbar.grid(column=0, row=1, sticky=(N,W,E,S))
        self.tview.configure(yscrollcommand=self.yscrollbar.set)

        #self.tview.bind('<Up>', self.up_attr)
        #self.tview.bind('<Down>', self.down_attr)
        #self.tview.bind('<ButtonRelease-1>', self.select_attr)

        return

    def get_frame(self):
        return self.tframe

    def get_children(self):
        return self.tview.get_children()

    def delete_child(self, idx):
        self.tview.delete(idx)

    def focus(self):
        return self.tview.focus()

    def item(self, idx):
        return self.tview.item(idx)

    def update_treeview(self, attr_list):
        global module_logger

        module_logger.debug(f'update_treeview: {str(attr_list)}')
        for ii in self.tview.get_children():
            self.tview.delete(ii)
        tree_ids = {}
        while len(tree_ids) < len(attr_list):
            for ii in attr_list:
                id = ii.get_id()
                pid = ii.get_parent_id()
                value = ii.get_value()
                under_id = ''
                if pid == 0 and id not in tree_ids:
                    curid = self.tview.insert(under_id, END,
                                              text=value,
                                              values=(id, pid),
                                              open=self.attr_open,
                                             )
                    tree_ids[id] = curid
                elif pid != 0 and id not in tree_ids:
                    if pid in tree_ids:
                        under_id = tree_ids[pid]
                        curid = self.tview.insert(under_id, END,
                                                  text=value,
                                                  values=(id, pid),
                                                  open=self.attr_open,
                                                 )
                        tree_ids[id] = curid

    def get_toggle(self):
        return self.attr_open

    def toggle_treeview(self, toggle):
        self.attr_open = toggle
        all_kids = []
        items = list(self.tview.get_children())
        module_logger.debug(f'ITEMS: {str(items)}')
        while len(items) > 0:
            all_kids.extend(items)
            kids = []
            for ii in items:
                kids.extend(list(self.tview.get_children(ii)))
            items = kids
            module_logger.debug(f'KIDS: {str(kids)}')
        module_logger.debug(f'ALL KIDS: {str(all_kids)}')
        for ii in all_kids:
            self.tview.item(ii, open=toggle)


class PlornAddAttr(Toplevel):
    def __init__(self, parent, parent_id=0,
                 attr_name='Attribute', table_name=''):
        super().__init__(parent)
        module_logger.debug('started PlornAddAttr')
        self.parent = parent
        self.parent_id = parent_id
        self.attr_name = attr_name
        self.table_name = table_name

        self.tfont = font.nametofont('TkDefaultFont')
        style = ttk.Style()
        style.configure('TCombobox', font=self.tfont)
        self.value = ''
        self.db = plorn.db.open()
        self.new_attr = None

        self.geometry('600x200')
        self.title(f'Add {self.attr_name}')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        container_frame = ttk.Frame(self.frame, padding='10 10 10 10')
        container_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        container_frame.option_add('*TCombobox*Listbox.font', self.tfont)

        self.container_list = {}
        self.container_list[''] = 0
        self.container_selector = None
        self.container_selected = StringVar(self.frame)
        lab1 = ttk.Label(container_frame)
        lab1.configure(text=f'Select parent {self.attr_name}:  ')
        lab1.grid(column=0, row=0, sticky=W)
        entries = self.db.get_all_attrs(table_name=self.table_name)
        for ii in entries:
            self.container_list[ii['value']] = ii['id']
            if self.parent_id == ii['id']:
                self.container_selected.set(ii['value'])
        module_logger.debug(f'attrs: {str(self.container_list)}')
        self.container_selector = ttk.Combobox(container_frame, font=self.tfont,
                                        textvariable=self.container_selected)
        entry_keys = list(self.container_list.keys())
        entry_keys.sort()
        self.container_selector.config(values=entry_keys)
        self.container_selector.config(state='readonly')
        self.container_selector.grid(column=1, row=0, sticky=(W+E))

        entry_frame = ttk.Frame(self.frame, padding='10 10 10 10')
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text=f'{self.attr_name}: ')
        lab2.grid(column=0, row=0, sticky=W)
        self.attr_entered = StringVar(self.frame)
        self.attr_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.attr_entered,
                                    font=self.tfont)
        self.attr_entry.grid(column=1, row=0, sticky=W)

        self.container_selector.focus_set()

        bframe = ttk.Frame(self.frame, padding='10 10 10 10')
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text='add', command=self.add_attr),
            ttk.Button(bframe, text='clear', command=self.clear_attr),
            ttk.Button(bframe, text='cancel', command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def add_attr(self):
        new_attr = self.attr_entered.get()
        container_attr = self.container_selected.get()
        if new_attr == '':
            messagebox.showerror(parent=self,
                                 title=f'Add {self.attr_name}',
                                 detail=f'{self.attr_name} cannot be blank')
            return

        pid = self.container_list[container_attr]
        attr = PlornAttr(new_attr, parent_id=pid, table_name=self.table_name)
        if self.db.attr_exists(attr):
            messagebox.showerror(parent=self,
                    title=f'Add {self.attr_name}',
                    detail=f'{self.attr_name} already exists with same parent')
            return

        self.new_attr = self.db.add_attr(attr)
        self.destroy()

    def clear_attr(self):
        self.attr_entered.set('')

    def get_new_attr(self):
        return self.new_attr


class PlornRemoveAttr(Toplevel):
    def __init__(self, parent, attr, attr_name='Attribute'):
        super().__init__(parent)
        module_logger.debug('started PlornRemoveAttr')
        self.parent = parent
        self.attr = attr
        self.attr_id = attr.get_id()
        self.parent_id = attr.get_parent_id()
        self.attr_name = attr_name
        self.db = plorn.db.open()
        self.tfont = font.nametofont('TkDefaultFont')
        style = ttk.Style()
        style.configure('TCombobox', font=self.tfont)

        self.geometry('600x200')
        self.title(f'Remove {self.attr_name}')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        lab1 = ttk.Label(self.frame, text=f'Remove {self.attr_name}: ')
        lab1.grid(column=0, row=0, sticky=W)

        self.entry_frame = ttk.Frame(self.frame, padding='10 10 10 10')
        self.entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(self.entry_frame, text=f'{self.attr_name}: ')
        lab2.grid(column=0, row=0, sticky=W)
        self.attr_entered = StringVar(self.frame)
        fullattr = ', '.join(self.db.get_full_attr(self.attr))
        self.attr_entered.set(fullattr)
        self.attr_entry = ttk.Entry(self.entry_frame, width=40,
                                    textvariable=self.attr_entered,
                                    font=self.tfont, state='readonly')
        self.attr_entry.grid(column=1, row=0, sticky=W)

        bframe = ttk.Frame(self.frame, padding='10 10 10 10')
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text='remove', command=self.remove_attr),
            ttk.Button(bframe, text='cancel', command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def remove_attr(self):
        res = None
        kids = self.db.get_attr_children(self.attr)
        if len(kids) > 0:
            msg  = f'Cannot remove a {self.attr_name}'
            msg += f' that still contains another {self.attr_name}'
            messagebox.showerror(parent=self,
                                 title=f'Remove {self.attr_name}',
                                 detail=msg)
        else:
            self.db.remove_attr(self.attr)
            msg = f'removed: {self.attr.get_value()} from {self.parent_id}'
            module_logger.debug(msg)
        self.destroy()


class PlornEditAttr(Toplevel):
    def __init__(self, parent, attr, attr_name='Attribute', table_name=''):
        super().__init__(parent)
        module_logger.debug('started PlornEditAttr')
        self.attr = attr
        self.attr_name = attr_name
        self.table_name = table_name
        self.tfont = font.nametofont('TkDefaultFont')
        self.style = ttk.Style()
        self.style.configure('TCombobox', font=self.tfont)
        self.attr_id = attr.get_id()
        self.parent_id = attr.get_parent_id()
        self.parent_row = {}
        self.db = plorn.db.open()

        self.geometry('600x200')
        self.title(f'Edit {self.attr_name}')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        container_frame = ttk.Frame(self.frame, padding='10 10 10 10')
        container_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        container_frame.option_add('*TCombobox*Listbox.font', self.tfont)

        self.container_list = {}
        self.container_list[''] = 0
        self.container_selector = None
        self.container_selected = StringVar(self.frame)
        lab1 = ttk.Label(container_frame)
        lab1.configure(text=f'{self.attr_name}: ')
        lab1.grid(column=0, row=0, sticky=W)

        entries = {}
        entries = self.db.get_all_attrs(table_name=self.table_name)
        for ii in entries:
            self.container_list[ii['value']] = ii['id']
        module_logger.debug(f'entries: {str(self.container_list)}')
        self.container_selector = ttk.Combobox(container_frame, font=self.tfont,
                                        textvariable=self.container_selected)
        entry_keys = list(self.container_list.keys())
        entry_keys.sort()
        self.container_selector.config(values=entry_keys)
        self.container_selector.config(state='readonly')
        self.container_selector.grid(column=1, row=0, sticky=(W+E))
        if self.parent_id == 0:
            value = ''
        else:
            module_logger.debug(f'parent_row pre: {self.parent_id}, {self.table_name}')
            self.parent_row = self.db.get_attr(self.parent_id,
                                               table_name=self.table_name)
            module_logger.debug(f'parent_row: {str(self.parent_row)}')
            value = self.parent_row['value']
        self.container_selected.set(value)

        entry_frame = ttk.Frame(self.frame, padding='10 10 10 10')
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text=f'{self.attr_name}: ')
        lab2.grid(column=0, row=0, sticky=W)
        self.attr_entered = StringVar(self.frame)
        self.attr_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.attr_entered,
                                    font=self.tfont)
        self.attr_entry.grid(column=1, row=0, sticky=W)
        self.attr_entered.set(self.attr.get_value())
        self.attr_entry.focus_set()

        bframe = ttk.Frame(self.frame, padding='10 10 10 10')
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text='update', command=self.update_attr),
            ttk.Button(bframe, text='cancel', command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def get_parent_attr(self):
        container = ''
        for ii in self.container_list.keys():
            if self.container_list[ii] == self.parent_id:
                container = self.container_list[ii]
                break
        return self.db.get_attr(container, table_name=self.table_name)

    def update_attr(self):
        new_value = self.attr_entered.get()
        container_value = self.container_selector.get()
        if new_value == '':
            messagebox.showerror(parent=self,
                                 title=f'Edit {self.attr_name}',
                                 detail=f'{self.attr_name} cannot be blank')
            return

        if container_value == '':
            pid = 0
        else:
            pid = self.container_list[container_value]

        attr_copy = copy.deepcopy(self.attr)
        attr_copy.set_value(new_value)
        attr_copy.set_parent_id(pid)
        if self.db.attr_exists(attr_copy):
            messagebox.showerror(parent=self,
                     title=f'Edit {self.attr_name}',
                     detail=f'{self.attr_name} already exists with same parent')
            return

        id = self.db.update_attr(self.attr, attr_copy)
        self.destroy()


class PlornSelectAttr(Toplevel):
    def __init__(self, attr_name='Attribute', table_name='',
                 attr_list=[]):
        super().__init__()
        module_logger.debug('started PlornSelectAttr')
        self.attr_name = attr_name
        self.table_name = table_name
        self.attr = None
        self.attr_list = attr_list
        module_logger.debug(f'PlornSelectAttr attr_list: {str(attr_list)}')
        self.db = plorn.db.open()
        self.tfont = font.nametofont('TkDefaultFont')

        self.geometry('600x450')
        self.title(f'Select {self.attr_name}')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        self.tview = PlornAttrTreeview(self.frame, heading=attr_name,
                                       table_name=table_name,
                                       selectmode='browse')
        self.tview.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))
        self.tview.update_treeview(self.attr_list)

        self.bframe = ttk.Frame(self, padding='10 10 10 10')
        self.bframe.grid(column=0, row=1, sticky=(W+E))
        self.buttons = [
            ttk.Button(self.bframe, text='add', command=self.select_attr),
            ttk.Button(self.bframe, text='done', command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def select_attr(self):
        idx = self.tview.focus()
        if idx != '':
            entry = self.tview.item(idx)
            self.attr = self.db.get_attr(entry['values'][0],
                                         table_name=self.table_name)
        self.destroy()

    def get_attr(self):
        return copy.deepcopy(self.attr)
