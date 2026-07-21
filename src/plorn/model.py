#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import os.path

from plorn.config import PlornConfig
from plorn.db import PlornDb, AlbumFields, PhotoFields

from PyQt6.QtCore import (
    Qt,
)

from PyQt6.QtGui import (
    QIcon,
)

from PyQt6.QtSql import (
    QSqlDatabase,
)

from PyQt6.QtWidgets import (
    QTreeWidgetItem,
)

module_logger = logging.getLogger('plorn.model')
module_logger.setLevel(logging.DEBUG)


class PlornDbModel:                   # sort of a model ...
    def __init__(self, tree):
        self.tree = tree
        config = PlornConfig()
        catalog, datadir, dbname = config.get_current_catalog()
        self.dbname = dbname
        dbpath = os.path.join(datadir, dbname)
        if not hasattr(self, 'db'):
            self.db = PlornDb(dbpath)
        self.rows = []

    def get_db(self):
        return self.db

    def add_albums(self):
        global module_logger

        module_logger.debug(f'entering {__name__}.PlornDbModel.add_albums')
        album_list = self.db.get_all_albums_list()
        album_icon = QIcon('./src/plorn/album.png')
        self.rows = []
        while album_list.next():
            module_logger.debug(f'adding album item: {album_list.value(0):04}')
            item = QTreeWidgetItem(self.tree)
            item.setChildIndicatorPolicy(
             QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
            )
            item.setText(0, f'{album_list.value(AlbumFields.NAME)}')
            item.setIcon(0, album_icon)
            item.setText(1, f'{album_list.value(AlbumFields.PHOTO_COUNT)}')
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            item.setText(2, 'album')
            item.setText(3, f'{album_list.value(AlbumFields.PHOTO_COUNT):04}')

            photos = self.add_photos(item, album_list.value(AlbumFields.ID))
            item.addChildren(photos)
            self.rows.append(item)

    def add_photos(self, parent_item, album_id):
        global module_logger
        module_logger.debug(f'entering {__name__}.PlornDbModel.add_photos')

        def normalize_suffix(val):
            basic = val.upper()
            if basic in ['JPG', 'JPEG']:
                res = 'JPG'
            elif basic in ['PNG']:
                res = 'PNG'
            elif basic in ['HEIC']:
                res = 'Apple'
            elif basic in ['RAW']:
                res = 'Raw'
            else:
                res = basic
            return res

        photo_list = self.db.get_all_photos_list()
        photo_icon = QIcon('./src/plorn/picture.png')
        photos = []
        while photo_list.next():
            module_logger.debug(f'adding photo item: {photo_list.value(0):04}')
            item = QTreeWidgetItem(parent_item)
            item.setChildIndicatorPolicy(
             QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
            )
            item.setText(0, f'{photo_list.value(PhotoFields.NAME)}')
            item.setIcon(0, photo_icon)
            item.setText(1, '')
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            suffix = photo_list.value(PhotoFields.PATH).split('.')
            #module_logger.debug(f'photo suffix: {suffix}')
            kind = normalize_suffix(suffix[len(suffix)-1])
            item.setText(2, f'{kind} photo')
            item.setText(3, f'{photo_list.value(PhotoFields.ID):04}')
            photos.append(item)

        return photos

    def get_albums(self):
        return self.rows

    def album_count(self):
        return self.db.album_count()

    def photo_count(self):
        return self.db.photo_count()

