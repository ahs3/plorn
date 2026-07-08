#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import os.path

from plorn.config import config
from plorn.db import PlornDb

from PyQt6.QtCore import (
    Qt,
)

from PyQt6.QtGui import (
    QIcon,
)

from PyQt6.QtWidgets import (
    QTreeWidgetItem,
)

module_logger = logging.getLogger('plorn.model')
module_logger.setLevel(logging.INFO)

class PlornDbModel:                   # sort of a model ...
    def __init__(self, tree):
        self.tree=tree
        dbname = os.path.join(config.get_datadir(), config.get_dbname())
        if not hasattr(self, 'db'):
            self.db = PlornDb(dbname, config)
        self.rows = []

    def add_albums(self):
        global module_logger

        module_logger.debug(f'entering {__name__}.PlornDbModel.add_albums')
        cursor = self.db.get_album_cursor()
        album_icon = QIcon('./src/plorn/album.png')
        self.rows = []
        for ii in cursor:
            module_logger.debug(f'adding album item: {ii}')
            item = QTreeWidgetItem(self.tree)
            item.setChildIndicatorPolicy(
             QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
            )
            item.setText(0, f'{ii['name']}')
            item.setIcon(0, album_icon)
            item.setText(1, f'{ii['photo_count']}')
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            item.setText(2, 'album')
            item.setText(3, f'{ii['id']:04}')
            photos = self.add_photos(item, ii['id'])
            item.addChildren(photos)
            self.rows.append(item)

    def add_photos(self, parent_item, album_id):
        global module_logger

        module_logger.debug(f'entering {__name__}.PlornDbModel.add_photos')
        cursor = self.db.get_photo_cursor()
        photo_icon = QIcon('./src/plorn/picture.png')
        photos = []
        for ii in cursor:
            module_logger.debug(f'adding photo item: {ii}')
            item = QTreeWidgetItem(parent_item)
            item.setChildIndicatorPolicy(
             QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
            )
            item.setText(0, f'{ii['name']}')
            item.setIcon(0, photo_icon)
            item.setText(1, '')
            item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            item.setText(2, 'photo')
            item.setText(3, f'{ii['id']:04}')
            photos.append(item)

        return photos

    def get_albums(self):
        return self.rows
