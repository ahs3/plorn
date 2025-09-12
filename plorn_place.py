import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_db

module_logger = logging.getLogger("plorn.place")
module_logger.setLevel(logging.DEBUG)

class PlornPlace:
    def __init__(self, place, id=None, parent_id=0):
        self.place = place
        self.id = id
        self.parent_id = parent_id

    def __copy__(self):
        return PlornPlace(self.place, id=self.id, parent_id=self.parent_id)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_place(self, place):
        self.place = place

    def get_place(self):
        return self.place

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def __str__(self):
        val  = f"id: \"{self.id}\""
        val += f", place: \"{self.place}\""
        val += f", parent_id: \"{self.parent_id}\""
        return val

class PlornAddPlace(Toplevel):
    def __init__(self, parent, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornAddPlace")
        module_logger.debug(f"PlornAddPlace: {parent}, {parent_id}")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.place = ""
        self.parent_id = parent_id
        self.db = plorn_db.open()
        self.new_place = None

        self.geometry("600x200")
        self.title("Add Place")
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
        #locs = self.db.get_places().sort(key=lambda x: x["place"])
        locs = self.db.get_places()
        for ii in locs:
            self.container_list[ii.get_place()] = ii.get_id()
            if self.parent_id == ii.get_id():
                self.container_selected.set(ii.get_place())
        module_logger.debug(f"places: {str(self.container_list)}")
        self.container_selector = ttk.Combobox(container_frame, font=tfont,
                                        textvariable=self.container_selected)
        loc_keys = list(self.container_list.keys())
        loc_keys.sort()
        self.container_selector.config(values=loc_keys)
        self.container_selector.config(state="readonly")
        self.container_selector.grid(column=1, row=0, sticky=(W+E))

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Place: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.place_entered = StringVar(self.frame)
        self.place_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.place_entered,
                                    font=tfont)
        self.place_entry.grid(column=1, row=0, sticky=W)

        if self.parent_id == 0:
            self.place_entry.focus_set()
        else:
            self.container_selector.focus_set()

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="add", command=self.add_place),
            ttk.Button(bframe, text="clear", command=self.clear_place),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def add_place(self):
        new_place = self.place_entered.get()
        container_place = self.container_selected.get()
        if new_place == "":
            messagebox.showerror(parent=self,
                                 title="Add Place",
                                 detail="Place cannot be blank")
            return

        pid = self.container_list[container_place]
        if self.db.place_exists(new_place, pid):
            messagebox.showerror(parent=self,
                                 title="Add Place",
                                 detail="Place already exists with same parent")
            return

        self.new_place = self.db.add_place(new_place, parent_id=pid)
        #module_logger.debug(f"added: {str(self.db.get_place(id))}")
        self.destroy()

    def clear_place(self):
        self.place_entered.set("")

    def get_new_place(self):
        return self.new_place


class PlornRemovePlace(Toplevel):
    def __init__(self, parent, place_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornRemovePlace")
        self.place_id = place_id
        self.parent_id = parent_id
        self.db = plorn_db.open()
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)

        self.geometry("600x200")
        self.title("Remove Place")
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
        lab2 = ttk.Label(entry_frame, text="Place: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.place_entered = StringVar(self.frame)
        fullplace = ", ".join(self.db.get_full_place(place_id))
        self.place_entered.set(fullplace)
        self.place_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.place_entered,
                                    font=tfont, state="readonly")
        self.place_entry.grid(column=1, row=0, sticky=W)

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="remove", command=self.remove_place),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def remove_place(self):
        res = None
        kids = self.db.get_place_children(self.place_id)
        if len(kids) > 0:
            msg = "Cannot remove a place that still contains other places"
            messagebox.showerror(parent=self, title="Remove Place", detail=msg)
        else:
            self.db.remove_place(self.place_id, self.parent_id)
            msg = f"removed: {self.place_id} from {self.parent_id}"
            module_logger.debug(msg)
        self.destroy()


class PlornEditPlace(Toplevel):
    def __init__(self, parent, place, place_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornEditPlace")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.place = place
        self.place_id = place_id
        self.parent_id = parent_id
        self.db = plorn_db.open()
        self.place_obj = self.db.get_place(place_id, parent_id)

        self.geometry("600x200")
        self.title("Edit Place")
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
        lab1.configure(text="Place:")
        lab1.grid(column=0, row=0, sticky=W)

        locs = {}
        locs = self.db.get_places()
        for ii in locs:
            self.container_list[ii.get_place()] = ii.get_id()
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
            pl = self.get_parent_place()
        self.container_selected.set(pl.get_place())

        entry_frame = ttk.Frame(self.frame, padding="10 10 10 10")
        entry_frame.grid(column=0, row=1, sticky=(N, W, E, S))
        lab2 = ttk.Label(entry_frame, text="Place: ")
        lab2.grid(column=0, row=0, sticky=W)
        self.place_entered = StringVar(self.frame)
        self.place_entry = ttk.Entry(entry_frame, width=40,
                                    textvariable=self.place_entered,
                                    font=tfont)
        self.place_entry.grid(column=1, row=0, sticky=W)
        self.place_entered.set(self.place_obj.get_place())
        self.place_entry.focus_set()

        bframe = ttk.Frame(self.frame, padding="10 10 10 10")
        bframe.grid(column=0, row=2, sticky=(W+E))
        self.buttons = [
            ttk.Button(bframe, text="update", command=self.update_place),
            ttk.Button(bframe, text="cancel", command=self.destroy),
        ]
        for n in range(0, len(self.buttons)):
            self.buttons[n].grid(column=n, row=0, padx=10, pady=10)

    def get_parent_place(self):
        container = ""
        for ii in self.container_list.keys():
            if self.container_list[ii] == self.parent_id:
                container = self.container_list[ii]
                break
        return self.db.get_place(container)

    def update_place(self):
        new_place = self.place_entered.get()
        container_place = self.container_selector.get()
        if new_place == "":
            messagebox.showerror(parent=self,
                                 title="Edit Place",
                                 detail="Place cannot be blank")
            return

        if container_place == "":
            messagebox.showerror(parent=self,
                                 title="Edit Place",
                                 detail="Place cannot be blank")
            return

        place_copy = self.place_obj
        module_logger.debug(f"updating(0) {str(self.place_obj)} to {str(place_copy)}")
        pid = self.container_list[container_place]
        if self.db.place_exists(new_place, parent_id=pid):
            messagebox.showerror(parent=self,
                                 title="Edit Place",
                                 detail="Place already exists with same parent")
            return

        place_copy.set_place(new_place)
        place_copy.set_parent_id(self.container_list[container_place])
        module_logger.debug(f"updating(1) {str(self.place_obj)} to {str(place_copy)}")
        id = self.db.update_place(self.place_obj, place_copy)
        self.destroy()

