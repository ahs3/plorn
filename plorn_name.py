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

UNKNOWN_FAMILY = 1          # ID for unknown parent

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

        self.geometry("600x200")
        if self.parent_id == 0:
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
        if self.parent_id == 0:
            lab1.configure(text="Adding family:")
            lab1.grid(column=0, row=0, sticky=W)
        else:
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
            if self.parent_id != 0:
                parent_name = self.db.get_name_object(self.parent_id).get_name()
                self.family_selected.set(parent_name)

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
        family_name = self.family_selected.get()
        if new_name == "":
            messagebox.showerror(parent=self,
                                 title="Add Name",
                                 detail="Name cannot be blank")
            return

        pid = 0
        if not self.parent_id == 0:
            row = self.db.get_name_by_name(family_name, parent_id=0)
            if row == None:
                pid = 1
            else:
                pid = row["id"]

        if self.db.name_exists(new_name, pid):
            messagebox.showerror(parent=self,
                                 title="Add Name",
                                 detail="Name already exists with same parent")
            return

        id = self.db.add_name(new_name, parent_id=pid)
        #module_logger.debug(f"added: {str(self.db.get_name_object(id))}")
        self.destroy()

    def clear_name(self):
        self.name_entered.set("")


class PlornRemoveName(Toplevel):
    def __init__(self, parent, name_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornRemoveName")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.name_id = name_id
        self.parent_id = parent_id
        self.db = plorn_db.open()

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
        if self.parent_id == 0:         # it's a family
            kids = self.db.get_name_children(self.name_id)
            if len(kids) > 0:
                detail  = "Should all family members be removed also?"
                detail += " If NO, they will be put in the <unknown> family."
                res = messagebox.askyesnocancel(parent=self,
                                                title="Remove Family Members",
                                                detail=detail)
                if res == None:
                    return

                elif res == True:           # remove kids, too
                    for ii in kids:
                        id = self.db.remove_name(ii["id"], self.name_id)

                elif res == False:          # remove family only
                    for ii in kids:
                        kid = self.db.get_name_child_object(ii["id"],
                                                            self.name_id)
                        kid_copy = kid
                        kid.copy.set_parent_id(UNKNOWN_FAMILY)
                        self.db.update_name(kid, kid_copy)
            id = self.db.remove_name(self.name_id, self.parent_id)

        else:                               # it's a person only
            id = self.db.remove_name(self.name_id, self.parent_id)

        module_logger.debug(f"removed: {self.name_id} from {self.parent_id}")
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
        self.name_obj = self.db.get_name_object(name_id, parent_id)

        self.geometry("600x200")
        self.title("Edit Name")
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
        if self.parent_id == 0:
            lab1.configure(text="Family name:")
            lab1.grid(column=0, row=0, sticky=W)
        else:
            lab1.configure(text="Person name:")
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
            self.family_selected.set(self.get_parent_name())

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
        name = self.db.get_name_object(self.parent_id, parent_id=0)
        return name.get_name()

    def update_name(self):
        new_name = self.name_entered.get()
        if self.parent_id == 0:
            family_name = new_name
        else:
            family_name = self.family_selector.get()
        if new_name == "":
            messagebox.showerror(parent=self,
                                 title="Edit Name",
                                 detail="Name cannot be blank")
            return

        if family_name == "":
            messagebox.showerror(parent=self,
                                 title="Edit Name",
                                 detail="Name cannot be blank")
            return

        name_copy = self.name_obj
        module_logger.debug(f"updating(0) {str(self.name_obj)} to {str(name_copy)}")
        pid = 0
        if self.parent_id != 0:
            row = self.db.get_name_by_name(family_name)
            parent_obj = self.db.get_name_object(row["id"], parent_id=0)
            pid = parent_obj.get_id()
        if self.db.name_exists(new_name, parent_id=pid):
            messagebox.showerror(parent=self,
                                 title="Edit Name",
                                 detail="Name already exists with same parent")
            return

        name_copy.set_parent_id(pid)
        name_copy.set_name(new_name)
        module_logger.debug(f"updating(1) {str(self.name_obj)} to {str(name_copy)}")
        id = self.db.update_name(self.name_obj, name_copy)
        self.destroy()

