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
    def __init__(self, name, id=None, parent_id=0):
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
    def __init__(self, parent, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornAddName")
        module_logger.debug(f"PlornAddName: {parent}, {parent_id}")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.name = ""
        self.parent_id = parent_id
        self.db = plorn_db.open()
        self.new_name = None

        self.geometry("600x200")
        self.title("Add Name")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        container_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        container_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        container_frame.option_add("*TCombobox*Listbox.font", tfont)

        self.container_list = {}
        self.container_list[""] = 0
        self.container_selector = None
        self.container_selected = StringVar(self.frame)
        lab1 = ttk.Label(container_frame)
        lab1.configure(text=f"Select container:  ")
        lab1.grid(column=0, row=0, sticky=W)
        rents = self.db.get_names()
        for ii in rents:
            self.container_list[ii.get_name()] = ii.get_id()
            if self.parent_id == ii.get_id():
                self.container_selected.set(ii.get_name())
        module_logger.debug(f"names: {str(self.container_list)}")
        self.container_selector = ttk.Combobox(container_frame, font=tfont,
                                        textvariable=self.container_selected)
        rent_keys = list(self.container_list.keys())
        rent_keys.sort()
        self.container_selector.config(values=rent_keys)
        self.container_selector.config(state="readonly")
        self.container_selector.grid(column=1, row=0, sticky=(W+E))

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Name: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.name_entered = StringVar(self.frame)
        self.name_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.name_entered,
                                    font=tfont)
        self.name_entry.grid(column=1, row=0, sticky=W)

        if self.parent_id == 0:
            self.name_entry.focus_set()
        else:
            self.container_selector.focus_set()

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
        container_name = self.container_selected.get()
        if new_name == "":
            messagebox.showerror(parent=self,
                                 title="Add Name",
                                 detail="Name cannot be blank")
            return

        pid = self.container_list[container_name]
        if self.db.name_exists(new_name, pid):
            messagebox.showerror(parent=self,
                                 title="Add Name",
                                 detail="Name already exists with same parent")
            return

        self.new_name = self.db.add_name(new_name, parent_id=pid)
        #module_logger.debug(f"added: {str(self.db.get_name(id))}")
        self.destroy()

    def clear_name(self):
        self.name_entered.set("")

    def get_new_name(self):
        return self.new_name


class PlornRemoveName(Toplevel):
    def __init__(self, parent, name_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornRemoveName")
        self.name_id = name_id
        self.parent_id = parent_id
        self.db = plorn_db.open()
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)

        self.geometry("600x200")
        self.title("Remove Name")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        lab1 = ttk.Label(self.frame, text="Remove: ")
        lab1.grid(column=0, row=0, sticky=W)

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Name: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.name_entered = StringVar(self.frame)
        fullname = ", ".join(self.db.get_full_name(name_id))
        self.name_entered.set(fullname)
        self.name_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.name_entered,
                                    font=tfont, state="readonly")
        self.name_entry.grid(column=1, row=0, sticky=W)

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="remove", command=self.remove_name),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def remove_name(self):
        res = None
        kids = self.db.get_name_children(self.name_id)
        if len(kids) > 0:
            msg = "Cannot remove a name that still contains other names"
            messagebox.showerror(parent=self, title="Remove Name", detail=msg)
        else:
            self.db.remove_name(self.name_id, self.parent_id)
            msg = f"removed: {self.name_id} from {self.parent_id}"
            module_logger.debug(msg)
        self.destroy()


class PlornEditName(Toplevel):
    def __init__(self, parent, name, name_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornEditName")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.name = name
        self.name_id = name_id
        self.parent_id = parent_id
        self.db = plorn_db.open()
        self.name_obj = self.db.get_name(name_id, parent_id)

        self.geometry("600x200")
        self.title("Edit Name")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=2)
        self.frame = ttk.Frame(self, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))

        container_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        container_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        container_frame.option_add("*TCombobox*Listbox.font", tfont)

        self.container_list = {}
        self.container_list[""] = 0
        self.container_selector = None
        self.container_selected = StringVar(self.frame)
        lab1 = ttk.Label(container_frame)
        lab1.configure(text="Parent:")
        lab1.grid(column=0, row=0, sticky=W)

        rents = {}
        rents[""] = 0
        rents = self.db.get_names()
        for ii in rents:
            self.container_list[ii.get_name()] = ii.get_id()
        module_logger.debug(f"rents: {str(self.container_list)}")
        self.container_selector = ttk.Combobox(container_frame, font=tfont,
                                        textvariable=self.container_selected)
        rent_keys = list(self.container_list.keys())
        rent_keys.sort()
        self.container_selector.config(values=rent_keys)
        self.container_selector.config(state="readonly")
        self.container_selector.grid(column=1, row=0, sticky=(W+E))
        if self.parent_id == 0:
            pl = ""
        else:
            pl = self.get_parent_name().get_name()
        self.container_selected.set(pl)

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Name: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.name_entered = StringVar(self.frame)
        self.name_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.name_entered,
                                    font=tfont)
        self.name_entry.grid(column=1, row=0, sticky=W)
        self.name_entered.set(self.name_obj.get_name())
        self.name_entry.focus_set()

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="update", command=self.update_name),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def get_parent_name(self):
        container = ""
        for ii in self.container_list.keys():
            if self.container_list[ii] == self.parent_id:
                container = self.container_list[ii]
                break
        return self.db.get_name(container)

    def update_name(self):
        new_name = self.name_entered.get()
        container_name = self.container_selector.get()
        if new_name == "":
            messagebox.showerror(parent=self,
                                 title="Edit Name",
                                 detail="Name cannot be blank")
            return

        if container_name == "":
            messagebox.showerror(parent=self,
                                 title="Edit Name",
                                 detail="Name cannot be blank")
            return

        name_copy = self.name_obj
        module_logger.debug(f"updating(0) {str(self.name_obj)} to {str(name_copy)}")
        pid = self.container_list[container_name]
        if self.db.name_exists(new_name, parent_id=pid):
            messagebox.showerror(parent=self,
                                 title="Edit Name",
                                 detail="Name already exists with same parent")
            return

        name_copy.set_name(new_name)
        name_copy.set_parent_id(self.container_list[container_name])
        module_logger.debug(f"updating(1) {str(self.name_obj)} to {str(name_copy)}")
        id = self.db.update_name(self.name_obj, name_copy)
        self.destroy()

