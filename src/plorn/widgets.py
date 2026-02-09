#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import filetype
import logging
import os
import re
import shutil
import sys
import time
from PIL import Image as pilImage
from PIL import ImageTk

from tkinter import font
import ttkbootstrap as ttk
from ttkbootstrap import StringVar, IntVar
from ttkbootstrap.constants import *

from plorn.config import get_config

module_logger = logging.getLogger('plorn.widgets')
module_logger.setLevel(logging.INFO)

def make_button(parent, text='Button', command=None, width=10, **kwargs):
    return ttk.Button(parent, text=text, command=command, width=width,
                      bootstyle="outline-primary", **kwargs)

def make_header_label(parent, width=20, text='', size=None):
    lbl = ttk.Label(parent, width=width, text=text)
    if not size:
        size = get_config().get_fontsize()+4
    lbl.configure(font=(font.nametofont('TkDefaultFont'),
                        size, 'bold', 'italic'))
    return lbl

