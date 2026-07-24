
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

from enum import IntEnum
import sqlite3

#-- handy field number constants
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

