import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.name")
module_logger.setLevel(logging.DEBUG)

class PlornName:
    def __init__(self, name, id=None, parent_id=None):
        self.name = name
        self.id = id
        self.parent_id = parent_id

    def __copy__(self):
        return PlornName(self.name, id=self.id, parent_id=self.parent_id)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def __str__(self):
        val  = f"id: \"{self.id}\""
        val += f", name: \"{self.name}\""
        val += f", parent_id: \"{self.parent_id}\""
        return val

class PlornAddName(Toplevel):
    def __init__(self, parent, parent_id=None, family=False):
        super().__init__(parent)
        module_logger.debug("started PlornAddName")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.name = ""
        self.parent_id = parent_id
        self.add_family = family
        self.db = plorn_db.open()

        self.geometry("600x200")
        if self.add_family:
            self.title("Add Family")
        else:
            self.title("Add Person")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        family_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        family_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        family_frame.option_add("*TCombobox*Listbox.font", tfont)

        self.family_list = []
        self.family_selector = None
        self.family_selected = StringVar(self.frame)
        lab1 = ttk.Label(family_frame)
        if self.add_family:
            lab1.configure(text="Adding family:")
            lab1.grid(column=0, row=0, sticky=W)
        else:
            parent_name = self.db.get_name_object(parent_id).get_name()
            lab1.configure(text=f"Select family:  ")
            lab1.grid(column=0, row=0, sticky=W)
            fams = self.db.get_families()
            for ii in fams:
                self.family_list.append(ii["name"])
            module_logger.debug(f"fams: {str(self.family_list)}")
            self.family_selector = ttk.Combobox(family_frame, font=tfont,
                                            textvariable=self.family_selected)
            self.family_selector.config(values=self.family_list)
            self.family_selector.config(state="readonly")
            self.family_selector.grid(column=1, row=0, sticky=(W+E))

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Name: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.name_entered = StringVar(self.frame)
        self.name_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.name_entered,
                                    font=tfont)
        self.name_entry.grid(column=1, row=0, sticky=W)

        if self.add_family:
            self.name_entry.focus_set()
        else:
            self.family_selector.focus_set()

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="add", command=self.add_name),
            ttk.Button(bframe, text="clear", command=self.clear_name),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def add_name(self):
        new_name = self.name_entered.get()
        if new_name == "":
            messagebox.showerror(parent=self,
                                 title="Add Name",
                                 detail="Name cannot be blank")
            return

        if self.db.name_exists(new_name):
            messagebox.showerror(parent=self,
                                 title="Add Name",
                                 detail="Name already exists with same parent")
            return

        pid = 0
        if not self.add_family:
            family_name = self.family_selector.get()
            row = self.db.get_name_by_name(family_name)
            pid = row["id"]
            #module_logger.debug(f"got family_name: {family_name}")
            #module_logger.debug(f"got family row: {str(row)}")
        id = self.db.add_name(new_name, parent_id=pid)
        #module_logger.debug(f"added: {str(self.db.get_name_object(id))}")
        self.destroy()

    def clear_name(self):
        self.name_entered.set("")
