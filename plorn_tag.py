import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.tag")
module_logger.setLevel(logging.DEBUG)

class PlornTag:
    def __init__(self, tag, id=None, parent_id=0):
        self.tag = tag
        self.id = id
        self.parent_id = parent_id

    def __copy__(self):
        return PlornTag(self.tag, id=self.id, parent_id=self.parent_id)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_tag(self, tag):
        self.tag = tag

    def get_tag(self):
        return self.tag

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def __str__(self):
        val  = f"id: \"{self.id}\""
        val += f", tag: \"{self.tag}\""
        val += f", parent_id: \"{self.parent_id}\""
        return val

class PlornAddTag(Toplevel):
    def __init__(self, parent, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornAddTag")
        module_logger.debug(f"PlornAddTag: {parent}, {parent_id}")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.tag = ""
        self.parent_id = parent_id
        self.db = plorn_db.open()
        self.new_tag = None

        self.geometry("600x200")
        self.title("Add Tag")
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
        locs = self.db.get_tags()
        for ii in locs:
            self.container_list[ii.get_tag()] = ii.get_id()
            if self.parent_id == ii.get_id():
                self.container_selected.set(ii.get_tag())
        module_logger.debug(f"tags: {str(self.container_list)}")
        self.container_selector = ttk.Combobox(container_frame, font=tfont,
                                        textvariable=self.container_selected)
        loc_keys = list(self.container_list.keys())
        loc_keys.sort()
        self.container_selector.config(values=loc_keys)
        self.container_selector.config(state="readonly")
        self.container_selector.grid(column=1, row=0, sticky=(W+E))

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Tag: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.tag_entered = StringVar(self.frame)
        self.tag_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.tag_entered,
                                    font=tfont)
        self.tag_entry.grid(column=1, row=0, sticky=W)

        if self.parent_id == 0:
            self.tag_entry.focus_set()
        else:
            self.container_selector.focus_set()

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="add", command=self.add_tag),
            ttk.Button(bframe, text="clear", command=self.clear_tag),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def add_tag(self):
        new_tag = self.tag_entered.get()
        container_tag = self.container_selected.get()
        if new_tag == "":
            messagebox.showerror(parent=self,
                                 title="Add Tag",
                                 detail="Tag cannot be blank")
            return

        pid = self.container_list[container_tag]
        if self.db.tag_exists(new_tag, pid):
            messagebox.showerror(parent=self,
                                 title="Add Tag",
                                 detail="Tag already exists with same parent")
            return

        self.new_tag = self.db.add_tag(new_tag, parent_id=pid)
        self.destroy()

    def clear_tag(self):
        self.tag_entered.set("")

    def get_new_tag(self):
        return self.new_tag


class PlornRemoveTag(Toplevel):
    def __init__(self, parent, tag_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornRemoveTag")
        self.tag_id = tag_id
        self.parent_id = parent_id
        self.db = plorn_db.open()
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)

        self.geometry("600x200")
        self.title("Remove Tag")
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
        lab2 = ttk.Label(entry_frame, text="Tag: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.tag_entered = StringVar(self.frame)
        fulltag = ", ".join(self.db.get_full_tag(tag_id))
        self.tag_entered.set(fulltag)
        self.tag_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.tag_entered,
                                    font=tfont, state="readonly")
        self.tag_entry.grid(column=1, row=0, sticky=W)

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="remove", command=self.remove_tag),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def remove_tag(self):
        res = None
        kids = self.db.get_tag_children(self.tag_id)
        if len(kids) > 0:
            msg = "Cannot remove a tag that still contains other tags"
            messagebox.showerror(parent=self, title="Remove Tag", detail=msg)
        else:
            self.db.remove_tag(self.tag_id, self.parent_id)
            msg = f"removed: {self.tag_id} from {self.parent_id}"
            module_logger.debug(msg)
        self.destroy()


class PlornEditTag(Toplevel):
    def __init__(self, parent, tag, tag_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornEditTag")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.tag = tag
        self.tag_id = tag_id
        self.parent_id = parent_id
        self.db = plorn_db.open()
        self.tag_obj = self.db.get_tag(tag_id, parent_id)

        self.geometry("600x200")
        self.title("Edit Tag")
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
        lab1.configure(text="Tag:")
        lab1.grid(column=0, row=0, sticky=W)

        locs = {}
        locs = self.db.get_tags()
        for ii in locs:
            self.container_list[ii.get_tag()] = ii.get_id()
        module_logger.debug(f"locs: {str(self.container_list)}")
        self.container_selector = ttk.Combobox(container_frame, font=tfont,
                                        textvariable=self.container_selected)
        loc_keys = list(self.container_list.keys())
        loc_keys.sort()
        self.container_selector.config(values=loc_keys)
        self.container_selector.config(state="readonly")
        self.container_selector.grid(column=1, row=0, sticky=(W+E))
        if self.parent_id == 0:
            pl = ""
        else:
            pl = self.get_parent_tag().get_tag()
        self.container_selected.set(pl)

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Tag: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.tag_entered = StringVar(self.frame)
        self.tag_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.tag_entered,
                                    font=tfont)
        self.tag_entry.grid(column=1, row=0, sticky=W)
        self.tag_entered.set(self.tag_obj.get_tag())
        self.tag_entry.focus_set()

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="update", command=self.update_tag),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def get_parent_tag(self):
        container = ""
        for ii in self.container_list.keys():
            if self.container_list[ii] == self.parent_id:
                container = self.container_list[ii]
                break
        return self.db.get_tag(container)

    def update_tag(self):
        new_tag = self.tag_entered.get()
        container_tag = self.container_selector.get()
        if new_tag == "":
            messagebox.showerror(parent=self,
                                 title="Edit Tag",
                                 detail="Tag cannot be blank")
            return

        if container_tag == "":
            messagebox.showerror(parent=self,
                                 title="Edit Tag",
                                 detail="Tag cannot be blank")
            return

        tag_copy = self.tag_obj
        module_logger.debug(f"updating(0) {str(self.tag_obj)} to {str(tag_copy)}")
        pid = self.container_list[container_tag]
        if self.db.tag_exists(new_tag, parent_id=pid):
            messagebox.showerror(parent=self,
                                 title="Edit Tag",
                                 detail="Tag already exists with same parent")
            return

        tag_copy.set_tag(new_tag)
        tag_copy.set_parent_id(self.container_list[container_tag])
        module_logger.debug(f"updating(1) {str(self.tag_obj)} to {str(tag_copy)}")
        id = self.db.update_tag(self.tag_obj, tag_copy)
        self.destroy()

