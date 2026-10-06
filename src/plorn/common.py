
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
import filetype
import getpass
import logging
import os
import shutil
from enum import IntEnum

#import ttkbootstrap as ttk
#from ttkbootstrap.constants import *
#from ttkbootstrap.widgets.tableview import Tableview, TableRow
#from ttkbootstrap.dialogs.message import Messagebox

#import plorn.db
from plorn.config import config

module_logger = logging.getLogger('plorn.common')
module_logger.setLevel(logging.INFO)


class SearchDomains(IntEnum):
    ALBUMS = 0
    PHOTOS = 1
    ALL    = 2

SearchDomainStrings = [ 'Albums', 'Photos', 'Albums & Photos', ]

class SearchFields(IntEnum):
    NAME = 0
    PATH = 1
    DATED = 2
    NOTES = 3
    PHOTO_COUNTS = 4
    NAME_ATTR = 5
    PLACE_ATTR = 6
    TAG_ATTR = 7

SearchFieldStrings = [
    'Name', 'Path', 'Dated', 'Notes', 'Photo Counts',
    'Name Attribute', 'Place Attribute', 'Tag Attribute',
]

AlbumSearchInfo = {
    SearchFields.NAME: 'name',
    SearchFields.DATED: 'dated',
    SearchFields.NOTES: 'notes',
    SearchFields.PHOTO_COUNTS: 'photo_count',
}

PhotoSearchInfo = {
    SearchFields.NAME: 'name',
    SearchFields.PATH: 'path',
    SearchFields.DATED: 'dated',
    SearchFields.NOTES: 'notes',
}

AttrSearchInfo = {
    SearchFields.NAME_ATTR: 'names',
    SearchFields.PLACE_ATTR: 'places',
    SearchFields.TAG_ATTR: 'tags',
}

