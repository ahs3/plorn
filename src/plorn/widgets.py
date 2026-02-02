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

from tkinter import *
from tkinter import font
from tkinter import messagebox

import plorn.album
import plorn.attr
import plorn.common
from plorn.common import SearchDomains, SearchDomainStrings
from plorn.common import SearchFields, SearchFieldStrings
from plorn.common import AlbumSearchInfo, PhotoSearchInfo
from plorn.config import get_config
import plorn.db
import plorn.photo
import plorn.search

module_logger = logging.getLogger('plorn.widgets')
module_logger.setLevel(logging.INFO)

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def make_button(parent, text='Button', command=None, **kwargs):
    return ttk.Button(parent, text=text, command=command,
                      bootstyle="outline-primary", **kwargs)

def make_header_label(parent, width=20, text='', size=None):
    lbl = ttk.Label(parent, width=width, text=text)
    if not size:
        size = get_config().get_fontsize()+4
    lbl.configure(font=(font.nametofont('TkDefaultFont'),
                        size, 'bold', 'italic'))
    return lbl

