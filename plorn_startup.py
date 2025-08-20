import logging

from tkinter import *
from tkinter import ttk
from tkinter import font

import plorn_config

module_logger = logging.getLogger("plorn.startup")
module_logger.setLevel(logging.DEBUG)

class PlornStartup(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        module_logger.debug("started PlornStartup")
        self.geometry("150x250")
        self.title("Initialization")
        b = ttk.Button(self, text="Done",
                       command=self.destroy).pack(expand=True)
        module_logger.debug("PlornStartup added button")

