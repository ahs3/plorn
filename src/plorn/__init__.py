#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
from enum import IntEnum
import filetype
import getpass
import logging
import os
import shutil
import traceback

import faulthandler
faulthandler.enable()

module_logger = logging.getLogger('plorn')
module_logger.setLevel(logging.INFO)

config = ''                 # global config info to be filled in later

def DUMP_STACK():
    with open('tb.log', 'a+') as fd:
        print('\n===== traceback started ====', file=fd)
        traceback.print_stack(limit=10, file=fd)
        print('===== traceback done ====\n', file=fd)
        fd.close()

################################################################
#
#   handy field number constants
#
class AlbumFields(IntEnum):
    ID          = 0
    NAME        = 1
    DATED       = 2
    NOTES       = 3
    PHOTO_COUNT = 4

class AlbumNameFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    NAME_ID     = 2

class AlbumPlaceFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    PLACE_ID    = 2

class AlbumTagFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    TAG_ID      = 2

class AttrFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2

class ConfigFields(IntEnum):
    ID          = 0
    NAME        = 1
    VERSION     = 2
    USERNAME    = 3
    FULLNAME    = 4
    DATADIR     = 5

class NameFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2

class PhotoFields(IntEnum):
    ID          = 0
    ALBUM_ID    = 1
    NAME        = 2
    PATH        = 3
    DATED       = 4
    NOTES       = 5

class PhotoNameFields(IntEnum):
    ID          = 0
    PHOTO_ID    = 1
    NAME_ID     = 2

class PhotoPlaceFields(IntEnum):
    ID          = 0
    PHOTO_ID    = 1
    PLACE_ID    = 2

class PhotoTagFields(IntEnum):
    ID          = 0
    PHOTO_ID    = 1
    TAG_ID      = 2

class PlaceFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2

class TagFields(IntEnum):
    ID          = 0
    PARENT_ID   = 1
    VALUE       = 2

################################################################
#
#   object structures
#
class PlornBaseObj:
    def __init__(self, name, id=None, dated='', notes='',
                 names=[], places=[], tags=[]):
        global module_logger

        self.name = name
        self.id = id
        self.dated = dated
        self.notes = notes
        self.name_list = names
        self.place_list = places
        self.tag_list = tags

        module_logger.debug('initializing base object: ' + str(self))

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_dated(self, dated):
        self.dated = dated

    def get_dated(self):
        return self.dated

    def set_notes(self, notes):
        self.notes = notes

    def get_notes(self):
        return self.notes

    def set_name_list(self, name_list):
        self.name_list.clear()
        self.name_list = copy.deepcopy(name_list)

    def get_name_list(self):
        return self.name_list

    def add_name_to_list(self, name):
        self.name_list.append(name)

    def remove_name_from_list(self, name):
        for ii in range(0, len(self.name_list)):
            if self.name_list[ii].get_id() == name.get_id():
                del self.name_list[ii]
                break

    def set_place_list(self, place_list):
        self.place_list.clear()
        self.place_list = copy.deepcopy(place_list)

    def get_place_list(self):
        return self.place_list

    def add_place_to_list(self, place):
        self.place_list.append(place)

    def remove_place_from_list(self, place):
        for ii in range(0, len(self.place_list)):
            if self.place_list[ii].get_id() == place.get_id():
                del self.place_list[ii]
                break

    def set_tag_list(self, tag_list):
        self.tag_list.clear()
        self.tag_list = copy.deepcopy(tag_list)

    def get_tag_list(self):
        return self.tag_list

    def add_tag_to_list(self, tag):
        self.tag_list.append(tag)

    def remove_tag_from_list(self, tag):
        for ii in range(0, len(self.tag_list)):
            if self.tag_list[ii].get_id() == tag.get_id():
                del self.tag_list[ii]
                break

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', name: \'{self.name}\''
        val += f', id: \'{self.id}\''
        val += f', dated: \'{self.dated}\''
        val += f', notes: \'{self.notes}\''
        val += f', name_list: \'{str(self.name_list)}\''
        val += f', place_list: \'{str(self.place_list)}\''
        val += f', tag_list: \'{str(self.tag_list)}\''
        return val

#######################################################################

class PlornAlbum(PlornBaseObj):
    def __init__(self, name, id=None, dated='', notes='', photo_count=0,
                 names=[], places=[], tags=[]):
        self.photo_count = photo_count
        super().__init__(name, id, dated, notes, names, places, tags)
        module_logger.debug('initializing album object: ' + str(self))

    def set_photo_count(self, photo_count):
        self.photo_count = photo_count

    def get_photo_count(self):
        return self.photo_count

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', name: \'{self.name}\''
        val += f', dated: \'{self.dated}\''
        val += f', notes: \'{self.notes}\''
        val += f', photo_count: \'{self.photo_count}\''
        val += f', name_list: \'{str(self.name_list)}\''
        val += f', place_list: \'{str(self.place_list)}\''
        val += f', tag_list: \'{str(self.tag_list)}\''
        return val


#######################################################################

class PlornPhoto(PlornBaseObj):
    def __init__(self, name, id=None, album_id=None,
                 path='', dated='', notes='', 
                 names=[], places=[], tags=[]):
        self.album_id = album_id
        self.path = path
        super().__init__(name, id, dated, notes, names, places, tags)
        module_logger.debug('initializing photo object: ' + str(self))

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def set_album_id(self, album_id):
        self.album_id = album_id

    def get_album_id(self):
        return self.album_id

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', name: \'{self.name}\''
        val += f', path: \'{self.path}\''
        val += f', dated: \'{self.dated}\''
        val += f', notes: \'{self.notes}\''
        return val


#######################################################################

class PlornAttr:
    '''
    Base class for the attributes of albums and photos,
    i.e., names, places, and tags
    '''
    def __init__(self, value, id=None, parent_id=None, table_name=''):
        self.value = value
        self.id = id
        self.parent_id = parent_id
        self.db_table_name = table_name

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_parent_id(self, id):
        self.parent_id = id

    def get_parent_id(self):
        return self.parent_id

    def set_db_table_name(self, table_name):
        self.db_table_name = table_name

    def get_db_table_name(self):
        return self.db_table_name

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', value: \'{self.value}\''
        val += f', parent_id: \'{self.parent_id}\''
        val += f', db_table_name: \'{self.db_table_name}\''
        return val

class PlornName(PlornAttr):
    def __init__(self, name, id=None, parent_id=0):
        super().__init__(name, id=id, parent_id=parent_id, table_name='names')

    def set_db_table_name(self, name):
        pass

class PlornPlace(PlornAttr):
    def __init__(self, place, id=None, parent_id=0):
        super().__init__(place, id=id, parent_id=parent_id, table_name='places')

    def set_db_table_name(self, name):
        pass

class PlornTag(PlornAttr):
    def __init__(self, tag, id=None, parent_id=0):
        super().__init__(tag, id=id, parent_id=parent_id, table_name='tags')

    def set_db_table_name(self, name):
        pass

