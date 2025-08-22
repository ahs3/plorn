import logging
import os

from tkinter import *
from tkinter import ttk
from tkinter import font

import plorn_config
from plorn_config import FONTSIZE
import plorn_startup

#-- the application
class Plorn(Tk):
    def __init__(self, is_new):
        super().__init__()
        self.geometry("800x600")
        self.title("plorn")
        self.is_new = is_new
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        font.nametofont("TkDefaultFont").configure(size=FONTSIZE)

        #-- main frame for the application
        self.mainframe = ttk.Frame(self, padding="10 10 10 10")
        self.mainframe["borderwidth"] = 5
        self.mainframe["relief"] = "groove"
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=1)
        self.mainframe.rowconfigure(0, weight=10)
        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.rowconfigure(1, weight=1)
        self.mainframe.rowconfigure(2, weight=1)
        self.mainframe.rowconfigure(2, weight=1)
        self.mainframe.rowconfigure(3, weight=80)
        self.mainframe.rowconfigure(6, weight=10)

        label_text = "plorn: photo catalog"
        lheader = ttk.Label(self.mainframe, width=30,
                            text=f"{label_text:<30}")
        lheader.grid(column=0, row=0, sticky=(W))
        blanks = "      "
        mheader = ttk.Label(self.mainframe, width=30, text=f"{blanks:^30}")
        mheader.grid(column=1, row=0)
        value = f"version {plorn_config.version} "
        rheader = ttk.Label(self.mainframe, width=30, text=f"{value:>30}")
        rheader.grid(column=2, row=0, sticky=(E))
        sep1 = ttk.Separator(self.mainframe, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.mainframe, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=3, sticky=(W+E))

        #-- create a tabbed pane windows
        self.notebook = ttk.Notebook(self.mainframe)
        self.notebook.grid(column=0, row=3, columnspan=3, sticky=(N, W, E, S))
        self.albums = ttk.Frame(self.notebook, padding="5 5 5 5")
        self.albums["borderwidth"] = 2
        self.albums["relief"] = "groove"
        self.album_buttons = []
        self.build_album_list(self.albums)
        self.notebook.add(self.albums, text=" Albums ")

        self.settings = ttk.Frame(self.notebook, padding="5 5 5 5")
        self.settings["borderwidth"] = 2
        self.settings["relief"] = "groove"
        self.settings.columnconfigure(0, weight=1)
        self.settings.columnconfigure(1, weight=2)
        self.build_settings(self.settings)
        self.notebook.add(self.settings, text=" Settings ")

        #-- and an exit button ....
        sep3 = ttk.Separator(self.mainframe, orient=HORIZONTAL)
        sep3.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep4 = ttk.Separator(self.mainframe, orient=HORIZONTAL)
        sep4.grid(column=0, row=5, columnspan=3, sticky=(W+E))
        b = ttk.Button(self.mainframe, text="Quit", command=self.destroy)
        b.grid(column=1, row=6)

    def startup(self):
        if self.is_new:
            window = plorn_startup.PlornStartup(self)
            window.grab_set()
        else:
            logger.debug("just idle for now")

    def add_album(self):
        pass

    def remove_album(self):
        pass

    def album_info(self):
        pass

    def build_album_list(self, parent):
        tfont = font.nametofont("TkDefaultFont")

        parent.columnconfigure(0, weight=8)
        parent.columnconfigure(1, weight=2)
        parent.rowconfigure(0, weight=1)
        parent.pack()

        lframe = ttk.Frame(parent, padding=(5, 5, 5, 5))
        lframe.grid(column=0, row=0)
        rframe = ttk.Frame(parent, padding=(5, 5, 5, 5))
        rframe.grid(column=1, row=0)

        tview = ttk.Treeview(lframe,
                             columns=("name", "photos"),
                             select="browse")
        tview.column("#0", anchor="w")
        tview.heading("#0", text="Path")
        tview.column("name", anchor="w")
        tview.heading("name", text="Name")
        tview.column("photos", anchor="center")
        tview.heading("photos", text="Photos")
        tview.grid(column=0, row=0)
        scrollbar = ttk.Scrollbar(lframe, orient="vertical",
                                  command=tview.yview)
        scrollbar.grid(column=1, row=0)
        tview.configure(xscrollcommand=scrollbar.set)

        self.album_buttons = [
            ttk.Button(rframe, text="add", command=self.add_album),
            ttk.Button(rframe, text="remove", command=self.remove_album),
            ttk.Button(rframe, text="info", command=self.album_info),
        ]
        for n in range(0, len(self.album_buttons)):
            self.album_buttons[n].grid(column=0, row=n)

    def build_settings(self, parent):
        config = plorn_config.get_config()
        tfont = font.nametofont("TkDefaultFont")

        items = [
            ["User Name:",        0, config.get_username()],
            ["Full Name:",        1, config.get_fullname()],
            ["Config Directory:", 2, config.get_configdir()],
            ["Data Directory:",   3, config.get_datadir()],
            ["SQLite Database:",  4, config.get_dbname()],
        ]

        num = 0
        labels = {}
        entries = {}
        for label_text, row, value in items:
            labels[row] = ttk.Label(parent, width=20, text=label_text)
            labels[row].grid(column=0, row=row)
            entries[row] = ttk.Entry(parent, width=30, font=tfont)
            entries[row].insert(0, value)
            entries[row].grid(column=1, row=row)
            entries[row].configure(state="readonly")


#-- set up logging
root_logger = logging.getLogger("")
root_logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("plorn.log")
fh.setLevel(logging.DEBUG)
fhformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(fhformat)
fh.setFormatter(formatter)
root_logger.addHandler(fh)

logger = logging.getLogger("plorn")
logger.setLevel(logging.DEBUG)

#-- get the config file
logger.debug("calling PlornConfig()")
config = plorn_config.get_config()
logger.debug(f"config is new? {config.is_new()}")

if __name__ == "__main__":
    plorn = Plorn(config.is_new())
    plorn.mainloop()

