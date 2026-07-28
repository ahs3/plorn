#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import logging
import os.path

from plorn.config import PlornConfig
from plorn.db import AlbumFields, PhotoFields

from PyQt6.QtCore import (
    Qt,
)

from PyQt6.QtGui import (
    QIcon,
)

from PyQt6.QtSql import (
    QSqlDatabase,
    QSqlTableModel,
    QSqlRelationalTableModel,
)

from PyQt6.QtWidgets import (
    QTreeWidgetItem,
)

module_logger = logging.getLogger('plorn.model')
module_logger.setLevel(logging.DEBUG)


class PlornAlbumModel(QSqlRelationalTableModel):
    '''
    NB: we always use the defalt connection for the db
    '''
    def __init__(self, parent=None, db=QSqlDatabase(), *args, **kwargs):
        global module_logger
        super().__init__(parent=parent, db=db, *args, **kwargs)

        module_logger.debug(f'album model init: {db.connectionName()}')
        self.setTable('albums')
        module_logger.debug(f'album model: valid? {db.isValid()}')
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.setHeaderData(AlbumFields.ID,
                           Qt.Orientation.Horizontal, 'ID')
        self.setHeaderData(AlbumFields.NAME,
                           Qt.Orientation.Horizontal, 'Album')
        self.setHeaderData(AlbumFields.DATED,
                           Qt.Orientation.Horizontal, 'Dated')
        self.setHeaderData(AlbumFields.NOTES,
                           Qt.Orientation.Horizontal, 'Notes')
        self.setHeaderData(AlbumFields.PHOTO_COUNT,
                           Qt.Orientation.Horizontal, 'Photo Count')
        res = self.select()
        module_logger.debug(f'album model init: select result {res}')

