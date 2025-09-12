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
        locs.sort(key=lambda x: x["place"])
        for ii in locs:
            self.container_list[ii["place"]] = ii["id"]
            if self.parent_id == ii["id"]:
                self.container_selected.set(ii["place"])
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

        id = self.db.add_place(new_place, parent_id=pid)
        #module_logger.debug(f"added: {str(self.db.get_place_object(id))}")
        self.destroy()

    def clear_place(self):
        self.place_entered.set("")


class PlornRemovePlace(Toplevel):
    def __init__(self, parent, place_id, parent_id=0):
        super().__init__(parent)
        module_logger.debug("started PlornRemovePlace")
        tfont = font.nametofont("TkDefaultFont")
        style = ttk.Style()
        style.configure("TCombobox", font=tfont)
        self.place_id = place_id
        self.parent_id = parent_id
        self.db = plorn_db.open()

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
            detail  = "Should all container members be removed also?"
            detail += " If NO, they will be put in the <unknown> container."
            res = messagebox.askyesnocancel(parent=self,
                                            title="Remove Family Members",
                                            detail=detail)
            if res == None:
                return

            elif res == True:           # remove kids, too
                for ii in kids:
                    id = self.db.remove_place(ii["id"], self.place_id)

            elif res == False:          # remove container only
                for ii in kids:
                    kid = self.db.get_place_child_object(ii["id"],
                                                        self.place_id)
                    kid_copy = kid
                    kid.copy.set_parent_id(UNKNOWN_FAMILY)
                    self.db.update_place(kid, kid_copy)
        id = self.db.remove_place(self.place_id, self.parent_id)
        module_logger.debug(f"removed: {self.place_id} from {self.parent_id}")
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
        self.place_obj = self.db.get_place_object(place_id, parent_id)

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

        self.container_list = []
        self.container_selector = None
        self.container_selected = StringVar(self.frame)
        lab1 = ttk.Label(container_frame)
        if self.parent_id == 0:
            lab1.configure(text="Family place:")
            lab1.grid(column=0, row=0, sticky=W)
        else:
            lab1.configure(text="Person place:")
            lab1.grid(column=0, row=0, sticky=W)

            locs = self.db.get_families().sort(key=lambda x: x["name"])
            for ii in locs:
                self.container_list.append(ii["place"])
            module_logger.debug(f"locs: {str(self.container_list)}")
            self.container_selector = ttk.Combobox(container_frame, font=tfont,
                                            textvariable=self.container_selected)
            self.container_selector.config(values=self.container_list)
            self.container_selector.config(state="readonly")
            self.container_selector.grid(column=1, row=0, sticky=(W+E))
            self.container_selected.set(self.get_parent_place())

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
        place = self.db.get_place_object(self.parent_id, parent_id=0)
        return place.get_place()

    def update_place(self):
        new_place = self.place_entered.get()
        if self.parent_id == 0:
            container_place = new_place
        else:
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
        pid = 0
        if self.parent_id != 0:
            row = self.db.get_place_by_place(container_place)
            parent_obj = self.db.get_place_object(row["id"], parent_id=0)
            pid = parent_obj.get_id()
        if self.db.place_exists(new_place, parent_id=pid):
            messagebox.showerror(parent=self,
                                 title="Edit Place",
                                 detail="Place already exists with same parent")
            return

        place_copy.set_parent_id(pid)
        place_copy.set_place(new_place)
        module_logger.debug(f"updating(1) {str(self.place_obj)} to {str(place_copy)}")
        id = self.db.update_place(self.place_obj, place_copy)
        self.destroy()

